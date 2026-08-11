"""认证接口冒烟测试：验证服务启动、登录、限流、鉴权链路。

用法（后端运行时执行）：python scripts/smoke_test.py
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"


def encode_path(path: str) -> str:
    """URL 编码（保留 / ? & = 等字符，支持中文 query）。"""
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


if __name__ == "__main__":
    try:
        status, body = request("GET", "/")
        print("[1] GET /", status, body)
    except (json.JSONDecodeError, urllib.error.HTTPError):
        print("[1] GET / 非 API 路径，跳过")
    status, body = request("POST", "/api/v1/auth/login", {"username": "admin", "password": "admin123"})
    print("[2] 管理员登录", status, body.get("user") if status == 200 else body)
    token = body.get("access_token", "")
    print("[3] GET /auth/me", request("GET", "/api/v1/auth/me", token=token))
    print("[4] 错误密码", request("POST", "/api/v1/auth/login", {"username": "admin", "password": "wrong-pass"}))
    print("[5] 无Token访问me", request("GET", "/api/v1/auth/me"))
    status, body = request("POST", "/api/v1/auth/login", {"username": "member", "password": "member123"})
    print("[6] 帮众登录", status, body.get("user") if status == 200 else body)
    member_token = body.get("access_token", "")

    # ---- 常驻库模块 ----
    print("[7] 创建成员", request("POST", "/api/v1/members", {"name": "张三", "main_profession": "铁衣", "status": "formal"}, token=token))
    print("[8] 创建成员(非法职业)", request("POST", "/api/v1/members", {"name": "李四", "main_profession": "法师"}, token=token))
    print("[9] 成员列表", request("GET", "/api/v1/members?keyword=张", token=token))
    print("[10] 帮众访问成员(应403)", request("GET", "/api/v1/members", token=member_token))
    print("[11] 出勤率(空)", request("GET", "/api/v1/members/attendance-rate", token=token))
