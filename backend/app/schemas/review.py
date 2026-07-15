"""复盘模块 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class QuestionReview(BaseModel):
    question: str = ""
    answer_summary: str = ""
    score: int = 0
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


class SuggestionItem(BaseModel):
    priority: str = "medium"
    dimension: str = ""
    action: str = ""


class ReviewResponse(BaseModel):
    id: str
    interview_id: str
    overall_score: int = 0
    radar_data: dict[str, int] = Field(default_factory=dict)
    question_reviews: list[QuestionReview] = Field(default_factory=list)
    interviewer_summary: str = ""
    suggestions: list[SuggestionItem] = Field(default_factory=list)
    created_at: str = ""

    class Config:
        from_attributes = True


class ReviewListItem(BaseModel):
    id: str
    interview_id: str
    overall_score: int
    created_at: str

    class Config:
        from_attributes = True
