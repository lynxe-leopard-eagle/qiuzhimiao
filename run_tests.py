import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any

import httpx

BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@qiuzhimiao.com"
TEST_PASSWORD = "test123456"

class TestResult:
    def __init__(self, case_id: str, name: str, status: str, expected: str, actual: str, response_time: float = 0):
        self.case_id = case_id
        self.name = name
        self.status = status
        self.expected = expected
        self.actual = actual
        self.response_time = response_time

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "name": self.name,
            "status": self.status,
            "expected": self.expected,
            "actual": self.actual,
            "response_time": round(self.response_time, 2)
        }

class TestSuite:
    def __init__(self):
        self.results: List[TestResult] = []
        self.token = None
        self.client = httpx.AsyncClient()
        self.data: Dict[str, Any] = {}

    async def login(self):
        try:
            start = time.time()
            resp = await self.client.post(
                f"{BASE_URL}/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            elapsed = time.time() - start
            if resp.status_code == 200:
                self.token = resp.json().get("access_token")
                return True, elapsed
            return False, elapsed
        except Exception as e:
            return False, 0

    async def run_test(self, case_id: str, name: str, method: str, path: str, 
                       headers: dict = None, json_data: dict = None, 
                       expected_status: int = 200, expected_contains: str = None,
                       use_token: bool = True):
        url = f"{BASE_URL}{path}"
        start = time.time()
        
        try:
            if headers is None:
                headers = {}
            if self.token and use_token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            if method.upper() == "GET":
                resp = await self.client.get(url, headers=headers)
            elif method.upper() == "POST":
                resp = await self.client.post(url, headers=headers, json=json_data)
            elif method.upper() == "PUT":
                resp = await self.client.put(url, headers=headers, json=json_data)
            elif method.upper() == "DELETE":
                resp = await self.client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            elapsed = time.time() - start
            actual = f"Status: {resp.status_code}"
            
            if resp.status_code == expected_status:
                if expected_contains and expected_contains not in resp.text:
                    status = "FAIL"
                    actual += f", Body: {resp.text[:200]}"
                else:
                    status = "PASS"
                    # 保存有用的数据
                    if path == "/resumes" and method == "GET":
                        self.data["resumes"] = resp.json()
                    if path == "/jobs" and method == "GET":
                        self.data["jobs"] = resp.json()
                    if path == "/interviews" and method == "GET":
                        self.data["interviews"] = resp.json()
                    if path == "/applications" and method == "GET":
                        self.data["applications"] = resp.json()
            else:
                status = "FAIL"
                actual += f", Body: {resp.text[:200]}"
            
            self.results.append(TestResult(
                case_id=case_id,
                name=name,
                status=status,
                expected=f"Status: {expected_status}" + (f", Contains: {expected_contains}" if expected_contains else ""),
                actual=actual,
                response_time=elapsed
            ))
            
        except Exception as e:
            elapsed = time.time() - start
            self.results.append(TestResult(
                case_id=case_id,
                name=name,
                status="ERROR",
                expected=f"Status: {expected_status}",
                actual=f"Exception: {str(e)[:200]}",
                response_time=elapsed
            ))

    async def run_all(self):
        print("=" * 60)
        print("开始执行求职喵系统 API 测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 认证模块测试
        print("\n--- 认证模块测试 ---")
        await self.run_test("AUTH-001", "正常登录", "POST", "/auth/login", 
                            json_data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                            expected_status=200, expected_contains="access_token")
        
        await self.run_test("AUTH-002", "错误密码登录", "POST", "/auth/login",
                            json_data={"email": TEST_EMAIL, "password": "wrongpass"},
                            expected_status=401)
        
        await self.run_test("AUTH-003", "无用户登录", "POST", "/auth/login",
                            json_data={"email": "nonexistent@test.com", "password": TEST_PASSWORD},
                            expected_status=401)
        
        await self.run_test("AUTH-004", "缺少参数登录", "POST", "/auth/login",
                            json_data={"password": TEST_PASSWORD},
                            expected_status=422)

        # 登录获取token
        success, _ = await self.login()
        if not success:
            print("\n登录失败，无法继续测试")
            return

        # 简历模块测试
        print("\n--- 简历模块测试 ---")
        await self.run_test("RES-001", "获取简历列表", "GET", "/resumes",
                            expected_status=200)
        
        if self.data.get("resumes"):
            resume_id = self.data["resumes"][0]["id"]
            self.data["resume_id"] = resume_id
            await self.run_test("RES-002", "获取单个简历", "GET", f"/resumes/{resume_id}",
                                expected_status=200)
            
            await self.run_test("RES-005", "简历诊断", "POST", "/resumes/diagnose",
                                json_data={"resume_id": resume_id},
                                expected_status=200)
        
        await self.run_test("RES-003", "获取不存在简历", "GET", "/resumes/invalid-uuid-1234",
                            expected_status=400)
        
        await self.run_test("RES-004", "未认证获取简历列表", "GET", "/resumes",
                            use_token=False,
                            expected_status=401)

        # 岗位模块测试
        print("\n--- 岗位模块测试 ---")
        await self.run_test("JOB-001", "获取岗位列表", "GET", "/jobs",
                            expected_status=200)
        
        if self.data.get("jobs"):
            job_id = self.data["jobs"][0]["id"]
            self.data["job_id"] = job_id
            await self.run_test("JOB-002", "获取单个岗位", "GET", f"/jobs/{job_id}",
                                expected_status=200)
            
            await self.run_test("JOB-004", "岗位分析", "POST", "/jobs/analyze",
                                json_data={"job_description": "测试岗位描述", "title": "测试岗位"},
                                expected_status=200)
        
        await self.run_test("JOB-003", "创建岗位", "POST", "/jobs",
                            json_data={"title": "测试岗位", "company": "测试公司", "description": "测试描述"},
                            expected_status=200)

        # 面试模块测试
        print("\n--- 面试模块测试 ---")
        await self.run_test("INT-001", "获取面试列表", "GET", "/interviews",
                            expected_status=200)
        
        await self.run_test("INT-002", "开始面试", "POST", "/interviews/start",
                            json_data={"round": "tech1"},
                            expected_status=200)
        
        if self.data.get("interviews"):
            interview_id = self.data["interviews"][0]["id"]
            await self.run_test("INT-003", "获取面试消息", "GET", f"/interviews/{interview_id}/messages",
                                expected_status=200)

        # 投递记录模块测试
        print("\n--- 投递记录模块测试 ---")
        await self.run_test("APP-001", "获取投递列表", "GET", "/applications",
                            expected_status=200)
        
        await self.run_test("APP-002", "创建投递", "POST", "/applications",
                            json_data={"company": "测试公司", "position": "测试职位"},
                            expected_status=200)
        
        if self.data.get("applications"):
            app_id = self.data["applications"][0]["id"]
            await self.run_test("APP-003", "更新投递", "PUT", f"/applications/{app_id}",
                                json_data={"stage": "offer"},
                                expected_status=200)
            
            await self.run_test("APP-004", "删除投递", "DELETE", f"/applications/{app_id}",
                                expected_status=204)

        # 性能测试
        print("\n--- 性能测试 ---")
        await self.run_performance_tests()

    async def run_performance_tests(self):
        # 响应时间测试
        if self.data.get("resumes") and len(self.data["resumes"]) > 0 and self.data.get("jobs") and len(self.data["jobs"]) > 0:
            resume_id = self.data["resumes"][0]["id"]
            job_id = self.data["jobs"][0]["id"]
            
            # 多次请求测量响应时间
            times = []
            for i in range(5):
                start = time.time()
                await self.client.get(f"{BASE_URL}/resumes", headers={"Authorization": f"Bearer {self.token}"})
                elapsed = time.time() - start
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            self.results.append(TestResult(
                case_id="PERF-001",
                name="响应时间测试",
                status="PASS" if avg_time < 1.0 else "WARN",
                expected="平均响应时间 < 1000ms",
                actual=f"平均: {avg_time*1000:.2f}ms, 最大: {max_time*1000:.2f}ms, 最小: {min_time*1000:.2f}ms",
                response_time=avg_time
            ))

            # 并发测试
            async def make_request():
                start = time.time()
                try:
                    await self.client.get(f"{BASE_URL}/jobs", headers={"Authorization": f"Bearer {self.token}"})
                    return time.time() - start, True
                except:
                    return time.time() - start, False
            
            tasks = [make_request() for _ in range(10)]
            results = await asyncio.gather(*tasks)
            
            success_count = sum(1 for _, ok in results if ok)
            total_time = sum(t for t, _ in results)
            
            self.results.append(TestResult(
                case_id="PERF-002",
                name="并发处理测试(10请求)",
                status="PASS" if success_count == 10 else "FAIL",
                expected="10个并发请求全部成功",
                actual=f"成功: {success_count}/10, 总耗时: {total_time*1000:.2f}ms",
                response_time=total_time
            ))

    def generate_report(self):
        print("\n" + "=" * 60)
        print("测试报告")
        print("=" * 60)

        # 统计
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        errors = sum(1 for r in self.results if r.status == "ERROR")
        warns = sum(1 for r in self.results if r.status == "WARN")

        print(f"\n测试结果统计:")
        print(f"  总数: {total}")
        print(f"  通过: {passed}")
        print(f"  失败: {failed}")
        print(f"  错误: {errors}")
        print(f"  警告: {warns}")
        print(f"  通过率: {passed/total*100:.1f}%")

        # 详细结果
        print("\n详细测试结果:")
        print("-" * 80)
        print(f"{'用例ID':<12} {'状态':<6} {'响应时间(ms)':<15} {'测试场景'}")
        print("-" * 80)
        
        for r in self.results:
            time_str = f"{r.response_time*1000:.1f}ms" if r.response_time else ""
            print(f"{r.case_id:<12} {r.status:<6} {time_str:<15} {r.name}")
            if r.status != "PASS":
                print(f"          预期: {r.expected}")
                print(f"          实际: {r.actual}")

        # 问题清单
        print("\n问题清单:")
        print("-" * 80)
        print(f"{'优先级':<8} {'用例ID':<12} {'问题描述'}")
        print("-" * 80)
        
        issue_count = 0
        for r in self.results:
            if r.status not in ("PASS", "WARN"):
                issue_count += 1
                priority = "高" if r.status == "ERROR" else "中"
                print(f"{priority:<8} {r.case_id:<12} {r.name}: {r.actual}")

        if issue_count == 0:
            print("  无问题")

        # 性能汇总
        print("\n性能测试结果:")
        print("-" * 80)
        for r in self.results:
            if r.case_id.startswith("PERF"):
                print(f"{r.case_id}: {r.name}")
                print(f"  状态: {r.status}")
                print(f"  结果: {r.actual}")

        # 测试结论
        print("\n测试结论:")
        print("-" * 80)
        if passed == total:
            print("✓ 所有测试用例通过，系统功能正常")
        elif failed + errors <= total * 0.2:
            print("✓ 大部分测试用例通过，系统基本功能正常，存在少量问题")
        else:
            print("✗ 存在较多问题，建议修复后重新测试")

        # 生成JSON报告
        report_data = {
            "test_time": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "warns": warns,
                "pass_rate": passed/total*100
            },
            "results": [r.to_dict() for r in self.results],
            "issues": [r.to_dict() for r in self.results if r.status not in ("PASS", "WARN")]
        }

        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存到: test_results.json")

async def main():
    suite = TestSuite()
    await suite.run_all()
    suite.generate_report()
    await suite.client.aclose()

if __name__ == "__main__":
    asyncio.run(main())