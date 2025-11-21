# Aggregator Docker 部署指南 - 中文完整版

> 💡 **提示**: 本文档提供了完整的Docker部署方案，适合所有用户使用，从初学者到高级用户。

## 📋 文档导航

本项目提供了多份Docker相关文档，根据你的需求选择：

| 文档 | 适用场景 | 内容 |
|------|---------|------|
| **DEPLOYMENT.md** | 全面指南 | 5000+字详细部署指南，包含快速启动、详细步骤、故障排查、高级配置等 |
| **README.docker** | 快速查考 | 快速参考表，常用命令速查，适合已安装Docker用户 |
| **本文件** | 导航索引 | 帮助你快速找到需要的文档和工具 |

## 🚀 快速开始三步走

### 步骤1: 检查Docker环境

```bash
# 检查Docker是否安装
docker --version

# 检查Docker Compose
docker-compose --version

# 如果未安装，访问: https://docs.docker.com/get-docker/
```

### 步骤2: 配置项目

```bash
# 克隆项目
git clone https://github.com/wzdnzd/aggregator.git
cd aggregator

# 复制配置模板
cp .env.example .env

# 编辑配置（至少填写GIST_PAT和GIST_LINK）
nano .env
# 或使用其他编辑器: vim, code, subl 等
```

### 步骤3: 启动服务

```bash
# 方式一：使用快速启动脚本（推荐）
bash docker-quickstart.sh

# 方式二：手动启动
docker-compose build
docker-compose up -d
docker-compose logs -f aggregator
```

## 📚 详细文档

### 🔍 首次部署用户

**推荐路径**：
1. 阅读本文件的"快速开始"部分
2. 查看 [DEPLOYMENT.md - 快速启动（5分钟）](DEPLOYMENT.md#快速启动5分钟)
3. 参考对应的 [常见配置场景](DEPLOYMENT.md#常见配置场景)

**关键步骤**：
- [前置要求](DEPLOYMENT.md#前置要求)
- [详细安装步骤](DEPLOYMENT.md#详细安装步骤)
- [验证安装](DEPLOYMENT.md#step-4-验证安装)

### ⚙️ 配置用户

**主要文档**: [DEPLOYMENT.md - 详细安装步骤](DEPLOYMENT.md#step-2-配置准备)

**关键配置**：
- [环境变量说明](DEPLOYMENT.md#25-关键配置说明) - 所有环境变量的详细说明
- [.env.example](DEPLOYMENT.md#21-获取env-example文件说明) - 所有支持的配置项
- [配置场景](DEPLOYMENT.md#常见配置场景) - 针对不同场景的配置示例

### 🎯 场景指南

根据你的使用场景选择相应配置：

#### 场景1: 本地个人使用
- **文档**: [DEPLOYMENT.md - 场景1](DEPLOYMENT.md#场景1-本地单机部署最简配置)
- **特点**: 最简配置，无需复杂设置
- **启动**: `bash docker-quickstart.sh`

#### 场景2: 生产部署
- **文档**: [DEPLOYMENT.md - 场景2](DEPLOYMENT.md#场景2-生产部署带redis缓存)
- **特点**: 包含Redis缓存、性能优化
- **启动**: `docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d`

#### 场景3: 高并发处理
- **文档**: [DEPLOYMENT.md - 场景3](DEPLOYMENT.md#场景3-高并发场景)
- **特点**: 高并发参数、性能监控
- **启动**: 根据配置调整参数后启动

#### 场景4: 外部服务集成
- **文档**: [DEPLOYMENT.md - 场景4](DEPLOYMENT.md#场景4-与外部服务集成)
- **特点**: Upstash Redis、通知集成
- **启动**: 配置环境变量后启动

### 🛠️ 维护和管理

**日志和监控**：
- [查看日志](DEPLOYMENT.md#查看日志)
- [性能监控](DEPLOYMENT.md#监控存储)
- [常见日志解读](DEPLOYMENT.md#常见日志信息解读)

**故障排查**：
- [常见问题解决](DEPLOYMENT.md#常见问题解决)
- [高内存占用](DEPLOYMENT.md#问题4-高内存占用)
- [代理测试失败](DEPLOYMENT.md#问题2-代理测试失败)

**维护任务**：
- [升级版本](DEPLOYMENT.md#升级aggregator版本)
- [数据迁移](DEPLOYMENT.md#数据迁移)
- [定期维护](DEPLOYMENT.md#定期维护)

### 🔐 安全建议

- [环境变量保护](DEPLOYMENT.md#环境变量敏感信息保护)
- [容器权限](DEPLOYMENT.md#容器权限设置)
- [网络隔离](DEPLOYMENT.md#网络隔离)
- [数据备份](DEPLOYMENT.md#数据备份策略)

### 🚀 高级配置

- [自定义webhook通知](DEPLOYMENT.md#自定义webhook通知)
- [Clash订阅集成](DEPLOYMENT.md#与clash订阅管理系统集成)
- [性能监控告警](DEPLOYMENT.md#性能监控和告警)
- [多实例部署](DEPLOYMENT.md#多实例部署)

## 🛠️ 快捷工具

### docker-quickstart.sh - 快速启动脚本

一个方便的启动脚本，自动处理所有常见操作：

```bash
# 首次启动
bash docker-quickstart.sh

# 查看实时日志
bash docker-quickstart.sh --logs

# 停止服务
bash docker-quickstart.sh --stop

# 重新启动（保留数据）
bash docker-quickstart.sh --reset

# 完全清理
bash docker-quickstart.sh --clean

# 查看帮助
bash docker-quickstart.sh --help
```

### test-docker-config.sh - 配置验证脚本

验证Docker配置是否正确：

```bash
bash test-docker-config.sh
```

输出会显示：
- ✓ 所有配置正确 - 可以继续启动
- ✗ 检查失败 - 需要修复问题

## 📖 常用命令速查表

### 容器管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps

# 删除容器
docker-compose down

# 重新构建镜像
docker-compose build --no-cache
```

### 日志查看

```bash
# 实时日志
docker-compose logs -f aggregator

# 最后100行
docker-compose logs -n 100 aggregator

# 只看错误
docker-compose logs aggregator | grep ERROR

# 导出日志
docker-compose logs aggregator > logs.txt
```

### 数据访问

```bash
# 查看输出文件
docker-compose cp aggregator:/aggregator/output/clash.yaml ./

# 进入容器
docker-compose exec aggregator bash

# 查看容器内文件
docker-compose exec aggregator ls -la /aggregator/output

# 执行命令
docker-compose exec aggregator python --version
```

更多命令详见 [README.docker](README.docker)

## ✅ 验收清单

使用以下清单验证部署是否完成：

- [ ] Docker已安装并运行
- [ ] docker-compose.yml配置正确
- [ ] .env文件已复制并配置
- [ ] 容器已启动（`docker-compose ps` 显示Up状态）
- [ ] 日志显示正常（无ERROR）
- [ ] 输出文件已生成（`ls output/`）
- [ ] 代理已抓取（`cat output/clash.yaml | wc -l`）

## 🐛 遇到问题？

### 快速诊断

```bash
# 1. 检查容器状态
docker-compose ps

# 2. 查看错误日志
docker-compose logs aggregator | grep -E "ERROR|FAILED|Exception"

# 3. 检查配置
cat .env | grep -E "GIST|STORAGE|CONCURRENT"

# 4. 手动测试
docker-compose exec aggregator python --version
```

### 查找解决方案

1. **简单问题**: 查看 [README.docker](README.docker) 常见问题部分
2. **详细问题**: 查看 [DEPLOYMENT.md 故障排查](DEPLOYMENT.md#故障排查)
3. **特定场景**: 查看 [DEPLOYMENT.md 常见配置场景](DEPLOYMENT.md#常见配置场景)
4. **报告问题**: https://github.com/wzdnzd/aggregator/issues

## 📁 文件结构参考

```
aggregator/
├── Dockerfile                      # Docker镜像定义
├── docker-compose.yml              # 服务编排配置
├── docker-compose.override.yml.example  # 场景覆盖配置示例
├── .env.example                   # 环境变量模板（重要！）
├── .dockerignore                  # Docker构建忽略文件
├── redis.conf                     # Redis配置文件（可选）
│
├── DEPLOYMENT.md                  # 详细部署指南（主文档）
├── README.docker                  # 快速参考
├── DOCKER_DEPLOYMENT_GUIDE.md     # 本文件（导航索引）
│
├── docker-quickstart.sh           # 快速启动脚本
├── test-docker-config.sh          # 配置验证脚本
│
├── subscribe/                     # 主程序目录
├── clash/                         # Clash配置和二进制
├── subconverter/                  # Subconverter工具
├── cmd/                           # 命令行工具
│
├── output/                        # 输出目录（Docker卷）
├── data/                          # 数据目录（Docker卷）
├── logs/                          # 日志目录（Docker卷）
└── requirements.txt               # Python依赖
```

## 🎓 学习路径

### 初学者路径
1. 阅读 "快速开始三步走"
2. 运行 `bash docker-quickstart.sh`
3. 查看生成的文件 `ls output/`
4. 如遇问题，查看故障排查

### 中级用户路径
1. 理解 .env 配置
2. 学习 [DEPLOYMENT.md 常见配置场景](DEPLOYMENT.md#常见配置场景)
3. 自定义场景配置
4. 监控和优化性能

### 高级用户路径
1. 研究 docker-compose.yml 配置
2. 使用 docker-compose.override.yml 自定义
3. 集成外部服务（Redis、监控、反向代理）
4. 多实例部署和负载均衡

## 💡 常见建议

### 性能优化
- 根据服务器硬件调整 CONCURRENT_LIMIT
- 启用Redis缓存进行大规模部署
- 使用较高的并发进行频繁爬虫

### 安全建议
- 定期更新 GitHub Token
- 使用 .gitignore 保护 .env 文件
- 限制 Docker 容器资源
- 定期备份重要数据

### 可靠性建议
- 启用自动重启策略
- 定期检查日志
- 设置定时备份
- 监控磁盘空间

## 📞 获取帮助

- 📚 **文档**: [DEPLOYMENT.md](DEPLOYMENT.md) 完整指南
- 🔧 **快速查询**: [README.docker](README.docker) 命令速查
- 🐛 **问题报告**: https://github.com/wzdnzd/aggregator/issues
- 💬 **讨论**: https://github.com/wzdnzd/aggregator/discussions

---

**下一步**:
- ✅ 确认已安装Docker
- ✅ 运行 `bash docker-quickstart.sh`
- ✅ 查看日志验证启动成功
- ✅ 访问输出文件

祝你部署成功！🎉
