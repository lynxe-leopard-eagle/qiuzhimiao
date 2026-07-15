"""岗位模块 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel


class JobCreateRequest(BaseModel):
    title: str
    company: str | None = None
    description: str | None = None
    requirements: dict | None = None
    category: str | None = None


class JobResponse(BaseModel):
    id: str
    title: str
    company: str | None = None
    description: str | None = None
    requirements: dict | None = None
    category: str | None = None

    class Config:
        from_attributes = True


class JobAnalyzeRequest(BaseModel):
    job_description: str
    title: str | None = None
    company: str | None = None


class JobAnalyzeResponse(BaseModel):
    title: str = ""
    company: str = ""
    job_level: str = ""
    experience_required: str = ""
    education_required: str = ""
    salary_range: str = ""
    core_skills: list[str] = []
    bonus_skills: list[str] = []
    responsibilities: list[str] = []
    hard_requirements: list[str] = []
    difficulty_score: int = 0
    market_demand: str = ""
    career_outlook: str = ""
    summary: str = ""


class MatchingRequest(BaseModel):
    resume_id: str
    job_id: str | None = None
    job_description: str | None = None


class MatchReasons(BaseModel):
    why_match: str = ""
    advantages: list[str] = []
    gaps: list[str] = []


class MatchingResponse(BaseModel):
    resume_id: str
    job_id: str | None = None
    match_score: float = 0.0
    dimensions: dict[str, float] = {}
    strengths: list[str] = []
    weaknesses: list[str] = []
    gaps: list[str] = []
    suggestion: str = ""
    match_reasons: MatchReasons | None = None
