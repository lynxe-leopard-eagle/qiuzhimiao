"""成长追踪模块 SQLAlchemy ORM 模型。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.db_types import get_uuid_column_type


class GrowthRecord(Base):
    __tablename__ = "growth_records"

    id = Column(get_uuid_column_type(), primary_key=True, default=uuid.uuid4)
    user_id = Column(get_uuid_column_type(), ForeignKey("users.id"), nullable=False, index=True)
    interview_id = Column(get_uuid_column_type(), ForeignKey("interviews.id"), nullable=True, index=True)
    dimension = Column(String(20), nullable=False)
    score = Column(Integer, nullable=False)
    record_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="growth_records")

