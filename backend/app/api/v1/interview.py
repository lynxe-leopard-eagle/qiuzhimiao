"""面试模块 API 路由。"""

from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.core.database import get_db_session
from app.core.redis import get_redis
from app.core.security import get_current_user
from app.models.interview import Evaluation, Interview, InterviewStatus, Message
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.interview import (
    EvaluationResponse,
    InterviewAnswerRequest,
    InterviewEndResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)

router = APIRouter(prefix="/interviews", tags=["interviews"])

logger = logging.getLogger(__name__)


_QUESTION_BANK = {
    "behavioral": [
        "请分享一个你在工作中遇到的最大挑战，你是如何应对的？（请用 STAR 法则描述情境、任务、行动、结果）",
        "描述一次你与同事或上级产生分歧的经历，你是如何处理并达成共识的？",
        "举一个你主动承担额外责任的例子，最终结果如何？",
        "讲述一个你失败的项目或任务，你从中学到了什么？后来如何改进？",
        "请举例说明你如何在团队中推动一项重要变革或流程改进。",
        "描述一次你在紧迫 deadline 下完成任务的经过，你是如何取舍的？",
        "举一个你帮助团队成员解决问题的例子，你的具体贡献是什么？",
        "请分享一个你超越预期完成工作的案例，背后的动机是什么？",
        "讲述一次你需要快速学习新技能以完成任务的经过，学习路径是怎样的？",
        "描述一个你识别并解决潜在风险或问题的实例，结果如何？",
    ],
    "hr": [
        "请简单介绍一下你自己。",
        "你为什么选择应聘我们公司？",
        "你未来的职业规划是什么？",
        "你认为自己最大的优点和缺点分别是什么？",
        "你的期望薪资是多少？依据是什么？",
        "你为什么从上一家公司离职？",
        "你如何应对工作中的压力和紧急情况？",
        "描述你理想中的团队氛围和管理风格。",
        "你最近一年学到了什么新技能或新知识？是如何学习的？",
        "你如何看待加班和出差？",
        "如果你被录用，前三个月你会如何开展工作？",
        "你有哪些业余爱好？这些爱好对你的工作有什么帮助？",
    ],
    "tech1": [
        "请介绍你简历中最有挑战性的一个项目。",
        "你在项目中遇到过什么技术难题？如何解决的？",
        "请说说你对微服务架构的理解。",
        "请解释常见数据结构（数组、链表、哈希表、树）的区别与适用场景。",
        "什么是时间复杂度和空间复杂度？请举例说明如何分析。",
        "请讲讲数据库索引的原理，什么时候该建索引，什么时候不该建？",
        "HTTP 和 HTTPS 的区别是什么？HTTPS 的握手过程是怎样的？",
        "什么是进程和线程？它们之间有什么区别和联系？",
        "请说说你常用编程语言的特性，以及它适合解决什么类型的问题。",
        "你是如何使用 Git 进行版本控制的？请讲讲 rebase 和 merge 的区别。",
        "请解释一下 ACID 是什么，以及事务的隔离级别有哪些。",
        "TCP 三次握手和四次挥手的过程是怎样的？为什么需要三次和四次？",
    ],
    "tech2": [
        "请设计一个高并发秒杀系统。",
        "如何排查线上服务的性能瓶颈？",
        "分布式事务有哪些解决方案？各自的优缺点是什么？",
        "请设计一个短链生成服务，需要支持亿级 QPS。",
        "如何设计一个微服务架构？服务拆分的原则是什么？",
        "请讲讲分布式锁的实现方式，以及各自的优缺点。",
        "如何保证消息队列的高可用和消息不丢失？",
        "请说说你对缓存穿透、缓存击穿、缓存雪崩的理解和解决方案。",
        "如何进行接口性能优化？请从多个层面（数据库、缓存、代码、网络）说明。",
        "请描述一个 CI/CD 流程的最佳实践，包括代码合并、测试、部署等环节。",
        "常见的 Web 安全漏洞有哪些？如何防范 SQL 注入、XSS、CSRF？",
        "如何设计一个限流方案？令牌桶和漏桶算法的区别是什么？",
    ],
}

# 条件触发维度关键词
_LEARNING_KEYWORDS = {"学", "研究", "新", "快速", "上手", "探索", "没接触过", "不熟悉", "学习", "文档", "阅读源码"}
_STRESS_KEYWORDS = {"压力", "deadline", "冲突", "加班", "紧迫", "失败", "挫折", "批评", "矛盾", "延期", "线上事故", "紧急"}
_DECOMPOSITION_KEYWORDS = {"设计", "方案", "系统", "架构", "排查", "分析", "如何解决", "怎么规划", "拆解", "步骤", "模块", "分层"}
_ENGINEERING_KEYWORDS = {"代码质量", "规范", "测试", "异常处理", "性能", "安全", "code review", "重构", "最佳实践", "监控", "日志", "CI/CD", "单元测试", "代码审查"}
_INNOVATION_KEYWORDS = {"创新", "优化", "改进", "新思路", "想法", "不一样", "突破", "自研", "专利", "从零", "提出", "改进方案"}


_ROUND_INTRO_PROMPT = {
    "hr": "HR面试，侧重考察职业规划、团队协作、沟通表达、职业素养等软性能力。",
    "tech1": "技术一面，侧重考察项目经验、技术基础、编程能力、问题解决。",
    "tech2": "技术二面，侧重考察系统设计、架构能力、技术深度、开放性问题。",
    "behavioral": "行为面试，侧重考察过往经历、行为模式、价值观匹配。",
}


def _check_trigger(question: str, answer: str, keywords: set[str]) -> bool:
    """检查问答内容是否触发某个条件维度。"""
    combined = (question + answer).lower()
    return any(kw in combined for kw in keywords)


async def _generate_dynamic_question(
    resume_text: str,
    job_text: str,
    interview_round: str,
    previous_questions: list[str] | None = None,
) -> str | None:
    """使用 LLM 根据简历+JD 动态生成个性化面试题目。

    当 LLM 不可用时返回 None，由调用方回退到固定题库。
    """
    try:
        from app.core.llm_service import get_llm_service
        llm = get_llm_service()
        if not llm.is_real_llm_available:
            return None

        round_desc = _ROUND_INTRO_PROMPT.get(interview_round, "技术面试")
        prev_q_text = ""
        if previous_questions:
            prev_q_text = "\n已问过的问题（请勿重复）：\n" + "\n".join(f"- {q}" for q in previous_questions)

        system_prompt = (
            f"你是一位资深技术面试官，正在进行{round_desc}\n"
            "你的任务是根据候选人的简历和岗位JD，生成一道高度个性化的面试首题。\n"
            "要求：\n"
            "1. 题目必须紧密结合候选人简历中的具体项目/技能和JD中的核心要求\n"
            "2. 避免使用通用的套话，要针对候选人的背景提出有深度的问题\n"
            "3. 如果是技术面试，可以要求候选人讲解具体项目的技术细节\n"
            "4. 如果是HR面试，可以围绕候选人的职业经历提出行为面试问题\n"
            "5. 直接输出题目内容，不要有任何前缀说明"
        )

        user_content = ""
        if resume_text:
            user_content += f"【候选人简历内容】\n{resume_text[:1500]}\n\n"
        if job_text:
            user_content += f"【目标岗位JD】\n{job_text[:1000]}\n\n"
        user_content += f"请生成一道{round_desc}的首题。{prev_q_text}"

        result = await llm.chat(
            [{"role": "user", "content": user_content}],
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=256,
        )

        question = result.strip().strip('"').strip("'")
        # 过滤掉可能的markdown格式
        if question.startswith("**") and "**" in question[2:]:
            question = question.split("**", 2)[-1].strip()
        if len(question) < 10:
            return None
        return question
    except Exception as e:
        logger.warning("动态题库生成失败: %s", e)
        return None


def _mock_evaluate(answer: str, question: str = "", interviewer_style: str = "professional") -> EvaluationResponse:
    length = len(answer)
    has_code = "=" in answer or "(" in answer or ":" in answer
    has_numbers = any(ch.isdigit() for ch in answer)
    
    # 面试官风格权重调整
    style_weights = {
        "friendly": {"leniency": 0.1, "detail_weight": 0.8},
        "professional": {"leniency": 0.0, "detail_weight": 1.0},
        "strict": {"leniency": -0.1, "detail_weight": 1.2},
    }
    weights = style_weights.get(interviewer_style, style_weights["professional"])
    leniency = weights["leniency"]
    detail_weight = weights["detail_weight"]

    # 基础五维度（始终评分）
    professional_base = 50 + length // 10 + (10 if has_code else 0)
    professional = min(100, max(0, professional_base + int(professional_base * leniency)))
    
    logic_base = 50 + length // 12 + (5 if "首先" in answer or "然后" in answer else 0)
    logic = min(100, max(0, logic_base + int(logic_base * leniency)))
    
    communication_base = 50 + length // 15
    communication = min(100, max(0, communication_base + int(communication_base * leniency)))
    
    project_base = 50 + length // 8 + (10 if has_numbers else 0)
    project = min(100, max(0, project_base + int(project_base * leniency)))
    
    match_score_base = 50 + length // 10
    match_score = min(100, max(0, match_score_base + int(match_score_base * leniency)))

    # 条件触发维度（仅当问答内容涉及相关关键词时才评分）
    learning = None
    if _check_trigger(question, answer, _LEARNING_KEYWORDS):
        learning_base = 50 + length // 12 + (15 if any(kw in answer for kw in ["学", "研究", "文档"]) else 0)
        learning = min(100, max(0, learning_base + int(learning_base * leniency)))

    stress_resistance = None
    if _check_trigger(question, answer, _STRESS_KEYWORDS):
        stress_base = 50 + length // 10 + (15 if any(kw in answer for kw in ["解决", "处理", "复盘", "改进"]) else 0)
        stress_resistance = min(100, max(0, stress_base + int(stress_base * leniency)))

    decomposition = None
    if _check_trigger(question, answer, _DECOMPOSITION_KEYWORDS):
        has_structure = any(kw in answer for kw in ["首先", "其次", "第一", "1.", "2.", "步骤", "分为"])
        decomp_base = 50 + length // 10 + (20 if has_structure else 0)
        decomposition = min(100, max(0, int(decomp_base * detail_weight)))

    engineering_quality = None
    if _check_trigger(question, answer, _ENGINEERING_KEYWORDS):
        has_eng_details = any(kw in answer for kw in ["测试", "监控", "日志", "异常", "规范", "review", "重构"])
        eng_base = 50 + length // 12 + (20 if has_eng_details else 0)
        engineering_quality = min(100, max(0, int(eng_base * detail_weight)))

    innovation = None
    if _check_trigger(question, answer, _INNOVATION_KEYWORDS):
        has_innovation = any(kw in answer for kw in ["创新", "优化", "改进", "自研", "突破", "提出"])
        innov_base = 50 + length // 12 + (20 if has_innovation else 0)
        innovation = min(100, max(0, innov_base + int(innov_base * leniency)))

    # 综合评分：基础五维度 + 已触发的条件维度
    all_scores = [professional, logic, communication, project, match_score]
    if learning is not None:
        all_scores.append(learning)
    if stress_resistance is not None:
        all_scores.append(stress_resistance)
    if decomposition is not None:
        all_scores.append(decomposition)
    if engineering_quality is not None:
        all_scores.append(engineering_quality)
    if innovation is not None:
        all_scores.append(innovation)
    overall = int(sum(all_scores) / len(all_scores))

    # 根据面试官风格调整追问策略
    if interviewer_style == "strict":
        should_follow = length < 150 or (not has_numbers and not has_code)
    elif interviewer_style == "friendly":
        should_follow = length < 80 or (not has_numbers and not has_code)
    else:
        should_follow = length < 100 or (not has_numbers and not has_code)

    # 附加维度反馈
    extra_feedback = []
    if learning is not None and learning < 60:
        extra_feedback.append("学习能力：建议展示更具体的学习路径和方法论。")
    if stress_resistance is not None and stress_resistance < 60:
        extra_feedback.append("抗压表现：建议补充具体的应对措施和复盘改进。")
    if decomposition is not None and decomposition < 60:
        extra_feedback.append("问题拆解：建议使用分层思路，将大问题拆为可执行的小步骤。")
    if engineering_quality is not None and engineering_quality < 60:
        extra_feedback.append("工程素养：建议补充测试策略、监控方案或异常处理细节。")
    if innovation is not None and innovation < 60:
        extra_feedback.append("创新思维：建议展示独特的解决思路或改进方案。")

    # 根据面试官风格调整反馈语气
    if interviewer_style == "friendly":
        base_feedback = "回答不错！继续保持这个思路，建议补充更多量化指标会更有说服力。" if should_follow else "回答很完整，表达清晰，继续保持！"
    elif interviewer_style == "strict":
        base_feedback = "回答不够深入，缺少关键细节。请提供更具体的技术实现方案和数据支撑。" if should_follow else "回答基本合格，但在深度和细节上仍有提升空间。"
    else:
        base_feedback = "回答基本完整。建议补充更多量化指标和技术细节。" if should_follow else "回答较为充分。"
    
    feedback = base_feedback + (" " + " ".join(extra_feedback) if extra_feedback else "")

    # 根据面试官风格调整追问问题
    follow_up_options = {
        "friendly": [
            "能否再详细说说这部分？我很感兴趣。",
            "这个思路很棒，能举个具体的例子吗？",
            "听起来很有收获，还有其他想分享的吗？",
        ],
        "professional": [
            "能否补充一下具体的性能数据或业务指标？",
            "请深入讲讲这个技术方案的实现细节。",
            "这个项目的技术难点在哪里？如何解决的？",
        ],
        "strict": [
            "这个回答太笼统了，请给出具体的数据和实现细节。",
            "你提到的方案有什么潜在风险？如何规避？",
            "这个方案的时间复杂度和空间复杂度是多少？有优化空间吗？",
        ],
    }
    follow_up_list = follow_up_options.get(interviewer_style, follow_up_options["professional"])
    follow_up_question = follow_up_list[0] if should_follow else None

    return EvaluationResponse(
        professional=professional,
        logic=logic,
        communication=communication,
        project=project,
        match=match_score,
        learning=learning,
        stress_resistance=stress_resistance,
        decomposition=decomposition,
        engineering_quality=engineering_quality,
        innovation=innovation,
        overall=overall,
        confidence=0.82,
        feedback=feedback,
        should_follow_up=should_follow,
        follow_up_question=follow_up_question,
    )


async def _llm_evaluate(
    answer: str,
    question: str = "",
    interviewer_style: str = "professional",
    interview_round: str = "tech1",
) -> EvaluationResponse:
    """使用 LLM 进行面试评判。当 LLM 不可用时回退到本地模拟。"""
    try:
        from app.core.llm_service import get_llm_service
        llm = get_llm_service()

        if not llm.is_real_llm_available:
            return _mock_evaluate(answer, question, interviewer_style)

        style_desc = {"friendly": "友好亲切", "professional": "专业严谨", "strict": "严格深入"}
        round_desc = {"hr": "HR面试", "tech1": "技术一面", "tech2": "技术二面", "behavioral": "行为面试"}

        system_prompt = (
            f"你是一位{style_desc.get(interviewer_style, '专业严谨')}的面试官，正在进行{round_desc.get(interview_round, '技术面试')}。"
            "请对候选人的回答进行客观评分和建设性反馈。\n\n"
            "请严格按以下 JSON 格式输出，不要输出其他内容：\n"
            '{"professional": 0-100, "logic": 0-100, "communication": 0-100, '
            '"project": 0-100, "match": 0-100, "overall": 0-100, '
            '"feedback": "具体反馈", "should_follow_up": true/false, '
            '"follow_up_question": "追问或null"}\n\n'
            "评分标准：\n"
            "- professional: 技术知识准确性和深度\n"
            "- logic: 回答的逻辑性和条理性\n"
            "- communication: 表达清晰度和沟通效果\n"
            "- project: 项目经验的展示质量\n"
            "- match: 与岗位的匹配程度\n"
            "- overall: 综合表现\n"
            "- should_follow_up: 回答是否需要追问（回答太短、缺少数据、不够深入时追问）\n"
            "- follow_up_question: 追问问题（如不需要追问则为null）"
        )

        messages = [
            {"role": "user", "content": f"面试问题：{question}\n\n候选人回答：{answer}\n\n请评分并给出反馈。"}
        ]

        result = await llm.chat(
            messages, system_prompt=system_prompt,
            temperature=0.3, max_tokens=512,
            response_format={"type": "json_object"},
        )

        data = json.loads(result)

        # 基础五维度
        professional = max(0, min(100, data.get("professional", 50)))
        logic = max(0, min(100, data.get("logic", 50)))
        communication = max(0, min(100, data.get("communication", 50)))
        project = max(0, min(100, data.get("project", 50)))
        match_score = max(0, min(100, data.get("match", 50)))
        overall = max(0, min(100, data.get("overall", 50)))
        feedback = data.get("feedback", "")
        should_follow = data.get("should_follow_up", False)
        follow_up = data.get("follow_up_question")

        # 条件触发维度（仍使用本地关键词检测）
        learning = None
        if _check_trigger(question, answer, _LEARNING_KEYWORDS):
            learning_base = 50 + len(answer) // 12 + (15 if any(kw in answer for kw in ["学", "研究", "文档"]) else 0)
            learning = min(100, max(0, learning_base))

        stress_resistance = None
        if _check_trigger(question, answer, _STRESS_KEYWORDS):
            stress_base = 50 + len(answer) // 10 + (15 if any(kw in answer for kw in ["解决", "处理", "复盘", "改进"]) else 0)
            stress_resistance = min(100, max(0, stress_base))

        decomposition = None
        if _check_trigger(question, answer, _DECOMPOSITION_KEYWORDS):
            has_structure = any(kw in answer for kw in ["首先", "其次", "第一", "1.", "2.", "步骤", "分为"])
            decomp_base = 50 + len(answer) // 10 + (20 if has_structure else 0)
            decomposition = min(100, max(0, decomp_base))

        engineering_quality = None
        if _check_trigger(question, answer, _ENGINEERING_KEYWORDS):
            has_eng = any(kw in answer for kw in ["测试", "监控", "日志", "异常", "规范", "review", "重构"])
            eng_base = 50 + len(answer) // 12 + (20 if has_eng else 0)
            engineering_quality = min(100, max(0, eng_base))

        innovation = None
        if _check_trigger(question, answer, _INNOVATION_KEYWORDS):
            has_innov = any(kw in answer for kw in ["创新", "优化", "改进", "自研", "突破", "提出"])
            innov_base = 50 + len(answer) // 12 + (20 if has_innov else 0)
            innovation = min(100, max(0, innov_base))

        # 如果有条件触发维度，重新计算 overall
        all_scores = [professional, logic, communication, project, match_score]
        if learning is not None:
            all_scores.append(learning)
        if stress_resistance is not None:
            all_scores.append(stress_resistance)
        if decomposition is not None:
            all_scores.append(decomposition)
        if engineering_quality is not None:
            all_scores.append(engineering_quality)
        if innovation is not None:
            all_scores.append(innovation)
        overall = int(sum(all_scores) / len(all_scores))

        return EvaluationResponse(
            professional=professional,
            logic=logic,
            communication=communication,
            project=project,
            match=match_score,
            learning=learning,
            stress_resistance=stress_resistance,
            decomposition=decomposition,
            engineering_quality=engineering_quality,
            innovation=innovation,
            overall=overall,
            confidence=0.9,
            feedback=feedback,
            should_follow_up=should_follow,
            follow_up_question=follow_up,
        )
    except Exception as e:
        logger.warning("LLM 评判失败，回退到本地模拟: %s", e)
        return _mock_evaluate(answer, question, interviewer_style)


@router.get("", response_model=list[dict])
async def list_interviews(
    current_user: str = Depends(get_current_user),
):
    async with get_db_session() as session:
        result = await session.execute(
            select(Interview).where(Interview.user_id == current_user).order_by(Interview.created_at.desc())
        )
        interviews = result.scalars().all()
        return [{
            "id": str(i.id),
            "round": i.round,
            "status": i.status,
            "duration": i.duration,
            "created_at": i.created_at.isoformat(),
        } for i in interviews]


@router.post("/start", response_model=InterviewStartResponse)
async def start_interview(
    request: InterviewStartRequest,
    current_user: str = Depends(get_current_user),
):
    interview = Interview(
        id=uuid.uuid4(),
        user_id=uuid.UUID(current_user),
        resume_id=uuid.UUID(request.resume_id) if request.resume_id else None,
        job_id=uuid.UUID(request.job_id) if request.job_id else None,
        round=request.round,
        status=InterviewStatus.ONGOING,
    )

    # 获取简历和JD内容用于生成个性化首题
    resume_text = ""
    job_text = ""
    async with get_db_session() as session:
        if request.resume_id:
            result = await session.execute(
                select(Resume).where(Resume.id == uuid.UUID(request.resume_id))
            )
            resume = result.scalar_one_or_none()
            if resume and resume.parsed_data:
                resume_text = resume.parsed_data.get("raw_text", "")

        if request.job_id:
            result = await session.execute(
                select(Job).where(Job.id == uuid.UUID(request.job_id))
            )
            job = result.scalar_one_or_none()
            if job:
                job_text = job.description or ""

    # 尝试用LLM生成个性化首题
    dynamic_question = await _generate_dynamic_question(
        resume_text=resume_text,
        job_text=job_text,
        interview_round=request.round,
    )

    first_question = dynamic_question or _QUESTION_BANK.get(
        request.round, _QUESTION_BANK["tech1"]
    )[0]

    async with get_db_session() as session:
        session.add(interview)

        msg = Message(
            id=uuid.uuid4(),
            interview_id=interview.id,
            role="interviewer",
            content=first_question,
        )
        session.add(msg)
        await session.commit()

    # 将会话上下文存入Redis（TTL=2小时）
    try:
        redis = await get_redis()
        session_key = f"interview:{interview.id}"
        await redis.hset(session_key, mapping={
            "user_id": current_user,
            "round": request.round,
            "style": request.interviewer_style or "professional",
            "resume_text": resume_text[:2000] if resume_text else "",
            "job_text": job_text[:1500] if job_text else "",
            "questions_asked": json.dumps([first_question], ensure_ascii=False),
        })
        await redis.expire(session_key, 7200)
    except Exception as e:
        logger.warning("Redis 会话缓存写入失败: %s", e)

    return InterviewStartResponse(
        interview_id=str(interview.id),
        round=request.round,
        first_question=first_question,
    )


@router.post("/answer")
async def answer_question(
    request: InterviewAnswerRequest,
    current_user: str = Depends(get_current_user),
):
    async with get_db_session() as session:
        result = await session.execute(
            select(Interview).where(Interview.id == uuid.UUID(request.interview_id))
        )
        interview = result.scalar_one_or_none()
        if not interview or str(interview.user_id) != current_user:
            raise HTTPException(status_code=404, detail="面试不存在")
        if interview.status != InterviewStatus.ONGOING:
            raise HTTPException(status_code=400, detail="面试已结束")

        user_msg_id = uuid.uuid4()
        user_msg = Message(
            id=user_msg_id,
            interview_id=interview.id,
            role="user",
            content=request.answer,
        )
        session.add(user_msg)
        await session.commit()

        interview_round = interview.round
        interviewer_style = "professional"

    # 流式返回评判和追问
    async def event_stream():
        # 获取当前面试官问题（最后一条 interviewer 消息）
        async with get_db_session() as session:
            msg_result = await session.execute(
                select(Message)
                .where(Message.interview_id == uuid.UUID(request.interview_id))
                .where(Message.role == "interviewer")
                .order_by(Message.created_at.desc())
            )
            last_question = msg_result.scalars().first()
            question_text = last_question.content if last_question else ""

        evaluation = await _llm_evaluate(request.answer, question_text, interviewer_style)

        # 保存评判记录
        async with get_db_session() as session:
            eval_record = Evaluation(
                id=uuid.uuid4(),
                interview_id=uuid.UUID(request.interview_id),
                message_id=user_msg_id,
                professional=evaluation.professional,
                logic=evaluation.logic,
                communication=evaluation.communication,
                project=evaluation.project,
                match=evaluation.match,
                learning=evaluation.learning,
                stress_resistance=evaluation.stress_resistance,
                decomposition=evaluation.decomposition,
                engineering_quality=evaluation.engineering_quality,
                innovation=evaluation.innovation,
                overall=evaluation.overall,
                confidence=evaluation.confidence,
                feedback=evaluation.feedback,
                should_follow_up="true" if evaluation.should_follow_up else "false",
                follow_up_question=evaluation.follow_up_question,
            )
            session.add(eval_record)
            await session.commit()

        yield f"data: {json.dumps({'type': 'evaluation', 'payload': evaluation.model_dump()}, ensure_ascii=False)}\n\n"

        if evaluation.should_follow_up and evaluation.follow_up_question:
            yield f"data: {json.dumps({'type': 'question', 'payload': evaluation.follow_up_question}, ensure_ascii=False)}\n\n"
            async with get_db_session() as session:
                msg = Message(
                    id=uuid.uuid4(),
                    interview_id=uuid.UUID(request.interview_id),
                    role="interviewer",
                    content=evaluation.follow_up_question,
                )
                session.add(msg)
                await session.commit()
        else:
            # 下一题：优先从Redis获取上下文，尝试LLM动态生成
            resume_text_ctx = ""
            job_text_ctx = ""
            previous_qs = []
            try:
                redis = await get_redis()
                session_key = f"interview:{request.interview_id}"
                ctx = await redis.hgetall(session_key)
                if ctx:
                    resume_text_ctx = ctx.get("resume_text", "")
                    job_text_ctx = ctx.get("job_text", "")
                    asked = ctx.get("questions_asked", "[]")
                    previous_qs = json.loads(asked) if asked else []
            except Exception:
                pass

            next_q = await _generate_dynamic_question(
                resume_text=resume_text_ctx,
                job_text=job_text_ctx,
                interview_round=interview_round,
                previous_questions=previous_qs,
            )

            if not next_q:
                # 回退到固定题库
                questions = _QUESTION_BANK.get(interview_round, _QUESTION_BANK["tech1"])
                async with get_db_session() as session:
                    msg_result = await session.execute(
                        select(Message).where(Message.interview_id == uuid.UUID(request.interview_id))
                    )
                    msg_count = len([m for m in msg_result.scalars().all() if m.role == "interviewer"])
                next_q = questions[msg_count % len(questions)] if msg_count < len(questions) else None

            if next_q:
                yield f"data: {json.dumps({'type': 'question', 'payload': next_q}, ensure_ascii=False)}\n\n"
                async with get_db_session() as session:
                    msg = Message(
                        id=uuid.uuid4(),
                        interview_id=uuid.UUID(request.interview_id),
                        role="interviewer",
                        content=next_q,
                    )
                    session.add(msg)
                    await session.commit()
                # 更新Redis已问问题列表
                try:
                    redis = await get_redis()
                    session_key = f"interview:{request.interview_id}"
                    previous_qs.append(next_q)
                    await redis.hset(session_key, "questions_asked", json.dumps(previous_qs, ensure_ascii=False))
                except Exception:
                    pass
            else:
                yield f"data: {json.dumps({'type': 'end', 'payload': '面试结束，请查看复盘报告。'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/end", response_model=InterviewEndResponse)
async def end_interview(
    interview_id: str,
    current_user: str = Depends(get_current_user),
):
    async with get_db_session() as session:
        result = await session.execute(select(Interview).where(Interview.id == uuid.UUID(interview_id)))
        interview = result.scalar_one_or_none()
        if not interview or str(interview.user_id) != current_user:
            raise HTTPException(status_code=404, detail="面试不存在")

        interview.status = InterviewStatus.ENDED
        await session.commit()

    return InterviewEndResponse(interview_id=interview_id, status="ended", review_id=None)


@router.get("/{interview_id}/messages")
async def list_messages(interview_id: str, current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(
            select(Message).where(Message.interview_id == uuid.UUID(interview_id)).order_by(Message.created_at)
        )
        messages = result.scalars().all()
        return [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else "",
            }
            for m in messages
        ]
