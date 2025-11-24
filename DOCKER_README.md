# Aggregator Docker 部署指南

> **使用 Docker 快速部署 Aggregator 免费代理池构建工具**

[![Docker Pulls](https://img.shields.io/docker/pulls/wzdnzd/aggregator)](https://hub.docker.com/r/wzdnzd/aggregator)
[![Docker Image Size](https://img.shields.io/docker/image-size/wzdnzd/aggregator/latest)](https://hub.docker.com/r/wzdnzd/aggregator)
[![GitHub Container Registry](https://img.shields.io/badge/ghcr.io-aggregator-blue)](https://github.com/wzdnzd/aggregator/pkgs/container/aggregator)

---

## 📦 镜像信息

### 可用镜像源

- **GitHub Container Registry**: `ghcr.io/wzdnzd/aggregator`
- **Docker Hub**: `wzdnzd/aggregator`

### 支持的架构

- ✅ **linux/amd64** (x86_64)
- ✅ **linux/arm64** (aarch64)

### 镜像标签

| 标签 | 说明 | 推荐场景 |
|-----|------|---------|
| `latest` | 最新稳定版本 | 开发测试、个人使用 |
| `v1.0.0` | 固定版本号 | 生产环境 |
| `main` | 主分支最新代码 | 尝鲜新功能 |
| `commit-abc1234` | 特定提交 | 调试、回溯 |

---

## 🚀 快速开始

### 方式一：使用 Docker Compose（推荐）

**1. 下载配置文件**

```bash
# 创建目录
mkdir -p ~/aggregator && cd ~/aggregator

# 下载配置文件
curl -O https://raw.githubusercontent.com/wzdnzd/aggregator/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/wzdnzd/aggregator/main/.env.example
mv .env.example .env
```

**2. 配置环境变量**

编辑 `.env` 文件：

```bash
# 必需配置
GIST_PAT=ghp_your_github_token_here
GIST_LINK=your_username/your_gist_id

# 可选配置
CUSTOMIZE_LINK=
ENABLE_SPECIAL_PROTOCOLS=false
TZ=Asia/Shanghai
```

**3. 启动服务**

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f aggregator

# 查看状态
docker-compose ps
```

### 方式二：使用 Docker 命令

```bash
docker run -d \
  --name aggregator \
  --restart unless-stopped \
  -e GIST_PAT=ghp_your_token \
  -e GIST_LINK=username/gist_id \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/data:/aggregator/data \
  -v $(pwd)/logs:/aggregator/logs \
  wzdnzd/aggregator:latest
```

---

## 📚 完整文档

我们提供了详细的文档帮助您部署和使用 Aggregator：

### 🔰 新手指南

1. **[INSTALLATION.md](./INSTALLATION.md)** - 完整安装部署指引 (>=8000字)
   - 镜像获取方式（GHCR/Docker Hub）
   - 快速部署（3步启动）
   - 5个真实部署场景详解
   - 配置管理详解

### 🐛 问题排查

2. **[DEBUG.md](./DEBUG.md)** - 详细调试指引 (>=5000字)
   - 日志查看和分析
   - 常见问题诊断和解决
   - 进阶调试技巧
   - 性能分析和优化

3. **[TROUBLESHOOTING_TREE.md](./TROUBLESHOOTING_TREE.md)** - 问题诊断决策树
   - 流程图式问题诊断
   - 根据症状快速定位
   - 7大类问题分类索引

### 📋 快速参考

4. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - 快速参考卡
   - 常用命令速查
   - 常见问题速查表
   - 一键脚本集合

### 🔧 最佳实践

5. **[BEST_PRACTICES.md](./BEST_PRACTICES.md)** - 最佳实践指南
   - 安全配置建议
   - 性能优化技巧
   - 监控和告警设置
   - 备份恢复策略

---

## 🎯 常用场景

### 场景 1: 本地开发环境

```yaml
# docker-compose.yml
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
    
    volumes:
      - ./data:/aggregator/data
      - ./logs:/aggregator/logs
```

**启动**：
```bash
docker-compose up -d
docker-compose logs -f
```

### 场景 2: 生产环境部署

```yaml
version: '3.8'

services:
  aggregator:
    image: wzdnzd/aggregator:v1.0.0  # 使用固定版本
    container_name: aggregator-prod
    restart: always
    
    environment:
      - GIST_PAT=${GIST_PAT}
      - GIST_LINK=${GIST_LINK}
      - TZ=Asia/Shanghai
    
    volumes:
      - /opt/aggregator/data:/aggregator/data
      - /opt/aggregator/logs:/aggregator/logs
    
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
    
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "10"
        compress: "true"
```

### 场景 3: 使用 Upstash Redis

```yaml
version: '3.8'

services:
  aggregator:
    image: wzdnzd/aggregator:latest
    environment:
      - GIST_PAT=${GIST_PAT}
      - GIST_LINK=${GIST_LINK}
      - REDIS_URL=${REDIS_URL}  # Upstash Redis URL
      - TZ=Asia/Shanghai
```

### 场景 4: 自动更新（Watchtower）

```yaml
version: '3.8'

services:
  aggregator:
    image: wzdnzd/aggregator:latest
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
    # ... 其他配置

  watchtower:
    image: containrrr/watchtower:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=86400  # 每天检查
      - WATCHTOWER_LABEL_ENABLE=true
```

更多场景请参考 [INSTALLATION.md](./INSTALLATION.md)。

---

## ⚙️ 配置说明

### 必需环境变量

| 变量 | 说明 | 示例 |
|-----|------|------|
| `GIST_PAT` | GitHub Personal Access Token | `ghp_abc123...` |
| `GIST_LINK` | Gist 用户名/ID（格式：`username/gist_id`） | `wzdnzd/abc123...` |

### 可选环境变量

| 变量 | 默认值 | 说明 |
|-----|--------|------|
| `CUSTOMIZE_LINK` | - | 自定义机场列表 URL |
| `ENABLE_SPECIAL_PROTOCOLS` | `false` | 启用特殊协议（vless, hysteria等） |
| `REDIS_URL` | - | Redis 连接字符串 |
| `TZ` | `UTC` | 时区设置 |
| `PYTHONUNBUFFERED` | `1` | Python 输出缓冲 |

### 数据卷

| 容器路径 | 说明 | 推荐挂载 |
|---------|------|---------|
| `/aggregator/data` | 数据目录 | `./data:/aggregator/data` |
| `/aggregator/logs` | 日志目录 | `./logs:/aggregator/logs` |
| `/aggregator/config` | 配置目录（可选） | `./config:/aggregator/config:ro` |

---

## 🔐 GitHub Token 配置

### 创建 Personal Access Token

1. 访问 [GitHub Settings - Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 选择权限：
   - ✅ **gist** (完整访问 gist)
4. 生成并复制 token

### 创建 Gist

1. 访问 [GitHub Gist](https://gist.github.com/)
2. 创建新 gist（可以是空的或包含初始内容）
3. 记录 Gist ID（URL 中的字符串）

示例：`https://gist.github.com/username/【这部分是 Gist ID】`

### 配置到 .env 文件

```bash
GIST_PAT=ghp_YourTokenHere
GIST_LINK=username/your_gist_id
```

---

## 📊 健康检查

容器内置健康检查，每 30 秒检查一次：

```bash
# 查看健康状态
docker inspect aggregator | jq '.[0].State.Health'

# 输出示例：
# {
#   "Status": "healthy",
#   "FailingStreak": 0,
#   "Log": [...]
# }
```

---

## 🔄 更新镜像

### 手动更新

```bash
# 1. 拉取最新镜像
docker pull wzdnzd/aggregator:latest

# 2. 停止并删除旧容器
docker-compose down

# 3. 启动新容器
docker-compose up -d

# 4. 清理旧镜像
docker image prune -a
```

### 自动更新

使用 Watchtower 实现自动更新（见场景4）。

---

## 🐛 故障排查

### 容器无法启动

```bash
# 1. 查看日志
docker-compose logs aggregator

# 2. 检查配置
docker-compose config

# 3. 验证环境变量
cat .env
```

### 代理测试失败

```bash
# 1. 启用 DEBUG 模式
docker exec -it aggregator /bin/bash
export LOG_LEVEL=DEBUG
python -u subscribe/collect.py --all --overwrite --skip

# 2. 测试网络
docker exec aggregator ping -c 3 8.8.8.8
docker exec aggregator curl -I https://www.google.com
```

### Gist 上传失败

```bash
# 1. 验证 Token
docker exec aggregator env | grep GIST_PAT

# 2. 测试 GitHub API
docker exec aggregator curl -H "Authorization: token $GIST_PAT" \
  https://api.github.com/user
```

更多问题请参考 [DEBUG.md](./DEBUG.md) 和 [TROUBLESHOOTING_TREE.md](./TROUBLESHOOTING_TREE.md)。

---

## 📈 性能优化

### 资源限制

```yaml
deploy:
  resources:
    limits:
      cpus: '2'      # 最大 2 个 CPU
      memory: 2G     # 最大 2GB 内存
    reservations:
      cpus: '0.5'    # 至少保证 0.5 个 CPU
      memory: 512M   # 至少保证 512MB 内存
```

### 并发配置

```bash
# 增加并发数（如果 CPU 充足）
docker exec aggregator python -u subscribe/collect.py -n 128

# 减少并发数（如果资源有限）
docker exec aggregator python -u subscribe/collect.py -n 16
```

### 网络优化

```yaml
# 使用 host 网络模式（仅 Linux）
network_mode: host
```

详细优化指南请参考 [BEST_PRACTICES.md](./BEST_PRACTICES.md)。

---

## 💾 备份和恢复

### 备份数据

```bash
# 备份数据和日志
tar -czf backup-$(date +%Y%m%d).tar.gz ./data ./logs

# 上传到远程
scp backup-*.tar.gz user@remote:/backups/
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

自动备份脚本请参考 [BEST_PRACTICES.md](./BEST_PRACTICES.md)。

---

## 🔍 监控和日志

### 查看日志

```bash
# 实时查看
docker-compose logs -f aggregator

# 查看最近 100 行
docker-compose logs --tail=100 aggregator

# 导出日志
docker-compose logs aggregator > logs-$(date +%Y%m%d).log
```

### 监控资源

```bash
# 查看资源使用
docker stats aggregator

# 查看容器进程
docker top aggregator
```

### 日志管理

```yaml
# 配置日志轮转
logging:
  driver: "json-file"
  options:
    max-size: "50m"
    max-file: "10"
    compress: "true"
```

---

## 🏗️ 高可用部署

### Docker Swarm

```bash
# 初始化 Swarm
docker swarm init

# 部署服务栈
docker stack deploy -c docker-compose.swarm.yml aggregator

# 扩展服务
docker service scale aggregator_aggregator=3
```

### Kubernetes

详细 Kubernetes 部署配置请参考 [INSTALLATION.md](./INSTALLATION.md) - 场景5。

---

## 🆘 获取帮助

### 文档资源

- 📖 [完整安装指引](./INSTALLATION.md)
- 🐛 [详细调试指引](./DEBUG.md)
- 📋 [快速参考卡](./QUICK_REFERENCE.md)
- 🔧 [最佳实践](./BEST_PRACTICES.md)
- 🌳 [问题诊断树](./TROUBLESHOOTING_TREE.md)

### 社区支持

- 💬 [GitHub Issues](https://github.com/wzdnzd/aggregator/issues) - 报告问题
- 🗣️ [GitHub Discussions](https://github.com/wzdnzd/aggregator/discussions) - 提问讨论
- 🎁 [共享订阅](https://github.com/wzdnzd/aggregator/issues/91) - 获取现成订阅

### 提交 Issue 模板

```markdown
**环境信息**
- 操作系统: Ubuntu 22.04
- Docker 版本: 24.0.7
- Docker Compose 版本: 2.23.0
- Aggregator 镜像版本: wzdnzd/aggregator:latest

**问题描述**
简要描述问题...

**复现步骤**
1. ...
2. ...

**错误日志**
```
粘贴相关日志（已脱敏）
```

**期望行为**
描述期望的正常行为...
```

---

## 📝 更新日志

查看 [GitHub Releases](https://github.com/wzdnzd/aggregator/releases) 了解最新版本和更新内容。

---

## ⚖️ 许可证

本项目采用 [GPL-3.0](./LICENSE) 许可证。

---

## 🙏 致谢

- [Subconverter](https://github.com/asdlokj1qpi233/subconverter) - 订阅转换核心
- [Mihomo](https://github.com/MetaCubeX/mihomo) - 代理测试引擎
- Docker 社区 - 提供强大的容器化技术

---

**📝 文档更新**: 2024-11  
**✍️ 作者**: wzdnzd  
**🔗 项目地址**: https://github.com/wzdnzd/aggregator  
**📦 Docker Hub**: https://hub.docker.com/r/wzdnzd/aggregator  
**📦 GHCR**: https://github.com/wzdnzd/aggregator/pkgs/container/aggregator

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐**

[快速开始](#-快速开始) · [完整文档](#-完整文档) · [获取帮助](#-获取帮助)

</div>
