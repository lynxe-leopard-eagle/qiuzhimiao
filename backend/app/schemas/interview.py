"""面试模块 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class InterviewStartRequest(BaseModel):
    resume_id: str | None = None
    job_id: str | None = None
    round: str = "tech1"
    interviewer_style: str = "professional"


class InterviewStartResponse(BaseModel):
    interview_id: str
    round: str
    first_question: str


class InterviewAnswerRequest(BaseModel):
    interview_id: str
    answer: str


class InterviewMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    professional: int = 0
    logic: int = 0
    communication: int = 0
    project: int = 0
    match: int = 0
    learning: int | None = None
    stress_resistance: int | None = None
    decomposition: int | None = None
    engineering_quality: int | None = None
    innovation: int | None = None
    overall: int = 0
    confidence: float = 0.0
    feedback: str = ""
    should_follow_up: bool = False
    follow_up_question: str | None = None


class InterviewEndResponse(BaseModel):
    interview_id: str
    status: str
    review_id: str | None = None
