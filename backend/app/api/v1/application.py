"""投递追踪模块 API 路由。"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.application import Application
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStageStats,
    ApplicationUpdateRequest,
)

router = APIRouter(prefix="/applications", tags=["applications"])

_STAGES = {
    "applied": "已投递",
    "screening": "简历筛选",
    "interview": "面试中",
    "offer": "已Offer",
    "rejected": "已拒绝",
}


@router.post("", response_model=ApplicationResponse)
async def create_application(
    request: ApplicationCreateRequest,
    current_user: str = Depends(get_current_user),
):
    application = Application(
        id=uuid.uuid4(),
        user_id=uuid.UUID(current_user),
        job_id=uuid.UUID(request.job_id) if request.job_id else None,
        company=request.company,
        position=request.position,
        stage=request.stage,
        city=request.city,
        salary_range=request.salary_range,
        notes=request.notes,
        contact_info=request.contact_info,
    )
    async with get_db_session() as session:
        session.add(application)
        await session.commit()
    return ApplicationResponse(
        id=str(application.id),
        company=application.company,
        position=application.position,
        stage=application.stage,
        city=application.city,
        salary_range=application.salary_range,
        notes=application.notes,
        contact_info=application.contact_info,
        feedback=application.feedback,
        created_at=application.created_at.isoformat(),
        updated_at=application.updated_at.isoformat(),
    )


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    current_user: str = Depends(get_current_user),
    stage: str | None = None,
):
    async with get_db_session() as session:
        query = select(Application).where(Application.user_id == uuid.UUID(current_user))
        if stage:
            query = query.where(Application.stage == stage)
        result = await session.execute(query.order_by(Application.created_at.desc()))
        applications = result.scalars().all()
        return [
            ApplicationResponse(
                id=str(a.id),
                company=a.company,
                position=a.position,
                stage=a.stage,
                city=a.city,
                salary_range=a.salary_range,
                notes=a.notes,
                contact_info=a.contact_info,
                feedback=a.feedback,
                created_at=a.created_at.isoformat(),
                updated_at=a.updated_at.isoformat(),
            )
            for a in applications
        ]


@router.get("/stats", response_model=list[ApplicationStageStats])
async def get_application_stats(current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(
            select(Application.stage, func.count(Application.id))
            .where(Application.user_id == uuid.UUID(current_user))
            .group_by(Application.stage)
        )
        stats = result.all()
        return [
            ApplicationStageStats(
                stage=stage,
                label=_STAGES.get(stage, stage),
                count=count,
            )
            for stage, count in stats
        ]


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    current_user: str = Depends(get_current_user),
):
    async with get_db_session() as session:
        result = await session.execute(
            select(Application).where(Application.id == uuid.UUID(application_id))
        )
        application = result.scalar_one_or_none()
        if not application or str(application.user_id) != current_user:
            raise HTTPException(status_code=404, detail="投递记录不存在")
        return ApplicationResponse(
            id=str(application.id),
            company=application.company,
            position=application.position,
            stage=application.stage,
            city=application.city,
            salary_range=application.salary_range,
            notes=application.notes,
            contact_info=application.contact_info,
            feedback=application.feedback,
            created_at=application.created_at.isoformat(),
            updated_at=application.updated_at.isoformat(),
        )


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    request: ApplicationUpdateRequest,
    current_user: str = Depends(get_current_user),
):
    async with get_db_session() as session:
        result = await session.execute(
            select(Application).where(Application.id == uuid.UUID(application_id))
        )
        application = result.scalar_one_or_none()
        if not application or str(application.user_id) != current_user:
            raise HTTPException(status_code=404, detail="投递记录不存在")

        if request.stage is not None:
            application.stage = request.stage
        if request.salary_range is not None:
            application.salary_range = request.salary_range
        if request.notes is not None:
            application.notes = request.notes
        if request.contact_info is not None:
            application.contact_info = request.contact_info
        if request.feedback is not None:
            application.feedback = request.feedback
        application.updated_at = datetime.utcnow()

        await session.commit()

        return ApplicationResponse(
            id=str(application.id),
            company=application.company,
            position=application.position,
            stage=application.stage,
            city=application.city,
            salary_range=application.salary_range,
            notes=application.notes,
            contact_info=application.contact_info,
            feedback=application.feedback,
            created_at=application.created_at.isoformat(),
            updated_at=application.updated_at.isoformat(),
        )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: str,
    current_user: str = Depends(get_current_user),
):
    async with get_db_session() as session:
        result = await session.execute(
            select(Application).where(Application.id == uuid.UUID(application_id))
        )
        application = result.scalar_one_or_none()
        if not application or str(application.user_id) != current_user:
            raise HTTPException(status_code=404, detail="投递记录不存在")
        await session.delete(application)
        await session.commit()
