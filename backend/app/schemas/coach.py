"""AI教练模块 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel


class CoachTool(BaseModel):
    name: str
    description: str
    parameters: list[dict] = []


class CoachToolResult(BaseModel):
    tool: str
    success: bool
    data: dict = {}
    error: str = ""
    needs_user_input: bool = False


class CoachMessage(BaseModel):
    role: str = "user"
    content: str = ""
    tool_result: CoachToolResult | None = None


class CoachChatRequest(BaseModel):
    message: str = ""
    messages: list[CoachMessage] = []
    job_description: str = ""


class CoachChatResponse(BaseModel):
    response: str = ""
    needs_user_input: bool = False


class CoachReportResponse(BaseModel):
    status: str = ""
    resume_count: int = 0
    interview_count: int = 0
    application_count: int = 0
    avg_interview_score: float = 0.0
    stage_stats: dict[str, int] = {}
    recent_resumes: list[dict] = []
    recent_applications: list[dict] = []
    recent_interviews: list[dict] = []
    recommendations: list[str] = []
