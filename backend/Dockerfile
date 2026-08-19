FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

COPY . .

# 创建非 root 用户，安装 gosu 用于降权（使用阿里云 Debian 镜像源加速）
RUN useradd -r -s /usr/sbin/nologin appuser && \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends gosu && \
    rm -rf /var/lib/apt/lists/* && \
    chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

# 每次启动：迁移 → 初始化账号（幂等）→ 启动服务（SQLite 使用单 worker 避免写锁竞争）
CMD ["sh", "-c", "alembic upgrade head && python -m app.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
