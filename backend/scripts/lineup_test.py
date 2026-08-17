"""排表接口测试：空结构、候选池、保存校验、权限、级联。

用法（后端运行时执行）：python scripts/lineup_test.py [base_url]
"""
import json
import sys
import time
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


def empty_slots() -> list[dict]:
    return [{"slot_index": i, "member_id": None, "member_name": "", "remark": ""} for i in range(6)]


def build_teams(member_id: int | None, filler_name: str = "") -> list[dict]:
    teams = []
    for category, count in [("进攻1", 3), ("进攻2", 3), ("防守1", 2), ("防守2", 2)]:
        for idx in range(count):
            slots = empty_slots()
            if category == "进攻1" and idx == 0:
                slots[0] = {"slot_index": 0, "member_id": member_id, "member_name": "", "remark": "主T"}
                if filler_name:
                    slots[1] = {"slot_index": 1, "member_id": None, "member_name": filler_name, "remark": "补位"}
            teams.append({"category": category, "team_index": idx, "slots": slots})
    return teams


if __name__ == "__main__":
    admin = login("admin", "admin123")
    member_token = login("member", "member123")

    # 准备：创建成员（唯一名）+ 赛程 + 导入出勤
    name = f"排表测试{int(time.time())}"
    status, body = request("POST", "/api/v1/members", {"name": name, "main_profession": "铁衣", "status": "formal"}, token=admin)
    print("[1] 创建成员", status, body.get("name") if status == 200 else body)
    member_id = body.get("id") if status == 200 else None

    status, body = request("POST", "/api/v1/schedules", {"opponent": "排表测试队", "match_time": "2026-09-01T19:00:00", "rounds": 2}, token=admin)
    print("[2] 创建赛程", status, body.get("id") if status == 200 else body)
    schedule_id = body.get("id") if status == 200 else None

    print("[3] 导入正式成员", request("POST", f"/api/v1/schedules/{schedule_id}/attendance/import-formal", token=admin))
    status, body = request("GET", f"/api/v1/schedules/{schedule_id}/lineup/candidates", token=admin)
    print("[4] 候选池", status, [c["member_name"] for c in body] if status == 200 else body)

    status, body = request("GET", f"/api/v1/schedules/{schedule_id}/lineup", token=admin)
    print("[5] 空结构", status, f"队伍 {len(body['data'])} 支" if status == 200 else body)
    if status == 200:
        teams_ok = len(body["data"]) == 10 and all(len(t["slots"]) == 6 for t in body["data"])
        cats = [t["category"] for t in body["data"]]
        print("   结构校验", "10队x6槽 OK" if teams_ok else "FAIL", "分类", cats[:3], cats[6:])

    filler = f"补人{int(time.time())}"
    status, body = request("PUT", f"/api/v1/schedules/{schedule_id}/lineup", {"data": build_teams(member_id, filler)}, token=admin)
    print("[6] 保存排表", status, "OK" if status == 200 else body)
    if status == 200:
        slot = body["data"][0]["slots"][0]
        slot2 = body["data"][0]["slots"][1]
        print("   规范化姓名", f"{slot['member_name']}/{slot['remark']}", "补人", slot2["member_name"], "OK" if slot["member_name"] == name else "FAIL")

    bad_teams = build_teams(member_id)[:9]
    print("[7] 结构错误(9队)", request("PUT", f"/api/v1/schedules/{schedule_id}/lineup", {"data": bad_teams}, token=admin))
    print("[8] 非本帮会成员", request("PUT", f"/api/v1/schedules/{schedule_id}/lineup", {"data": build_teams(99999)}, token=admin))

    print("[9] 帮众GET排表", request("GET", f"/api/v1/schedules/{schedule_id}/lineup", token=member_token))
    print("[10] 帮众PUT排表(应403)", request("PUT", f"/api/v1/schedules/{schedule_id}/lineup", {"data": build_teams(member_id)}, token=member_token))
    print("[11] 帮众候选池(应403)", request("GET", f"/api/v1/schedules/{schedule_id}/lineup/candidates", token=member_token))

    print("[12] 删除赛程(级联)", request("DELETE", f"/api/v1/schedules/{schedule_id}", token=admin))
    print("[13] 删除成员", request("DELETE", f"/api/v1/members/{member_id}", token=admin))
    print("[PASS] 排表测试完成")
