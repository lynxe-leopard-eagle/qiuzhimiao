"""对象存储客户端（支持 MinIO 和本地文件存储）。"""

from __future__ import annotations

import os

from app.core.config import settings

_storage_backend: str = "local"


def _is_minio_available() -> bool:
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        host, port = settings.MINIO_ENDPOINT.split(":")
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return result == 0
    except Exception:
        return False


try:
    from minio import Minio
    _minio_client: Minio | None = None

    def get_minio_client() -> Minio:
        global _minio_client
        if _minio_client is None:
            _minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        return _minio_client

    async def _minio_upload_file(object_name: str, data: bytes, content_type: str) -> None:
        client = get_minio_client()
        if not client.bucket_exists(settings.MINIO_BUCKET):
            client.make_bucket(settings.MINIO_BUCKET)
        from io import BytesIO
        client.put_object(
            settings.MINIO_BUCKET,
            object_name,
            BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    async def _minio_get_presigned_url(object_name: str, expires: int = 3600) -> str:
        client = get_minio_client()
        return client.presigned_get_object(settings.MINIO_BUCKET, object_name, expires=expires)

    if _is_minio_available():
        _storage_backend = "minio"
    else:
        _storage_backend = "local"
except Exception:
    _storage_backend = "local"


if _storage_backend == "minio":
    upload_file = _minio_upload_file
    get_presigned_url = _minio_get_presigned_url
else:
    from app.core.local_storage import upload_file, get_presigned_url

__all__ = ["upload_file", "get_presigned_url"]
