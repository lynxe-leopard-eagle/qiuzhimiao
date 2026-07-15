#!/bin/bash
set -e

echo "====================================="
echo "  求职喵 - SSL 证书申请脚本"
echo "  (使用 Let's Encrypt + Certbot)"
echo "====================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
SSL_DIR="$DEPLOY_DIR/nginx/ssl"

if [ -z "$1" ]; then
    echo "用法: $0 <your-domain.com>"
    echo "示例: $0 qiuzhimiao.com"
    exit 1
fi

DOMAIN=$1
EMAIL="admin@$DOMAIN"

echo ""
echo "📋 域名: $DOMAIN"
echo "📧 邮箱: $EMAIL"
echo ""
read -p "确认以上信息正确吗？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "🔧 安装 certbot..."
if command -v certbot &> /dev/null; then
    echo "✅ certbot 已安装"
else
    apt-get update && apt-get install -y certbot
fi

echo ""
echo "📝 申请 SSL 证书..."
mkdir -p "$SSL_DIR"

certbot certonly --standalone \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --cert-path "$SSL_DIR/fullchain.pem" \
    --key-path "$SSL_DIR/privkey.pem"

echo ""
echo "✅ SSL 证书申请成功！"
echo "证书路径: $SSL_DIR"
echo ""
echo "💡 提示: 证书有效期 90 天，建议设置自动续期"
echo "   crontab 添加: 0 3 * * * certbot renew --quiet --deploy-hook 'docker compose -f $DEPLOY_DIR/docker-compose.prod.yml restart nginx'"
