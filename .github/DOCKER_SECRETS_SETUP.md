# GitHub Actions Docker Build Secrets 配置指南

本文档说明如何配置 GitHub Actions 自动构建和推送 Docker 镜像所需的 Secrets。

---

## 📋 必需的 Secrets

### 1. GITHUB_TOKEN（自动提供）

**说明**: GitHub 自动提供，用于推送镜像到 GitHub Container Registry (GHCR)

**权限**: 
- ✅ `packages: write` - 推送镜像到 GHCR
- ✅ `contents: read` - 读取仓库内容

**配置**: 无需手动配置，GitHub Actions 自动提供

---

### 2. DOCKERHUB_USERNAME（可选）

**说明**: Docker Hub 用户名，用于推送镜像到 Docker Hub

**获取方式**:
1. 访问 [Docker Hub](https://hub.docker.com/)
2. 注册或登录账号
3. 用户名即为您的 Docker Hub 用户名

**配置步骤**:
1. 在 GitHub 仓库中，进入 `Settings` → `Secrets and variables` → `Actions`
2. 点击 `New repository secret`
3. Name: `DOCKERHUB_USERNAME`
4. Secret: 输入您的 Docker Hub 用户名
5. 点击 `Add secret`

---

### 3. DOCKERHUB_TOKEN（可选）

**说明**: Docker Hub Access Token，用于认证推送镜像

**获取方式**:
1. 访问 [Docker Hub](https://hub.docker.com/)
2. 登录您的账号
3. 进入 `Account Settings` → `Security` → `Access Tokens`
4. 点击 `New Access Token`
5. 配置 Token:
   - **Description**: `GitHub Actions - Aggregator`
   - **Access permissions**: `Read, Write, Delete`
6. 点击 `Generate`
7. **重要**: 复制生成的 Token（只显示一次）

**配置步骤**:
1. 在 GitHub 仓库中，进入 `Settings` → `Secrets and variables` → `Actions`
2. 点击 `New repository secret`
3. Name: `DOCKERHUB_TOKEN`
4. Secret: 粘贴您复制的 Docker Hub Access Token
5. 点击 `Add secret`

---

## 🔐 安全最佳实践

### 1. 使用 Access Token 而非密码

❌ **不要使用**: Docker Hub 账号密码  
✅ **使用**: Docker Hub Access Token

**原因**:
- Token 可以随时撤销
- Token 可以设置特定权限
- Token 不会暴露您的密码

### 2. 定期轮换 Token

建议每 6-12 个月更换一次 Access Token：

1. 在 Docker Hub 生成新的 Access Token
2. 在 GitHub Secrets 中更新 `DOCKERHUB_TOKEN`
3. 撤销旧的 Access Token

### 3. 最小权限原则

只授予必要的权限：
- **推送镜像**: `Read, Write` 权限
- **不需要**: `Delete` 权限（除非确实需要删除镜像）

### 4. 监控 Token 使用

定期检查 Docker Hub 的 Access Token 使用记录：
- 进入 `Account Settings` → `Security` → `Access Tokens`
- 查看 `Last Used` 时间
- 撤销不再使用的 Token

---

## 🚀 配置验证

### 1. 查看 Secrets 配置

在 GitHub 仓库中：
1. 进入 `Settings` → `Secrets and variables` → `Actions`
2. 确认已配置：
   - ✅ `DOCKERHUB_USERNAME`
   - ✅ `DOCKERHUB_TOKEN`

### 2. 触发工作流测试

**方式 1: 手动触发**
1. 进入 `Actions` 标签页
2. 选择 `Build and Push Docker Images` 工作流
3. 点击 `Run workflow`
4. 选择分支 `main`
5. 点击 `Run workflow`

**方式 2: 推送代码触发**
```bash
git add .
git commit -m "test: trigger docker build"
git push origin main
```

**方式 3: 创建 Tag 触发**
```bash
git tag v1.0.0
git push origin v1.0.0
```

### 3. 查看构建结果

1. 进入 `Actions` 标签页
2. 查看最新的工作流运行
3. 检查构建日志：
   - ✅ 成功推送到 GHCR
   - ✅ 成功推送到 Docker Hub（如果配置了）

### 4. 验证镜像

**验证 GHCR 镜像**:
```bash
docker pull ghcr.io/your-username/aggregator:latest
docker run --rm ghcr.io/your-username/aggregator:latest python --version
```

**验证 Docker Hub 镜像**:
```bash
docker pull your-dockerhub-username/aggregator:latest
docker run --rm your-dockerhub-username/aggregator:latest python --version
```

---

## ❓ 常见问题

### Q1: 为什么推送到 GHCR 不需要额外配置？

A: GitHub Actions 自动提供 `GITHUB_TOKEN`，具有推送到 GHCR 的权限。您只需要在工作流中使用 `secrets.GITHUB_TOKEN` 即可。

### Q2: 如果不配置 Docker Hub Secrets 会怎样？

A: 工作流仍然可以正常运行，只是不会推送镜像到 Docker Hub。镜像只会推送到 GHCR。

### Q3: 如何撤销泄露的 Token？

A: 立即执行以下步骤：
1. 在 Docker Hub 中撤销该 Token
2. 在 GitHub Secrets 中删除 `DOCKERHUB_TOKEN`
3. 生成新的 Token 并重新配置

### Q4: 工作流推送失败怎么办？

A: 检查以下几点：
1. Secrets 是否正确配置
2. Docker Hub Token 是否有效
3. Token 权限是否正确
4. 查看工作流日志获取详细错误信息

### Q5: 如何推送到其他镜像仓库？

A: 修改 `.github/workflows/docker-build.yml`，添加额外的登录和推送步骤。例如，推送到阿里云容器镜像服务：

```yaml
- name: Login to Aliyun Container Registry
  uses: docker/login-action@v3
  with:
    registry: registry.cn-hangzhou.aliyuncs.com
    username: ${{ secrets.ALIYUN_USERNAME }}
    password: ${{ secrets.ALIYUN_PASSWORD }}

- name: Build and push to Aliyun
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: registry.cn-hangzhou.aliyuncs.com/your-namespace/aggregator:latest
```

---

## 📚 相关资源

- [GitHub Actions Secrets 文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Docker Hub Access Tokens 文档](https://docs.docker.com/docker-hub/access-tokens/)
- [GitHub Container Registry 文档](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Build Push Action 文档](https://github.com/docker/build-push-action)

---

## 🆘 获取帮助

如果在配置 Secrets 时遇到问题，请：

1. 查看 [GitHub Actions 日志](../../actions) 获取详细错误信息
2. 在 [Issues](../../issues) 中搜索类似问题
3. 提交新的 [Issue](../../issues/new) 并包含：
   - 错误日志（脱敏后）
   - 您的配置步骤
   - 遇到的具体问题

---

**📝 文档更新**: 2024-11  
**✍️ 作者**: wzdnzd
