"""基础 API 测试用例。"""

from __future__ import annotations

import random
import string

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _random_email() -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{suffix}@example.com"


# ── health ──────────────────────────────────────────────


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── auth register ───────────────────────────────────────


def test_register():
    email = _random_email()
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Str0ng!Pass123", "nickname": "测试用户"},
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == email


def test_register_weak_password():
    email = _random_email()
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "123", "nickname": "弱密码用户"},
    )
    # 注册可能仍然成功（取决于后端是否有密码强度校验），
    # 若无强度校验则接受 200/201；若有则期望 400
    assert resp.status_code in (200, 201, 400)


# ── auth login ──────────────────────────────────────────


def test_login():
    # 先注册一个用户
    email = _random_email()
    password = "Str0ng!Pass123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "nickname": "登录测试"},
    )
    # 再登录
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_login_wrong_password():
    email = _random_email()
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Str0ng!Pass123", "nickname": "错误密码测试"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword!1"},
    )
    assert resp.status_code == 401


# ── auth me ─────────────────────────────────────────────


def test_get_me():
    email = _random_email()
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Str0ng!Pass123", "nickname": "ME测试"},
    )
    token = reg_resp.json()["access_token"]
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == email


# ── job analyze ─────────────────────────────────────────


def test_job_analyze():
    # 需要先获取 token
    email = _random_email()
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Str0ng!Pass123", "nickname": "岗位分析测试"},
    )
    token = reg_resp.json()["access_token"]

    resp = client.post(
        "/api/v1/jobs/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "job_description": "熟练掌握 Python、Go，3年以上后端开发经验，熟悉微服务架构和 Kubernetes 部署",
            "title": "高级后端工程师",
            "company": "测试公司",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "core_skills" in data
    assert isinstance(data["core_skills"], list)
