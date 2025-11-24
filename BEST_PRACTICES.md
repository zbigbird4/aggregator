# Aggregator 最佳实践指南

> **生产环境部署和运维的最佳实践**

---

## 📖 目录

- [1. 安全最佳实践](#1-安全最佳实践)
- [2. 性能优化](#2-性能优化)
- [3. 监控和告警](#3-监控和告警)
- [4. 备份策略](#4-备份策略)
- [5. 容器镜像更新策略](#5-容器镜像更新策略)
- [6. 日志管理](#6-日志管理)
- [7. 资源管理](#7-资源管理)
- [8. 网络配置](#8-网络配置)
- [9. 故障恢复](#9-故障恢复)
- [10. 开发环境实践](#10-开发环境实践)

---

## 1. 安全最佳实践

### 1.1 敏感信息管理

#### ✅ **使用环境变量而非硬编码**

❌ **不好的做法**：
```yaml
environment:
  - GIST_PAT=ghp_1234567890abcdefghijk  # 硬编码在配置文件中
```

✅ **好的做法**：
```yaml
environment:
  - GIST_PAT=${GIST_PAT}  # 从 .env 文件读取
```

#### ✅ **保护 .env 文件**

```bash
# 设置严格的文件权限
chmod 600 .env
chown $USER:$USER .env

# 确保 .env 在 .gitignore 中
echo ".env" >> .gitignore

# 验证权限
ls -la .env
# 应该显示: -rw------- (600)
```

#### ✅ **使用 Docker Secrets（Swarm/Kubernetes）**

Docker Swarm 示例：
```bash
# 创建 secret
echo "ghp_your_token" | docker secret create gist_pat -

# 使用 secret
services:
  aggregator:
    secrets:
      - gist_pat
    environment:
      - GIST_PAT_FILE=/run/secrets/gist_pat

secrets:
  gist_pat:
    external: true
```

Kubernetes 示例：
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aggregator-secrets
type: Opaque
stringData:
  GIST_PAT: "ghp_your_token"
```

### 1.2 网络安全

#### ✅ **使用内部网络**

```yaml
services:
  aggregator:
    networks:
      - internal-network

networks:
  internal-network:
    internal: true  # 不允许外部访问
```

#### ✅ **最小化端口暴露**

```yaml
# Aggregator 默认不需要暴露端口
# 只在必要时暴露
services:
  aggregator:
    # ports: []  # 不暴露任何端口
```

#### ✅ **配置防火墙**

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # 只允许 SSH
sudo ufw enable

# 查看状态
sudo ufw status
```

### 1.3 容器安全

#### ✅ **以非 root 用户运行**

```dockerfile
# 在 Dockerfile 中
RUN useradd -m -u 1000 aggregator
USER aggregator
```

或在 docker-compose.yml 中：
```yaml
services:
  aggregator:
    user: "1000:1000"
```

#### ✅ **只读文件系统（可选）**

```yaml
services:
  aggregator:
    read_only: true
    tmpfs:
      - /tmp
      - /aggregator/data
```

#### ✅ **限制容器能力**

```yaml
services:
  aggregator:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # 只添加必需的能力
```

### 1.4 镜像安全

#### ✅ **使用固定版本标签**

❌ **不好的做法**：
```yaml
image: wzdnzd/aggregator:latest  # 生产环境不推荐
```

✅ **好的做法**：
```yaml
image: wzdnzd/aggregator:v1.0.0  # 使用固定版本
```

#### ✅ **定期扫描镜像漏洞**

```bash
# 使用 Trivy 扫描
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image wzdnzd/aggregator:latest

# 使用 Grype 扫描
grype wzdnzd/aggregator:latest

# 使用 Docker Scan
docker scan wzdnzd/aggregator:latest
```

#### ✅ **验证镜像签名**

```bash
# 启用 Docker Content Trust
export DOCKER_CONTENT_TRUST=1
docker pull wzdnzd/aggregator:latest
```

---

## 2. 性能优化

### 2.1 资源配置

#### ✅ **合理设置资源限制**

```yaml
services:
  aggregator:
    deploy:
      resources:
        limits:
          cpus: '2'         # 最大 2 个 CPU
          memory: 2G        # 最大 2GB 内存
        reservations:
          cpus: '1'         # 至少保证 1 个 CPU
          memory: 512M      # 至少保证 512MB 内存
```

**推荐配置（根据场景）**：

| 场景 | CPU 限制 | 内存限制 | 说明 |
|-----|---------|---------|------|
| **轻量使用** | 1 CPU | 1GB | 个人使用，代理少 |
| **中等使用** | 2 CPU | 2GB | 正常使用，适中代理量 |
| **重度使用** | 4 CPU | 4GB | 大量代理，高并发 |
| **企业级** | 8 CPU | 8GB | 生产环境，高可用 |

### 2.2 并发优化

#### ✅ **根据 CPU 核心数调整并发**

```bash
# 查看 CPU 核心数
nproc

# 并发数建议：CPU 核心数 × 2 到 4
# 例如：4 核 CPU，并发数可设为 8 到 16

# 使用自定义并发数
docker exec aggregator python -u subscribe/collect.py -n 16
```

#### ✅ **批量处理**

```python
# 在自定义配置中
{
  "batch_size": 100,          # 每批处理 100 个代理
  "max_concurrent": 32,       # 最大并发数
  "timeout": 5000             # 超时时间（毫秒）
}
```

### 2.3 存储优化

#### ✅ **使用 SSD 存储**

```yaml
volumes:
  aggregator-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/ssd/aggregator/data  # 挂载到 SSD
```

#### ✅ **使用卷缓存**

```yaml
volumes:
  - ./data:/aggregator/data:cached  # macOS/Windows 优化
```

### 2.4 网络优化

#### ✅ **使用 host 网络模式（Linux）**

```yaml
services:
  aggregator:
    network_mode: host  # 性能最好，但安全性较低
```

#### ✅ **禁用不必要的网络功能**

```yaml
services:
  aggregator:
    networks:
      aggregator-network:
        ipv6_address: false  # 如果不需要 IPv6
```

---

## 3. 监控和告警

### 3.1 健康检查

#### ✅ **配置容器健康检查**

```yaml
services:
  aggregator:
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s         # 每 30 秒检查一次
      timeout: 10s          # 超时时间
      retries: 3            # 失败 3 次认为不健康
      start_period: 30s     # 启动后 30 秒才开始检查
```

#### ✅ **自动重启策略**

```yaml
services:
  aggregator:
    restart: unless-stopped  # 推荐：除非手动停止，否则总是重启
    # restart: always        # 总是重启
    # restart: on-failure    # 只在失败时重启
```

### 3.2 资源监控

#### ✅ **使用 Prometheus + Grafana**

```yaml
# 添加 cAdvisor 监控容器
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker:/var/lib/docker:ro
    ports:
      - "8080:8080"

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
```

**prometheus.yml 配置**：
```yaml
scrape_configs:
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

### 3.3 日志监控

#### ✅ **配置日志告警**

创建 `/opt/aggregator/scripts/log-monitor.sh`：

```bash
#!/bin/bash
# 监控错误日志并告警

LOG_FILE="/opt/aggregator/logs/aggregator.log"
ERROR_THRESHOLD=10
WEBHOOK_URL="${WEBHOOK_URL:-}"

# 统计最近 1 小时的错误数
ERROR_COUNT=$(docker logs aggregator --since 1h 2>&1 | grep -c "ERROR")

if [ "$ERROR_COUNT" -gt "$ERROR_THRESHOLD" ]; then
    MESSAGE="⚠️ Aggregator 在过去 1 小时出现 $ERROR_COUNT 个错误"
    
    # 发送通知
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" \
          -H "Content-Type: application/json" \
          -d "{\"text\":\"$MESSAGE\"}"
    fi
    
    echo "$MESSAGE"
fi
```

定时运行：
```bash
# 每小时检查一次
0 * * * * /opt/aggregator/scripts/log-monitor.sh >> /opt/aggregator/logs/monitor.log 2>&1
```

### 3.4 告警通知

#### ✅ **配置 Email 通知**

使用 Watchtower 的邮件通知：

```yaml
services:
  watchtower:
    environment:
      - WATCHTOWER_NOTIFICATIONS=email
      - WATCHTOWER_NOTIFICATION_EMAIL_FROM=aggregator@yourdomain.com
      - WATCHTOWER_NOTIFICATION_EMAIL_TO=admin@yourdomain.com
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER=smtp.gmail.com
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PORT=587
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_USER=your_email@gmail.com
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PASSWORD=your_app_password
```

#### ✅ **配置 Webhook 通知**

```yaml
environment:
  - WATCHTOWER_NOTIFICATIONS=shoutrrr
  - WATCHTOWER_NOTIFICATION_URL=generic+https://your-webhook-url.com
```

支持的通知方式：
- Email
- Slack
- Discord
- Telegram
- Microsoft Teams
- Webhook (Generic)

---

## 4. 备份策略

### 4.1 自动备份

#### ✅ **每日自动备份脚本**

创建 `/opt/aggregator/scripts/daily-backup.sh`：

```bash
#!/bin/bash
set -e

BACKUP_DIR="/opt/aggregator/backups"
DATA_DIR="/opt/aggregator/data"
RETENTION_DAYS=30

# 创建备份
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

echo "📦 开始备份: $TIMESTAMP"

# 停止容器（可选，确保数据一致性）
docker-compose -f /opt/aggregator/docker-compose.yml stop aggregator

# 备份数据
tar -czf "$BACKUP_FILE" -C "$DATA_DIR" .

# 启动容器
docker-compose -f /opt/aggregator/docker-compose.yml start aggregator

# 验证备份
if [ -f "$BACKUP_FILE" ]; then
    echo "✅ 备份成功: $BACKUP_FILE"
    echo "📊 备份大小: $(du -sh "$BACKUP_FILE" | cut -f1)"
else
    echo "❌ 备份失败"
    exit 1
fi

# 删除旧备份
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "🗑️  已删除 $RETENTION_DAYS 天前的备份"

# 上传到远程（可选）
# rsync -avz "$BACKUP_FILE" user@remote:/backups/aggregator/
```

#### ✅ **配置定时任务**

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点备份
0 2 * * * /opt/aggregator/scripts/daily-backup.sh >> /opt/aggregator/logs/backup.log 2>&1

# 每周日凌晨 3 点备份到远程
0 3 * * 0 rsync -avz /opt/aggregator/backups/ user@remote:/backups/aggregator/
```

### 4.2 备份验证

#### ✅ **定期验证备份可恢复性**

创建 `/opt/aggregator/scripts/verify-backup.sh`：

```bash
#!/bin/bash
set -e

BACKUP_FILE="$1"
TEST_DIR="/tmp/backup-test-$$"

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file>"
    exit 1
fi

echo "🔍 验证备份: $BACKUP_FILE"

# 创建测试目录
mkdir -p "$TEST_DIR"

# 解压备份
tar -xzf "$BACKUP_FILE" -C "$TEST_DIR"

# 检查关键文件
if [ -f "$TEST_DIR/proxies.txt" ]; then
    echo "✅ proxies.txt 存在"
else
    echo "❌ proxies.txt 缺失"
    exit 1
fi

# 清理
rm -rf "$TEST_DIR"

echo "✅ 备份验证通过"
```

### 4.3 异地备份

#### ✅ **使用 rsync 同步到远程**

```bash
# 同步到远程服务器
rsync -avz --delete \
  /opt/aggregator/backups/ \
  user@remote:/backups/aggregator/

# 使用 SSH 密钥认证（推荐）
ssh-keygen -t rsa -b 4096
ssh-copy-id user@remote
```

#### ✅ **使用云存储（S3/OSS）**

```bash
# 安装 AWS CLI
pip install awscli

# 配置 AWS 凭证
aws configure

# 同步到 S3
aws s3 sync /opt/aggregator/backups/ s3://your-bucket/aggregator/backups/

# 或使用 rclone（支持多种云存储）
rclone sync /opt/aggregator/backups/ remote:aggregator/backups/
```

---

## 5. 容器镜像更新策略

### 5.1 手动更新

#### ✅ **有计划的更新流程**

```bash
#!/bin/bash
# 更新流程脚本

set -e

echo "📦 开始更新 Aggregator..."

# 1. 备份当前数据
echo "1️⃣ 备份数据..."
./scripts/daily-backup.sh

# 2. 拉取新镜像
echo "2️⃣ 拉取新镜像..."
docker pull wzdnzd/aggregator:latest

# 3. 停止旧容器
echo "3️⃣ 停止容器..."
docker-compose down

# 4. 启动新容器
echo "4️⃣ 启动容器..."
docker-compose up -d

# 5. 等待启动
sleep 10

# 6. 验证运行状态
echo "5️⃣ 验证状态..."
if docker ps | grep -q aggregator; then
    echo "✅ 更新成功"
    docker-compose logs --tail=20 aggregator
else
    echo "❌ 更新失败，正在回滚..."
    # 回滚到旧版本
    docker-compose down
    docker tag wzdnzd/aggregator:backup wzdnzd/aggregator:latest
    docker-compose up -d
    exit 1
fi

# 7. 清理旧镜像
echo "6️⃣ 清理旧镜像..."
docker image prune -a -f

echo "✅ 更新完成！"
```

### 5.2 自动更新（Watchtower）

#### ✅ **生产环境配置**

```yaml
services:
  watchtower:
    image: containrrr/watchtower:latest
    environment:
      # 每天凌晨 2 点检查更新
      - WATCHTOWER_SCHEDULE=0 0 2 * * *
      
      # 清理旧镜像
      - WATCHTOWER_CLEANUP=true
      
      # 只更新有标签的容器
      - WATCHTOWER_LABEL_ENABLE=true
      
      # 监控模式（只通知不更新）
      # - WATCHTOWER_MONITOR_ONLY=true
      
      # 通知配置
      - WATCHTOWER_NOTIFICATIONS=email
      - WATCHTOWER_NOTIFICATION_EMAIL_FROM=${EMAIL_FROM}
      - WATCHTOWER_NOTIFICATION_EMAIL_TO=${EMAIL_TO}
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER=${EMAIL_SERVER}
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PORT=587
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_USER=${EMAIL_USER}
      - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PASSWORD=${EMAIL_PASSWORD}
    
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

### 5.3 版本控制

#### ✅ **使用语义化版本**

```yaml
# 开发环境：使用 latest
image: wzdnzd/aggregator:latest

# 测试环境：使用主分支版本
image: wzdnzd/aggregator:main

# 生产环境：使用固定版本
image: wzdnzd/aggregator:v1.0.0

# 或使用次版本（接受补丁更新）
image: wzdnzd/aggregator:v1.0
```

---

## 6. 日志管理

### 6.1 日志轮转

#### ✅ **配置 Docker 日志轮转**

```yaml
services:
  aggregator:
    logging:
      driver: "json-file"
      options:
        max-size: "50m"      # 单个日志文件最大 50MB
        max-file: "10"       # 保留 10 个日志文件
        compress: "true"     # 压缩旧日志
```

#### ✅ **使用 logrotate**

创建 `/etc/logrotate.d/aggregator`：

```
/opt/aggregator/logs/*.log {
    daily                    # 每天轮转
    rotate 30                # 保留 30 天
    compress                 # 压缩旧日志
    delaycompress            # 延迟压缩（下次轮转时压缩）
    notifempty               # 空文件不轮转
    create 0640 root root    # 创建新文件的权限
    sharedscripts
    postrotate
        docker-compose -f /opt/aggregator/docker-compose.yml restart aggregator > /dev/null 2>&1 || true
    endscript
}
```

### 6.2 日志聚合

#### ✅ **使用 ELK Stack**

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  aggregator:
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://logstash:5000"
```

### 6.3 日志分析

#### ✅ **使用 lnav 分析日志**

```bash
# 安装 lnav
sudo apt-get install lnav

# 分析日志
docker-compose logs aggregator | lnav

# 或直接分析日志文件
lnav /opt/aggregator/logs/*.log
```

---

## 7. 资源管理

### 7.1 磁盘空间管理

#### ✅ **定期清理**

创建 `/opt/aggregator/scripts/cleanup.sh`：

```bash
#!/bin/bash
set -e

echo "🧹 开始清理..."

# 1. 清理 Docker 缓存
echo "1️⃣ 清理 Docker 缓存..."
docker system prune -a -f --volumes
DOCKER_FREED=$(docker system df | tail -1 | awk '{print $4}')
echo "   释放: $DOCKER_FREED"

# 2. 清理旧日志
echo "2️⃣ 清理旧日志..."
find /opt/aggregator/logs -name "*.log" -mtime +30 -delete
find /opt/aggregator/logs -name "*.log.gz" -mtime +90 -delete

# 3. 清理临时文件
echo "3️⃣ 清理临时文件..."
rm -rf /opt/aggregator/data/temp/*

# 4. 清理旧备份
echo "4️⃣ 清理旧备份..."
find /opt/aggregator/backups -name "backup_*.tar.gz" -mtime +30 -delete

echo "✅ 清理完成！"
df -h /
```

定时运行：
```bash
# 每周日凌晨 4 点清理
0 4 * * 0 /opt/aggregator/scripts/cleanup.sh >> /opt/aggregator/logs/cleanup.log 2>&1
```

### 7.2 监控磁盘使用

#### ✅ **磁盘使用告警**

创建 `/opt/aggregator/scripts/disk-monitor.sh`：

```bash
#!/bin/bash

THRESHOLD=80
WEBHOOK_URL="${WEBHOOK_URL:-}"

# 检查磁盘使用率
USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ "$USAGE" -gt "$THRESHOLD" ]; then
    MESSAGE="⚠️ 磁盘使用率 ${USAGE}% 超过阈值 ${THRESHOLD}%"
    
    # 发送通知
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" -d "$MESSAGE"
    fi
    
    echo "$MESSAGE"
fi
```

---

## 8. 网络配置

### 8.1 DNS 配置

#### ✅ **配置可靠的 DNS**

```yaml
services:
  aggregator:
    dns:
      - 8.8.8.8          # Google DNS
      - 1.1.1.1          # Cloudflare DNS
      - 223.5.5.5        # 阿里 DNS（国内）
```

### 8.2 代理配置

#### ✅ **为容器配置代理**

```yaml
services:
  aggregator:
    environment:
      - HTTP_PROXY=http://proxy-server:8080
      - HTTPS_PROXY=http://proxy-server:8080
      - NO_PROXY=localhost,127.0.0.1
```

---

## 9. 故障恢复

### 9.1 自动恢复

#### ✅ **配置健康检查和自动重启**

```yaml
services:
  aggregator:
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

### 9.2 灾难恢复计划

#### ✅ **完整的恢复流程**

1. **准备恢复环境**
```bash
# 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com | bash
```

2. **恢复配置**
```bash
# 从备份恢复配置文件
scp user@backup-server:/backups/aggregator/.env ./
scp user@backup-server:/backups/aggregator/docker-compose.yml ./
```

3. **恢复数据**
```bash
# 从备份恢复数据
mkdir -p data logs
scp user@backup-server:/backups/aggregator/backup_latest.tar.gz ./
tar -xzf backup_latest.tar.gz -C ./data
```

4. **启动服务**
```bash
docker-compose up -d
```

5. **验证服务**
```bash
docker-compose ps
docker-compose logs -f aggregator
```

---

## 10. 开发环境实践

### 10.1 本地开发

#### ✅ **使用 docker-compose override**

创建 `docker-compose.override.yml`：

```yaml
version: '3.8'

services:
  aggregator:
    # 开发环境使用 latest 标签
    image: wzdnzd/aggregator:latest
    
    # 挂载代码目录（用于开发）
    volumes:
      - ./subscribe:/aggregator/subscribe:ro
      - ./data:/aggregator/data
      - ./logs:/aggregator/logs
    
    # 启用 DEBUG 模式
    environment:
      - LOG_LEVEL=DEBUG
      - PYTHONUNBUFFERED=1
    
    # 开发环境不限制资源
    # deploy: {}
```

### 10.2 测试环境

#### ✅ **独立的测试环境**

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  aggregator-test:
    image: wzdnzd/aggregator:main
    container_name: aggregator-test
    environment:
      - GIST_PAT=${GIST_PAT_TEST}
      - GIST_LINK=${GIST_LINK_TEST}
    volumes:
      - ./test-data:/aggregator/data
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
```

启动测试环境：
```bash
docker-compose -f docker-compose.test.yml up -d
```

---

## 📚 参考资源

- 📖 [完整安装指引](./INSTALLATION.md)
- 🐛 [详细调试指引](./DEBUG.md)
- 📋 [快速参考卡](./QUICK_REFERENCE.md)
- 🌳 [问题诊断树](./TROUBLESHOOTING_TREE.md)

---

**📝 文档更新**: 2024-11  
**✍️ 作者**: wzdnzd  
**🔗 项目地址**: https://github.com/wzdnzd/aggregator
