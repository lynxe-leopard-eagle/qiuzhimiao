import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@qiuzhimiao.com"
TEST_PASSWORD = "test123456"

results = []
token = None
data = {}

def test(case_id, name, method, path, headers=None, json_data=None, expected_status=200, use_token=True):
    url = f"{BASE_URL}{path}"
    start = time.time()
    
    try:
        if headers is None:
            headers = {}
        if token and use_token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method.upper() == "GET":
            resp = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            resp = requests.post(url, headers=headers, json=json_data)
        elif method.upper() == "PUT":
            resp = requests.put(url, headers=headers, json=json_data)
        elif method.upper() == "DELETE":
            resp = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        elapsed = time.time() - start
        
        if resp.status_code == expected_status:
            status = "PASS"
            # Save data
            try:
                body = resp.json()
                if path == "/resumes" and method == "GET":
                    data["resumes"] = body
                if path == "/jobs" and method == "GET":
                    data["jobs"] = body
                if path == "/interviews" and method == "GET":
                    data["interviews"] = body
                if path == "/applications" and method == "GET":
                    data["applications"] = body
            except:
                pass
        else:
            status = "FAIL"
        
        results.append({
            "case_id": case_id,
            "name": name,
            "status": status,
            "expected": expected_status,
            "actual": resp.status_code,
            "response_time": round(elapsed * 1000, 1)
        })
        print(f"  {case_id}: {name} - {status} ({round(elapsed*1000,1)}ms)")
        
    except Exception as e:
        elapsed = time.time() - start
        results.append({
            "case_id": case_id,
            "name": name,
            "status": "ERROR",
            "expected": expected_status,
            "actual": str(e),
            "response_time": round(elapsed * 1000, 1)
        })
        print(f"  {case_id}: {name} - ERROR ({round(elapsed*1000,1)}ms): {e}")

print("=" * 60)
print("求职喵系统 API 测试")
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# 认证模块
print("\n--- 认证模块 ---")
test("AUTH-001", "正常登录", "POST", "/auth/login", 
     json_data={"email": TEST_EMAIL, "password": TEST_PASSWORD}, expected_status=200)

# 获取token
try:
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        print(f"  登录成功，获取token")
except Exception as e:
    print(f"  登录失败: {e}")

# 简历模块
print("\n--- 简历模块 ---")
test("RES-001", "获取简历列表", "GET", "/resumes", expected_status=200)

if data.get("resumes") and len(data["resumes"]) > 0:
    resume_id = data["resumes"][0]["id"]
    test("RES-002", "获取单个简历", "GET", f"/resumes/{resume_id}", expected_status=200)

test("RES-003", "获取不存在简历", "GET", "/resumes/invalid-uuid-1234", expected_status=400)
test("RES-004", "未认证获取简历列表", "GET", "/resumes", use_token=False, expected_status=401)

# 岗位模块
print("\n--- 岗位模块 ---")
test("JOB-001", "获取岗位列表", "GET", "/jobs", expected_status=200)

if data.get("jobs") and len(data["jobs"]) > 0:
    job_id = data["jobs"][0]["id"]
    test("JOB-002", "获取单个岗位", "GET", f"/jobs/{job_id}", expected_status=200)

test("JOB-003", "创建岗位", "POST", "/jobs", 
     json_data={"title": "测试岗位", "company": "测试公司", "description": "测试描述"}, expected_status=200)

# 面试模块
print("\n--- 面试模块 ---")
test("INT-001", "获取面试列表", "GET", "/interviews", expected_status=200)

# 投递记录模块
print("\n--- 投递记录模块 ---")
test("APP-001", "获取投递列表", "GET", "/applications", expected_status=200)
test("APP-002", "创建投递", "POST", "/applications", 
     json_data={"company": "测试公司", "position": "测试职位"}, expected_status=200)

# 性能测试
print("\n--- 性能测试 ---")
if data.get("resumes") and len(data["resumes"]) > 0:
    times = []
    for i in range(5):
        start = time.time()
        requests.get(f"{BASE_URL}/resumes", headers={"Authorization": f"Bearer {token}"})
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times) * 1000
    results.append({
        "case_id": "PERF-001",
        "name": "响应时间测试",
        "status": "PASS" if avg_time < 1000 else "WARN",
        "expected": "< 1000ms",
        "actual": f"{avg_time:.1f}ms",
        "response_time": avg_time
    })
    print(f"  PERF-001: 响应时间测试 - 平均 {avg_time:.1f}ms")

# 生成报告
print("\n" + "=" * 60)
print("测试报告")
print("=" * 60)

passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
errors = sum(1 for r in results if r["status"] == "ERROR")
warns = sum(1 for r in results if r["status"] == "WARN")
total = len(results)

print(f"\n统计: 总数={total}, 通过={passed}, 失败={failed}, 错误={errors}, 警告={warns}")
print(f"通过率: {passed/total*100:.1f}%")

print("\n详细结果:")
print("-" * 70)
print(f"{'用例ID':<12} {'状态':<6} {'时间(ms)':<10} {'场景'}")
print("-" * 70)
for r in results:
    print(f"{r['case_id']:<12} {r['status']:<6} {r['response_time']:<10} {r['name']}")
    if r["status"] != "PASS":
        print(f"          预期: {r['expected']}, 实际: {r['actual']}")

# 保存报告
report = {
    "time": datetime.now().isoformat(),
    "summary": {"total": total, "passed": passed, "failed": failed, "errors": errors},
    "results": results
}
with open("test_results.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n报告已保存到 test_results.json")