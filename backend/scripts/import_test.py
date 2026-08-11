"""常驻库 Excel 导入接口测试：生成测试 xlsx 上传验证重名跳过与非法职业。

用法（后端运行时执行）：python scripts/import_test.py
"""
import io
import json
import time
import urllib.error
import urllib.request

from openpyxl import Workbook

BASE = "http://127.0.0.1:8000"
UNIQUE_NAME = f"王五{int(time.time())}"


def login() -> str:
    req = urllib.request.Request(
        BASE + "/api/v1/auth/login",
        data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def build_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(["姓名", "主职业", "副职业", "状态", "备注"])
    ws.append([UNIQUE_NAME, "碎梦", "玄机", "正式", "主C"])
    ws.append(["张三", "铁衣", "", "正式", "重复名应跳过"])
    ws.append(["赵六", "法师", "", "替补", "非法职业应跳过"])
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def upload(token: str, content: bytes) -> tuple[int, dict]:
    boundary = "----ImportTestBoundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="members.xlsx"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        BASE + "/api/v1/members/import",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


if __name__ == "__main__":
    token = login()
    status, body = upload(token, build_xlsx())
    print("导入结果", status, body)
    assert status == 200, "导入接口应返回 200"
    assert body["imported"] == 1, f"应导入 1 条（{UNIQUE_NAME}），实际 {body['imported']}"
    assert body["skipped"] == 2, f"应跳过 2 条（重名+非法职业），实际 {body['skipped']}"
    print("[PASS] Excel 导入测试通过")
