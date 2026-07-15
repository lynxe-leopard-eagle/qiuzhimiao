"""投递追踪模块 SQLAlchemy ORM 模型。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.db_types import get_uuid_column_type, get_json_column_type


class Application(Base):
    __tablename__ = "applications"

    id = Column(get_uuid_column_type(), primary_key=True, default=uuid.uuid4)
    user_id = Column(get_uuid_column_type(), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(get_uuid_column_type(), ForeignKey("jobs.id"), nullable=True)
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    stage = Column(String(50), nullable=False, default="applied")
    city = Column(String(100), nullable=True)
    salary_range = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    contact_info = Column(String(255), nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="applications")
