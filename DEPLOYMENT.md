# Aggregator Docker 部署指南

## 目录

- [前置要求](#前置要求)
- [快速启动（5分钟）](#快速启动5分钟)
- [详细安装步骤](#详细安装步骤)
- [常见配置场景](#常见配置场景)
- [日志和监控](#日志和监控)
- [故障排查](#故障排查)
- [升级和维护](#升级和维护)
- [安全建议](#安全建议)
- [高级配置](#高级配置)

---

## 前置要求

### 系统要求

#### Docker 版本
- **Docker**: >= 20.10
- **Docker Compose**: >= 1.29
  
  查看版本命令：
  ```bash
  docker --version
  docker-compose --version
  ```

#### 硬件要求
- **CPU**: 2核心 (推荐 4核以上)
- **内存**: 2GB 最小 (推荐 4GB以上)
- **磁盘空间**: 5GB 最小 (推荐 20GB以上，用于存储代理数据)
- **网络**: 稳定的互联网连接，用于爬虫获取代理源

#### 操作系统
- Linux (Ubuntu 18.04+, CentOS 7+, Debian 10+)
- macOS (10.15+)
- Windows 10+ (使用WSL2或Docker Desktop)

### 网络要求
- 能够访问互联网（爬虫需要访问多个代理源）
- 如果配置Gist上传，需要能访问 github.com
- 如果使用Upstash Redis，需要能访问 upstash.com
- 代理测试需要良好的网络连接

### 可选依赖
- **Redis** (本地或远程) - 用于缓存和持久化存储
- **Upstash Redis** - 云端Redis服务（无需本地部署）
- **GitHub Account** - 用于上传代理到Gist

---

## 快速启动（5分钟）

### 第1步：准备环境

```bash
# 检查Docker是否安装
docker --version

# 检查Docker Compose是否安装
docker-compose --version

# 创建项目目录
mkdir -p ~/aggregator
cd ~/aggregator
```

### 第2步：获取配置文件

```bash
# 方式一：克隆仓库（推荐）
git clone https://github.com/wzdnzd/aggregator.git .

# 方式二：下载docker-compose和配置文件
# 从https://github.com/wzdnzd/aggregator下载以下文件：
# - Dockerfile
# - docker-compose.yml
# - .env.example
# - requirements.txt
# - subscribe/ 目录
```

### 第3步：配置环境变量

```bash
# 复制模板文件
cp .env.example .env

# 编辑配置（使用你喜欢的编辑器，例如nano）
nano .env

# 至少需要填写以下内容：
# GIST_PAT=你的GitHub令牌
# GIST_LINK=用户名/gist-id
```

### 第4步：启动服务

```bash
# 构建镜像（首次运行）
docker-compose build

# 启动容器
docker-compose up -d

# 查看启动日志
docker-compose logs -f aggregator

# 查看服务状态
docker-compose ps
```

### 第5步：验证安装

```bash
# 检查容器是否运行
docker-compose ps
# 期望输出：aggregator 容器状态为 Up

# 查看日志确认启动成功
docker-compose logs aggregator | grep -E "SUCCESS|ERROR|completed"

# 检查输出目录是否生成文件
ls -la output/

# 查看生成的clash.yaml
cat output/clash.yaml | head -20
```

> **完成！** 服务已成功启动，代理爬虫将按照计划任务自动运行

---

## 详细安装步骤

### Step 1: 环境准备

#### 1.1 安装Docker

**Ubuntu/Debian:**
```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加当前用户到docker组（可选，避免每次都用sudo）
sudo usermod -aG docker $USER
newgrp docker
```

**CentOS/RHEL:**
```bash
# 安装必要工具
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install docker-ce docker-ce-cli containerd.io -y

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker
```

**macOS:**
```bash
# 使用Homebrew安装
brew install docker docker-compose

# 或下载Docker Desktop
# https://www.docker.com/products/docker-desktop/
```

#### 1.2 验证安装

```bash
# 验证Docker
docker run hello-world

# 验证Docker Compose
docker-compose --version

# 检查磁盘空间
df -h

# 检查内存
free -h
```

### Step 2: 配置准备

#### 2.1 获取.env.example文件说明

所有支持的环境变量详见 `.env.example` 文件中的详细说明。主要配置项包括：

| 配置项 | 说明 | 示例 |
|-------|------|------|
| GIST_PAT | GitHub访问令牌 | ghp_xxxx |
| GIST_LINK | Gist位置 (username/gist-id) | octocat/abc123 |
| CONCURRENT_LIMIT | 并发测试数 | 10-50 |
| STORAGE_TYPE | 存储后端 | file / redis / upstash |
| AUTO_RUN_ON_START | 启动时自动运行 | true / false |

#### 2.2 编辑.env配置文件

```bash
# 创建自己的.env文件
cp .env.example .env

# 使用编辑器编辑
nano .env
# 或
vim .env
# 或
code .env  # VS Code
```

#### 2.3 获取GitHub Token

用于上传到GitHub Gist的配置：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 配置权限（需要 `gist` 权限）
4. 生成token，复制并保存到 `.env` 的 `GIST_PAT` 变量

#### 2.4 获取或创建Gist

1. 访问 https://gist.github.com/
2. 点击 "Create a new gist"
3. 创建一个新的Gist（可以是空文件）
4. 获取Gist ID（URL最后的ID）
5. 填写到 `.env` 的 `GIST_LINK` 变量（格式：username/gist-id）

#### 2.5 关键配置说明

**基础配置：**
```env
# 日志级别选择：DEBUG（开发）、INFO（推荐）、WARNING、ERROR
AGGREGATOR_LOG_LEVEL=INFO

# 是否启用调试模式（开发用，生产不推荐）
AGGREGATOR_DEBUG=false
```

**代理测试配置：**
```env
# 并发限制：根据服务器性能调整
# - 低端服务器（1核2GB）: 5-10
# - 中端服务器（2核4GB）: 10-20
# - 高端服务器（4核8GB）: 20-50
CONCURRENT_LIMIT=10

# 测试超时时间（毫秒）：
# - 低速网络: 10000 (10秒)
# - 中等网络: 5000 (5秒)
# - 高速网络: 3000 (3秒)
MAX_LATENCY=5000
```

**计划任务配置：**
```env
# Cron表达式示例：
# 0 */6 * * *      每6小时
# 0 0 * * *        每天0点（UTC）
# 0 3,9,15,21 * * * 每天4个时间点（建议用于生产）
# */30 * * * *     每30分钟
CRON_SCHEDULE=0 */6 * * *

# 启动时立即运行一次（快速获得初始数据）
AUTO_RUN_ON_START=true
```

### Step 3: 启动服务

#### 3.1 构建镜像

```bash
# 首次运行或更新代码后需要重新构建
docker-compose build

# 如果速度太慢，可指定pip镜像（中国用户推荐）
docker-compose build --build-arg PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"

# 查看已构建的镜像
docker images | grep aggregator
```

#### 3.2 启动容器

```bash
# 后台启动
docker-compose up -d

# 前台启动（用于调试，按Ctrl+C停止）
docker-compose up

# 重启容器
docker-compose restart

# 停止容器
docker-compose stop

# 删除容器（保留数据卷）
docker-compose down

# 完全删除（包括数据卷）
docker-compose down -v
```

#### 3.3 查看日志

```bash
# 实时查看日志
docker-compose logs -f aggregator

# 查看最后100行日志
docker-compose logs -n 100 aggregator

# 查看指定时间段的日志
docker-compose logs --since 2024-01-01 aggregator

# 导出日志到文件
docker-compose logs aggregator > logs.txt
```

#### 3.4 检查服务状态

```bash
# 查看运行的容器
docker-compose ps

# 查看容器详细信息
docker ps -a

# 查看容器资源使用情况
docker stats aggregator

# 进入容器内部（调试用）
docker-compose exec aggregator bash
```

### Step 4: 验证安装

#### 4.1 检查容器运行状态

```bash
# 容器应该处于Up状态
docker-compose ps

# 预期输出：
# NAME      IMAGE                    STATUS
# aggregator  wzdnzd/aggregator:latest  Up X minutes
```

#### 4.2 验证日志输出

```bash
# 查看是否有错误
docker-compose logs aggregator | grep -i error

# 查看初始化完成信息
docker-compose logs aggregator | grep -E "SUCCESS|COMPLETED|READY"
```

#### 4.3 验证数据生成

```bash
# 检查输出目录
ls -la output/

# 预期输出应该包含：
# - clash.yaml
# - v2ray.json (如果启用)
# - proxies.json 或类似文件

# 查看生成的Clash配置
cat output/clash.yaml | head -30

# 检查代理数量
grep -c "name:" output/clash.yaml
```

#### 4.4 验证Gist上传（如果配置了）

```bash
# 访问你的Gist URL
# https://gist.github.com/username/gist-id

# 或使用API查询
curl -s "https://api.github.com/gists/你的gist-id" | grep "updated_at"
```

### Step 5: 后续操作

#### 5.1 从容器复制数据

```bash
# 将代理文件复制到本地
docker-compose cp aggregator:/aggregator/output/clash.yaml ./my-clash.yaml

# 查看详细配置
cat my-clash.yaml | head -50
```

#### 5.2 配置客户端使用

**Clash客户端：**
- 打开Clash配置管理
- 添加订阅URL：`http://localhost:8080/clash.yaml` 或文件路径
- 选择代理组，启用代理

**其他客户端：**
- 根据生成的配置文件格式选择对应客户端
- 导入配置或订阅URL

---

## 常见配置场景

### 场景1: 本地单机部署（最简配置）

**用途**：个人使用或测试环境

**环境要求**：任何能运行Docker的PC/服务器

**.env配置示例：**
```env
# 最小必须配置
GIST_PAT=              # 留空则本地存储
GIST_LINK=
CONCURRENT_LIMIT=5     # 本机性能有限，使用较低的并发
TEST_COUNT=1
MAX_LATENCY=8000       # 宽松的延迟要求

# 存储
STORAGE_TYPE=file      # 使用本地文件存储

# 计划任务
AUTO_RUN_ON_START=true # 启动时立即获取数据
CRON_SCHEDULE=0 */12 * * *  # 12小时更新一次
```

**docker-compose.yml配置：**
```yaml
# 使用默认配置，注释掉Redis服务
services:
  aggregator:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env
    volumes:
      - ./config:/aggregator/subscribe/config
      - ./output:/aggregator/output
      - ./data:/aggregator/data
      - ./logs:/aggregator/logs
    restart: unless-stopped
    # 注释掉Redis依赖
    # depends_on:
    #   - redis

# 注释掉Redis服务
# redis:
#   ...
```

**启动步骤：**
```bash
cp .env.example .env
# 编辑.env，配置GIST_PAT和GIST_LINK（可选）
docker-compose build
docker-compose up -d
docker-compose logs -f aggregator
```

**数据访问：**
```bash
# 查看生成的文件
ls -la output/

# 使用生成的代理
cat output/clash.yaml | grep -A 5 "proxies:"

# 监视日志
docker-compose logs -f
```

### 场景2: 生产部署（带Redis缓存）

**用途**：生产环境，需要高性能和数据持久化

**环境要求**：
- 服务器：4核+ CPU, 8GB+ 内存, 50GB+ 磁盘
- 网络：稳定的互联网连接
- 是否上传到Gist可选

**.env配置示例：**
```env
# 日志
AGGREGATOR_LOG_LEVEL=INFO
AGGREGATOR_DEBUG=false

# GitHub配置（可选）
GIST_PAT=ghp_your_token_here
GIST_LINK=your-username/your-gist-id

# 代理测试（生产推荐参数）
CONCURRENT_LIMIT=30        # 中等并发
TEST_COUNT=2              # 测试2次确保准确
MAX_LATENCY=5000          # 严格的延迟要求
PING_TIMEOUT=3
HTTP_TIMEOUT=10
RETRY_TIMES=2

# 存储（使用Redis）
STORAGE_TYPE=redis
REDIS_URL=redis://redis:6379/0

# 计划任务（生产推荐）
CRON_SCHEDULE=0 3,9,15,21 * * *  # 每天4个时间点
AUTO_RUN_ON_START=true

# 通知配置
NOTIFICATION_ENABLED=true
NOTIFICATION_WEBHOOKS=https://your-webhook-url

# 输出
ENABLE_CLASH_GENERATION=true
ENABLE_V2RAY_GENERATION=true
```

**docker-compose.yml配置调整：**
```yaml
services:
  aggregator:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
    depends_on:
      - redis

  redis:
    # 完整启用Redis服务
    image: redis:7-alpine
    container_name: aggregator-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

**启动命令：**
```bash
# 构建镜像
docker-compose build

# 启动包括Redis的完整栈
docker-compose up -d

# 验证两个服务都在运行
docker-compose ps

# 检查Redis连接
docker-compose exec redis redis-cli ping
# 预期输出：PONG
```

**性能优化建议：**
```bash
# 监控资源使用
watch -n 1 'docker stats --no-stream'

# 查看Redis内存使用
docker-compose exec redis redis-cli info memory

# 检查爬虫性能
docker-compose logs -f aggregator | grep -E "processed|failed|success"
```

### 场景3: 高并发场景

**用途**：需要快速获取大量代理的场景

**硬件需求**：
- CPU: 8核+
- 内存: 16GB+
- 网络: 1Gbps+

**.env配置示例：**
```env
# 高并发参数
CONCURRENT_LIMIT=100       # 高并发数
TEST_COUNT=1              # 快速测试
MAX_LATENCY=3000          # 严格筛选
HTTP_TIMEOUT=5

# Redis用于缓存和去重
STORAGE_TYPE=redis
REDIS_URL=redis://redis:6379/0

# 大量数据处理
MAX_PROXIES_PER_CRAWL=50000
ENABLE_DEDUPLICATION=true

# 频繁更新
CRON_SCHEDULE=*/30 * * * *  # 30分钟一次

# 监控
AGGREGATOR_LOG_LEVEL=DEBUG
```

**Docker资源配置：**
```yaml
aggregator:
  deploy:
    resources:
      limits:
        cpus: '8'
        memory: 16G
      reservations:
        cpus: '4'
        memory: 8G

redis:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
```

**性能监控：**
```bash
# 实时监控
docker stats

# 查看爬虫速率
docker-compose logs -f aggregator | grep -oP '\d+\s*proxies?/s'

# 监控Redis内存
watch -n 1 'docker exec aggregator-redis redis-cli info memory | grep used'
```

### 场景4: 与外部服务集成

#### 4.1 使用Upstash Redis（云端Redis）

**配置步骤：**
1. 注册Upstash账户：https://upstash.com
2. 创建Redis数据库，获取连接URL
3. 配置.env：

```env
STORAGE_TYPE=upstash
UPSTASH_REDIS_URL=redis://default:your-password@endpoint.upstash.io:port
```

#### 4.2 配置WeCom（企业微信）通知

```env
NOTIFICATION_ENABLED=true
NOTIFICATION_WEBHOOKS=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx
```

#### 4.3 配置钉钉通知

```env
NOTIFICATION_ENABLED=true
NOTIFICATION_WEBHOOKS=https://hook.dingding.com/access/content/xxxxx
```

---

## 日志和监控

### 查看日志

#### 实时日志
```bash
# 查看实时日志
docker-compose logs -f aggregator

# 只查看错误
docker-compose logs aggregator | grep ERROR

# 查看最后N行
docker-compose logs -n 50 aggregator
```

#### 常见日志信息解读

```
# 成功开始爬虫
[INFO] Starting crawler...
[INFO] Crawling from source: https://...
[INFO] Found 100 proxies

# 测试进行中
[INFO] Testing proxies: 50%
[INFO] Testing proxies: 100%

# 完成处理
[INFO] Processing complete
[INFO] Results saved to /aggregator/output
[INFO] Uploaded to Gist successfully

# 错误示例
[ERROR] Failed to connect to Redis
[ERROR] Gist upload failed: Invalid token
[WARNING] Proxy source timeout
```

### 性能指标观察

```bash
# 查看Docker资源使用
docker stats aggregator

# 预期健康的资源占用：
# - CPU: 30-50% (高峰期)
# - 内存: 200-500MB (根据并发数调整)

# 查看处理速率
docker-compose logs aggregator | grep -oP 'processed \K\d+'

# 预期速率：
# - 单机: 1000-5000 proxies/s
# - 高并发: 5000-20000 proxies/s
```

### 监控存储

```bash
# 如果使用Redis，检查内存
docker-compose exec redis redis-cli info memory

# 检查本地存储
du -sh data/ output/ logs/

# 预期大小：
# - data/: 100MB-1GB (缓存)
# - output/: 10-100MB (生成文件)
# - logs/: 50-500MB (日志)
```

---

## 故障排查

### 常见问题 & 解决方案

#### 问题1: 容器无法启动

**症状**：
```bash
docker-compose up
# 容器立即退出或Error状态
```

**原因与解决方案：**

```bash
# 1. 查看错误日志
docker-compose logs aggregator

# 2. 常见错误：

# 错误: ModuleNotFoundError: No module named 'yaml'
# 解决: pip依赖未安装，重新构建镜像
docker-compose build --no-cache
docker-compose up -d

# 错误: Permission denied
# 解决: 目录权限问题
sudo chown -R $USER:$USER output data logs config

# 错误: Address already in use
# 解决: 端口被占用，修改docker-compose.yml中的ports
# 将 "8080:8080" 改为 "8081:8080"

# 错误: No such file or directory
# 解决: 文件路径错误，检查COPY指令的路径
docker-compose build --no-cache

# 3. 查看文件系统
docker-compose exec aggregator ls -la /aggregator

# 4. 验证环境变量
docker-compose exec aggregator env | grep AGGREGATOR
```

#### 问题2: 代理测试失败

**症状**：
```
[ERROR] Failed to test proxy
[WARNING] All proxies failed
```

**排查步骤：**

```bash
# 1. 检查网络连接
docker-compose exec aggregator ping -c 4 8.8.8.8
# 应该有响应

# 2. 检查代理源可用性
docker-compose exec aggregator curl -s https://example.com/proxies.txt | head

# 3. 调整超时参数 - 编辑.env
MAX_LATENCY=10000        # 增加延迟容限
HTTP_TIMEOUT=15          # 增加HTTP超时
PING_TIMEOUT=5           # 增加Ping超时

# 4. 降低并发限制
CONCURRENT_LIMIT=5       # 从10降低到5

# 5. 检查日志中的详细错误
docker-compose logs aggregator | grep -A 5 "FAILED"

# 6. 重启容器并观察
docker-compose restart
docker-compose logs -f aggregator
```

#### 问题3: 输出文件未生成

**症状**：
```bash
ls -la output/
# 输出目录为空或不存在
```

**排查步骤：**

```bash
# 1. 检查输出目录权限
ls -la output/
chmod 755 output/

# 2. 检查容器内输出目录
docker-compose exec aggregator ls -la /aggregator/output

# 3. 检查爬虫是否运行过
docker-compose logs aggregator | grep -E "START|COMPLETE"

# 4. 手动触发爬虫
docker-compose exec aggregator python subscribe/collect.py --all --overwrite

# 5. 检查是否生成了中间文件
docker-compose exec aggregator ls -la /aggregator/data

# 6. 检查存储配置
docker-compose exec aggregator env | grep STORAGE
```

#### 问题4: 高内存占用

**症状**：
```bash
docker stats
# 内存占用超过限制
```

**优化方案：**

```bash
# 1. 降低并发限制
# 编辑.env
CONCURRENT_LIMIT=5  # 从10降低到5

# 2. 减少单次处理的代理数
MAX_PROXIES_PER_CRAWL=1000  # 从10000降低

# 3. 启用数据去重减少存储
ENABLE_DEDUPLICATION=true

# 4. 清理旧数据
docker-compose exec aggregator rm -rf /aggregator/data/*

# 5. 如果使用Redis，清理过期key
docker-compose exec redis redis-cli FLUSHDB

# 6. 增加容器内存限制 (需修改docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 2G  # 从1G增加到2G
```

#### 问题5: Gist上传失败

**症状**：
```
[ERROR] Failed to upload to Gist
[ERROR] Invalid GitHub token
```

**排查步骤：**

```bash
# 1. 验证token格式和权限
echo $GIST_PAT
# 应该输出: ghp_xxxxxxxx...

# 2. 测试GitHub API连接
docker-compose exec aggregator curl -H "Authorization: token $GIST_PAT" \
  https://api.github.com/user

# 3. 验证Gist ID
curl -s "https://api.github.com/gists/your-gist-id" | head

# 4. 检查.env中的配置
cat .env | grep -E "GIST_PAT|GIST_LINK"

# 5. 更新token
# 访问 https://github.com/settings/tokens 重新生成token
# 更新.env文件中的GIST_PAT
docker-compose restart

# 6. 测试upload
docker-compose exec aggregator python -c \
  "import sys; sys.path.insert(0, '/aggregator'); \
   from subscribe import push; \
   p = push.PushToGist(token='$GIST_PAT'); \
   print('Token valid' if p else 'Token invalid')"
```

#### 问题6: Docker Compose命令失败

**症状**：
```
docker-compose: command not found
或
Cannot connect to Docker daemon
```

**解决方案：**

```bash
# 1. 检查Docker是否运行
sudo systemctl start docker
sudo systemctl status docker

# 2. 检查Docker Compose版本
# 新版本使用 docker compose (v2+)
docker compose --version

# 3. 如果是新版本，使用docker compose代替docker-compose
docker compose up -d

# 4. 添加当前用户到docker组（避免sudo）
sudo usermod -aG docker $USER
newgrp docker

# 5. 重新登录验证
exit
ssh user@host
docker ps
```

---

## 升级和维护

### 升级Aggregator版本

```bash
# 1. 停止运行的容器
docker-compose stop

# 2. 备份重要数据（可选但推荐）
cp -r output output.backup.$(date +%Y%m%d)
cp -r data data.backup.$(date +%Y%m%d)

# 3. 拉取最新代码
git pull origin main

# 4. 重新构建镜像（会自动使用最新代码）
docker-compose build --no-cache

# 5. 启动新版本
docker-compose up -d

# 6. 验证升级
docker-compose logs -f aggregator | head -20
```

### 数据迁移

```bash
# 1. 导出Redis数据（如果使用Redis）
docker-compose exec redis redis-cli BGSAVE
docker cp aggregator-redis:/data/dump.rdb ./redis-backup.rdb

# 2. 导出文件存储数据
tar -czf aggregator-data.tar.gz data/ output/

# 3. 在新服务器上导入
tar -xzf aggregator-data.tar.gz
docker cp redis-backup.rdb aggregator-redis:/data/dump.rdb
docker-compose exec redis redis-cli SHUTDOWN
docker-compose up -d redis
```

### 定期维护

```bash
# 每周执行一次：

# 1. 清理无用的Docker镜像和容器
docker system prune -a -f

# 2. 检查磁盘空间
df -h

# 3. 轮转日志（避免日志过大）
docker-compose logs --tail 0 > /dev/null

# 4. 备份关键数据
tar -czf backup-$(date +%Y%m%d).tar.gz output/

# 5. 检查服务健康
docker-compose exec aggregator curl -s http://localhost:8080/health

# 每月执行一次：

# 6. 完整备份
tar -czf full-backup-$(date +%Y%m%d).tar.gz data/ output/ config/

# 7. 更新依赖（检查更新）
# 修改requirements.txt后重建镜像
docker-compose build --no-cache

# 8. 清理过期数据
docker-compose exec aggregator find /aggregator/data -mtime +30 -delete
```

---

## 安全建议

### 环境变量敏感信息保护

```bash
# 1. 不要在docker-compose.yml中写入敏感信息
# ❌ 错误示例：
# env_file: .env  # 如果.env被提交到仓库

# ✅ 正确做法：
# - 使用.gitignore排除.env文件
echo ".env" >> .gitignore

# - 只提交.env.example
git add .env.example
git commit -m "Add .env.example template"

# 2. 保护.env文件权限
chmod 600 .env
chmod 600 .env.example

# 3. 使用docker secrets管理敏感信息（Swarm模式）
echo "your-github-token" | docker secret create gist_pat -

# 4. 定期轮转token
# 访问 https://github.com/settings/tokens
# 定期删除旧token，生成新token
```

### 容器权限设置

```bash
# 1. 以非root用户运行（已在Dockerfile中配置）
# Dockerfile已配置：USER aggregator

# 2. 检查容器用户
docker-compose exec aggregator id
# 应该显示非root用户

# 3. 限制容器权限
# docker-compose.yml已配置：
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE  # 仅限必要权限

# 4. 只读文件系统（可选）
# volumes:
#   - ./output:/aggregator/output:ro
```

### 网络隔离

```bash
# 1. 默认隐离在内部网络（已在docker-compose.yml配置）
networks:
  aggregator-network:
    driver: bridge

# 2. 限制端口暴露
# 只暴露必要的端口
ports:
  - "127.0.0.1:8080:8080"  # 仅本地访问

# 3. 使用防火墙进一步限制
sudo ufw allow 22/tcp
sudo ufw allow 8080/tcp from 127.0.0.1
sudo ufw enable

# 4. 使用代理反向代理容器
# Nginx配置示例
location /proxies {
  proxy_pass http://localhost:8080;
  auth_basic "Restricted";
  auth_basic_user_file /etc/nginx/.htpasswd;
}
```

### 数据备份策略

```bash
# 1. 定期自动备份脚本
#!/bin/bash
BACKUP_DIR="/backup/aggregator"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz \
  output/ data/ config/

# 删除7天前的备份
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

# 2. 添加到crontab
# 每天2:00 AM执行备份
0 2 * * * /path/to/backup.sh

# 3. 远程备份
# 上传到对象存储（S3、阿里云OSS等）
aws s3 cp $BACKUP_DIR/backup_$DATE.tar.gz \
  s3://my-backup-bucket/aggregator/

# 4. 验证备份完整性
tar -tzf backup.tar.gz | head
```

---

## 高级配置

### 自定义webhook通知

```bash
# 1. 配置.env
NOTIFICATION_ENABLED=true
NOTIFICATION_WEBHOOKS=https://your-server.com/webhook

# 2. 实现webhook处理程序
# 示例（Python Flask）：
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Aggregator notification: {data}")
    
    if data['status'] == 'success':
        print(f"Generated {data['proxy_count']} proxies")
    else:
        print(f"Error: {data['error']}")
    
    return {'status': 'ok'}

# 3. 启动webhook服务器
python app.py &
```

### 与Clash订阅管理系统集成

```bash
# 1. 配置生成Clash YAML
ENABLE_CLASH_GENERATION=true
CLASH_CONFIG_PATH=/aggregator/output/clash.yaml

# 2. 导出为订阅链接
# 使用HTTP服务器暴露输出目录
docker run -d \
  -v /path/to/aggregator/output:/usr/share/nginx/html:ro \
  -p 8081:80 \
  nginx:alpine

# 3. 在Clash中添加订阅
# http://server-ip:8081/clash.yaml

# 4. 自动更新订阅
# 在Clash管理面板配置自动更新周期（通常30分钟）
```

### 性能监控和告警

```bash
# 1. 使用Prometheus + Grafana监控
# docker-compose.yml中添加：
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  depends_on:
    - prometheus

# 2. 配置alerting规则
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'aggregator'
    static_configs:
      - targets: ['aggregator:8080']

# 3. 告警规则示例
# alert.rules.yml
groups:
  - name: aggregator
    rules:
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{name="aggregator"} > 1e9
        for: 5m
        annotations:
          summary: "High memory usage on aggregator"
```

### 多实例部署

```bash
# docker-compose.yml配置多个aggregator实例
services:
  aggregator-1:
    image: wzdnzd/aggregator:latest
    environment:
      - INSTANCE_ID=1
      - CRON_SCHEDULE=0 0 * * *     # 午夜
    
  aggregator-2:
    image: wzdnzd/aggregator:latest
    environment:
      - INSTANCE_ID=2
      - CRON_SCHEDULE=0 6 * * *     # 6点
    
  aggregator-3:
    image: wzdnzd/aggregator:latest
    environment:
      - INSTANCE_ID=3
      - CRON_SCHEDULE=0 12 * * *    # 中午
  
  # 共享Redis用于去重
  redis:
    image: redis:7-alpine
```

---

## 常见问题（FAQ）

**Q: 如何快速部署到云服务器？**

A: 使用以下一行命令：
```bash
git clone https://github.com/wzdnzd/aggregator.git && \
cd aggregator && \
cp .env.example .env && \
# 编辑.env填入配置 && \
docker-compose build && \
docker-compose up -d
```

**Q: 代理爬虫需要多长时间？**

A: 取决于：
- 并发数：通常5-30分钟，并发越高越快
- 代理源数量：多源需要更长时间
- 网络状况：网络不稳定会加长时间

建议在计划任务中错开运行时间，避免资源竞争。

**Q: 可以在Windows上运行吗？**

A: 可以，需要：
1. 安装Docker Desktop for Windows
2. 启用WSL 2 后端
3. 使用相同的docker-compose命令

**Q: 如何在多个服务器上同步代理？**

A: 建议方案：
1. 使用Upstash Redis（云端，自动同步）
2. 或使用共享存储（NFS、S3等）
3. 或通过Gist实现同步

**Q: 生成的代理什么时候更新？**

A: 根据CRON_SCHEDULE配置：
- 默认：每6小时
- 可以改为更频繁（如1小时）但会占用更多资源

---

## 获取帮助

- 📖 详见 [README.md](./README.md)
- 🐛 报告问题: https://github.com/wzdnzd/aggregator/issues
- 💬 讨论: https://github.com/wzdnzd/aggregator/discussions

---

最后更新: 2024年
