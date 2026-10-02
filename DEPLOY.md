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

### 健康检查与在线 API 文档（2026-10-02 新增）

- **健康检查端点** `GET /health`（根路径；容器 `healthcheck` 探它）：进程可用且数据库可查询 →
  `200 {"status":"ok","database":"ok"}`；数据库不可用 → `503 {"status":"degraded","database":"error"}`。
  数据库异常刻意**不抛 500**：否则对外表现为「应用崩溃」而非「依赖不可用」，不利排查。
  同一端点也挂在 `/api/v1/health`，可经既有 `/api/*` 反向代理对外访问，供外部 uptime 监控探活；
  若不希望对外暴露，可在边缘 Nginx 拦掉该路径（探活改用内网方式）。
- **手动探活**：backend 不映射宿主端口，宿主机直接 `curl` 不通。可执行
  `docker compose exec backend python -c "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"`。
- **生产环境关闭在线 API 文档**：`/docs`、`/redoc`、`/openapi.json` 一律 404（本地开发环境保留，便于调试）。
  依据 OWASP Top 10:2025 A02（安全配置错误）。需要临时查阅接口时请在本地以开发环境运行后端，
  **不要在服务器上开启**。

## 三、日常更新流程（一键）

在**本地项目根目录**执行：

```bash
./deploy.sh
```

流程：本地 tar 打包（约 2.4M）→ scp 上传 → 服务器解压 → `docker compose up -d --build`
→ 健康检查。数据双卷不受影响，迁移自动执行。

> **2026-10-02 补充（合规化计划 W1-1/W1-2）**：
> - `deploy.sh` 本身不入库（含服务器信息），其**占位符模板已入库**为 `deploy.sh.example`——依据本节流程重建，含排除清单、路径锚定告警与非零退出的健康检查。新环境执行 `cp deploy.sh.example deploy.sh`，填写 `SERVER_IP` / `SERVER_USER` / `DOMAIN` 后使用。
> - `frontend/nginx.conf`（**占位符版**）现已入库，作为 frontend 镜像的构建输入：此前该文件不在仓库内，导致全新克隆在 `COPY nginx.conf` 一步直接构建失败。它仍在下方排除清单内，**服务器版本不受影响**；两边漂移由本节「服务器配置类文件的变更规则」管理。
> - `frontend/nginx.conf.example` 已收窄为**边缘层（B 段）模板**，内层（A 段）以 `frontend/nginx.conf` 为唯一副本，避免同一配置两处漂移。

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
| 错误率告警 | 后台循环（启动即查一次，之后每 `ALERT_CHECK_INTERVAL_MINUTES` 分钟，默认 15）：最近 `ALERT_WINDOW_MINUTES`（默认 30）分钟内 `level=error` 达 `ALERT_ERROR_THRESHOLD`（默认 20）条 → 写 **WARNING** 日志并（若配置 `ALERT_WEBHOOK_URL`）POST JSON 到 webhook；同一窗口内不重复通知（进程内去重）。阈值为 0 表示禁用。**未配置 webhook 时告警仍会写日志**，不静默 |

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

### 自动化备份（2026-10-02 新增，合规化计划 W3-2）

`scripts/backup-db.sh.example` 把上面的「方式一」自动化（复制为 `scripts/backup-db.sh` 使用）：

- **默认 dry-run**（`DRY_RUN=1`）只打印将执行的命令；确认无误后用 `DRY_RUN=0` 真正执行；
- 快照先在容器内生成并执行 `PRAGMA integrity_check`，**校验通过才拷出**——避免把坏库当备份；
- 产物 `$BACKUP_DIR/nsh-YYYYmmdd-HHMMSS.db`（默认 `~/nsh-backups`），默认保留 30 天（`RETENTION_DAYS`）；
- cron 示例（每日 03:30）与全部可调参数见脚本头部注释。

**为什么不能用 `cp`（本机实测，2026-10-02，Python 3.14 + SQLite）**：建库并写入 2000 行、**保持连接打开**时，
直接复制**主库文件**得到的副本报 `no such table: t`（表结构都还在 `-wal` 里）；而 `backup API` 生成的快照
读到 2000 行且 `integrity_check = ok`。这就是上方 ⚠️ 的实证依据。

### 恢复演练记录（每季一次）

| 日期 | 演练人 | 备份文件 | 恢复到 | 结果 | 备注 |
|------|--------|----------|--------|------|------|
| 2026-10-02（模板） | — | `nsh-YYYYmmdd-HHMMSS.db` | 非生产实例 | 待执行 | 首次演练按本节命令覆盖后，用 `PRAGMA integrity_check` + 登录冒烟验证 |

> 演练要求：①使用**真实备份产物**恢复（不是现场重新生成）；②在**非生产**实例上验证可登录、可读常驻库与出勤库；
> ③记录耗时与问题；④**禁止**在生产实例上演练恢复。

## 六、环境变量（服务器 `~/nsh-management/.env`）

> **表格口径（2026-10-02）**：§六 表格已按 `.env.example` 补全（此前只列了必需项，运行时可选变量缺失）；门禁 `scripts/check_env_docs.py` 会校验「`.env.example` 的每个键都在本文档出现」，因此**新增环境变量时必须同时更新两处**。

| 键 | 用途 |
|----|------|
| `SECRET_KEY` | JWT 签名密钥（强随机，`openssl rand -hex 32`） |
| `DEVELOPER_PASSWORD` / `ADMIN_PASSWORD` / `MEMBER_PASSWORD` | 三角色密码（仅首次建库生效） |
| `CORS_ORIGINS` | 允许的跨域来源（逗号分隔，可选）。默认值仅本地开发来源；生产由 Nginx **同源**反代 `/api`，通常**无需设置**；仅当 API 被跨域直连时显式列出。**不要填 `*`**（本项目 `allow_credentials=True`） |
| `ALERT_WEBHOOK_URL` | 错误率告警的 webhook 地址（可选）。**未配置时仍会在容器日志写 WARNING**（不静默）；阈值 / 窗口 / 检查间隔分别为 `ALERT_ERROR_THRESHOLD`（默认 20）/ `ALERT_WINDOW_MINUTES`（30）/ `ALERT_CHECK_INTERVAL_MINUTES`（15），阈值为 0 表示禁用 |
| `APP_ENV` | 运行环境标识。Compose 已在 backend 服务固定 `production`，此处**无需重复设置**；非 Compose 部署（k8s / 裸机）**必须显式设为 `production`**，否则启动弱密钥校验的兜底判定可能失效 |
| `DEBUG` | 调试模式（默认 `false`）。**生产必须保持 false**；生产环境下 `/docs`、`/redoc`、`/openapi.json` 亦被关闭 |
| `DATABASE_URL` | 数据库连接串（可选）。默认 `sqlite+aiosqlite:///<数据目录>/nsh.db`（容器内为挂载卷）；改用其它路径或外部数据库时才需设置，SQLite 路径须为绝对路径（四个斜杠） |
| `LOG_RETENTION_DAYS` | 审计日志保留天数（默认 `90`）：服务启动时清理更早的记录 |
| `DEVELOPER_USERNAME` / `ADMIN_USERNAME` / `MEMBER_USERNAME` | 首次初始化账号的登录名（默认 `developer` / `admin` / `member`，仅首次建库生效） |
| `DEFAULT_GUILD_NAME` | 首次建库创建的默认帮会名（默认「默认帮会」） |
| `ALERT_ERROR_THRESHOLD` / `ALERT_WINDOW_MINUTES` / `ALERT_CHECK_INTERVAL_MINUTES` | 错误率告警的阈值（默认 20 条）/ 统计窗口（30 分钟）/ 检查间隔（15 分钟）；阈值 0 表示禁用 |

敏感内容，严禁写入任何入库文件；修改 `SECRET_KEY` 会使所有登录态失效。

### 关键秘密清单（2026-10-02 新增，对应 ASVS 13.1.4）

> 本节是**秘密清单与管理策略的唯一落点**（环境变量取值见上一张表，本节不重复列默认值）。
> 判定口径：秘密 = 泄漏后可直接或间接获得权限、解密能力或身份的东西。

| 秘密 | 存放位置 | 访问边界（谁能读） | 泄漏影响（按严重度） |
|------|---------|------------------|--------------------|
| `SECRET_KEY` | 服务器 `.env`（`.gitignore` 忽略；`backend/.dockerignore` 亦排除，**不入镜像**） | 仅服务器部署账号/root | **最高**：可伪造任意角色（含 developer）的 JWT。经代码核实，它的唯一用途是 JWT 签发与校验（`backend/app/core/security.py`），不涉及口令哈希与审计 |
| `DEVELOPER_PASSWORD` / `ADMIN_PASSWORD` / `MEMBER_PASSWORD` | 服务器 `.env` | 同上 | 高：可直接登录对应初始账号。**仅在首次建库时生效**，改库后不再读取 |
| 账号口令（运行时） | 库内 `users.password_hash`（bcrypt）；另有 `users.plain_password` **明文列**（仅 developer 可见，属已接受风险，见 `security-review.md §十六 A2`） | 库文件属主 `appuser`；备份产物**未加密** | 高：库文件或备份泄漏 = 口令全量泄漏 |
| `ALERT_WEBHOOK_URL` | 服务器 `.env` | 同上 | 低-中：可向该 webhook 发送伪造告警；若 URL 内嵌共享令牌，等同该令牌泄漏 |
| `DATABASE_URL` | 服务器 `.env`（仅改用外部库时才设置） | 同上 | 中：可能内嵌外部数据库账号口令 |
| TLS 私钥 | 宿主 `/etc/letsencrypt`（以 `:ro` 只读挂载进边缘 `nginx-proxy`） | 宿主 root | 高：可解密或冒充站点 |
| 服务器 SSH 凭据 | 部署者本机的 `deploy.sh`（**不入库**，见 §三 排除清单） | 部署者本机 | 最高：服务器接管 |

**"不入库"的验证方式**（不要靠记忆）：

```bash
git check-ignore -v .env deploy.sh        # 应各自命中一条忽略规则
git ls-files | grep -E '(^|/)\.env$'      # 期望：无输出（模板 .env.example 除外，它是占位符）
```

### 秘密轮换与泄漏处置（2026-10-02 新增，对应 ASVS 13.3.4）

**轮换周期建议**：`SECRET_KEY` 每 6–12 个月、或**人员变动 / 疑似泄漏 / 服务器重建**时立即轮换；
三角色初始口令在**首次部署完成后立即**改为强口令（此后系统不再读取这两个变量）。

| 秘密 | 轮换步骤 | 影响与验证 |
|------|---------|-----------|
| `SECRET_KEY` | ①`openssl rand -hex 32`；②替换服务器 `.env` 中的值；③`docker compose up -d backend`（重建容器） | **所有已登录用户需重新登录**（旧令牌验签失败；这是预期代价，见 §六 末尾与 Q6）。验证：旧令牌请求返回 401、重新登录后 200 |
| 三角色初始口令 | 首次部署后通过系统内**自助改密**（右上角菜单 →「修改密码」）或管理端重置 | 无需重启；改密会使该账号的**其他会话立即失效**（`token_version` 自增） |
| 账号口令（疑似泄漏） | 立即改密；必要时在系统配置禁用该账号（禁用即 401） | 无需重启 |
| `ALERT_WEBHOOK_URL` | 替换 `.env` 中值 → `docker compose up -d backend` | 无登录影响 |
| TLS 私钥/证书 | 交由宿主 `certbot` 续期（证书路径与挂载见 §二）；续期后重载边缘 `nginx-proxy` | 验证：`openssl s_client` 查看证书有效期 |
| SSH 凭据 | 更换密钥对并清理 `authorized_keys`；确认 `deploy.sh` 未入库 | 验证：`git check-ignore -v deploy.sh` 有命中 |

**泄漏应急处置（按顺序）**：

1. **先轮换、后排查**：按上表轮换相关秘密（`SECRET_KEY` 轮换会让攻击者已窃取的令牌立即失效）；
2. **查审计**：`operation_logs` 表按 `module='auth'` 检索异常登录/IP（登录成功与失败均已埋点）；
3. **查暴露面**：确认泄漏路径（误提交到 git / 镜像 / 日志 / 备份），若曾推送过 git，轮换是唯一补救（历史无法回收）；
4. **记录**：在 `security-review.md` 追加一条处置记录（含时间、影响面、轮换范围），便于回溯。

### 启动门禁（2026-09-28 新增）

后端启动时校验 SECRET_KEY（`backend/app/core/config.py`）：**生产环境**（`APP_ENV=production`
或容器特征兜底）下弱密钥（模板占位值、<32 字符、含项目名/单词/年份等可猜片段）
将打印 `FATAL` 并拒绝启动；开发环境仅告警放行。推荐密钥为 `openssl rand -hex 32`
输出的 64 位十六进制串（恒判定为强）。

**部署前核对命令**（在服务器 `~/nsh-management` 目录执行）：

```bash
# 长度须 ≥32（推荐 64）
awk -F= '/^SECRET_KEY=/{print length($2)}' .env
# 不得为模板占位值（无输出即正常）
grep -E '^SECRET_KEY=(please-change-me|your-secret-key|dev-secret-key)' .env
```

**服务器侧同步项（2026-09-28）**：`docker-compose.yml` 在 deploy.sh 排除清单中，本地已为
backend 服务新增 `environment: APP_ENV: production`，**服务器侧需手动同步**（先备份）。同步前
容器特征兜底（`/.dockerenv`）在 Docker 部署下仍生效，但显式声明可避免迁移 k8s/裸机时校验被静默跳过。

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

### Q6：backend 日志出现 `FATAL: 生产环境 SECRET_KEY ...`，容器反复重启？

启动门禁拦截了弱密钥（见 §六），backend 退出 → frontend 因 `service_healthy` 不启动 →
整站不可用（deploy.sh 健康检查已改为失败退出并打印日志，不会再报假成功）。

**处置**：

```bash
cd ~/nsh-management
cp .env .env.bak-$(date +%F)          # 先备份
openssl rand -hex 32                   # 生成强密钥，替换 .env 中 SECRET_KEY
docker compose up -d backend           # 重启后端（迁移自动执行）
docker compose ps                      # 确认 healthy 后 frontend 会自动拉起
```

注意：更换 `SECRET_KEY` 会使所有已登录用户强制重登一次（预期内代价）。

**紧急回退**（无法立即生成强密钥、需先恢复站点时）：在服务器 `docker-compose.yml` 的
backend 服务临时设 `APP_ENV: development` 后 `docker compose up -d backend`，可跳过门禁
恢复启动（仅容器特征兜底被覆盖时有效）；**事后必须换强密钥并改回 production**，
回退期间旧密钥可被用于伪造 Token，属带风险运行。

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

## 九、版本归档与回滚（2026-10-02 新增，合规化计划 W3-3）

本项目**不使用镜像仓库**，制品以带版本号的 tar 归档。**版本权威是 git 标签**（`vX.Y.Z`；
面向使用者的变更见 `CHANGELOG.md`，打标签流程见 `GIT-GUIDE.md §5`）。

### 9.1 发布前归档（在服务器 compose 目录执行）

```bash
cp scripts/release-archive.sh.example scripts/release-archive.sh && chmod +x scripts/release-archive.sh
./scripts/release-archive.sh v1.2.0              # 默认 dry-run：先看要做什么
DRY_RUN=0 ./scripts/release-archive.sh v1.2.0    # 真正归档 backend / frontend 镜像
```

产物：`~/nsh-archives/nsh-backend-v1.2.0.tar`、`nsh-frontend-v1.2.0.tar` 与清单
`nsh-v1.2.0.manifest.txt`（记录版本、提交号、镜像引用、归档时间）。脚本会核对标签是否存在、
工作区是否干净并给出**警告**——归档的镜像必须能对应到一个已提交版本。

### 9.2 回滚步骤（停服 → 换回旧版本 → 启动 → 验证）

```bash
cd ~/nsh-management
docker compose stop                                     # 1) 停服
docker load -i ~/nsh-archives/nsh-backend-v1.1.0.tar     # 2) 载入上一版本镜像
docker load -i ~/nsh-archives/nsh-frontend-v1.1.0.tar
docker images | grep -i nsh                              # 3) 记下旧镜像的 IMAGE ID
# 4) 让 compose 使用旧镜像：为该镜像打上 compose 期望的本地 tag（回滚完成后还原 compose 文件）
docker tag <旧镜像ID> nsh-management_backend:rollback
docker tag <旧镜像ID> nsh-management_frontend:rollback
docker compose up -d                                     # 5) 启动
docker compose ps                                        # 6) backend 需 healthy、frontend 需 running
curl -sk -o /dev/null -w '%{http_code}\n' \
  -H 'Host: <YOUR_DOMAIN>' https://127.0.0.1/            # 7) 入口应为 200
```

### 9.3 ⚠️ 数据库迁移不可逆：回滚前必须先判断

- 容器**每次启动**都会执行 `alembic upgrade head`（Dockerfile CMD），迁移**只前进不回退**。
- 若已发布的版本包含**破坏性迁移**（删列 / 改类型 / 不可逆数据改写），仅回滚镜像会与已迁移的库不兼容；
  此时必须**先回滚数据库**：用 `scripts/backup-db.sh` 在**升级前**生成的备份，按 §五 的恢复流程覆盖数据库，
  再启动旧镜像。
- 因此发布纪律：**先归档镜像（9.1）+ 先做数据库备份（§五），再执行 `up -d --build`**。
- 迁移 head 与版本对应关系见 §二 与 `backend/alembic/versions/`；用户可见变更见 `CHANGELOG.md`。

### 9.4 归档保留

镜像 tar 体积较大（每服务数百 MB），建议 `~/nsh-archives` 只保留最近 3～5 个版本。
删除前确认：该版本已不在生产使用，且其对应的**数据库备份仍在保留期内**（§五，默认 30 天）。
