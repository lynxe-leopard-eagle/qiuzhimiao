"""Redis 缓存工具模块。

提供基于Redis的缓存装饰器和工具函数，用于：
- 缓存频繁访问的数据（简历诊断结果、岗位分析结果）
- 缓存面试会话上下文
- 实现分布式锁
- API限流计数
"""

from __future__ import annotations

import functools
import hashlib
import json
import logging
from typing import Any, Callable

from app.core.redis import get_redis

logger = logging.getLogger(__name__)


async def get_cache(key: str) -> Any | None:
    """从Redis获取缓存值。"""
    try:
        redis = await get_redis()
        data = await redis.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning("Redis缓存读取失败: %s", e)
    return None


async def set_cache(key: str, value: Any, ttl: int = 3600) -> None:
    """写入Redis缓存，默认TTL=1小时。"""
    try:
        redis = await get_redis()
        await redis.setex(key, ttl, json.dumps(value, ensure_ascii=False, default=str))
    except Exception as e:
        logger.warning("Redis缓存写入失败: %s", e)


async def delete_cache(key: str) -> None:
    """删除Redis缓存。"""
    try:
        redis = await get_redis()
        await redis.delete(key)
    except Exception as e:
        logger.warning("Redis缓存删除失败: %s", e)


async def delete_cache_pattern(pattern: str) -> None:
    """按模式删除Redis缓存。"""
    try:
        redis = await get_redis()
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
    except Exception as e:
        logger.warning("Redis缓存批量删除失败: %s", e)


def cache_result(prefix: str, ttl: int = 3600, key_func: Callable | None = None):
    """Redis缓存装饰器。

    使用示例:
        @cache_result("diag", ttl=7200)
        async def diagnose_resume(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存key
            if key_func:
                cache_key = f"{prefix}:{key_func(*args, **kwargs)}"
            else:
                # 基于函数名和参数生成key
                key_parts = [prefix, func.__name__]
                for arg in args:
                    key_parts.append(str(arg))
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}={v}")
                raw_key = "|".join(key_parts)
                cache_key = f"{prefix}:{hashlib.md5(raw_key.encode()).hexdigest()}"

            # 尝试读取缓存
            cached = await get_cache(cache_key)
            if cached is not None:
                logger.debug("缓存命中: %s", cache_key)
                return cached

            # 执行原函数
            result = await func(*args, **kwargs)

            # 写入缓存
            await set_cache(cache_key, result, ttl)
            return result

        return wrapper
    return decorator


async def acquire_lock(lock_key: str, ttl: int = 30) -> bool:
    """获取分布式锁。

    Args:
        lock_key: 锁的唯一标识
        ttl: 锁的过期时间（秒）

    Returns:
        是否成功获取锁
    """
    try:
        redis = await get_redis()
        acquired = await redis.set(lock_key, "1", nx=True, ex=ttl)
        return acquired is not None
    except Exception as e:
        logger.warning("分布式锁获取失败: %s", e)
        return False


async def release_lock(lock_key: str) -> None:
    """释放分布式锁。"""
    try:
        redis = await get_redis()
        await redis.delete(lock_key)
    except Exception as e:
        logger.warning("分布式锁释放失败: %s", e)


async def rate_limit_check(
    identifier: str,
    limit: int = 60,
    window: int = 60,
) -> tuple[bool, int, int]:
    """滑动窗口限流检查。

    Args:
        identifier: 限流标识（如IP地址或用户ID）
        limit: 窗口期内允许的最大请求数
        window: 窗口大小（秒）

    Returns:
        (是否允许, 当前计数, 剩余额度)
    """
    try:
        redis = await get_redis()
        key = f"rate:{identifier}"
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        current = results[0]
        remaining = max(0, limit - current)
        return current <= limit, current, remaining
    except Exception as e:
        logger.warning("限流检查失败: %s", e)
        # 限流服务故障时放行
        return True, 0, limit
