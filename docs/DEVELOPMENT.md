# 求职喵 - 开发规范文档

## 1. 代码规范

### 1.1 Python 后端规范

#### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块/包 | 小写，下划线分隔 | `resume_service.py` |
| 类 | 大驼峰 | `BusinessException` |
| 函数/方法 | 小写，下划线分隔 | `diagnose_resume()` |
| 常量 | 全大写，下划线分隔 | `MAX_FILE_SIZE = 10 * 1024 * 1024` |
| 私有变量 | 前缀下划线 | `_internal_cache` |
| 异步函数 | 正常命名，使用 `async def` | `async def get_user()` |

#### 导入顺序

```python
# 1. 标准库
import json
import logging
from datetime import datetime

# 2. 第三方库
from fastapi import APIRouter, Depends
from sqlalchemy import select

# 3. 项目内部模块
from app.core.database import get_db_session
from app.models.user import User
```

#### 类型注解

```python
# 必须使用类型注解
async def get_user(user_id: str) -> User | None:
    ...

# 使用 | 而不是 Optional 和 Union (Python 3.10+)
def find_item(items: list[str], target: str) -> str | None:
    ...
```

#### 异常处理

```python
# 使用自定义业务异常
from app.core.exceptions import ResourceNotFoundException, ValidationException

# 不要直接返回 HTTPException，使用业务异常
raise ResourceNotFoundException("简历不存在")

# 不要捕获所有异常后静默处理
try:
    result = await some_operation()
except SpecificException as e:
    logger.warning("操作失败: %s", e)
    raise BusinessException(50001, "操作失败")
```

#### 日志规范

```python
import logging

logger = logging.getLogger(__name__)

# 使用结构化日志
logger.info("用户 %s 上传了简历 %s", user_id, resume_id)
logger.warning("Provider %s 调用失败: %s", provider.name, e)
logger.error("数据库连接失败: %s", e)
```

### 1.2 TypeScript/React 前端规范

#### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件 | 大驼峰 | `ResumeUploader` |
| Hooks | 小驼峰，前缀 `use` | `useAuthStore` |
| 工具函数 | 小驼峰 | `formatDate` |
| 类型/接口 | 大驼峰 | `UserProfile` |
| 常量 | 全大写 | `MAX_RETRY_COUNT = 3` |

#### 组件结构

```tsx
// 1. 导入
import React from 'react'
import { useAuthStore } from '@/stores/authStore'

// 2. 类型定义
interface Props {
  userId: string
  onUpdate?: () => void
}

// 3. 组件定义
export const UserCard: React.FC<Props> = ({ userId, onUpdate }) => {
  // 4. Hooks
  const { user } = useAuthStore()

  // 5. 渲染
  return (
    <div className="p-4 rounded-lg border">
      <h3 className="text-lg font-bold">{user?.name}</h3>
    </div>
  )
}
```

#### 状态管理

```typescript
// 使用 Zustand 进行状态管理
import { create } from 'zustand'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  setUser: (user: User | null) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
}))
```

## 2. API 设计规范

### 2.1 RESTful API 规范

```
GET    /api/v1/resources          # 列表查询
GET    /api/v1/resources/:id      # 详情查询
POST   /api/v1/resources          # 创建资源
PUT    /api/v1/resources/:id      # 全量更新
PATCH  /api/v1/resources/:id      # 部分更新（可选）
DELETE /api/v1/resources/:id      # 删除资源
POST   /api/v1/resources/:id/action  # 自定义操作
```

### 2.2 响应格式

```json
// 成功响应（200 OK）
{
  "id": "uuid",
  "name": "资源名称"
}

// 错误响应
{
  "error_code": 40401,
  "detail": "资源不存在"
}
```

### 2.3 错误码规范

| 错误码 | 含义 | HTTP状态码 |
|--------|------|-----------|
| 40001 | 参数校验错误 | 400 |
| 40101 | 认证失败 | 401 |
| 40102 | Token过期 | 401 |
| 40301 | 权限不足 | 403 |
| 40401 | 资源不存在 | 404 |
| 40901 | 资源冲突 | 409 |
| 42901 | 请求过于频繁 | 429 |
| 50001 | 服务器内部错误 | 500 |

## 3. Git 工作流

### 3.1 分支策略

```
main          - 生产环境分支，只允许合并
  │
  ├─ develop  - 开发分支，日常开发合并至此
  │    │
  │    ├─ feature/resume-upload    - 功能分支
  │    ├─ feature/llm-integration  - 功能分支
  │    └─ bugfix/login-error       - 修复分支
  │
  └─ hotfix/security-patch         - 紧急修复分支
```

### 3.2 提交规范

使用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型说明：

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复bug |
| docs | 文档更新 |
| style | 代码格式调整（不影响功能）|
| refactor | 重构 |
| test | 测试相关 |
| chore | 构建/工具链更新 |

示例：

```
feat(interview): 实现动态题库生成

- 根据简历+JD内容使用LLM生成个性化首题
- 添加Redis会话上下文缓存
- 失败时回退到固定题库

fix #123
```

## 4. 测试规范

### 4.1 后端测试

```python
# 测试文件命名: test_<module>.py
# 测试类命名: Test<ModuleName>
# 测试方法命名: test_<scenario>_<expected_result>

class TestResumeUpload:
    """简历上传测试。"""

    async def test_upload_valid_pdf_should_succeed(self):
        """上传合法PDF应成功。"""
        ...

    async def test_upload_exe_file_should_reject(self):
        """上传可执行文件应被拒绝。"""
        ...
```

### 4.2 前端测试

```typescript
// 组件测试
describe('LoadingSpinner', () => {
  it('应该渲染加载文本', () => {
    render(<LoadingSpinner text="加载中..." />)
    expect(screen.getByText('加载中...')).toBeInTheDocument()
  })
})
```

### 4.3 测试覆盖率要求

| 层级 | 目标覆盖率 | 说明 |
|------|----------|------|
| 单元测试 | ≥ 80% | 核心业务逻辑 |
| 集成测试 | ≥ 60% | 模块间交互 |
| E2E测试 | 关键流程 | 用户核心场景 |

## 5. 文档规范

### 5.1 代码注释

```python
# 函数文档字符串（Google风格）
def calculate_match_score(resume: dict, jd: dict) -> float:
    """计算简历与岗位的匹配度。

    Args:
        resume: 简历解析后的结构化数据
        jd: 岗位描述文本

    Returns:
        0-100的匹配度分数

    Raises:
        ValidationException: 当输入数据格式不正确时
    """
    ...
```

### 5.2 API 文档

使用 FastAPI 自动生成的 OpenAPI 文档，配合 docstring 说明：

```python
@router.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_resume(request: DiagnosisRequest):
    """诊断简历与目标岗位的匹配度。

    分析维度：
    - 简历结构完整性
    - 内容充实度
    - 关键词覆盖度
    - 量化数据使用
    - ATS兼容性

    结果会缓存2小时，相同简历+JD直接返回缓存结果。
    """
    ...
```

## 6. 性能规范

### 6.1 API 响应时间目标

| 接口类型 | 目标响应时间 | 说明 |
|---------|-------------|------|
| 普通查询 | < 200ms | 直接数据库查询 |
| 缓存查询 | < 50ms | Redis缓存命中 |
| 文件上传 | < 3s | 包含解析过程 |
| LLM调用 | < 5s | 同步调用，流式除外 |
| 流式响应 | < 1s首字节 | SSE首字节延迟 |

### 6.2 数据库查询优化

- 使用 select() 明确指定查询字段
- 复杂查询添加适当索引
- N+1查询使用 joinedload 或 selectinload
- 分页查询使用 limit/offset

## 7. 安全规范

### 7.1 敏感数据处理

- 密码：必须使用 bcrypt 哈希，禁止明文存储
- Token：设置合理的过期时间，使用 HTTPS 传输
- 日志：禁止记录密码、Token等敏感信息
- 配置：密钥等敏感配置使用环境变量

### 7.2 输入校验

- 所有用户输入都必须校验
- 文件上传使用白名单机制
- SQL查询使用参数化查询
- 输出进行适当的转义
