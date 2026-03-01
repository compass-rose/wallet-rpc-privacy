#!/bin/bash

# MetaMask 真实流量捕获 - 快速启动脚本
# Usage: ./start_real_capture.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     MetaMask 真实流量捕获 - 快速启动脚本                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env 文件不存在，创建中...${NC}"
    cat > .env << EOF
# 数据库配置
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/wallet_privacy

# 流量提供者 (使用真实流量)
TRAFFIC_PROVIDER=mitm

# 真实 RPC 端点（请替换为你的 RPC URL）
# 获取免费 RPC:
# - Infura: https://infura.io (注册后获取)
# - Alchemy: https://www.alchemy.com
# - Ankr: https://www.ankr.com (免费公链: https://rpc.ankr.com/eth)

REAL_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# 本地分析服务地址
PRIVACY_API_URL=http://localhost:8000

# 模拟流量配置（开发模式）
MOCK_TRAFFIC_COUNT=500

# 日志级别
LOG_LEVEL=INFO

# CORS 配置
CORS_ORIGINS=*
EOF
    echo -e "${GREEN}✓ 已创建 .env 文件${NC}"
    echo -e "${YELLOW}⚠ 请编辑 .env 文件，设置你的 REAL_RPC_URL${NC}"
    echo ""
    echo "免费 RPC 选项："
    echo "  • Infura (推荐): https://infura.io"
    echo "  • Alchemy:      https://www.alchemy.com"
    echo "  • Ankr:         https://rpc.ankr.com/eth"
    echo ""
    read -p "按 Enter 继续，或 Ctrl+C 取消..."
fi

# 读取配置
source .env

if [ "$REAL_RPC_URL" == "https://mainnet.infura.io/v3/YOUR_PROJECT_ID" ]; then
    echo -e "${RED}❌ 未配置真实 RPC URL！${NC}"
    echo ""
    echo "请编辑 .env 文件，设置 REAL_RPC_URL 为你的 RPC 端点："
    echo ""
    echo "示例："
    echo "  REAL_RPC_URL=https://mainnet.infura.io/v3/abc123def456"
    echo "  REAL_RPC_URL=https://rpc.ankr.com/eth"
    echo ""
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ 虚拟环境不存在，创建中...${NC}"
    /opt/homebrew/bin/python3.10 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境已创建${NC}"
fi

# 激活虚拟环境
echo -e "${BLUE}📦 激活虚拟环境...${NC}"
source venv/bin/activate

# 检查依赖
echo -e "${BLUE}🔧 检查依赖...${NC}"
pip install -q httpx 2>/dev/null || true

# 检查 MySQL
echo -e "${BLUE}🗄️  检查 MySQL...${NC}"
if ! docker ps | grep -q wallet_privacy_mysql; then
    echo -e "${YELLOW}⚠ MySQL 容器未运行，启动中...${NC}"
    docker-compose up -d mysql
    sleep 5
fi
echo -e "${GREEN}✓ MySQL 正在运行${NC}"

# 启动后端服务
echo ""
echo -e "${BLUE}🚀 启动后端分析服务 (端口 8000)...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info &
BACKEND_PID=$!
sleep 3

# 检查后端启动
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}❌ 后端服务启动失败！${NC}"
    kill $BACKEND_PID
    exit 1
fi
echo -e "${GREEN}✓ 后端服务运行在 http://localhost:8000${NC}"

# 启动 RPC 代理
echo ""
echo -e "${BLUE}🔄 启动 RPC 代理服务 (端口 8545)...${NC}"
python rpc_proxy.py --port 8545 --real-rpc "$REAL_RPC_URL" &
PROXY_PID=$!
sleep 2

# 输出使用说明
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅ 服务启动成功！                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 服务信息:${NC}"
echo -e "  后端分析服务:  ${GREEN}http://localhost:8000${NC}"
echo -e "  RPC 代理服务:  ${GREEN}http://localhost:8545${NC}"
echo -e "  真实 RPC 节点:  ${YELLOW}${REAL_RPC_URL}${NC}"
echo ""
echo -e "${BLUE}📝 下一步：配置 MetaMask${NC}"
echo ""
echo -e "  1. 打开 MetaMask"
echo -e "  2. 点击网络选择器 → 添加网络 → 手动添加网络"
echo -e "  3. 填写以下信息:"
echo ""
echo -e "     网络名称:     ${YELLOW}Ethereum (隐私分析)${NC}"
echo -e "     新的 RPC URL: ${GREEN}http://localhost:8545${NC}"
echo -e "     链 ID:        ${GREEN}1${NC}"
echo -e "     货币符号:     ${GREEN}ETH${NC}"
echo -e "     区块浏览器:   ${GREEN}https://etherscan.io${NC}"
echo ""
echo -e "  4. 保存并切换到该网络"
echo ""
echo -e "${BLUE}🚀 开始使用 MetaMask，流量将被自动捕获！${NC}"
echo ""
echo -e "${BLUE}📖 查看分析结果:${NC}"
echo -e "  API 文档:      ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  Swagger UI:    ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}📊 常用命令:${NC}"
echo -e "  获取会话:     ${YELLOW}curl http://localhost:8000/api/v1/sessions${NC}"
echo -e "  查看流量:     ${YELLOW}curl http://localhost:8000/api/v1/sessions/{id}/traffic${NC}"
echo -e "  检测泄露:     ${YELLOW}curl http://localhost:8000/api/v1/sessions/{id}/leaks${NC}"
echo -e "  风险评估:     ${YELLOW}curl -X POST http://localhost:8000/api/v1/sessions/{id}/assess${NC}"
echo ""
echo -e "${RED}⚠️  注意事项:${NC}"
echo -e "  • 此配置只是在 Ethereum 主网添加了新的 RPC 端点"
echo -e "  • 不会改变你的私钥或现有网络配置"
echo -e "  • 操作完成后可以切换回原来的网络"
echo -e "  • 不要在公共网络上暴露代理服务"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服务...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $PROXY_PID 2>/dev/null || true
    echo -e "${GREEN}✓ 服务已停止${NC}"
}

# 捕获中断信号
trap cleanup INT TERM

# 等待用户中断
wait
