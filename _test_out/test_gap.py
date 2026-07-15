"""验证 skills/gap 修复。"""
import urllib.request
import json

BASE = "http://localhost:8002"

# 登录
req = urllib.request.Request(
    f"{BASE}/api/v1/auth/login",
    data=json.dumps({"email": "test@qiuzhimiao.com", "password": "test123456"}).encode(),
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req)
token = json.loads(resp.read().decode("utf-8"))["access_token"]
print("登录成功，token 已获取")

# 测试 skills/gap（body 方式）
req2 = urllib.request.Request(
    f"{BASE}/api/v1/skills/gap",
    data=json.dumps({
        "resume_id": "00000000-0000-0000-0000-000000000000",
        "job_description": "Python 后端工程师，熟悉 FastAPI、PostgreSQL、Redis"
    }).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST",
)
try:
    resp2 = urllib.request.urlopen(req2)
    print(f"skills/gap 状态: {resp2.getcode()}")
    print(f"响应: {resp2.read().decode('utf-8')[:200]}")
except urllib.error.HTTPError as e:
    print(f"skills/gap 错误: {e.code}")
    print(f"响应: {e.read().decode('utf-8')[:200]}")
