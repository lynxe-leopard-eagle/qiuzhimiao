@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo =====================================
echo   求职喵 - 生产环境部署脚本 (Windows)
echo =====================================
echo.

cd /d "%~dp0"
cd ..

if not exist ".env.production" (
    echo [错误] 未找到 .env.production 配置文件
    echo        请复制 .env.production 并修改其中的配置
    pause
    exit /b 1
)

echo [1/4] 检查 Docker 环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装 Docker
    pause
    exit /b 1
)
echo [OK] Docker 环境正常
echo.

echo [2/4] 创建必要目录...
if not exist "data\uploads" mkdir data\uploads
if not exist "nginx\ssl" mkdir nginx\ssl
if not exist "nginx\html" mkdir nginx\html
echo [OK] 目录创建完成
echo.

echo [3/4] 检查 SSL 证书...
if exist "nginx\ssl\fullchain.pem" if exist "nginx\ssl\privkey.pem" (
    echo [OK] SSL 证书已存在
) else (
    echo [警告] 未找到 SSL 证书，使用自签名证书（仅用于测试）
    docker run --rm -v "%cd%\nginx\ssl:/certs" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/privkey.pem -out /certs/fullchain.pem -subj "/CN=localhost" 2>nul
    echo [OK] 自签名证书已生成（生产环境请替换为真实证书）
)
echo.

echo [4/4] 构建并启动服务...
docker compose -f docker-compose.prod.yml up -d --build
echo.

timeout /t 10 /nobreak >nul

echo =====================================
echo   [完成] 部署完成！
echo =====================================
echo.
echo 访问地址: https://your-domain.com
echo API 文档: https://your-domain.com/docs
echo 健康检查: https://your-domain.com/health
echo.
echo 常用命令:
echo   查看日志:  cd deploy ^&^& docker compose -f docker-compose.prod.yml logs -f
echo   停止服务:  cd deploy ^&^& docker compose -f docker-compose.prod.yml down
echo   重启服务:  cd deploy ^&^& docker compose -f docker-compose.prod.yml restart
echo.
pause
