# 部署文档

> 本文档描述生产服务器的实际部署架构与运维流程（2026-09-15 按服务器实况核对更新：单层 TLS）。
> 文中服务器地址、用户名、域名等一律使用**占位符**；真实值仅保存在本地 `deploy.sh`
> 与服务器配置中（`deploy.sh` 已被 `.gitignore` 排除，本文件会随仓库提交，严禁写入敏感信息）。

## 一、生产环境概况

| 项目 | 值 |
|------|-----|
| 服务器 | `<SERVER_IP>`（Ubuntu 22.04，SSH 密钥登录，用户 `<USER>`） |
| 项目目录 | `~/nsh-management`（非 git 仓库，靠本地 `deploy.sh` 打包更新） |
| 域名 | `<YOUR_DOMAIN>` / `www.<YOUR_DOMAIN>`（HTTPS，Let's Encrypt 证书） |
| 同机共存 | 全局反向代理 `nginx-proxy` 容器及另一独立站点服务（互不影响，均不归本项目管理） |

## 二、部署架构

```
浏览器 ─ 80/443 ──> nginx-proxy 容器（全局入口，**唯一 TLS 终止点**，配置只读挂载于宿主机）
                        │  proxy_pass http://nsh-management-frontend-1:80（容器网络明文）
                        │  （限流 api 20r/s burst 40、login 5r/m burst 3，按真实客户端 IP；
                        │    安全响应头 / HTTP→HTTPS 跳转 / 默认 server 444 也都在这一层）
                        ▼
             nsh-management-frontend-1（Nginx，容器内 :80，无宿主端口映射、无证书挂载）
                        ├── /          → 前端静态资源（SPA 回退 + 缓存头）
                        ├── /api/*     → proxy_pass http://backend:8000
                        └── client_max_body_size 20m（Excel 导入上限）
                        ▼
             nsh-management-backend-1（FastAPI :8000，内网，gosu appuser 降权运行）
                        ├── 卷 nsh-data  → /app/data/nsh.db（SQLite）
                        └── 卷 nsh-logs  → /app/logs（文件日志，10MB×5 轮转）
```

- `nginx-proxy` 为同机多个站点共用的反向代理，frontend 容器接入外部网络 `proxy-net` 供其回源。
- **单层 TLS（2026-09-15 调整）**：TLS 终止、证书、限流、安全响应头、HTTP→HTTPS 跳转、默认 server
  兜底全部只在 `nginx-proxy` 一层完成；frontend 容器退化为「静态资源 + `/api` 反代」，
  容器内明文 `:80`、**不映射宿主端口**（原 8080/8443 已移除）、不再挂载证书。
- 真实客户端 IP 链路：边缘层写 `X-Real-IP` / `X-Forwarded-For`（后者用
  `$remote_addr` **覆盖**客户端传入值以防伪造审计 IP），内层以
  `set_real_ip_from 172.20.0.0/16` + `real_ip_header X-Forwarded-For` 识别，
  反代 backend 时原样透传。**内层不得用 `$remote_addr` / `$proxy_add_x_forwarded_for`
  覆盖这两个头**，否则真实 IP 会被冲成容器 IP（曾导致限流退化为「全站共享桶」、登录审计 IP 记为容器 IP）。
- 边缘层 upstream 启用 keepalive(32)，内层不再做 TLS：每请求少一次 TLS 握手与连接建立。
- 数据库迁移在**容器每次启动时自动执行**（Dockerfile CMD 含 `alembic upgrade head`），
  当前 head：`o9p0q1r2s3t4`（member_game_id_requests 游戏 ID 修改申请表；此前为 `n8o9p0q1r2s3` 出勤备注列）。
- SQLite 以 **WAL 模式**运行（`journal_mode=WAL` + `synchronous=NORMAL` + `busy_timeout=30s`，
  见 `backend/app/core/database.py` 连接事件），读写不互斥；**备份方式需注意 WAL 文件**（见第五节）。
- 后端以 `appuser`（非 root）运行，`entrypoint.sh` 负责修复 `/app/data`、`/app/logs`
  目录属主后降权。
- 前端静态资源已启用 gzip 传输 + `/assets/` 一年强缓存（immutable）+ `index.html` no-store
  （`frontend/nginx.conf`，2026-09-11 生效；no-store 为 2026-09-11 下午针对微信端
  缓存旧 HTML 问题强化，index.html 同时内嵌 meta 缓存标签，见 `frontend/index.html`）。

## 三、日常更新流程（一键）

在**本地项目根目录**执行：

```bash
./deploy.sh
```

流程：本地 tar 打包（约 2.4M）→ scp 上传 → 服务器解压 → `docker compose up -d --build`
→ 健康检查。数据双卷不受影响，迁移自动执行。

### deploy.sh 打包排除清单（⚠️ 严禁移除）

| 排除项 | 原因 |
|--------|------|
| `docker-compose.yml` | 服务器版本与本地的**网络配置不同**（frontend 无宿主端口映射 + proxy-net），覆盖即宕机 |
| `frontend/nginx.conf`(.example) / `frontend/Dockerfile` / `backend/Dockerfile` / `backend/entrypoint.sh` / `backend/alembic.ini` | 构建输入与服务器配置可能漂移，只保留服务器版本 |
| `data/`、`*.db`、`backend/logs/`、`.env`、`_backup/` 等 | 本地数据/密钥/日志严禁上服务器 |

> 教训记录（2026-09-07）：曾新增 `--exclude='logs'`（未锚定路径）导致
> `frontend/src/views/logs/` 整个目录被排除，前端构建失败。排除规则必须带路径锚定，
> 如 `--exclude='backend/logs'`。

### 服务器配置类文件的变更规则

以下文件**只能直接在服务器上改**（先 `cp xxx xxx.bak-日期` 备份），本地同名文件仅作参考：

- `docker-compose.yml`（端口、网络、卷）
- `backend/Dockerfile`、`backend/entrypoint.sh`
- `frontend/nginx.conf`、`frontend/Dockerfile`
- `.env`

> 2026-09-11 同步记录：`frontend/nginx.conf`（gzip + `/assets/` immutable 缓存 + `index.html`
> no-cache）与 `frontend/Dockerfile`（`build:only` 跳过 vue-tsc 类型检查）已通过
> 备份（`*.bak-20260911`）+ scp 覆盖的方式手动同步至与本地一致。
> 2026-09-11 下午追加：`index.html` 缓存头由 no-cache 强化为 **no-store + Pragma**（微信
> 内置浏览器 X5/XWeb 在仅 no-cache 时仍可能使用磁盘缓存，导致部署后微信端打开旧页面），
> 本地 `frontend/nginx.conf` 与 `frontend/nginx.conf.example` 均已更新，**服务器侧需再次
> 手动同步 nginx.conf 并重建 frontend 镜像**（`index.html` 内嵌 meta 缓存标签随构建产物进入镜像）。
> 后续若再修改这两个文件，仍需重复"服务器侧手动同步"流程（`deploy.sh` 排除清单不变）。
>
> 2026-09-15 同步记录（单层 TLS 改造）：`frontend/nginx.conf`（内层改明文 80：删 443 监听、
> 证书引用、HTTP→HTTPS 跳转、限流 zone 与安全头；加 `set_real_ip_from` 与 IP 头透传）、
> `nginx-proxy/conf.d/nsh-management.conf`（反代改 `http://…:80` + upstream
> keepalive，删 `proxy_ssl_verify off`）、`docker-compose.yml`（frontend 删
> `/etc/letsencrypt` 与 `/var/www/certbot` 挂载、删 8080/8443 宿主端口）三者均已
> 按「备份（`*.bak-20260915`）→ 改文件 → 重建镜像 → 热重载」在服务器侧落地并验证；
> 切换采用两阶段（内层先 80+443 双监听 → 边缘切 80 → 收尾删 443），配置切换零停机，
> 仅容器重建瞬间有约 1 秒 502。

**重要**：改动 `entrypoint.sh` / `Dockerfile` / `nginx.conf` 后必须
`docker compose up -d --build` 重建对应镜像才生效（nginx.conf 随 frontend 镜像 COPY 进容器，
`up -d` 不重建时旧版仍在）。

## 四、日志系统

| 层 | 位置 | 说明 |
|----|------|------|
| 文件日志 | 卷 `nsh-logs` → `/app/logs/app.log` | 统一格式，含 uvicorn access/error；RotatingFileHandler 10MB×5 自动轮转；**UTC 时间戳** |
| 审计日志 | SQLite 表 `operation_logs`（库内） | 所有写操作（POST/PUT/DELETE/PATCH）+ 5xx 错误自动落库；登录成功/失败手动埋点；detail 已脱敏（password/token 等不落库） |
| 页面查看 | 站点侧边栏「系统日志」（仅开发者账号） | 概览统计（今日操作/错误、近 7 天错误分布，北京时间口径）+ 筛选分页 + 清理 |
| 保留策略 | 审计日志默认保留 **90 天**，启动时自动清理过期记录；页面亦可手动清理（操作本身会被审计） |

运维排查路径：页面看审计 → `docker compose logs -f backend` 看实时控制台 →
`/app/logs/app.log` 看历史文件日志。

## 五、备份与恢复

> ⚠️ 数据库已切换 **WAL 模式**：运行中直接 `cp nsh.db` 可能不含尚未合并的 `-wal`
> 文件内容，导致备份缺最新写入。请使用下方方式一（在线安全）或方式二（停服拷贝）。

```bash
# 方式一（推荐，在线安全）：SQLite backup API 生成一致性快照后拷出
docker compose exec -T backend python -c "
import sqlite3
src = sqlite3.connect('/app/data/nsh.db')
dst = sqlite3.connect('/app/data/nsh-backup.db')
src.backup(dst); dst.close(); src.close()"
docker run --rm -v nsh-management_nsh-data:/data -v $PWD:/backup alpine \
  sh -c "cp /data/nsh-backup.db /backup/nsh-$(date +%F).db && rm /data/nsh-backup.db"

# 方式二（停服拷贝）：WAL 模式下需一并复制 -wal/-shm 文件
docker compose stop backend
docker run --rm -v nsh-management_nsh-data:/data -v $PWD:/backup alpine \
  sh -c "cp /data/nsh.db* /backup/"
docker compose start backend

# 恢复（停服后覆盖，再启动；WAL 模式下同时清理旧 -wal/-shm 避免不一致）
docker compose stop backend
docker run --rm -v nsh-management_nsh-data:/data -v $PWD:/backup alpine \
  sh -c "rm -f /data/nsh.db-wal /data/nsh.db-shm && cp /backup/nsh-YYYY-MM-DD.db /data/nsh.db"
docker compose start backend
```

> 卷的实际名称带 compose 项目前缀：`nsh-management_nsh-data` / `nsh-management_nsh-logs`
>（`docker volume ls | grep nsh` 可查）。切勿 `docker compose down -v`。

## 六、环境变量（服务器 `~/nsh-management/.env`）

| 键 | 用途 |
|----|------|
| `SECRET_KEY` | JWT 签名密钥（强随机） |
| `DEVELOPER_PASSWORD` / `ADMIN_PASSWORD` / `MEMBER_PASSWORD` | 三角色密码（仅首次建库生效） |

敏感内容，严禁写入任何入库文件；修改 `SECRET_KEY` 会使所有登录态失效。

## 七、常见问题

### Q1：宿主机 `curl 127.0.0.1:8080` 连不上？

2026-09-15 起 frontend **不再映射任何宿主端口**（8080/8443 已移除），8080 无监听属正常现象；
即便有监听，安全组/防火墙也会拦截直连。不要以此判断服务故障，**以域名入口为准**：
`curl -sk -o /dev/null -w '%{http_code}' -H 'Host: <YOUR_DOMAIN>' https://127.0.0.1/`
应返回 200。

### Q2：backend 容器反复重启（Restarting）？

`docker logs --tail 30 nsh-management-backend-1` 查原因。历史案例：
`PermissionError: '/app/logs/app.log'` —— 卷 root 属主且镜像内 entrypoint.sh 是旧版
（无 `chown /app/logs`）。修复：确认服务器 `backend/entrypoint.sh` 为新版后
`docker compose up -d --build backend` 重建镜像。

### Q3：部署后页面 500 / 接口报"表不存在"？

迁移未执行。检查 `docker compose exec backend alembic current` 是否为 head；
CMD 启动即迁移，通常重启容器即可。

### Q4：部署后数据丢失？

数据在卷中不会因 `up -d --build` 丢失。若丢失，检查是否误用了**本地** compose 覆盖
服务器（会导致容器重建到错误配置），按第五节备份恢复。

### Q5：SSH 连不上（超时）？

检查云厂商安全组 22 端口源 IP 白名单；443 能通而 22 超时即为白名单问题。

## 八、与本地开发环境的差异对照

| 项目 | 本地开发 | 生产服务器 |
|------|---------|-----------|
| 入口 | Vite dev server :5173（proxy /api） | nginx-proxy :443（唯一 TLS 终止）→ frontend :80（容器网络明文） |
| 后端 | `uvicorn --reload :8000` | 容器内单 worker :8000（gosu appuser） |
| 数据库 | `backend/data/nsh.db` | 卷 `nsh-data` |
| 文件日志 | `backend/logs/app.log` | 卷 `nsh-logs` |
| 配置 | `core/config.py` 默认值 + 本地 `.env` | 服务器 `.env` |
| compose | 端口 80/443，仅 nsh-net | frontend 无宿主端口，nsh-net + proxy-net（external） |
| 更新方式 | — | 本地 `./deploy.sh` 一键 |
