"""简历模块 SQLAlchemy ORM 模型。"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.db_types import get_uuid_column_type, get_json_column_type


class ResumeStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(get_uuid_column_type(), primary_key=True, default=uuid.uuid4)
    user_id = Column(get_uuid_column_type(), ForeignKey("users.id"), nullable=False, index=True)
    original_filename = Column(String(256), nullable=False)
    minio_key = Column(String(512), nullable=False)
    mime_type = Column(String(64), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default=ResumeStatus.PENDING, index=True)
    parsed_data = Column(get_json_column_type(), nullable=True)
    raw_text_hash = Column(String(64), nullable=True)
    parse_method = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="resumes")
    interviews = relationship("Interview", back_populates="resume")
