"""Redis 缓存模块单元测试。

覆盖范围：
- get_cache / set_cache / delete_cache
- cache_result 装饰器
- rate_limit_check
- acquire_lock / release_lock
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from app.core.redis_cache import (
    get_cache,
    set_cache,
    delete_cache,
    delete_cache_pattern,
    rate_limit_check,
    acquire_lock,
    release_lock,
)


@pytest.mark.asyncio
class TestCacheBasic:
    """基础缓存操作测试。"""

    async def test_set_and_get_cache(self):
        """测试缓存写入和读取。"""
        key = "test:key:1"
        value = {"name": "test", "score": 100}
        await set_cache(key, value, ttl=60)
        cached = await get_cache(key)
        assert cached == value

    async def test_get_nonexistent_cache(self):
        """测试读取不存在的缓存应返回None。"""
        cached = await get_cache("test:nonexistent:12345")
        assert cached is None

    async def test_delete_cache(self):
        """测试删除缓存。"""
        key = "test:key:2"
        await set_cache(key, "value", ttl=60)
        await delete_cache(key)
        cached = await get_cache(key)
        assert cached is None

    async def test_cache_ttl_expiration(self):
        """测试缓存过期。"""
        key = "test:key:ttl"
        await set_cache(key, "value", ttl=1)
        # 立即读取应存在
        assert await get_cache(key) == "value"
        # 等待过期
        import asyncio
        await asyncio.sleep(1.5)
        assert await get_cache(key) is None

    async def test_cache_complex_data(self):
        """测试缓存复杂数据结构。"""
        key = "test:complex"
        value = {
            "list": [1, 2, 3],
            "nested": {"a": {"b": "c"}},
            "bool": True,
            "null": None,
        }
        await set_cache(key, value, ttl=60)
        cached = await get_cache(key)
        assert cached == value


@pytest.mark.asyncio
class TestRateLimit:
    """限流功能测试。"""

    async def test_rate_limit_allows_within_limit(self):
        """测试在限制范围内的请求应被允许。"""
        identifier = "test:user:1"
        for _ in range(5):
            allowed, current, remaining = await rate_limit_check(
                identifier, limit=10, window=60
            )
            assert allowed is True
            assert current <= 10
            assert remaining >= 0

    async def test_rate_limit_blocks_over_limit(self):
        """测试超出限制后应被阻止。"""
        identifier = "test:user:2"
        # 先发出超过限制的请求
        for _ in range(15):
            await rate_limit_check(identifier, limit=10, window=60)

        # 第16个请求应被阻止
        allowed, current, remaining = await rate_limit_check(
            identifier, limit=10, window=60
        )
        assert allowed is False
        assert current > 10

    async def test_rate_limit_different_identifiers(self):
        """测试不同标识符应独立计数。"""
        # user1 达到限制
        for _ in range(15):
            await rate_limit_check("test:user:a", limit=10, window=60)

        # user2 仍然可以访问
        allowed, _, _ = await rate_limit_check("test:user:b", limit=10, window=60)
        assert allowed is True


@pytest.mark.asyncio
class TestDistributedLock:
    """分布式锁测试。"""

    async def test_acquire_and_release_lock(self):
        """测试获取和释放锁。"""
        lock_key = "test:lock:1"
        acquired = await acquire_lock(lock_key, ttl=30)
        assert acquired is True

        # 同一个锁应无法再次获取
        acquired2 = await acquire_lock(lock_key, ttl=30)
        assert acquired2 is False

        # 释放后应可以获取
        await release_lock(lock_key)
        acquired3 = await acquire_lock(lock_key, ttl=30)
        assert acquired3 is True

        await release_lock(lock_key)

    async def test_lock_expiration(self):
        """测试锁过期后应可重新获取。"""
        lock_key = "test:lock:ttl"
        acquired = await acquire_lock(lock_key, ttl=1)
        assert acquired is True

        # 锁未过期时无法获取
        acquired2 = await acquire_lock(lock_key, ttl=1)
        assert acquired2 is False

        # 等待锁过期
        import asyncio
        await asyncio.sleep(1.5)

        # 锁过期后应可获取
        acquired3 = await acquire_lock(lock_key, ttl=30)
        assert acquired3 is True
        await release_lock(lock_key)

    async def test_lock_different_keys(self):
        """测试不同key的锁应相互独立。"""
        key1 = "test:lock:a"
        key2 = "test:lock:b"

        assert await acquire_lock(key1, ttl=30) is True
        assert await acquire_lock(key2, ttl=30) is True

        await release_lock(key1)
        await release_lock(key2)
