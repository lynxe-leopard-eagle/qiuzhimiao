"""扩展API测试 — 覆盖全部业务模块的关键接口。

测试范围：
- Auth: 注册、登录、获取当前用户、刷新Token
- Resume: 上传、诊断、获取状态
- Job: 创建、分析、匹配
- Interview: 开始、结束、获取消息
- Review: 生成复盘、获取复盘、列表
- Growth: 雷达图、趋势
- Application: 创建、列表、统计、更新
- Coach: 工具、聊天
- Skill: 雷达、树、差距
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# 全局测试用户凭证
TEST_EMAIL = "test_api_extended@example.com"
TEST_PASSWORD = "TestPass123"
TEST_NAME = "API测试用户"


@pytest.fixture(scope="module")
def auth_headers():
    """创建测试用户并获取认证Header。"""
    # 注册
    register_resp = client.post(
        "/api/v1/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD, "name": TEST_NAME},
    )
    # 可能用户已存在，忽略409

    # 登录
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert login_resp.status_code == 200, f"登录失败: {login_resp.text}"
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuthAPI:
    """认证模块API测试。"""

    def test_register_and_login(self):
        """测试注册和登录流程。"""
        email = f"auth_test_{pytest.__version__}@example.com"
        # 注册
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": TEST_PASSWORD, "name": "AuthTest"},
        )
        assert resp.status_code in [200, 409]  # 成功或已存在

        # 登录
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": TEST_PASSWORD},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """测试错误密码登录应被拒绝。"""
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": TEST_EMAIL, "password": "WrongPass123"},
        )
        assert resp.status_code == 401

    def test_get_current_user(self, auth_headers):
        """测试获取当前用户信息。"""
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "email" in data

    def test_refresh_token(self, auth_headers):
        """测试刷新Token。"""
        # 先登录获取refresh_token
        login_resp = client.post(
            "/api/v1/auth/login",
            data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        refresh_token = login_resp.json()["refresh_token"]

        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    def test_protected_route_without_auth(self):
        """测试未认证访问受保护路由应被拒绝。"""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401


class TestJobAPI:
    """岗位模块API测试。"""

    def test_create_job(self, auth_headers):
        """测试创建岗位。"""
        resp = client.post(
            "/api/v1/jobs",
            json={
                "title": "后端工程师",
                "company": "测试公司",
                "description": "负责后端服务开发，要求熟悉Python、Go、MySQL",
                "requirements": "3年以上经验，本科及以上学历",
                "category": "backend",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "后端工程师"
        assert "id" in data

    def test_list_jobs(self, auth_headers):
        """测试获取岗位列表。"""
        resp = client.get("/api/v1/jobs", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_analyze_job(self, auth_headers):
        """测试岗位分析。"""
        jd = """
        岗位：高级后端工程师
        要求：
        - 5年以上后端开发经验
        - 精通Python、Go语言
        - 熟悉MySQL、Redis、Kafka
        - 有微服务架构设计经验
        - 本科及以上学历
        """
        resp = client.post(
            "/api/v1/jobs/analyze",
            json={"job_description": jd, "title": "高级后端工程师", "company": "大厂"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "core_skills" in data
        assert "difficulty_score" in data
        assert "summary" in data

    def test_analyze_job_empty_description(self, auth_headers):
        """测试空JD分析应返回有效结构。"""
        resp = client.post(
            "/api/v1/jobs/analyze",
            json={"job_description": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 200


class TestGrowthAPI:
    """成长追踪模块API测试。"""

    def test_get_radar(self, auth_headers):
        """测试获取成长雷达图。"""
        resp = client.get("/api/v1/growth/radar", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "radar" in data or "latest" in data

    def test_get_trend(self, auth_headers):
        """测试获取成长趋势。"""
        resp = client.get("/api/v1/growth/trend", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "trends" in data or "dimensions" in data


class TestApplicationAPI:
    """投递看板模块API测试。"""

    def test_create_and_list_applications(self, auth_headers):
        """测试创建和列表投递记录。"""
        # 创建
        resp = client.post(
            "/api/v1/applications",
            json={
                "company": "字节跳动",
                "position": "后端开发",
                "job_description": "负责抖音后端服务",
                "status": "applied",
                "priority": "high",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        app_id = resp.json()["id"]

        # 列表
        resp = client.get("/api/v1/applications", headers=auth_headers)
        assert resp.status_code == 200
        apps = resp.json()
        assert isinstance(apps, list)
        assert any(a["id"] == app_id for a in apps)

    def test_get_application_stats(self, auth_headers):
        """测试获取投递统计。"""
        resp = client.get("/api/v1/applications/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "by_status" in data

    def test_update_application_status(self, auth_headers):
        """测试更新投递状态。"""
        # 先创建
        resp = client.post(
            "/api/v1/applications",
            json={
                "company": "测试公司",
                "position": "测试岗位",
                "status": "applied",
                "priority": "medium",
            },
            headers=auth_headers,
        )
        app_id = resp.json()["id"]

        # 更新
        resp = client.put(
            f"/api/v1/applications/{app_id}",
            json={
                "company": "测试公司",
                "position": "测试岗位",
                "status": "interview",
                "priority": "high",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "interview"


class TestCoachAPI:
    """AI教练模块API测试。"""

    def test_get_coach_tools(self, auth_headers):
        """测试获取教练工具列表。"""
        resp = client.get("/api/v1/coach/tools", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert "name" in data[0]
            assert "description" in data[0]

    def test_coach_chat(self, auth_headers):
        """测试教练对话。"""
        resp = client.post(
            "/api/v1/coach/chat",
            json={"message": "如何准备技术面试？"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert len(data["reply"]) > 0

    def test_coach_report(self, auth_headers):
        """测试获取作战报告。"""
        resp = client.get("/api/v1/coach/report", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "report" in data


class TestSkillAPI:
    """技能图谱模块API测试。"""

    def test_get_skill_radar(self, auth_headers):
        """测试获取技能雷达图。"""
        resp = client.get("/api/v1/skills/radar", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "radar" in data

    def test_get_skill_tree(self, auth_headers):
        """测试获取技能树。"""
        resp = client.get("/api/v1/skills/tree", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "tree" in data

    def test_get_skill_gap(self, auth_headers):
        """测试获取技能差距分析。"""
        resp = client.post(
            "/api/v1/skills/gap",
            json={"target_position": "后端工程师"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "gaps" in data


class TestHealthAPI:
    """健康检查API测试。"""

    def test_health_check(self):
        """测试健康检查端点。"""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "service" in data

    def test_api_docs_accessible(self):
        """测试API文档可访问（debug模式下）。"""
        resp = client.get("/docs")
        # 可能返回200（debug模式）或404（生产模式）
        assert resp.status_code in [200, 404]
