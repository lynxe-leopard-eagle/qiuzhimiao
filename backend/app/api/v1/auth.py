"""用户认证 API 路由。"""

from __future__ import annotations

import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.core.database import get_db_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)
from app.models.user import User
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def validate_password(password: str) -> None:
    """校验密码复杂度：至少8位、包含大小写字母、包含数字。"""
    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码至少需要8位")
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码需要包含小写字母")
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码需要包含大写字母")
    if not re.search(r'\d', password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码需要包含数字")


@router.post("/register", response_model=TokenResponse)
async def register(request: UserRegisterRequest):
    validate_password(request.password)
    async with get_db_session() as session:
        result = await session.execute(select(User).where(User.email == request.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已注册")

        user = User(
            id=uuid.uuid4(),
            email=request.email,
            password_hash=get_password_hash(request.password),
            nickname=request.nickname,
        )
        session.add(user)
        await session.commit()

        token = create_access_token({"sub": str(user.id)})
        return TokenResponse(
            access_token=token,
            user=UserResponse(id=str(user.id), email=user.email, nickname=user.nickname),
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    async with get_db_session() as session:
        result = await session.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")

        token = create_access_token({"sub": str(user.id)})
        return TokenResponse(
            access_token=token,
            user=UserResponse(id=str(user.id), email=user.email, nickname=user.nickname),
        )


@router.get("/me", response_model=UserResponse)
async def me(current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(select(User).where(User.id == uuid.UUID(current_user)))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        return UserResponse(id=str(user.id), email=user.email, nickname=user.nickname)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    validate_password(request.new_password)
    async with get_db_session() as session:
        result = await session.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        user.password_hash = get_password_hash(request.new_password)
        await session.commit()
        return {"message": "密码重置成功"}


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    payload = verify_refresh_token(request.refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌中无用户标识")

    new_access_token = create_access_token({"sub": user_id})
    return {"access_token": new_access_token, "token_type": "bearer"}
