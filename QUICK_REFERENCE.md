# Aggregator 快速参考卡

> **快速查找常用命令和解决方案**

---

## 📦 镜像获取

```bash
# GitHub Container Registry
docker pull ghcr.io/wzdnzd/aggregator:latest

# Docker Hub
docker pull wzdnzd/aggregator:latest

# 特定架构
docker pull --platform linux/amd64 wzdnzd/aggregator:latest
docker pull --platform linux/arm64 wzdnzd/aggregator:latest

# 特定版本
docker pull wzdnzd/aggregator:v1.0.0
```

---

## 🚀 快速启动

```bash
# 1. 下载配置文件
curl -O https://raw.githubusercontent.com/wzdnzd/aggregator/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/wzdnzd/aggregator/main/.env.example
mv .env.example .env

# 2. 编辑 .env 文件，填入你的配置
nano .env

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f aggregator
```

---

## 🎛️ 常用命令

### 容器管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart aggregator

# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷（慎用！）
docker-compose down -v

# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats aggregator
```

### 日志查看

```bash
# 实时查看日志
docker-compose logs -f aggregator

# 查看最近 100 行日志
docker-compose logs --tail=100 aggregator

# 查看最近 1 小时的日志
docker-compose logs --since="1h" aggregator

# 导出日志到文件
docker-compose logs aggregator > logs-$(date +%Y%m%d).log

# 只看错误日志
docker-compose logs aggregator 2>&1 | grep -i "error"
```

### 进入容器

```bash
# 进入容器 bash
docker exec -it aggregator /bin/bash

# 以 root 用户进入
docker exec -it -u root aggregator /bin/bash

# 执行单个命令
docker exec aggregator ls -la /aggregator/data

# 查看环境变量
docker exec aggregator env
```

### 文件操作

```bash
# 从容器复制文件到本地
docker cp aggregator:/aggregator/data/clash.yaml ./

# 从本地复制文件到容器
docker cp ./config.json aggregator:/aggregator/config/

# 查看容器内文件
docker exec aggregator cat /aggregator/data/clash.yaml
```

---

## 🐛 常见问题速查表

| 问题症状 | 可能原因 | 快速解决 |
|---------|---------|---------|
| **容器启动失败** | Docker 服务未启动 | `sudo systemctl start docker` |
| **容器立即退出** | 环境变量缺失 | 检查 `.env` 文件，确保 `GIST_PAT` 和 `GIST_LINK` 已配置 |
| **OOMKilled** | 内存不足 | 增加内存限制：`memory: 2G` |
| **Permission denied** | 权限不足 | `chmod -R 755 ./data ./logs` |
| **无网络连接** | DNS/网络问题 | `docker exec aggregator ping 8.8.8.8` |
| **代理测试失败** | 代理全部失效或网络问题 | 启用 DEBUG 模式查看详细日志 |
| **Gist 上传失败** | Token 无效或权限不足 | 重新生成 Token，确保有 gist 权限 |
| **磁盘空间满** | 日志或数据过多 | `docker system prune -a` |
| **测试速度慢** | 并发数太低 | 增加并发：`-n 128` |
| **高 CPU 使用** | 并发数太高 | 降低并发：`-n 16` |

---

## 🔧 故障排查流程

```bash
# 1. 检查容器状态
docker-compose ps

# 2. 查看最近日志
docker-compose logs --tail=50 aggregator

# 3. 检查资源使用
docker stats aggregator --no-stream

# 4. 测试网络连接
docker exec aggregator ping -c 3 8.8.8.8

# 5. 检查磁盘空间
df -h

# 6. 查看容器详细信息
docker inspect aggregator | jq '.[0].State'

# 7. 启用 DEBUG 模式重新运行
docker exec -it aggregator /bin/bash
export LOG_LEVEL=DEBUG
python -u subscribe/collect.py --all --overwrite --skip
```

---

## ⚙️ 配置速查

### 环境变量

| 变量 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `GIST_PAT` | ✅ | GitHub Token | `ghp_abc123...` |
| `GIST_LINK` | ✅ | Gist 用户名/ID | `username/gist_id` |
| `CUSTOMIZE_LINK` | ❌ | 自定义机场列表 | `https://...` |
| `ENABLE_SPECIAL_PROTOCOLS` | ❌ | 启用特殊协议 | `true`/`false` |
| `REDIS_URL` | ❌ | Redis 连接 | `redis://...` |
| `TZ` | ❌ | 时区 | `Asia/Shanghai` |

### 资源限制

```yaml
# 在 docker-compose.yml 中
deploy:
  resources:
    limits:
      cpus: '2'      # 最大 CPU
      memory: 2G     # 最大内存
    reservations:
      cpus: '0.5'    # 预留 CPU
      memory: 512M   # 预留内存
```

---

## 🔐 GitHub Token 配置

### 创建 Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：
   - ✅ **gist** (完整访问)
4. 生成并复制 token

### 配置 Token

```bash
# 在 .env 文件中
GIST_PAT=ghp_YourTokenHere
GIST_LINK=your_username/your_gist_id
```

### 创建 Gist

1. 访问：https://gist.github.com/
2. 创建新 gist
3. 复制 URL 中的 Gist ID
4. 格式：`https://gist.github.com/username/【这部分是 Gist ID】`

---

## 📊 性能优化

### 增加并发数（如果 CPU 充足）

```bash
docker exec aggregator python -u subscribe/collect.py -n 128
```

### 减少超时时间

```bash
docker exec aggregator python -u subscribe/collect.py -t 5000
```

### 增加资源限制

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

### 使用 host 网络模式

```yaml
network_mode: host
```

---

## 🔄 更新和维护

### 手动更新镜像

```bash
# 1. 拉取最新镜像
docker pull wzdnzd/aggregator:latest

# 2. 停止旧容器
docker-compose down

# 3. 启动新容器
docker-compose up -d

# 4. 清理旧镜像
docker image prune -a
```

### 自动更新（Watchtower）

```yaml
# 在 docker-compose.yml 中添加
services:
  watchtower:
    image: containrrr/watchtower:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=86400
    command: aggregator
```

---

## 💾 备份和恢复

### 备份数据

```bash
# 备份数据目录
tar -czf backup-$(date +%Y%m%d).tar.gz ./data ./logs

# 备份到远程
scp backup-*.tar.gz user@remote:/backups/

# 或使用 rsync
rsync -avz ./data user@remote:/backups/aggregator/
```

### 恢复数据

```bash
# 停止容器
docker-compose down

# 解压备份
tar -xzf backup-20240101.tar.gz

# 启动容器
docker-compose up -d
```

---

## 🧹 清理和维护

```bash
# 清理 Docker 缓存
docker system prune -a

# 清理数据卷
docker volume prune

# 清理旧日志
find ./logs -name "*.log" -mtime +30 -delete

# 查看 Docker 磁盘使用
docker system df -v

# 清理特定镜像
docker rmi wzdnzd/aggregator:old-tag
```

---

## 🔍 调试命令

```bash
# 启用 DEBUG 模式
docker exec -it aggregator /bin/bash
export LOG_LEVEL=DEBUG
python -u subscribe/collect.py --all --overwrite --skip

# 手动测试代理
docker exec aggregator curl -x http://1.2.3.4:8080 https://www.google.com

# 测试 Gist 连接
docker exec aggregator curl -H "Authorization: token $GIST_PAT" \
  https://api.github.com/gists/$GIST_ID

# 查看 Clash 二进制
docker exec aggregator /aggregator/clash/clash-linux-amd -v

# 验证 YAML 文件
docker exec aggregator python -c "
import yaml
with open('/aggregator/data/clash.yaml') as f:
    print('✅ Valid YAML')
"
```

---

## 📱 监控命令

```bash
# 实时监控资源
docker stats aggregator

# 查看容器进程
docker top aggregator

# 查看容器健康状态
docker inspect aggregator | jq '.[0].State.Health'

# 监控日志（新错误）
docker-compose logs -f aggregator | grep -i "error"

# 查看网络连接
docker exec aggregator netstat -tuln
```

---

## 🎯 一键脚本

### 快速启动脚本

```bash
#!/bin/bash
# save as: start.sh

set -e
echo "🚀 启动 Aggregator..."

# 检查配置
if [ ! -f .env ]; then
    echo "❌ .env 不存在"
    exit 1
fi

# 创建目录
mkdir -p data logs

# 启动
docker-compose up -d

# 等待启动
sleep 5

# 显示状态
docker-compose ps
docker-compose logs --tail=20 aggregator

echo "✅ 启动完成！"
```

### 健康检查脚本

```bash
#!/bin/bash
# save as: health-check.sh

CONTAINER="aggregator"

if docker ps | grep -q "$CONTAINER"; then
    echo "✅ 容器运行中"
    docker stats $CONTAINER --no-stream
else
    echo "❌ 容器未运行"
    docker-compose up -d
fi
```

---

## 📚 更多资源

- 📖 [完整安装指引](./INSTALLATION.md)
- 🐛 [详细调试指引](./DEBUG.md)
- 🔧 [最佳实践](./BEST_PRACTICES.md)
- 🌳 [问题诊断树](./TROUBLESHOOTING_TREE.md)
- 💬 [GitHub Issues](https://github.com/wzdnzd/aggregator/issues)
- 🗣️ [GitHub Discussions](https://github.com/wzdnzd/aggregator/discussions)

---

**📝 文档更新**: 2024-11  
**✍️ 作者**: wzdnzd  
**🔗 项目地址**: https://github.com/wzdnzd/aggregator
