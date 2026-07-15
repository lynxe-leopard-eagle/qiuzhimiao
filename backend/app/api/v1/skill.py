"""技能图谱模块 API 路由。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.resume import Resume
from app.schemas.skill import SkillDimension, SkillGapAnalysis, SkillGapRequest, SkillRadarResponse, SkillTreeResponse

router = APIRouter(prefix="/skills", tags=["skills"])

_SKILL_DIMENSIONS = {
    "frontend": [
        {"name": "HTML/CSS", "keywords": ["html", "css", "sass", "less", "tailwind", "layout", "responsive"]},
        {"name": "JavaScript/TypeScript", "keywords": ["javascript", "typescript", "es6", "async", "promise", "vue", "react"]},
        {"name": "前端框架", "keywords": ["react", "vue", "angular", "next.js", "nuxt", "redux", "vuex", "pinia"]},
        {"name": "工程化", "keywords": ["webpack", "vite", "rollup", "babel", "jest", "cypress", "storybook"]},
        {"name": "性能优化", "keywords": ["performance", "lazy", "code-splitting", "cache", "bundle", "web-vitals"]},
        {"name": "浏览器原理", "keywords": ["browser", "render", "dom", "event", "reflow", "repaint"]},
    ],
    "backend": [
        {"name": "编程语言", "keywords": ["python", "java", "go", "node", "typescript", "rust", "c++"]},
        {"name": "框架", "keywords": ["fastapi", "flask", "django", "spring", "nestjs", "gin", "express"]},
        {"name": "数据库", "keywords": ["mysql", "postgresql", "redis", "mongodb", "sql", "orm", "query"]},
        {"name": "中间件", "keywords": ["kafka", "rabbitmq", "redis", "nginx", "load-balancing", "cache"]},
        {"name": "微服务", "keywords": ["microservice", "docker", "kubernetes", "k8s", "grpc", "api-gateway"]},
        {"name": "运维", "keywords": ["linux", "shell", "ci/cd", "jenkins", "docker", "prometheus"]},
    ],
    "ai": [
        {"name": "机器学习", "keywords": ["ml", "tensorflow", "pytorch", "scikit-learn", "classification", "regression"]},
        {"name": "深度学习", "keywords": ["deep-learning", "cnn", "rnn", "transformer", "nlp", "computer-vision"]},
        {"name": "大模型", "keywords": ["llm", "chatgpt", "langchain", "prompt", "fine-tune", "embedding"]},
        {"name": "数据处理", "keywords": ["pandas", "numpy", "spark", "data-analysis", "feature-engineering"]},
        {"name": "MLOps", "keywords": ["mlops", "model-deployment", "mlflow", "wandb", "docker", "kubernetes"]},
        {"name": "数学基础", "keywords": ["math", "calculus", "linear-algebra", "probability", "statistics", "optimization"]},
    ],
    "test": [
        {"name": "功能测试", "keywords": ["testing", "manual", "test-case", "bug", "defect", "regression"]},
        {"name": "自动化测试", "keywords": ["automation", "selenium", "playwright", "cypress", "pytest", "unittest"]},
        {"name": "接口测试", "keywords": ["api-testing", "postman", "jmeter", "http", "rest", "graphql"]},
        {"name": "性能测试", "keywords": ["performance", "load", "stress", "jmeter", "locust", "qps"]},
        {"name": "测试管理", "keywords": ["test-management", "jira", "testrail", "confluence", "ci/cd"]},
        {"name": "质量保障", "keywords": ["qa", "quality", "bug-tracking", "metrics", "process", "review"]},
    ],
    "product": [
        {"name": "需求分析", "keywords": ["requirements", "user-research", "analysis", "prd", "story"]},
        {"name": "产品设计", "keywords": ["design", "wireframe", "prototype", "figma", "sketch", "ux"]},
        {"name": "项目管理", "keywords": ["project", "agile", "scrum", "kanban", "jira", "milestone"]},
        {"name": "数据分析", "keywords": ["data", "metrics", "analytics", "sql", "excel", "dashboard"]},
        {"name": "用户增长", "keywords": ["growth", "user", "acquisition", "retention", "engagement"]},
        {"name": "沟通协调", "keywords": ["communication", "stakeholder", "meeting", "presentation"]},
    ],
    "default": [
        {"name": "专业技能", "keywords": ["skill", "expertise", "technical", "knowledge", "ability"]},
        {"name": "项目经验", "keywords": ["project", "experience", "delivery", "team", "leadership"]},
        {"name": "沟通能力", "keywords": ["communication", "presentation", "interview", "coordination"]},
        {"name": "学习能力", "keywords": ["learning", "adaptation", "growth", "new-tech", "self-study"]},
        {"name": "问题解决", "keywords": ["problem", "solution", "troubleshooting", "critical-thinking"]},
        {"name": "职业素养", "keywords": ["professional", "attitude", "responsibility", "teamwork"]},
    ],
}

_JD_SKILL_MAP = {
    "前端": "frontend",
    "后端": "backend",
    "AI": "ai",
    "测试": "test",
    "产品": "product",
    "开发": "backend",
    "工程师": "backend",
    "机器学习": "ai",
    "深度学习": "ai",
    "数据": "ai",
    "算法": "ai",
    "自动化": "test",
    "QA": "test",
}


def _detect_job_domain(job_description: str) -> str:
    job_lower = job_description.lower() if job_description else ""
    for keyword, domain in _JD_SKILL_MAP.items():
        if keyword.lower() in job_lower:
            return domain
    return "default"


def _analyze_skills(raw_text: str, domain: str) -> list[SkillDimension]:
    text_lower = raw_text.lower() if raw_text else ""
    dimensions = _SKILL_DIMENSIONS.get(domain, _SKILL_DIMENSIONS["default"])
    
    result = []
    for dim in dimensions:
        matched = [kw for kw in dim["keywords"] if kw in text_lower]
        score = min(100, len(matched) * 20 + 20 if matched else 10)
        description = f"检测到 {len(matched)} 个相关关键词" if matched else "需补充相关技能描述"
        
        result.append(SkillDimension(
            name=dim["name"],
            score=score,
            max_score=100,
            description=description,
            keywords=matched,
        ))
    
    return result


@router.get("/radar", response_model=SkillRadarResponse)
async def get_skill_radar(
    resume_id: str | None = None,
    job_description: str | None = None,
    current_user: str = Depends(get_current_user),
):
    raw_text = ""
    
    if resume_id:
        async with get_db_session() as session:
            result = await session.execute(select(Resume).where(Resume.id == uuid.UUID(resume_id)))
            resume = result.scalar_one_or_none()
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")
            if str(resume.user_id) != current_user:
                raise HTTPException(status_code=403, detail="无权访问")
            parsed = resume.parsed_data or {}
            raw_text = parsed.get("raw_text", "")
    
    domain = _detect_job_domain(job_description or "")
    dimensions = _analyze_skills(raw_text, domain)
    
    avg_score = sum(d.score for d in dimensions) / len(dimensions) if dimensions else 0
    job_fit_score = round(avg_score, 1)
    
    weak_dimensions = sorted(dimensions, key=lambda d: d.score)[:3]
    suggested_skills = [f"强化 {d.name}（当前 {d.score} 分）" for d in weak_dimensions]
    
    improvement_path = []
    if job_fit_score < 60:
        improvement_path.extend([
            "补充核心技能关键词到项目描述中",
            "添加量化成果数据增强说服力",
            "完善项目经验模块",
        ])
    elif job_fit_score < 80:
        improvement_path.extend([
            "优化技能描述的深度和广度",
            "添加更多技术细节和实现方案",
            "准备技能相关的面试题",
        ])
    else:
        improvement_path.append("技能覆盖良好，保持更新即可")
    
    return SkillRadarResponse(
        dimensions=dimensions,
        job_fit_score=job_fit_score,
        suggested_skills=suggested_skills,
        improvement_path=improvement_path,
    )


@router.get("/tree", response_model=SkillTreeResponse)
async def get_skill_tree(domain: str = "default", current_user: str = Depends(get_current_user)):
    dimensions = _SKILL_DIMENSIONS.get(domain, _SKILL_DIMENSIONS["default"])
    
    categories = []
    for dim in dimensions:
        categories.append({
            "name": dim["name"],
            "skills": dim["keywords"],
        })
    
    return SkillTreeResponse(categories=categories)


@router.post("/gap", response_model=SkillGapAnalysis)
async def analyze_skill_gap(
    request: SkillGapRequest,
    current_user: str = Depends(get_current_user),
):
    resume_id = request.resume_id
    job_description = request.job_description
    async with get_db_session() as session:
        result = await session.execute(select(Resume).where(Resume.id == uuid.UUID(resume_id)))
        resume = result.scalar_one_or_none()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        if str(resume.user_id) != current_user:
            raise HTTPException(status_code=403, detail="无权访问")
        
        parsed = resume.parsed_data or {}
        raw_text = parsed.get("raw_text", "")
    
    resume_lower = raw_text.lower()
    job_lower = job_description.lower()
    
    domain = _detect_job_domain(job_description)
    dimensions = _SKILL_DIMENSIONS.get(domain, _SKILL_DIMENSIONS["default"])
    
    required_skills = []
    for dim in dimensions:
        for kw in dim["keywords"]:
            if kw in job_lower and kw not in required_skills:
                required_skills.append(kw)
    
    matched_skills = [kw for kw in required_skills if kw in resume_lower]
    missing_skills = [kw for kw in required_skills if kw not in resume_lower]
    
    gap_count = len(missing_skills)
    if gap_count == 0:
        gap_description = "技能匹配度很高，建议重点准备面试中对技能深度的考察"
    elif gap_count <= 3:
        gap_description = f"存在 {gap_count} 个关键技能缺口，建议针对性补充"
    elif gap_count <= 6:
        gap_description = f"存在 {gap_count} 个技能缺口，需要系统性补强"
    else:
        gap_description = f"技能缺口较多（{gap_count}个），建议重新评估岗位匹配度或制定详细学习计划"
    
    learning_suggestions = []
    if missing_skills:
        learning_suggestions.append(f"重点学习：{', '.join(missing_skills[:5])}")
        learning_suggestions.append("在简历项目经验中补充相关技能的实践描述")
        learning_suggestions.append("准备相关技能的面试题和深度讲解")
    
    return SkillGapAnalysis(
        required_skills=required_skills,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        gap_description=gap_description,
        learning_suggestions=learning_suggestions,
    )
