"""面试模块 SQLAlchemy ORM 模型。"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.db_types import get_uuid_column_type, get_json_column_type


class InterviewRound(StrEnum):
    HR = "hr"
    TECH1 = "tech1"
    TECH2 = "tech2"


class InterviewStatus(StrEnum):
    ONGOING = "ongoing"
    ENDED = "ended"


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(get_uuid_column_type(), primary_key=True, default=uuid.uuid4)
    user_id = Column(get_uuid_column_type(), ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(get_uuid_column_type(), ForeignKey("resumes.id"), nullable=True, index=True)
    job_id = Column(get_uuid_column_type(), ForeignKey("jobs.id"), nullable=True, index=True)
    round = Column(String(10), nullable=False, default=InterviewRound.TECH1)
    status = Column(String(10), nullable=False, default=InterviewStatus.ONGOING)
    duration = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    messages = relationship("Message", back_populates="interview", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="interview", cascade="all, delete-orphan")
    review = relationship("Review", back_populates="interview", uselist=False, cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(get_uuid_column_type(), primary_key=True, default=uuid.uuid4)
    interview_id = Column(get_uuid_column_type(), ForeignKey("interviews.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    model_used = Column(String(50), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    interview = relationship("Interview", back_populates="messages")
    evaluations = relationship("Evaluation", back_populates="message", cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(get_uuid_column_type(), primary_key=True, default=uuid.uuid4)
    interview_id = Column(get_uuid_column_type(), ForeignKey("interviews.id"), nullable=False, index=True)
    message_id = Column(get_uuid_column_type(), ForeignKey("messages.id"), nullable=True, index=True)
    professional = Column(Integer, nullable=True)
    logic = Column(Integer, nullable=True)
    communication = Column(Integer, nullable=True)
    project = Column(Integer, nullable=True)
    match = Column(Integer, nullable=True)
    learning = Column(Integer, nullable=True, comment="学习能力 0-100，条件触发")
    stress_resistance = Column(Integer, nullable=True, comment="抗压表现 0-100，条件触发")
    decomposition = Column(Integer, nullable=True, comment="问题拆解 0-100，条件触发")
    engineering_quality = Column(Integer, nullable=True, comment="工程素养 0-100，条件触发")
    innovation = Column(Integer, nullable=True, comment="创新思维 0-100，条件触发")
    overall = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    should_follow_up = Column(String(10), nullable=True, default="false")
    follow_up_question = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    interview = relationship("Interview", back_populates="evaluations")
    message = relationship("Message", back_populates="evaluations")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(get_uuid_column_type(), primary_key=True, default=uuid.uuid4)
    interview_id = Column(get_uuid_column_type(), ForeignKey("interviews.id"), nullable=False, unique=True, index=True)
    overall_score = Column(Integer, nullable=True)
    radar_data = Column(get_json_column_type(), nullable=True)
    question_reviews = Column(get_json_column_type(), nullable=True)
    interviewer_summary = Column(Text, nullable=True)
    suggestions = Column(get_json_column_type(), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    interview = relationship("Interview", back_populates="review")

