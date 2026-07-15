# 求职喵 - 生产环境部署指南

## 目录

1. [系统要求](#系统要求)
2. [服务器准备](#服务器准备)
3. [域名配置](#域名配置)
4. [SSL 证书](#ssl-证书)
5. [部署步骤](#部署步骤)
6. [防火墙配置](#防火墙配置)
7. [运维维护](#运维维护)
8. [常见问题](#常见问题)

---

## 系统要求

### 最低配置
- CPU: 2 核
- 内存: 4 GB
- 硬盘: 40 GB SSD
- 操作系统: Ubuntu 20.04 / 22.04 / CentOS 7+

### 推荐配置
- CPU: 4 核
- 内存: 8 GB
- 硬盘: 80 GB SSD
- 操作系统: Ubuntu 22.04 LTS

### 软件依赖
- Docker 20.10+
- Docker Compose v2+
- 域名（可选，无域名可用 IP 访问）

---

## 服务器准备

### 1. 系统更新 (Ubuntu)

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 安装 Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

安装完成后重新登录或执行：
```bash
newgrp docker
```

验证安装：
```bash
docker --version
docker compose version
```

### 3. 上传项目代码

将项目上传到服务器，例如：
```bash
scp -r /path/to/resume user@your-server:/opt/qiuzhimiao
```

或使用 Git：
```bash
git clone <your-repo-url> /opt/qiuzhimiao
```

---

## 域名配置

如果已有域名，需要配置 DNS 解析：

1. 登录域名服务商控制台
2. 添加 A 记录：
   - 主机记录：`@`
   - 记录类型：`A`
   - 记录值：`你的服务器公网IP`
3. 添加 www 解析（可选）：
   - 主机记录：`www`
   - 记录类型：`A`
   - 记录值：`你的服务器公网IP`

等待 DNS 生效（通常几分钟到几小时）。

验证解析：
```bash
ping your-domain.com
```

---

## SSL 证书

### 方式一：使用 Let's Encrypt 免费证书（推荐）

```bash
cd /opt/qiuzhimiao/deploy/scripts
chmod +x setup-ssl.sh
sudo ./setup-ssl.sh your-domain.com
```

证书会自动保存到 `deploy/nginx/ssl/` 目录。

### 方式二：使用已有证书

将证书文件放入 `deploy/nginx/ssl/` 目录：
- `fullchain.pem` - 证书链文件
- `privkey.pem` - 私钥文件

### 方式三：自签名证书（仅测试用）

部署脚本会自动生成自签名证书，浏览器会提示不安全。

---

## 部署步骤

### 第一步：修改配置文件

```bash
cd /opt/qiuzhimiao/deploy
```

复制并编辑环境变量配置：
```bash
cp .env.production .env.production.local
nano .env.production.local
```

**必须修改的配置项：**

| 配置项 | 说明 | 示例 |
|-------|------|------|
| `DATABASE_URL` | 数据库连接字符串 | 替换密码 |
| `JWT_SECRET_KEY` | JWT 密钥（随机长字符串） | 请务必修改！ |
| `CORS_ORIGINS` | 允许的跨域源 | `https://your-domain.com` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 可选，配置后启用真实 AI |
| `DOUBAO_API_KEY` | 豆包 API Key | 可选 |
| `QWEN_API_KEY` | 通义千问 API Key | 可选 |
| `MINIO_SECRET_KEY` | MinIO 密钥 | 请务必修改！ |

生成强随机密钥：
```bash
openssl rand -hex 32
```

### 第二步：修改 Nginx 配置

编辑 `deploy/nginx/conf.d/qiuzhimiao.conf`：

将所有 `your-domain.com` 替换为你的实际域名：
```bash
sed -i 's/your-domain.com/实际域名.com/g' nginx/conf.d/qiuzhimiao.conf
```

### 第三步：修改 docker-compose 配置

编辑 `deploy/docker-compose.prod.yml`：

将 `your_secure_db_password` 和 `change_this_to_secure_password` 替换为强密码。

**注意：数据库密码必须与 `.env.production` 中的一致。**

### 第四步：执行部署

```bash
cd /opt/qiuzhimiao/deploy/scripts
chmod +x deploy.sh
./deploy.sh
```

等待部署完成，验证服务状态：
```bash
cd /opt/qiuzhimiao/deploy
docker compose -f docker-compose.prod.yml ps
```

所有服务状态应为 `Up` 或 `Up (healthy)`。

### 第五步：验证访问

在浏览器中访问：
- 网站首页：`https://your-domain.com`
- API 文档：`https://your-domain.com/docs`
- 健康检查：`https://your-domain.com/health`

---

## 防火墙配置

### Ubuntu (ufw)

```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
sudo ufw status
```

### CentOS (firewalld)

```bash
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

### 云服务商安全组

在阿里云/腾讯云等控制台的安全组中放行：
- 入方向：22 (SSH)、80 (HTTP)、443 (HTTPS)
- 出方向：全部放行（默认配置即可）

---

## 运维维护

### 常用命令

```bash
cd /opt/qiuzhimiao/deploy

# 查看所有服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f        # 所有服务
docker compose -f docker-compose.prod.yml logs -f backend  # 仅后端
docker compose -f docker-compose.prod.yml logs -f --tail=100  # 最近100行

# 重启服务
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml restart backend

# 停止服务
docker compose -f docker-compose.prod.yml down

# 启动服务
docker compose -f docker-compose.prod.yml up -d

# 更新并重新构建
docker compose -f docker-compose.prod.yml up -d --build
```

### 数据库备份

```bash
# 备份
docker exec qiuzhimiao-db pg_dump -U qiuzhimiao qiuzhimiao > backup_$(date +%Y%m%d).sql

# 恢复
cat backup_20240101.sql | docker exec -i qiuzhimiao-db psql -U qiuzhimiao qiuzhimiao
```

设置定时备份（crontab）：
```bash
crontab -e
# 添加：每天凌晨 3 点备份
0 3 * * * docker exec qiuzhimiao-db pg_dump -U qiuzhimiao qiuzhimiao > /opt/qiuzhimiao/backups/db_$(date +\%Y\%m\%d).sql && find /opt/qiuzhimiao/backups -mtime +30 -delete
```

### SSL 证书自动续期

```bash
crontab -e
# 添加：每天凌晨 2 点检查续期
0 2 * * * certbot renew --quiet --deploy-hook 'docker compose -f /opt/qiuzhimiao/deploy/docker-compose.prod.yml restart nginx'
```

### 系统监控

查看资源使用：
```bash
docker stats
```

查看磁盘使用：
```bash
docker system df
```

清理无用镜像和缓存：
```bash
docker system prune -a
```

---

## 常见问题

### 1. 访问网站显示 502 Bad Gateway

**原因**：后端服务未启动或启动失败

**排查**：
```bash
docker compose -f docker-compose.prod.yml logs backend
```

### 2. 数据库连接失败

**原因**：数据库密码不匹配或数据库未就绪

**排查**：
```bash
docker compose -f docker-compose.prod.yml logs db
docker compose -f docker-compose.prod.yml logs backend
```

### 3. SSL 证书无效

**原因**：证书路径错误或域名不匹配

**排查**：
```bash
ls -la deploy/nginx/ssl/
docker compose -f docker-compose.prod.yml logs nginx
```

### 4. 文件上传失败

**原因**：上传大小限制或 MinIO 配置错误

**排查**：
- 检查 `UPLOAD_MAX_SIZE` 配置
- 检查 MinIO 服务状态：`docker compose -f docker-compose.prod.yml logs minio`

### 5. Redis 连接失败

**原因**：Redis 服务未启动

**排查**：
```bash
docker compose -f docker-compose.prod.yml logs redis
```

### 6. API 限流太严格

修改后端代码中的限流设置，或在 `deploy/.env.production` 中调整相关配置。

---

## 性能优化建议

1. **启用 CDN**：将静态资源通过 CDN 加速
2. **数据库索引**：根据实际查询模式添加适当索引
3. **Redis 缓存**：合理设置缓存 TTL，提高缓存命中率
4. **负载均衡**：流量大时考虑多实例部署
5. **监控告警**：接入 Prometheus + Grafana 监控

---

## 安全加固建议

1. **修改默认密码**：所有服务密码使用强密码
2. **定期更新**：定期更新 Docker 镜像和系统补丁
3. **限制访问**：后台管理接口增加 IP 白名单
4. **日志审计**：开启访问日志和操作日志
5. **备份策略**：定期备份数据库和配置文件

---

如有部署问题，请参考项目 README 或提交 Issue。
