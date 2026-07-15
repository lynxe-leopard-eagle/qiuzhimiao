"""成长追踪 API 路由。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.growth import GrowthRecord
from app.schemas.growth import GrowthRadarResponse, GrowthTrendAllResponse, GrowthTrendPoint, GrowthTrendResponse

router = APIRouter(prefix="/growth", tags=["growth"])


@router.get("/radar", response_model=GrowthRadarResponse)
async def get_radar(current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(
            select(GrowthRecord)
            .where(GrowthRecord.user_id == uuid.UUID(current_user))
            .order_by(GrowthRecord.record_date.desc())
        )
        records = result.scalars().all()

        dimensions = ["专业能力", "逻辑表达", "沟通能力", "项目讲解", "岗位匹配", "综合表现"]
        dim_map = {
            "professional": "专业能力",
            "logic": "逻辑表达",
            "communication": "沟通能力",
            "project": "项目讲解",
            "match": "岗位匹配",
            "comprehensive": "综合表现",
        }

        latest = {}
        previous = {}
        for r in records:
            cn = dim_map.get(r.dimension, r.dimension)
            if cn not in latest:
                latest[cn] = r.score
            elif cn not in previous:
                previous[cn] = r.score

        latest_scores = [latest.get(d, 0) for d in dimensions]
        previous_scores = [previous.get(d, 0) for d in dimensions]

        return GrowthRadarResponse(
            dimensions=dimensions,
            latest_scores=latest_scores,
            previous_scores=previous_scores,
        )


@router.get("/trend", response_model=GrowthTrendAllResponse)
async def get_trend(current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(
            select(GrowthRecord)
            .where(GrowthRecord.user_id == uuid.UUID(current_user))
            .order_by(GrowthRecord.record_date)
        )
        records = result.scalars().all()

        dim_map = {
            "professional": "专业能力",
            "logic": "逻辑表达",
            "communication": "沟通能力",
            "project": "项目讲解",
            "match": "岗位匹配",
            "comprehensive": "综合表现",
        }

        by_dim = {}
        for r in records:
            cn = dim_map.get(r.dimension, r.dimension)
            by_dim.setdefault(cn, []).append(
                GrowthTrendPoint(
                    date=r.record_date.strftime("%Y-%m-%d") if r.record_date else "",
                    score=r.score,
                )
            )

        trends = [
            GrowthTrendResponse(dimension=dim, data=pts)
            for dim, pts in by_dim.items()
        ]

        return GrowthTrendAllResponse(trends=trends)
