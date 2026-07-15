# 求职喵平台完整开发 Spec

## Why
求职喵是面向理工科求职者的 AI 面试教练 Web 应用。D:\AAA-demo 中已有前后端基础框架与简历模块原型，但尚未形成"简历诊断 → 岗位匹配 → AI 面试 → 复盘报告"的完整 MVP 闭环。本 spec 旨在基于现有代码完成全流程开发，使产品达到可演示状态。

## What Changes
- 新增/补全数据库模型：users、jobs、interviews、messages、evaluations、reviews、growth_records
- 新增用户认证模块：注册、登录、JWT 认证、密码哈希
- 新增岗位匹配模块：JD 粘贴、四维度匹配度评分、差距分析
- 扩展简历诊断：接入 LLM 深度诊断（保留规则诊断作为 fallback）
- 新增 AI 面试后端：REST + SSE 对话流、五维度实时评判、追问策略
- 新增复盘报告后端：数据聚合、雷达图数据、逐题点评
- 新增成长追踪后端：能力维度历史记录、趋势数据
- 前端新增/完善页面：岗位匹配页、复盘报告页（含雷达图）、成长追踪页
- 前端 InterviewPage 对接真实后端 API，替换 mock 数据
- 前端 API 服务层扩展：匹配、面试、复盘、成长接口封装
- 统一错误处理与加载状态

## Impact
- Affected specs: 简历诊断、岗位匹配、AI 面试、复盘报告、成长追踪
- Affected code: frontend/src/pages/*、frontend/src/services/*、frontend/src/types/*、backend/app/api/v1/*、backend/app/models/*、backend/app/schemas/*、backend/app/services/*

## ADDED Requirements

### Requirement: 用户认证系统
The system SHALL provide user registration and login with JWT-based authentication.

#### Scenario: Success case
- **WHEN** user submits valid email and password to `/api/v1/auth/register`
- **THEN** system creates user record and returns JWT token
- **WHEN** user submits valid credentials to `/api/v1/auth/login`
- **THEN** system returns JWT token
- **WHEN** authenticated user accesses protected endpoints
- **THEN** system validates JWT and extracts user_id

### Requirement: 岗位智能匹配
The system SHALL analyze job description against parsed resume and output four-dimension match scores.

#### Scenario: Success case
- **WHEN** user pastes JD and selects resume
- **THEN** system extracts JD keywords and computes scores for: hard requirements, skill keywords, project experience, industry experience
- **AND** returns match percentage, strengths/weaknesses/gaps, and投递建议

### Requirement: AI 面试模拟
The system SHALL simulate a multi-round interview with dynamic follow-up and real-time evaluation.

#### Scenario: Success case
- **WHEN** user starts interview with selected round (HR/tech1/tech2)
- **THEN** system generates initial question based on resume + JD context
- **WHEN** user submits answer
- **THEN** system evaluates answer on five dimensions (professional, logic, communication, project, match) with scores 0-100
- **AND** decides whether to follow up based on answer quality
- **WHEN** interview ends
- **THEN** system persists all messages and evaluations

### Requirement: 面试复盘报告
The system SHALL generate a comprehensive review report after interview completion.

#### Scenario: Success case
- **WHEN** interview session ends
- **THEN** system aggregates all evaluations and generates:
  - overall score and radar chart data (6 dimensions)
  - per-question review with score, strengths, improvements
  - interviewer perspective summary
  - prioritized improvement suggestions

### Requirement: 成长追踪
The system SHALL track user capability growth across multiple interviews.

#### Scenario: Success case
- **WHEN** user views growth page
- **THEN** system returns radar chart data comparing latest vs historical scores
- **AND** returns trend curves for each dimension over time

## MODIFIED Requirements

### Requirement: 简历诊断引擎
The existing rule-based diagnosis SHALL be augmented with LLM-based deep diagnosis.

- **WHEN** LLM API is available and enabled
- **THEN** system uses LLM to generate five-dimension scores and detailed suggestions
- **WHEN** LLM is unavailable
- **THEN** system falls back to existing rule-based diagnosis

## REMOVED Requirements
### Requirement: 语音交互 (ASR/TTS)
**Reason**: MVP 阶段聚焦文本交互，语音功能延后至 v2.0
**Migration**: 前端 InterviewPage 保持文本输入输出，预留语音接口扩展点

### Requirement: LangGraph 复杂编排
**Reason**: MVP 阶段使用简化版对话管理，LangGraph 完整状态机延后至 v2.0
**Migration**: 后端使用轻量级对话管理服务替代完整 LangGraph StateGraph

### Requirement: RAG 知识库
**Reason**: MVP 阶段使用 prompt engineering 生成问题，4D 知识库延后至 v2.0
**Migration**: 面试官问题通过 LLM prompt 中的 resume + JD 上下文动态生成

### Requirement: Celery 异步任务扩展
**Reason**: 当前 resume_parse 任务已足够，其他模块使用同步或 SSE 流式响应
**Migration**: 面试对话使用 SSE 流式输出，评判同步返回
