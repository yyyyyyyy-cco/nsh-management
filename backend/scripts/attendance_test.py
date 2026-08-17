"""出勤库接口测试：一键导入、补人、替补导入、状态切换、保存、权限。

用法（后端运行时执行）：python scripts/attendance_test.py [base_url]
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"


def encode_path(path: str) -> str:
    if "?" in path:
        base, query = path.split("?", 1)
        return urllib.parse.quote(base, safe="/") + "?" + urllib.parse.quote(query, safe="=&%")
    return urllib.parse.quote(path, safe="/")


def request(method: str, path: str, body: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + encode_path(path), data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def login(username: str, password: str) -> str:
    status, body = request("POST", "/api/v1/auth/login", {"username": username, "password": password})
    assert status == 200, f"登录失败: {body}"
    return body["access_token"]


if __name__ == "__main__":
    admin = login("admin", "admin123")
    member = login("member", "member123")

    # 准备：一个替补成员 + 一个赛程
    status, body = request("POST", "/api/v1/members", {"name": "替补甲", "main_profession": "血河", "status": "substitute"}, token=admin)
    print("[1] 创建替补成员", status, body.get("id") if status == 200 else body)
    status, body = request("POST", "/api/v1/schedules", {"opponent": "出勤测试对手", "match_time": "2026-08-20T19:00:00", "rounds": 2}, token=admin)
    print("[2] 创建赛程", status, body.get("id") if status == 200 else body)
    schedule_id = body.get("id") if status == 200 else None
    assert schedule_id, "赛程创建失败"
    base = f"/api/v1/schedules/{schedule_id}/attendance"

    print("[3] 一键导入正式成员", request("POST", f"{base}/import-formal", token=admin))
    print("[4] 重复导入(幂等)", request("POST", f"{base}/import-formal", token=admin))
    status, body = request("GET", base, token=admin)
    print("[5] 出勤列表", status, body.get("stats"))
    print("[6] 添加补人", request("POST", f"{base}/fillers", {"name": "外援一号", "profession": "素问"}, token=admin))
    print("[7] 重复补人(应400)", request("POST", f"{base}/fillers", {"name": "外援一号", "profession": "素问"}, token=admin))
    print("[8] 替补候选", request("GET", f"{base}/substitute-candidates", token=admin))
    status, body = request("GET", f"{base}/substitute-candidates", token=admin)
    sub_ids = [m["id"] for m in body] if status == 200 else []
    print("[9] 导入替补", request("POST", f"{base}/import-substitutes", {"member_ids": sub_ids}, token=admin))

    status, body = request("GET", base, token=admin)
    records = body.get("items", [])
    print("[10] 出勤统计", status, body.get("stats"))
    first_id = records[0]["id"] if records else None
    print("[11] 单人切换请假", request("PUT", f"{base}/{first_id}/status", {"status": "leave"}, token=admin) if first_id else "跳过")
    batch_ids = [r["id"] for r in records[1:3]]
    print("[12] 批量切换正常", request("POST", f"{base}/batch-status", {"ids": batch_ids, "status": "normal"}, token=admin))
    print("[13] 保存考勤", request("POST", f"{base}/save", token=admin))
    print("[14] 帮众查看出勤", request("GET", base, token=member))
    print("[15] 帮众切换状态", request("PUT", f"{base}/{first_id}/status", {"status": "normal"}, token=member) if first_id else "跳过")
    print("[16] 帮众导入(应403)", request("POST", f"{base}/import-formal", token=member))
    print("[17] 删除补人记录", request("DELETE", f"{base}/{first_id}", token=admin) if first_id else "跳过")
    print("[18] 清理赛程", request("DELETE", f"/api/v1/schedules/{schedule_id}", token=admin))
