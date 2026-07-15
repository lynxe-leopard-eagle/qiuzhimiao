<div align="center">

# 求职喵 — 你的 AI 面试教练

面试不慌，喵喵帮忙

[![TRAE AI Contest](https://img.shields.io/badge/TRAE%20AI-%E5%88%9B%E9%80%A0%E5%8A%9B%E5%A4%A7%E8%B5%9B-blue)](https://forum.trae.cn)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-green)](https://python.org)
[![React 18](https://img.shields.io/badge/React-18-61dafb)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**求职喵 = 简历医生 + 岗位分析师 + 面试陪练 + 复盘教练**

[在线演示](链接) · [创意文档](链接) · [产品 PRD](链接) · [技术架构](链接)

</div>

---

## 目录

- [一、项目简介](#一项目简介)
  - [1.1 产品定位](#11-产品定位)
  - [1.2 核心价值](#12-核心价值)
  - [1.3 目标用户](#13-目标用户)
  - [1.4 竞品对比](#14-竞品对比)
  - [1.5 Demo 预览](#15-demo-预览)
- [二、功能规划](#二功能规划)
  - [2.1 核心功能全景图](#21-核心功能全景图)
  - [2.2 用户核心旅程](#22-用户核心旅程)
  - [2.3 六大功能模块详解](#23-六大功能模块详解)
- [三、技术架构](#三技术架构)
  - [3.1 技术栈总览](#31-技术栈总览)
  - [3.2 系统架构图](#32-系统架构图)
  - [3.3 前端目录结构](#33-前端目录结构)
  - [3.4 后端目录结构](#34-后端目录结构)
  - [3.5 数据库设计](#35-数据库设计)
- [四、层次要求与实现思路](#四层次要求与实现思路)
  - [4.1 表现层](#41-表现层)
  - [4.2 控制层](#42-控制层)
  - [4.3 业务逻辑层](#43-业务逻辑层)
  - [4.4 数据访问层](#44-数据访问层)
- [五、智能化技术方案](#五智能化技术方案)
  - [5.1 Agent 智能体架构](#51-agent-智能体架构)
  - [5.2 RAG 知识库方案](#52-rag-知识库方案)
  - [5.3 Agent 记忆系统](#53-agent-记忆系统)
  - [5.4 语音交互方案](#54-语音交互方案)
- [六、部署与运行](#六部署与运行)
  - [6.1 环境要求](#61-环境要求)
  - [6.2 本地开发](#62-本地开发)
  - [6.3 Docker Compose 部署](#63-docker-compose-部署)
  - [6.4 生产部署](#64-生产部署)
- [七、项目路线图](#七项目路线图)
- [附录](#附录)

---

## 一、项目简介

### 1.1 产品定位

求职喵是一款面向理工科求职者的 AI 面试教练 Web 应用，覆盖"简历诊断 - 岗位分析与匹配 - AI 面试模拟 - 复盘成长"全链路。

系统内置三大智能体——面试官 Agent、评判 Agent、复盘 Agent，通过 LangGraph 编排协作，实现从提问、实时评判到复盘报告的全流程 AI 自动化。

**核心目标岗位：**

- AI 应用开发工程师
- Agent 应用开发工程师
- 算法工程师（全方向）
- 后端开发工程师
- 产品经理（技术方向）

**覆盖行业：** 互联网、游戏、机器人、芯片/半导体、AI 公司

### 1.2 核心价值

- **效率提升**：10 分钟搞定简历诊断，AI 替代重复性准备，面试官 7x24 在线
- **精准匹配**：基于 JD 深度分析，量化简历与岗位匹配度，精准定位差距
- **真实模拟**：5 层项目深挖模型，AI 实时追问，比刷面经有效得多
- **成长可见**：能力雷达图 + 成长曲线，进步有方向

### 1.3 目标用户

| 用户类型 | 占比 | 典型场景 |
|---------|------|---------|
| 应届生校招 | 40% | 海投简历石沉大海、面试紧张不知道说什么、被拒后不知道原因 |
| 在校生找实习 | 35% | 第一次投实习简历不知道怎么写、面试时被问到课程项目不知道怎么展开 |
| 应届生找工作 | 15% | 错过校招窗口，与社招人员竞争劣势，缺乏实习经历 |
| 社招/转岗 | 10% | 项目经验不知道怎么包装成目标岗位所需、转岗时技能匹配度不足 |

**全学历覆盖：** 985 / 211 / 一本 / 二本 / 民办本科 / 专科

### 1.4 竞品对比

| 维度 | 求职喵 | 超级简历 | 牛客网 | HireVue |
|------|--------|---------|--------|---------|
| 简历诊断 | AI 深度诊断 + 优化建议 | 模板排版 | 无 | 无 |
| 岗位分析与匹配 | JD 深度分析 + 简历匹配度量化 + 差距分析 | 无 | 简单标签 | 无 |
| AI 面试 | 动态追问模拟 | 无 | 笔试题库 | 企业端（不面向求职者） |
| 面试复盘 | 逐题点评 + 改进建议 | 无 | 简单解析 | 无 |
| 成长追踪 | 雷达图 + 趋势曲线 | 无 | 无 | 无 |

### 1.5 Demo 预览

当前项目为**完整前后端实现**，包含真实 API 服务和数据库持久化，可直接运行体验全部功能。

**包含九大功能模块：**

| 模块 | 功能说明 | 状态 |
|------|---------|------|
| 简历上传与诊断 | 支持 PDF/Word 简历上传、AI 解析、五维度诊断评分 | ✅ 完整实现 |
| 岗位分析与匹配 | JD 深度分析（技能/级别/难度/市场）、简历匹配度四维评估、AI 差距分析 | ✅ 完整实现 |
| AI 面试模拟 | HR 面/技术一面/技术二面三轮模拟、SSE 实时流式回答、实时评判评分 | ✅ 完整实现 |
| 面试评判 | 五维度基础评分 + 五维度条件触发评分（学习能力、抗压表现、问题拆解、工程素养、创新思维） | ✅ 完整实现 |
| 复盘报告 | 逐题点评、能力雷达图、改进建议、面试官视角总结 | ✅ 完整实现 |
| 成长追踪 | 能力雷达图对比、成长趋势曲线、薄弱点分析 | ✅ 完整实现 |
| 技能图谱 | 技能雷达图、技能树、技能差距分析 | ✅ 完整实现 |
| 投递看板 | 五列拖拽看板、投递统计、状态管理 | ✅ 完整实现 |
| AI 教练 | ReAct Agent 架构、对话式交互、个性化求职策略 | ✅ 完整实现 |

**测试账号：**
- 邮箱：`test@qiuzhimiao.com`
- 密码：`test123456`

**启动方式：**
```bash
# 后端（http://localhost:8000）
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 前端（http://localhost:5173）
cd frontend
npm run dev
```

**核心技术特性：**
- 前端：React 18 + Vite + TypeScript + Tailwind CSS + Zustand + Recharts
- 后端：FastAPI + SQLAlchemy async + PostgreSQL/SQLite + Pydantic + JWT
- 实时通信：Server-Sent Events（SSE）实现面试流式对话

---

## 二、功能规划

### 2.1 核心功能全景图

```mermaid
flowchart TB
    subgraph 入口层
        A[简历上传] --> B[岗位 JD 粘贴]
    end
    subgraph 分析层
        C[简历诊断] --> D[岗位分析与匹配]
        D --> E[项目分析]
    end
    subgraph 面试层
        F[AI 面试模拟器]
        F --> G[面试官 Agent 提问]
        G --> H[用户回答]
        H --> I[评判 Agent 评分]
        I -->|追问| G
        I -->|结束| J[复盘 Agent]
    end
    subgraph 成长层
        J --> K[复盘报告]
        K --> L[成长追踪]
        L --> M[薄弱点训练]
    end
    A --> C
    B --> D
    E --> F
```

### 2.2 用户核心旅程

用户从注册到获得面试能力的完整路径分为四步：

```
上传简历  -->  选择岗位  -->  开始面试  -->  查看报告
```

1. **上传简历**：用户上传 PDF/Word/TXT 格式的简历，系统自动解析提取关键信息（教育背景、项目经验、技能列表等）
2. **选择岗位**：粘贴目标岗位 JD，系统进行岗位深度分析，再与简历进行匹配度评估，给出四维度评分与差距分析
3. **开始面试**：选择面试轮次（HR 面 / 技术一面 / 技术二面），AI 面试官发起对话，实时追问、实时评判
4. **查看报告**：面试结束后，复盘 Agent 生成完整复盘报告，包含逐题点评、能力雷达图与改进建议

### 2.3 九大功能模块详解

#### 2.3.1 简历诊断与优化 `[MVP]`

- **简历上传**：支持 PDF / Word / TXT 格式，AI 自动解析提取关键信息
- **五维度诊断模型**：

  | 维度 | 权重 | 评估内容 |
  |------|------|---------|
  | 结构完整性 | 20% | 各模块（教育/经历/技能/项目）是否齐全、顺序是否合理 |
  | 内容质量 | 30% | 描述是否具体、是否有量化成果、动词使用是否专业 |
  | 关键词匹配 | 25% | 与目标岗位 JD 的技能关键词重合度 |
  | 量化表达 | 15% | 数据、百分比、排名等量化指标的使用频率与质量 |
  | 排版规范 | 10% | 格式一致性、字体字号统一、信息密度 |

- **输出内容**：匹配度百分比 + 优势/改进/缺失项列表 + 技能匹配分析条 + 迭代优先级标注

#### 2.3.2 岗位分析与简历匹配 `[MVP]`

**岗位分析**：对 JD 进行深度结构化解析，提取关键信息

- **基本信息提取**：岗位级别、工作经验要求、学历要求、薪资范围
- **技能识别**：核心技能要求（必会项）+ 加分项技能
- **职责梳理**：岗位职责列表 + 任职硬性要求列表
- **综合评估**：面试难度评分（0-100）、市场需求热度、职业前景分析

**简历与岗位匹配度分析**：基于岗位分析结果，与简历进行四维度量化匹配

- **四维度匹配度评分**：

  | 维度 | 说明 |
  |------|------|
  | 硬性条件 | 学历、工作年限、行业经验等硬性门槛 |
  | 技能关键词 | 技术/工具/框架等关键词匹配度 |
  | 项目经验 | 简历中的项目与岗位要求的契合度 |
  | 行业经验 | 行业背景、领域知识的匹配情况 |

- **AI 匹配分析输出**：匹配理由 + 核心优势 + 关键差距 + 行动建议

#### 2.3.3 项目分析与面试预演 `[P1]`

采用独创的 5 层项目深挖模型，帮助用户系统化梳理项目经验：

| 层级 | 关注点 | 典型问题 |
|------|--------|---------|
| L1 项目概述 | 做了什么、为什么做 | "介绍一下你最有成就感的项目" |
| L2 角色与贡献 | 你负责什么、团队多大 | "你在项目中承担什么角色？" |
| L3 技术细节 | 用了什么技术、怎么选型的 | "为什么选 LangChain 而不是自研？" |
| L4 难点与决策 | 遇到什么问题、怎么解决的 | "最大的技术难点是什么？" |
| L5 数据与反思 | 效果如何、如果重来会怎么做 | "如果重新做会有什么不同？" |

面试预演会按照 L1 -> L5 逐层深入，用户可针对薄弱层级反复练习。

#### 2.3.4 AI 面试模拟器 `[MVP]` -- 核心亮点

- **三轮次切换**：

  | 轮次 | 面试重点 | 考察能力 |
  |------|---------|---------|
  | HR 面 | 职业规划、团队协作、自我介绍、离职原因 | 沟通表达、职业素养 |
  | 技术一面 | 项目深挖、技术基础、编码能力 | 专业能力、项目讲解 |
  | 技术二面 | 系统设计、架构能力、开放性问题 | 架构思维、逻辑推理 |

- **动态追问策略**：根据回答深度决定是否追问，直接切入技术细节，不使用过渡语

- **实时评判面板**：专业能力、逻辑表达、沟通能力、项目讲解、岗位匹配度五维度实时评分 + 条件触发维度（学习能力、抗压表现、问题拆解、工程素养、创新思维）

- **行业/公司风格定制**：可根据目标公司类型调整面试风格（大厂面 vs 创业公司面）

追问触发逻辑：

```python
def should_follow_up(answer, context):
    """根据用户回答质量决定追问策略"""
    if answer.is_vague:
        return generate_specific_question(context)
    if answer.has_data_points:
        return ask_data_validation(context)
    if answer.has_architecture:
        return ask_bottleneck_and_scaling(context)
    if answer.is_excellent:
        return escalate_difficulty(context)
    return move_to_next_topic()
```

#### 2.3.5 面试复盘与成长 `[MVP]`

复盘报告结构：

1. **综合评分总览** — 五维度雷达图 + 总分
2. **逐题回顾与点评** — 每道题的回答摘要、评分、改进建议
3. **面试官视角总结** — 从面试官角度的整体评价与录用建议
4. **成长趋势对比** — 与历史面试数据的趋势对比图
5. **下次策略建议** — 基于薄弱环节的个性化练习建议

- **能力雷达图**：使用 SVG/Canvas 绘制六维度雷达图（专业能力、逻辑表达、沟通能力、项目讲解、岗位匹配度、综合素养）
- **改进建议卡片** + 下次练习重点标签

#### 2.3.6 薄弱点专项训练 `[P2]`

基于多次面试数据的薄弱点自动识别与专项训练：

| 薄弱点类型 | 检测指标 | 训练方式 |
|-----------|---------|---------|
| 数据支撑不足 | 回答中缺乏量化数据 | 引导式数据挖掘练习 |
| 技术深度不够 | 技术题回答停留在表面 | 深度追问专项练习 |
| 逻辑清晰度差 | 回答结构混乱、条理不清 | STAR 法则结构化训练 |
| 表达流畅度低 | 回答磕巴、停顿过多 | 模拟面试流利度训练 |
| 内容完整度低 | 回答遗漏关键信息 | 要素检查清单训练 |

#### 2.3.7 技能图谱 `[P1]`

- **技能雷达图**：基于简历和目标 JD，生成技能覆盖雷达图，直观展示技能广度与深度
- **技能树**：按技术领域（前端/后端/数据/DevOps 等）展示技能层级关系
- **技能差距分析**：对比简历技能与目标岗位技能要求，识别缺失技能和需提升技能

#### 2.3.8 投递看板 `[P1]`

- **五列看板**：待投递 → 已投递 → 面试中 → 已 Offer → 已拒绝
- **拖拽排序**：支持拖拽移动卡片在不同阶段间切换
- **投递统计**：投递总数、面试率、Offer 率等关键指标统计
- **信息管理**：公司、岗位、城市、薪资范围、备注、联系人等

#### 2.3.9 AI 教练 `[P1]`

- **ReAct Agent 架构**：基于推理-行动循环的智能体，支持工具调用和多轮记忆
- **工具集成**：简历查询、JD 分析、面试策略建议等工具
- **对话式交互**：自然语言对话，支持上下文连续追问
- **个性化报告**：基于对话历史生成个性化求职策略报告

---

## 三、技术架构

### 3.1 技术栈总览

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 前端 | React + Vite + TypeScript | 18 / 5.x | SPA 构建 |
| 前端 | Tailwind CSS | 3.x | 原子化样式 |
| 前端 | Zustand | 4.x | 轻量状态管理 |
| 前端 | Recharts | 2.x | 数据可视化（雷达图/趋势图） |
| 前端 | Framer Motion | 10.x | 交互动效 |
| 前端 | lucide-react | latest | 图标库 |
| 前端 | axios | 1.x | HTTP 请求 |
| 后端 | FastAPI | 0.110 | REST API + SSE |
| 后端 | SQLAlchemy | 2.0 | 异步 ORM 数据访问 |
| 后端 | Pydantic | 2.x | 数据校验与序列化 |
| 后端 | python-jose + passlib | latest | JWT 认证 + bcrypt 密码哈希 |
| 后端 | Alembic | 1.x | 数据库迁移 |
| 数据库 | PostgreSQL + pgvector | 15+ | 关系型 + 向量存储 |
| 数据库 | Redis | 7.x | 缓存 + 会话 + 消息队列 |
| 数据库 | MinIO | latest | 对象存储（简历文件） |
| AI 层 | LangGraph | 0.x | Agent 编排引擎 |
| AI 层 | LangChain | 0.x | LLM 调用与工具链 |
| AI 层 | 豆包 / DeepSeek / 通义千问 | latest | 多模型调度 |
| 部署 | Docker + Docker Compose | latest | 容器化部署 |
| 部署 | Nginx | 1.25 | 反向代理 + 静态资源 |

### 3.2 系统架构图

```mermaid
flowchart TB
    subgraph 用户层
        U[浏览器 / 移动端]
    end
    subgraph 表现层
        FE[React 18 + Vite + Tailwind CSS]
    end
    subgraph 控制层
        NG[Nginx 反向代理]
        API[FastAPI REST API + WebSocket]
    end
    subgraph 业务逻辑层
        RS[简历服务]
        IS[面试服务]
        JS[评判服务]
        RVS[复盘服务]
        GS[成长服务]
    end
    subgraph AI 引擎层
        LG[LangGraph 编排引擎]
        IA[面试官 Agent]
        EA[评判 Agent]
        RA[复盘 Agent]
        GW[路由 Gateway]
    end
    subgraph 数据层
        PG[PostgreSQL + pgvector]
        RD[Redis]
        MO[MinIO]
    end
    U --> FE
    FE --> NG --> API
    API --> RS & IS & JS & RVS & GS
    IS --> LG --> IA & EA & RA
    LG --> GW
    RS --> PG & RD
    IS --> PG & RD
```

### 3.3 前端目录结构

```
frontend/
├── public/
├── src/
│   ├── components/        # 通用 UI 组件
│   │   ├── layout/        # Navbar / Sidebar / Footer
│   │   ├── resume/        # 简历诊断模块
│   │   ├── interview/     # 面试模拟模块
│   │   ├── review/        # 复盘报告模块
│   │   └── charts/        # ECharts 可视化
│   ├── pages/             # 页面路由
│   ├── stores/            # Zustand 状态管理
│   ├── hooks/             # 自定义 Hooks
│   ├── services/          # API 调用封装
│   ├── utils/             # 工具函数
│   └── styles/            # Tailwind 自定义主题
├── package.json
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

### 3.4 后端目录结构

```
backend/
├── app/
│   ├── main.py            # FastAPI 入口
│   ├── config.py          # 配置管理
│   ├── api/v1/            # API 路由层
│   │   ├── resume.py      # 简历诊断接口
│   │   ├── job.py         # 岗位分析与匹配接口
│   │   ├── interview.py   # 面试模拟接口
│   │   ├── review.py      # 复盘报告接口
│   │   ├── skill.py       # 技能图谱接口
│   │   ├── coach.py       # AI 教练接口
│   │   ├── application.py  # 投递看板接口
│   │   └── growth.py      # 成长追踪接口
│   ├── models/            # SQLAlchemy 数据模型
│   ├── schemas/           # Pydantic 请求/响应模型
│   ├── services/          # 业务逻辑层
│   │   ├── agent/         # Agent 智能体
│   │   │   ├── interviewer.py
│   │   │   ├── evaluator.py
│   │   │   ├── reviewer.py
│   │   │   └── router.py  # 多模型路由网关
│   │   └── rag/           # RAG 引擎
│   │       ├── embedder.py
│   │       ├── retriever.py
│   │       └── knowledge_base.py
│   ├── core/              # 核心模块
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── redis.py
│   │   └── minio.py
│   └── tasks/             # Celery 异步任务
├── alembic/               # 数据库迁移
├── tests/
├── requirements.txt
└── Dockerfile
```

### 3.5 数据库设计

**核心业务表：**

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| users | 用户表 | id, email, password_hash, nickname, created_at |
| resumes | 简历表 | id, user_id, parsed_content(JSONB), file_path, is_default |
| jobs | 岗位表 | id, user_id, title, company, description, requirements(JSONB), category |
| applications | 投递看板表 | id, user_id, company, position, stage, city, salary_range, notes |
| interviews | 面试会话表 | id, user_id, resume_id, job_id, round, status, duration |
| messages | 消息记录表 | id, interview_id, role, content, model_used, latency_ms |
| evaluations | 评判记录表 | id, interview_id, message_id, professional/logic/communication/project/match/learning/stress_resistance/decomposition/engineering_quality/innovation（后5项为条件触发维度，nullable） |
| reviews | 复盘报告表 | id, interview_id, overall_score, radar_data(JSONB), suggestions(JSONB) |
| growth_records | 成长追踪表 | id, user_id, dimension, score, record_date |

**向量表（pgvector）：**

| 表名 | 说明 | 向量维度 |
|------|------|---------|
| resume_embeddings | 简历语义向量 | vector(1536) |
| job_embeddings | 岗位 JD 语义向量 | vector(1536) |
| question_embeddings | 面试题目语义向量 | vector(1536) |
| knowledge_embeddings | 知识库文档向量 | vector(1536) |

向量检索使用 pgvector 的 HNSW 索引，支持高维近似最近邻查询（IVFFlat 作为备选方案）。

---

## 四、层次要求与实现思路

```
+--------------------------------------------------+
|                    表现层                          |
|   React 18 + Vite + TailwindCSS + Zustand        |
+--------------------------------------------------+
|                    控制层                          |
|   FastAPI REST API + WebSocket + Nginx           |
+--------------------------------------------------+
|                  业务逻辑层                        |
|   Service 层 + Celery 异步任务 + LangGraph Agent   |
+--------------------------------------------------+
|                  数据访问层                        |
|   SQLAlchemy ORM + pgvector + Redis + MinIO       |
+--------------------------------------------------+
```

### 4.1 表现层

- **React 18 + Vite** 构建 SPA，利用 Vite 的 HMR 实现快速开发迭代
- **TailwindCSS 原子化样式**：避免编写冗余 CSS，保持设计一致性
- **Zustand 状态管理**：选型理由——比 Redux 轻量（打包体积约 1KB），API 简洁（无需 Provider 包裹），适合中等规模应用的状态管理需求
- **SSE 实时通信**：面试场景下基于 Server-Sent Events 实现流式消息推送，轻量高效
- **Recharts 数据可视化**：雷达图（能力维度）、趋势曲线（成长追踪）、柱状图（评分对比）
- **Framer Motion 交互动效**：页面过渡动画、卡片展开/折叠、评分进度动画

### 4.2 控制层

- **FastAPI 路由模式**：RESTful API 负责 CRUD 操作，SSE 负责面试实时对话流式推送

- **API 路由表**：

  | 模块 | 前缀 | 核心接口 |
  |------|------|---------|
  | 用户认证 | `/api/v1/auth` | POST /register, POST /login, GET /me |
  | 简历诊断 | `/api/v1/resume` | POST /upload, GET /{id}, POST /diagnose |
  | 岗位分析与匹配 | `/api/v1/jobs` | POST /analyze（岗位分析）, POST /matching（匹配分析） |
  | 面试模拟 | `/api/v1/interview` | POST /start, WS /chat, POST /end |
  | 复盘报告 | `/api/v1/review` | GET /{interview_id}, GET /list |
  | 成长追踪 | `/api/v1/growth` | GET /radar, GET /trend |

- **中间件栈**：

  | 中间件 | 功能 |
  |--------|------|
  | CORS | 跨域资源共享控制 |
  | JWT Auth | 基于 JSON Web Token 的用户认证 |
  | Rate Limiter | API 限流（防止滥用） |
  | Request Logger | 请求日志记录与追踪 |

- **WebSocket 事件协议**：

  | 事件 | 方向 | Payload |
  |------|------|---------|
  | `interview:question` | Server -> Client | `{ question_id, content, round, topic }` |
  | `interview:answer` | Client -> Server | `{ answer_text, audio_url? }` |
  | `interview:evaluation` | Server -> Client | `{ scores: {...}, feedback, should_follow_up }` |
  | `interview:ended` | Server -> Client | `{ reason, review_id }` |

### 4.3 业务逻辑层

- **Service 层单一职责**：每个 Service 只负责一个业务域，通过依赖注入解耦

- **核心流程编排**：

  - **简历诊断流程**：文件上传 -> 解析提取 -> 五维度评分 -> 生成诊断报告 -> 缓存结果
  - **面试模拟流程**：创建会话 -> Agent 初始化 -> 提问-回答循环 -> 实时评判 -> 结束复盘
  - **岗位匹配流程**：JD 解析 -> 岗位分析（技能/级别/难度/市场） -> 简历匹配度评估 -> 四维度评分 -> 差距分析 -> 输出建议

- **Celery 异步任务**：

  | 任务 | 触发场景 | 说明 |
  |------|---------|------|
  | resume_parse | 简历上传后 | PDF/Word 解析、关键信息提取 |
  | audio_transcribe | 语音面试时 | Whisper 录音转文字 |
  | report_generate | 面试结束后 | 长文本复盘报告生成 |
  | embedding_update | 新知识入库时 | 文档向量化与索引更新 |

### 4.4 数据访问层

- **SQLAlchemy 2.0 ORM**：使用声明式映射（Declarative Mapping），支持 async session
- **Alembic 迁移管理**：版本化数据库 Schema 变更，支持 upgrade/downgrade
- **pgvector 向量检索**：
  - 索引类型：HNSW（默认，适合中小规模数据）、IVFFlat（大规模数据备选）
  - 距离度量：Cosine Similarity（余弦相似度）
  - Top-K 检索：默认返回 Top-5 最相关文档
- **Redis 缓存策略**：

  | 缓存类型 | Key 模式 | TTL | 说明 |
  |---------|---------|-----|------|
  | 会话上下文 | `session:{interview_id}` | 2h | 当前面试会话的对话历史 |
  | 诊断结果 | `diag:{resume_id}:{job_id}` | 24h | 简历诊断缓存 |
  | 用户 Token | `token:{user_id}` | 7d | JWT Token 黑名单 |
  | 限流计数 | `rate:{ip}:{endpoint}` | 1min | API 限流滑动窗口 |

- **MinIO 对象存储**：存储用户上传的简历文件（PDF/Word），通过 presigned URL 实现安全下载

---

## 五、智能化技术方案

### 5.1 Agent 智能体架构（3+1）

系统采用"3 个专业 Agent + 1 个路由 Gateway"的架构设计，通过 LangGraph 进行统一编排。

```mermaid
flowchart LR
    subgraph 路由 Gateway
        GW[Model Router]
    end
    subgraph 三大 Agent
        IA[面试官 Agent]
        EA[评判 Agent]
        RA[复盘 Agent]
    end
    subgraph LLM 层
        D[豆包]
        S[DeepSeek]
        Q[通义千问]
    end
    GW -->|提问场景| D
    GW -->|评判场景| S
    GW -->|报告场景| Q
    IA --> GW
    EA --> GW
    RA --> GW
```

#### 面试官 Agent（Interviewer Agent）

- **角色定义**：模拟真实面试官，根据轮次、岗位、用户简历动态生成面试问题
- **轮次规则**：HR 面侧重软技能考察，技术一面侧重项目深挖，技术二面侧重系统设计
- **追问规则**：回答模糊时追问细节，回答优秀时提升难度，回答较差时降低难度

- **追问策略**：

  | 回答质量 | 策略 | 示例 |
  |---------|------|------|
  | 模糊/笼统 | 追问具体细节 | "你提到'优化了性能'，具体优化了哪些指标？" |
  | 有数据支撑 | 验证数据合理性 | "QPS 从 100 提升到 1000，用的是什么压测工具？" |
  | 涉及架构 | 追问瓶颈与扩展性 | "如果流量再增加 10 倍，这个方案还能扛住吗？" |
  | 优秀回答 | 提升难度 | "那如果让你重新设计，你会怎么做？" |

- **Function Calling 工具列表**：

  | 工具名 | 功能 | 调用时机 |
  |--------|------|---------|
  | `query_resume` | 查询用户简历信息 | 需要了解用户背景时 |
  | `query_jd` | 查询岗位 JD 要求 | 需要针对性提问时 |
  | `search_knowledge` | 检索知识库 | 需要获取行业/公司面试风格时 |
  | `get_history` | 获取历史面试记录 | 需要避免重复提问时 |

#### 评判 Agent（Evaluator Agent）

- **五维度评分标准（基础维度）**：

  | 维度 | 分值范围 | 评估内容 |
  |------|---------|---------|
  | 专业能力 | 0-100 | 技术知识、工具使用、方案设计 |
  | 逻辑表达 | 0-100 | 回答结构、因果推理、条理性 |
  | 沟通能力 | 0-100 | 语言组织、倾听理解、互动反馈 |
  | 项目讲解 | 0-100 | STAR 法则运用、量化数据、难点展示 |
  | 岗位匹配度 | 0-100 | 技能匹配、经验匹配、潜力评估 |

- **条件触发维度（仅在面试中涉及相关话题时触发评分，未触发为 null）**：

  | 维度 | 分值范围 | 触发关键词示例 |
  |------|---------|-------------|
  | 学习能力 | 0-100 或 null | 学习、研究、快速上手、阅读源码 |
  | 抗压表现 | 0-100 或 null | 压力、deadline、加班、线上事故 |
  | 问题拆解 | 0-100 或 null | 设计、架构、分析、拆解、模块 |
  | 工程素养 | 0-100 或 null | 代码质量、规范、测试、CI/CD、重构 |
  | 创新思维 | 0-100 或 null | 创新、优化、改进、新思路、自研 |

- **JSON 输出格式**：

```json
{
  "evaluation": {
    "professional": 85,
    "logic": 78,
    "communication": 82,
    "project": 75,
    "match": 80,
    "overall": 80,
    "confidence": 0.85
  },
  "feedback": "技术基础扎实，但项目讲解缺乏量化数据支撑",
  "should_follow_up": true,
  "follow_up_question": "项目中具体的性能提升数据是多少？"
}
```

- **置信度标注机制**：每个评分附带 confidence 字段（0-1），低于 0.6 的评分标记为"低置信度"，在复盘报告中标注说明

#### 复盘 Agent（Reviewer Agent）

- **报告生成流程**：收集全部评判数据 -> 汇总统计 -> 生成雷达图数据 -> 逐题点评 -> 整体评价 -> 改进建议

- **JSON 输出结构**：

```json
{
  "review": {
    "overall_score": 78,
    "radar_data": {
      "professional": 85,
      "logic": 78,
      "communication": 82,
      "project": 72,
      "match": 80,
      "comprehensive": 79
    },
    "question_reviews": [
      {
        "question": "介绍一下你最熟悉的项目",
        "answer_summary": "介绍了基于 LangChain 的 RAG 项目",
        "score": 75,
        "strengths": ["技术选型清晰", "架构设计合理"],
        "improvements": ["缺少量化数据", "未提及遇到的难点"]
      }
    ],
    "interviewer_summary": "候选人技术基础扎实，项目经验尚可，但表达缺乏数据支撑",
    "suggestions": [
      {"priority": "high", "dimension": "project", "action": "练习用 STAR 法则描述项目"},
      {"priority": "medium", "dimension": "professional", "action": "补充系统设计相关知识"}
    ]
  }
}
```

#### 路由 Gateway（Model Router）

- **三模型调度策略**：

  | 模型 | 适用场景 | 选型理由 |
  |------|---------|---------|
  | 豆包（Doubao） | 面试提问生成 | 中文能力强，响应速度快，性价比高 |
  | DeepSeek | 实时评判评分 | 推理能力强，适合结构化评分任务 |
  | 通义千问（Qwen） | 复盘报告生成 | 国产大模型，长文本处理能力强，成本友好 |

- **调度决策逻辑**：

```python
def route_model(task_type, context):
    """根据任务类型和上下文选择最优模型"""
    model_map = {
        "interview_question": "doubao",
        "evaluation": "deepseek",
        "review_report": "claude"
    }
    primary = model_map[task_type]

    # 降级策略：主模型不可用时自动切换
    if not is_model_available(primary):
        fallback_order = {
            "doubao": ["deepseek", "claude"],
            "deepseek": ["doubao", "claude"],
            "claude": ["deepseek", "doubao"]
        }
        for fallback in fallback_order[primary]:
            if is_model_available(fallback):
                return fallback

    return primary
```

#### LangGraph 编排

使用 LangGraph 的 StateGraph 定义面试流程状态机：

```mermaid
stateDiagram-v2
    [*] --> InitSession: 用户开始面试
    InitSession --> LoadContext: 加载简历/JD/历史
    LoadContext --> GenerateQuestion: 面试官 Agent
    GenerateQuestion --> WaitAnswer: 等待用户回答
    WaitAnswer --> EvaluateAnswer: 评判 Agent
    EvaluateAnswer --> GenerateQuestion: 需要追问
    EvaluateAnswer --> CheckComplete: 不追问
    CheckComplete --> GenerateQuestion: 题目未完
    CheckComplete --> GenerateReview: 面试结束
    GenerateReview --> [*]: 复盘 Agent 生成报告
```

### 5.2 RAG 知识库方案

RAG（Retrieval-Augmented Generation）用于增强面试官 Agent 的专业性，使其能够基于真实面试题库和行业知识进行提问。

**处理流程：**

```
文档采集  -->  文本分块  -->  Embedding 向量化  -->  pgvector 存储
                                                          |
用户提问  -->  问题向量化  -->  相似度检索 Top-K  -->  上下文拼接  -->  LLM 生成
```

**4D 知识库矩阵：**

| 维度 | 说明 | 示例 |
|------|------|------|
| 行业维度 | 不同行业的面试侧重点 | 互联网/AI/芯片/游戏 |
| 公司维度 | 各公司面试风格与题库 | 字节/腾讯/阿里/华为 |
| 岗位维度 | 不同岗位的考察重点 | 后端/算法/产品/AI 工程师 |
| 轮次维度 | 各轮次的面试策略 | HR 面/技术一面/技术二面 |

每条知识条目包含：原文内容、所属维度标签、难度等级、使用频率统计。

### 5.3 Agent 记忆系统

```mermaid
flowchart LR
    subgraph 短期记忆
        R[Redis]
    end
    subgraph 长期记忆
        P[PostgreSQL]
    end
    U[用户回答] --> R
    R -->|当前会话上下文| IA[面试官 Agent]
    IA --> EA[评判 Agent]
    EA -->|评分数据| P
    P -->|历史弱项| R
    R --> IA
```

- **短期记忆（Redis）**：存储当前面试会话的对话历史、实时评判数据、追问上下文。会话结束后自动清理（TTL = 2 小时）
- **长期记忆（PostgreSQL）**：存储跨会话的用户数据，包括历次面试评分、能力维度变化、薄弱点统计。用于成长追踪和面试策略调整

**记忆调用策略**：

| 记忆类型 | 调用时机 | 用途 |
|---------|---------|------|
| 短期-对话历史 | 每次生成问题前 | 避免重复提问、保持对话连贯 |
| 短期-评判数据 | 每次生成问题前 | 根据上轮表现调整难度 |
| 长期-薄弱点 | 初始化面试时 | 重点提问薄弱环节 |
| 长期-成长趋势 | 生成复盘报告时 | 对比历史数据计算趋势 |

### 5.4 语音交互方案

语音面试模式提供更接近真实面试的体验，支持语音输入与语音播报。

- **语音输入（ASR）**：OpenAI Whisper 模型，支持中文实时语音转文字
- **语音播报（TTS）**：Edge TTS / 系统合成语音，面试官问题以语音形式播报
- **实时通信**：WebRTC 实现低延迟语音流传输
- **语音质量分析**：分析语速、停顿频率、语气词使用频率等指标，作为"表达流畅度"维度的评分参考

**语音面试交互流程：**

```
用户说话  -->  WebRTC 音频流  -->  Whisper ASR  -->  文字
                                                         |
面试官文字  -->  TTS 合成  -->  WebRTC 音频流  -->  用户听到
```

---

## 六、部署与运行

### 6.1 环境要求

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.11+ | 后端运行时 |
| Node.js | 18+ | 前端构建工具 |
| PostgreSQL | 15+ | 主数据库（需安装 pgvector 扩展） |
| Redis | 7.x | 缓存与消息队列 |
| MinIO | latest | 对象存储（简历文件） |
| Docker | 24+ | 容器化部署（可选） |
| Docker Compose | 2.x | 多服务编排（可选） |

### 6.2 本地开发

**1. 克隆项目**

```bash
git clone https://github.com/your-org/jobs-cat.git
cd jobs-cat
```

**2. 启动后端**

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写数据库连接、API Key 等配置

# 数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

**3. 启动前端**

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 访问 http://localhost:5173
```

**4. 启动依赖服务（Redis / MinIO）**

```bash
# 使用 Docker 单独启动依赖服务
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name minio -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin123 \
  minio/minio server /data --console-address ":9001"
```

### 6.3 Docker Compose 部署

项目提供完整的 `docker-compose.yml`，一键启动全部服务：

```yaml
version: "3.9"

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:80"
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/jobs_cat
      - REDIS_URL=redis://redis:6379/0
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - postgres
      - redis
      - minio

  postgres:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=jobs_cat
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin123
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

volumes:
  postgres_data:
  minio_data:
```

启动命令：

```bash
docker-compose up -d --build
```

### 6.4 生产部署

#### Nginx 反向代理配置要点

```nginx
server {
    listen 80;
    server_name jobs-cat.example.com;

    # 前端静态资源
    location / {
        root /var/www/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### GitHub Actions CI/CD

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build & Deploy
        run: |
          docker-compose -f docker-compose.prod.yml up -d --build
```

#### 省钱方案：阿里云轻量应用服务器

- **配置**：2 核 2G 内存，40GB SSD
- **费用**：约 38 元/年（新用户优惠价）
- **运行能力**：足够运行全部 5 个服务（PostgreSQL / Redis / MinIO / Backend / Nginx），支撑约 100 并发用户
- **扩展建议**：用户量增长后可按需升级配置或拆分服务

---

## 七、项目路线图

| 阶段 | 目标 | 核心交付物 | 时间节点 |
|------|------|-----------|---------|
| MVP | 验证核心闭环 | 简历诊断 + 岗位分析与匹配 + AI 面试（3 层追问）+ 复盘报告 | 第 1-4 周 |
| v2.0 | 补齐关键差距 | LangGraph Agent 编排 + RAG 知识库 + 4D 题库 | 第 5-8 周 |
| 完整版 | 建立完整体验 | 语音面试 + Agent 记忆 + 多模型路由 | 第 9-12 周 |
| 护城河 | 建立不可替代性 | 1000+ 4D 标注真题库 + 全平台覆盖（Web/iOS/Android） | 第 13-20 周 |

**MVP 阶段验证指标：**

- 核心路径可用性：上传简历 -> 诊断 -> 面试 -> 复盘全流程跑通
- AI 回复质量：追问相关性 > 80%，评分合理性 > 70%
- 用户体验：单次面试完成率 > 60%，复盘报告阅读率 > 80%

---

## 附录

### A. 贡献指南

**分支策略：**

| 分支 | 用途 | 命名规范 |
|------|------|---------|
| `main` | 生产稳定版本 | - |
| `develop` | 开发集成分支 | - |
| `feature/*` | 新功能开发 | `feature/resume-diagnosis` |
| `fix/*` | Bug 修复 | `fix/websocket-timeout` |
| `docs/*` | 文档更新 | `docs/api-spec` |

**PR 流程：**

1. 从 `develop` 创建 `feature/*` 分支
2. 完成开发后提交 PR，至少 1 人 Code Review
3. CI 通过 + Review 通过后合并至 `develop`
4. 发布时从 `develop` 合并至 `main`

### B. 许可证

本项目采用 [MIT License](LICENSE) 开源许可。

### C. 相关链接

| 资源 | 链接 |
|------|------|
| 在线演示 | [Demo 页面](链接) |
| 创意文档 | [创意文档](链接) |
| 产品 PRD | [产品 PRD](链接) |
| 技术架构 | [技术架构](链接) |
| 问题反馈 | [GitHub Issues](链接) |

---

<div align="center">

**求职喵 -- 面试不慌，喵喵帮忙**

Built with React + FastAPI + LangGraph

</div>

