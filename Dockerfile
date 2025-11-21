# Build: docker buildx build --platform linux/amd64 -f Dockerfile -t wzdnzd/aggregator:tag --build-arg PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple" .
# Docker image for Aggregator - Free Proxy Pool Builder

FROM python:3.10-slim

LABEL maintainer="wzdnzd" \
      description="Aggregator - Free Proxy Pool Builder" \
      version="1.0"

# 基础配置
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AGGREGATOR_LOG_LEVEL=INFO \
    AGGREGATOR_DEBUG=false

# GitHub配置
ENV GIST_PAT="" \
    GIST_LINK="" \
    CUSTOMIZE_LINK=""

# pip索引配置
ARG PIP_INDEX_URL="https://pypi.org/simple"

# 工作目录
WORKDIR /aggregator

# 安装系统依赖（网络工具、curl等）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    iputils-ping \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 复制应用文件
COPY requirements.txt /aggregator/
COPY subscribe /aggregator/subscribe
COPY clash/clash-linux-amd clash/Country.mmdb /aggregator/clash/
COPY subconverter /aggregator/subconverter
COPY cmd /aggregator/cmd

# 清理subconverter非Linux文件以优化镜像大小
RUN rm -rf /aggregator/subconverter/subconverter-darwin-amd \
    && rm -rf /aggregator/subconverter/subconverter-darwin-arm \
    && rm -rf /aggregator/subconverter/subconverter-linux-arm \
    && rm -rf /aggregator/subconverter/subconverter-windows.exe

# 创建必要的目录
RUN mkdir -p /aggregator/data /aggregator/logs /aggregator/output \
    && chmod 755 /aggregator/data /aggregator/logs /aggregator/output

# 安装Python依赖
RUN pip install -i ${PIP_INDEX_URL} --no-cache-dir -r requirements.txt

# 非root用户运行（提高安全性）
RUN useradd -m -u 1000 aggregator && \
    chown -R aggregator:aggregator /aggregator
USER aggregator

# 默认命令 - 运行collect.py
CMD ["python", "-u", "subscribe/collect.py", "--all", "--overwrite", "--skip"]
