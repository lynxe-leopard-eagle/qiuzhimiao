"""集成测试 — 覆盖完整业务流程。

测试场景：
1. 用户注册 -> 登录
2. 上传简历 -> 解析 -> 诊断
3. 创建岗位 -> 分析 -> 匹配
4. 开始面试 -> 回答问题 -> 结束面试
5. 生成复盘 -> 查看成长记录
6. AI教练对话

验证模块间数据流和状态转换的正确性。
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

INTEGRATION_EMAIL = "integration_test@example.com"
INTEGRATION_PASSWORD = "TestPass123"


@pytest.fixture(scope="module")
def test_user():
    """创建集成测试用户并返回认证信息。"""
    # 注册（忽略已存在）
    client.post(
        "/api/v1/auth/register",
        json={"email": INTEGRATION_EMAIL, "password": INTEGRATION_PASSWORD, "name": "集成测试"},
    )

    # 登录
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": INTEGRATION_EMAIL, "password": INTEGRATION_PASSWORD},
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    return {
        "email": INTEGRATION_EMAIL,
        "headers": headers,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
    }


class TestCompleteFlow:
    """完整业务流程集成测试。"""

    def test_flow_01_auth(self, test_user):
        """步骤1: 验证用户认证有效。"""
        resp = client.get("/api/v1/auth/me", headers=test_user["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == INTEGRATION_EMAIL
        print(f"[集成测试] 用户认证通过: {data['email']}")

    def test_flow_02_resume_upload_and_diagnose(self, test_user):
        """步骤2: 上传简历并进行诊断。"""
        # 模拟上传PDF简历（使用文本内容模拟）
        resume_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n"
        files = {"file": ("integration_resume.pdf", resume_content, "application/pdf")}
        upload_resp = client.post(
            "/api/v1/resumes/upload",
            files=files,
            headers=test_user["headers"],
        )
        assert upload_resp.status_code == 200, f"上传失败: {upload_resp.text}"
        resume_id = upload_resp.json()["id"]
        print(f"[集成测试] 简历上传成功: {resume_id}")

        # 诊断简历
        jd = "招聘后端工程师，要求熟悉Python、Go、MySQL、Redis、微服务架构"
        diag_resp = client.post(
            "/api/v1/resumes/diagnose",
            json={"resume_id": resume_id, "job_description": jd},
            headers=test_user["headers"],
        )
        assert diag_resp.status_code == 200, f"诊断失败: {diag_resp.text}"
        diag_data = diag_resp.json()
        assert "match_score" in diag_data
        assert "radar_scores" in diag_data
        assert "ats_analysis" in diag_data
        print(f"[集成测试] 简历诊断完成: 匹配度={diag_data['match_score']}")

        # 保存resume_id供后续步骤使用
        test_user["resume_id"] = resume_id

    def test_flow_03_job_and_matching(self, test_user):
        """步骤3: 创建岗位并进行匹配分析。"""
        # 创建岗位
        job_resp = client.post(
            "/api/v1/jobs",
            json={
                "title": "高级后端工程师",
                "company": "测试大厂",
                "description": "负责高并发后端服务，要求Python、Go、MySQL、Redis、Kafka、K8s",
                "requirements": "5年以上经验，本科及以上学历，有大规模分布式系统经验",
                "category": "backend",
            },
            headers=test_user["headers"],
        )
        assert job_resp.status_code == 200
        job_id = job_resp.json()["id"]
        print(f"[集成测试] 岗位创建成功: {job_id}")

        # 岗位分析
        analyze_resp = client.post(
            "/api/v1/jobs/analyze",
            json={
                "job_description": "高级后端工程师，负责高并发后端服务，要求Python、Go、MySQL、Redis、Kafka、K8s",
                "title": "高级后端工程师",
                "company": "测试大厂",
            },
            headers=test_user["headers"],
        )
        assert analyze_resp.status_code == 200
        analyze_data = analyze_resp.json()
        assert analyze_data["difficulty_score"] > 0
        print(f"[集成测试] 岗位分析完成: 难度={analyze_data['difficulty_score']}")

        # 匹配分析
        resume_id = test_user.get("resume_id")
        if resume_id:
            match_resp = client.post(
                "/api/v1/jobs/matching",
                json={"resume_id": resume_id, "job_id": job_id},
                headers=test_user["headers"],
            )
            assert match_resp.status_code == 200
            match_data = match_resp.json()
            assert "match_score" in match_data
            assert "dimensions" in match_data
            assert "match_reasons" in match_data
            print(f"[集成测试] 匹配分析完成: 匹配度={match_data['match_score']}")

        test_user["job_id"] = job_id

    def test_flow_04_interview(self, test_user):
        """步骤4: 开始面试并结束。"""
        resume_id = test_user.get("resume_id")
        job_id = test_user.get("job_id")

        start_payload = {"round": "tech1", "interviewer_style": "professional"}
        if resume_id:
            start_payload["resume_id"] = resume_id
        if job_id:
            start_payload["job_id"] = job_id

        start_resp = client.post(
            "/api/v1/interviews/start",
            json=start_payload,
            headers=test_user["headers"],
        )
        assert start_resp.status_code == 200, f"面试开始失败: {start_resp.text}"
        start_data = start_resp.json()
        interview_id = start_data["interview_id"]
        assert "first_question" in start_data
        print(f"[集成测试] 面试开始成功: {interview_id}, 首题: {start_data['first_question'][:30]}...")

        # 模拟回答一个问题
        answer_resp = client.post(
            "/api/v1/interviews/answer",
            json={
                "interview_id": interview_id,
                "answer": "我在之前的项目中使用了Python和Go开发微服务，处理了日均百万级的请求。",
                "request_evaluation": False,
            },
            headers=test_user["headers"],
        )
        assert answer_resp.status_code == 200

        # 结束面试
        end_resp = client.post(
            f"/api/v1/interviews/{interview_id}/end",
            headers=test_user["headers"],
        )
        assert end_resp.status_code == 200
        end_data = end_resp.json()
        assert "interview_id" in end_data
        print(f"[集成测试] 面试结束成功: {interview_id}")

        test_user["interview_id"] = interview_id

    def test_flow_05_review_and_growth(self, test_user):
        """步骤5: 生成复盘并验证成长记录。"""
        interview_id = test_user.get("interview_id")
        if not interview_id:
            pytest.skip("前置面试步骤未成功")

        # 生成复盘
        review_resp = client.post(
            f"/api/v1/reviews/{interview_id}/generate",
            headers=test_user["headers"],
        )
        assert review_resp.status_code == 200, f"复盘生成失败: {review_resp.text}"
        review_data = review_resp.json()
        assert "overall_score" in review_data
        assert "radar_data" in review_data
        assert "suggestions" in review_data
        print(f"[集成测试] 复盘生成成功: 总分={review_data['overall_score']}")

        # 获取复盘
        get_resp = client.get(
            f"/api/v1/reviews/{interview_id}",
            headers=test_user["headers"],
        )
        assert get_resp.status_code == 200

        # 验证成长记录已生成
        growth_resp = client.get("/api/v1/growth/radar", headers=test_user["headers"])
        assert growth_resp.status_code == 200
        print("[集成测试] 成长记录已更新")

    def test_flow_06_applications(self, test_user):
        """步骤6: 投递看板完整CRUD。"""
        # 创建投递
        create_resp = client.post(
            "/api/v1/applications",
            json={
                "company": "阿里巴巴",
                "position": "Java后端",
                "job_description": "负责淘宝核心交易链路",
                "status": "applied",
                "priority": "high",
                "notes": "已投递，等待回复",
            },
            headers=test_user["headers"],
        )
        assert create_resp.status_code == 200
        app_id = create_resp.json()["id"]

        # 列表
        list_resp = client.get("/api/v1/applications", headers=test_user["headers"])
        assert list_resp.status_code == 200
        apps = list_resp.json()
        assert any(a["id"] == app_id for a in apps)

        # 统计
        stats_resp = client.get("/api/v1/applications/stats", headers=test_user["headers"])
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert stats["total"] >= 1

        # 更新
        update_resp = client.put(
            f"/api/v1/applications/{app_id}",
            json={
                "company": "阿里巴巴",
                "position": "Java后端",
                "status": "interview",
                "priority": "high",
                "notes": "收到面试邀请",
            },
            headers=test_user["headers"],
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "interview"

        # 删除
        del_resp = client.delete(
            f"/api/v1/applications/{app_id}",
            headers=test_user["headers"],
        )
        assert del_resp.status_code == 200

        # 验证已删除
        list_resp2 = client.get("/api/v1/applications", headers=test_user["headers"])
        apps2 = list_resp2.json()
        assert not any(a["id"] == app_id for a in apps2)
        print("[集成测试] 投递看板CRUD测试通过")

    def test_flow_07_coach_conversation(self, test_user):
        """步骤7: AI教练对话。"""
        # 获取工具列表
        tools_resp = client.get("/api/v1/coach/tools", headers=test_user["headers"])
        assert tools_resp.status_code == 200
        tools = tools_resp.json()
        assert isinstance(tools, list)
        print(f"[集成测试] AI教练工具: {len(tools)}个")

        # 对话
        chat_resp = client.post(
            "/api/v1/coach/chat",
            json={"message": "我明天有一个技术面试，请给我一些建议"},
            headers=test_user["headers"],
        )
        assert chat_resp.status_code == 200
        chat_data = chat_resp.json()
        assert "reply" in chat_data
        assert len(chat_data["reply"]) > 0
        print(f"[集成测试] AI教练回复: {chat_data['reply'][:50]}...")

        # 获取作战报告
        report_resp = client.get("/api/v1/coach/report", headers=test_user["headers"])
        assert report_resp.status_code == 200
        print("[集成测试] AI教练作战报告获取成功")
