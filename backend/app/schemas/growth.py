"""成长追踪模块 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel


class GrowthRadarResponse(BaseModel):
    dimensions: list[str] = []
    latest_scores: list[int] = []
    previous_scores: list[int] = []


class GrowthTrendPoint(BaseModel):
    date: str
    score: int


class GrowthTrendResponse(BaseModel):
    dimension: str
    data: list[GrowthTrendPoint] = []


class GrowthTrendAllResponse(BaseModel):
    trends: list[GrowthTrendResponse] = []
