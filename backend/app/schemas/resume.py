"""简历模块 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ParsedResume(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    education: list[dict] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    work_experience: list[dict] = Field(default_factory=list)
    raw_text: str = ""
    parse_method: str = ""
    confidence: float = 0.0


class ResumeUploadResponse(BaseModel):
    id: str
    original_filename: str
    status: str = "pending"
    message: str = ""
    parse_method: str | None = None
    confidence: float | None = None
    extracted_name: str | None = None
    extracted_phone: str | None = None
    extracted_email: str | None = None
    education_summary: str | None = None
    skills_summary: list[str] | None = None


class DiagnosisRequest(BaseModel):
    resume_id: str
    job_id: str | None = None
    job_description: str | None = None


class ATSAnalysis(BaseModel):
    """ATS 兼容性分析结果。"""
    overall_score: float = 0.0
    keyword_coverage: float = 0.0
    format_issues: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    detected_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class DiagnosisResponse(BaseModel):
    resume_id: str
    match_score: float = 0.0
    radar_scores: dict[str, float] = Field(default_factory=dict)
    analysis: str = ""
    skill_gap: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    ats_analysis: ATSAnalysis | None = None


class ParseStatus(BaseModel):
    status: str
    parse_method: str | None = None
    confidence: float | None = None
    error_message: str | None = None
