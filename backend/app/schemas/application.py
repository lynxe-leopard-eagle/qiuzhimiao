"""投递追踪模块数据模型定义。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ApplicationCreateRequest(BaseModel):
    job_id: str | None = None
    company: str = Field(..., min_length=1, description="公司名称")
    position: str = Field(..., min_length=1, description="岗位名称")
    stage: str = Field("applied", description="投递阶段")
    city: str | None = None
    salary_range: str | None = None
    notes: str | None = None
    contact_info: str | None = None


class ApplicationUpdateRequest(BaseModel):
    stage: str | None = None
    salary_range: str | None = None
    notes: str | None = None
    contact_info: str | None = None
    feedback: str | None = None


class ApplicationResponse(BaseModel):
    id: str
    company: str
    position: str
    stage: str
    city: str | None
    salary_range: str | None
    notes: str | None
    contact_info: str | None
    feedback: str | None
    created_at: str
    updated_at: str


class ApplicationStageStats(BaseModel):
    stage: str
    label: str
    count: int
