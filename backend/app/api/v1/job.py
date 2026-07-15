"""岗位模块 API 路由。"""

from __future__ import annotations

import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

import hashlib
import logging

from app.core.database import get_db_session
from app.core.redis_cache import get_cache, set_cache
from app.core.security import get_current_user
from app.models.job import Job
from app.models.resume import Resume

logger = logging.getLogger(__name__)
from app.schemas.job import (
    JobCreateRequest,
    JobResponse,
    JobAnalyzeRequest,
    JobAnalyzeResponse,
    MatchingRequest,
    MatchingResponse,
    MatchReasons,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


_TECH_SKILLS = {
    "python", "java", "go", "golang", "c++", "c", "javascript", "js", "typescript",
    "ts", "rust", "php", "ruby", "swift", "kotlin", "scala", "c#", ".net",
    "react", "vue", "angular", "node", "nodejs", "nextjs", "nuxt",
    "django", "flask", "fastapi", "spring", "springboot", "express", "laravel",
    "rails", "gin", "echo",
    "mysql", "postgresql", "postgres", "mongodb", "mongo", "redis", "memcached",
    "elasticsearch", "es", "kafka", "rabbitmq", "rocketmq", "pulsar", "zookeeper",
    "etcd", "consul", "hbase", "cassandra", "clickhouse", "hive", "hadoop", "spark",
    "flink", "storm",
    "docker", "kubernetes", "k8s", "aws", "gcp", "azure", "aliyun", "tencent",
    "linux", "unix", "git", "svn", "jenkins", "gitlab", "github", "circleci",
    "nginx", "apache", "envoy", "istio", "prometheus", "grafana", "elk",
    "微服务", "分布式", "高并发", "高可用", "负载均衡", "消息队列", "缓存",
    "机器学习", "深度学习", "自然语言处理", "nlp", "计算机视觉", "cv",
    "数据分析", "数据挖掘", "推荐系统", "大模型", "llm",
    "sql", "nosql", "restful", "rest", "graphql", "rpc", "grpc", "thrift",
    "tcp", "http", "https", "udp",
    "ci/cd", "devops", "agile", "scrum",
}


@router.post("", response_model=JobResponse)
async def create_job(
    request: JobCreateRequest,
    current_user: str = Depends(get_current_user),
):
    job = Job(
        id=uuid.uuid4(),
        user_id=uuid.UUID(current_user),
        title=request.title,
        company=request.company,
        description=request.description,
        requirements=request.requirements,
        category=request.category,
    )
    async with get_db_session() as session:
        session.add(job)
        await session.commit()
    return JobResponse(
        id=str(job.id),
        title=job.title,
        company=job.company,
        description=job.description,
        requirements=job.requirements,
        category=job.category,
    )


@router.get("", response_model=list[JobResponse])
async def list_jobs(current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(select(Job).where(Job.user_id == uuid.UUID(current_user)))
        jobs = result.scalars().all()
        return [
            JobResponse(
                id=str(j.id),
                title=j.title,
                company=j.company,
                description=j.description,
                requirements=j.requirements,
                category=j.category,
            )
            for j in jobs
        ]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(select(Job).where(Job.id == uuid.UUID(job_id)))
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="岗位不存在")
        if str(job.user_id) != current_user:
            raise HTTPException(status_code=403, detail="无权访问")
        return JobResponse(
            id=str(job.id),
            title=job.title,
            company=job.company,
            description=job.description,
            requirements=job.requirements,
            category=job.category,
        )


@router.post("/analyze", response_model=JobAnalyzeResponse)
async def analyze_job(
    request: JobAnalyzeRequest,
    current_user: str = Depends(get_current_user),
):
    # Redis缓存
    jd_hash = hashlib.md5(request.job_description.encode()).hexdigest()[:12]
    cache_key = f"job:analyze:{jd_hash}"
    cached = await get_cache(cache_key)
    if cached:
        logger.debug("岗位分析缓存命中: %s", cache_key)
        return JobAnalyzeResponse(**cached)

    jd_text = request.job_description
    jd_lower = jd_text.lower()

    title = request.title or ""
    company = request.company or ""

    jd_words = set(re.findall(r"[a-zA-Z+#]+|\d+年|[\u4e00-\u9fa5]{2,}", jd_lower))

    jd_skills = sorted(_TECH_SKILLS & jd_words)

    core_skills = []
    bonus_skills = []
    in_required_section = False
    in_bonus_section = False
    for line in jd_text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if any(kw in line_stripped for kw in ["任职要求", "岗位要求", "职位要求", "任职资格", "基本要求", "要求"]):
            in_required_section = True
            in_bonus_section = False
            continue
        if any(kw in line_stripped for kw in ["加分项", "优先考虑", "优先", "额外", "bonus", "加分"]):
            in_required_section = False
            in_bonus_section = True
            continue
        if any(kw in line_stripped for kw in ["岗位职责", "工作职责", "工作内容", "职责描述", "你将做什么"]):
            in_required_section = False
            in_bonus_section = False
            continue

        line_skills = [s for s in jd_skills if s in line_stripped.lower()]
        if line_skills:
            if in_bonus_section:
                bonus_skills.extend(line_skills)
            else:
                core_skills.extend(line_skills)

    core_skills = sorted(set(core_skills)) if core_skills else jd_skills[:10]
    bonus_skills = sorted(set(bonus_skills)) if bonus_skills else jd_skills[10:16]

    responsibilities = []
    hard_requirements = []
    in_resp_section = False
    in_req_section = False
    for line in jd_text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if any(kw in line_stripped for kw in ["岗位职责", "工作职责", "工作内容", "职责描述", "你将做什么"]):
            in_resp_section = True
            in_req_section = False
            continue
        if any(kw in line_stripped for kw in ["任职要求", "岗位要求", "职位要求", "任职资格", "基本要求"]):
            in_resp_section = False
            in_req_section = True
            continue
        if line_stripped.startswith(("- ", "• ", "· ", "* ", "1.", "2.", "3.", "4.", "5.")):
            if in_resp_section and len(responsibilities) < 8:
                clean_line = re.sub(r"^[-•·*\d.]+\s*", "", line_stripped).strip()
                if clean_line:
                    responsibilities.append(clean_line)
            elif in_req_section and len(hard_requirements) < 10:
                clean_line = re.sub(r"^[-•·*\d.]+\s*", "", line_stripped).strip()
                if clean_line:
                    hard_requirements.append(clean_line)

    if not responsibilities:
        for line in jd_text.splitlines():
            line_stripped = line.strip()
            if line_stripped.startswith(("- ", "• ", "· ", "* ")) and len(responsibilities) < 5:
                clean_line = re.sub(r"^[-•·*]+\s*", "", line_stripped).strip()
                if clean_line and len(clean_line) > 10:
                    responsibilities.append(clean_line)

    if not hard_requirements:
        for line in jd_text.splitlines():
            line_stripped = line.strip()
            if any(kw in line_stripped for kw in ["年以上", "经验", "学历", "本科", "硕士", "熟练", "熟悉", "掌握"]):
                if len(hard_requirements) < 6 and len(line_stripped) > 8:
                    hard_requirements.append(line_stripped)

    experience_required = ""
    exp_match = re.search(r"(\d+)\s*[-~到]\s*(\d+)\s*年", jd_text)
    if exp_match:
        experience_required = f"{exp_match.group(1)}-{exp_match.group(2)}年"
    else:
        exp_match = re.search(r"(\d+)\s*年以上", jd_text)
        if exp_match:
            experience_required = f"{exp_match.group(1)}年以上"
        elif "应届" in jd_text or "校招" in jd_text:
            experience_required = "应届生"
        elif "3年" in jd_text:
            experience_required = "3-5年"
        elif "5年" in jd_text:
            experience_required = "5-10年"

    education_required = ""
    if "博士" in jd_text:
        education_required = "博士"
    elif "硕士" in jd_text:
        education_required = "硕士"
    elif "本科" in jd_text:
        education_required = "本科"
    elif "大专" in jd_text or "专科" in jd_text:
        education_required = "大专"
    else:
        education_required = "本科及以上"

    job_level = ""
    if "资深" in jd_text or "高级" in jd_text or "专家" in jd_text or "架构师" in jd_text:
        job_level = "高级/专家"
    elif "中级" in jd_text:
        job_level = "中级"
    elif "初级" in jd_text or "实习" in jd_text or "校招" in jd_text or "应届" in jd_text:
        job_level = "初级/应届生"
    else:
        job_level = "中级"

    salary_range = ""
    salary_match = re.search(r"(\d+)[-~到](\d+)\s*[kK千]", jd_text)
    if salary_match:
        salary_range = f"{salary_match.group(1)}-{salary_match.group(2)}K"
    else:
        salary_match = re.search(r"(\d+)\s*[kK千]\s*[-~到]\s*(\d+)\s*[kK千]", jd_text)
        if salary_match:
            salary_range = f"{salary_match.group(1)}-{salary_match.group(2)}K"
        elif "高薪" in jd_text or "有竞争力" in jd_text:
            salary_range = "面议/有竞争力"

    difficulty_score = 50
    if job_level == "高级/专家":
        difficulty_score += 25
    elif job_level == "中级":
        difficulty_score += 10
    if experience_required and "5年" in experience_required:
        difficulty_score += 10
    elif experience_required and "3年" in experience_required:
        difficulty_score += 5
    if len(core_skills) > 8:
        difficulty_score += 10
    elif len(core_skills) > 5:
        difficulty_score += 5
    if education_required == "硕士":
        difficulty_score += 5
    elif education_required == "博士":
        difficulty_score += 10
    difficulty_score = min(100, difficulty_score)

    market_demand = ""
    hot_skills = {"python", "java", "go", "react", "vue", "typescript", "大模型", "llm", "ai", "人工智能", "机器学习", "深度学习", "数据分析", "云原生", "k8s", "微服务"}
    hot_count = len(_TECH_SKILLS & jd_words & hot_skills)
    if hot_count >= 4:
        market_demand = "需求旺盛"
    elif hot_count >= 2:
        market_demand = "需求稳定"
    else:
        market_demand = "需求一般"

    career_outlook = ""
    if any(kw in jd_lower for kw in ["ai", "大模型", "llm", "人工智能", "机器学习", "深度学习", "aigc"]):
        career_outlook = "前景广阔，AI 时代核心岗位"
    elif any(kw in jd_lower for kw in ["云原生", "k8s", "kubernetes", "微服务", "分布式"]):
        career_outlook = "发展稳定，企业数字化转型刚需"
    elif any(kw in jd_lower for kw in ["数据", "数据分析", "数据挖掘", "大数据"]):
        career_outlook = "数据驱动时代，持续增长"
    else:
        career_outlook = "发展稳定，技术积累可迁移"

    summary_parts = []
    if title:
        summary_parts.append(f"这是一份{title}岗位")
    else:
        summary_parts.append("这是一份技术岗位")
    if company:
        summary_parts.append(f"来自{company}")
    if job_level:
        summary_parts.append(f"定位{job_level}")
    if experience_required:
        summary_parts.append(f"要求{experience_required}工作经验")
    if education_required:
        summary_parts.append(f"学历要求{education_required}")
    if core_skills:
        summary_parts.append(f"核心技术栈包括{''.join(core_skills[:5])}等")
    summary = "，".join(summary_parts) + "。"

    result = JobAnalyzeResponse(
        title=title,
        company=company,
        job_level=job_level,
        experience_required=experience_required,
        education_required=education_required,
        salary_range=salary_range,
        core_skills=core_skills,
        bonus_skills=bonus_skills,
        responsibilities=responsibilities,
        hard_requirements=hard_requirements,
        difficulty_score=difficulty_score,
        market_demand=market_demand,
        career_outlook=career_outlook,
        summary=summary,
    )
    await set_cache(cache_key, result.model_dump(), ttl=3600)
    return result


@router.post("/matching", response_model=MatchingResponse)
async def analyze_matching(
    request: MatchingRequest,
    current_user: str = Depends(get_current_user),
):
    async with get_db_session() as session:
        result = await session.execute(select(Resume).where(Resume.id == uuid.UUID(request.resume_id)))
        resume = result.scalar_one_or_none()
        if not resume or str(resume.user_id) != current_user:
            raise HTTPException(status_code=404, detail="简历不存在")

        jd_text = ""
        job_id = None
        if request.job_id:
            job_result = await session.execute(select(Job).where(Job.id == uuid.UUID(request.job_id)))
            job = job_result.scalar_one_or_none()
            if job and str(job.user_id) == current_user:
                jd_text = job.description or ""
                job_id = str(job.id)
        if request.job_description:
            jd_text = request.job_description

        # Redis缓存
        jd_hash = hashlib.md5(jd_text.encode()).hexdigest()[:8] if jd_text else "none"
        cache_key = f"job:match:{request.resume_id}:{job_id or jd_hash}"
        cached = await get_cache(cache_key)
        if cached:
            logger.debug("匹配分析缓存命中: %s", cache_key)
            return MatchingResponse(**cached)

        raw_text = resume.parsed_data.get("raw_text", "") if resume.parsed_data else ""
        resume_lower = raw_text.lower()
        jd_lower = jd_text.lower()

        # 提取 JD 关键词（简单分词）
        jd_words = set(re.findall(r"[a-zA-Z+#]+|\d+年|[\u4e00-\u9fa5]{2,}", jd_lower))
        resume_words = set(re.findall(r"[a-zA-Z+#]+|\d+年|[\u4e00-\u9fa5]{2,}", resume_lower))

        matched = jd_words & resume_words
        total = jd_words if jd_words else set(["placeholder"])
        ratio = len(matched) / len(total)

        hard_requirements = []
        skill_keywords = []
        for line in jd_text.splitlines():
            if "要求" in line or "必备" in line or "必须" in line:
                hard_requirements.append(line.strip())
            elif any(kw in line.lower() for kw in ["python", "java", "go", "c++", "sql", "docker", "k8s", "aws"]):
                skill_keywords.append(line.strip())

        hard_score = min(100, int(ratio * 100) + 20)
        skill_score = min(100, int(ratio * 100) + 10)
        project_score = 70 if "项目" in resume_lower or "project" in resume_lower else 40
        industry_score = 60

        overall = int((hard_score + skill_score + project_score + industry_score) / 4)

        strengths = []
        weaknesses = []
        gaps = []

        if hard_score >= 70:
            strengths.append("硬性条件匹配度较好")
        else:
            weaknesses.append("硬性条件匹配度一般")
            gaps.append("核对 JD 中的硬性要求（学历、年限、证书）")

        if skill_score >= 70:
            strengths.append("技能关键词匹配")
        else:
            weaknesses.append("技能关键词覆盖不足")
            gaps.append("在简历中补充 JD 中的核心技术栈")

        if project_score < 60:
            gaps.append("补充与岗位相关的项目经验描述")

        suggestion = "建议优先补充技能关键词和项目量化成果，再优化行业术语匹配度。"

        # 生成 match_reasons：基于技能关键词的匹配分析
        jd_skills = _TECH_SKILLS & jd_words
        resume_skills = _TECH_SKILLS & resume_words
        matched_skills = jd_skills & resume_skills
        extra_skills = resume_skills - jd_skills
        missing_skills = jd_skills - resume_skills

        why_matched = []
        if matched_skills:
            why_matched.append(
                "简历中包含 JD 要求的核心技能：" + "、".join(sorted(matched_skills)[:6])
            )
        if hard_score >= 70:
            why_matched.append("硬性条件（学历、工作年限等）基本符合岗位要求")
        if skill_score >= 70:
            why_matched.append("技能关键词覆盖度较高，与岗位技术栈匹配")
        if project_score >= 70:
            why_matched.append("具备相关项目经验，能够快速胜任岗位职责")
        if "项目" in resume_lower or "project" in resume_lower:
            why_matched.append("简历中包含可量化的项目经验描述")
        if not why_matched:
            why_matched.append("简历与岗位存在基础匹配，建议进一步优化关键词")

        potential_advantages = []
        if extra_skills:
            potential_advantages.append(
                "掌握 JD 之外的技能：" + "、".join(sorted(extra_skills)[:6]) + "，可带来额外价值"
            )
        if len(resume_skills) > len(jd_skills):
            potential_advantages.append("技能栈广度超出岗位要求，具备技术深度拓展空间")
        if any(kw in resume_lower for kw in ["架构", "设计", "主导", "负责"]):
            potential_advantages.append("具备架构设计或主导经验，有潜力承担更高级别职责")
        if any(kw in resume_lower for kw in ["优化", "提升", "改进", "性能"]):
            potential_advantages.append("有性能优化或流程改进经验，能够持续提升团队效率")
        if not potential_advantages:
            potential_advantages.append("当前简历与岗位要求高度贴合，暂无明显超出项")

        needs_improvement = []
        if missing_skills:
            needs_improvement.append(
                "JD 要求但简历中未体现的技能：" + "、".join(sorted(missing_skills)[:6])
            )
        if hard_score < 70:
            needs_improvement.append("硬性条件匹配度不足，建议核对学历、年限、证书等要求")
        if skill_score < 70:
            needs_improvement.append("技能关键词覆盖不足，建议在简历中突出核心技术栈")
        if project_score < 60:
            needs_improvement.append("项目经验描述偏少，建议补充与岗位相关的项目细节和量化成果")
        if not needs_improvement:
            needs_improvement.append("当前匹配度较好，建议持续关注行业新技术动态")

        why_match_text = "；".join(why_matched) if why_matched else "简历与岗位存在基础匹配"

        match_reasons = MatchReasons(
            why_match=why_match_text,
            advantages=potential_advantages,
            gaps=needs_improvement,
        )

        result = MatchingResponse(
            resume_id=request.resume_id,
            job_id=job_id,
            match_score=overall,
            dimensions={
                "硬性要求": hard_score,
                "技能关键词": skill_score,
                "项目经验": project_score,
                "行业经验": industry_score,
            },
            strengths=strengths,
            weaknesses=weaknesses,
            gaps=gaps,
            suggestion=suggestion,
            match_reasons=match_reasons,
        )
        await set_cache(cache_key, result.model_dump(), ttl=3600)
        return result
