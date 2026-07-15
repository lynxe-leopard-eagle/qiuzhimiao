# 求职喵 - 系统架构设计文档

## 1. 系统概述

求职喵（QiuZhiMiao）是一款面向技术求职者的AI面试教练平台，通过LLM驱动的智能分析，帮助用户诊断简历、模拟面试、追踪成长。

### 1.1 核心功能

| 模块 | 功能描述 |
|------|---------|
| 简历诊断 | 上传简历，AI分析结构、内容、关键词、量化指标 |
| 岗位匹配 | 粘贴JD，智能分析岗位需求，计算简历匹配度 |
| AI面试 | 多轮次模拟面试，SSE流式交互，实时评判 |
| 复盘报告 | 面试结束后生成五维度雷达图和改进建议 |
| 成长追踪 | 历史面试数据对比，可视化成长曲线 |
| 投递看板 | 管理求职投递进度，统计转化率 |
| AI教练 | 对话式职业咨询，生成个性化作战报告 |

### 1.2 技术栈

```
前端: React 18 + Vite + TypeScript + Tailwind CSS + Zustand + Recharts
后端: FastAPI + SQLAlchemy(async) + PostgreSQL/SQLite + Pydantic
AI:   DeepSeek / 豆包 / 通义千问 (三级路由 + Mock fallback)
缓存: Redis (简历诊断结果、岗位分析、面试会话上下文)
存储: MinIO + 本地存储自动降级
部署: Docker Compose (backend + frontend + PostgreSQL + Redis)
```

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Web    │  │  Mobile  │  │  小程序  │  │  桌面端  │   │
│  │ (React)  │  │  (H5)    │  │  (未来)  │  │  (未来)  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼─────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │ HTTPS / HTTP2
┌────────────────────────────┼─────────────────────────────┐
│                      CDN / Nginx                          │
│              (静态资源缓存 / 负载均衡 / SSL)                  │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────┐
│                     后端服务层                              │
│  ┌────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                    │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  │
│  │  │  Auth   │ │ Resume  │ │   Job   │ │Interview│  │  │
│  │  │  API    │ │  API    │ │  API    │ │  API    │  │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  │
│  │  │ Review  │ │ Growth  │ │  Skill  │ │  Coach  │  │  │
│  │  │  API    │ │  API    │ │  API    │ │  API    │  │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │  │
│  │  ┌─────────┐ ┌─────────┐                            │  │
│  │  │Application│ │  Health │                            │  │
│  │  │  API    │ │  Check  │                            │  │
│  │  └─────────┘ └─────────┘                            │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │              中间件层                                │  │
│  │  CORS → RequestID → RateLimit → Logging             │  │
│  │  Auth(JWT) → Exception Handler                      │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────┴───────┐  ┌─────────┴────────┐  ┌──────┴──────┐
│   PostgreSQL  │  │      Redis       │  │    MinIO    │
│  (主数据库)    │  │   (缓存/会话)    │  │  (对象存储)  │
│               │  │                  │  │             │
│ - users       │  │ - 诊断结果缓存   │  │ - 简历文件  │
│ - resumes     │  │ - 岗位分析缓存   │  │ - 头像      │
│ - jobs        │  │ - 面试会话上下文 │  │             │
│ - interviews  │  │ - 限流计数器     │  │             │
│ - evaluations │  │ - 分布式锁      │  │             │
│ - reviews     │  │                  │  │             │
│ - applications│  │                  │  │             │
└───────────────┘  └──────────────────┘  └─────────────┘
                             │
                    ┌────────┴────────┐
                    │   LLM Service   │
                    │  (统一服务层)   │
                    │                 │
                    │ DeepSeek ──┐   │
                    │ 豆包 ──────┼── fallback
                    │ 通义千问 ──┘   │
                    │  Mock (兜底)   │
                    └─────────────────┘
```

### 2.2 数据流图

```
用户上传简历
    │
    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 文件校验     │───▶│ 内容提取     │───▶│ LLM结构化解析 │
│ (安全)       │    │ (pdf/docx)   │    │ (技能/项目)   │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
                                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 诊断报告展示 │◀───│ 诊断结果缓存 │◀───│ 简历诊断引擎 │
│ (前端)       │    │ (Redis 2h)   │    │ (规则+LLM)   │
└──────────────┘    └──────────────┘    └──────────────┘

用户开始面试
    │
    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 获取简历+JD  │───▶│ LLM生成首题  │───▶│ SSE流式回答  │
│ 内容         │    │ (个性化)     │    │ (评判+追问)   │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
                                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 成长记录更新 │◀───│ 复盘报告生成 │◀───│ 面试结束     │
│ (自动)       │    │ (LLM总结)    │    │ (评判汇总)   │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 3. 模块设计

### 3.1 认证模块 (Auth)

```
POST /api/v1/auth/register    - 用户注册（密码复杂度校验）
POST /api/v1/auth/login       - 用户登录（bcrypt + JWT）
GET  /api/v1/auth/me          - 获取当前用户
POST /api/v1/auth/refresh     - 刷新Access Token
POST /api/v1/auth/reset-password - 密码重置
```

**安全设计：**
- 密码：bcrypt哈希，复杂度要求（≥8位+大小写+数字）
- JWT：access_token(60分钟) + refresh_token(7天)
- 中间件：请求日志、限流、ID追踪

### 3.2 简历模块 (Resume)

```
POST /api/v1/resumes/upload      - 上传简历（文件安全校验）
POST /api/v1/resumes/diagnose    - 简历诊断（Redis缓存）
GET  /api/v1/resumes/:id         - 获取简历状态
GET  /api/v1/resumes/:id/poll    - 轮询解析状态
```

**解析流程：**
1. 文件校验（扩展名、MIME、大小、路径遍历）
2. 内容类型深度校验（magic number检测）
3. 文本提取（pdfplumber / python-docx）
4. LLM结构化解析（教育、技能、项目、工作经历）
5. 存储到数据库 + 对象存储

### 3.3 面试模块 (Interview)

```
POST   /api/v1/interviews/start   - 开始面试（LLM动态生成首题）
POST   /api/v1/interviews/answer  - 回答问题（SSE流式返回）
POST   /api/v1/interviews/:id/end - 结束面试
GET    /api/v1/interviews/:id/messages - 获取消息列表
```

**动态题库生成：**
- 根据简历内容 + JD内容，使用LLM生成个性化首题
- 回退机制：LLM不可用时使用固定题库
- 面试会话上下文存入Redis（TTL=2小时）

### 3.4 LLM服务层

```python
class LLMService:
    - _providers: [DeepSeek, Doubao, Qwen]  # 优先级排序
    - chat(): 同步调用，自动fallback
    - chat_stream(): 流式调用，自动fallback
    - is_real_llm_available: 是否有真实LLM可用
```

**路由策略：**
1. 优先尝试 DeepSeek
2. 失败则尝试 豆包
3. 再失败则尝试 通义千问
4. 全部失败使用 Mock 模式（确保可演示）

## 4. 数据库设计

### 4.1 ER图

```
users ||--o{ resumes : owns
users ||--o{ jobs : creates
users ||--o{ interviews : participates
users ||--o{ applications : tracks
users ||--o{ growth_records : has

resumes ||--o{ interviews : used_in
jobs ||--o{ interviews : used_in
interviews ||--|{ messages : contains
interviews ||--o{ evaluations : has
interviews ||--o| reviews : generates
```

### 4.2 核心表结构

| 表名 | 主要字段 | 说明 |
|------|---------|------|
| users | id, email, name, hashed_password, avatar_url | 用户基础信息 |
| resumes | id, user_id, minio_key, parsed_data, status | 简历及解析结果 |
| jobs | id, user_id, title, company, description | 岗位信息 |
| interviews | id, user_id, resume_id, job_id, round, status | 面试会话 |
| messages | id, interview_id, role, content, evaluation_id | 消息记录 |
| evaluations | id, interview_id, dimension, score, comment | 评判记录 |
| reviews | id, interview_id, overall_score, radar_data | 复盘报告 |
| growth_records | id, user_id, interview_id, dimension, score | 成长追踪 |
| applications | id, user_id, company, position, status | 投递看板 |

## 5. 缓存策略

### 5.1 Redis使用场景

| 场景 | Key模式 | TTL | 说明 |
|------|---------|-----|------|
| 简历诊断结果 | `diag:{resume_id}:{jd_hash}` | 2h | 相同简历+JD直接返回缓存 |
| 岗位分析结果 | `job:analyze:{jd_hash}` | 1h | 相同JD分析结果复用 |
| 匹配分析结果 | `job:match:{resume_id}:{job_id}` | 1h | 相同简历+岗位匹配结果复用 |
| 面试会话上下文 | `interview:{interview_id}` | 2h | 存储已问问题、简历文本、JD文本 |
| API限流计数 | `rate:{identifier}:{path}` | 60s/3600s | 滑动窗口限流 |
| 分布式锁 | `lock:{resource_id}` | 30s | 防止并发冲突 |

### 5.2 缓存更新策略

- **被动更新**：缓存过期后重新计算
- **主动失效**：简历重新上传时清除相关诊断缓存

## 6. 安全设计

### 6.1 多层安全体系

```
┌─────────────────────────────────────────┐
│  边界层：CORS、文件上传校验、路径遍历检测    │
├─────────────────────────────────────────┤
│  认证层：JWT Token、密码复杂度、Token刷新   │
├─────────────────────────────────────────┤
│  接口层：API限流、请求日志、ID追踪          │
├─────────────────────────────────────────┤
│  数据层：SQL注入防护、参数化查询            │
├─────────────────────────────────────────┤
│  存储层：文件内容类型检测、对象存储隔离      │
└─────────────────────────────────────────┘
```

### 6.2 文件上传安全

1. **扩展名白名单**：仅允许 .pdf, .docx, .txt
2. **MIME类型校验**：与声明的MIME对比
3. **内容类型检测**：通过magic number识别真实文件类型
4. **大小限制**：最大10MB
5. **路径遍历检测**：阻止 `../` 等恶意路径
6. **文件名安全化**：去除特殊字符

## 7. 部署架构

### 7.1 Docker Compose 配置

```yaml
services:
  frontend:  nginx serving static files
  backend:   FastAPI + uvicorn
  postgres:  PostgreSQL 15
  redis:     Redis 7 (持久化)
  # minio:   MinIO (可选，本地存储为fallback)
```

### 7.2 环境配置

| 环境变量 | 开发环境 | 生产环境 |
|---------|---------|---------|
| DATABASE_URL | SQLite | PostgreSQL |
| REDIS_URL | 可选 | 必填 |
| MINIO_ENDPOINT | 本地文件 | MinIO服务 |
| APP_DEBUG | true | false |
| LLM API Keys | 可选 | 推荐配置 |
