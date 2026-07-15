"""AI教练模块 API 路由。参考职途AI的ReAct Agent架构。"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.application import Application
from app.models.interview import Interview, Evaluation
from app.models.resume import Resume
from app.schemas.coach import CoachChatRequest, CoachChatResponse, CoachReportResponse, CoachTool, CoachToolResult

router = APIRouter(prefix="/coach", tags=["coach"])

_TOOLS: list[CoachTool] = [
    {
        "name": "get_resume_list",
        "description": "获取用户的简历列表，用于了解用户的技能和经验",
        "parameters": [],
    },
    {
        "name": "get_resume_detail",
        "description": "获取指定简历的详细内容，包括技能、项目经验等",
        "parameters": [{"name": "resume_id", "type": "string", "required": True}],
    },
    {
        "name": "get_application_list",
        "description": "获取用户的投递记录，了解求职进度",
        "parameters": [],
    },
    {
        "name": "get_interview_list",
        "description": "获取用户的面试记录，了解面试表现和反馈",
        "parameters": [],
    },
    {
        "name": "analyze_skill_gap",
        "description": "分析简历与目标岗位的技能差距",
        "parameters": [
            {"name": "resume_id", "type": "string", "required": True},
            {"name": "job_description", "type": "string", "required": True},
        ],
    },
    {
        "name": "generate_report",
        "description": "生成求职作战报告，汇总简历、面试、投递数据",
        "parameters": [],
    },
    {
        "name": "get_dashboard",
        "description": "获取求职仪表盘数据，包括简历数、面试数、投递数等统计",
        "parameters": [],
    },
    {
        "name": "ask_user",
        "description": "向用户提问，获取更多信息",
        "parameters": [{"name": "question", "type": "string", "required": True}],
    },
]


async def _call_tool(tool_name: str, params: dict, user_id: str) -> CoachToolResult:
    async with get_db_session() as session:
        if tool_name == "get_resume_list":
            result = await session.execute(
                select(Resume.id, Resume.original_filename, Resume.created_at)
                .where(Resume.user_id == uuid.UUID(user_id))
            )
            resumes = []
            for row in result.all():
                resumes.append({
                    "id": str(row[0]),
                    "filename": row[1],
                    "created_at": row[2].strftime("%Y-%m-%d") if row[2] else "",
                })
            return {"tool": tool_name, "success": True, "data": {"resumes": resumes}}
        
        elif tool_name == "get_resume_detail":
            resume_id = params.get("resume_id")
            if not resume_id:
                return {"tool": tool_name, "success": False, "error": "缺少 resume_id 参数"}
            result = await session.execute(select(Resume).where(Resume.id == uuid.UUID(resume_id)))
            resume = result.scalar_one_or_none()
            if not resume:
                return {"tool": tool_name, "success": False, "error": "简历不存在"}
            parsed = resume.parsed_data or {}
            return {
                "tool": tool_name,
                "success": True,
                "data": {
                    "id": str(resume.id),
                    "filename": resume.original_filename,
                    "skills": parsed.get("skills", []),
                    "projects": parsed.get("projects", []),
                    "education": parsed.get("education", []),
                    "work_experience": parsed.get("work_experience", []),
                    "raw_text": parsed.get("raw_text", "")[:500],
                },
            }
        
        elif tool_name == "get_application_list":
            result = await session.execute(
                select(Application)
                .where(Application.user_id == uuid.UUID(user_id))
                .order_by(Application.created_at.desc())
            )
            applications = []
            for app in result.scalars().all():
                applications.append({
                    "id": str(app.id),
                    "company": app.company,
                    "position": app.position,
                    "stage": app.stage,
                    "city": app.city,
                    "salary_range": app.salary_range,
                    "feedback": app.feedback,
                    "created_at": app.created_at.strftime("%Y-%m-%d") if app.created_at else "",
                })
            return {"tool": tool_name, "success": True, "data": {"applications": applications}}
        
        elif tool_name == "get_interview_list":
            result = await session.execute(
                select(Interview)
                .where(Interview.user_id == uuid.UUID(user_id))
                .order_by(Interview.created_at.desc())
            )
            interviews = []
            for interview in result.scalars().all():
                eval_result = await session.execute(
                    select(Evaluation.overall).where(Evaluation.interview_id == interview.id)
                )
                overall_score = eval_result.scalar_one_or_none()
                interviews.append({
                    "id": str(interview.id),
                    "round": interview.round.value if hasattr(interview.round, "value") else interview.round,
                    "status": interview.status.value if hasattr(interview.status, "value") else interview.status,
                    "score": overall_score,
                    "created_at": interview.created_at.strftime("%Y-%m-%d") if interview.created_at else "",
                })
            return {"tool": tool_name, "success": True, "data": {"interviews": interviews}}
        
        elif tool_name == "get_dashboard":
            resume_count = await session.scalar(
                select(func.count(Resume.id)).where(Resume.user_id == uuid.UUID(user_id))
            )
            interview_count = await session.scalar(
                select(func.count(Interview.id)).where(Interview.user_id == uuid.UUID(user_id))
            )
            application_count = await session.scalar(
                select(func.count(Application.id)).where(Application.user_id == uuid.UUID(user_id))
            )
            
            stage_stats = {}
            stage_result = await session.execute(
                select(Application.stage, func.count(Application.id))
                .where(Application.user_id == uuid.UUID(user_id))
                .group_by(Application.stage)
            )
            for row in stage_result.all():
                stage_stats[row[0]] = row[1]
            
            avg_score = await session.scalar(
                select(func.avg(Evaluation.overall)).where(
                    Evaluation.interview_id.in_(
                        select(Interview.id).where(Interview.user_id == uuid.UUID(user_id))
                    ),
                    Evaluation.overall.is_not(None),
                )
            )
            
            return {
                "tool": tool_name,
                "success": True,
                "data": {
                    "resume_count": resume_count or 0,
                    "interview_count": interview_count or 0,
                    "application_count": application_count or 0,
                    "stage_stats": stage_stats,
                    "avg_interview_score": round(avg_score, 1) if avg_score else 0,
                },
            }
        
        elif tool_name == "analyze_skill_gap":
            resume_id = params.get("resume_id")
            job_description = params.get("job_description")
            if not resume_id or not job_description:
                return {"tool": tool_name, "success": False, "error": "缺少必要参数"}
            
            result = await session.execute(select(Resume).where(Resume.id == uuid.UUID(resume_id)))
            resume = result.scalar_one_or_none()
            if not resume:
                return {"tool": tool_name, "success": False, "error": "简历不存在"}
            
            parsed = resume.parsed_data or {}
            raw_text = parsed.get("raw_text", "")
            
            resume_lower = raw_text.lower()
            job_lower = job_description.lower()
            
            common_keywords = ["python", "java", "javascript", "typescript", "react", "vue", "node", "sql", "mysql", "postgresql", "redis", "docker", "kubernetes", "git", "api", "http", "json"]
            required = [kw for kw in common_keywords if kw in job_lower]
            matched = [kw for kw in required if kw in resume_lower]
            missing = [kw for kw in required if kw not in resume_lower]
            
            return {
                "tool": tool_name,
                "success": True,
                "data": {
                    "required_skills": required,
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "match_rate": round(len(matched) / len(required) * 100, 1) if required else 0,
                },
            }
        
        elif tool_name == "generate_report":
            dashboard_result = await _call_tool("get_dashboard", {}, user_id)
            resume_result = await _call_tool("get_resume_list", {}, user_id)
            application_result = await _call_tool("get_application_list", {}, user_id)
            interview_result = await _call_tool("get_interview_list", {}, user_id)
            
            return {
                "tool": tool_name,
                "success": True,
                "data": {
                    "dashboard": dashboard_result.get("data", {}),
                    "resumes": resume_result.get("data", {}).get("resumes", []),
                    "applications": application_result.get("data", {}).get("applications", []),
                    "interviews": interview_result.get("data", {}).get("interviews", []),
                },
            }
        
        elif tool_name == "ask_user":
            question = params.get("question")
            return {
                "tool": tool_name,
                "success": True,
                "data": {"question": question},
                "needs_user_input": True,
            }
        
        else:
            return {"tool": tool_name, "success": False, "error": f"未知工具: {tool_name}"}


def _generate_local_response(user_message: str, context: dict) -> str:
    tools_used = context.get("tools_used", [])
    
    if any(t in user_message for t in ["报告", "作战报告", "总结"]):
        dashboard = context.get("dashboard", {})
        resume_count = dashboard.get("resume_count", 0)
        interview_count = dashboard.get("interview_count", 0)
        application_count = dashboard.get("application_count", 0)
        
        report = "## 求职作战报告\n\n"
        report += "### 当前状态概览\n"
        report += f"- 简历数量：{resume_count} 份\n"
        report += f"- 面试次数：{interview_count} 次\n"
        report += f"- 投递数量：{application_count} 个\n"
        
        if application_count > 0:
            report += "\n### 投递阶段分布\n"
            stage_stats = dashboard.get("stage_stats", {})
            stages = {"applied": "已投递", "interview": "面试中", "offer": "已获得Offer", "rejected": "已拒绝", "pending": "待回复"}
            for stage, count in stage_stats.items():
                report += f"- {stages.get(stage, stage)}：{count} 个\n"
        
        avg_score = dashboard.get("avg_interview_score", 0)
        if avg_score > 0:
            report += f"\n### 面试表现\n"
            report += f"- 平均面试评分：{avg_score} 分\n"
        
        report += "\n### 下一步建议\n"
        if resume_count == 0:
            report += "1. 上传简历，建立你的求职资产\n"
        if interview_count == 0:
            report += "2. 进行模拟面试，熟悉面试流程\n"
        if application_count == 0:
            report += "3. 开始投递，记录求职进度\n"
        else:
            report += "4. 复盘已完成的面试，优化回答\n"
        
        return report
    
    if any(t in user_message for t in ["简历", "优化", "诊断"]):
        return (
            "我建议从以下几个方面优化简历：\n\n"
            "1. **结构完整度**：确保包含教育背景、工作经历、项目经验、技能清单、联系方式\n"
            "2. **量化成果**：使用具体数字描述成果，如用户量、QPS、性能提升百分比\n"
            "3. **技能匹配**：根据目标岗位JD调整技能关键词密度\n"
            "4. **项目深度**：按STAR法则描述项目，强调你的职责和贡献\n\n"
            "你可以上传简历后，我帮你做详细的ATS诊断分析。"
        )
    
    if any(t in user_message for t in ["面试", "模拟", "练习"]):
        return (
            "模拟面试可以帮你熟悉真实面试流程：\n\n"
            "1. **自我介绍**：准备1分钟、3分钟两个版本\n"
            "2. **项目深挖**：准备2-3个核心项目的详细讲法\n"
            "3. **技术追问**：熟悉常见技术问题的深度回答\n"
            "4. **行为面试**：准备STAR案例回答\n\n"
            "建议你先上传简历，这样我可以根据你的背景生成更有针对性的面试题。"
        )
    
    if any(t in user_message for t in ["投递", "跟进", "看板"]):
        return (
            "投递看板可以帮你管理求职进度：\n\n"
            "- 记录公司、岗位、阶段、联系方式\n"
            "- 按阶段组织机会池（已投递、面试中、待回复、Offer、已拒绝）\n"
            "- 生成跟进建议和沟通话术\n\n"
            "保持记录更新，方便后续复盘。"
        )
    
    return (
        "你好！我是你的求职教练。我可以帮你：\n\n"
        "1. **简历诊断与优化**：ATS兼容性分析、关键词优化、量化建议\n"
        "2. **岗位匹配分析**：技能差距分析、匹配度评估、补强路线\n"
        "3. **模拟面试**：多轮面试练习、实时反馈、语音分析\n"
        "4. **投递追踪**：看板管理、跟进建议、薪资评估\n"
        "5. **求职作战报告**：汇总数据、阶段性复盘、下一步计划\n\n"
        "请问你想从哪个方面开始？"
    )


@router.get("/tools", response_model=list[CoachTool])
async def get_tools(current_user: str = Depends(get_current_user)):
    return _TOOLS


@router.post("/chat", response_model=CoachChatResponse)
async def coach_chat(
    request: CoachChatRequest,
    current_user: str = Depends(get_current_user),
):
    messages = request.messages or []
    tool_results = []
    context = {}
    
    for msg in messages:
        if msg.get("tool_result"):
            tool_results.append(msg["tool_result"])
            context.update(msg["tool_result"].get("data", {}))
            if msg["tool_result"].get("needs_user_input"):
                return CoachChatResponse(
                    response=msg["tool_result"]["data"].get("question", "请提供更多信息"),
                    needs_user_input=True,
                )
    
    user_text = messages[-1].get("content", "") if messages else request.message
    
    simple_intents = {
        "报告": "generate_report",
        "总结": "generate_report",
        "dashboard": "get_dashboard",
        "仪表盘": "get_dashboard",
        "简历列表": "get_resume_list",
        "投递": "get_application_list",
        "面试记录": "get_interview_list",
        "差距分析": "analyze_skill_gap",
    }
    
    matched_tool = None
    for intent, tool_name in simple_intents.items():
        if intent in user_text:
            matched_tool = tool_name
            break
    
    if matched_tool == "analyze_skill_gap":
        resume_result = await _call_tool("get_resume_list", {}, current_user)
        resumes = resume_result.get("data", {}).get("resumes", [])
        if not resumes:
            return CoachChatResponse(
                response="请先上传简历，我才能帮你做技能差距分析。",
                needs_user_input=True,
            )
        
        if not request.job_description:
            return CoachChatResponse(
                response="请提供目标岗位的JD描述，我才能分析技能差距。",
                needs_user_input=True,
            )
        
        gap_result = await _call_tool(
            "analyze_skill_gap",
            {"resume_id": resumes[0]["id"], "job_description": request.job_description},
            current_user,
        )
        gap_data = gap_result.get("data", {})
        
        response_text = "## 技能差距分析\n\n"
        response_text += f"**匹配度**：{gap_data.get('match_rate', 0)}%\n\n"
        response_text += "### 已匹配技能\n"
        if gap_data.get("matched_skills"):
            response_text += ", ".join(gap_data["matched_skills"]) + "\n\n"
        else:
            response_text += "暂无\n\n"
        response_text += "### 技能缺口\n"
        if gap_data.get("missing_skills"):
            response_text += ", ".join(gap_data["missing_skills"]) + "\n\n"
        else:
            response_text += "无，匹配度很高！\n\n"
        response_text += "### 建议\n"
        if gap_data.get("missing_skills"):
            response_text += f"重点学习：{', '.join(gap_data['missing_skills'][:5])}\n"
            response_text += "在简历项目经验中补充相关技能的实践描述\n"
        else:
            response_text += "技能匹配度很高，建议重点准备面试中对技能深度的考察\n"
        
        return CoachChatResponse(response=response_text)
    
    if matched_tool:
        tool_result = await _call_tool(matched_tool, {}, current_user)
        tool_data = tool_result.get("data", {})
        
        if matched_tool == "generate_report":
            response_text = _generate_local_response(user_text, tool_data)
        elif matched_tool == "get_dashboard":
            response_text = (
                f"📊 **求职仪表盘**\n\n"
                f"- 简历：{tool_data.get('resume_count', 0)} 份\n"
                f"- 面试：{tool_data.get('interview_count', 0)} 次\n"
                f"- 投递：{tool_data.get('application_count', 0)} 个\n"
                f"- 平均面试评分：{tool_data.get('avg_interview_score', 0)} 分\n"
            )
            stages = {"applied": "已投递", "interview": "面试中", "offer": "Offer", "rejected": "拒绝", "pending": "待回复"}
            for stage, count in tool_data.get("stage_stats", {}).items():
                response_text += f"- {stages.get(stage, stage)}：{count} 个\n"
        elif matched_tool == "get_resume_list":
            resumes = tool_data.get("resumes", [])
            if resumes:
                response_text = "📄 **你的简历列表**\n\n"
                for r in resumes[:5]:
                    response_text += f"- [{r['filename']}](resume/{r['id']}) - {r['created_at']}\n"
            else:
                response_text = "你还没有上传简历，建议先上传一份简历作为求职资产。"
        elif matched_tool == "get_application_list":
            apps = tool_data.get("applications", [])
            if apps:
                response_text = "📋 **你的投递记录**\n\n"
                for app in apps[:5]:
                    response_text += f"- {app['company']} - {app['position']} ({app['stage']})\n"
            else:
                response_text = "你还没有投递记录，建议开始记录你的求职进度。"
        elif matched_tool == "get_interview_list":
            interviews = tool_data.get("interviews", [])
            if interviews:
                response_text = "💬 **你的面试记录**\n\n"
                for i in interviews[:5]:
                    score = f" - 评分: {i['score']}" if i.get("score") else ""
                    response_text += f"- {i['round']}面试 {i['status']}{score}\n"
            else:
                response_text = "你还没有面试记录，建议进行模拟面试练习。"
        else:
            response_text = json.dumps(tool_data, ensure_ascii=False)
        
        return CoachChatResponse(response=response_text)
    
    response_text = _generate_local_response(user_text, context)

    # 尝试使用 LLM 增强回复
    try:
        from app.core.llm_service import get_llm_service
        llm = get_llm_service()
        if llm.is_real_llm_available:
            coach_system = (
                "你是「求职喵」的 AI 求职教练，帮助求职者提升简历、准备面试、规划职业路径。\n"
                "你的风格：专业但不刻板、鼓励为主、建议具体可执行。\n"
                "回答要简洁实用，使用 Markdown 格式，适当用 emoji 增加亲和力。\n"
                "如果用户询问简历优化，给出具体可操作的建议。\n"
                "如果用户询问面试技巧，结合 STAR 法则和常见问题类型给出指导。"
            )
            llm_messages = []
            # 加入工具调用获取的上下文
            if tool_results:
                context_summary = json.dumps(context, ensure_ascii=False)
                llm_messages.append({
                    "role": "system",
                    "content": f"用户数据上下文：{context_summary}",
                })
            llm_messages.append({"role": "user", "content": user_text})
            response_text = await llm.chat(
                llm_messages, system_prompt=coach_system,
                temperature=0.7, max_tokens=1024,
            )
    except Exception as e:
        logger.warning("AI教练 LLM 调用失败，使用本地回复: %s", e)

    return CoachChatResponse(response=response_text)


@router.get("/report", response_model=CoachReportResponse)
async def get_career_report(current_user: str = Depends(get_current_user)):
    result = await _call_tool("generate_report", {}, current_user)
    data = result.get("data", {})
    
    dashboard = data.get("dashboard", {})
    resumes = data.get("resumes", [])
    applications = data.get("applications", [])
    interviews = data.get("interviews", [])
    
    resume_count = dashboard.get("resume_count", 0)
    interview_count = dashboard.get("interview_count", 0)
    application_count = dashboard.get("application_count", 0)
    avg_score = dashboard.get("avg_interview_score", 0)
    
    status = "起步阶段"
    if application_count >= 10:
        status = "积极投递阶段"
    if interview_count >= 5:
        status = "面试冲刺阶段"
    if any(a.get("stage") == "offer" for a in applications):
        status = "收获阶段"
    
    recommendations = []
    if resume_count == 0:
        recommendations.append("上传简历，建立求职资产")
    if interview_count == 0:
        recommendations.append("进行模拟面试练习")
    if application_count == 0:
        recommendations.append("开始投递并记录进度")
    if avg_score > 0 and avg_score < 70:
        recommendations.append("复盘面试，优化回答技巧")
    
    return CoachReportResponse(
        status=status,
        resume_count=resume_count,
        interview_count=interview_count,
        application_count=application_count,
        avg_interview_score=avg_score,
        stage_stats=dashboard.get("stage_stats", {}),
        recent_resumes=resumes[:3],
        recent_applications=applications[:5],
        recent_interviews=interviews[:5],
        recommendations=recommendations,
    )
