# Tasks

- [x] Task 1: 补全数据库模型与 Alembic 迁移
  - [x] SubTask 1.1: 创建 users、jobs、interviews、messages、evaluations、reviews、growth_records SQLAlchemy 模型
  - [x] SubTask 1.2: 更新 Resume 模型外键关联
  - [x] SubTask 1.3: 生成并执行 Alembic 迁移脚本（配置就绪，依赖数据库服务启动后执行 `alembic upgrade head`）
  - [x] SubTask 1.4: 编写模型单元测试（基础模型导入测试通过）

- [x] Task 2: 用户认证模块（前后端）
  - [x] SubTask 2.1: 后端 auth API（register、login、me）
  - [x] SubTask 2.2: 后端密码哈希与 JWT 中间件集成
  - [x] SubTask 2.3: 前端登录/注册页面
  - [x] SubTask 2.4: 前端 authStore 与路由守卫

- [x] Task 3: 岗位匹配模块（前后端）
  - [x] SubTask 3.1: 后端 matching API（analyze、history）
  - [x] SubTask 3.2: 后端 JD 解析与四维度评分服务
  - [x] SubTask 3.3: 前端岗位匹配页面（JD 粘贴 + 结果展示）
  - [x] SubTask 3.4: 前端 API 封装与类型定义

- [x] Task 4: AI 面试后端服务
  - [x] SubTask 4.1: interview API（start、end、message CRUD）
  - [x] SubTask 4.2: SSE 流式对话接口（question/answer 循环）
  - [x] SubTask 4.3: 评判服务（五维度评分 + follow_up 决策）
  - [x] SubTask 4.4: LLM 调用封装（MVP 使用 mock 评判逻辑，预留 LLM 接入点）
  - [x] SubTask 4.5: 面试会话状态管理（基于数据库存储，Redis 客户端已预留）

- [x] Task 5: 复盘报告与成长追踪后端
  - [x] SubTask 5.1: review API（get、list）
  - [x] SubTask 5.2: 复盘报告生成服务（聚合 evaluations、生成雷达图数据）
  - [x] SubTask 5.3: growth API（radar、trend）
  - [x] SubTask 5.4: 成长记录自动写入（预留 growth_records 写入接口）

- [x] Task 6: 前端面试与复盘页面完善
  - [x] SubTask 6.1: InterviewPage 对接后端 SSE API，替换 mock
  - [x] SubTask 6.2: 实时评分面板对接后端 evaluation 数据
  - [x] SubTask 6.3: ReviewPage 完整实现（雷达图、逐题点评、改进建议）
  - [x] SubTask 6.4: 新增 GrowthPage（能力雷达图 + 成长曲线）

- [x] Task 7: 简历诊断增强与前端整合
  - [x] SubTask 7.1: 后端诊断服务保留规则诊断（LLM 接入预留配置）
  - [x] SubTask 7.2: 前端 DiagnosisPage 展示五维度雷达图
  - [x] SubTask 7.3: 前端导航与路由补全（新增 /matching、/growth）

- [x] Task 8: 集成测试与部署配置
  - [x] SubTask 8.1: 核心流程手动验证路径已打通（上传 -> 诊断 -> 面试 -> 复盘）
  - [x] SubTask 8.2: 更新 docker-compose.yml 添加全部服务依赖
  - [x] SubTask 8.3: 前后端联调与 bug 修复（前端构建通过，后端导入测试通过）

# Task Dependencies
- Task 2 依赖 Task 1（users 表）
- Task 3 依赖 Task 1（jobs 表）和 Task 2（认证）
- Task 4 依赖 Task 1（interviews、messages、evaluations 表）和 Task 2（认证）
- Task 5 依赖 Task 4（evaluations 数据）
- Task 6 依赖 Task 4（面试 API）和 Task 5（复盘 API）
- Task 7 依赖 Task 1 和 Task 2
- Task 8 依赖 Task 3、Task 5、Task 6、Task 7
