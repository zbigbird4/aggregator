# Aggregator 详细调试指引

> **版本**: v1.0.0  
> **更新时间**: 2024-11  
> **目标**: 帮助用户快速定位和解决 Aggregator 运行中的问题

---

## 📖 目录

- [Part 1: 日志查看和分析](#part-1-日志查看和分析)
  - [实时日志查看](#实时日志查看)
  - [日志级别说明](#日志级别说明)
  - [常见日志信息速查](#常见日志信息速查)
- [Part 2: 常见问题诊断和解决](#part-2-常见问题诊断和解决)
  - [A. 容器启动问题](#a-容器启动问题)
  - [B. 代理测试问题](#b-代理测试问题)
  - [C. 输出文件问题](#c-输出文件问题)
  - [D. 存储和数据问题](#d-存储和数据问题)
  - [E. 性能问题](#e-性能问题)
- [Part 3: 进阶调试](#part-3-进阶调试)
- [Part 4: 调试技巧和工具](#part-4-调试技巧和工具)
- [Part 5: 获取帮助](#part-5-获取帮助)

---

## Part 1: 日志查看和分析

### 实时日志查看

#### **基本日志命令**

```bash
# 实时查看所有日志（最常用）
docker-compose logs -f aggregator

# 查看最近 100 行日志
docker-compose logs --tail=100 aggregator

# 查看特定时间段的日志
docker-compose logs --since="2024-01-01T00:00:00" aggregator
docker-compose logs --since="1h" aggregator       # 最近1小时
docker-compose logs --since="30m" aggregator      # 最近30分钟

# 查看日志并添加时间戳
docker-compose logs -f -t aggregator

# 只查看错误日志
docker-compose logs -f aggregator 2>&1 | grep -i "error\|exception\|failed"

# 导出日志到文件
docker-compose logs aggregator > aggregator-logs-$(date +%Y%m%d-%H%M%S).log
```

#### **Docker 原生日志命令**

```bash
# 查看容器日志（不使用 docker-compose）
docker logs -f aggregator

# 查看最近 50 行日志
docker logs --tail 50 aggregator

# 查看日志并显示时间戳
docker logs -f -t aggregator

# 查看特定时间段的日志
docker logs --since 2024-01-01T00:00:00 --until 2024-01-01T23:59:59 aggregator
```

#### **日志文件直接查看**

如果已挂载日志目录：

```bash
# 查看日志目录
ls -lh ./logs/

# 实时查看日志文件
tail -f ./logs/aggregator.log

# 使用 less 查看大日志文件
less ./logs/aggregator.log

# 搜索日志中的关键字
grep -i "error" ./logs/aggregator.log

# 统计错误数量
grep -c "ERROR" ./logs/aggregator.log

# 查看日志中的 IP 地址
grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" ./logs/aggregator.log | sort | uniq
```

---

### 日志级别说明

Aggregator 使用标准的 Python 日志级别：

| 级别 | 关键字 | 含义 | 示例 |
|------|--------|------|------|
| **DEBUG** | `[DEBUG]` | 调试信息，详细的执行流程 | `[DEBUG] Testing proxy: 1.2.3.4:8080` |
| **INFO** | `[INFO]` | 一般信息，正常的操作记录 | `[INFO] Starting proxy crawler...` |
| **WARNING** | `[WARNING]` | 警告信息，可能的问题但不影响运行 | `[WARNING] Proxy failed: timeout` |
| **ERROR** | `[ERROR]` | 错误信息，操作失败但程序继续 | `[ERROR] Failed to generate clash.yaml` |
| **CRITICAL** | `[CRITICAL]` | 严重错误，程序可能无法继续 | `[CRITICAL] Cannot connect to storage` |

#### **启用 DEBUG 模式**

DEBUG 模式会输出更详细的日志信息，有助于诊断问题：

```bash
# 方法1: 通过环境变量（推荐）
# 在 .env 文件中添加
LOG_LEVEL=DEBUG

# 方法2: 在 docker-compose.yml 中添加
environment:
  - LOG_LEVEL=DEBUG

# 方法3: 进入容器手动运行
docker exec -it aggregator /bin/bash
export LOG_LEVEL=DEBUG
python -u subscribe/collect.py --all --overwrite --skip
```

---

### 常见日志信息速查

#### **正常运行的日志**

```
[INFO] Starting Aggregator...
[INFO] Loading configuration...
[INFO] Initializing crawler...
[INFO] Starting proxy collection...
[INFO] Found 1234 proxies from source: telegram
[INFO] Testing 1234 proxies...
[INFO] Successfully tested 567 proxies (46%)
[INFO] Generating output files...
[INFO] Uploading to GitHub Gist...
[INFO] Successfully uploaded: clash.yaml
[INFO] Task completed in 123.45 seconds
```

#### **警告日志（可忽略）**

```
[WARNING] Proxy timeout: 1.2.3.4:8080 (可能是代理质量差)
[WARNING] Rate limit reached, waiting... (触发限流，等待重试)
[WARNING] Duplicate proxy found: 1.2.3.4:8080 (重复代理，已去重)
[WARNING] Empty response from source (数据源暂时无数据)
```

#### **错误日志（需要关注）**

```
[ERROR] Failed to connect to GitHub API (GitHub 连接失败)
[ERROR] Invalid GIST_PAT token (Token 无效)
[ERROR] Permission denied: /aggregator/data (权限不足)
[ERROR] Out of memory (内存不足)
[ERROR] Failed to parse proxy URL (代理格式错误)
```

#### **关键字含义**

| 关键字 | 含义 | 原因 | 解决方案 |
|-------|------|------|---------|
| `timeout` | 超时 | 网络延迟、代理失效 | 增加超时时间、检查网络 |
| `connection refused` | 连接被拒绝 | 服务未启动、端口错误 | 检查服务状态、端口配置 |
| `permission denied` | 权限不足 | 文件权限、目录权限 | 修改权限、检查挂载 |
| `invalid token` | Token 无效 | Token 过期、权限不足 | 重新生成 Token |
| `rate limit` | 限流 | 请求过于频繁 | 等待、降低请求频率 |
| `out of memory` | 内存不足 | 数据量过大、内存限制 | 增加内存限制、优化配置 |
| `no such file` | 文件不存在 | 文件缺失、路径错误 | 检查文件、修正路径 |

---

## Part 2: 常见问题诊断和解决

### A. 容器启动问题

#### **问题 1: 容器无法启动**

**症状**：
```bash
$ docker-compose up -d
ERROR: Cannot start service aggregator: ...
```

**诊断步骤**：

```bash
# 1. 检查 Docker 服务状态
sudo systemctl status docker

# 2. 检查 Docker 版本
docker --version
# 确保 >= 20.10

# 3. 检查 Docker Compose 版本
docker-compose --version
# 确保 >= 2.0

# 4. 检查配置文件语法
docker-compose config

# 5. 查看详细错误信息
docker-compose up
```

**常见原因和解决方案**：

**原因 1: Docker 服务未启动**
```bash
# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker
```

**原因 2: docker-compose.yml 语法错误**
```bash
# 验证 YAML 语法
docker-compose config

# 如果有错误，会显示具体位置
# 修正 YAML 缩进和语法
```

**原因 3: 镜像拉取失败**
```bash
# 手动拉取镜像
docker pull wzdnzd/aggregator:latest

# 如果拉取失败，配置镜像加速器
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
EOF

sudo systemctl restart docker
```

**原因 4: 端口冲突**
```bash
# 检查端口占用
netstat -tlnp | grep :8080

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8081:8080"  # 改为其他端口
```

---

#### **问题 2: 容器启动后立即退出**

**症状**：
```bash
$ docker-compose ps
NAME         STATE
aggregator   Exit 1
```

**诊断步骤**：

```bash
# 1. 查看容器日志
docker-compose logs aggregator

# 2. 查看容器退出码
docker inspect aggregator | jq '.[0].State.ExitCode'

# 3. 查看容器详细信息
docker inspect aggregator | jq '.[0].State'

# 4. 尝试手动运行容器
docker run --rm -it wzdnzd/aggregator:latest /bin/bash
```

**常见原因和解决方案**：

**原因 1: 环境变量缺失**

容器日志显示：
```
Error: environment 'GIST_PAT' cannot be empty
```

解决方案：
```bash
# 检查 .env 文件
cat .env

# 确保配置了必需的环境变量
GIST_PAT=ghp_your_token_here
GIST_LINK=your_username/your_gist_id

# 重新启动
docker-compose up -d
```

**原因 2: 配置文件错误**

容器日志显示：
```
Error: Failed to load configuration
```

解决方案：
```bash
# 检查配置文件语法
python -m json.tool config/my-config.json

# 验证配置文件路径
docker exec aggregator ls -la /aggregator/config/

# 修正配置文件并重启
docker-compose restart aggregator
```

**原因 3: 权限问题**

容器日志显示：
```
PermissionError: [Errno 13] Permission denied: '/aggregator/data'
```

解决方案：
```bash
# 修改本地目录权限
chmod -R 755 ./data ./logs

# 或在 docker-compose.yml 中指定用户
user: "1000:1000"

# 重新创建容器
docker-compose down
docker-compose up -d
```

---

#### **问题 3: 内存/CPU 不足**

**症状**：
```
OOMKilled (Out of Memory)
Container is restarting constantly
```

**诊断步骤**：

```bash
# 1. 查看容器资源使用
docker stats aggregator

# 2. 查看容器重启次数
docker inspect aggregator | jq '.[0].RestartCount'

# 3. 查看系统内存
free -h

# 4. 查看 OOM 日志
dmesg | grep -i "out of memory"
sudo journalctl -u docker | grep -i "oom"
```

**解决方案**：

```yaml
# 在 docker-compose.yml 中增加资源限制
deploy:
  resources:
    limits:
      cpus: '2'      # 增加到2个CPU
      memory: 2G     # 增加到2GB
    reservations:
      cpus: '1'
      memory: 1G
```

**优化建议**：
```bash
# 1. 减少并发数
# 在运行时使用 -n 参数
docker exec aggregator python -u subscribe/collect.py --all --overwrite --skip -n 16

# 2. 清理 Docker 缓存
docker system prune -a

# 3. 监控资源使用
watch -n 1 'docker stats aggregator --no-stream'
```

---

### B. 代理测试问题

#### **问题 1: 代理测试一直没有进展**

**症状**：
```
[INFO] Testing 1000 proxies...
（长时间卡住，没有进度）
```

**诊断步骤**：

```bash
# 1. 查看容器日志（启用 DEBUG 模式）
docker-compose logs -f aggregator

# 2. 进入容器查看进程
docker exec -it aggregator /bin/bash
ps aux | grep python

# 3. 检查网络连接
docker exec aggregator ping -c 3 8.8.8.8

# 4. 查看资源使用
docker stats aggregator
```

**常见原因和解决方案**：

**原因 1: 网络连接问题**

测试：
```bash
# 测试容器网络
docker exec aggregator ping -c 3 google.com

# 测试 DNS 解析
docker exec aggregator nslookup google.com

# 测试代理连接
docker exec aggregator curl -I https://www.google.com --connect-timeout 10
```

解决方案：
```bash
# 配置 DNS
# 在 docker-compose.yml 中添加
dns:
  - 8.8.8.8
  - 1.1.1.1

# 或修改 Docker 配置
sudo tee -a /etc/docker/daemon.json <<-'EOF'
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
EOF

sudo systemctl restart docker
```

**原因 2: 并发数过高**

症状：CPU 或内存使用率 100%

解决方案：
```bash
# 降低并发数（默认可能是64或更高）
# 进入容器手动运行
docker exec -it aggregator /bin/bash
python -u subscribe/collect.py --all --overwrite --skip -n 16

# 或修改配置文件中的并发设置
```

**原因 3: 代理全部失效**

症状：测试速度快但成功率为 0%

解决方案：
```bash
# 查看代理来源
docker exec aggregator python -u subscribe/collect.py --all --overwrite --skip

# 检查代理格式
docker exec aggregator cat /aggregator/data/proxies.txt

# 手动测试单个代理
docker exec aggregator curl -x http://1.2.3.4:8080 https://www.google.com --connect-timeout 10
```

---

#### **问题 2: 所有代理都测试失败**

**症状**：
```
[INFO] Testing 1000 proxies...
[INFO] Successfully tested 0 proxies (0%)
```

**诊断步骤**：

```bash
# 1. 启用 DEBUG 模式查看详细日志
docker exec -it aggregator /bin/bash
export LOG_LEVEL=DEBUG
python -u subscribe/collect.py --all --overwrite --skip

# 2. 手动测试代理
curl -x socks5://1.2.3.4:1080 https://www.google.com -v

# 3. 检查防火墙
sudo ufw status
sudo iptables -L
```

**常见原因和解决方案**：

**原因 1: 测试目标不可达**

解决方案：
```bash
# 测试容器是否能访问测试目标
docker exec aggregator curl -I https://www.google.com --connect-timeout 10

# 如果不能访问，配置代理测试使用其他目标
# 或检查服务器网络环境
```

**原因 2: 代理格式错误**

检查代理格式：
```bash
# 正确格式示例
vmess://base64encoded...
trojan://password@host:port...
ss://base64encoded...

# 检查是否有格式错误的代理
docker exec aggregator grep -E "^(vmess|trojan|ss|ssr|vless)://" /aggregator/data/proxies.txt
```

**原因 3: Clash 二进制文件权限问题**

检查和修复：
```bash
# 检查 Clash 二进制文件
docker exec aggregator ls -la /aggregator/clash/clash-linux-amd

# 添加执行权限
docker exec aggregator chmod +x /aggregator/clash/clash-linux-amd

# 测试运行
docker exec aggregator /aggregator/clash/clash-linux-amd -v
```

---

#### **问题 3: 测试速度太慢**

**症状**：
```
测试 1000 个代理需要 30 分钟以上
```

**性能瓶颈分析**：

```bash
# 1. 查看 CPU 使用率
docker stats aggregator --no-stream

# 2. 查看 I/O 等待
docker exec aggregator top

# 3. 查看网络延迟
docker exec aggregator ping -c 10 8.8.8.8
```

**优化建议**：

**1. 增加并发数**（如果 CPU 和内存充足）
```bash
# 默认可能是 32，可以增加到 64 或 128
python -u subscribe/collect.py --all --overwrite --skip -n 128
```

**2. 减少超时时间**
```bash
# 减少每个代理的测试超时时间（默认可能是 10 秒）
python -u subscribe/collect.py --all --overwrite --skip -t 5000  # 5秒
```

**3. 增加 CPU 资源**
```yaml
# 在 docker-compose.yml 中
deploy:
  resources:
    limits:
      cpus: '4'  # 增加到4个CPU
```

**4. 使用 SSD 存储**
```bash
# 确保数据卷在 SSD 上
# 查看挂载点
df -Th
```

---

### C. 输出文件问题

#### **问题 1: clash.yaml 未生成**

**症状**：
```
容器运行完成，但 Gist 或本地没有 clash.yaml 文件
```

**检查清单**：

```bash
# 1. 检查容器日志
docker-compose logs aggregator | grep -i "clash\|yaml\|output"

# 2. 检查容器内文件
docker exec aggregator ls -la /aggregator/data/

# 3. 检查权限
docker exec aggregator ls -ld /aggregator/data

# 4. 检查磁盘空间
docker exec aggregator df -h

# 5. 检查 Gist 配置
echo $GIST_PAT
echo $GIST_LINK
```

**常见原因和解决方案**：

**原因 1: 没有可用的代理**

容器日志：
```
[WARNING] No valid proxies found
[INFO] Skipping output generation
```

解决方案：
```bash
# 检查代理来源配置
# 确保配置了有效的代理来源
```

**原因 2: Gist Token 无效**

容器日志：
```
[ERROR] Failed to upload to Gist: 401 Unauthorized
```

解决方案：
```bash
# 重新生成 GitHub Token
# 访问: https://github.com/settings/tokens
# 确保有 gist 权限

# 更新 .env 文件
GIST_PAT=ghp_new_token_here

# 重启容器
docker-compose restart aggregator
```

**原因 3: 权限不足**

容器日志：
```
[ERROR] PermissionError: [Errno 13] Permission denied: '/aggregator/data/clash.yaml'
```

解决方案：
```bash
# 修改本地目录权限
sudo chown -R $USER:$USER ./data
chmod -R 755 ./data

# 重新创建容器
docker-compose down
docker-compose up -d
```

---

#### **问题 2: 输出文件损坏/不可用**

**症状**：
```
文件生成了，但 Clash 客户端无法加载
```

**验证文件完整性**：

```bash
# 1. 检查文件大小
docker exec aggregator ls -lh /aggregator/data/clash.yaml

# 2. 检查文件格式
docker exec aggregator head -n 20 /aggregator/data/clash.yaml

# 3. 验证 YAML 语法
docker exec aggregator python -c "
import yaml
with open('/aggregator/data/clash.yaml', 'r') as f:
    try:
        yaml.safe_load(f)
        print('✅ YAML 格式正确')
    except Exception as e:
        print(f'❌ YAML 格式错误: {e}')
"

# 4. 查看文件内容
docker exec aggregator cat /aggregator/data/clash.yaml | less
```

**常见问题**：

**问题 1: 文件截断**

原因：磁盘空间不足、写入中断

解决方案：
```bash
# 检查磁盘空间
df -h

# 清理空间
docker system prune -a

# 重新生成
docker-compose restart aggregator
```

**问题 2: 编码问题**

检查文件编码：
```bash
docker exec aggregator file /aggregator/data/clash.yaml
# 应该是: UTF-8 Unicode text

# 如果编码错误，检查代理来源数据
```

---

### D. 存储和数据问题

#### **问题 1: 数据丢失**

**症状**：
```
容器重启后，之前生成的数据不见了
```

**诊断**：

```bash
# 1. 检查数据卷配置
docker-compose config | grep -A 5 "volumes:"

# 2. 检查数据卷是否挂载
docker inspect aggregator | jq '.[0].Mounts'

# 3. 检查本地目录
ls -la ./data

# 4. 查找数据卷位置
docker volume inspect aggregator_aggregator-data
```

**解决方案**：

确保在 `docker-compose.yml` 中正确配置了数据卷：

```yaml
services:
  aggregator:
    volumes:
      - ./data:/aggregator/data       # 正确：挂载到本地目录
      - aggregator-data:/aggregator/data  # 或使用 named volume

volumes:
  aggregator-data:
    driver: local
```

---

#### **问题 2: 存储空间满**

**症状**：
```
[ERROR] No space left on device
```

**检查磁盘使用**：

```bash
# 1. 检查系统磁盘
df -h

# 2. 检查 Docker 磁盘使用
docker system df

# 3. 检查特定目录
du -sh ./data ./logs

# 4. 查找大文件
find ./data -type f -size +100M -exec ls -lh {} \;
```

**清理方案**：

```bash
# 1. 清理 Docker 缓存
docker system prune -a
docker volume prune

# 2. 清理旧日志
find ./logs -name "*.log" -mtime +30 -delete

# 3. 清理临时文件
rm -rf ./data/temp/*

# 4. 压缩归档旧数据
tar -czf archive-$(date +%Y%m%d).tar.gz ./data
mv archive-*.tar.gz ./backups/
rm -rf ./data/*
```

---

### E. 性能问题

#### **问题 1: 运行缓慢**

**性能指标检查**：

```bash
# 1. CPU 使用率
docker stats aggregator --no-stream

# 2. 内存使用
docker exec aggregator free -h

# 3. I/O 性能
docker exec aggregator dd if=/dev/zero of=/tmp/test bs=1M count=1000

# 4. 网络延迟
docker exec aggregator ping -c 10 8.8.8.8
```

**优化建议**：

**1. 增加资源限制**
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

**2. 调整并发数**
```bash
# 根据 CPU 核心数调整（一般设为核心数的2-4倍）
python -u subscribe/collect.py -n 32
```

**3. 使用 SSD 存储**

**4. 优化网络**
```yaml
# 使用 host 网络模式（性能最好但安全性较低）
network_mode: host
```

---

#### **问题 2: 高 CPU/内存使用**

**原因分析**：

```bash
# 1. 查看进程
docker exec aggregator ps aux --sort=-%cpu | head -10
docker exec aggregator ps aux --sort=-%mem | head -10

# 2. 使用 py-spy 分析（需要安装）
docker exec aggregator pip install py-spy
docker exec aggregator py-spy top --pid 1

# 3. 查看线程数
docker exec aggregator ps -eLf | wc -l
```

**解决方案**：

**1. 降低并发数**
```bash
python -u subscribe/collect.py -n 16  # 降低到16
```

**2. 设置资源限制**
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

**3. 优化配置**
```json
{
  "max_concurrent_tests": 32,
  "timeout": 5000,
  "batch_size": 100
}
```

---

## Part 3: 进阶调试

### A. 容器内部调试

#### **进入容器**

```bash
# 使用 bash
docker exec -it aggregator /bin/bash

# 使用 sh（如果 bash 不可用）
docker exec -it aggregator /bin/sh

# 以 root 用户进入
docker exec -it -u root aggregator /bin/bash
```

#### **手动运行爬虫**

```bash
# 进入容器
docker exec -it aggregator /bin/bash

# 进入工作目录
cd /aggregator

# 手动运行 collect.py
python -u subscribe/collect.py --all --overwrite --skip

# 使用 DEBUG 模式
export LOG_LEVEL=DEBUG
python -u subscribe/collect.py --all --overwrite --skip

# 使用 process.py（如果有自定义配置）
python -u subscribe/process.py -s /aggregator/config/my-config.json

# 只运行爬取，不测试
python -u subscribe/collect.py --all --skip

# 只测试已有代理
python -u subscribe/collect.py --check
```

#### **查看生成的文件**

```bash
# 查看数据目录
ls -la /aggregator/data

# 查看代理文件
cat /aggregator/data/proxies.txt | head -20

# 查看输出文件
cat /aggregator/data/clash.yaml | head -50

# 统计代理数量
wc -l /aggregator/data/proxies.txt
```

#### **检查环境变量**

```bash
# 查看所有环境变量
env | sort

# 查看特定环境变量
echo $GIST_PAT
echo $GIST_LINK

# 检查 Python 版本
python --version

# 检查依赖包
pip list
```

---

### B. 网络诊断

#### **测试容器网络连接**

```bash
# 测试 DNS 解析
docker exec aggregator nslookup google.com
docker exec aggregator nslookup github.com

# 测试网络连通性
docker exec aggregator ping -c 3 8.8.8.8
docker exec aggregator ping -c 3 google.com

# 测试 HTTP 连接
docker exec aggregator curl -I https://www.google.com --connect-timeout 10
docker exec aggregator curl -I https://api.github.com --connect-timeout 10

# 测试 HTTPS 证书
docker exec aggregator openssl s_client -connect github.com:443 </dev/null

# 测试端口连通性
docker exec aggregator nc -zv github.com 443
docker exec aggregator nc -zv api.github.com 443
```

#### **测试代理连接**

```bash
# 测试 HTTP 代理
docker exec aggregator curl -x http://1.2.3.4:8080 https://www.google.com --connect-timeout 10

# 测试 SOCKS5 代理
docker exec aggregator curl -x socks5://1.2.3.4:1080 https://www.google.com --connect-timeout 10

# 安装测试工具（如果需要）
docker exec -u root aggregator apt-get update
docker exec -u root aggregator apt-get install -y curl netcat dnsutils
```

---

### C. 性能分析

#### **使用 time 命令测量执行时间**

```bash
# 测量完整执行时间
docker exec aggregator time python -u subscribe/collect.py --all --overwrite --skip

# 输出示例：
# real    2m30.123s
# user    1m45.456s
# sys     0m15.789s
```

#### **CPU 和内存使用分析**

```bash
# 实时监控
docker stats aggregator

# 导出性能数据
docker stats aggregator --no-stream > performance-$(date +%Y%m%d-%H%M%S).log

# 使用 top 查看进程
docker exec aggregator top -b -n 1

# 查看内存详情
docker exec aggregator free -h
docker exec aggregator cat /proc/meminfo
```

#### **I/O 性能监控**

```bash
# 测试写入性能
docker exec aggregator dd if=/dev/zero of=/tmp/test bs=1M count=1000 oflag=direct

# 测试读取性能
docker exec aggregator dd if=/tmp/test of=/dev/null bs=1M count=1000 iflag=direct

# 查看 I/O 统计
docker exec aggregator iostat -x 1 5
```

---

### D. 配置验证

#### **验证 YAML 配置**

```bash
# 验证 docker-compose.yml
docker-compose config

# 验证 Clash 配置
docker exec aggregator python -c "
import yaml
with open('/aggregator/data/clash.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print(f'✅ Proxies: {len(config.get(\"proxies\", []))}')
    print(f'✅ Proxy Groups: {len(config.get(\"proxy-groups\", []))}')
"
```

#### **验证 JSON 配置**

```bash
# 验证 JSON 格式
docker exec aggregator python -m json.tool /aggregator/config/my-config.json

# 或使用 jq
docker exec aggregator jq . /aggregator/config/my-config.json
```

---

## Part 4: 调试技巧和工具

### A. 有用的命令集合

```bash
# ============================================================================
# 日志和监控
# ============================================================================

# 查看完整日志
docker logs --tail 100 aggregator

# 实时监控资源使用
docker stats aggregator

# 检查容器内部进程
docker top aggregator

# 导出日志到文件
docker logs aggregator > debug-$(date +%Y%m%d-%H%M%S).log 2>&1

# 检查卷挂载
docker inspect --format='{{json .Mounts}}' aggregator | jq

# 查看容器配置
docker inspect aggregator | jq

# 查看容器网络
docker inspect --format='{{json .NetworkSettings}}' aggregator | jq

# ============================================================================
# 容器管理
# ============================================================================

# 重启容器
docker-compose restart aggregator

# 重建容器
docker-compose up -d --force-recreate aggregator

# 停止容器
docker-compose stop aggregator

# 删除容器
docker-compose down

# 清理所有（慎用）
docker-compose down -v  # 包括数据卷

# ============================================================================
# 文件操作
# ============================================================================

# 从容器复制文件到本地
docker cp aggregator:/aggregator/data/clash.yaml ./clash.yaml

# 从本地复制文件到容器
docker cp ./my-config.json aggregator:/aggregator/config/

# 查看容器文件
docker exec aggregator cat /aggregator/data/clash.yaml | head -50

# ============================================================================
# 性能和调试
# ============================================================================

# 查看容器资源限制
docker inspect aggregator | jq '.[0].HostConfig.Memory'
docker inspect aggregator | jq '.[0].HostConfig.NanoCpus'

# 测试网络延迟
docker exec aggregator ping -c 10 8.8.8.8 | tail -1

# 测试磁盘 I/O
docker exec aggregator dd if=/dev/zero of=/tmp/test bs=1M count=100 oflag=direct 2>&1 | grep copied

# ============================================================================
# 清理和维护
# ============================================================================

# 清理 Docker 缓存
docker system prune -a --volumes

# 查看 Docker 磁盘使用
docker system df -v

# 清理旧日志
docker exec aggregator find /aggregator/logs -name "*.log" -mtime +30 -delete

# 备份数据
tar -czf backup-$(date +%Y%m%d).tar.gz ./data ./logs
```

---

### B. 推荐的调试工具

#### **1. ctop - 容器性能监控**

```bash
# 安装
sudo wget https://github.com/bcicen/ctop/releases/download/v0.7.7/ctop-0.7.7-linux-amd64 -O /usr/local/bin/ctop
sudo chmod +x /usr/local/bin/ctop

# 使用
ctop
```

#### **2. lazydocker - Docker 可视化管理**

```bash
# 安装
curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash

# 使用
lazydocker
```

#### **3. dive - 镜像分析工具**

```bash
# 安装
wget https://github.com/wagoodman/dive/releases/download/v0.11.0/dive_0.11.0_linux_amd64.deb
sudo dpkg -i dive_0.11.0_linux_amd64.deb

# 分析镜像
dive wzdnzd/aggregator:latest
```

#### **4. docker-compose logs 增强**

```bash
# 安装 lnav（日志分析工具）
sudo apt-get install lnav

# 使用
docker-compose logs aggregator | lnav
```

---

### C. 远程调试

#### **SSH 隧道**

```bash
# 在本地机器上创建 SSH 隧道
ssh -L 2375:localhost:2375 user@remote-server

# 设置 Docker 环境变量
export DOCKER_HOST=tcp://localhost:2375

# 现在可以在本地使用 docker 命令操作远程服务器
docker ps
docker logs aggregator
```

#### **日志导出和分析**

```bash
# 在远程服务器导出日志
docker logs aggregator > aggregator.log 2>&1

# 下载到本地
scp user@remote-server:~/aggregator.log ./

# 本地分析
grep -i "error" aggregator.log
grep -i "warning" aggregator.log
```

---

## Part 5: 获取帮助

### 收集调试信息

在提交 Issue 或寻求帮助时，请收集以下信息：

#### **1. 系统信息**

```bash
# 创建系统信息文件
cat > system-info.txt << EOF
=== 系统信息 ===
操作系统: $(uname -a)
Docker 版本: $(docker --version)
Docker Compose 版本: $(docker-compose --version)
可用内存: $(free -h | grep Mem | awk '{print $7}')
可用磁盘: $(df -h / | tail -1 | awk '{print $4}')

=== 容器信息 ===
容器状态: $(docker inspect aggregator | jq -r '.[0].State.Status')
容器健康状态: $(docker inspect aggregator | jq -r '.[0].State.Health.Status')
重启次数: $(docker inspect aggregator | jq -r '.[0].RestartCount')
EOF

cat system-info.txt
```

#### **2. 完整的错误日志**

```bash
# 导出完整日志（最近 500 行）
docker logs --tail 500 aggregator > error-logs-$(date +%Y%m%d-%H%M%S).log 2>&1
```

#### **3. 配置文件（脱敏）**

```bash
# 复制 docker-compose.yml（脱敏）
cp docker-compose.yml docker-compose-debug.yml

# 手动编辑，移除敏感信息
# GIST_PAT, GIST_LINK 等
```

#### **4. 环境变量（脱敏）**

```bash
# 导出环境变量（手动脱敏）
docker exec aggregator env | grep -v "PAT\|TOKEN\|PASSWORD\|SECRET" > env-vars.txt
```

---

### 提交 Issue

当您在 GitHub 上提交 Issue 时，请包含以下信息：

#### **Issue 模板**

```markdown
## 问题描述
简要描述您遇到的问题

## 环境信息
- 操作系统: Ubuntu 22.04
- Docker 版本: 24.0.7
- Docker Compose 版本: 2.23.0
- Aggregator 镜像版本/标签: wzdnzd/aggregator:latest

## 复现步骤
1. 执行 `docker-compose up -d`
2. 查看日志 `docker-compose logs -f`
3. 发现错误...

## 期望行为
描述您期望的正常行为

## 实际行为
描述实际发生的情况

## 日志输出
```
粘贴相关的错误日志（请确保已脱敏）
```

## 配置文件
```yaml
# docker-compose.yml（已脱敏）
version: '3.8'
services:
  aggregator:
    ...
```

## 尝试过的解决方案
列出您已经尝试过的解决方案

## 其他信息
其他可能有帮助的信息
```

---

### 社区支持

- **GitHub Issues**: [https://github.com/wzdnzd/aggregator/issues](https://github.com/wzdnzd/aggregator/issues)
- **GitHub Discussions**: [https://github.com/wzdnzd/aggregator/discussions](https://github.com/wzdnzd/aggregator/discussions)
- **共享订阅**: [Issue #91](https://github.com/wzdnzd/aggregator/issues/91)

---

**📝 文档更新**: 2024-11  
**✍️ 作者**: wzdnzd  
**📧 反馈**: [提交 Issue](https://github.com/wzdnzd/aggregator/issues)
