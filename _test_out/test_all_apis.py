"""综合 API 测试脚本：测试所有核心端点。"""
import urllib.request
import json
import sys

BASE = "http://localhost:8002"
results = []

def req(method, path, token=None, body=None):
    url = BASE + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r)
        status = resp.getcode()
        try:
            content = json.loads(resp.read().decode("utf-8"))
        except Exception:
            content = {"raw": resp.read().decode("utf-8", errors="replace")}
        return status, content
    except urllib.error.HTTPError as e:
        try:
            content = json.loads(e.read().decode("utf-8"))
        except Exception:
            content = {"error": str(e)}
        return e.code, content
    except Exception as e:
        return -1, {"error": str(e)}

# 1. 健康检查
s, c = req("GET", "/health")
results.append(("GET /health", s, c))

# 2. 登录
s, c = req("POST", "/api/v1/auth/login", body={"email": "test@qiuzhimiao.com", "password": "test123456"})
results.append(("POST /auth/login", s, "OK" if s == 200 else c))
token = c.get("access_token") if s == 200 else None

# 3. auth/me
s, c = req("GET", "/api/v1/auth/me", token=token)
results.append(("GET /auth/me", s, c))

# 4. 简历列表/上传（仅查询，不上传文件）
s, c = req("GET", "/api/v1/resumes/upload", token=token)
results.append(("GET /resumes/upload (probe)", s, c))

# 5. 岗位匹配
s, c = req("POST", "/api/v1/jobs/matching", token=token, body={
    "resume_id": "00000000-0000-0000-0000-000000000000",
    "job_description": "Python 后端工程师，熟悉 FastAPI、PostgreSQL、Redis"
})
results.append(("POST /jobs/matching", s, c))

# 6. 岗位列表
s, c = req("GET", "/api/v1/jobs", token=token)
results.append(("GET /jobs", s, "count=" + str(len(c)) if isinstance(c, list) else c))

# 7. 面试启动
s, c = req("POST", "/api/v1/interviews/start", token=token, body={
    "resume_id": "00000000-0000-0000-0000-000000000000",
    "job_id": "00000000-0000-0000-0000-000000000000",
    "round": "hr"
})
results.append(("POST /interviews/start", s, c))

# 8. 技能雷达图
s, c = req("GET", "/api/v1/skills/radar?direction=backend", token=token)
results.append(("GET /skills/radar", s, c))

# 9. 技能树
s, c = req("GET", "/api/v1/skills/tree?direction=backend", token=token)
results.append(("GET /skills/tree", s, "OK" if s == 200 else c))

# 10. 技能差距分析
s, c = req("POST", "/api/v1/skills/gap", token=token, body={
    "resume_id": "00000000-0000-0000-0000-000000000000",
    "target_direction": "backend"
})
results.append(("POST /skills/gap", s, c))

# 11. 投递列表
s, c = req("GET", "/api/v1/applications", token=token)
results.append(("GET /applications", s, "count=" + str(len(c)) if isinstance(c, list) else c))

# 12. 投递统计
s, c = req("GET", "/api/v1/applications/stats", token=token)
results.append(("GET /applications/stats", s, c))

# 13. 创建投递
s, c = req("POST", "/api/v1/applications", token=token, body={
    "company": "测试公司",
    "position": "后端工程师",
    "stage": "applied",
    "city": "北京"
})
results.append(("POST /applications", s, "OK" if s == 200 else c))

# 14. 教练工具列表
s, c = req("GET", "/api/v1/coach/tools", token=token)
results.append(("GET /coach/tools", s, "count=" + str(len(c)) if isinstance(c, list) else c))

# 15. 教练对话
s, c = req("POST", "/api/v1/coach/chat", token=token, body={"message": "你好，帮我分析一下求职状态"})
results.append(("POST /coach/chat", s, "OK" if s == 200 else c))

# 16. 教练报告
s, c = req("POST", "/api/v1/coach/report", token=token, body={})
results.append(("POST /coach/report", s, c))

# 17. 成长雷达图
s, c = req("GET", "/api/v1/growth/radar", token=token)
results.append(("GET /growth/radar", s, c))

# 18. 成长趋势
s, c = req("GET", "/api/v1/growth/trend", token=token)
results.append(("GET /growth/trend", s, c))

# 19. 复盘报告列表
s, c = req("GET", "/api/v1/reviews", token=token)
results.append(("GET /reviews", s, "count=" + str(len(c)) if isinstance(c, list) else c))

# 20. 无 token 访问受保护接口（应 401）
s, c = req("GET", "/api/v1/auth/me")
results.append(("GET /auth/me (no token)", s, c))

# 21. 错误密码登录（应 401）
s, c = req("POST", "/api/v1/auth/login", body={"email": "test@qiuzhimiao.com", "password": "wrong"})
results.append(("POST /auth/login (wrong pwd)", s, c))

print("=" * 80)
print("API 测试结果汇总")
print("=" * 80)
ok = 0
fail = 0
for name, status, info in results:
    marker = "OK " if 200 <= status < 300 else "FAIL"
    info_str = str(info)[:100] if not isinstance(info, str) else info[:100]
    print(f"[{marker}] {status:3d} {name:40s} {info_str}")
    if 200 <= status < 300:
        ok += 1
    else:
        fail += 1
print("=" * 80)
print(f"通过: {ok}  失败: {fail}  总计: {ok+fail}")
