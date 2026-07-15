"""初始化种子数据，包括测试账号、参考简历、岗位信息、面试记录等。"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.database import get_db_session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.resume import Resume, ResumeStatus
from app.models.job import Job
from app.models.interview import Interview, InterviewRound, InterviewStatus, Message, Evaluation, Review
from app.models.application import Application

logger = logging.getLogger(__name__)

TEST_USER_EMAIL = "test@qiuzhimiao.com"
TEST_USER_PASSWORD = "test123456"
TEST_USER_NICKNAME = "测试喵"

TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"


async def seed_test_user() -> User:
    """确保测试账号存在，不存在则创建。"""
    async with get_db_session() as session:
        result = await session.execute(
            select(User).where(User.email == TEST_USER_EMAIL)
        )
        existing = result.scalar_one_or_none()
        if existing:
            logger.info("测试账号已存在: %s", TEST_USER_EMAIL)
            return existing

        user = User(
            id=TEST_USER_ID,
            email=TEST_USER_EMAIL,
            password_hash=get_password_hash(TEST_USER_PASSWORD),
            nickname=TEST_USER_NICKNAME,
        )
        session.add(user)
        await session.commit()
        logger.info("测试账号创建成功: %s / %s", TEST_USER_EMAIL, TEST_USER_PASSWORD)
        return user


async def seed_reference_resumes(user: User) -> list[Resume]:
    """为测试用户创建参考简历数据。"""
    async with get_db_session() as session:
        result = await session.execute(
            select(Resume).where(Resume.user_id == user.id)
        )
        existing = result.scalars().all()
        if existing:
            logger.info("测试用户已有简历数据，跳过")
            return list(existing)

        resumes = []

        # 简历1：后端开发工程师
        resume1_data = {
            "raw_text": """
张三
电话: 13800138000  邮箱: zhangsan@example.com

教育背景
北京大学 计算机科学与技术 本科 2019-2023

技能清单
- 精通 Python、Go、Java
- 熟悉 Kubernetes、Docker、Prometheus、Grafana
- 掌握 MySQL、PostgreSQL、Redis、MongoDB、Elasticsearch
- 了解 Kafka、RabbitMQ、RocketMQ
- 熟练使用 Git、CI/CD、Terraform

工作经历
字节跳动 高级后端工程师 2023.07-至今
- 主导抖音推荐系统的存储层架构升级，将 QPS 从 50K 提升到 200K，降低 P99 延迟 40%
- 负责设计并实现分布式缓存一致性方案，解决缓存穿透和击穿问题，日均拦截异常请求 2亿+
- 带领 5 人小组完成用户画像服务从 Python 到 Go 的重构，CPU 利用率降低 60%，内存降低 45%
- 制定团队代码规范和 CR 流程，推动单元测试覆盖率从 30% 提升到 85%

阿里巴巴 后端开发工程师 2021.07-2023.06
- 参与天猫双十一订单系统的容量规划和压测，支持峰值 100W TPS
- 独立负责商品搜索服务的索引优化，检索耗时从 120ms 降低到 35ms
- 从0到1搭建商品实时价格同步系统，日均处理消息 5亿+，延迟 < 100ms

项目经验
高性能日志采集系统
- 背景：业务线日志采集延迟高，影响问题排查效率
- 任务：负责设计新一代日志采集架构
- 行动：基于 Kafka + Flink 实现端到端日志管道，引入 ZSTD 压缩，自定义 batch 策略
- 结果：日志采集延迟从 5 分钟降低到 10 秒，存储成本降低 70%，获公司年度技术创新奖

分布式任务调度平台
- 背景：原有定时任务系统单机瓶颈，任务经常堆积
- 任务：主导调度平台的架构设计和开发
- 行动：基于 etcd 实现分布式锁和任务分片，自研任务编排 DSL，支持 DAG 依赖
- 结果：支持 10W+ 并发任务，调度成功率 99.99%，已推广至全集团 20+ 业务线

个人简介
8年后端开发经验，深耕分布式系统和高并发架构。擅长从0到1搭建核心服务，对性能优化和系统稳定性有独到见解。热衷技术分享，GitHub 开源项目累计 Star 5K+。
            """,
            "name": "张三",
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "education": [
                {"school": "北京大学", "degree": "本科", "major": "计算机科学与技术", "start_date": "2019-09-01", "end_date": "2023-06-30"}
            ],
            "experience": [
                {
                    "company": "字节跳动",
                    "position": "高级后端工程师",
                    "start_date": "2023-07-01",
                    "end_date": "至今",
                    "description": "主导抖音推荐系统架构升级，负责分布式缓存方案设计，带领团队完成技术栈迁移"
                },
                {
                    "company": "阿里巴巴",
                    "position": "后端开发工程师",
                    "start_date": "2021-07-01",
                    "end_date": "2023-06-30",
                    "description": "参与双十一订单系统压测，负责商品搜索服务优化，搭建实时数据同步系统"
                }
            ],
            "projects": [
                {
                    "name": "高性能日志采集系统",
                    "description": "基于 Kafka + Flink 实现端到端日志管道，延迟从5分钟降到10秒"
                },
                {
                    "name": "分布式任务调度平台",
                    "description": "基于 etcd 实现分布式锁和任务分片，支持 10W+ 并发任务"
                }
            ],
            "skills": ["Python", "Go", "Java", "Kubernetes", "Docker", "MySQL", "PostgreSQL", "Redis", "MongoDB", "Elasticsearch", "Kafka", "RabbitMQ", "Git", "CI/CD"],
            "summary": "8年后端开发经验，深耕分布式系统和高并发架构"
        }

        resume1 = Resume(
            id=str(uuid.uuid4()),
            user_id=user.id,
            original_filename="张三_高级后端工程师.pdf",
            minio_key=f"resumes/{user.id}/zhangsan_backend.pdf",
            mime_type="application/pdf",
            file_size=456789,
            status=ResumeStatus.COMPLETED,
            parsed_data=resume1_data,
            parse_method="llm",
            confidence=0.95,
            created_at=datetime.utcnow() - timedelta(days=3),
        )
        resumes.append(resume1)

        # 简历2：前端开发工程师
        resume2_data = {
            "raw_text": """
李四
电话: 13900139000  邮箱: lisi@example.com

教育背景
上海交通大学 软件工程 硕士 2020-2023
本科：复旦大学 计算机科学 2016-2020

技能清单
- 精通 React、TypeScript、Next.js
- 熟悉 Vue、Nuxt、Svelte
- 掌握 Tailwind CSS、Styled Components、CSS Modules
- 了解 Webpack、Vite、Rollup、ESBuild
- 熟练使用 Jest、Cypress、Playwright、Storybook
- 掌握 GraphQL、RESTful API、WebSocket

工作经历
美团 前端技术专家 2023.07-至今
- 负责美团外卖主站前端架构升级，推动 SSR 方案落地，首屏加载时间降低 60%
- 设计并实现组件化体系，沉淀 200+ 通用组件，团队开发效率提升 40%
- 主导前端性能监控体系建设，建立 P0-P3 四级告警机制，线上问题发现时间缩短 80%
- 推动 TypeScript 全量迁移，代码类型覆盖率从 40% 提升到 95%

腾讯 前端开发工程师 2021.07-2023.06
- 参与微信小程序性能优化，首屏渲染时间从 2.5s 优化到 1.2s
- 独立开发企业微信前端组件库，服务 50+ 内部业务线
- 负责 QQ 音乐 H5 播放器重构，播放成功率提升 5%，内存降低 30%

项目经验
美团外卖主站架构升级
- 背景：业务快速发展，前端性能和维护成本成为瓶颈
- 任务：负责前端架构设计和核心模块开发
- 行动：引入 Next.js SSR，重构组件体系，建立性能监控平台
- 结果：首屏时间降低 60%，开发效率提升 40%，获公司技术创新奖

企业微信组件库
- 背景：各业务线重复造轮子，组件风格不统一
- 任务：设计并实现统一的企业级组件库
- 行动：基于 React + TypeScript，采用 Monorepo 架构，配套 Storybook 文档
- 结果：沉淀 200+ 组件，服务 50+ 业务线，代码复用率提升 60%

个人简介
6年前端开发经验，专注于前端架构和性能优化。擅长构建高质量的前端基础设施，对用户体验有极致追求。技术博客累计阅读量 100W+。
            """,
            "name": "李四",
            "phone": "13900139000",
            "email": "lisi@example.com",
            "education": [
                {"school": "上海交通大学", "degree": "硕士", "major": "软件工程", "start_date": "2020-09-01", "end_date": "2023-06-30"},
                {"school": "复旦大学", "degree": "本科", "major": "计算机科学", "start_date": "2016-09-01", "end_date": "2020-06-30"}
            ],
            "experience": [
                {
                    "company": "美团",
                    "position": "前端技术专家",
                    "start_date": "2023-07-01",
                    "end_date": "至今",
                    "description": "负责美团外卖主站前端架构升级，推动 SSR 方案落地"
                },
                {
                    "company": "腾讯",
                    "position": "前端开发工程师",
                    "start_date": "2021-07-01",
                    "end_date": "2023-06-30",
                    "description": "参与微信小程序性能优化，开发企业微信组件库"
                }
            ],
            "projects": [
                {
                    "name": "美团外卖主站架构升级",
                    "description": "引入 Next.js SSR，首屏时间降低 60%"
                },
                {
                    "name": "企业微信组件库",
                    "description": "沉淀 200+ 组件，服务 50+ 业务线"
                }
            ],
            "skills": ["React", "TypeScript", "Next.js", "Vue", "Nuxt", "Tailwind CSS", "Styled Components", "Webpack", "Vite", "Jest", "Cypress", "GraphQL", "RESTful API"],
            "summary": "6年前端开发经验，专注于前端架构和性能优化"
        }

        resume2 = Resume(
            id=str(uuid.uuid4()),
            user_id=user.id,
            original_filename="李四_前端技术专家.pdf",
            minio_key=f"resumes/{user.id}/lisi_frontend.pdf",
            mime_type="application/pdf",
            file_size=389234,
            status=ResumeStatus.COMPLETED,
            parsed_data=resume2_data,
            parse_method="llm",
            confidence=0.93,
            created_at=datetime.utcnow() - timedelta(days=1),
        )
        resumes.append(resume2)

        session.add_all(resumes)
        await session.commit()
        logger.info("参考简历数据创建成功，共 %d 份", len(resumes))
        return resumes


async def seed_reference_jobs(user: User) -> list[Job]:
    """为测试用户创建参考岗位信息。"""
    async with get_db_session() as session:
        result = await session.execute(
            select(Job).where(Job.user_id == user.id)
        )
        existing = result.scalars().all()
        if existing:
            logger.info("测试用户已有岗位数据，跳过")
            return list(existing)

        jobs = []

        job1 = Job(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="高级后端工程师",
            company="字节跳动",
            description="""
我们正在寻找技术能力扎实、有大型分布式系统开发经验的高级后端工程师加入抖音推荐团队。

岗位职责：
1. 负责抖音推荐系统核心模块的设计与开发
2. 参与系统架构设计，优化系统性能和稳定性
3. 解决高并发场景下的技术难题
4. 推动团队技术成长，提升工程质量

岗位要求：
1. 本科及以上学历，计算机相关专业
2. 3年以上后端开发经验，精通 Go/Python/Java 中至少一种
3. 熟悉分布式系统、微服务架构
4. 熟悉 Kubernetes、Docker、消息队列等中间件
5. 有千万级流量系统经验者优先
6. 良好的沟通能力和团队协作精神
            """,
            requirements={
                "education": "本科及以上",
                "experience": "3年以上",
                "skills": ["Go", "Python", "Java", "Kubernetes", "Docker", "分布式系统", "微服务", "消息队列"],
                "preferred": ["千万级流量", "推荐系统", "高并发"]
            },
            category="backend",
            created_at=datetime.utcnow() - timedelta(days=5),
        )
        jobs.append(job1)

        job2 = Job(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="前端技术专家",
            company="美团",
            description="""
美团外卖正在招聘前端技术专家，负责核心产品的前端架构设计和技术攻关。

岗位职责：
1. 负责美团外卖主站的前端架构设计与优化
2. 推动前端工程化建设，提升开发效率
3. 解决复杂业务场景下的性能和体验问题
4. 沉淀技术资产，推动团队技术分享

岗位要求：
1. 本科及以上学历，计算机相关专业
2. 5年以上前端开发经验，精通 React/Vue
3. 熟悉 Next.js/Nuxt 等服务端渲染框架
4. 有大型项目架构设计经验
5. 对性能优化有深入理解
6. 良好的沟通能力和团队协作精神
            """,
            requirements={
                "education": "本科及以上",
                "experience": "5年以上",
                "skills": ["React", "Vue", "TypeScript", "Next.js", "Nuxt", "性能优化", "工程化"],
                "preferred": ["服务端渲染", "大型项目架构", "组件库建设"]
            },
            category="frontend",
            created_at=datetime.utcnow() - timedelta(days=3),
        )
        jobs.append(job2)

        job3 = Job(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="AI 算法工程师",
            company="阿里云",
            description="""
阿里云达摩院正在招聘 AI 算法工程师，参与大模型训练和推理优化。

岗位职责：
1. 负责大语言模型的训练和微调
2. 优化模型推理性能，降低部署成本
3. 探索前沿 AI 技术，落地业务场景
4. 与业务团队协作，推动 AI 能力产品化

岗位要求：
1. 硕士及以上学历，计算机、数学相关专业
2. 3年以上机器学习/深度学习经验
3. 熟悉 PyTorch/TensorFlow 等框架
4. 有大模型训练或微调经验者优先
5. 良好的数学基础和编程能力
6. 良好的英文读写能力
            """,
            requirements={
                "education": "硕士及以上",
                "experience": "3年以上",
                "skills": ["PyTorch", "TensorFlow", "机器学习", "深度学习", "大模型"],
                "preferred": ["LLM", "模型训练", "推理优化"]
            },
            category="ai",
            created_at=datetime.utcnow() - timedelta(days=2),
        )
        jobs.append(job3)

        job4 = Job(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="测试开发工程师",
            company="腾讯",
            description="""
腾讯游戏正在招聘测试开发工程师，负责游戏后端服务的质量保障。

岗位职责：
1. 设计和实现自动化测试框架和工具
2. 负责核心模块的测试用例设计和执行
3. 参与代码评审，推动开发质量提升
4. 建立质量度量体系，持续改进测试流程

岗位要求：
1. 本科及以上学历，计算机相关专业
2. 2年以上测试开发经验
3. 熟悉 Python/Go 等编程语言
4. 熟悉测试框架和持续集成工具
5. 有游戏或高并发系统测试经验者优先
6. 良好的沟通能力和团队协作精神
            """,
            requirements={
                "education": "本科及以上",
                "experience": "2年以上",
                "skills": ["Python", "Go", "自动化测试", "CI/CD", "测试框架"],
                "preferred": ["游戏测试", "高并发", "性能测试"]
            },
            category="testing",
            created_at=datetime.utcnow() - timedelta(days=1),
        )
        jobs.append(job4)

        session.add_all(jobs)
        await session.commit()
        logger.info("参考岗位数据创建成功，共 %d 个", len(jobs))
        return jobs


async def seed_reference_interviews(user: User, resumes: list[Resume], jobs: list[Job]) -> list[Interview]:
    """为测试用户创建参考面试记录。"""
    async with get_db_session() as session:
        result = await session.execute(
            select(Interview).where(Interview.user_id == user.id)
        )
        existing = result.scalars().all()
        if existing:
            logger.info("测试用户已有面试数据，跳过")
            return list(existing)

        interviews = []

        # 面试1：技术一面（字节跳动-高级后端工程师）
        interview1 = Interview(
            id=str(uuid.uuid4()),
            user_id=user.id,
            resume_id=resumes[0].id,
            job_id=jobs[0].id,
            round=InterviewRound.TECH1,
            status=InterviewStatus.ENDED,
            duration=45,
            created_at=datetime.utcnow() - timedelta(days=7),
        )
        interviews.append(interview1)

        messages1 = [
            Message(id=str(uuid.uuid4()), interview_id=interview1.id, role="system", content="欢迎参加字节跳动技术一面，请自我介绍。", created_at=datetime.utcnow() - timedelta(days=7)),
            Message(id=str(uuid.uuid4()), interview_id=interview1.id, role="user", content="面试官您好，我叫张三，有8年后端开发经验，目前在阿里巴巴担任后端开发工程师。", created_at=datetime.utcnow() - timedelta(days=7)),
            Message(id=str(uuid.uuid4()), interview_id=interview1.id, role="system", content="请介绍一下你最有成就感的项目。", created_at=datetime.utcnow() - timedelta(days=7)),
            Message(id=str(uuid.uuid4()), interview_id=interview1.id, role="user", content="我最有成就感的项目是高性能日志采集系统。背景是业务线日志采集延迟高，影响问题排查效率。任务是负责设计新一代日志采集架构。行动是基于 Kafka + Flink 实现端到端日志管道，引入 ZSTD 压缩，自定义 batch 策略。结果是日志采集延迟从5分钟降低到10秒，存储成本降低70%，获公司年度技术创新奖。", created_at=datetime.utcnow() - timedelta(days=7)),
            Message(id=str(uuid.uuid4()), interview_id=interview1.id, role="system", content="说说你对分布式锁的理解，常用的实现方式有哪些？", created_at=datetime.utcnow() - timedelta(days=7)),
            Message(id=str(uuid.uuid4()), interview_id=interview1.id, role="user", content="分布式锁是用于在分布式环境下保证数据一致性的机制。常用的实现方式有：1）基于 Redis 的 Redlock 算法；2）基于 ZooKeeper 的临时节点；3）基于数据库的乐观锁/悲观锁。Redis 方案性能最好，但需要考虑锁的过期时间；ZooKeeper 方案可靠性更高，但性能相对较低。", created_at=datetime.utcnow() - timedelta(days=7)),
            Message(id=str(uuid.uuid4()), interview_id=interview1.id, role="system", content="好的，一面到此结束，感谢你的参与。我们会在3个工作日内通知你结果。", created_at=datetime.utcnow() - timedelta(days=7)),
        ]

        eval1 = Evaluation(
            id=str(uuid.uuid4()),
            interview_id=interview1.id,
            message_id=messages1[1].id,
            professional=85,
            logic=80,
            communication=85,
            project=90,
            match=85,
            overall=85,
            confidence=0.9,
            feedback="自我介绍清晰，项目经历丰富，但技术细节可以更深入。",
        )

        eval2 = Evaluation(
            id=str(uuid.uuid4()),
            interview_id=interview1.id,
            message_id=messages1[3].id,
            professional=90,
            logic=95,
            communication=88,
            project=92,
            match=88,
            overall=90,
            confidence=0.95,
            feedback="STAR 法则运用得当，项目描述完整，成果量化清晰。",
        )

        eval3 = Evaluation(
            id=str(uuid.uuid4()),
            interview_id=interview1.id,
            message_id=messages1[5].id,
            professional=85,
            logic=88,
            communication=85,
            project=80,
            match=85,
            overall=85,
            confidence=0.9,
            feedback="分布式锁理解准确，实现方式讲得清楚，但可以补充更多细节。",
        )

        review1 = Review(
            id=str(uuid.uuid4()),
            interview_id=interview1.id,
            overall_score=87,
            radar_data={"professional": 85, "logic": 88, "communication": 86, "project": 90, "match": 86},
            question_reviews=[
                {"question": "自我介绍", "score": 85, "feedback": "清晰简洁，重点突出"},
                {"question": "最有成就感的项目", "score": 90, "feedback": "STAR法则运用得当，成果量化"},
                {"question": "分布式锁", "score": 85, "feedback": "理解准确，但深度有待加强"},
            ],
            interviewer_summary="整体表现优秀，技术基础扎实，项目经验丰富。建议在技术深度上继续提升。",
            suggestions=["加强分布式系统理论学习", "准备更多系统设计案例", "练习白板编程"],
        )

        # 面试2：HR面试（美团-前端技术专家）
        interview2 = Interview(
            id=str(uuid.uuid4()),
            user_id=user.id,
            resume_id=resumes[1].id,
            job_id=jobs[1].id,
            round=InterviewRound.HR,
            status=InterviewStatus.ENDED,
            duration=30,
            created_at=datetime.utcnow() - timedelta(days=5),
        )
        interviews.append(interview2)

        messages2 = [
            Message(id=str(uuid.uuid4()), interview_id=interview2.id, role="system", content="欢迎参加美团HR面试，请简单介绍一下你的职业规划。", created_at=datetime.utcnow() - timedelta(days=5)),
            Message(id=str(uuid.uuid4()), interview_id=interview2.id, role="user", content="未来3-5年，我希望在前端架构领域深入发展，成为技术专家，带领团队解决复杂问题，推动前端技术的演进和落地。", created_at=datetime.utcnow() - timedelta(days=5)),
            Message(id=str(uuid.uuid4()), interview_id=interview2.id, role="system", content="你为什么选择美团？", created_at=datetime.utcnow() - timedelta(days=5)),
            Message(id=str(uuid.uuid4()), interview_id=interview2.id, role="user", content="美团是一家非常有活力的互联网公司，业务场景丰富，技术挑战大。我很认同美团的企业文化，也希望能在这样的平台上发挥自己的价值。", created_at=datetime.utcnow() - timedelta(days=5)),
            Message(id=str(uuid.uuid4()), interview_id=interview2.id, role="system", content="你对加班怎么看？", created_at=datetime.utcnow() - timedelta(days=5)),
            Message(id=str(uuid.uuid4()), interview_id=interview2.id, role="user", content="我认为工作和生活需要平衡，但在项目紧急时也会全力支持。更重要的是提升工作效率，避免无效加班。", created_at=datetime.utcnow() - timedelta(days=5)),
            Message(id=str(uuid.uuid4()), interview_id=interview2.id, role="system", content="HR面试到此结束，感谢你的参与。", created_at=datetime.utcnow() - timedelta(days=5)),
        ]

        eval4 = Evaluation(
            id=str(uuid.uuid4()),
            interview_id=interview2.id,
            message_id=messages2[1].id,
            professional=80,
            logic=85,
            communication=90,
            project=75,
            match=85,
            overall=83,
            confidence=0.85,
            feedback="职业规划清晰，有明确的发展目标。",
        )

        eval5 = Evaluation(
            id=str(uuid.uuid4()),
            interview_id=interview2.id,
            message_id=messages2[3].id,
            professional=85,
            logic=80,
            communication=88,
            project=70,
            match=90,
            overall=83,
            confidence=0.85,
            feedback="对公司有一定了解，表达真诚。",
        )

        review2 = Review(
            id=str(uuid.uuid4()),
            interview_id=interview2.id,
            overall_score=83,
            radar_data={"professional": 83, "logic": 82, "communication": 89, "project": 73, "match": 88},
            question_reviews=[
                {"question": "职业规划", "score": 83, "feedback": "目标明确，规划合理"},
                {"question": "为什么选择美团", "score": 83, "feedback": "表达真诚，有备而来"},
                {"question": "对加班的看法", "score": 83, "feedback": "态度客观，注重效率"},
            ],
            interviewer_summary="沟通能力强，表达清晰，价值观与公司文化匹配度较高。",
            suggestions=["准备更多关于美团业务的了解", "思考如何在美团发挥更大价值"],
        )

        # 面试3：技术二面（字节跳动-高级后端工程师）- 进行中
        interview3 = Interview(
            id=str(uuid.uuid4()),
            user_id=user.id,
            resume_id=resumes[0].id,
            job_id=jobs[0].id,
            round=InterviewRound.TECH2,
            status=InterviewStatus.ONGOING,
            duration=60,
            created_at=datetime.utcnow() - timedelta(hours=2),
        )
        interviews.append(interview3)

        messages3 = [
            Message(id=str(uuid.uuid4()), interview_id=interview3.id, role="system", content="欢迎参加字节跳动技术二面，请设计一个高并发的订单系统。", created_at=datetime.utcnow() - timedelta(hours=2)),
            Message(id=str(uuid.uuid4()), interview_id=interview3.id, role="user", content="好的，我会从以下几个方面来设计：1）系统架构：采用微服务架构，分为订单服务、库存服务、支付服务等；2）数据库设计：使用 MySQL 存储订单数据，Redis 做缓存；3）高并发处理：使用消息队列异步解耦，引入限流熔断；4）一致性保证：使用分布式事务或最终一致性方案。", created_at=datetime.utcnow() - timedelta(hours=2)),
            Message(id=str(uuid.uuid4()), interview_id=interview3.id, role="system", content="如果订单量达到 100W TPS，如何保证系统稳定性？", created_at=datetime.utcnow() - timedelta(hours=2)),
        ]

        session.add_all(interviews)
        session.add_all(messages1 + messages2 + messages3)
        session.add_all([eval1, eval2, eval3, eval4, eval5])
        session.add_all([review1, review2])
        await session.commit()
        logger.info("参考面试数据创建成功，共 %d 场", len(interviews))
        return interviews


async def seed_reference_applications(user: User, jobs: list[Job]) -> list[Application]:
    """为测试用户创建参考投递记录。"""
    async with get_db_session() as session:
        result = await session.execute(
            select(Application).where(Application.user_id == user.id)
        )
        existing = result.scalars().all()
        if existing:
            logger.info("测试用户已有投递数据，跳过")
            return list(existing)

        applications = []

        applications.append(Application(
            id=str(uuid.uuid4()),
            user_id=user.id,
            job_id=jobs[0].id,
            company="字节跳动",
            position="高级后端工程师",
            stage="interviewing",
            city="北京",
            salary_range="35K-45K",
            notes="技术一面已通过，等待二面通知",
            contact_info="HR王女士 13812345678",
            created_at=datetime.utcnow() - timedelta(days=10),
        ))

        applications.append(Application(
            id=str(uuid.uuid4()),
            user_id=user.id,
            job_id=jobs[1].id,
            company="美团",
            position="前端技术专家",
            stage="offer",
            city="北京",
            salary_range="30K-40K",
            notes="HR面已通过，正在谈薪资",
            contact_info="HR李女士 13987654321",
            feedback="面试官评价：沟通能力强，技术扎实",
            created_at=datetime.utcnow() - timedelta(days=8),
        ))

        applications.append(Application(
            id=str(uuid.uuid4()),
            user_id=user.id,
            job_id=jobs[2].id,
            company="阿里云",
            position="AI算法工程师",
            stage="pending",
            city="杭州",
            salary_range="32K-42K",
            notes="简历已投递，等待HR筛选",
            created_at=datetime.utcnow() - timedelta(days=3),
        ))

        applications.append(Application(
            id=str(uuid.uuid4()),
            user_id=user.id,
            company="腾讯",
            position="测试开发工程师",
            stage="rejected",
            city="深圳",
            salary_range="25K-35K",
            notes="笔试未通过",
            feedback="算法基础需要加强",
            created_at=datetime.utcnow() - timedelta(days=15),
        ))

        applications.append(Application(
            id=str(uuid.uuid4()),
            user_id=user.id,
            company="百度",
            position="后端开发工程师",
            stage="applied",
            city="北京",
            salary_range="28K-38K",
            notes="今日投递",
            created_at=datetime.utcnow(),
        ))

        applications.append(Application(
            id=str(uuid.uuid4()),
            user_id=user.id,
            company="京东",
            position="高级后端工程师",
            stage="interviewing",
            city="北京",
            salary_range="30K-40K",
            notes="已安排技术一面",
            contact_info="HR张女士 13611112222",
            created_at=datetime.utcnow() - timedelta(days=5),
        ))

        session.add_all(applications)
        await session.commit()
        logger.info("参考投递数据创建成功，共 %d 条", len(applications))
        return applications


async def seed_all() -> None:
    """执行所有种子数据初始化。"""
    logger.info("开始初始化种子数据...")
    user = await seed_test_user()
    resumes = await seed_reference_resumes(user)
    jobs = await seed_reference_jobs(user)
    await seed_reference_interviews(user, resumes, jobs)
    await seed_reference_applications(user, jobs)
    logger.info("种子数据初始化完成！")
