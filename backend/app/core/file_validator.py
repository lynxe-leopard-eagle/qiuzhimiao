"""文件上传校验。"""

from __future__ import annotations

import filetype
from dataclasses import dataclass


# 上传文件白名单
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}

MAX_FILENAME_LENGTH = 256


@dataclass
class ValidationResult:
    is_valid: bool
    detected_mime: str = ""
    error: str = ""


def validate_upload_file(filename: str, content_type: str, file_size: int) -> None:
    """校验上传文件的基本信息，失败时抛出 ValueError。"""
    from app.core.config import settings

    # a. 文件扩展名白名单校验
    if "." not in filename:
        raise ValueError("文件名缺少扩展名")
    ext = filename.rsplit(".", 1)[-1].lower()
    ext_with_dot = f".{ext}"
    if ext_with_dot not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件扩展名: {ext_with_dot}，允许: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # b. MIME 类型白名单校验
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"不支持的 MIME 类型: {content_type}，允许: {', '.join(sorted(ALLOWED_MIME_TYPES))}")

    # c. 文件大小校验
    if file_size > settings.UPLOAD_MAX_SIZE:
        max_mb = settings.UPLOAD_MAX_SIZE // (1024 * 1024)
        raise ValueError(f"文件大小超过限制（最大 {max_mb}MB）")

    # d. 文件名长度校验
    if len(filename) > MAX_FILENAME_LENGTH:
        raise ValueError(f"文件名长度超过限制（最大 {MAX_FILENAME_LENGTH} 字符）")

    # e. 路径遍历字符校验
    if "../" in filename or "\\" in filename:
        raise ValueError("文件名包含非法路径遍历字符")


class FileValidator:
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "image/png",
        "image/jpeg",
    }
    MAX_SIZE = 10 * 1024 * 1024

    @classmethod
    def validate(cls, file_bytes: bytes, declared_filename: str, declared_content_type: str) -> ValidationResult:
        if len(file_bytes) > cls.MAX_SIZE:
            return ValidationResult(is_valid=False, error="文件大小超过 10MB 限制")

        kind = filetype.guess(file_bytes)
        if kind is None:
            if declared_filename.endswith(".txt"):
                return ValidationResult(is_valid=True, detected_mime="text/plain")
            return ValidationResult(is_valid=False, error="无法识别文件类型")

        if kind.mime not in cls.ALLOWED_MIME_TYPES:
            return ValidationResult(is_valid=False, error=f"不支持的文件类型: {kind.mime}")

        return ValidationResult(is_valid=True, detected_mime=kind.mime)
