# OneKE-Streamlit-Frontend 项目

## 🎯 项目说明

**OneKE-Streamlit-Frontend** 是本项目的核心，提供知识图谱构建的 Web 界面。

**OneKE** 仅作为代码依赖，提供算法支持，不需要独立运行。

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <your-repository-url>
cd OneKE
```

### 2. 一键启动
```bash
# Linux/macOS
./deploy.sh

# Windows
deploy.bat
```

### 3. 访问应用
- **前端界面**: http://localhost:8501
- **数据库管理**: http://localhost:7474 (用户名: neo4j, 密码: password123)

## 📁 项目结构

```
OneKE/
├── OneKE-Streamlit-Frontend/    # 🎯 主项目 (Web前端)
│   ├── app.py                  # 应用入口
│   ├── requirements.txt        # Python依赖
│   └── ...
├── OneKE/                      # 📚 代码依赖 (算法库)
│   ├── src/                    # 核心算法
│   └── ...
├── docker/                     # 🐳 容器配置
│   ├── Dockerfile
│   └── docker-compose.yml
└── deploy.sh                   # 🚀 部署脚本
```

## 🔧 环境说明

- **Python环境**: 只需要 `OneKE-Streamlit-Frontend/requirements.txt`
- **代码挂载**: 两个项目文件夹都挂载到容器中
- **依赖关系**: 前端项目可直接导入 OneKE 模块

```python
# 在前端项目中使用 OneKE 算法
from OneKE.src.modules import some_module
```

## 🛠️ 常用命令

```bash
./deploy.sh start    # 启动服务
./deploy.sh stop     # 停止服务
./deploy.sh logs     # 查看日志
./deploy.sh shell    # 进入容器
./deploy.sh build    # 重新构建
```

## 📋 前置要求

- Docker Desktop
- Git

## 💡 开发提示

- 修改 `OneKE-Streamlit-Frontend/` 中的文件会实时生效
- 只需维护前端项目的 `requirements.txt`
- OneKE 项目保持只读，作为算法库使用

## 📚 项目引用

本项目基于 **OneKE** 项目构建，OneKE 是一个强大的知识抽取框架。

### OneKE 项目信息
- **项目名称**: OneKE (One-stop Knowledge Extraction)
- **项目地址**: [https://github.com/zjunlp/OneKE](https://github.com/zjunlp/OneKE)
- **论文**: [OneKE: A Dockerized Schema-Guided LLM Agent-based Knowledge Extraction Toolkit](https://arxiv.org/abs/2409.13793)
- **作者**: ZJUNLP Team

### 致谢
感谢 OneKE 团队提供的优秀知识抽取算法和工具，本项目在其基础上构建了 Streamlit Web 界面，为用户提供更便捷的知识图谱构建体验。

---

**🎉 现在可以开始使用 OneKE-Streamlit-Frontend 构建知识图谱了！**