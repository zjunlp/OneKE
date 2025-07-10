# 快速开始

## ⚡ 三步部署

### 1️⃣ 克隆项目
```bash
git clone git@github.com:ABOYL-Tuna/OneKE-Streamlit-LQ.git
cd OneKE-Streamlit-LQ
```

### 2️⃣ 一键部署

**Linux/macOS:**
```bash
# 如果遇到权限问题，先添加执行权限
chmod +x deploy.sh

# 然后运行部署脚本
./deploy.sh

# 或者直接用bash运行
bash deploy.sh
```

**Windows:**
```bash
deploy.bat
```

### 3️⃣ 打开浏览器

**本地访问：**
访问 http://localhost:8501 开始使用！

**服务器部署：**
如果在服务器上部署，可以使用公网 IP 访问：
- 访问 http://your-server-ip:8501
- 确保服务器防火墙已开放 8501 端口
- Neo4j 管理界面：http://your-server-ip:7474

## 🔧 环境要求

- **Docker Desktop** (包含Docker Compose)
- **Git**

### Docker Compose 安装检查

**检查是否已安装:**
```bash
# 新版本Docker (推荐)
docker compose version

# 旧版本Docker Compose
docker-compose --version
```

**如果没有安装Docker Compose:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker-compose-plugin

# CentOS/RHEL
sudo yum install docker-compose-plugin

# 或者使用pip安装
pip install docker-compose
```

## 📋 核心概念

- **OneKE-Streamlit-Frontend**: 主项目，Web前端界面
- **OneKE**: 代码依赖，提供算法支持
- **环境**: 只需要一个Python环境（前端项目的requirements.txt）

## 🛠️ 常用操作

```bash
./deploy.sh stop     # 停止
./deploy.sh restart  # 重启
./deploy.sh logs     # 查看日志
./deploy.sh shell    # 进入容器调试
```

## 🚨 遇到问题？

### 常见问题及解决方案：

1. **Permission denied 错误 (Linux/macOS)**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **docker-compose: command not found 错误**
   ```bash
   # 方案1: 使用新版本Docker命令
   docker compose up -d
   
   # 方案2: 安装docker-compose
   sudo apt-get install docker-compose-plugin
   
   # 方案3: 检查Docker版本
   docker --version
   docker compose version
   ```

3. **Docker 相关问题**
   - 确保 Docker 已启动
   - 检查 Docker 服务状态: `docker --version`

4. **端口占用问题**
   - 检查端口 8501 是否被占用
   - 修改端口: 编辑 docker-compose.yml

5. **查看详细日志**
   ```bash
   ./deploy.sh logs
   ```

6. **手动部署 (备选方案)**
   ```bash
   # 新版本Docker
   cd docker
   docker compose up -d
   
   # 旧版本Docker Compose
   cd docker
   docker-compose up -d
   ```

---

**🎯 就这么简单！开始构建你的知识图谱吧！**