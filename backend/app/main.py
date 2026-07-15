"""FastAPI 应用入口。"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BusinessException,
    RateLimitException,
    ResourceNotFoundException,
    ValidationException,
)

from app.models import *  # noqa: F401,F403 确保所有模型已注册

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("求职喵服务启动中...")
    try:
        from app.core.database import engine, Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表已就绪")
    except Exception as e:
        logger.warning("数据库初始化失败: %s", e)
    try:
        from app.core.seed import seed_all
        await seed_all()
    except Exception as e:
        logger.warning("种子数据初始化失败: %s", e)
    yield
    logger.info("求职喵服务已关闭")


app = FastAPI(
    title="求职喵 API",
    description="AI 面试教练后端服务",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册自定义中间件
from app.core.middleware import RequestIDMiddleware, RateLimitMiddleware, RequestLoggingMiddleware

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("未处理的异常: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "服务器内部错误"},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "detail": exc.message},
    )


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok", "service": "qiuzhimiao-api"}


from app.api.v1.auth import router as auth_router
from app.api.v1.resume import router as resume_router
from app.api.v1.job import router as job_router
from app.api.v1.interview import router as interview_router
from app.api.v1.review import router as review_router
from app.api.v1.growth import router as growth_router
from app.api.v1.application import router as application_router
from app.api.v1.skill import router as skill_router
from app.api.v1.coach import router as coach_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(resume_router, prefix="/api/v1")
app.include_router(job_router, prefix="/api/v1")
app.include_router(interview_router, prefix="/api/v1")
app.include_router(review_router, prefix="/api/v1")
app.include_router(growth_router, prefix="/api/v1")
app.include_router(application_router, prefix="/api/v1")
app.include_router(skill_router, prefix="/api/v1")
app.include_router(coach_router, prefix="/api/v1")
