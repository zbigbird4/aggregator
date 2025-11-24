# Aggregator 完整安装部署指引

> **版本**: v1.0.0  
> **更新时间**: 2024-11  
> **适用对象**: 所有希望部署 Aggregator 的用户

---

## 📖 目录

- [Part 1: 镜像获取](#part-1-镜像获取)
  - [从 GitHub Container Registry (GHCR) 获取](#从-github-container-registry-ghcr-获取)
  - [从 Docker Hub 获取](#从-docker-hub-获取)
  - [镜像版本选择指南](#镜像版本选择指南)
  - [验证镜像完整性](#验证镜像完整性)
- [Part 2: 快速部署](#part-2-快速部署)
  - [Step 1: 准备环境](#step-1-准备环境)
  - [Step 2: 配置环境变量](#step-2-配置环境变量)
  - [Step 3: 启动容器](#step-3-启动容器)
- [Part 3: 详细部署场景](#part-3-详细部署场景)
  - [场景1: 本地开发环境部署](#场景1-本地开发环境部署)
  - [场景2: VPS/云服务器单机生产部署](#场景2-vps云服务器单机生产部署)
  - [场景3: 使用 Upstash Redis (无服务器存储)](#场景3-使用-upstash-redis-无服务器存储)
  - [场景4: Docker Hub 自动镜像更新](#场景4-docker-hub-自动镜像更新)
  - [场景5: 高可用多实例部署](#场景5-高可用多实例部署)
- [Part 4: 配置管理详解](#part-4-配置管理详解)
  - [环境变量详细说明](#环境变量详细说明)
  - [数据卷管理](#数据卷管理)
  - [网络配置](#网络配置)
  - [资源限制配置](#资源限制配置)
- [Part 5: 常见问题](#part-5-常见问题)
- [Part 6: 下一步](#part-6-下一步)

---

## Part 1: 镜像获取

Aggregator 提供了多个镜像仓库供用户选择，您可以根据网络环境和个人偏好选择最合适的镜像源。

### 从 GitHub Container Registry (GHCR) 获取

GitHub Container Registry (GHCR) 是 GitHub 官方提供的容器镜像仓库服务，与项目源码紧密集成。

#### **基本拉取命令**

```bash
# 拉取最新版本
docker pull ghcr.io/wzdnzd/aggregator:latest

# 拉取特定版本
docker pull ghcr.io/wzdnzd/aggregator:v1.0.0

# 拉取特定架构
docker pull --platform linux/amd64 ghcr.io/wzdnzd/aggregator:latest
docker pull --platform linux/arm64 ghcr.io/wzdnzd/aggregator:latest
```

#### **GHCR 的优点**

1. **与 GitHub 集成**: 直接关联到项目仓库，版本管理清晰
2. **自动构建**: 每次代码提交都会触发自动构建
3. **安全可靠**: GitHub 的安全体系保障
4. **多架构支持**: 原生支持 AMD64 和 ARM64
5. **免费使用**: 对于公开仓库完全免费

#### **访问私有镜像（如果项目设为私有）**

如果项目设置为私有，您需要进行身份认证：

```bash
# 1. 创建 GitHub Personal Access Token
# 访问: https://github.com/settings/tokens
# 权限: read:packages

# 2. 登录 GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 3. 拉取镜像
docker pull ghcr.io/wzdnzd/aggregator:latest
```

#### **检查镜像可用性**

```bash
# 查看镜像信息
docker image inspect ghcr.io/wzdnzd/aggregator:latest

# 查看镜像层
docker history ghcr.io/wzdnzd/aggregator:latest

# 查看镜像标签
curl -s https://ghcr.io/v2/wzdnzd/aggregator/tags/list | jq
```

---

### 从 Docker Hub 获取

Docker Hub 是最流行的公共容器镜像仓库，拥有广泛的用户基础和良好的国内访问速度（使用镜像加速器）。

#### **基本拉取命令**

```bash
# 拉取最新版本
docker pull wzdnzd/aggregator:latest

# 拉取特定版本
docker pull wzdnzd/aggregator:v1.0.0

# 拉取特定架构
docker pull --platform linux/amd64 wzdnzd/aggregator:latest
docker pull --platform linux/arm64 wzdnzd/aggregator:latest
```

#### **Docker Hub 的优点**

1. **广泛使用**: 最流行的容器镜像仓库
2. **良好的生态**: 丰富的文档和社区支持
3. **镜像加速**: 国内有多个镜像加速服务
4. **易于搜索**: 可以通过 Docker Hub 网站轻松搜索
5. **自动构建**: 支持自动构建和 webhook

#### **配置 Docker Hub 镜像加速器（中国大陆用户推荐）**

为了提升镜像拉取速度，建议配置镜像加速器：

```bash
# 创建或编辑 Docker 配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.ccs.tencentyun.com"
  ]
}
EOF

# 重启 Docker 服务
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证配置
docker info | grep -A 5 "Registry Mirrors"
```

#### **搜索和确认官方镜像**

```bash
# 在命令行搜索
docker search wzdnzd/aggregator

# 或访问 Docker Hub 网站
# https://hub.docker.com/r/wzdnzd/aggregator
```

#### **Docker Hub 账号设置（可选）**

如果您需要推送自己的镜像或访问私有镜像：

```bash
# 登录 Docker Hub
docker login

# 输入用户名和密码
Username: your_username
Password: your_password

# 验证登录状态
docker info | grep Username
```

---

### 镜像版本选择指南

选择合适的镜像版本对于不同的使用场景至关重要。

#### **版本标签说明**

| 标签格式 | 示例 | 说明 | 推荐场景 | 稳定性 |
|---------|------|------|---------|--------|
| `latest` | `aggregator:latest` | 最新稳定版本，自动更新 | 开发测试、个人使用 | ⭐⭐⭐⭐ |
| `v{major}.{minor}.{patch}` | `aggregator:v1.2.3` | 语义化版本号，固定版本 | 生产环境、需要稳定性 | ⭐⭐⭐⭐⭐ |
| `v{major}.{minor}` | `aggregator:v1.2` | 小版本固定，补丁更新 | 生产环境、接受小更新 | ⭐⭐⭐⭐ |
| `v{major}` | `aggregator:v1` | 大版本固定，次版本更新 | 长期支持 | ⭐⭐⭐⭐ |
| `commit-{sha}` | `aggregator:commit-abc1234` | 特定提交的镜像 | 调试、回溯问题 | ⭐⭐⭐ |
| `main` | `aggregator:main` | 主分支最新代码 | 开发测试、尝鲜 | ⭐⭐ |
| `develop` | `aggregator:develop` | 开发分支最新代码 | 测试新功能 | ⭐ |

#### **版本选择决策树**

```
┌─ 你的使用场景？
│
├─ 生产环境
│  ├─ 需要绝对稳定 → 使用固定版本标签 (v1.2.3)
│  ├─ 接受安全补丁 → 使用次版本标签 (v1.2)
│  └─ 长期维护 → 使用主版本标签 (v1)
│
├─ 开发/测试环境
│  ├─ 日常开发 → 使用 latest
│  ├─ 测试新功能 → 使用 main 或 develop
│  └─ 问题回溯 → 使用 commit-{sha}
│
└─ 个人使用
   ├─ 追求稳定 → 使用 latest
   └─ 尝鲜 → 使用 main
```

#### **查看可用版本**

```bash
# 方法1: 使用 Docker Hub API (Docker Hub)
curl -s "https://hub.docker.com/v2/repositories/wzdnzd/aggregator/tags/" | jq -r '.results[].name'

# 方法2: 使用 GHCR API (GitHub Container Registry)
curl -s "https://api.github.com/users/wzdnzd/packages/container/aggregator/versions" | jq -r '.[].metadata.container.tags[]'

# 方法3: 使用 crane 工具
crane ls wzdnzd/aggregator
```

#### **版本升级建议**

```bash
# 升级前备份数据
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz ./data ./logs

# 拉取新版本
docker pull wzdnzd/aggregator:v1.2.0

# 更新 docker-compose.yml 中的版本
# 启动新版本
docker-compose up -d

# 查看日志确认正常
docker-compose logs -f aggregator
```

---

### 验证镜像完整性

为确保镜像未被篡改，建议验证镜像完整性。

#### **查看镜像摘要**

```bash
# 查看镜像 SHA256 摘要
docker images --digests wzdnzd/aggregator

# 输出示例：
# REPOSITORY          TAG       DIGEST                                                                    IMAGE ID       CREATED        SIZE
# wzdnzd/aggregator   latest    sha256:abc123...                                                          xyz789         2 days ago     250MB
```

#### **验证镜像签名（如果启用）**

```bash
# 使用 Docker Content Trust
export DOCKER_CONTENT_TRUST=1
docker pull wzdnzd/aggregator:latest

# 查看签名信息
docker trust inspect wzdnzd/aggregator:latest
```

#### **扫描镜像漏洞**

```bash
# 使用 Docker Scan（需要 Docker Desktop）
docker scan wzdnzd/aggregator:latest

# 使用 Trivy
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image wzdnzd/aggregator:latest

# 使用 Grype
grype wzdnzd/aggregator:latest
```

---

## Part 2: 快速部署

本节将指导您在 **3 个步骤** 内完成 Aggregator 的快速部署。

### Step 1: 准备环境

#### **1.1 检查 Docker 版本**

```bash
# 检查 Docker 版本（需要 >= 20.10）
docker --version

# 输出示例：Docker version 24.0.7, build afdd53b

# 如果版本过低，请升级
# Ubuntu/Debian
curl -fsSL https://get.docker.com | bash

# 或使用官方安装脚本
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### **1.2 检查 Docker Compose 版本**

```bash
# 检查 Docker Compose 版本（需要 >= 2.0）
docker-compose --version
# 或
docker compose version

# 输出示例：Docker Compose version v2.23.0

# 如果未安装，安装 Docker Compose V2
sudo apt-get install docker-compose-plugin
```

#### **1.3 检查系统资源**

```bash
# 检查可用磁盘空间（建议 >= 5GB）
df -h /var/lib/docker

# 检查可用内存（建议 >= 2GB）
free -h

# 检查 CPU 核心数
nproc
```

#### **1.4 创建工作目录**

```bash
# 创建项目目录
mkdir -p ~/aggregator
cd ~/aggregator

# 创建必要的子目录
mkdir -p data logs config
```

#### **1.5 配置防火墙（如果需要）**

```bash
# 如果需要对外提供服务，开放必要端口
# 注意：Aggregator 默认不需要对外开放端口

# UFW（Ubuntu）
sudo ufw allow 22/tcp    # SSH
sudo ufw enable

# firewalld（CentOS/RHEL）
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --reload
```

---

### Step 2: 配置环境变量

#### **2.1 下载环境变量模板**

```bash
# 方法1: 从 GitHub 下载
curl -O https://raw.githubusercontent.com/wzdnzd/aggregator/main/.env.example

# 方法2: 手动创建
cat > .env << 'EOF'
# GitHub Gist 配置
GIST_PAT=your_github_token
GIST_LINK=your_username/your_gist_id

# 可选配置
CUSTOMIZE_LINK=
ENABLE_SPECIAL_PROTOCOLS=false

# 时区
TZ=Asia/Shanghai
EOF
```

#### **2.2 获取 GitHub Personal Access Token**

1. 访问 [GitHub Settings - Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置权限：
   - ✅ **gist** (完整访问 gist)
4. 生成并复制 token（格式：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）

#### **2.3 创建 GitHub Gist**

1. 访问 [GitHub Gist](https://gist.github.com/)
2. 点击 "Create new gist"
3. 创建一个文件，例如 `clash.yaml`
4. 选择 "Create public gist" 或 "Create secret gist"
5. 记录 Gist ID（URL 中的字符串，如：`https://gist.github.com/username/1234567890abcdef...`）

#### **2.4 配置 .env 文件**

```bash
# 编辑 .env 文件
nano .env
# 或
vim .env

# 填入实际值
GIST_PAT=ghp_YourActualTokenHere123456789
GIST_LINK=wzdnzd/1234567890abcdef1234567890abcdef
```

#### **2.5 验证配置**

```bash
# 检查环境变量文件
cat .env

# 确保没有多余的空格和引号
# 确保 token 和 gist ID 正确
```

---

### Step 3: 启动容器

#### **3.1 下载 docker-compose.yml**

```bash
# 从 GitHub 下载
curl -O https://raw.githubusercontent.com/wzdnzd/aggregator/main/docker-compose.yml

# 查看配置
cat docker-compose.yml
```

#### **3.2 启动服务**

```bash
# 启动容器（后台运行）
docker-compose up -d

# 输出示例：
# [+] Running 2/2
#  ⠿ Network aggregator_aggregator-network  Created                    0.1s
#  ⠿ Container aggregator                   Started                    0.5s
```

#### **3.3 查看日志**

```bash
# 实时查看日志
docker-compose logs -f aggregator

# 查看最近 100 行日志
docker-compose logs --tail=100 aggregator

# 查看特定时间的日志
docker-compose logs --since="2024-01-01T00:00:00" aggregator
```

#### **3.4 验证容器状态**

```bash
# 检查容器运行状态
docker-compose ps

# 输出示例：
# NAME         IMAGE                        COMMAND                  SERVICE      STATUS         PORTS
# aggregator   wzdnzd/aggregator:latest     "python -u subscribe…"   aggregator   Up 10 seconds

# 检查容器健康状态
docker inspect aggregator | jq '.[0].State.Health'

# 查看容器资源使用
docker stats aggregator
```

#### **3.5 验证功能**

```bash
# 进入容器
docker exec -it aggregator /bin/bash

# 在容器内查看生成的文件
ls -la /aggregator/data

# 检查 Gist 是否更新
# 访问您的 Gist URL 查看是否有新内容
```

#### **3.6 快速启动脚本（可选）**

创建一个快速启动脚本：

```bash
# 创建启动脚本
cat > start.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 启动 Aggregator..."

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ .env 文件不存在，请先配置环境变量"
    exit 1
fi

# 检查必需的环境变量
source .env
if [ -z "$GIST_PAT" ] || [ -z "$GIST_LINK" ]; then
    echo "❌ 请在 .env 中配置 GIST_PAT 和 GIST_LINK"
    exit 1
fi

# 创建必要的目录
mkdir -p data logs

# 启动容器
docker-compose up -d

# 等待容器启动
sleep 5

# 显示状态
docker-compose ps
docker-compose logs --tail=20 aggregator

echo "✅ Aggregator 已启动！"
echo "📝 查看日志: docker-compose logs -f aggregator"
echo "🛑 停止服务: docker-compose down"
EOF

# 添加执行权限
chmod +x start.sh

# 运行
./start.sh
```

---

## Part 3: 详细部署场景

本节提供多个真实场景的详细部署指南，涵盖从本地开发到生产环境的各种需求。

### 场景1: 本地开发环境部署

**适用场景**：本地机器开发测试、学习使用、功能验证

**特点**：最简化配置、快速启动、便于调试

#### **1.1 目录结构**

```
~/aggregator-dev/
├── .env                  # 环境变量配置
├── docker-compose.yml    # Docker Compose 配置
├── data/                 # 数据目录
├── logs/                 # 日志目录
└── config/               # 自定义配置（可选）
```

#### **1.2 创建目录**

```bash
mkdir -p ~/aggregator-dev
cd ~/aggregator-dev
mkdir -p data logs config
```

#### **1.3 docker-compose.yml 配置**

```yaml
version: '3.8'

services:
  aggregator:
    image: wzdnzd/aggregator:latest
    container_name: aggregator-dev
    restart: unless-stopped
    
    environment:
      - GIST_PAT=${GIST_PAT}
      - GIST_LINK=${GIST_LINK}
      - TZ=Asia/Shanghai
      - PYTHONUNBUFFERED=1
    
    volumes:
      # 挂载本地目录，便于查看生成的文件
      - ./data:/aggregator/data
      - ./logs:/aggregator/logs
      # 如果需要使用自定义配置
      # - ./config/my-config.json:/aggregator/my-config.json:ro
    
    # 开发环境不需要严格的资源限制
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
    
    # 直接输出日志到 stdout，便于调试
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### **1.4 .env 配置**

```bash
# 开发环境配置
GIST_PAT=ghp_your_token_here
GIST_LINK=your_username/your_gist_id

# 开发模式：启用详细日志
# ENABLE_DEBUG=true

TZ=Asia/Shanghai
```

#### **1.5 启动和测试**

```bash
# 启动服务
docker-compose up -d

# 实时查看日志（观察运行情况）
docker-compose logs -f

# 进入容器调试
docker exec -it aggregator-dev /bin/bash

# 在容器内手动运行
python -u subscribe/collect.py --all --overwrite --skip

# 查看生成的文件
ls -la data/
ls -la logs/

# 停止服务
docker-compose down
```

#### **1.6 开发技巧**

```bash
# 使用 VS Code 连接到容器
# 1. 安装 "Remote - Containers" 插件
# 2. 右键点击容器，选择 "Attach Visual Studio Code"

# 使用 Docker Desktop 查看容器状态和日志
# 适合不熟悉命令行的用户

# 快速重启容器（测试配置更改）
docker-compose restart aggregator

# 重建并启动（代码或配置有较大变化）
docker-compose up -d --build --force-recreate
```

---

### 场景2: VPS/云服务器单机生产部署

**适用场景**：VPS、云服务器、专用服务器生产环境

**特点**：完整配置、数据持久化、安全加固、监控告警

#### **2.1 系统准备**

```bash
# 更新系统（推荐）
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y curl wget git vim htop

# 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER
newgrp docker

# 配置防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp   # 如果需要 HTTP
sudo ufw allow 443/tcp  # 如果需要 HTTPS
sudo ufw enable
```

#### **2.2 目录结构（生产环境）**

```
/opt/aggregator/
├── .env                      # 环境变量（权限 600）
├── docker-compose.yml        # Docker Compose 配置
├── docker-compose.prod.yml   # 生产环境覆盖配置
├── data/                     # 持久化数据
│   ├── proxies/              # 代理数据
│   └── cache/                # 缓存数据
├── logs/                     # 日志目录
│   ├── aggregator.log        # 应用日志
│   └── archive/              # 归档日志
├── backups/                  # 备份目录
├── scripts/                  # 管理脚本
│   ├── backup.sh             # 备份脚本
│   ├── restore.sh            # 恢复脚本
│   └── health-check.sh       # 健康检查脚本
└── config/                   # 配置文件
    └── process-config.json   # 自定义配置
```

#### **2.3 创建目录和设置权限**

```bash
# 创建目录
sudo mkdir -p /opt/aggregator/{data,logs,backups,scripts,config}
sudo mkdir -p /opt/aggregator/data/{proxies,cache}
sudo mkdir -p /opt/aggregator/logs/archive

# 设置所有者
sudo chown -R $USER:$USER /opt/aggregator

# 设置权限
chmod 700 /opt/aggregator
chmod 755 /opt/aggregator/{data,logs,backups,scripts,config}
chmod 700 /opt/aggregator/.env  # .env 文件仅所有者可读写
```

#### **2.4 docker-compose.yml（生产配置）**

```yaml
version: '3.8'

services:
  aggregator:
    image: wzdnzd/aggregator:v1.0.0  # 使用固定版本
    container_name: aggregator-prod
    restart: always  # 生产环境总是重启
    
    environment:
      - GIST_PAT=${GIST_PAT}
      - GIST_LINK=${GIST_LINK}
      - CUSTOMIZE_LINK=${CUSTOMIZE_LINK:-}
      - ENABLE_SPECIAL_PROTOCOLS=${ENABLE_SPECIAL_PROTOCOLS:-false}
      - TZ=Asia/Shanghai
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
    
    volumes:
      # 数据持久化
      - /opt/aggregator/data:/aggregator/data
      - /opt/aggregator/logs:/aggregator/logs
      
      # 配置文件（只读）
      - /opt/aggregator/config:/aggregator/config:ro
    
    # 生产环境资源限制
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
    
    # 健康检查
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    
    # 日志管理（防止日志占满磁盘）
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "10"
        compress: "true"
    
    networks:
      - aggregator-network
  
  # Watchtower - 自动更新镜像（可选）
  watchtower:
    image: containrrr/watchtower:latest
    container_name: aggregator-watchtower
    restart: always
    
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=86400  # 每天检查一次
      - WATCHTOWER_INCLUDE_RESTARTING=true
      - WATCHTOWER_NOTIFICATIONS=email
      - WATCHTOWER_NOTIFICATION_EMAIL_FROM=${NOTIFICATION_EMAIL}
      - WATCHTOWER_NOTIFICATION_EMAIL_TO=${NOTIFICATION_EMAIL}
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER=${EMAIL_SERVER}
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PORT=587
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_USER=${EMAIL_USER}
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PASSWORD=${EMAIL_PASSWORD}
      - TZ=Asia/Shanghai
    
    command: aggregator-prod
    
    networks:
      - aggregator-network

networks:
  aggregator-network:
    driver: bridge
```

#### **2.5 .env 配置（生产环境）**

```bash
# GitHub Gist 配置
GIST_PAT=ghp_your_production_token_here
GIST_LINK=your_username/your_production_gist_id

# 自定义机场列表（可选）
CUSTOMIZE_LINK=https://your-domain.com/airports.txt

# 功能开关
ENABLE_SPECIAL_PROTOCOLS=true

# Watchtower 通知配置（可选）
NOTIFICATION_EMAIL=admin@yourdomain.com
EMAIL_SERVER=smtp.gmail.com
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# 时区
TZ=Asia/Shanghai
```

#### **2.6 备份脚本**

创建自动备份脚本 `/opt/aggregator/scripts/backup.sh`：

```bash
#!/bin/bash
# Aggregator 备份脚本

set -e

# 配置
BACKUP_DIR="/opt/aggregator/backups"
DATA_DIR="/opt/aggregator/data"
LOG_DIR="/opt/aggregator/logs"
RETENTION_DAYS=30

# 创建备份目录
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"
mkdir -p "$BACKUP_PATH"

echo "🔄 开始备份 - $TIMESTAMP"

# 备份数据目录
echo "📦 备份数据目录..."
tar -czf "$BACKUP_PATH/data.tar.gz" -C "$DATA_DIR" .

# 备份日志目录（最近7天）
echo "📝 备份日志目录..."
find "$LOG_DIR" -name "*.log" -mtime -7 -exec tar -czf "$BACKUP_PATH/logs.tar.gz" {} +

# 备份配置文件
echo "⚙️  备份配置文件..."
cp /opt/aggregator/.env "$BACKUP_PATH/.env.backup"
cp /opt/aggregator/docker-compose.yml "$BACKUP_PATH/docker-compose.yml.backup"

# 创建备份清单
echo "📋 创建备份清单..."
cat > "$BACKUP_PATH/manifest.txt" << EOF
Backup Date: $TIMESTAMP
Hostname: $(hostname)
Data Size: $(du -sh "$DATA_DIR" | cut -f1)
Log Size: $(du -sh "$LOG_DIR" | cut -f1)
Docker Version: $(docker --version)
Compose Version: $(docker-compose --version)
EOF

# 计算校验和
echo "🔐 计算校验和..."
cd "$BACKUP_PATH"
sha256sum * > checksums.sha256

# 压缩整个备份
echo "🗜️  压缩备份..."
cd "$BACKUP_DIR"
tar -czf "backup_$TIMESTAMP.tar.gz" "backup_$TIMESTAMP"
rm -rf "backup_$TIMESTAMP"

# 删除旧备份
echo "🗑️  清理旧备份..."
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ 备份完成: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
echo "📊 备份大小: $(du -sh "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" | cut -f1)"
```

添加执行权限并设置定时任务：

```bash
# 添加执行权限
chmod +x /opt/aggregator/scripts/backup.sh

# 添加到 crontab（每天凌晨2点备份）
crontab -e

# 添加以下行
0 2 * * * /opt/aggregator/scripts/backup.sh >> /opt/aggregator/logs/backup.log 2>&1
```

#### **2.7 健康检查脚本**

创建健康检查脚本 `/opt/aggregator/scripts/health-check.sh`：

```bash
#!/bin/bash
# Aggregator 健康检查脚本

set -e

CONTAINER_NAME="aggregator-prod"
WEBHOOK_URL="${WEBHOOK_URL:-}"  # 可配置 webhook 通知

# 检查容器是否运行
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ 容器未运行，尝试启动..."
    cd /opt/aggregator
    docker-compose up -d
    
    # 发送通知
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" -d "容器 $CONTAINER_NAME 已自动重启"
    fi
    exit 1
fi

# 检查容器健康状态
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME")
if [ "$HEALTH_STATUS" != "healthy" ] && [ "$HEALTH_STATUS" != "starting" ]; then
    echo "❌ 容器健康检查失败: $HEALTH_STATUS"
    
    # 发送通知
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" -d "容器 $CONTAINER_NAME 健康检查失败: $HEALTH_STATUS"
    fi
    exit 1
fi

# 检查磁盘空间
DISK_USAGE=$(df -h /opt/aggregator | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  磁盘使用率过高: ${DISK_USAGE}%"
    
    # 发送通知
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" -d "Aggregator 磁盘使用率过高: ${DISK_USAGE}%"
    fi
fi

echo "✅ 健康检查通过"
```

添加到 crontab（每5分钟检查一次）：

```bash
chmod +x /opt/aggregator/scripts/health-check.sh

crontab -e
# 添加
*/5 * * * * /opt/aggregator/scripts/health-check.sh >> /opt/aggregator/logs/health-check.log 2>&1
```

#### **2.8 启动生产环境**

```bash
cd /opt/aggregator

# 首次启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 验证运行状态
docker-compose ps
docker stats aggregator-prod

# 测试备份
./scripts/backup.sh

# 测试健康检查
./scripts/health-check.sh
```

#### **2.9 监控和维护**

```bash
# 定期查看资源使用
docker stats aggregator-prod

# 查看日志大小
du -sh /opt/aggregator/logs

# 手动清理日志（如果需要）
find /opt/aggregator/logs -name "*.log" -mtime +30 -delete

# 查看备份
ls -lh /opt/aggregator/backups

# 更新镜像（如果使用 Watchtower，会自动更新）
docker-compose pull
docker-compose up -d

# 查看容器资源限制
docker inspect aggregator-prod | jq '.[0].HostConfig.Memory'
```

---

### 场景3: 使用 Upstash Redis (无服务器存储)

**适用场景**：不想自己运维 Redis、需要全球分布式存储、serverless 架构

**特点**：零运维、按量计费、全球低延迟、免费额度

#### **3.1 Upstash 简介**

Upstash 是一个无服务器 Redis 服务，提供：
- **免费额度**：10,000 命令/天，256MB 存储
- **全球分布**：多个区域可选
- **REST API**：支持 HTTP 访问
- **兼容 Redis**：支持标准 Redis 命令

#### **3.2 注册和创建数据库**

1. 访问 [Upstash Console](https://console.upstash.com/)
2. 注册账号（支持 GitHub/Google 登录）
3. 点击 "Create Database"
4. 配置：
   - **Name**: aggregator-redis
   - **Type**: Regional (单区域) 或 Global (多区域)
   - **Region**: 选择离您最近的区域（如 ap-southeast-1 for Singapore）
   - **TLS**: ✅ 启用（推荐）
5. 点击 "Create"

#### **3.3 获取连接信息**

在数据库详情页面，找到：

```
# Redis 连接字符串
REDIS_URL=redis://default:your_password@your-endpoint.upstash.io:6379

# REST API 端点（可选）
REST_URL=https://your-endpoint.upstash.io
REST_TOKEN=your_rest_token
```

#### **3.4 docker-compose.yml 配置**

由于 Aggregator 当前版本主要使用 GitHub Gist 作为存储，Redis 主要用于缓存和状态管理。如果您的自定义配置需要 Redis：

```yaml
version: '3.8'

services:
  aggregator:
    image: wzdnzd/aggregator:latest
    container_name: aggregator-upstash
    restart: unless-stopped
    
    environment:
      # GitHub Gist 配置
      - GIST_PAT=${GIST_PAT}
      - GIST_LINK=${GIST_LINK}
      
      # Upstash Redis 配置
      - REDIS_URL=${REDIS_URL}
      
      # 其他配置
      - TZ=Asia/Shanghai
      - PYTHONUNBUFFERED=1
    
    volumes:
      - ./data:/aggregator/data
      - ./logs:/aggregator/logs
    
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### **3.5 .env 配置**

```bash
# GitHub Gist 配置
GIST_PAT=ghp_your_token_here
GIST_LINK=your_username/your_gist_id

# Upstash Redis 配置
REDIS_URL=rediss://default:your_password@your-endpoint.upstash.io:6379

# 时区
TZ=Asia/Shanghai
```

注意：`rediss://` 表示使用 TLS 加密连接。

#### **3.6 验证 Redis 连接**

```bash
# 启动容器
docker-compose up -d

# 进入容器测试 Redis 连接
docker exec -it aggregator-upstash /bin/bash

# 在容器内安装 redis-cli（如果需要）
apt-get update && apt-get install -y redis-tools

# 测试连接
redis-cli -u "$REDIS_URL" ping
# 应返回: PONG

# 测试写入
redis-cli -u "$REDIS_URL" SET test "Hello Upstash"
redis-cli -u "$REDIS_URL" GET test
# 应返回: "Hello Upstash"

# 退出容器
exit
```

#### **3.7 成本分析**

**Upstash 免费额度**：
- 每日命令数：10,000
- 最大存储：256 MB
- 最大连接数：100
- 数据持久化：✅

**付费计划**（按需）：
- **Pro 500K**: $0.2/100K 命令
- **Pro 5M**: $0.15/100K 命令
- **Enterprise**: 定制

对于 Aggregator 的典型使用场景（每天运行几次），免费额度完全足够。

#### **3.8 监控 Upstash 使用量**

1. 登录 [Upstash Console](https://console.upstash.com/)
2. 进入您的数据库
3. 查看 "Metrics" 标签页：
   - **Commands**: 命令数使用量
   - **Storage**: 存储使用量
   - **Connections**: 连接数

#### **3.9 Upstash 优势总结**

| 特性 | Upstash Redis | 自建 Redis |
|-----|--------------|-----------|
| **运维成本** | 零运维 | 需要维护 |
| **可用性** | 99.99% SLA | 取决于自己 |
| **扩展性** | 自动扩展 | 手动扩展 |
| **全球分布** | 支持 | 需要自建 |
| **备份** | 自动备份 | 需要配置 |
| **成本** | 免费额度 + 按量计费 | 服务器成本 |
| **延迟** | 全球低延迟 | 取决于位置 |

---

### 场景4: Docker Hub 自动镜像更新

**适用场景**：希望自动获取最新镜像、减少手动维护、保持系统最新

**特点**：自动更新、通知告警、安全可靠

#### **4.1 Watchtower 简介**

Watchtower 是一个用于自动更新 Docker 容器的工具：
- **自动检测**：定期检查镜像更新
- **自动更新**：发现新版本时自动拉取并重启
- **通知支持**：Email、Slack、Discord 等
- **灵活配置**：可指定更新时间、容器白名单等

#### **4.2 docker-compose.yml 配置**

```yaml
version: '3.8'

services:
  # Aggregator 主服务
  aggregator:
    image: wzdnzd/aggregator:latest  # 使用 latest 标签以便自动更新
    container_name: aggregator
    restart: unless-stopped
    
    environment:
      - GIST_PAT=${GIST_PAT}
      - GIST_LINK=${GIST_LINK}
      - TZ=Asia/Shanghai
    
    volumes:
      - ./data:/aggregator/data
      - ./logs:/aggregator/logs
    
    # 添加标签，Watchtower 使用这些标签
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
      - "com.centurylinklabs.watchtower.scope=aggregator"
    
    networks:
      - aggregator-network

  # Watchtower 自动更新服务
  watchtower:
    image: containrrr/watchtower:latest
    container_name: aggregator-watchtower
    restart: unless-stopped
    
    volumes:
      # 需要访问 Docker socket
      - /var/run/docker.sock:/var/run/docker.sock
    
    environment:
      # 基础配置
      - WATCHTOWER_CLEANUP=true                    # 清理旧镜像
      - WATCHTOWER_INCLUDE_RESTARTING=true         # 包括重启中的容器
      - WATCHTOWER_INCLUDE_STOPPED=false           # 不包括已停止的容器
      - WATCHTOWER_REVIVE_STOPPED=false            # 不唤醒已停止的容器
      
      # 更新策略
      - WATCHTOWER_POLL_INTERVAL=86400             # 检查间隔：86400秒 = 24小时
      - WATCHTOWER_TIMEOUT=10s                     # 停止容器超时时间
      - WATCHTOWER_ROLLING_RESTART=true            # 滚动重启
      
      # 作用域（只监控 aggregator 容器）
      - WATCHTOWER_SCOPE=aggregator
      - WATCHTOWER_LABEL_ENABLE=true               # 只更新有标签的容器
      
      # 时间安排（可选，在特定时间更新）
      # - WATCHTOWER_SCHEDULE=0 0 2 * * *          # Cron 表达式：每天凌晨2点
      
      # 通知配置（Email）
      - WATCHTOWER_NOTIFICATIONS=email
      - WATCHTOWER_NOTIFICATION_EMAIL_FROM=${EMAIL_FROM}
      - WATCHTOWER_NOTIFICATION_EMAIL_TO=${EMAIL_TO}
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER=${EMAIL_SERVER}
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PORT=587
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_USER=${EMAIL_USER}
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PASSWORD=${EMAIL_PASSWORD}
      - WATCHTOWER_NOTIFICATION_EMAIL_DELAY=2      # 发送延迟（秒）
      
      # 时区
      - TZ=Asia/Shanghai
    
    labels:
      - "com.centurylinklabs.watchtower.scope=aggregator"
    
    networks:
      - aggregator-network

networks:
  aggregator-network:
    driver: bridge
```

#### **4.3 .env 配置**

```bash
# Aggregator 配置
GIST_PAT=ghp_your_token_here
GIST_LINK=your_username/your_gist_id

# Email 通知配置（Gmail 示例）
EMAIL_FROM=aggregator@yourdomain.com
EMAIL_TO=admin@yourdomain.com
EMAIL_SERVER=smtp.gmail.com
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

# 时区
TZ=Asia/Shanghai
```

#### **4.4 Gmail App Password 配置**

如果使用 Gmail 发送通知邮件：

1. 启用两步验证：[Google Account Security](https://myaccount.google.com/security)
2. 生成应用专用密码：[App Passwords](https://myaccount.google.com/apppasswords)
3. 选择 "Mail" 和 "Other (Custom name)"
4. 生成密码并复制到 `.env` 文件的 `EMAIL_PASSWORD`

#### **4.5 其他通知方式**

**Slack 通知**：

```yaml
environment:
  - WATCHTOWER_NOTIFICATIONS=slack
  - WATCHTOWER_NOTIFICATION_SLACK_HOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
  - WATCHTOWER_NOTIFICATION_SLACK_IDENTIFIER=aggregator-watchtower
  - WATCHTOWER_NOTIFICATION_SLACK_CHANNEL=#alerts
```

**Webhook 通知**：

```yaml
environment:
  - WATCHTOWER_NOTIFICATIONS=shoutrrr
  - WATCHTOWER_NOTIFICATION_URL=generic+https://your-webhook-url.com/notify?title=Aggregator+Update
```

**Telegram 通知**：

```yaml
environment:
  - WATCHTOWER_NOTIFICATIONS=shoutrrr
  - WATCHTOWER_NOTIFICATION_URL=telegram://${TELEGRAM_TOKEN}@telegram?chats=${TELEGRAM_CHAT_ID}
```

#### **4.6 启动和验证**

```bash
# 启动服务
docker-compose up -d

# 查看 Watchtower 日志
docker-compose logs -f watchtower

# 手动触发更新（测试）
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower --run-once --cleanup aggregator

# 查看更新记录
docker-compose logs watchtower | grep "Updated"
```

#### **4.7 高级配置**

**定时更新（Cron 表达式）**：

```yaml
environment:
  # 每天凌晨 2 点检查并更新
  - WATCHTOWER_SCHEDULE=0 0 2 * * *
  
  # 每周一凌晨 3 点检查并更新
  - WATCHTOWER_SCHEDULE=0 0 3 * * MON
  
  # 每月 1 号凌晨 4 点检查并更新
  - WATCHTOWER_SCHEDULE=0 0 4 1 * *
```

**只通知不更新（测试模式）**：

```yaml
environment:
  - WATCHTOWER_MONITOR_ONLY=true  # 只监控，不执行更新
```

**白名单模式（只更新指定容器）**：

```bash
# 在 command 中指定容器名称
command: aggregator other-container
```

#### **4.8 回滚策略**

如果更新后出现问题，可以快速回滚：

```bash
# 查看镜像历史
docker images wzdnzd/aggregator

# 回滚到之前的版本
docker-compose down
docker tag wzdnzd/aggregator:<old-image-id> wzdnzd/aggregator:latest
docker-compose up -d

# 或使用特定版本
# 修改 docker-compose.yml 中的 image 为特定版本号
image: wzdnzd/aggregator:v1.0.0
docker-compose up -d
```

#### **4.9 监控和告警**

创建监控脚本 `/opt/aggregator/scripts/monitor-updates.sh`：

```bash
#!/bin/bash
# 监控 Watchtower 更新记录

LOG_FILE="/var/lib/docker/containers/$(docker inspect -f '{{.Id}}' aggregator-watchtower)/aggregator-watchtower-json.log"
WEBHOOK_URL="${WEBHOOK_URL:-}"

# 检查最近的更新
RECENT_UPDATES=$(docker logs aggregator-watchtower --since 24h | grep -c "Updated")

if [ "$RECENT_UPDATES" -gt 0 ]; then
    echo "✅ 检测到 $RECENT_UPDATES 次更新"
    
    # 发送通知
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" -d "Aggregator 已自动更新 $RECENT_UPDATES 次"
    fi
else
    echo "ℹ️  最近24小时无更新"
fi
```

---

### 场景5: 高可用多实例部署

**适用场景**：高并发、高可用性要求、生产环境、多服务器集群

**特点**：负载均衡、故障转移、水平扩展、健康检查

#### **5.1 架构设计**

```
                    ┌─────────────┐
                    │ Load Balancer│
                    │   (Nginx)   │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
    │Instance1│       │Instance2│      │Instance3│
    │  Node1  │       │  Node2  │      │  Node3  │
    └────┬────┘       └────┬────┘      └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────┐
                    │Shared Redis │
                    │   (Upstash) │
                    └─────────────┘
                           │
                    ┌──────▼──────┐
                    │GitHub Gist  │
                    └─────────────┘
```

#### **5.2 Docker Swarm 部署**

Docker Swarm 提供了简单的集群管理和服务编排。

**初始化 Swarm 集群**：

```bash
# 在主节点上初始化 Swarm
docker swarm init --advertise-addr <MANAGER-IP>

# 输出示例：
# docker swarm join --token SWMTKN-1-xxxxx <MANAGER-IP>:2377

# 在工作节点上加入 Swarm
docker swarm join --token SWMTKN-1-xxxxx <MANAGER-IP>:2377

# 查看节点状态
docker node ls
```

**创建 docker-compose.swarm.yml**：

```yaml
version: '3.8'

services:
  aggregator:
    image: wzdnzd/aggregator:latest
    
    environment:
      - GIST_PAT=${GIST_PAT}
      - GIST_LINK=${GIST_LINK}
      - REDIS_URL=${REDIS_URL}
      - TZ=Asia/Shanghai
    
    networks:
      - aggregator-network
    
    # Swarm 部署配置
    deploy:
      # 副本数
      replicas: 3
      
      # 更新策略
      update_config:
        parallelism: 1         # 每次更新1个实例
        delay: 10s             # 更新间隔
        failure_action: rollback  # 失败时回滚
        monitor: 60s           # 监控时间
      
      # 回滚策略
      rollback_config:
        parallelism: 1
        delay: 10s
      
      # 重启策略
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      
      # 资源限制
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      
      # 放置约束（确保每个节点只有一个实例）
      placement:
        max_replicas_per_node: 1
        constraints:
          - node.role == worker
      
      # 标签
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.aggregator.rule=Host(`aggregator.yourdomain.com`)"
        - "traefik.http.services.aggregator.loadbalancer.server.port=8080"

networks:
  aggregator-network:
    driver: overlay
    attachable: true

# Swarm 使用 named volumes
volumes:
  aggregator-data:
    driver: local
```

**部署到 Swarm**：

```bash
# 部署服务栈
docker stack deploy -c docker-compose.swarm.yml aggregator

# 查看服务状态
docker service ls

# 查看服务详情
docker service ps aggregator_aggregator

# 查看服务日志
docker service logs -f aggregator_aggregator

# 扩展服务（增加到5个副本）
docker service scale aggregator_aggregator=5

# 更新服务
docker service update --image wzdnzd/aggregator:v1.1.0 aggregator_aggregator

# 回滚服务
docker service rollback aggregator_aggregator

# 删除服务栈
docker stack rm aggregator
```

#### **5.3 Kubernetes 部署**

对于更复杂的生产环境，可以使用 Kubernetes。

**创建 k8s-deployment.yaml**：

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: aggregator

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: aggregator-config
  namespace: aggregator
data:
  TZ: "Asia/Shanghai"

---
apiVersion: v1
kind: Secret
metadata:
  name: aggregator-secrets
  namespace: aggregator
type: Opaque
stringData:
  GIST_PAT: "ghp_your_token_here"
  GIST_LINK: "your_username/your_gist_id"
  REDIS_URL: "redis://your-redis-url"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aggregator
  namespace: aggregator
  labels:
    app: aggregator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aggregator
  template:
    metadata:
      labels:
        app: aggregator
    spec:
      containers:
      - name: aggregator
        image: wzdnzd/aggregator:latest
        imagePullPolicy: Always
        
        env:
        - name: GIST_PAT
          valueFrom:
            secretKeyRef:
              name: aggregator-secrets
              key: GIST_PAT
        - name: GIST_LINK
          valueFrom:
            secretKeyRef:
              name: aggregator-secrets
              key: GIST_LINK
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: aggregator-secrets
              key: REDIS_URL
        - name: TZ
          valueFrom:
            configMapKeyRef:
              name: aggregator-config
              key: TZ
        
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "500m"
            memory: "512Mi"
        
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        volumeMounts:
        - name: data
          mountPath: /aggregator/data
        - name: logs
          mountPath: /aggregator/logs
      
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: aggregator-data-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: aggregator-logs-pvc

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: aggregator-data-pvc
  namespace: aggregator
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: aggregator-logs-pvc
  namespace: aggregator
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: aggregator-hpa
  namespace: aggregator
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: aggregator
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**部署到 Kubernetes**：

```bash
# 应用配置
kubectl apply -f k8s-deployment.yaml

# 查看部署状态
kubectl get all -n aggregator

# 查看 Pod 状态
kubectl get pods -n aggregator

# 查看日志
kubectl logs -f -l app=aggregator -n aggregator

# 扩展 Pod 数量
kubectl scale deployment aggregator --replicas=5 -n aggregator

# 更新镜像
kubectl set image deployment/aggregator aggregator=wzdnzd/aggregator:v1.1.0 -n aggregator

# 查看滚动更新状态
kubectl rollout status deployment/aggregator -n aggregator

# 回滚
kubectl rollout undo deployment/aggregator -n aggregator

# 查看 HPA 状态
kubectl get hpa -n aggregator

# 删除部署
kubectl delete namespace aggregator
```

#### **5.4 高可用性配置建议**

1. **使用共享存储**：NFS、Ceph、GlusterFS
2. **配置健康检查**：确保故障实例自动重启
3. **设置资源限制**：防止单个实例占用过多资源
4. **监控和告警**：Prometheus + Grafana
5. **备份策略**：定期备份数据和配置
6. **负载均衡**：Nginx、HAProxy、Traefik
7. **日志聚合**：ELK、Loki、Fluentd

---

## Part 4: 配置管理详解

### 环境变量详细说明

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|-------|------|--------|------|------|
| `GIST_PAT` | ✅ | - | GitHub Personal Access Token | `ghp_1234567890abcdefghijk...` |
| `GIST_LINK` | ✅ | - | Gist 用户名/ID（格式：`username/gist_id`） | `wzdnzd/abc123def456...` |
| `CUSTOMIZE_LINK` | ❌ | - | 自定义机场列表 URL | `https://example.com/airports.txt` |
| `ENABLE_SPECIAL_PROTOCOLS` | ❌ | `false` | 是否启用特殊协议（vless, hysteria等） | `true` 或 `false` |
| `REDIS_URL` | ❌ | - | Redis 连接字符串 | `redis://localhost:6379` |
| `TZ` | ❌ | `UTC` | 时区设置 | `Asia/Shanghai` |
| `PYTHONUNBUFFERED` | ❌ | `0` | Python 输出缓冲（建议设为1） | `1` |
| `PYTHONDONTWRITEBYTECODE` | ❌ | `0` | 禁止生成 .pyc 文件（建议设为1） | `1` |

### 数据卷管理

#### **持久化目录**

```bash
# 数据目录结构
/aggregator
├── data/          # 持久化数据
│   ├── proxies/   # 代理数据
│   ├── cache/     # 缓存文件
│   └── temp/      # 临时文件
├── logs/          # 日志文件
│   ├── collect.log
│   ├── process.log
│   └── error.log
└── config/        # 配置文件（可选）
    └── process-config.json
```

#### **备份和恢复**

```bash
# 备份数据
docker run --rm \
  -v aggregator-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/aggregator-data-$(date +%Y%m%d).tar.gz /data

# 恢复数据
docker run --rm \
  -v aggregator-data:/data \
  -v $(pwd):/backup \
  alpine sh -c "cd / && tar xzf /backup/aggregator-data-20240101.tar.gz"
```

#### **权限管理**

```bash
# 设置正确的权限
docker exec aggregator chown -R root:root /aggregator/data
docker exec aggregator chmod -R 755 /aggregator/data

# 查看权限
docker exec aggregator ls -la /aggregator/
```

### 网络配置

#### **端口映射**

Aggregator 默认不需要对外开放端口，但如果需要：

```yaml
services:
  aggregator:
    ports:
      - "8080:8080"  # HTTP API（如果实现）
```

#### **容器网络模式**

```yaml
# 桥接模式（默认）
network_mode: bridge

# 主机模式（共享主机网络）
network_mode: host

# 无网络
network_mode: none
```

### 资源限制配置

```yaml
deploy:
  resources:
    limits:
      cpus: '2'      # 最大2个CPU核心
      memory: 2G     # 最大2GB内存
    reservations:
      cpus: '0.5'    # 预留0.5个CPU
      memory: 512M   # 预留512MB内存
```

---

## Part 5: 常见问题

**Q1: 如何选择镜像源（GHCR vs Docker Hub）？**

A: 
- 如果在国内，推荐 Docker Hub（配合镜像加速器）
- 如果在国外，两者差不多，GHCR 与 GitHub 集成更好
- 生产环境建议同时配置两个源作为备份

**Q2: 如何查看容器内的文件？**

```bash
docker exec -it aggregator /bin/bash
ls -la /aggregator/data
```

**Q3: 如何自定义运行命令？**

修改 `docker-compose.yml` 中的 `command`：

```yaml
command: ["python", "-u", "subscribe/process.py", "-s", "/aggregator/config/my-config.json"]
```

**Q4: 如何定时运行？**

使用 cron 或在 `docker-compose.yml` 中配置定时任务。

---

## Part 6: 下一步

- 📖 阅读 [DEBUG.md](./DEBUG.md) 了解调试技巧
- 📋 查看 [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) 快速参考
- 🔧 阅读 [BEST_PRACTICES.md](./BEST_PRACTICES.md) 最佳实践
- 🌳 查看 [TROUBLESHOOTING_TREE.md](./TROUBLESHOOTING_TREE.md) 问题诊断

---

**📝 文档更新**: 2024-11  
**✍️ 作者**: wzdnzd  
**📧 反馈**: [提交 Issue](https://github.com/wzdnzd/aggregator/issues)
