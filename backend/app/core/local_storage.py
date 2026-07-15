"""本地文件存储（SQLite 模式的降级方案）。"""

from __future__ import annotations

import os
from pathlib import Path

from app.core.config import settings

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def upload_file(object_name: str, data: bytes, content_type: str) -> None:
    """上传文件到本地目录。"""
    filepath = UPLOAD_DIR / object_name
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_bytes(data)


async def get_presigned_url(object_name: str, expires: int = 3600) -> str:
    """返回本地文件路径（测试模式）。"""
    filepath = UPLOAD_DIR / object_name
    if filepath.exists():
        return f"/uploads/{object_name}"
    return ""


def get_file_path(object_name: str) -> str:
    """获取本地文件完整路径。"""
    return str(UPLOAD_DIR / object_name)
