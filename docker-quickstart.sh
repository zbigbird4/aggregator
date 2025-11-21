#!/bin/bash

# Aggregator Docker 快速启动脚本
# 用法: bash docker-quickstart.sh [选项]
# 选项:
#   --help       显示帮助信息
#   --reset      重置所有数据并重新启动
#   --logs       实时查看日志
#   --build      重新构建镜像
#   --stop       停止服务
#   --clean      删除所有容器和数据

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
${BLUE}Aggregator Docker 快速启动脚本${NC}

用法: $0 [选项]

选项:
    --help          显示此帮助信息
    --reset         重置所有数据并重新启动
    --logs          实时查看日志
    --build         重新构建镜像
    --stop          停止服务
    --clean         删除所有容器和数据

示例:
    # 首次启动
    $0

    # 查看日志
    $0 --logs

    # 重新启动（保留数据）
    $0 --reset

    # 完全清理
    $0 --clean

EOF
}

# 检查必要命令
check_requirements() {
    print_info "检查依赖..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请访问 https://docs.docker.com/get-docker/ 安装"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        # 尝试 docker compose (v2+)
        if ! docker compose version &> /dev/null; then
            print_error "Docker Compose未安装，请访问 https://docs.docker.com/compose/install/ 安装"
            exit 1
        fi
        DOCKER_COMPOSE="docker compose"
    else
        DOCKER_COMPOSE="docker-compose"
    fi

    print_success "Docker和Docker Compose已安装"
}

# 检查配置文件
check_config() {
    print_info "检查配置文件..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env文件不存在，从.env.example创建..."
            cp .env.example .env
            print_warning "请编辑 .env 文件并填入你的配置（特别是GIST_PAT和GIST_LINK）"
            print_warning "编辑命令: nano .env 或 vi .env"
            return 1
        else
            print_error ".env.example文件不存在"
            exit 1
        fi
    fi

    print_success ".env文件已存在"
    return 0
}

# 启动服务
start_service() {
    print_info "启动Aggregator服务..."

    $DOCKER_COMPOSE build
    print_success "镜像构建完成"

    $DOCKER_COMPOSE up -d
    print_success "容器启动完成"

    # 等待容器启动
    sleep 2

    # 检查容器状态
    if $DOCKER_COMPOSE ps | grep -q "aggregator.*Up"; then
        print_success "Aggregator服务运行中"
    else
        print_error "Aggregator服务启动失败"
        $DOCKER_COMPOSE logs aggregator
        exit 1
    fi
}

# 显示日志
show_logs() {
    print_info "显示日志（按 Ctrl+C 退出）..."
    sleep 1
    $DOCKER_COMPOSE logs -f aggregator
}

# 停止服务
stop_service() {
    print_info "停止服务..."
    $DOCKER_COMPOSE stop
    print_success "服务已停止"
}

# 清理所有数据
clean_all() {
    print_warning "将删除所有容器和数据，是否继续？(y/N)"
    read -r response
    if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
        print_info "操作已取消"
        return
    fi

    print_info "清理中..."
    $DOCKER_COMPOSE down -v
    print_success "清理完成，所有数据已删除"
}

# 重置数据
reset_service() {
    print_warning "将重置所有数据，保留容器配置，是否继续？(y/N)"
    read -r response
    if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
        print_info "操作已取消"
        return
    fi

    print_info "停止服务..."
    $DOCKER_COMPOSE stop

    print_info "删除数据..."
    rm -rf data/* output/* logs/* 2>/dev/null || true

    print_info "重新启动..."
    $DOCKER_COMPOSE up -d

    print_success "重置完成"
}

# 显示启动后的信息
show_startup_info() {
    echo ""
    echo -e "${GREEN}======================================${NC}"
    print_success "Aggregator 启动成功！"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo "接下来的步骤:"
    echo ""
    echo "1. 查看日志："
    echo "   $0 --logs"
    echo ""
    echo "2. 检查输出文件："
    echo "   ls -la output/"
    echo ""
    echo "3. 查看生成的代理："
    echo "   cat output/clash.yaml | head -30"
    echo ""
    echo "4. 停止服务："
    echo "   $0 --stop"
    echo ""
    echo "更多信息请参考: README.docker 或 DEPLOYMENT.md"
    echo ""
}

# 主函数
main() {
    # 检查是否在项目根目录
    if [ ! -f "Dockerfile" ] || [ ! -f "docker-compose.yml" ]; then
        print_error "请在 aggregator 项目根目录运行此脚本"
        exit 1
    fi

    check_requirements

    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --logs)
            show_logs
            exit 0
            ;;
        --stop)
            stop_service
            exit 0
            ;;
        --clean)
            clean_all
            exit 0
            ;;
        --reset)
            reset_service
            show_startup_info
            exit 0
            ;;
        --build)
            print_info "重建镜像..."
            $DOCKER_COMPOSE build --no-cache
            print_success "镜像已重建"
            exit 0
            ;;
        "")
            # 默认启动
            if check_config; then
                start_service
                show_startup_info
            else
                print_warning "请编辑 .env 文件完成配置，然后重新运行此脚本"
                exit 1
            fi
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
