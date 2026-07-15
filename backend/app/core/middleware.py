"""FastAPI 中间件集合。

包含：
- 请求日志中间件
- API限流中间件（基于Redis滑动窗口）
- 请求ID追踪中间件
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import RateLimitException
from app.core.redis_cache import rate_limit_check

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件：记录每个请求的耗时和状态码。"""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(
            "%s %s - %s - %.3fs",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """API限流中间件：对敏感接口进行滑动窗口限流。

    限流规则（可按路径自定义）：
    - /interviews/start: 每用户 5次/分钟
    - /interviews/answer: 每用户 30次/分钟
    - /resumes/diagnose: 每用户 10次/小时
    - /jobs/analyze: 每用户 20次/小时
    - /jobs/matching: 每用户 20次/小时
    """

    # 路径 -> (每分钟限制数, 窗口秒数)
    _RULES = {
        "/api/v1/interviews/start": (5, 60),
        "/api/v1/interviews/answer": (30, 60),
        "/api/v1/resumes/diagnose": (10, 3600),
        "/api/v1/jobs/analyze": (20, 3600),
        "/api/v1/jobs/matching": (20, 3600),
    }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        rule = None
        for prefix, limit_config in self._RULES.items():
            if path.startswith(prefix):
                rule = limit_config
                break

        if rule:
            limit, window = rule
            # 优先使用用户ID作为限流标识，未登录时使用IP
            user_id = None
            try:
                auth = request.headers.get("Authorization", "")
                if auth.startswith("Bearer "):
                    token = auth[7:]
                    from app.core.security import verify_token
                    payload = verify_token(token)
                    if payload:
                        user_id = payload.get("sub")
            except Exception:
                pass

            identifier = user_id or request.client.host if request.client else "unknown"
            key = f"{identifier}:{path}"

            allowed, current, remaining = await rate_limit_check(key, limit=limit, window=window)
            if not allowed:
                raise RateLimitException(
                    f"请求过于频繁，该接口限制 {limit} 次/{window}秒，请稍后重试"
                )

            response = await call_next(request)
            # 在响应头中附加限流信息
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            return response

        return await call_next(request)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求ID追踪中间件：为每个请求生成唯一ID，便于日志追踪。"""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
