"""用户模块 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    email: str
    password: str
    nickname: str | None = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    nickname: str | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
