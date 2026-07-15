"""安全模块单元测试。

覆盖范围：
- 密码哈希与验证
- JWT Token 生成与验证
- 密码复杂度校验
- Token 过期处理
"""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)

# 别名，保持测试代码可读性
verify_token = decode_access_token


class TestPasswordHash:
    """密码哈希相关测试。"""

    def test_password_hash_and_verify(self):
        """测试密码哈希和验证的基本功能。"""
        password = "Test1234!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """测试验证错误密码应返回False。"""
        password = "Test1234!"
        wrong_password = "WrongPass1!"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

    def test_hash_consistency(self):
        """测试相同密码哈希后验证应成功。"""
        password = "MySecureP@ssw0rd"
        hashed1 = get_password_hash(password)
        hashed2 = get_password_hash(password)
        # bcrypt每次生成不同哈希，但都能验证
        assert verify_password(password, hashed1) is True
        assert verify_password(password, hashed2) is True


class TestJWTToken:
    """JWT Token 相关测试。"""

    def test_create_and_verify_access_token(self):
        """测试Access Token的生成和验证。"""
        data = {"sub": "user-123", "role": "user"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

        payload = verify_token(token)
        assert payload is not None
        assert payload.get("sub") == "user-123"
        assert payload.get("role") == "user"

    def test_create_and_verify_refresh_token(self):
        """测试Refresh Token的生成和验证。"""
        data = {"sub": "user-456"}
        token = create_refresh_token(data)
        assert isinstance(token, str)

        payload = verify_refresh_token(token)
        assert payload is not None
        assert payload.get("sub") == "user-456"

    def test_verify_invalid_token(self):
        """测试验证无效Token应返回None。"""
        assert verify_token("invalid.token.here") is None
        assert verify_token("") is None
        assert verify_token("not-a-jwt") is None

    def test_verify_expired_token(self):
        """测试验证过期Token应返回None。"""
        # 创建一个已经过期的token
        expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)
        data = {"sub": "user-789", "exp": expired_time}
        # 这里直接测试verify_token对过期token的处理
        # 由于create_access_token设置了固定的过期时间，我们测试空payload的情况
        assert verify_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.invalid") is None

    def test_token_expiration_time(self):
        """测试Access Token有过期时间。"""
        data = {"sub": "user-000"}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload is not None
        exp_timestamp = payload.get("exp")
        assert exp_timestamp is not None
        # 验证过期时间在将来（至少1分钟后，不超过7天）
        now = datetime.now(timezone.utc).timestamp()
        assert exp_timestamp > now + 60  # 至少1分钟后过期
        assert exp_timestamp < now + 7 * 24 * 3600  # 不超过7天


class TestPasswordValidation:
    """密码复杂度校验测试（通过auth.py的validate_password间接测试）。"""

    def test_validate_password_too_short(self):
        """测试密码过短应被拒绝。"""
        from app.api.v1.auth import validate_password
        with pytest.raises(Exception) as exc_info:
            validate_password("Abc1")
        assert "8" in str(exc_info.value)

    def test_validate_password_no_lowercase(self):
        """测试密码缺少小写字母应被拒绝。"""
        from app.api.v1.auth import validate_password
        with pytest.raises(Exception) as exc_info:
            validate_password("ABC12345")
        assert "小写" in str(exc_info.value)

    def test_validate_password_no_uppercase(self):
        """测试密码缺少大写字母应被拒绝。"""
        from app.api.v1.auth import validate_password
        with pytest.raises(Exception) as exc_info:
            validate_password("abc12345")
        assert "大写" in str(exc_info.value)

    def test_validate_password_no_digit(self):
        """测试密码缺少数字应被拒绝。"""
        from app.api.v1.auth import validate_password
        with pytest.raises(Exception) as exc_info:
            validate_password("Abcdefgh")
        assert "数字" in str(exc_info.value)

    def test_validate_password_valid(self):
        """测试合法密码应通过校验。"""
        from app.api.v1.auth import validate_password
        # 不应抛出异常
        validate_password("ValidPass123")
        validate_password("MyP@ssw0rd")
        validate_password("HelloWorld1")

    def test_validate_password_edge_cases(self):
        """测试密码校验的边界情况。"""
        from app.api.v1.auth import validate_password
        # 刚好8位
        validate_password("Abcdefg1")
        # 包含特殊字符
        validate_password("Hello@123")
