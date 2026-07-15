"""技能图谱模块 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel


class SkillDimension(BaseModel):
    name: str
    score: int
    max_score: int = 100
    description: str = ""
    keywords: list[str] = []


class SkillRadarResponse(BaseModel):
    dimensions: list[SkillDimension] = []
    job_fit_score: float = 0.0
    suggested_skills: list[str] = []
    improvement_path: list[str] = []


class SkillCategory(BaseModel):
    name: str
    skills: list[str] = []


class SkillTreeResponse(BaseModel):
    categories: list[SkillCategory] = []


class SkillGapAnalysis(BaseModel):
    required_skills: list[str] = []
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    gap_description: str = ""
    learning_suggestions: list[str] = []


class SkillGapRequest(BaseModel):
    resume_id: str
    job_description: str
