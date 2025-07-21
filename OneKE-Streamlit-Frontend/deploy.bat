@echo off
setlocal enabledelayedexpansion

REM OneKE 部署脚本 (Windows)

REM 检查环境
:check_env
docker --version >nul 2>&1 || (echo Docker未安装 && exit /b 1)
docker info >nul 2>&1 || (echo Docker未运行 && exit /b 1)
if not exist "OneKE-Streamlit-Frontend" (echo 前端目录不存在 && exit /b 1)
if not exist "OneKE" (echo OneKE目录不存在 && exit /b 1)
if not exist "docker" (echo docker目录不存在 && exit /b 1)
goto :eof

REM 启动
:start
echo 启动环境...
mkdir data logs uploads models 2>nul
cd docker
docker-compose up -d
cd ..
echo 访问: http://localhost:8501
goto :eof

REM 构建
:build
echo 构建镜像...
cd docker
if "%~2"=="--no-cache" (
    docker-compose build --no-cache
) else (
    docker-compose build
)
cd ..
goto :eof

REM 停止
:stop
cd docker && docker-compose down && cd ..
goto :eof

REM 重启
:restart
cd docker && docker-compose restart && cd ..
goto :eof

REM 日志
:logs
cd docker
if "%~2"=="" (
    docker-compose logs -f
) else (
    docker-compose logs -f %~2
)
cd ..
goto :eof

REM 进入容器
:shell
cd docker && docker-compose exec oneke-frontend bash && cd ..
goto :eof

REM 清理
:cleanup
echo 确定清理所有资源? (y/N)
set /p response=
if /i "%response%"=="y" cd docker && docker-compose down -v --rmi all && cd ..
goto :eof

REM 状态
:status
cd docker && docker-compose ps && cd ..
goto :eof

REM 帮助
:help
echo 用法: %~nx0 [命令]
echo 命令: start^|stop^|restart^|build^|logs^|shell^|status^|cleanup
echo 示例: %~nx0 start
goto :eof

REM 主逻辑
set "cmd=%~1"
if "%cmd%"=="" set "cmd=start"

if "%cmd%"=="start" call :check_env && call :start
if "%cmd%"=="stop" call :stop
if "%cmd%"=="restart" call :restart
if "%cmd%"=="build" call :check_env && call :build %*
if "%cmd%"=="logs" call :logs %*
if "%cmd%"=="shell" call :shell
if "%cmd%"=="status" call :status
if "%cmd%"=="cleanup" call :cleanup
if "%cmd%"=="help" call :help
if not "%cmd%"=="start" if not "%cmd%"=="stop" if not "%cmd%"=="restart" if not "%cmd%"=="build" if not "%cmd%"=="logs" if not "%cmd%"=="shell" if not "%cmd%"=="status" if not "%cmd%"=="cleanup" if not "%cmd%"=="help" call :help