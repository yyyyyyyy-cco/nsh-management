# 部署文档

本系统采用 **Docker Compose** 方式部署：Nginx 托管前端静态资源并反向代理后端 API，FastAPI 单进程运行，数据存储于 SQLite 文件（Docker 卷持久化）。

## 部署架构

```
浏览器 ──HTTP 80──> Nginx (frontend 容器)
                     ├── /            → 前端静态资源 (dist, SPA 回退)
                     └── /api/*       → 反向代理 → FastAPI (backend 容器 :8000)
                                                      └── SQLite (/app/data/nsh.db, 卷 nsh-data)
```

- 前端：Vue 3 生产构建产物，由 Nginx 托管
- 后端：FastAPI + uvicorn（**单 worker**，避免 SQLite 写锁竞争）
- 数据库：SQLite 文件，挂载于 Docker 命名卷 `nsh-data`
- 后端容器不暴露端口到宿主机，仅 Nginx 通过 Compose 内部网络访问

## 前置要求

| 项目 | 要求 |
|------|------|
| 服务器 | Linux（Ubuntu 20.04+ / CentOS 7+ / Debian 11+ 等） |
| Docker | 20.10+（含 Compose v2 插件） |
| 网络 | 放行 TCP 80 端口（IP 直连方案，无域名） |

> 服务器无需安装 Python / Node，构建在容器内完成。

## 部署步骤

### 1. 上传项目代码

将项目上传至服务器（可用 `git clone`、scp、宝塔上传等），排除本地目录：

```bash
# 本机上传示例（rsync 排除开发目录）
rsync -av --exclude 'node_modules' --exclude '.venv' --exclude 'data' \
  --exclude '.git' --exclude 'memory-bank' ./ user@server:/opt/nsh-management/
```

### 2. 安装 Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker
docker compose version   # 确认 Compose v2 可用
```

### 3. 配置环境变量

```bash
cd /opt/nsh-management
cp .env.example .env
vi .env
```

`.env` 必须修改的变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `SECRET_KEY` | JWT 签名密钥，**生产必须替换为强随机值** | `openssl rand -hex 32` 生成 |
| `DEVELOPER_PASSWORD` | 开发者账号密码（仅首次建库生效） | 自定义强密码 |
| `ADMIN_PASSWORD` | 管理员账号密码（仅首次建库生效） | 自定义强密码 |
| `MEMBER_PASSWORD` | 帮众账号密码（仅首次建库生效） | 自定义强密码 |

### 4. 构建并启动

```bash
docker compose up -d --build
```

首次启动会自动完成：建表（alembic 迁移）→ 创建 developer/admin/member 账号 → 启动后端，Nginx 等待后端健康检查通过后对外服务。

### 5. 验证

```bash
curl -I http://服务器IP/              # 前端页面 200
curl http://服务器IP/api/v1/auth/me  # API 反代正常（未带 token 应返回 401 JSON）
docker compose ps                    # 两容器均为 Up (healthy)
```

浏览器访问 `http://服务器IP`，使用 `.env` 中设置的账号密码登录。

---

## 常用运维

### 查看日志

```bash
docker compose logs -f backend     # 后端日志
docker compose logs -f frontend    # Nginx 日志
```

### 升级版本

```bash
# 拉取新代码后
docker compose up -d --build       # 镜像重建 + 容器滚动更新，数据卷不丢
```

### 数据备份与恢复

SQLite 数据文件位于卷 `nsh-data`，宿主机路径：

```bash
docker volume inspect nsh-data     # 查看 Mountpoint
```

**备份**（推荐定时任务，服务运行中直接复制即可，SQLite 保证一致性）：

```bash
# 每周备份示例（crontab）
0 3 * * 1 cp "$(docker volume inspect nsh-data --format '{{.Mountpoint}}')/nsh.db" /backup/nsh-$(date +\%F).db
```

**恢复**：停服后覆盖数据库文件再启动：

```bash
docker compose stop backend
cp /backup/nsh-2026-08-17.db "$(docker volume inspect nsh-data --format '{{.Mountpoint}}')/nsh.db"
docker compose start backend
```

### 迁移开发数据（可选）

若需将本地开发库带到生产：

```bash
# 先停服
docker compose stop backend
# 覆盖卷内数据库
cp local-nsh.db "$(docker volume inspect nsh-data --format '{{.Mountpoint}}')/nsh.db"
docker compose start backend
```

> 全新部署建议直接使用 `init_db` 初始化，避免带入测试数据。

---

## 配置说明

### 环境变量（.env）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SECRET_KEY` | 无（必填） | JWT 签名密钥，生产必须设置 |
| `DEVELOPER_PASSWORD` | 无（必填） | 开发者账号密码，首次建库使用 |
| `ADMIN_PASSWORD` | 无（必填） | 管理员账号密码，首次建库使用 |
| `MEMBER_PASSWORD` | 无（必填） | 帮众账号密码，首次建库使用 |
| `DATABASE_URL` | `sqlite+aiosqlite:////app/data/nsh.db` | 数据库连接串，一般无需修改 |
| `LOGIN_MAX_FAILURES` / `LOGIN_LOCK_MINUTES` | `5` / `5` | 登录限流策略 |

### Nginx 关键配置（frontend/nginx.conf）

| 配置 | 值 | 说明 |
|------|-----|------|
| 监听端口 | `80` | 如需改端口改 `docker-compose.yml` 的 `ports` 映射 |
| `client_max_body_size` | `20m` | Excel 导入文件大小上限 |
| `/api/` 反代 | `http://backend:8000` | Compose 内部服务名 |
| SPA 回退 | `try_files ... /index.html` | 支持前端路由刷新 |

### Docker 镜像构建

- 后端：`python:3.11-slim`，启动命令 `alembic upgrade head && python -m app.init_db && uvicorn ... --workers 1`
- 前端：`node:18-alpine` 构建 → `nginx:alpine` 托管

---

## 常见问题

### Q1：访问 80 端口不通

1. 检查云服务器安全组 / 防火墙是否放行 80 端口（阿里云/腾讯云控制台入方向规则）
2. `docker compose ps` 确认容器状态
3. `curl http://127.0.0.1/` 在服务器本机验证

### Q2：后端健康检查失败，前端一直无法访问

```bash
docker compose logs backend    # 查看迁移/初始化报错
```

常见原因：`.env` 缺少 `DEVELOPER_PASSWORD` 等必填变量（`init_db` 会直接退出）。

### Q3：登录提示「网络错误」

确认 Nginx 反代正常：`curl http://服务器IP/api/v1/auth/me` 应返回 401 JSON 而非 404/502。502 表示后端未就绪，等待健康检查通过或查后端日志。

### Q4：升级后数据还在吗？

数据存于命名卷 `nsh-data`，`docker compose up -d --build` 不删除卷，数据保留。切勿在未备份时执行 `docker compose down -v`（会删除卷）。

---

## 与开发环境的关系

| 项目 | 开发环境 | 生产环境 |
|------|---------|---------|
| 前端 | Vite dev server :5173（proxy /api） | Nginx 托管构建产物 :80 |
| 后端 | uvicorn --reload :8000 | uvicorn 单 worker :8000（容器内） |
| 数据库 | `backend/data/nsh.db` | 卷 `nsh-data` 内 nsh.db |
| 配置 | 代码默认值 / 环境变量 | `.env` 文件 |
