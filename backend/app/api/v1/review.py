"""复盘模块 API 路由。"""

from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.growth import GrowthRecord
from app.models.interview import Evaluation, Interview, InterviewStatus, Message, Review
from app.schemas.review import ReviewListItem, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["reviews"])
logger = logging.getLogger(__name__)


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str, current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(select(Review).where(Review.id == uuid.UUID(review_id)))
        review = result.scalar_one_or_none()
        if not review:
            raise HTTPException(status_code=404, detail="复盘报告不存在")
        return ReviewResponse(
            id=str(review.id),
            interview_id=str(review.interview_id),
            overall_score=review.overall_score or 0,
            radar_data=review.radar_data or {},
            question_reviews=review.question_reviews or [],
            interviewer_summary=review.interviewer_summary or "",
            suggestions=review.suggestions or [],
            created_at=review.created_at.isoformat() if review.created_at else "",
        )


@router.get("", response_model=list[ReviewListItem])
async def list_reviews(current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(
            select(Review, Interview)
            .join(Interview, Review.interview_id == Interview.id)
            .where(Interview.user_id == uuid.UUID(current_user))
            .order_by(Review.created_at.desc())
        )
        rows = result.all()
        return [
            ReviewListItem(
                id=str(r.id),
                interview_id=str(r.interview_id),
                overall_score=r.overall_score or 0,
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
            for r, _ in rows
        ]


@router.post("/generate/{interview_id}", response_model=ReviewResponse)
async def generate_review(interview_id: str, current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        interview_result = await session.execute(
            select(Interview).where(Interview.id == uuid.UUID(interview_id))
        )
        interview = interview_result.scalar_one_or_none()
        if not interview or str(interview.user_id) != current_user:
            raise HTTPException(status_code=404, detail="面试不存在")

        eval_result = await session.execute(
            select(Evaluation).where(Evaluation.interview_id == uuid.UUID(interview_id))
        )
        evaluations = eval_result.scalars().all()

        msg_result = await session.execute(
            select(Message).where(Message.interview_id == uuid.UUID(interview_id)).order_by(Message.created_at)
        )
        messages = msg_result.scalars().all()

        # 聚合评分
        dims = {
            "professional": [], "logic": [], "communication": [],
            "project": [], "match": [], "overall": [],
            "learning": [], "stress_resistance": [], "decomposition": [],
            "engineering_quality": [], "innovation": [],
        }
        for ev in evaluations:
            if ev.professional is not None:
                dims["professional"].append(ev.professional)
            if ev.logic is not None:
                dims["logic"].append(ev.logic)
            if ev.communication is not None:
                dims["communication"].append(ev.communication)
            if ev.project is not None:
                dims["project"].append(ev.project)
            if ev.match is not None:
                dims["match"].append(ev.match)
            if ev.overall is not None:
                dims["overall"].append(ev.overall)
            if ev.learning is not None:
                dims["learning"].append(ev.learning)
            if ev.stress_resistance is not None:
                dims["stress_resistance"].append(ev.stress_resistance)
            if ev.decomposition is not None:
                dims["decomposition"].append(ev.decomposition)
            if ev.engineering_quality is not None:
                dims["engineering_quality"].append(ev.engineering_quality)
            if ev.innovation is not None:
                dims["innovation"].append(ev.innovation)

        avg = {k: int(sum(v) / len(v)) if v else 0 for k, v in dims.items()}
        overall = avg.get("overall", 0)

        # 雷达图：基础五维度 + 综合表现始终包含，条件维度仅在触及时展示
        radar_data = {
            "专业能力": avg.get("professional", 0),
            "逻辑表达": avg.get("logic", 0),
            "沟通能力": avg.get("communication", 0),
            "项目讲解": avg.get("project", 0),
            "岗位匹配": avg.get("match", 0),
        }
        if dims["learning"]:
            radar_data["学习能力"] = avg.get("learning", 0)
        if dims["stress_resistance"]:
            radar_data["抗压表现"] = avg.get("stress_resistance", 0)
        if dims["decomposition"]:
            radar_data["问题拆解"] = avg.get("decomposition", 0)
        if dims["engineering_quality"]:
            radar_data["工程素养"] = avg.get("engineering_quality", 0)
        if dims["innovation"]:
            radar_data["创新思维"] = avg.get("innovation", 0)
        radar_data["综合表现"] = overall

        question_reviews = []
        q_msgs = [m for m in messages if m.role == "interviewer"]
        for i, qm in enumerate(q_msgs):
            a_msgs = [m for m in messages if m.role == "user"]
            answer = a_msgs[i].content if i < len(a_msgs) else ""
            question_reviews.append({
                "question": qm.content,
                "answer_summary": answer[:100] + "..." if len(answer) > 100 else answer,
                "score": avg.get("overall", 60),
                "strengths": ["回答覆盖了核心要点"],
                "improvements": ["可补充量化数据", "使用 STAR 法则组织答案"],
            })

        suggestions = []
        if avg.get("professional", 0) < 70:
            suggestions.append({"priority": "high", "dimension": "专业能力", "action": "补充核心技术栈的深度项目案例"})
        if avg.get("logic", 0) < 70:
            suggestions.append({"priority": "high", "dimension": "逻辑表达", "action": "使用 STAR 法则结构化回答"})
        if avg.get("communication", 0) < 70:
            suggestions.append({"priority": "medium", "dimension": "沟通能力", "action": "增加与面试官的互动，确认问题意图"})
        if avg.get("project", 0) < 70:
            suggestions.append({"priority": "high", "dimension": "项目讲解", "action": "为每个项目准备 30 秒、1 分钟、3 分钟三个版本"})
        if avg.get("match", 0) < 70:
            suggestions.append({"priority": "medium", "dimension": "岗位匹配", "action": "突出与 JD 关键词的匹配经验"})
        if dims["learning"] and avg.get("learning", 0) < 70:
            suggestions.append({"priority": "medium", "dimension": "学习能力", "action": "准备具体的学习路径案例，如'X 天内学会 Y 技术'"})
        if dims["stress_resistance"] and avg.get("stress_resistance", 0) < 70:
            suggestions.append({"priority": "medium", "dimension": "抗压表现", "action": "准备一个线上事故处理案例，突出冷静应对和复盘改进"})
        if dims["decomposition"] and avg.get("decomposition", 0) < 70:
            suggestions.append({"priority": "high", "dimension": "问题拆解", "action": "练习系统设计题的分层拆解法，从上到下逐层细化"})
        if dims["engineering_quality"] and avg.get("engineering_quality", 0) < 70:
            suggestions.append({"priority": "medium", "dimension": "工程素养", "action": "在项目描述中补充测试覆盖、监控告警和异常处理方案"})
        if dims["innovation"] and avg.get("innovation", 0) < 70:
            suggestions.append({"priority": "low", "dimension": "创新思维", "action": "准备一个自研或改进方案的案例，突出思考过程"})
        if not suggestions:
            suggestions.append({"priority": "low", "dimension": "综合", "action": "继续保持，尝试更高难度的模拟面试"})

        # 尝试用LLM生成更丰富的面试官总结
        interviewer_summary = "整体表现良好，建议针对薄弱维度进行专项训练。"
        try:
            from app.core.llm_service import get_llm_service
            llm = get_llm_service()
            if llm.is_real_llm_available:
                summary_prompt = (
                    "你是一位资深面试官，请根据以下面试评判数据，用2-3句话总结候选人的整体表现，"
                    "包括主要优势和需要改进的地方。语气专业客观。"
                )
                summary_data = f"各维度平均分：{json.dumps(radar_data, ensure_ascii=False)}\n"
                summary_data += f"综合评分：{overall}分\n"
                if suggestions:
                    summary_data += f"改进建议：{', '.join(s['action'] for s in suggestions[:3])}\n"
                llm_result = await llm.chat(
                    [{"role": "user", "content": summary_data}],
                    system_prompt=summary_prompt,
                    temperature=0.5,
                    max_tokens=256,
                )
                if llm_result and len(llm_result.strip()) > 10:
                    interviewer_summary = llm_result.strip()
        except Exception as e:
            logger.warning("LLM生成面试官总结失败: %s", e)

        review = Review(
            id=uuid.uuid4(),
            interview_id=uuid.UUID(interview_id),
            overall_score=overall,
            radar_data=radar_data,
            question_reviews=question_reviews,
            interviewer_summary=interviewer_summary,
            suggestions=suggestions,
        )
        session.add(review)

        # 自动创建成长记录
        dim_key_map = {
            "professional": "专业能力",
            "logic": "逻辑表达",
            "communication": "沟通能力",
            "project": "项目讲解",
            "match": "岗位匹配",
            "comprehensive": "综合表现",
        }
        for key, cn_name in dim_key_map.items():
            score_val = avg.get(key, 0)
            if score_val > 0:
                growth = GrowthRecord(
                    id=uuid.uuid4(),
                    user_id=uuid.UUID(current_user),
                    interview_id=uuid.UUID(interview_id),
                    dimension=key,
                    score=score_val,
                )
                session.add(growth)

        # 更新面试状态为已结束
        interview.status = InterviewStatus.ENDED
        await session.commit()

        return ReviewResponse(
            id=str(review.id),
            interview_id=str(review.interview_id),
            overall_score=overall,
            radar_data=radar_data,
            question_reviews=question_reviews,
            interviewer_summary=review.interviewer_summary,
            suggestions=suggestions,
            created_at=review.created_at.isoformat() if review.created_at else "",
        )
