"""统一业务异常定义。"""

from __future__ import annotations


class BusinessException(Exception):
    """业务异常基类。"""

    def __init__(self, error_code: int, message: str, status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundException(BusinessException):
    """资源未找到异常。"""

    def __init__(self, message: str = "资源未找到"):
        super().__init__(error_code=40401, message=message, status_code=404)


class ValidationException(BusinessException):
    """数据校验异常。"""

    def __init__(self, message: str = "数据校验失败"):
        super().__init__(error_code=40001, message=message, status_code=400)


class AuthenticationException(BusinessException):
    """认证异常。"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(error_code=40101, message=message, status_code=401)


class AuthorizationException(BusinessException):
    """授权异常。"""

    def __init__(self, message: str = "无权访问"):
        super().__init__(error_code=40301, message=message, status_code=403)


class RateLimitException(BusinessException):
    """限流异常。"""

    def __init__(self, message: str = "请求过于频繁"):
        super().__init__(error_code=42901, message=message, status_code=429)
