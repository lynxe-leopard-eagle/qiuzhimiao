"""数据库类型兼容模块。根据数据库类型选择合适的字段类型。"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import TypeDecorator, JSON as JSONType

from app.core.config import settings


def get_uuid_column_type():
    """根据数据库类型返回 UUID 列类型。"""
    if settings.DATABASE_URL.startswith("sqlite"):
        return SQLiteUUID()
    return postgresql.UUID(as_uuid=True)


def get_json_column_type():
    """根据数据库类型返回 JSON 列类型。"""
    if settings.DATABASE_URL.startswith("sqlite"):
        return JSONType
    return postgresql.JSONB


class SQLiteUUID(TypeDecorator):
    """SQLite UUID 兼容类型。"""
    
    impl = String(36)
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)
    
    def process_result_value(self, value, dialect):
        import uuid
        if value is None:
            return None
        return uuid.UUID(value)
