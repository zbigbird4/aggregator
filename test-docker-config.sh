#!/bin/bash

# Docker 配置验证脚本
# 用于检查Dockerfile、docker-compose.yml和相关配置是否正确

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
PASSED=0
FAILED=0

# 测试结果函数
test_pass() {
    echo -e "${GREEN}✓ PASS${NC} $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}✗ FAIL${NC} $1"
    ((FAILED++))
}

test_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

test_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 验证工具
verify_tool() {
    if command -v "$1" &> /dev/null; then
        test_pass "$1 已安装"
    else
        test_fail "$1 未安装"
    fi
}

# 检查文件是否存在
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        test_pass "文件存在: $description ($file)"
    else
        test_fail "文件不存在: $description ($file)"
    fi
}

# 检查Dockerfile语法
check_dockerfile() {
    test_info "检查 Dockerfile..."
    
    if grep -q "FROM python" Dockerfile; then
        test_pass "Dockerfile 包含基础镜像"
    else
        test_fail "Dockerfile 缺少基础镜像定义"
    fi
    
    if grep -q "WORKDIR" Dockerfile; then
        test_pass "Dockerfile 定义了工作目录"
    else
        test_fail "Dockerfile 缺少工作目录定义"
    fi
    
    if grep -q "CMD\|ENTRYPOINT" Dockerfile; then
        test_pass "Dockerfile 定义了启动命令"
    else
        test_fail "Dockerfile 缺少启动命令"
    fi
    
    if grep -q "USER" Dockerfile; then
        test_pass "Dockerfile 配置了用户权限"
    else
        test_warning "Dockerfile 未配置用户权限（推荐配置）"
    fi
}

# 检查docker-compose.yml
check_docker_compose() {
    test_info "检查 docker-compose.yml..."
    
    if grep -q "services:" docker-compose.yml; then
        test_pass "docker-compose.yml 定义了服务"
    else
        test_fail "docker-compose.yml 未定义服务"
    fi
    
    if grep -q "aggregator:" docker-compose.yml; then
        test_pass "docker-compose.yml 包含 aggregator 服务"
    else
        test_fail "docker-compose.yml 缺少 aggregator 服务"
    fi
    
    if grep -q "volumes:" docker-compose.yml; then
        test_pass "docker-compose.yml 定义了卷挂载"
    else
        test_fail "docker-compose.yml 缺少卷挂载"
    fi
    
    if grep -q "environment:" docker-compose.yml; then
        test_pass "docker-compose.yml 定义了环境变量"
    else
        test_fail "docker-compose.yml 缺少环境变量配置"
    fi
    
    if grep -q "redis:" docker-compose.yml; then
        test_pass "docker-compose.yml 包含 redis 服务"
    else
        test_fail "docker-compose.yml 缺少 redis 服务（可选）"
    fi
}

# 检查.env.example
check_env_example() {
    test_info "检查 .env.example..."
    
    if grep -q "GIST_PAT" .env.example; then
        test_pass ".env.example 包含 GIST_PAT"
    else
        test_fail ".env.example 缺少 GIST_PAT"
    fi
    
    if grep -q "CONCURRENT_LIMIT" .env.example; then
        test_pass ".env.example 包含 CONCURRENT_LIMIT"
    else
        test_fail ".env.example 缺少 CONCURRENT_LIMIT"
    fi
    
    if grep -q "STORAGE_TYPE" .env.example; then
        test_pass ".env.example 包含 STORAGE_TYPE"
    else
        test_fail ".env.example 缺少 STORAGE_TYPE"
    fi
}

# 检查要求的依赖
check_requirements() {
    test_info "检查依赖..."
    
    if [ -f "requirements.txt" ]; then
        if grep -q "PyYAML\|pyyaml" requirements.txt; then
            test_pass "requirements.txt 包含 PyYAML"
        else
            test_fail "requirements.txt 缺少 PyYAML"
        fi
    else
        test_fail "requirements.txt 文件不存在"
    fi
}

# 检查文档
check_documentation() {
    test_info "检查文档..."
    
    check_file "DEPLOYMENT.md" "详细部署指南"
    check_file "README.docker" "Docker快速参考"
    check_file ".env.example" "环境变量示例"
}

# 检查脚本
check_scripts() {
    test_info "检查脚本..."
    
    check_file "docker-quickstart.sh" "快速启动脚本"
    
    if [ -x "docker-quickstart.sh" ]; then
        test_pass "docker-quickstart.sh 有执行权限"
    else
        test_warning "docker-quickstart.sh 需要执行权限（运行: chmod +x docker-quickstart.sh）"
    fi
}

# 检查.dockerignore
check_dockerignore() {
    test_info "检查 .dockerignore..."
    
    if [ -f ".dockerignore" ]; then
        if grep -q "__pycache__\|*.log" .dockerignore; then
            test_pass ".dockerignore 配置合理"
        else
            test_warning ".dockerignore 可能配置不完整"
        fi
    else
        test_fail ".dockerignore 文件不存在"
    fi
}

# 检查项目结构
check_project_structure() {
    test_info "检查项目结构..."
    
    if [ -d "subscribe" ]; then
        test_pass "subscribe 目录存在"
    else
        test_fail "subscribe 目录不存在"
    fi
    
    if [ -d "clash" ]; then
        test_pass "clash 目录存在"
    else
        test_fail "clash 目录不存在"
    fi
    
    if [ -d "subconverter" ]; then
        test_pass "subconverter 目录存在"
    else
        test_fail "subconverter 目录不存在"
    fi
}

# 检查是否在正确的目录
check_directory() {
    test_info "检查当前目录..."
    
    if [ -f "Dockerfile" ] && [ -f "docker-compose.yml" ]; then
        test_pass "在正确的项目目录"
    else
        test_fail "不在项目根目录（需要 Dockerfile 和 docker-compose.yml）"
        exit 1
    fi
}

# 主函数
main() {
    echo -e "${BLUE}========================================${NC}"
    echo "Docker 配置验证脚本"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # 运行所有检查
    check_directory
    echo ""
    
    check_project_structure
    echo ""
    
    verify_tool "docker"
    verify_tool "docker-compose"
    echo ""
    
    check_dockerfile
    echo ""
    
    check_docker_compose
    echo ""
    
    check_env_example
    echo ""
    
    check_requirements
    echo ""
    
    check_documentation
    echo ""
    
    check_scripts
    echo ""
    
    check_dockerignore
    echo ""
    
    # 输出总结
    echo -e "${BLUE}========================================${NC}"
    echo "验证结果: "
    echo -e "  ${GREEN}通过: $PASSED${NC}"
    echo -e "  ${RED}失败: $FAILED${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ 所有检查通过！Docker 配置正确${NC}"
        echo ""
        echo "接下来可以："
        echo "1. 运行: cp .env.example .env"
        echo "2. 编辑: nano .env（配置你的参数）"
        echo "3. 启动: bash docker-quickstart.sh"
        echo ""
        return 0
    else
        echo -e "${RED}✗ 检查失败，请修复上述问题${NC}"
        echo ""
        return 1
    fi
}

# 运行
main "$@"
