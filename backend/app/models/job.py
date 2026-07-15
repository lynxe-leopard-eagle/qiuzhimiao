"""岗位模块 SQLAlchemy ORM 模型。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.db_types import get_uuid_column_type, get_json_column_type


class Job(Base):
    __tablename__ = "jobs"

    id = Column(get_uuid_column_type(), primary_key=True, default=uuid.uuid4)
    user_id = Column(get_uuid_column_type(), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    requirements = Column(get_json_column_type(), nullable=True)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    interviews = relationship("Interview", back_populates="job")
