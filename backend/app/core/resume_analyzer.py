"""简历深度分析引擎 — 基于真实内容的质量评估与优化建议生成。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# ============ 常量定义 ============

# 强动词库（用于检测描述力度）
_STRONG_VERBS = {
    "主导", "负责", "设计", "开发", "实现", "搭建", "构建", "优化", "提升", "改进",
    "重构", "迁移", "整合", "统一", "规范", "制定", "推动", "带领", "管理", "协调",
    "解决", "处理", "排查", "定位", "修复", "攻克", "突破", "创新", "落地", "交付",
    "独立", "全程", "从0到1", "从 0 到 1", "从0-1", "端到端", "全链路", "全栈",
    " architect", " led", " designed", " developed", " implemented", " built",
    " optimized", " improved", " refactored", " migrated", " integrated",
    " standardized", " established", " drove", " managed", " coordinated",
    " resolved", " troubleshot", " debugged", " innovated", " delivered",
    " independently", " end-to-end", " full-stack",
}

# 弱动词库（需要替换为强动词）
_WEAK_VERBS = {
    "参与", "协助", "配合", "学习", "了解", "熟悉", "使用", "用过", "做过",
    "帮忙", "辅助", "参加", "涉及", "接触",
    " participated", " assisted", " helped", " learned", " familiar",
    " used", " knew", " involved",
}

# 量化指标模式（用于检测数据化表达）
_QUANTIFY_PATTERNS = [
    r"\d+%",                    # 百分比
    r"\d+\.?\d*\s*[万亿千万]",  # 数量级
    r"\d+\.?\d*\s*[wW万]",      # 万
    r"QPS\s*[\d\.]+[kKmM]?",    # QPS
    r"[\d\.]+[kKmMgG]?[Bb]",    # 数据量
    r"\d+\s*[ms秒分小时天月年]",   # 时间
    r"\d+\.?\d*\s*倍",          # 倍数
    r"[\d\.]+\s*亿",            # 亿
    r"DAU\s*[\d\.]+[wW万]?",    # DAU
    r"PV\s*[\d\.]+[wW万]?",      # PV
    r"UV\s*[\d\.]+[wW万]?",      # UV
    r"GMV\s*[\d\.]+[wW万]?",     # GMV
]

# STAR 关键词
_STAR_KEYWORDS = {
    "situation": ["背景", "面临", "当时", "由于", "因为", "场景", "context", "situation", "faced", "due to"],
    "task": ["负责", "任务", "目标", "需要", "职责", "role", "task", "goal", "objective", "responsible"],
    "action": ["通过", "采用", "使用", "利用", "借助", "引入", "搭建", "设计", "实现", "by", "using", "implemented", "designed", "developed"],
    "result": ["结果", "最终", "达成", "实现", "提升", "降低", "缩短", "增长", "result", "achieved", "increased", "reduced", "improved"],
}

# ATS 常见技术关键词库
_ATS_KEYWORDS = {
    "python", "java", "javascript", "typescript", "go", "c++", "c#", "rust", "ruby", "php",
    "swift", "kotlin", "scala", "dart", "lua", "perl",
    "react", "vue", "angular", "next.js", "nuxt", "html", "css", "tailwind", "sass",
    "webpack", "vite", "rollup", "babel", "jest", "cypress", "storybook", "redux",
    "vuex", "pinia", "zustand", "react-query", "tanstack",
    "spring", "springboot", "django", "flask", "fastapi", "express", "nestjs", "gin",
    "echo", "koa", "laravel", "symfony", "rails", "quarkus", "micronaut",
    "mysql", "postgresql", "redis", "mongodb", "elasticsearch", "sqlite", "oracle",
    "sqlserver", "dynamodb", "cassandra", "tidb", "clickhouse", "neo4j",
    "docker", "kubernetes", "k8s", "aws", "azure", "gcp", "aliyun", "tencent",
    "ci/cd", "jenkins", "gitlab", "github", "actions", "terraform", "ansible",
    "helm", "istio", "prometheus", "grafana", "elk", "loki",
    "kafka", "rabbitmq", "rocketmq", "pulsar", "activemq", "mqtt",
    "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "spark", "hadoop",
    "flink", "airflow", "mlflow", "xgboost", "lightgbm", "transformers", "langchain",
    "llm", "大模型",
    "微服务", "分布式", "高并发", "中间件", "负载均衡", "缓存", "消息队列",
    "restful", "graphql", "rpc", "grpc", "protobuf", "api", "websocket", "serverless",
    "oauth", "jwt", "oauth2", "sso", "https", "ssl", "tls", "加密", "安全",
    "tcp", "udp", "http", "https", "dns", "cdn", "nginx", "反向代理", "网关",
    "linux", "unix", "centos", "ubuntu", "shell", "bash",
    "领导力", "团队协作", "项目管理", "敏捷", "scrum", "kanban", "沟通", "复盘",
    "优化", "创新", "问题解决", "学习能力", "责任心", "执行力", "逻辑思维",
    "代码审查", "技术分享",
}

_ATS_SECTIONS = {
    "education": ["教育", "学历", "学校", "university", "education", "bachelor", "master", "phd", "本科", "硕士", "博士", "毕业"],
    "experience": ["工作经历", "实习", "experience", "work", "internship", "工作经验", "实习经历", "职业经历"],
    "projects": ["项目经历", "项目经验", "project", "projects", "项目", "项目描述"],
    "skills": ["技能", "skill", "skills", "技术栈", "技术能力", "programming", "专业技能"],
    "contact": ["联系方式", "电话", "邮箱", "email", "phone", "contact", "手机", "地址"],
    "summary": ["个人简介", "自我介绍", "summary", "profile", "about", "概述", "简介"],
}


# ============ 数据模型 ============

@dataclass
class ContentAnalysis:
    """内容质量分析结果。"""
    text_length: int = 0
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    strong_verb_count: int = 0
    weak_verb_count: int = 0
    strong_verb_ratio: float = 0.0
    quantify_count: int = 0
    star_score: float = 0.0
    star_breakdown: dict = field(default_factory=dict)
    redundancy_score: float = 0.0
    redundant_phrases: list = field(default_factory=list)
    tense_issues: list = field(default_factory=list)
    vague_phrases: list = field(default_factory=list)


@dataclass
class StructureAnalysis:
    """结构完整性分析结果。"""
    has_education: bool = False
    has_experience: bool = False
    has_projects: bool = False
    has_skills: bool = False
    has_contact: bool = False
    has_summary: bool = False
    missing_sections: list = field(default_factory=list)
    section_score: float = 0.0


@dataclass
class ATSAnalysisResult:
    """ATS 兼容性分析结果。"""
    overall_score: float = 0.0
    keyword_coverage: float = 0.0
    detected_keywords: list = field(default_factory=list)
    missing_keywords: list = field(default_factory=list)
    format_issues: list = field(default_factory=list)
    missing_sections: list = field(default_factory=list)


@dataclass
class DiagnosisResult:
    """完整诊断结果。"""
    match_score: float = 0.0
    radar_scores: dict = field(default_factory=dict)
    analysis: str = ""
    skill_gap: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    ats_analysis: ATSAnalysisResult | None = None
    content_analysis: ContentAnalysis | None = None
    structure_analysis: StructureAnalysis | None = None


# ============ 分析函数 ============

def analyze_structure(raw_text: str) -> StructureAnalysis:
    """分析简历结构完整性。"""
    text_lower = raw_text.lower() if raw_text else ""
    result = StructureAnalysis()

    for section, keywords in _ATS_SECTIONS.items():
        found = any(kw in text_lower for kw in keywords)
        setattr(result, f"has_{section}", found)
        if not found:
            result.missing_sections.append(section)

    # 计算结构分（6个模块，每个约16.7分）
    has_count = sum([
        result.has_education, result.has_experience, result.has_projects,
        result.has_skills, result.has_contact, result.has_summary,
    ])
    result.section_score = has_count / 6 * 100
    return result


def analyze_content(raw_text: str) -> ContentAnalysis:
    """深度分析简历内容质量。"""
    result = ContentAnalysis()
    if not raw_text:
        return result

    text = raw_text.strip()
    result.text_length = len(text)

    # 分句（中/英文）
    sentences = re.split(r'[。！？.!?\n]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    result.sentence_count = len(sentences)
    result.word_count = len(text.replace(" ", ""))
    result.avg_sentence_length = result.word_count / max(result.sentence_count, 1)

    text_lower = text.lower()

    # 强/弱动词检测
    for verb in _STRONG_VERBS:
        if verb.lower() in text_lower:
            result.strong_verb_count += text_lower.count(verb.lower())
    for verb in _WEAK_VERBS:
        if verb.lower() in text_lower:
            result.weak_verb_count += text_lower.count(verb.lower())

    total_verbs = result.strong_verb_count + result.weak_verb_count
    result.strong_verb_ratio = result.strong_verb_count / max(total_verbs, 1) * 100

    # 量化指标检测
    for pattern in _QUANTIFY_PATTERNS:
        result.quantify_count += len(re.findall(pattern, text, re.IGNORECASE))

    # STAR 法则检测
    star_counts = {k: 0 for k in _STAR_KEYWORDS}
    for category, keywords in _STAR_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                star_counts[category] += text_lower.count(kw.lower())

    result.star_breakdown = star_counts
    # STAR 完整度：四个维度都有且每维度至少出现2次得满分
    star_categories_met = sum(1 for c in star_counts.values() if c >= 2)
    result.star_score = star_categories_met / 4 * 100

    # 冗余短语检测（简单实现：检测重复出现的3-6字短语）
    phrases_found = {}
    for length in range(4, 7):
        for i in range(len(text) - length + 1):
            phrase = text[i:i + length]
            if " " not in phrase and "\n" not in phrase and len(phrase.strip()) == length:
                phrases_found[phrase] = phrases_found.get(phrase, 0) + 1

    # 找出出现3次以上的非功能性短语
    for phrase, count in phrases_found.items():
        if count >= 3 and len(set(phrase)) > 2:  # 避免 "AAA" 这种
            result.redundant_phrases.append(f"「{phrase}」出现 {count} 次")
    result.redundancy_score = max(0, 100 - len(result.redundant_phrases) * 15)

    # 模糊表达检测
    vague_patterns = [
        r"(负责相关工作|做一些|参与部分|协助处理一些|进行一定的|了解.{0,5}相关|熟悉.{0,5}相关)",
        r"(some|several|certain|various|many|few)\s+(work|tasks|projects)",
    ]
    for pattern in vague_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        result.vague_phrases.extend(matches)

    return result


def analyze_ats(raw_text: str, jd_text: str | None = None) -> ATSAnalysisResult:
    """执行 ATS 兼容性分析。"""
    result = ATSAnalysisResult()
    if not raw_text:
        result.format_issues.append("简历文本为空，无法解析")
        return result

    text_lower = raw_text.lower()

    # 1. 关键词覆盖
    detected = sorted([kw for kw in _ATS_KEYWORDS if kw in text_lower])
    result.detected_keywords = detected

    missing_keywords = []
    if jd_text:
        jd_lower = jd_text.lower()
        jd_keywords = {kw for kw in _ATS_KEYWORDS if kw in jd_lower}
        missing_keywords = sorted(jd_keywords - set(detected))
        result.keyword_coverage = len(set(detected) & jd_keywords) / len(jd_keywords) * 100 if jd_keywords else 100.0
    else:
        # 无JD时，基于通用技术栈期望评估
        essential_keywords = {
            "python", "java", "javascript", "react", "vue", "spring", "mysql", "redis",
            "docker", "linux", "git", "api", "restful", "sql",
        }
        matched_essential = len(set(detected) & essential_keywords)
        result.keyword_coverage = matched_essential / len(essential_keywords) * 100
        missing_keywords = sorted(essential_keywords - set(detected))

    result.keyword_coverage = min(result.keyword_coverage, 100.0)
    result.missing_keywords = missing_keywords[:10]  # 最多返回10个

    # 2. 格式问题检测
    format_issues = []
    lines = raw_text.split("\n")
    avg_line_len = sum(len(l) for l in lines) / len(lines) if lines else 0
    if avg_line_len > 200:
        format_issues.append("段落过长，建议拆分为短句以便 ATS 解析")
    if len(raw_text) < 200:
        format_issues.append("简历内容过少，建议补充至 500 字以上")
    if len(raw_text) > 4000:
        format_issues.append("简历内容过长，建议精简至 1-2 页")

    special_chars = sum(1 for c in raw_text if c in "│┃┌┐└┘├┤┬┴┼")
    if special_chars > 5:
        format_issues.append("包含表格框线字符，可能导致 ATS 解析异常")

    if "http" not in text_lower and "www" not in text_lower and "@" not in text_lower:
        format_issues.append("缺少可识别的链接或邮箱信息")

    image_indicators = ["[图片]", "[图]", "image", "picture", "photo"]
    if any(ind in text_lower for ind in image_indicators):
        format_issues.append("检测到图片引用，ATS 无法解析图片内容，请确保关键信息以文本形式呈现")

    if any(ch in raw_text for ch in "🎨🎯🚀💡🔥💪🌟⚡💻📊📈"):
        format_issues.append("包含 emoji 表情符号，部分 ATS 系统可能无法正确处理")

    # 检测PDF解析异常特征
    if len(raw_text) < 100 and raw_text.count("\x00") > 0:
        format_issues.append("文本内容异常，可能是扫描版 PDF 或图片简历，ATS 无法解析")

    result.format_issues = format_issues

    # 3. 模块完整性
    missing_sections = []
    for section, keywords in _ATS_SECTIONS.items():
        if not any(kw in text_lower for kw in keywords):
            missing_sections.append(section)
    result.missing_sections = missing_sections

    # 4. 综合评分
    section_score = (6 - len(missing_sections)) / 6 * 30
    keyword_score = result.keyword_coverage / 100 * 30
    format_score = (4 - min(len(format_issues), 4)) / 4 * 25

    # 量化指标加分
    quantify_count = 0
    for pattern in _QUANTIFY_PATTERNS:
        quantify_count += len(re.findall(pattern, raw_text, re.IGNORECASE))
    quantify_score = min(quantify_count / 5, 1.0) * 15

    result.overall_score = round(section_score + keyword_score + format_score + quantify_score, 1)
    result.overall_score = min(result.overall_score, 100.0)

    return result


def generate_suggestions(
    structure: StructureAnalysis,
    content: ContentAnalysis,
    ats: ATSAnalysisResult,
    parsed_data: dict,
    jd_text: str | None,
) -> list[str]:
    """基于分析结果生成具体可操作的修改建议。"""
    suggestions = []

    # 结构建议
    if structure.missing_sections:
        section_names = {
            "education": "教育背景", "experience": "工作/实习经历",
            "projects": "项目经验", "skills": "技能列表",
            "contact": "联系方式", "summary": "个人简介",
        }
        for s in structure.missing_sections:
            suggestions.append(f"【结构】补充「{section_names.get(s, s)}」模块，这是简历的核心组成部分")

    # 内容长度建议
    if content.text_length < 300:
        suggestions.append(f"【内容】当前简历仅 {content.text_length} 字，内容偏少。建议扩充至 500-1500 字，充分展现实力")
    elif content.text_length > 3500:
        suggestions.append(f"【内容】当前简历 {content.text_length} 字，内容过长。建议精简至 1-2 页，突出重点")

    # 动词力度建议
    if content.weak_verb_count > content.strong_verb_count:
        suggestions.append(
            f"【表达】检测到 {content.weak_verb_count} 处弱动词表达（如'参与''协助'），"
            f"建议替换为强动词（如'主导''独立负责''从0到1搭建'），"
            f"当前强动词占比仅 {content.strong_verb_ratio:.0f}%"
        )

    # 量化建议
    if content.quantify_count < 3:
        suggestions.append(
            "【量化】量化数据不足，建议为每个项目/经历添加具体指标，"
            '如"日均访问量 10W+"、"QPS 提升 300%"、"响应时间降低 50%"'
        )

    # STAR 法则建议
    if content.star_score < 50:
        star_missing = []
        for dim, count in content.star_breakdown.items():
            if count < 2:
                star_missing.append(dim)
        if star_missing:
            dim_names = {"situation": "背景", "task": "任务", "action": "行动", "result": "结果"}
            suggestions.append(
                f"【STAR法则】项目描述缺少 {', '.join(dim_names.get(d, d) for d in star_missing)} 维度，"
                f"建议按「背景→任务→行动→结果」结构重写，如"
                f'"在XX背景下，负责XX任务，通过XX方案，最终实现XX提升"'
            )

    # ATS 格式建议
    for issue in ats.format_issues:
        suggestions.append(f"【格式】{issue}")

    # 关键词建议
    if ats.missing_keywords:
        top_missing = ats.missing_keywords[:5]
        suggestions.append(
            f"【关键词】建议补充以下技术关键词：{', '.join(top_missing)}"
            f"{'（根据目标岗位JD）' if jd_text else '（这些是行业通用核心技术）'}"
        )

    # 冗余建议
    if content.redundant_phrases:
        suggestions.append(
            f"【冗余】检测到 {len(content.redundant_phrases)} 处重复表达，"
            f"建议精简：{content.redundant_phrases[0]}"
        )

    # 模糊表达建议
    if content.vague_phrases:
        suggestions.append(
            f"【精准】检测到模糊表达：「{content.vague_phrases[0]}」，"
            f'建议替换为具体描述，如"独立完成用户模块开发，覆盖注册/登录/权限管理"'
        )

    # 技能列表建议
    skills = parsed_data.get("skills", []) if parsed_data else []
    if skills and len(skills) < 5:
        suggestions.append(
            f"【技能】当前技能列表仅 {len(skills)} 项，建议扩充至 10-15 项核心技能，"
            f"并按「精通/熟悉/了解」分级标注熟练度"
        )
    elif skills and len(skills) > 30:
        suggestions.append(
            f"【技能】技能列表达 {len(skills)} 项，建议聚焦核心技能，"
            f"删减不相关或仅浅层了解的技术"
        )

    # 联系方式建议
    if not parsed_data.get("phone") and not parsed_data.get("email"):
        suggestions.append("【联系】未检测到有效的手机号或邮箱，请确保联系方式清晰可见")

    # 兜底建议
    if not suggestions:
        suggestions.append("简历整体质量良好！建议定期更新项目经验，并针对目标岗位微调关键词")

    return suggestions


def generate_skill_gap(
    ats: ATSAnalysisResult,
    content: ContentAnalysis,
    parsed_data: dict,
) -> list[str]:
    """生成技能缺口分析。"""
    gaps = []

    # 基于缺失关键词
    if ats.missing_keywords:
        for kw in ats.missing_keywords[:5]:
            gaps.append(f"未体现「{kw}」相关经验，建议补充相关项目或学习记录")

    # 基于量化能力不足
    if content.quantify_count < 2:
        gaps.append("缺乏数据化成果描述，无法直观体现技术影响力")

    # 基于STAR法则
    if content.star_score < 40:
        gaps.append("项目描述缺少结构化表达，难以评估实际贡献度")

    # 基于动词力度
    if content.strong_verb_ratio < 30:
        gaps.append("描述以被动参与为主，缺少主导性工作的证据")

    if not gaps:
        gaps.append("技能覆盖较全面，建议继续深耕核心技术栈")

    return gaps


def generate_analysis_summary(
    structure: StructureAnalysis,
    content: ContentAnalysis,
    ats: ATSAnalysisResult,
    parsed_data: dict,
    jd_text: str | None,
) -> str:
    """生成分析总结文本。"""
    parts = []

    # 整体评价
    if ats.overall_score >= 80:
        parts.append("简历整体质量优秀")
    elif ats.overall_score >= 60:
        parts.append("简历整体质量良好")
    elif ats.overall_score >= 40:
        parts.append("简历基本合格，仍有较大优化空间")
    else:
        parts.append("简历质量有待大幅提升")

    # 结构评价
    section_map = {"education": "教育背景", "experience": "工作经历", "projects": "项目经验", "skills": "技能列表", "contact": "联系方式", "summary": "个人简介"}
    if structure.section_score >= 80:
        present = [section_map.get(s, s) for s in ["education", "experience", "projects", "skills", "contact", "summary"] if getattr(structure, f"has_{s}")]
        parts.append(f"结构完整，包含{'、'.join(present)}等核心模块")
    else:
        missing_names = [section_map.get(s, s) for s in structure.missing_sections]
        parts.append(f"缺少 {', '.join(missing_names)} 模块")

    # 内容评价
    parts.append(f"内容长度 {content.text_length} 字，{'篇幅适中' if 300 <= content.text_length <= 2000 else '建议调整'}")

    # 关键词
    parts.append(f"检测到 {len(ats.detected_keywords)} 个技术关键词，覆盖率 {ats.keyword_coverage:.0f}%")

    # 量化
    parts.append(f"包含 {content.quantify_count} 处量化数据")

    # 动词
    parts.append(f"强动词使用占比 {content.strong_verb_ratio:.0f}%")

    # STAR
    parts.append(f"STAR法则完整度 {content.star_score:.0f}%")

    # JD匹配
    if jd_text:
        parts.append("已结合目标岗位JD进行分析")

    return "。".join(parts) + "。"


def calculate_radar_scores(
    structure: StructureAnalysis,
    content: ContentAnalysis,
    ats: ATSAnalysisResult,
) -> dict[str, float]:
    """计算雷达图各维度评分。"""
    return {
        "structure": round(structure.section_score, 0),
        "content": round(min(content.text_length / 15, 100) if content.text_length < 1500 else max(0, 100 - (content.text_length - 1500) / 20), 0),
        "keywords": round(ats.keyword_coverage, 0),
        "quantify": round(min(content.quantify_count / 5 * 100, 100), 0),
        "expression": round(content.star_score * 0.5 + content.strong_verb_ratio * 0.5, 0),
    }


def calculate_match_score(
    structure: StructureAnalysis,
    content: ContentAnalysis,
    ats: ATSAnalysisResult,
    jd_text: str | None,
) -> float:
    """计算综合匹配分数。"""
    radar = calculate_radar_scores(structure, content, ats)
    # 加权平均
    weights = {"structure": 0.20, "content": 0.15, "keywords": 0.25, "quantify": 0.20, "expression": 0.20}
    score = sum(radar[k] * weights[k] for k in weights)

    # ATS整体分数也参与计算
    score = score * 0.7 + ats.overall_score * 0.3

    return round(min(score, 100.0), 1)


async def llm_enhance_suggestions(
    raw_text: str,
    existing_suggestions: list[str],
    parsed_data: dict,
    jd_text: str | None,
) -> list[str]:
    """使用 LLM 增强建议的具体性和可操作性。"""
    try:
        from app.core.llm_service import get_llm_service
        llm = get_llm_service()
        if not llm.is_real_llm_available:
            return existing_suggestions

        system_prompt = (
            "你是一位资深HR和技术面试官，擅长简历优化。请基于简历分析结果，"
            "将以下建议改写为更具体、更可操作的形式。每条建议应包含："
            "1. 具体问题是什么；2. 为什么要改；3. 怎么改（给出示例）。"
            "保持简洁，每条建议不超过80字。直接输出建议列表，不要添加额外说明。"
        )

        context = f"简历内容摘要：{raw_text[:800]}\n\n当前建议：\n"
        for i, s in enumerate(existing_suggestions[:8], 1):
            context += f"{i}. {s}\n"

        if jd_text:
            context += f"\n目标岗位JD：{jd_text[:300]}"

        result = await llm.chat(
            [{"role": "user", "content": context}],
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=800,
        )

        # 解析返回的建议列表
        lines = result.strip().split("\n")
        enhanced = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 去除序号前缀
            line = re.sub(r"^\d+[\.\)\-]\s*", "", line)
            if len(line) > 10:
                enhanced.append(line)

        return enhanced[:8] if enhanced else existing_suggestions
    except Exception:
        return existing_suggestions


# ============ 主分析入口 ============

async def diagnose_resume(
    raw_text: str,
    parsed_data: dict,
    jd_text: str | None = None,
) -> DiagnosisResult:
    """对简历执行完整的深度诊断分析。"""
    # 1. 结构分析
    structure = analyze_structure(raw_text)

    # 2. 内容分析
    content = analyze_content(raw_text)

    # 3. ATS 分析
    ats = analyze_ats(raw_text, jd_text)

    # 4. 计算雷达图分数
    radar = calculate_radar_scores(structure, content, ats)

    # 5. 计算综合分数
    match_score = calculate_match_score(structure, content, ats, jd_text)

    # 6. 生成基础建议
    suggestions = generate_suggestions(structure, content, ats, parsed_data, jd_text)

    # 7. 使用 LLM 增强建议
    suggestions = await llm_enhance_suggestions(raw_text, suggestions, parsed_data, jd_text)

    # 8. 生成技能缺口
    skill_gap = generate_skill_gap(ats, content, parsed_data)

    # 9. 生成分析总结
    analysis = generate_analysis_summary(structure, content, ats, parsed_data, jd_text)

    return DiagnosisResult(
        match_score=match_score,
        radar_scores=radar,
        analysis=analysis,
        skill_gap=skill_gap,
        suggestions=suggestions,
        ats_analysis=ats,
        content_analysis=content,
        structure_analysis=structure,
    )
