# OneKE-Streamlit-Frontend 专用环境
# OneKE 项目仅作为代码依赖，不需要单独环境

FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app/OneKE/src:/app/OneKE-Streamlit-Frontend
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    vim \
    nano \
    htop \
    tree \
    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --upgrade pip setuptools wheel

# 复制前端项目的requirements文件
COPY ../OneKE-Streamlit-Frontend/requirements.txt /tmp/requirements.txt

# 安装前端项目依赖（这是唯一需要的Python环境）
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 清理临时文件
RUN rm /tmp/requirements.txt

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/uploads /app/models

# 设置权限
RUN chmod -R 755 /app

# 创建启动脚本
RUN echo '#!/bin/bash\n\
echo "=== OneKE-Streamlit-Frontend 环境已启动 ==="\n\
echo "工作目录: /app"\n\
echo ""\n\
echo "📋 项目说明:"\n\
echo "  🎯 主项目: OneKE-Streamlit-Frontend (前端应用)"\n\
echo "  📚 依赖项目: OneKE (代码库，不需要独立运行)"\n\
echo ""\n\
echo "🌐 可用服务:"\n\
echo "  📊 Streamlit 前端: http://localhost:8501"\n\
echo "  🗄️  Neo4j 数据库: http://localhost:7474"\n\
echo ""\n\
echo "✅ Python 环境: oneke-frontend (已配置完成)"\n\
echo "📦 依赖状态: 已安装前端项目所需的所有包"\n\
echo ""\n\
echo "🚀 启动 Streamlit 应用..."\n\
cd /app/OneKE-Streamlit-Frontend\n\
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true' > /app/start.sh

RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 默认启动命令
CMD ["/app/start.sh"]