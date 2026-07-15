"""简历模块 API 路由。"""

from __future__ import annotations

import hashlib
import re
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select

import json
import logging

from app.core.database import get_db_session
from app.core.file_validator import FileValidator, validate_upload_file
from app.core.minio import upload_file
from app.core.redis_cache import delete_cache, delete_cache_pattern, get_cache, set_cache
from app.core.security import get_current_user
from app.models.resume import Resume, ResumeStatus
from app.schemas.resume import ATSAnalysis, DiagnosisRequest, DiagnosisResponse, ParseStatus, ResumeUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _extract_phone(text: str) -> str | None:
    match = re.search(r"1[3-9]\d{9}", text)
    return match.group() if match else None


def _extract_email(text: str) -> str | None:
    match = re.search(r"[\w.-]+@[\w.-]+\.\w+", text)
    return match.group() if match else None


def _get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    ext = filename.rsplit(".", 1)[-1].lower()
    return f".{ext}" if ext.isalnum() else ""


async def _llm_parse_resume(raw_text: str) -> dict:
    """使用 LLM 对简历进行结构化解析。

    提取：姓名、教育背景、技能列表、项目经验、工作经历。
    当 LLM 不可用时返回空字典。
    """
    if not raw_text or len(raw_text) < 50:
        return {}

    try:
        from app.core.llm_service import get_llm_service
        llm = get_llm_service()
        if not llm.is_real_llm_available:
            return {}

        system_prompt = (
            "你是一位专业的简历解析助手。请将以下简历文本解析为结构化JSON。\n"
            "必须严格按以下JSON格式输出（不要添加任何其他文字）：\n"
            "{\n"
            '  "name": "候选人姓名",\n'
            '  "education": [{\n'
            '    "school": "学校名称",\n'
            '    "degree": "学历",\n'
            '    "major": "专业",\n'
            '    "duration": "起止时间"\n'
            '  }],\n'
            '  "skills": ["技能1", "技能2", ...],\n'
            '  "work_experience": [{\n'
            '    "company": "公司名称",\n'
            '    "position": "职位",\n'
            '    "duration": "起止时间",\n'
            '    "highlights": ["亮点1", "亮点2"]\n'
            '  }],\n'
            '  "projects": [{\n'
            '    "name": "项目名称",\n'
            '    "description": "项目描述",\n'
            '    "technologies": ["技术1", "技术2"],\n'
            '    "highlights": ["亮点1", "亮点2"]\n'
            '  }]\n'
            "}\n"
            "如果某项信息无法从简历中提取，使用空数组或空字符串。"
        )

        result = await llm.chat(
            [{"role": "user", "content": raw_text[:3000]}],
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=1024,
        )

        # 尝试从结果中提取JSON
        text = result.strip()
        # 去除可能的markdown代码块
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # 找到第一个 { 和最后一个 }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]

        parsed = json.loads(text)
        if isinstance(parsed, dict):
            logger.info("LLM简历结构化解析成功")
            return parsed
    except Exception as e:
        logger.warning("LLM简历结构化解析失败: %s", e)

    return {}


# ATS 常见技术关键词库
_ATS_KEYWORDS = {
    # 编程语言
    "python", "java", "javascript", "typescript", "go", "c++", "c#", "rust", "ruby", "php", "swift", "kotlin", "scala", "objective-c", "dart", "lua", "perl",
    # 前端
    "react", "vue", "angular", "next.js", "nuxt", "html", "css", "tailwind", "sass", "less", "webpack", "vite", "rollup", "babel", "jest", "cypress", "storybook", "redux", "vuex", "pinia", "zustand", "react-query", "tanstack",
    # 后端框架
    "spring", "springboot", "django", "flask", "fastapi", "express", "nestjs", "gin", "echo", "koa", "sails", "laravel", "symfony", "rails", "grails", "quarkus", "micronaut",
    # 数据库
    "mysql", "postgresql", "redis", "mongodb", "elasticsearch", "sqlite", "oracle", "sqlserver", "dynamodb", "cassandra", "cockroachdb", "tidb", "clickhouse", "neo4j", "memcached",
    # 云和运维
    "docker", "kubernetes", "k8s", "aws", "azure", "gcp", "aliyun", "tencent", "huawei", "ci/cd", "jenkins", "gitlab", "github", "actions", "terraform", "ansible", "helm", "istio", "prometheus", "grafana", "elk", "loki",
    # 消息队列
    "kafka", "rabbitmq", "rocketmq", "pulsar", "activemq", "mqtt",
    # 数据和AI
    "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "spark", "hadoop", "flink", "airflow", "dbt", "presto", "hive", "hbase", "impala", "kafka streams", "mlflow", "wandb", "xgboost", "lightgbm", "transformers", "langchain", "llm", "大模型",
    # 方法论
    "微服务", "分布式", "高并发", "中间件", "负载均衡", "缓存", "消息队列", "restful", "graphql", "rpc", "grpc", "thrift", "protobuf", "json", "xml", "api", "websocket", "serverless", "faas", "saas", "paas", "iaas",
    # 软技能关键词
    "领导力", "团队协作", "项目管理", "敏捷", "scrum", "kanban", "沟通", "复盘", "优化", "创新", "问题解决", "抗压", "学习能力", "责任心", "执行力", "逻辑思维", "分析能力", "文档编写", "代码审查", "技术分享",
    # 安全
    "oauth", "jwt", "oauth2", "sso", "https", "ssl", "tls", "加密", "解密", "安全", "渗透测试", "漏洞", "防火墙", "waf", "ddos",
    # 网络
    "tcp", "udp", "http", "https", "websocket", "dns", "cdn", "nginx", "负载均衡", "反向代理", "网关", "api gateway", "服务发现", "注册中心",
    # 操作系统
    "linux", "unix", "centos", "ubuntu", "debian", "redhat", "windows", "macos", "shell", "bash", "powershell",
}

# ATS 期望的简历核心模块
_ATS_SECTIONS = {
    "education": ["教育", "学历", "学校", "university", "education", "bachelor", "master", "phd", "本科", "硕士", "博士"],
    "experience": ["工作经历", "实习", "experience", "work", "internship", "工作经验", "实习经历"],
    "projects": ["项目经历", "项目经验", "project", "projects", "项目"],
    "skills": ["技能", "skill", "skills", "技术栈", "技术能力", "programming"],
    "contact": ["联系方式", "电话", "邮箱", "email", "phone", "contact", "手机"],
}


def _run_ats_analysis(parsed_data: dict, raw_text: str, jd_text: str | None = None) -> ATSAnalysis:
    """执行 ATS 兼容性分析。"""
    text_lower = raw_text.lower() if raw_text else ""
    
    # 1. 关键词覆盖分析
    detected = sorted([kw for kw in _ATS_KEYWORDS if kw in text_lower])
    
    missing_keywords = []
    if jd_text:
        jd_lower = jd_text.lower()
        jd_keywords = set()
        for kw in _ATS_KEYWORDS:
            if kw in jd_lower:
                jd_keywords.add(kw)
        missing_keywords = sorted(jd_keywords - set(detected))
        keyword_coverage = len(set(detected) & jd_keywords) / len(jd_keywords) * 100 if jd_keywords else 100.0
    else:
        keyword_coverage = len(detected) / 15 * 100 if len(detected) < 15 else 100.0
        missing_keywords = sorted(set(list(_ATS_KEYWORDS)[:15]) - set(detected))
    
    keyword_coverage = min(keyword_coverage, 100.0)
    
    # 2. 格式问题检测
    format_issues = []
    if raw_text:
        lines = raw_text.split("\n")
        avg_line_len = sum(len(l) for l in lines) / len(lines) if lines else 0
        if avg_line_len > 200:
            format_issues.append("段落过长，建议拆分为短句以便 ATS 解析")
        if len(raw_text) < 200:
            format_issues.append("简历内容过少，建议补充至 500 字以上")
        if len(raw_text) > 3000:
            format_issues.append("简历内容过长，建议精简至 1-2 页")
        special_chars = sum(1 for c in raw_text if c in "│┃┌┐└┘├┤┬┴┼")
        if special_chars > 5:
            format_issues.append("包含表格框线字符，可能导致 ATS 解析异常")
        if "http" not in text_lower and "www" not in text_lower and "@" not in text_lower:
            format_issues.append("缺少可识别的链接或邮箱信息")
        
        # 检测图片相关字符（ATS 无法读取图片）
        image_indicators = ["[图片]", "[图]", "image", "picture", "photo"]
        if any(ind in text_lower for ind in image_indicators):
            format_issues.append("检测到图片引用，ATS 系统无法解析图片内容，请确保关键信息以文本形式呈现")
        
        # 检测特殊字体或格式
        if any(ch in raw_text for ch in "🎨🎯🚀💡🔥💪🌟⚡💻📊📈"):
            format_issues.append("包含 emoji 表情符号，部分 ATS 系统可能无法正确处理")
    else:
        format_issues.append("简历文本为空，无法解析")
    
    # 3. 模块完整性检测
    missing_sections = []
    for section, keywords in _ATS_SECTIONS.items():
        if not any(kw in text_lower for kw in keywords):
            missing_sections.append(section)
    
    # 4. 量化指标检测
    quantify_score = 0
    quantify_issues = []
    if raw_text:
        numbers = re.findall(r"\d+", raw_text)
        if len(numbers) >= 5:
            quantify_score = 100
        elif len(numbers) >= 2:
            quantify_score = 60
            quantify_issues.append("量化数据较少，建议添加更多数字指标（如用户量、QPS、性能提升百分比等）")
        else:
            quantify_score = 20
            quantify_issues.append("缺少量化数据，使用具体数字描述成果更有说服力")
    
    # 5. 综合评分
    section_score = (5 - len(missing_sections)) / 5 * 30
    keyword_score = keyword_coverage / 100 * 30
    format_score = (3 - min(len(format_issues), 3)) / 3 * 25
    quantify_score_normalized = quantify_score / 100 * 15
    overall = round(section_score + keyword_score + format_score + quantify_score_normalized, 1)
    overall = min(overall, 100.0)
    
    # 6. 优化建议
    recommendations = []
    if missing_sections:
        section_names = {"education": "教育背景", "experience": "工作/实习经历", "projects": "项目经验", "skills": "技能列表", "contact": "联系方式"}
        for s in missing_sections:
            recommendations.append(f"补充{section_names.get(s, s)}模块，ATS 系统依赖模块化信息进行分类")
    if missing_keywords:
        top_missing = missing_keywords[:5]
        recommendations.append(f"增加以下关键词的覆盖：{', '.join(top_missing)}")
    if format_issues:
        recommendations.extend(format_issues)
    if quantify_issues:
        recommendations.extend(quantify_issues)
    if keyword_coverage < 60:
        recommendations.append("关键词覆盖率较低，建议根据目标岗位 JD 调整技术关键词密度")
    if len(detected) > 30:
        recommendations.append("关键词数量较多，建议聚焦核心技能，避免堆砌")
    if not recommendations:
        recommendations.append("简历 ATS 兼容性良好，建议定期更新以匹配最新岗位需求")
    
    return ATSAnalysis(
        overall_score=overall,
        keyword_coverage=round(keyword_coverage, 1),
        format_issues=format_issues,
        missing_sections=missing_sections,
        detected_keywords=detected,
        missing_keywords=missing_keywords,
        recommendations=recommendations,
    )


@router.get("", response_model=list[ResumeUploadResponse])
async def list_resumes(
    current_user: str = Depends(get_current_user),
):
    async with get_db_session() as session:
        result = await session.execute(
            select(Resume).where(Resume.user_id == current_user).order_by(Resume.created_at.desc())
        )
        resumes = result.scalars().all()
        return [ResumeUploadResponse(
            id=str(r.id),
            original_filename=r.original_filename,
            status=r.status,
            parse_method=r.parse_method,
            confidence=r.confidence,
        ) for r in resumes]


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    file_bytes = await file.read()

    # 先进行基础文件信息校验（扩展名、MIME、大小、文件名、路径遍历）
    validate_upload_file(file.filename or "", file.content_type or "", len(file_bytes))

    # 再进行内容类型深度校验
    validation = FileValidator.validate(file_bytes, file.filename or "unknown", file.content_type or "")
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.error)

    resume_id = str(uuid.uuid4())
    ext = _get_extension(file.filename or "")
    minio_key = f"resumes/{current_user}/{resume_id}{ext}"

    await upload_file(minio_key, file_bytes, validation.detected_mime)

    # 模拟解析（MVP：直接读取文本）
    raw_text = ""
    if validation.detected_mime == "text/plain":
        raw_text = file_bytes.decode("utf-8", errors="ignore")
    elif validation.detected_mime == "application/pdf":
        try:
            import pdfplumber
            from io import BytesIO
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            raw_text = ""
    elif validation.detected_mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            from docx import Document
            from io import BytesIO
            doc = Document(BytesIO(file_bytes))
            raw_text = "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            raw_text = ""

    phone = _extract_phone(raw_text)
    email = _extract_email(raw_text)

    # 使用LLM进行结构化解析
    structured = await _llm_parse_resume(raw_text)

    resume = Resume(
        id=uuid.UUID(resume_id),
        user_id=uuid.UUID(current_user),
        original_filename=file.filename or "unknown",
        minio_key=minio_key,
        mime_type=validation.detected_mime,
        file_size=len(file_bytes),
        status=ResumeStatus.COMPLETED,
        parsed_data={
            "name": structured.get("name") or None,
            "phone": phone,
            "email": email,
            "education": structured.get("education") or [],
            "skills": structured.get("skills") or [],
            "projects": structured.get("projects") or [],
            "work_experience": structured.get("work_experience") or [],
            "raw_text": raw_text,
            "parse_method": validation.detected_mime.split("/")[-1],
            "confidence": 0.92 if structured else 0.85,
        },
        raw_text_hash=hashlib.sha256(raw_text.encode()).hexdigest() if raw_text else None,
        parse_method=validation.detected_mime.split("/")[-1],
        confidence=0.92 if structured else 0.85,
    )
    async with get_db_session() as session:
        session.add(resume)
        await session.commit()

    return ResumeUploadResponse(
        id=resume_id,
        original_filename=file.filename or "unknown",
        status=ResumeStatus.COMPLETED,
        message="简历解析完成",
        parse_method=resume.parse_method,
        confidence=resume.confidence,
        extracted_name=None,
        extracted_phone=phone,
        extracted_email=email,
    )


@router.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_resume(
    request: DiagnosisRequest,
    current_user: str = Depends(get_current_user),
):
    # 尝试从Redis读取缓存
    jd_hash = hashlib.md5((request.job_description or "").encode()).hexdigest()[:8]
    cache_key = f"diag:{request.resume_id}:{jd_hash}"
    cached = await get_cache(cache_key)
    if cached:
        logger.debug("诊断结果缓存命中: %s", cache_key)
        return DiagnosisResponse(**cached)

    async with get_db_session() as session:
        result = await session.execute(select(Resume).where(Resume.id == uuid.UUID(request.resume_id)))
        resume = result.scalar_one_or_none()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        if str(resume.user_id) != current_user:
            raise HTTPException(status_code=403, detail="无权访问")

        parsed = resume.parsed_data or {}
        raw_text = parsed.get("raw_text", "")

        if not raw_text:
            raise HTTPException(status_code=400, detail="简历文本为空，无法诊断")

        # 使用真实的深度分析引擎
        from app.core.resume_analyzer import diagnose_resume as _diagnose
        diag = await _diagnose(raw_text, parsed, request.job_description)

        # ATS 兼容性分析
        ats = _run_ats_analysis(parsed, raw_text, request.job_description)

        response = DiagnosisResponse(
            resume_id=request.resume_id,
            match_score=diag.match_score,
            radar_scores=diag.radar_scores,
            analysis=diag.analysis,
            skill_gap=diag.skill_gap,
            suggestions=diag.suggestions,
            ats_analysis=ats,
        )

        # 写入Redis缓存（TTL=2小时）
        await set_cache(cache_key, response.model_dump(), ttl=7200)
        return response


@router.get("/{resume_id}/poll", response_model=ParseStatus)
async def poll_parse_status(resume_id: str, current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(
            select(Resume.status, Resume.parse_method, Resume.confidence, Resume.error_message)
            .where(Resume.id == uuid.UUID(resume_id))
        )
        row = result.one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="简历不存在")
        status_val, parse_method, confidence, error_message = row
        return ParseStatus(
            status=status_val.value if hasattr(status_val, "value") else status_val,
            parse_method=parse_method,
            confidence=confidence,
            error_message=error_message,
        )


@router.get("/{resume_id}", response_model=ResumeUploadResponse)
async def get_resume_status(resume_id: str, current_user: str = Depends(get_current_user)):
    async with get_db_session() as session:
        result = await session.execute(select(Resume).where(Resume.id == uuid.UUID(resume_id)))
        resume = result.scalar_one_or_none()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        if str(resume.user_id) != current_user:
            raise HTTPException(status_code=403, detail="无权访问")

        parsed = resume.parsed_data or {}
        return ResumeUploadResponse(
            id=resume_id,
            original_filename=resume.original_filename,
            status=resume.status.value if hasattr(resume.status, "value") else resume.status,
            parse_method=resume.parse_method,
            confidence=resume.confidence,
            extracted_name=parsed.get("name"),
            extracted_phone=parsed.get("phone"),
            extracted_email=parsed.get("email"),
            education_summary=parsed.get("education", [{}])[0].get("school", "") if parsed.get("education") else None,
            skills_summary=parsed.get("skills"),
        )
