#!/bin/bash
set -e

echo "====================================="
echo "  求职喵 - 生产环境部署脚本"
echo "====================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_DIR/deploy"

cd "$DEPLOY_DIR"

if [ ! -f .env.production ]; then
    echo "❌ 错误: 未找到 .env.production 配置文件"
    echo "   请复制 .env.production 并修改其中的配置"
    exit 1
fi

echo ""
echo "📦 步骤 1/5: 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    exit 1
fi
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误: 未安装 Docker Compose"
    exit 1
fi
echo "✅ Docker 环境正常"

echo ""
echo "📁 步骤 2/5: 创建必要目录..."
mkdir -p data/uploads
mkdir -p nginx/ssl
mkdir -p nginx/html
echo "✅ 目录创建完成"

echo ""
echo "🔐 步骤 3/5: 检查 SSL 证书..."
if [ -f nginx/ssl/fullchain.pem ] && [ -f nginx/ssl/privkey.pem ]; then
    echo "✅ SSL 证书已存在"
else
    echo "⚠️  未找到 SSL 证书，使用自签名证书（仅用于测试）"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/CN=localhost" 2>/dev/null || true
    echo "✅ 自签名证书已生成（生产环境请替换为真实证书）"
fi

echo ""
echo "🏗️  步骤 4/5: 构建并启动服务..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.prod.yml up -d --build
else
    docker compose -f docker-compose.prod.yml up -d --build
fi

echo ""
echo "⏳ 步骤 5/5: 等待服务启动..."
sleep 10

echo ""
echo "====================================="
echo "  ✅ 部署完成！"
echo "====================================="
echo ""
echo "🌐 访问地址: https://your-domain.com"
echo "📚 API 文档: https://your-domain.com/docs"
echo "💚 健康检查: https://your-domain.com/health"
echo ""
echo "常用命令:"
echo "  查看日志:  cd deploy && docker compose -f docker-compose.prod.yml logs -f"
echo "  停止服务:  cd deploy && docker compose -f docker-compose.prod.yml down"
echo "  重启服务:  cd deploy && docker compose -f docker-compose.prod.yml restart"
echo ""
