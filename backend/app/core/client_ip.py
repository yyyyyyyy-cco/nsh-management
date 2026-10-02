"""客户端 IP 解析：多层反向代理下统一取 X-Forwarded-For 首段。"""
from fastapi import Request


def get_client_ip(request: Request) -> str | None:
    """取真实客户端 IP：优先 XFF 首段，回退到直连对端地址。"""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    return request.client.host if request.client else None
