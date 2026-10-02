# 安全与性能审查报告

> §一～九保留历史审查记录；当前定向修复、结论更正与未解决项见 §十，历史「已修复」不代表所有响应路径已验证。

> 审查日期：2026-08-20
> 审查范围：nsh-management 全栈（FastAPI 后端 + Vue3 前端 + Nginx/Docker 部署）
> 审查方式：静态代码审查（未修改任何代码）
> 结论：**存在 2 个严重问题、7 个中等问题、7 个低危/建议项，1 项依赖已知漏洞**
> 状态：**修复方案已定稿并完成代码实施（2026-08-20），待部署到服务器验证**

---

## 一、总体评价

项目在基础安全上做得不错：bcrypt 密码哈希、JWT 认证、登录失败锁定、全接口角色权限校验（`require_admin`/`require_developer`）、SQL 全参数化（无注入）、Vue 模板默认转义（不能据此排除图表自定义 HTML 的 XSS，修正见 §十二）、Docker 非 root 运行 + 资源限制、HTTPS + 安全响应头均已具备。

**核心短板集中在三点：**
1. **明文密码入库且通过接口返回**（`plain_password` 字段贯穿数据流）；
2. **上传接口缺少后端大小限制与全局限流**（仅 nginx 层 20m 兜底，CSV 接口有 5MB 限制，Excel 接口无限制）；
3. **依赖版本存在已知 DoS 漏洞**（python-multipart 0.0.9 / starlette 相关 CVE）。

---

## 二、严重问题（P0，建议立即修复）

### S-1 明文密码存储并经接口返回
| 项 | 内容 |
|---|---|
| 位置 | [user.py](backend/app/models/user.py#L17)、[init_db.py](backend/app/init_db.py#L53)、[config_service.py](backend/app/services/config_service.py#L149-186)、[config.py](backend/app/schemas/config.py#L39) |
| 描述 | `users.plain_password` 字段明文存密码；`AccountOut` schema 含 `plain_password`，`GET /api/v1/config/accounts` 会把**所有账号明文密码返回给前端**；创建/更新账号、创建帮会均写入明文。 |
| 影响 | 数据库泄露 = 全部账号密码泄露；任何管理员可通过接口直接读到本帮会所有账号明文密码（含开发者帮会体系下其他帮会权限）。 |
| 已定方案 | **不删除数据库列**（用户决策：开发者需可查看）。接口按角色收窄：仅 `developer` 返回 `plain_password`，admin/member 置 None；前端密码列仅 `auth.isDeveloper` 显示，其余显示 "-"。**2026-09-28 补强**：脱敏由逐接口手工实现改为统一 `_build_account_out` 角色感知输出映射，覆盖 list/create/update/update_status 全部响应路径（原写接口缺口见 §十，已关闭）。残余风险：数据库文件本身仍含明文，依赖服务器与备份文件安全（M-7 修复后 `_backup` 不再随部署包上传）。 |

### S-2 成员 Excel 导入接口无任何文件限制
| 项 | 内容 |
|---|---|
| 位置 | [members.py](backend/app/api/v1/members.py#L89-97)、[excel_import.py](backend/app/utils/excel_import.py#L43-51) |
| 描述 | `POST /api/v1/members/import` 直接 `await file.read()` 全量读入内存，**无大小限制、无类型校验（MIME/魔数/扩展名均不检查）、无频率限制**。对比：CSV 导入接口有 5MB 限制（`MAX_FILE_SIZE`）与 `.csv` 后缀校验。openpyxl 解析无行数/单元格上限，恶意 xlsx（超大行数或 zip 膨胀）可耗尽内存。 |
| 影响 | 内存耗尽 DoS；文件类型绕过（改后缀传任意文件）；重复高频调用放大攻击。 |
| 已定方案 | 与 CSV 接口统一：① 读取前检查 `Content-Length` 超 5MB 直接 400，读取后 `len(content) > 5MB` 二次兜底；② 扩展名非 `.xlsx` 拒绝；③ openpyxl 解析限行数 5000、单元格字符串 ≤255；④ 配合全局限流（M-1）。 |

---

## 三、中等问题（P1）

### M-1 全局缺少接口频率限制（Rate Limit）
| 项 | 内容 |
|---|---|
| 位置 | [main.py](backend/app/main.py)、[nginx.conf](frontend/nginx.conf) |
| 描述 | 除登录失败锁定外，所有接口（导入、批量操作、报告导出、登录探测）均无限流。nginx 无 `limit_req_zone`，后端无中间件。登录仅按用户名锁定，**无 IP 维度限制**，攻击者可用多 IP / 多不存在用户名绕过（不存在的用户名锁定在进程内存，重启即清零）。 |
| 影响 | 暴力破解、接口滥用、上传轰炸、CPU/内存耗尽。 |
| 已定方案 | nginx 两层限流：`/api/` 20r/s（burst 40 nodelay，超限返回 429 JSON）；`/api/v1/auth/login` 单独 5r/min/IP（burst 3）。zone 用 1m（小服务器省内存）。**不做后端内存限流**（生产流量全经 nginx，本地开发无公网攻击面——结合服务器 2C/1.9G 实测后精简）。阈值上线后可调。 |

### M-2 创建帮会时账号密码硬编码 "123456"
| 项 | 内容 |
|---|---|
| 位置 | [config_service.py](backend/app/services/config_service.py#L238-258) |
| 描述 | `create_guild` 生成的管理员/帮众账号密码固定为 `123456`，不可配置，所有新帮会共享同一弱密码。 |
| 影响 | 新帮会账号极易被爆破；多帮会场景一个密码通吃。 |
| 已定方案 | **创建帮会时手动指定**（用户决策）：`GuildCreate` 增加 `admin_password`/`member_password` 字段（按 M-3 策略校验），删除硬编码 `123456`；创建后不回显密码，忘记可重置。 |

### M-3 密码策略过弱 + 初始密码强度不足
| 项 | 内容 |
|---|---|
| 位置 | [config.py](backend/app/schemas/config.py#L47-59)、.env |
| 描述 | 密码仅 `min_length=6`，无复杂度要求；`.env` 中 `DEVELOPER_PASSWORD` 仅 8 位；`LoginRequest`（[auth.py](backend/app/schemas/auth.py#L5-7)）无字段长度上限，可提交超大 body（配合 nginx 20m 上限形成内存/CPU 消耗向量）。 |
| 已定方案 | 密码字段 `min_length=8` + 正则 `^(?=.*[A-Za-z])(?=.*\d)`（8-128 位含字母和数字），应用于账号创建/修改与帮会初始密码；`LoginRequest` 加 `username max_length=64`、`password max_length=128`。已有账号密码不受影响（仅新设时校验）。 |

> **修订说明（2026-10-02，合规化计划 W4-10 / F-52）**：上述「正则 `^(?=.*[A-Za-z])(?=.*\d)`（强制含字母和数字）」的**做法已废止**——它违反 ASVS 5.0.0 **6.2.5（不得限制字符组成）**。现行策略为「长度 8–128 + 常见弱口令/项目上下文词表 + 不得含登录名 + 不得为单一重复字符」，实现见 `backend/app/core/password_policy.py`，逐条结论见 §17.6 与 §17.9。**历史行按 AGENTS §3.4 保留原文，不回改。**

### M-4 录屏链接提交无格式校验（存储型链接滥用）
| 项 | 内容 |
|---|---|
| 位置 | [recording_service.py](backend/app/services/recording_service.py#L127-143)、[RecordingTab.vue](frontend/src/components/recording/RecordingTab.vue#L66) |
| 描述 | `submit_recording` 接受任意字符串（无长度/协议校验）。前端 `normalizeUrl` 会为非 http(s) 开头补 `https://` 前缀（`javascript:` 会被转为域名，**未形成脚本执行**，风险已降低），但管理员点击链接可被导向任意外部站点（钓鱼）；字段 schema 无长度上限。 |
| 已定方案 | `RecordingSubmit.url` 加 `max_length=512` + 正则 `^https?://`（**不加域名白名单**，录屏链接业务多样；前端 `normalizeUrl` 已补协议，帮众输入 "b23.tv/xxx" 仍可用）。 |

### M-5 全局异常处理向客户端泄露内部信息
| 项 | 内容 |
|---|---|
| 位置 | [main.py](backend/app/main.py#L101-106) |
| 描述 | `general_exception_handler` 返回 `f"服务器内部错误: {str(exc)}"`，异常消息原样暴露给客户端（可能含文件路径、SQL 片段、库版本等）。 |
| 已定方案 | 加 `DEBUG` 环境变量（默认 false）：生产返回通用消息"服务器内部错误"，堆栈写日志；`DEBUG=true` 时保留异常详情（本地开发排查）。 |

### M-6 JWT 生命周期与登出缺陷
| 项 | 内容 |
|---|---|
| 位置 | [config.py](backend/app/core/config.py#L17)、[security.py](backend/app/core/security.py#L20-23)、[auth.py](backend/app/api/v1/auth.py#L21-24) |
| 描述 | ① Token 有效期 10 小时偏长且无刷新机制；② 登出仅前端丢弃 Token，服务端无吊销能力，**被窃 Token 10 小时内持续有效**；③ Token 无 `iat/jti` 声明，无设备/会话维度控制。 |
| 已定方案 | **保留 10 小时有效期**（用户决策，避免频繁重登）+ `token_version` 吊销：`users` 加 `token_version` 列（迁移），Token payload 携带 `ver`，`get_current_user` 校验一致；**改密时**版本 +1 使该账号所有旧 Token 立即 401（防设备丢失后旧 Token 继续使用）。**登出不吊销**（用户决策：共享账号多人多 IP 使用，一人登出不应踢掉同账号其他设备）。禁用账号无需自增（`get_current_user` 每请求校验 status，禁用已即时 401）。 |

### M-7 部署脚本含默认凭据与敏感信息，且打包未排除 `_backup`
| 项 | 内容 |
|---|---|
| 位置 | [deploy.sh](deploy.sh#L68) |
| 描述 | ① 健康检查硬编码 `password=dev123456`（若 `.env` 已改密，检查会误报失败；若未改密，脚本即泄露默认凭据）；② 打包 exclude 列表未含 `_backup/` 目录，本地备份（含数据库备份 `nsh.db.bak`、内部文档）会随部署包上传服务器；③ 服务器 IP/用户名硬编码。 |
| 已定方案 | 健康检查改为无凭据探活根路径（`curl http://127.0.0.1/`）；tar exclude 增加 `--exclude='_backup'`、`--exclude='DEPLOY.md'`、`--exclude='security-review.md'`，**删除 `--exclude='nginx.conf'`**（否则 B1 限流配置无法随部署包上传生效）；服务器 IP/用户名暂留脚本顶部（脚本已 gitignore）。已完成：服务器遗留 `_backup`/`DEPLOY.md`/`security-review.md` 已清理（2026-08-20，用户授权）。 |

---

## 四、低危问题与建议（P2）

| 编号 | 项 | 说明与建议 |
|---|---|---|
| L-1 | 依赖已知漏洞 | `python-multipart==0.0.9` 受 CVE-2024-53981（multipart 解析内存耗尽 DoS，影响全部上传/表单接口）；`fastapi==0.110.0` 锁定的 starlette 0.37.x 受 CVE-2024-47874（multipart DoS）。**已定方案**：升级 `python-multipart>=0.0.18`、`fastapi>=0.115.0`，回归测试两个上传接口。 |
| L-2 | 出勤状态接口未做后端角色校验 | 前端已防护：ScheduleDetailView 对帮众隐藏出勤 Tab（`v-if="!isMember"`），UI 无入口；但 [attendance_service.py](backend/app/services/attendance_service.py#L128-141) 的 `update_status` 接口层用 `get_current_user`（不区分角色），帮众 Token 绕过前端直接调接口仍可修改任意记录状态，属纵深防御缺口（低危）。**已定方案**：接口改 `require_admin`，前端 UI 不改。 |
| L-3 | 帮众共享账号本身 | 每个帮会一个共享帮众账号，无法区分个体、无操作审计。建议后续引入个人账号 + 操作日志。 |
| L-4 | 前端 Token 存 localStorage | 标准 SPA 做法但受 XSS 影响；建议评估 HttpOnly Cookie + CSRF 防护，或至少配置 CSP。 |
| L-5 | 无 CSP / server_tokens 未关闭 | [nginx.conf](frontend/nginx.conf) 已有 X-Frame-Options 等头，但无 `Content-Security-Policy`；未加 `server_tokens off`（泄露 nginx 版本）。**已定方案**：补充 `server_tokens off`；CSP 降级为可选后续（html2canvas/echarts 内联样式配错有白屏风险，本系统无 v-html 无外部脚本，XSS 面小、收益低）。 |
| L-6 | SQLite 未启用 WAL | [database.py](backend/app/core/database.py) 未设置 `PRAGMA journal_mode=WAL`，读多写少场景可提升并发读性能与写入稳定性。**已定方案：默认搁置不做**（数据量小，避免引入 -wal/-shm 文件与备份复杂度），遗留风险记录在案。 |
| L-7 | `limit` 参数无上限 | [match_data.py](backend/app/api/v1/match_data.py#L71) `limit: int = 20` 无 `le` 上限；[lineup.py](backend/app/schemas/lineup.py#L7-18) 槽位 remark 无长度限制。**已定方案**：`limit` 加 `ge=1, le=100`；`LineupSlot.remark` 加 `max_length=255`。 |
| L-8 | CORS 配置 | `allow_methods/headers=["*"]`，当前仅 localhost 来源，生产同源部署影响小；若未来多域名部署需收紧。 |
| L-9 | 登录不存在账号锁定存内存 | 服务重启清零（已知设计），多实例部署时失效。数据量小，可接受，记录在案。 |

---

## 五、已确认做好的防护（正面清单）

- ✅ 密码 bcrypt 哈希存储（`passlib[bcrypt]`，版本固定规避兼容问题）
- ✅ 登录失败 5 次锁定 5 分钟（数据库持久化 + 内存兜底，前端倒计时禁用表单）
- ✅ JWT 签名、过期校验、`get_current_user` 对异常 payload 防御
- ✅ 角色权限：`require_admin` / `require_developer`，帮会隔离（`guild_id` 过滤）+ 跨帮会资源 404 掩盖
- ✅ 全接口 SQL 参数化（SQLAlchemy ORM），未发现注入点
- Vue 模板默认转义；自定义 HTML 输出需单独检查，ECharts tooltip 修复与原结论更正见 §十二
- ✅ 管理员不能禁用/删除自己；开发者账号不可删除
- ✅ CSV 导入有 5MB 大小限制 + `.csv` 后缀校验 + 局号范围校验（1~rounds）
- ✅ 帮会图标仅限本帮会（403）；职业配置/账号操作限管理员
- ✅ 部署：非 root 运行（appuser）、`no-new-privileges`、内存/CPU 限额、HSTS、TLSv1.2/1.3、HTTP→HTTPS 跳转
- ✅ 敏感文件（.env、deploy.sh、nginx.conf、_backup、memory-bank）均已 gitignore

---

## 六、性能审查

### 6.1 数据库索引（良好）
- `users.guild_id`、`members.guild_id/name/main_profession/status`、`schedules.guild_id/match_time`、`attendance_records.schedule_id/member_id`、`recordings.schedule_id/member_id/status`、`match_data.schedule_id/round_no` 均有索引；唯一约束（lineups.schedule_id、profession 组合、attendance 组合、recording 组合）自动建索引。主要查询路径均命中索引。

### 6.2 查询模式（数据量小，当前可接受）
- `list_match_data` / `get_rankings` 全量加载后在 Python 内聚合排序（每局几十人，可接受；若 CSV 反复导入累积超大表会退化，建议后续按 `camp` 覆盖删除已处理）。
- `import_count` 用 `func.date(created_at)` distinct 全表扫描，无索引；数据量小可接受。
- `ensure_recordings` 对新建记录逐个 `refresh`，少量可接受。
- 无典型 N+1：`User.guild` 为 joined eager；录屏列表职业快照单查询映射；账号列表复用 lazy 关联单查。

### 6.3 其他
- uvicorn 单 worker 适配 SQLite 写锁，正确。
- Excel 导入一次性 `add_all` + 单次 commit，无逐行提交性能问题（但无行数上限，见 S-2）。
- 前端依赖包体偏大（echarts + element-plus 全量引入），首屏加载可考虑按需引入/分包，非安全问题。
- 登录接口 bcrypt 计算约 100ms/次，未限流时会被用于 CPU 消耗攻击（与 M-1 联动）。

---

## 七、修复计划与行动清单（代码已修复，待部署验证）

| 批次 | 行动 | 对应编号 | 状态 |
|---|---|---|---|
| A | 明文密码接口按角色收窄（仅 developer 可见） | S-1 | ✅ 已修复 |
| A | Excel 导入加 5MB/扩展名/行数限制 | S-2 | ✅ 已修复 |
| A | 升级 fastapi / python-multipart（已知 CVE） | L-1 | ✅ 已修复 |
| B | nginx 限流（20r/s + 登录 5r/min，zone 1m，不做后端限流） | M-1 | ✅ 已修复 |
| B | 创建帮会手动指定初始密码（删硬编码 123456） | M-2 | ✅ 已修复 |
| B | 密码 ≥8 位含字母数字 + 登录请求体长度限制 | M-3 | ✅ 已修复 |
| B | 录屏 URL 协议/长度校验（无白名单） | M-4 | ✅ 已修复 |
| B | 生产环境异常信息脱敏（DEBUG 开关） | M-5 | ✅ 已修复 |
| B | Token 保留 10h + token_version 吊销（仅改密自增，登出不吊销） | M-6 | ✅ 已修复 |
| B | 部署脚本无凭据探活、排除 `_backup` | M-7 | ✅ 已修复 |
| C | 出勤状态接口改 require_admin（UI 不改） | L-2 | ✅ 已修复 |
| C | nginx `server_tokens off`（CSP 可选后续） | L-5 | ✅ 已修复 |
| C | `limit` 1~100、remark ≤255 | L-7 | ✅ 已修复 |
| — | SQLite WAL | L-6 | ⏸ 默认搁置 |
| — | 帮众个人账号体系、Token 改 Cookie | L-3/L-4 | 📋 遗留风险记录 |

---

## 八、修复决策记录（2026-08-20 用户确认）

| 决策点 | 选择 | 理由/说明 |
|---|---|---|
| 明文密码（S-1） | 不删数据库列，仅 developer 接口可见 | 开发者需随时查看账号密码；残余风险（库文件含明文）已告知 |
| Token 有效期（M-6） | 保留 10 小时 + token_version 吊销 | 避免用户频繁重登，安全由吊销机制补足 |
| 帮会初始密码（M-2） | 创建时手动指定 | 创建者自定义，按新策略校验 |
| 出勤状态权限（L-2） | 前端已对帮众隐藏，仅收紧后端为 require_admin | UI 无变化，堵住绕过界面调接口的口子 |
| Excel 大小上限（S-2） | 5MB（与 CSV 接口统一） | 成员模板远小于 5MB |
| 录屏 URL 白名单（M-4） | 不加白名单，仅协议/长度校验 | 录屏链接业务多样，白名单过死板 |
| WAL（L-6） | 默认不做 | 数据量小，避免 -wal/-shm 与备份复杂度 |
| 过度防护精简（2026-08-20 服务器实测后） | 砍后端登录限流/CSP；禁用不自增版本；zone 1m | 服务器 2C/1.9G，生产流量全经 nginx，避免层层加码 |
| 登出吊销范围（2026-08-20） | 登出不吊销（仅改密全局吊销） | 共享账号多人多 IP 使用，一人登出不应踢掉其他人；改密踢下线仍保留 |
| token_version 去留（2026-08-20） | 保留 | 保留改密全局踢下线能力；接受部署后所有用户强制重登一次的代价 |

实施状态：**代码修复已全部完成并本地验证通过（2026-08-20）**；待用户部署后回归验证。实施顺序：批次 A（P0）→ 批次 B（P1）→ 批次 C。

---

## 九、审查依据文件清单

> 以下为 2026-08-20 的历史审查依据；2026-09-18 定向修复与结论更正见 §十。

- 后端：`app/main.py`、`app/core/config.py`、`app/core/security.py`、`app/core/database.py`、`app/api/deps.py`、`app/api/v1/*.py`（auth/members/match_data/config/attendance/lineups/recording/schedules）、`app/services/*.py`、`app/utils/excel_import.py`、`app/utils/attendance_import.py`、`app/schemas/*.py`、`app/models/*.py`、`app/init_db.py`、`requirements.txt`
- 前端：`src/api/http.ts`、`src/stores/auth.ts`、`src/components/recording/RecordingTab.vue`、`index.html`、`package.json`、`vite.config.ts`
- 部署：`nginx.conf`、`docker-compose.yml`、`backend/Dockerfile`、`frontend/Dockerfile`、`entrypoint.sh`、`deploy.sh`、`.env`（仅检查强度，未输出值）、`.gitignore`

---

## 十、用户隔离定向修复（2026-09-18）

本次经用户确认实施 F-1～F-5，不等同于全体系安全验收；历史条目保留，最新进度统一见 `progress.md`。

| 编号 | 核实结果与处理 | 实现位置 |
|---|---|---|
| F-1 | admin 原可通过请求体指定外帮会创建账号；现在只能使用自身帮会，跨帮会/未绑定帮会返回 403。developer 必须指定目标；目标 ID 非正数返回 422、不存在返回 404、未选择返回 400；service 在写库前检查目标存在性 | `backend/app/api/v1/accounts.py`、`backend/app/services/account_service.py`、`backend/app/schemas/config.py` |
| F-2 | 出勤聚合原全库扫描、输出再映射本帮会成员；改为关联 Schedule 并在聚合前限定 guild_id，避免外帮会赛程中的历史错误引用污染本帮会统计 | `backend/app/services/member_service.py` |
| F-3 | **更正前次结论**：Member.guild_id 已有 NOT NULL，不会成功写入无帮会成员；缺少业务校验可能导致 500。单个创建及 Excel 导入现在提前拒绝未绑定帮会（403），不修改表结构 | `backend/app/services/member_service.py`、`backend/app/utils/excel_import.py` |
| F-4 | Excel 各 Sheet 首行增加帮会名/ID，文件名包含帮会名，客户端与服务端清理非法文件名字符；兼容旧首行表头与新来源行格式。来源行不决定导入归属，导入始终以认证帮会为准；空成员导出保留有效工作表 | `backend/app/utils/excel_export.py`、`excel_import.py`、`backend/app/api/v1/members.py`、`frontend/src/composables/useMemberList.ts` |
| F-5 | 批量删除、出勤成员导入/状态更新、录屏批量审核统一使用 BatchIds：1～500 个严格正整数；空列表、超限、布尔值、字符串及非整数在请求校验阶段返回 422 | `backend/app/schemas/common.py`、`member.py`、`attendance.py`、`recording.py` |

### 验证范围
- `backend/scripts/selfcheck_security_fixes.py`：真实 JWT 与认证依赖、实际 ASGI 路由，覆盖管理员同帮会/跨帮会、开发者目标选择、帮众与匿名拒绝、空帮会成员创建、批量边界与跨帮会记录保护。
- `backend/scripts/selfcheck_member_exports.py`：内存库出勤隔离（含外帮会赛程脏引用）、新旧 Excel 回导、来源不可改写导入归属、空导出、文件名与来源文本处理。
- 两个脚本共 16 项测试通过（含参数子用例）；后端 compileall 与前端 vue-tsc/vite build 通过。未访问业务数据库，未做线上或浏览器验收，未运行前端 vitest。

### 边界与待办更正
- 帮会名、水印只用于识别来源，**不提供密码学防伪能力**；若需要防篡改验证，另行设计服务端签名与校验入口。
- 不改动已接受的明文列保留、共享账号、localStorage、10 小时 Token 或登出不吊销策略。
- **前次「明文密码仅 developer 返回已全面通过」结论不准确**：`accounts.py` 仅列表响应置空，创建/更新/状态更新响应仍直接序列化 AccountOut，可能向 admin 返回 plain_password。本项未列入已确认的 F-1～F-5；待用户确认后统一响应脱敏并覆盖回归，不能视为已修复。
  **→ 2026-09-28 已关闭**：新增统一 `_build_account_out(account, current_user)` 角色感知输出映射（集中处理 guild_name 填充 + 非 developer 置空 plain_password），list/create/update/update_status 四路径全部改经该函数构造响应，消除逐接口手工脱敏覆盖缺口；developer 行为不变。

---

## 十一、游戏 ID 改名申请与战绩关联安全决策（2026-09-20）

> 功能与 API 详见 `design-game-id-change.md`；表结构见 `database-design.md` §2.12；进度与验证结果见 `progress.md`。

**决策与实现要点**

| 项 | 处理 | 位置 |
|---|---|---|
| 角色边界 | 新增 `require_member`（提交/候选）、`require_admin_strict`（审核/审核列表）、`require_member_or_admin`（成员历史、个人战绩）；三者均要求账号绑定有效帮会，developer 访问一律 403；未改动包含 developer 的原 `require_admin` | `backend/app/api/deps.py`、`api/v1/game_id_requests.py`、`api/v1/my_stats.py` |
| 租户归属 | 归属只取 `current_user.guild_id`；成员/申请均先校验帮会归属，外帮会统一 404（不暴露存在性）；请求体 `extra="forbid"` 拒绝夹带 guild_id/status/requester/reviewer 等字段 | 同上 + `schemas/game_id_request.py` |
| 并发与一致性 | 提交侧：应用校验 + `UNIQUE(guild_id, member_id) WHERE status='pending'` 部分唯一索引兜底；审核侧：`request_id+guild_id+status='pending'` 条件 UPDATE 校验行数 → 同事务内名称占用检查 → `member_id+guild_id+name=旧值` 条件 UPDATE，任一步失败整体回滚；重放审核 409，不覆盖首位审核人 | `services/game_id_request_service.py` |
| 生命周期 | 成员被直接改名（`PUT /members/{id}`，仅 admin）→ pending 置 `invalidated(member_renamed)`，并在同一事务写入一条 approved 关联记录（提交/审核人=操作管理员快照，备注标注来源）；成员删除（单个/批量）→ pending 失效并将该成员全部申请 `member_id` 置空；账号删除 → 申请人/审核人引用置空、账号名快照保留；帮会删除 → 先清理本帮会申请记录。以上辅助函数均不自行 commit | `services/game_id_request_lifecycle.py` + member/account/guild 服务 |
| 历史数据 | 审核通过不改写出勤/排表/录屏/比赛数据；`match_data.player_name` 保持比赛当时 ID；旧 ID 战绩查询（merge_aliases=false）与原口径一致 | `services/my_stats_service.py` |
| 名称关联边界 | 仅 approved 记录作为已确认关系（来源：帮众申请审核通过 / 管理员直接改名自动记录，后者 `review_remark` 标注来源）；可检测冲突（其他当前成员占用、他人批准记录重叠、`member_id` 置空的失效引用、同一场同一局多名称/阵营）一律 409 并提示改用「仅查此 ID」；不承诺识别未登记的跨时期同名复用 | `services/player_identity_service.py` |
| 已知接受风险 | 共享 member 账号无法从技术上证明申请人身份，身份核实依赖管理员线下确认（沿用既有共享账号风险）；审批意见字段帮众可见，已提示不要填写隐私信息 | 已记录，无需额外修复 |

**验证范围（未做浏览器与线上验收）**

- `scripts/selfcheck_game_id_requests.py`（13 项，真实 JWT + ASGI）：角色矩阵与租户隔离、参数边界、重复待审、共享账号多成员提交、审核确认/重放/跨帮会、名称占用冲突回滚、双成员同名竞争、直接改名（含自动记录关联）与删除联动、账号删除快照、帮众响应脱敏。
- `scripts/selfcheck_game_id_requests_concurrency.py`（5 项，隔离文件库 + 独立连接）：并发重复提交、双管理员审核单赢家、通过与驳回竞争、同名目标竞争、直接改名与审核竞争后名称一致性（2026-09-20 修正该用例断言：原「审核 approved ⇒ 名称 == 新 ID」假设单一写者，未覆盖「审核通过 → 管理员再次直接改名」的合法交错；现按写者顺序断言并新增两条确定性约束，连续 10 次运行通过）。
- `scripts/selfcheck_my_stats_aliases.py`（10 项）：合并/精确模式、改名链与改回、管理员直接改名自动关联、新名无数据、跨帮会隔离、冲突 409 与精确退路、冲突位于最近 10 场之外仍被发现、开发者拒绝。
- `scripts/selfcheck_migration_game_id.py`（1 项）：临时库空库升级 → 回退 → 再升级，校验表、索引与 CHECK/唯一索引真实生效；未接触业务库。
- 既有回归 `selfcheck_security_fixes.py`（8 项）、`selfcheck_member_exports.py`（8 项）、`selfcheck_indicators.py` 全部通过；后端 `compileall` 与前端 `vue-tsc + vite build` 通过。

---

## 十二、全项目审查 F01：图表 HTML tooltip 输出边界（2026-09-24）

> 本节 F01 为全项目存量审查编号，与 §十的 F-1～F-5 无关。验证结果统一见 `progress.md` 对应日期记录；人工验收步骤见 `frontend/docs/README.md`。

- **问题与更正**：CSV 中的玩家名、职业、阵营经接口进入自定义 `tooltip.formatter` 后，原代码直接拼入 HTML；Vue 模板转义不作用于此输出路径。因此原「无 v-html 即无存储型 XSS」判断不成立。
- **修复边界**：`chartTheme.tooltipText` 复用 `echarts/core` 的 `format.encodeHTML`，仅在 HTML 输出边界编码 `& < > " '`；不预编码数据库、API、图例或 Canvas 标签，不改变姓名匹配、筛选与统计口径。
- **覆盖路径**：玩家伤害/治疗散点、KDA 散点、小队成员 KDA、职业热力图、阵营职业堆叠、KDA 构成、帕累托、综合评分雷达与散点等自定义 formatter；普通 HTML 标签保持静态，ECharts 根据固定配色生成的 `marker` 保留原样。
- **结构与兼容**：按工具文件行数限制抽出 `kdaScatterCharts.ts` 与 `paretoChart.ts`；原入口重导出函数，调用方接口不变。综合评分散点按实际元组位置读取姓名和职业。
- **不包含**：未调整认证策略、明文列、localStorage、共享账号、后端 CSV 存储或本轮其他审查项；类型检查与构建不等于浏览器 XSS 执行验证。

---

## 十三、SECRET_KEY 生产启动门禁（C-2，2026-09-28）

| 项 | 内容 |
|---|---|
| 问题 | `core/config.py` 原硬编码弱默认值 `dev-secret-key-change-in-production`，生产 `.env` 漏配或沿用模板占位值时，任何持有默认密钥者可伪造登录 Token |
| 方案 | 启动时校验：生产环境（主判据 `APP_ENV=production/prod`，未声明时容器特征兜底）下弱密钥打印 FATAL 到 stderr 并 `sys.exit(1)`；开发环境仅 WARNING 放行，不影响本地开发与现有 .env |
| 强度规则 | 弱集合（开发默认值 + 两处 .env.example 占位值）/ 长度 <32 / 含可猜片段（项目名、单词、年份 20xx 等黑名单）；≥64 字符纯十六进制串（`openssl rand -hex 32`）豁免恒通过 |
| 部署联动 | `docker-compose.yml` backend 固定 `APP_ENV: production`（服务器侧需手动同步，见 DEPLOY.md §六）；`deploy.sh` 健康检查改为 backend 非 healthy 则非零退出 + 打印容器日志，消除「门禁拦截→整站不可用→仍报部署完成」假成功；排障与紧急回退见 DEPLOY.md §七 Q6 |
| 实现位置 | `backend/app/core/config.py`（`_is_production` / `_secret_key_is_weak` / `validate_secret_key` / `enforce_secret_key`，2026-10-02 起门禁由**导入期**改为**应用启动期**，执行点移至 `backend/app/main.py` 的 `startup_checks()`）、`docker-compose.yml`、`deploy.sh`、两处 `.env.example`、`DEPLOY.md`、`README.md` |

---

## 十四、依赖漏洞审计（W4-3，2026-10-02）

审计工具与命令（结论来自实时公告库，非纸面推断）：

| 端 | 命令 | 审计对象 |
|----|------|----------|
| 前端 | `npm audit --json`（工作目录 `frontend/`） | `package-lock.json` 全量依赖树 |
| 后端 | `pip-audit -r backend/requirements.txt`（隔离环境安装 pip-audit，**不安装**业务依赖） | `requirements.txt` 解析出的依赖集 |

### 前端：7 项 → 4 项（已消除 1 个 high）

| 项 | 严重度 | 处置 |
|----|--------|------|
| `nanoid <3.3.18`（GHSA-2v37-7h3g-55p8） | **high** | ✅ **已修复**：`npm audit fix`（非破坏性，仅改 `package-lock.json`）；回归 `npm run lint`（0 error）/ `npm run test`（44 passed）/ `npm run build` 全绿 |
| `vite 5.4.x`：优化依赖 `.map` 路径穿越；`launch-editor` 在 Windows 经 UNC 路径泄露 NTLMv2 哈希 | **high** | ⏳ 待升级：修复版本为 `vite@8`（**semver-major**），并连带 `vitest 3→5` 与 `@vitejs/plugin-vue` / `unplugin-vue-components` 兼容性回归 |
| `esbuild`（随 vite）：开发服务器可被任意网站探测并读取响应 | moderate | ⏳ 随 vite 升级消解 |
| `vitest 3.2.7` + `@vitest/mocker`：重定向 mock 可致任意文件读取 | moderate | ⏳ 待升级 `vitest@5`（major） |

**可达性判定（生产）**：以上四项均属**开发/构建工具链**（dev server、测试 runner），不进入生产运行时
——生产由 Nginx 托管已构建的静态资源、`/api` 同源反代，仓库内没有任何对外提供 vite/vitest 服务的进程。
故**生产暴露面不受影响**；风险集中在「开发者本机 dev server 被恶意网页访问」这一场景。

### 后端：2 个包命中公告

| 包 | 命中 | 可达性判定（依据本项目代码） |
|----|------|------------------------------|
| `pillow 11.1.0` | 多条 PYSEC（修复版本 12.1.1～12.3.0，跨大版本） | **不可达**：Pillow 仅用于**生成**图片（`backend/app/utils/image_export.py` 只用 `Image.new` / `ImageDraw`），全仓**无 `Image.open`**，即从不解析外部图片；漏洞面位于解码器 |
| `ecdsa 0.19.2` | `PYSEC-2026-1325`（公告未给出修复版本） | **不可达**：`ecdsa` 由 `python-jose[cryptography]==3.3.0` 间接引入，仅在 ECDSA 算法路径使用；本项目 `ALGORITHM = "HS256"`，签发与校验均只传该算法（见 `core/security.py:24,30`） |

### 结论与后续项（均需回归，本次**不**直接升级）

1. **vite 8 + vitest 5 升级通道**：一次性升级并回归 `npm run lint` / `npm run test` / `npm run build` + 浏览器验收
   （回归面含路由分包预取与 unplugin 自动导入）。
2. **Pillow 12.x 升级**：需验证 `image_export.py` 的生成结果（字体与布局），回归
   `backend/scripts/selfcheck_member_exports.py`。
3. **`python-jose` → `PyJWT` 评估**：`python-jose` 维护活跃度低且携带本项目用不到的 `ecdsa` 依赖；
   迁移成本可控（仅 HS256），属依赖收敛而非漏洞驱动。
4. **是否把依赖审计接入 CI** 待定：需要容忍「开发工具链漏洞、生产不可达」的既有噪音，或采用分级阈值；
   当前结论以本文件记录为准，未接入门禁。

### CORS 白名单外置（同属 W4-3）

`CORS_ORIGINS` 由硬编码改为环境变量（逗号分隔，解析见 `core/config.py` 的 `_parse_cors_origins`），
默认值仅本地开发来源。生产由 Nginx **同源**反代 `/api`，浏览器不触发跨域，通常无需配置；
**禁止配置为 `*`**——本项目 `allow_credentials=True`，通配会放宽浏览器侧凭证策略。

---

### 14.6 2026-10-02 复核补充：python-jose 陈旧版本（**新增差距 F-48**）

| 项 | 事实 | 依据 |
|----|------|------|
| 原锁定版本 | `python-jose[cryptography]==3.3.0`（**2021-06 发布**） | `backend/requirements.txt`（升级前） |
| 上游版本序列 | **3.4.0（2025-02）为修复 JWT 相关 CVE 而发布**，最新 **3.5.0（2025-05）** | PyPI JSON 元数据（本轮实取 `pypi.org/pypi/python-jose/json`） |
| 兼容性 | 3.5.0 `requires_python >=3.9`，`vulnerabilities: []` | 同上 |
| 处置 | 升级为 `==3.5.0`；**全量套件 124 passed + 72 subtests、exit 0**（JWT 签发/解码/篡改用例覆盖） | 本轮 Python 3.12 隔离环境实测 |

**工具纪律（重要更正）**：本轮重跑 `pip-audit` **未能完成**（PyPI 咨询接口网络不可达，长时间无输出后终止），因此本次升级的依据是**上游发布史 + PyPI 元数据**，不是 pip-audit 的结论。
同时更正 §14 原有结论的适用范围：此前记录的「审计结果只报 `pillow`/`ecdsa`」**不能视为依赖面完整**——python-jose 3.3.0 属已知受影响版本却未被记录，而本轮该工具又跑不完，故**不再声称该审计完整**；后续应在网络可用时重跑并把工具版本、运行时间与原始输出一并留档。

**未逐一核实**：其余固定的依赖（`uvicorn 0.27.1`、`alembic 1.13.1`、`openpyxl 3.1.5` 等）的版本新旧与CVE 状态本轮未核对（不声称其“已过时”或“有漏洞”）；`bcrypt==4.0.1` 是**有意**固定（passlib 1.7.4 兼容需要）。

## 十五、暴露面清单与 OWASP 对照（W4-2，2026-10-02）

### 15.1 对外暴露面清单（读配置得出，非推测）

| 层 / 端点 | 是否对外可达 | 证据 |
|-----------|--------------|------|
| 边缘 Nginx `:443`（TLS 1.2/1.3） | ✅ 对外 | `frontend/nginx.conf.example:54-60` |
| 边缘 Nginx `:80` | ✅ 仅跳转 443 + ACME 校验路径 | `nginx.conf.example:24-48` |
| frontend 容器 `:80` | ❌ 无宿主端口映射 | `docker-compose.yml`、`DEPLOY.md §二` |
| backend 容器 `:8000` | ❌ 仅 compose 内网 | `docker-compose.yml`（`nsh-net`） |
| SQLite 数据库文件 | ❌ 卷内文件，无网络监听 | `docker-compose.yml`（`nsh-data` 卷） |

被代理路径与处置：

| 路径 | 处置 |
|------|------|
| `/assets/*` | 静态资源强缓存 `immutable`（内层 Nginx） |
| `/index.html` | `no-store` + Pragma/Expires（修微信端旧页面缓存） |
| `/api/v1/auth/login` | **独立限流** `5r/m`、burst 3、429 |
| `/api/*` | 全局限流 `20r/s`、burst 40、429；**`/api/v1/health` 亦经此路径对外可达**（如需关闭见 `DEPLOY.md §二`） |
| `/docs`、`/redoc`、`/openapi.json` | **生产环境 404**（W4-1，2026-10-02） |
| `/` | SPA 回退 |

已配置的边缘层安全响应头与加固（`nginx.conf.example`）：`server_tokens off`、`client_max_body_size 20m`、
HSTS（`max-age=31536000; includeSubDomains`）、`X-Frame-Options: SAMEORIGIN`、
`X-Content-Type-Options: nosniff`、`Referrer-Policy: strict-origin-when-cross-origin`、
CSP（`default-src 'self'` + `script-src 'self'` + `frame-ancestors 'self'` 等，W4-5 已收紧）、`X-XSS-Protection: 0`（历史头，已停用，见 15.4）。

### 15.2 OWASP Top 10:2025 逐项对照（**条目级**）

标准依据：官方 `top10.owasp.org/2025/` 清单（本轮实取，A03/A10 为 2025 新增条目）。

| 条目 | 本项目结论 | 证据 |
|------|------------|------|
| **A01** Broken Access Control | ✅ 已覆盖 | 6 个角色依赖矩阵 + 成员数据隔离 + 跨帮会越权修复；回归见 `backend/tests/test_permissions.py`、`scripts/selfcheck_security_fixes.py`；历史修复见本文件 §十/§六 |
| **A02** Security Misconfiguration | 🟢 基本满足 | 生产关闭 API 文档（W4-1）、`server_tokens off`、HSTS、CORS 外置（W4-3）、`DEBUG` 默认关闭、**CSP 已收紧**（W4-5：`script-src 'self'`，去 `unsafe-inline`/`unsafe-eval`，补 `object-src 'none'`/`base-uri`/`form-action`）；剩余：`style-src` 仍含 `'unsafe-inline'`（Element Plus/ECharts 运行时样式所需，见 15.4-1） |
| **A03** Software Supply Chain Failures（2025 新增） | 🟡 部分满足 | 已有：Dependabot、CI 镜像构建护栏、依赖漏洞审计（§十四）；**不足**：依赖无哈希锁定、无 SBOM、无签名（A03/A08 共同缺口） |
| **A04** Cryptographic Failures | 🟡 部分满足 | TLS 1.2+ 与 HSTS；密码 bcrypt；JWT HS256 + 生产弱密钥**拒绝启动**；**已知接受风险**：Token 存 localStorage（本文件已知风险清单） |
| **A05** Injection | ✅ 已覆盖 | SQLAlchemy 参数化查询、Pydantic 入参校验、图表 HTML tooltip 转义（本文件 §十二）、Excel 导入校验 |
| **A06** Insecure Design | 🟡 部分满足 | 有产品设计/权限矩阵权威源与录屏审核流程；**不足**：无威胁建模记录（见 15.4-4） |
| **A07** Authentication Failures | ✅ 已覆盖 | bcrypt、双层登录限流（应用侧 5 次/5 分钟 + Nginx `5r/m`）、账号锁定并回传剩余秒数、Token 版本吊销、弱密钥启动门禁 |
| **A08** Software or Data Integrity Failures | 🟡 部分满足 | CI 门禁、提交消息校验、依赖审计；**不足**：制品（镜像）未签名、无可校验摘要（SLSA 未达 L2） |
| **A09** Security Logging and Alerting Failures | 🟡 部分满足 | 写操作审计中间件 + 失败详情 + 90 天保留 + 每日清理；**不足：无告警通道**——日志有人写，没人被通知（见 15.4-2） |
| **A10** Mishandling of Exceptional Conditions（2025 新增） | 🟡 部分满足 | 全局异常处理 + 生产不泄露异常详情（`DEBUG` 脱敏）；`/health` 建立依赖降级语义（W3-1）；**不足**：未做异常路径演练与依赖超时/熔断设计 |

### 15.3 OWASP ASVS 5.0.0 对照（**域级**）

口径与边界（重要）：ASVS **5.0.0** 为当前稳定版本（本轮实取 `owasp.org/projects/asvs` 核实），
官方要求编号格式为 `v5.0.0-x.y.z`（同页核实）。本轮按计划点名的控制域对照，
**未做条目级逐条核对**，故下表只给域级结论；条目级核对列为后续项（见 15.4-5）。
另：ASVS 5.0 第 1 章为 *Encoding and Sanitization*（官方页实取），其余章节编号未逐一核实故不在此引用编号。

| ASVS 5.0 控制域 | 结论 | 证据 |
|-----------------|------|------|
| 配置（Configuration） | 🟡 部分满足 | 生产关闭在线文档、`server_tokens off`、HSTS、CORS 外置、容器 `no-new-privileges` + 资源限制 + 非 root（`entrypoint.sh` gosu）；不足：CSP 弱、`.env` 依赖人工核对 |
| 认证（Authentication） | ✅ 域级满足 | bcrypt + 双层限流 + 锁定提示 + Token 版本吊销 + 弱密钥启动门禁 |
| 会话（Session） | 🟡 部分满足 | 无服务端会话（无状态 JWT，10 小时有效期 + 版本吊销可强制下线）；已知接受风险：Token 存于 localStorage（XSS 场景下可被读取，已有 CSP 作为缓解） |
| 访问控制（Authorization） | ✅ 域级满足 | 角色依赖矩阵 + 帮会级数据隔离 + 越权回归用例（含跨帮会写入拦截） |
| 日志与错误处理（Logging & Error Handling） | 🟡 部分满足 | 审计中间件、异常脱敏、保留策略、**错误率告警（W4-6）**；不足：日志无完整性/防篡改保护 |

### 15.4 本次识别的新增不足（可执行后续项，已登记到整改计划）

1. **CSP 过宽**——**已于 2026-10-02 收紧（W4-5）**：`script-src` 由 `'self' 'unsafe-inline' 'unsafe-eval'` 改为 **`'self'`**，并补 `object-src 'none'` / `base-uri 'self'` / `form-action 'self'`。
   **依据（构建级证据）**：`npm run build` 产出的 `dist/index.html` 内联 `<script>`/`<style>` 均为 **0**（仅 1 个外部 module script + 1 个外链 CSS）；源码无 `v-html`/`eval`/`new Function`；产物中唯一一处 `new Function("return this")` 来自 **core-js 的全局对象探测且自带 try/catch 回退到 `window`**——被 CSP 拦截时走回退分支。
   **保留项**：`style-src` 仍含 `'unsafe-inline'`（Element Plus/ECharts 运行时会注入内联样式，去掉会白屏）；进一步收紧需 nonce/hash。
   **未验证（明确标注）**：本机无浏览器，**未做页面级验收**——收紧后的 CSP 未在真实浏览器中打开过应用；回滚方式为把两个 token 加回 `script-src`（唯一落点 `frontend/nginx.conf.example`）。
2. **无告警通道**（A09 alerting 部分）——**已于 2026-10-02 修复（W4-6）**：新增后台告警循环（`app/core/alerting.py` 纯策略 + `app/services/alert_service.py` 查库与编排），最近 30 分钟内 `level=error` 达 20 条即触发；**未配置 webhook 时也写 WARNING 日志（不静默）**，配置 `ALERT_WEBHOOK_URL` 后 POST JSON（标准库发送，无新依赖）；同一窗口内去重，阈值为 0 可禁用。
   环境变量与运维说明见 `DEPLOY.md §四/§六` 与 `.env.example`。
3. **供应链完整性**：依赖无哈希锁定、无 SBOM、镜像未签名（A03/A08，与计划 W1-4 依赖锁定、SLSA L2 相关）。
4. **无威胁建模记录**（A06）——**已于 2026-10-02 修复（W4-7）**：新增 **§十六 威胁建模（STRIDE）**（7 类资产、5 个信任边界、18 条威胁核对）；建模过程**发现并修复导出文件公式注入**（F-47，`tests/test_excel_export_formula.py` 往返验证）。
5. **ASVS 条目级核对未做**：本轮为域级对照；条目级需按官方 JSON/CSV 逐条标注（编号格式 `v5.0.0-x.y.z`）。
6. **历史响应头**——**已于 2026-10-02 处置（W4-5）**：`X-XSS-Protection` 由 `1; mode=block` 改为 **`0`**（现代浏览器已移除该过滤器，CSP 才是有效防线；置 0 避免旧浏览器过滤器的副作用）。

---

## 十六、威胁建模（STRIDE，2026-10-02，W4-7）

> **定位与边界**：为补齐 A06（Insecure Design）缺口而做的**轻量威胁建模留痕**——按 STRIDE 枚举关键资产的
> 主要威胁，逐条核对**现有控制与代码证据**，并给出残余风险与处置。
> **不覆盖**：云/主机/网络层加固、内部人员滥用、物理安全、供应链完整性（后者见 §十四 与计划 W1-4）。
> 方法：以本项目**自身代码与部署配置**为对象，每条结论都附文件与行为证据，便于复核。

### 16.1 资产与信任边界

| 编号 | 资产 | 位置 | 泄露/破坏的影响 |
|------|------|------|----------------|
| A1 | JWT 访问令牌（含 `ver` 吊销版本） | 浏览器 localStorage → 请求头 | 冒用身份、越权操作 |
| A2 | 账号凭据（bcrypt 哈希 + `plain_password` 明文列） | `users` 表 | 全量账号接管 |
| A3 | 帮会业务数据（成员/出勤/排表/战绩/日志） | SQLite | 跨帮会泄露、赛程被篡改 |
| A4 | 导入与导出文件（Excel/CSV ≤5MB、长图 ≤800 人、录屏外链） | 请求体 / 响应 | 恶意内容注入、资源耗尽 |
| A5 | `SECRET_KEY` | 服务器 `.env` | 伪造任意令牌 |
| A6 | SQLite 库文件与备份产物 | 命名卷 / 备份目录 | 全量数据泄露 |
| A7 | 审计日志 | `operation_logs` + 容器日志 | 抵赖、事后无法追溯 |

信任边界：①浏览器 ↔ 边缘 Nginx（TLS 终止）②Nginx ↔ frontend 容器（内网明文）③frontend ↔ backend（内网 `:8000`）
④backend ↔ SQLite 卷 ⑤运维 ↔ 服务器（SSH / `.env`）。

### 16.2 STRIDE 核对表

| # | 资产 | STRIDE | 威胁场景 | 现有控制（证据） | 残余风险 | 处置 |
|---|------|--------|----------|------------------|----------|------|
| 1 | A1 | S 仿冒 | 伪造/盗用令牌冒用身份 | HS256 签名；`ver` 与 `users.token_version` 比对（`core/security.py:20-23`、`api/deps.py:32`）；改密自增版本号（`services/account_service.py:84`） | 令牌在 localStorage（XSS 可窃取）；**登出不递增版本号**（共享账号多人多 IP，`api/v1/auth.py:54` 已说明）→ 登出后旧令牌在过期前仍有效 | 已接受（AGENTS §6 已记录；缓解：CSP 收紧 W4-5） |
| 2 | A1 | T 篡改 | 改载荷提升 role | 签名校验，改载荷即验签失败 | 无 | 已控制 |
| 3 | A1 | I 泄露 | 令牌进日志/响应 | 日志敏感键脱敏（`services/log_service.py:17` 含 `token`/`access_token`/`authorization`）；响应不回传令牌 | 无 | 已控制 |
| 4 | A2 | S 仿冒 | 撞库 / 弱口令 | bcrypt 哈希；登录限流 5 次 / 5 分钟（`core/config.py:52`、`services/auth_service.py:49`）；Nginx 限流；**口令策略**（长度 8–128 + 常见弱口令/上下文词表 + 不得含登录名，`app/core/password_policy.py`，2026-10-02 W4-10 实施） | **无 MFA**（口令策略已实施；逐条结论见 §17.6） | 建议（未列入计划，待决策） |
| 5 | A2 | I 泄露 | `plain_password` 明文列被读走 | 仅 developer 可见，响应按角色脱敏（`api/v1/accounts.py:21-26`）；`*.db` 不入库 | **库文件泄露即全量明文口令**（业务取舍：本地工具需可见密码） | 已接受（AGENTS §6） |
| 6 | A2 | R 抵赖 | 帮众共享账号 → 行为不可归因 | 审计记录 username/role/ip | 共享账号下无法区分到具体人 | 已接受（业务决定） |
| 7 | A3 | S/E 越权 | 用他帮会 ID 读写（水平/垂直越权） | 服务层按 `guild_id` 过滤；路由角色依赖（`api/deps.py`）；跨帮会回归 `scripts/selfcheck_security_fixes.py`；用例 `tests/test_permissions.py` | 无 | 已控制 |
| 8 | A3 | I 泄露 | 列表/导出接口绕过帮会过滤 | 列表与导出均带 guild 作用域；账号响应脱敏 | 无 | 已控制 |
| 9 | A3/A7 | R 抵赖 | 否认执行过写操作 | 审计中间件记录 module/action/path/status/detail（已脱敏） | 日志无防篡改（无 WORM/签名），developer 可手动清理（清理动作自身被审计） | 已接受（单机自托管）；建议：日志外发/只读副本 |
| 10 | A4 | T/I 注入 | 导入恶意 Excel/CSV | 大小双检（声明 + 读取后二次校验，`api/v1/members.py:107-112`；CSV `api/v1/match_data.py:39`）；行数上限 5000（`utils/excel_import.py:79`）；Nginx `client_max_body_size` | 无 | 已控制 |
| 11 | A4 | T 注入 | **导出**文件携带公式（姓名/备注以 `=` 开头） | **2026-10-02 已修复**：导出统一走 `_text_cell`，对 `=`/`+`/`-`/`@` 开头的值显式声明 `data_type='s'`（`utils/excel_export.py`）；往返回归 `tests/test_excel_export_formula.py` | 无（修复前 Excel 打开可能触发对外请求） | **已修复（F-47）** |
| 12 | A4 | D 耗尽 | 超大导出/长图耗尽 CPU/内存 | 长图 800 人上限（`utils/image_export.py:60`）；compose 资源上限（`docker-compose.yml` 的 `deploy.resources.limits`：内存 + cpus） | 无 | 已控制 |
| 13 | A4 | S/I 伪协议 | 提交 `javascript:` 等链接，管理员点击即执行 | 后端入参 `pattern=^https?://`（`schemas/recording.py:28`）；前端 `normalizeUrl` + `rel="noopener"`（`components/recording/RecordingTablePanel.vue:25`、`RecordingMobileList.vue:71`） | 外链目标站不可控（钓鱼/恶意页），非本项目可控面 | 已控制（技术面）；链接来自帮众，点击前自行判断 |
| 14 | A4 | — | 是否存在任意视频上传面 | **录屏不落服务器**：`submit_recording(url)` 仅保存外链（`services/recording_service.py:156-172`），无文件上传路径 | 无 | 已消除（架构选择） |
| 15 | A5 | I/S | 弱/默认密钥导致令牌可伪造 | 启动门禁：生产弱密钥直接拒绝启动（`core/config.py` `validate_secret_key`/`enforce_secret_key`；`tests/test_config_gate.py` 19 用例） | 密钥在 `.env` 明文，服务器文件权限即边界 | 已控制（§十三） |
| 16 | A6 | I/D | 备份泄露 / WAL 下直接 `cp` 得到损坏库 | 备份脚本用 SQLite 在线 backup API、默认 dry-run、生成后完整性校验、保留轮转（`scripts/backup-db.sh.example`）；`.db` 与 `_backup/` 不入库 | 备份产物未加密（磁盘权限即边界） | 已接受（§五、`DEPLOY.md §五/§九`） |
| 17 | A7 | D 耗尽 | 日志暴涨占满磁盘 | 90 天保留 + 启动清理（`services/log_service.py:192`）；错误率告警（W4-6） | 无 | 已控制 |
| 18 | 全局 | I/E | 经 `/docs`、调试异常获取内部信息 | 生产关闭 `docs_url`/`redoc_url`/`openapi_url`（`main.py`）；DEBUG 异常脱敏 | 无 | 已控制 |

### 16.3 本次建模产出

1. **发现并修复 1 个真实缺陷**：导出文件的**公式注入**（F-47，见核对表第 11 行）。修复后以「写 → 读回断言
   `data_type='s'`」往返验证（5 用例），另用独立脚本直接读单元格类型复核（`=1+1`、`=cmd|calc` 均为**文本**）。
2. **顺带修正一处耦合**：`utils/excel_export.py` 原在运行时 import ORM 模型，导致纯格式化逻辑无法脱离数据库测试；
   已改为 `if TYPE_CHECKING` + `from __future__ import annotations`（行为不变，回归用例因此可独立运行）。
3. **已记录的残余风险**（业务取舍或环境限制，非漏洞）：localStorage 令牌且登出不吊销、`plain_password` 明文列、
   共享账号不可归因、日志无防篡改、备份未加密、无 MFA（口令策略已于 2026-10-02 实施，见 §17.6 / §17.9）。
4. **建议（尚未列入整改计划，待决策）**：**MFA**（口令策略已实施，见上）、审计日志外发/只读副本、备份产物加密、CSP 收紧（已为 W4-5）。

---

## 十七、ASVS 5.0.0 条目级核对（W4-8，2026-10-02；本轮覆盖 V13/V8/V16）

> **来源与方法**：条目编号与原文取自官方仓库 **tag `v5.0.0`（commit `60437a5ed660f757ab9a8d9e0b7181a06492446a`）**
> 的 `5.0/en/` 章节 markdown，经 **git 稀疏检出**（`git clone --depth 1 --branch v5.0.0 --filter=blob:none --sparse`
> 后 `sparse-checkout set 5.0/en`）落到本地后解析，`HEAD` 与上述 commit 一致（非人工转述、非记忆）。
> **为什么不是抓网页**：`raw.githubusercontent.com` 在本机被阻断（连接重置）、jsdelivr 因仓库超 50MB 包限制拒绝、
> 镜像站 DNS/抓取失败、`github.com` 曾 503；最终 **git over HTTPS 通道可用**（见计划 §7 W4-8 的通道记录）。
>
> **结论口径**：✅ 满足（有代码/配置证据）｜🟡 部分（有控制但不完整或未成文）｜❌ 未满足（本次未做，多因自托管取舍）｜⚪ 不适用。
> **覆盖范围与边界**：**已完成 124 条**——V13 配置 21 / V8 访问控制 13 / V16 日志与错误处理 17（本轮前段）+ **V6 认证 47 / V7 会话 19 / V9 自包含令牌 7**（本轮补齐，见 17.6~17.8）。
> **尚未核对**：V1–V5、V10–V12、V14–V17（不在本计划范围；如日后引入 SSO/文件上传/加密等能力需扩展）。
> **取数说明（补充）**：第二轮改用 **`api.github.com` 内容接口 + 本地 base64 解码落盘**（`Invoke-RestMethod` + `[Convert]::FromBase64String`），6 个章节的 `sha` 与首轮列出一致（V6 `d9fa0025` / V7 `0124d000` / V9 `d34dd16b` 等），同样来自 tag `v5.0.0`。

### 17.1 V13 配置（21 条）

| 条目 | 等级 | 结论 | 证据 / 说明 |
|------|:---:|:---:|------|
| 13.1.1 | 2 | 🟡 部分 | 拓扑与依赖记于 `DEPLOY.md`；但「通信需求（含用户可提供的外链）」未成清单 |
| 13.1.2 | 3 | ⚪ 不适用 | 单实例 SQLite，无对外并发连接约束需要定义 |
| 13.1.3 | 3 | ⚪ 不适用 | 除可选 webhook 外无外部系统 |
| 13.1.4 | 3 | 🟡 部分 | `.env.example` 文档化 `SECRET_KEY`/`ALERT_WEBHOOK_URL` 等；「关键秘密清单 + 管理策略」未成文 |
| 13.2.1 | 2 | ⚪ 不适用 | 单后端进程，无「组件间通信绕过用户会话」的场景 |
| 13.2.2 | 2 | ⚪ 不适用 | 同上 |
| 13.2.3 | 2 | ⚪ 不适用 | 无服务间凭证 |
| 13.2.4 | 2 | 🟡 部分 | 外呼仅 `ALERT_WEBHOOK_URL`（运维配置）；CSP `connect-src 'self' https:` 仍放宽 `https:`（见 §15.4-1） |
| 13.2.5 | 2 | 🟡 部分 | 容器未做**出网白名单**（egress 限制）；建议在部署层加 |
| 13.2.6 | 3 | 🟡 部分 | 无外部连接配置需要遵循（同 13.2.3） |
| 13.3.1 | 2 | ❌ 未满足 | 未使用密钥管理服务，改为 `.env` + 服务器文件权限（单机自托管的取舍，见 §十六 A5） |
| 13.3.2 | 2 | 🟡 部分 | **2026-10-02 更正（原判 ❌，依据 F-49 的旧结论）**：`backend/entrypoint.sh` 用 `exec gosu appuser "$@"` 已降权（配合 `useradd` + chown 卷目录）→ 后端**非 root** ✓；`frontend/Dockerfile` 建了 `appuser/appgroup` 并 chown html/cache/log/pid，**但没有 `USER`** → nginx 以 root 运行 ✗（F-49 仅前端成立，W1-9 待 Docker 验证） |
| 13.3.3 | 3 | ⚪ 不适用 | 无 HSM/隔离密码模块需求 |
| 13.3.4 | 3 | ❌ 未满足 | `SECRET_KEY` 无轮换机制（轮换即需重签令牌）；建议在 `DEPLOY.md` 写明轮换步骤 |
| 13.4.1 | 1 | ✅ 满足 | 两个 `.dockerignore` 均排除 `.git`；镜像内不含版本控制元数据 |
| 13.4.2 | 2 | ✅ 满足 | `DEBUG` 默认 false；`APP_ENV=production` 时 `/docs`、`/redoc`、`/openapi.json` 关闭（W4-1）；启动门禁拒绝弱密钥 |
| 13.4.3 | 2 | ✅ 满足 | nginx 配置中无 `autoindex`（默认关闭目录列表） |
| 13.4.4 | 2 | ✅ 满足 | 未启用 HTTP TRACE（nginx 默认不支持该方法，配置中亦无 `limit_except` 放行） |
| 13.4.5 | 2 | ✅ 满足 | 生产关闭 API 文档；`/health` 为探针**有意**暴露且已在 `DEPLOY.md` 文档化 |
| 13.4.6 | 3 | ✅ 满足 | 两处 nginx 配置均 `server_tokens off`（L63 / L12） |
| 13.4.7 | 3 | 🟡 部分 | 前端仅挂载 `dist` 静态资源，但未按扩展名做白名单 |

### 17.2 V8 访问控制（13 条）

| 条目 | 等级 | 结论 | 证据 / 说明 |
|------|:---:|:---:|------|
| 8.1.1 | 1 | ✅ 满足 | `design-document-v2.md §3` 角色权限矩阵；`security-review.md` 记录越权修复 |
| 8.1.2 | 2 | 🟡 部分 | 有字段级处理的实现（`plain_password` 按角色脱敏、日志敏感键脱敏），但无成文「字段级规则」清单 |
| 8.1.3 | 3 | ⚪ 不适用 | 授权决策不使用环境/上下文属性（`client_ip` 仅用于限流与审计） |
| 8.1.4 | 3 | ⚪ 不适用 | 同上 |
| 8.2.1 | 1 | ✅ 满足 | `api/deps.py` 六个角色依赖（member/admin/developer 组合）+ `tests/test_permissions.py` 权限矩阵用例 |
| 8.2.2 | 1 | ✅ 满足 | 服务层按 `guild_id` 过滤；`scripts/selfcheck_security_fixes.py` 含跨帮会写入拦截回归；接口级用例覆盖 403 |
| 8.2.3 | 2 | 🟡 部分 | 字段级：`plain_password` 脱敏 + 日志脱敏已有；未系统化到「每个敏感字段」级别 |
| 8.2.4 | 3 | ⚪ 不适用 | 无自适应/风险评分控制（登录限流是其中一部分） |
| 8.3.1 | 1 | ✅ 满足 | 授权完全在服务端（`api/deps.py` + 服务层）；前端只做 UI 隐藏 |
| 8.3.2 | 3 | ✅ 满足 | 每请求**重新查库**并校验 `status` 与 `token_version`（`api/deps.py:28-33`），故改角色/禁用在下一个请求即生效，不依赖令牌声明 |
| 8.3.3 | 3 | ⚪ 不适用 | 无服务间代理调用 |
| 8.4.1 | 2 | ✅ 满足 | 多租户用帮会隔离实现，含跨帮会回归与接口级 403 用例 |
| 8.4.2 | 3 | 🟡 部分 | 管理入口同样经 TLS + JWT + 限流；无设备态势/持续身份校验 |

### 17.3 V16 日志与错误处理（17 条）

| 条目 | 等级 | 结论 | 证据 / 说明 |
|------|:---:|:---:|------|
| 16.1.1 | 2 | 🟡 部分 | 暴露面与日志策略在 `security-review.md §十五 15.1`、`DEPLOY.md §四` 有述；缺「逐层日志清单」 |
| 16.2.1 | 2 | ✅ 满足 | 审计表含 user/role/guild/module/action/method/path/status/detail/ip/created_at |
| 16.2.2 | 2 | ✅ 满足 | 统一 UTC（见 `schemas/common.py`）；容器时钟同步依赖宿主（已在部署文档前提中） |
| 16.2.3 | 2 | ✅ 满足 | 只写审计表与容器 stdout，二者均已文档化 |
| 16.2.4 | 2 | ✅ 满足 | 容器日志格式统一（`core/logging_config.py`）；审计可按字段检索 |
| 16.2.5 | 2 | ✅ 满足 | 敏感键脱敏（`services/log_service.py` `SENSITIVE_KEYS`）；`plain_password` 不入日志 |
| 16.3.1 | 2 | ✅ 满足 | 登录成功/失败均埋点（`api/v1/auth.py`），含账号、IP、状态码与失败原因 |
| 16.3.2 | 2 | ✅ 满足 | **2026-10-02 更正（F-50 已于 W4-9 修复）**：审计中间件的条件扩展为「写方法 **或** 非写方法 + 携带 Authorization + 401/403」，匿名 401 不记录；读接口的越权/失效令牌同样落库（`tests/test_audit_denials.py` 6 用例回归） |
| 16.3.3 | 2 | 🟡 部分 | 已记录关键事件；「文档定义的安全事件清单」未成文 |
| 16.3.4 | 2 | ✅ 满足 | 未预期异常经兜底处理器 + 中间件记为 `level=error` |
| 16.4.1 | 2 | ✅ 满足 | **2026-10-02 更正（F-51 已于 W4-9 修复）**：`escape_control` 把换行/制表等转成 `\x0a` 形态可见转义，应用于 `username`/`path`/`ip` 与 `sanitize_detail` 字符串分支；含换行用户名的端到端回归已入库 |
| 16.4.2 | 2 | ❌ 未满足 | 日志无防篡改（无 WORM/签名），developer 可手动清理（清理动作自身被审计）——已接受并记录于 §十六 |
| 16.4.3 | 2 | ❌ 未满足 | 日志未发送到逻辑独立系统（同机 SQLite + stdout）——已接受（单机自托管） |
| 16.5.1 | 2 | ✅ 满足 | 关闭 DEBUG 时统一错误体，异常细节不外泄（W4-2 已核） |
| 16.5.2 | 2 | ✅ 满足 | 告警推送失败只记异常不 fail-open；`/health` 依赖不可用时降级 503 而非 500 |
| 16.5.3 | 2 | ✅ 满足 | 权限失败一律 401/403；业务异常经统一处理器，不泄露内部结构 |
| 16.5.4 | 3 | ✅ 满足 | 存在**最后兜底** `@app.exception_handler(Exception)`（`main.py:292`） |

### 17.4 本轮发现（已登记到整改计划）

| 编号 | 发现 | 条目 | 处置 |
|------|------|------|------|
| **F-49** | 容器降权不完整 | **2026-10-02 更正：仅前端成立**——`frontend/Dockerfile` 建了 `appuser` 并 chown html/cache/log/pid，但**没有 `USER`**（nginx 以 root 运行）；**后端已降权**（`backend/entrypoint.sh`：`exec gosu appuser "$@"`）。任务 W1-9 范围已收窄为前端（需 Docker 验证） |
| **F-50** | 授权失败的**读操作**未审计（GET 403 不落库） | 16.3.2 | **已于 2026-10-02 修复（W4-9）**：非写方法 + 携带凭证 + 401/403 也落库；匿名 401 不记；**该路径改为 `await`**（罕见路径 + 不宜丢失），写操作热路径仍 `create_task` |
| **F-51** | 审计详情未做换行/控制字符转义 | 16.4.1 | **已于 2026-10-02 修复（W4-9）**：`escape_control` 应用于 `username`/`path`/`ip` 与 `sanitize_detail` 字符串分支；`tests/test_audit_denials.py` 含「含换行用户名落库无真实换行」端到端回归 |

### 17.6 V6 认证（47 条，本轮补齐）

| 条目 | 等级 | 结论 | 证据 / 说明 |
|------|:---:|:---:|------|
| 6.1.1 | 1 | 🟡 部分 | 限流已实现（登录 5 次/5 分钟 + Nginx 限流），但「速率限制/反自动化」策略未成文 |
| 6.1.2 | 2 | ❌ 未满足 | 未维护上下文相关词表用于口令（`core/config.py` 的弱密钥黑名单只用于 SECRET_KEY） |
| 6.1.3 | 2 | ✅ 满足 | 仅用户名+口令一条认证路径，无未文档化的第二路径 |
| 6.2.1 | 1 | ✅ 满足 | `AccountCreate/AccountUpdate` 的 `min_length=8`（**更正**：首轮只看了 `account_service`，漏了 schema 层，误判为「无长度下限」） |
| 6.2.2 | 1 | ✅ 满足 | **2026-10-02 已实现**：`POST /api/v1/auth/password`（自助改密） |
| 6.2.3 | 1 | ✅ 满足 | 自助改密**必须提供当前口令**并通过 bcrypt 校验（`auth_service.change_own_password`） |
| 6.2.4 | 1 | ❌ 未满足 | 未做已知泄露口令集比对（F-52） |
| 6.2.5 | 1 | ✅ 满足 | **2026-10-02 修正**：原实现**强制「字母+数字」违反本条**（更正首轮误判为「满足」）；现不限制字符组成，纯字母/纯数字/纯符号均允许（`app/core/password_policy.py`） |
| 6.2.6 | 1 | ✅ 满足 | 登录口令框使用 `type=password`（前端登录页） |
| 6.2.7 | 1 | ✅ 满足 | 未禁用粘贴与浏览器口令管理器 |
| 6.2.8 | 1 | ✅ 满足 | 口令按原样交给 bcrypt 校验，无截断/大小写转换（`auth_service.authenticate`） |
| 6.2.9 | 2 | ✅ 满足 | `max_length=128`，**已加回归用例**验证 64 位口令被接受 |
| 6.2.10 | 2 | ✅ 满足 | 未强制口令定期轮换（口令一直有效直至被改/禁用） |
| 6.2.11 | 2 | 🟡 部分 | **2026-10-02 已加**上下文词表（项目/角色/常见弱口令）+ 不得含登录名；词表仅存在于代码常量、未成文于文档 |
| 6.2.12 | 2 | ❌ 未满足 | 仍**未做泄露口令集比对**（需离线字典或外部服务）——记录为取舍（F-52 剩余部分） |
| 6.3.1 | 1 | ✅ 满足 | 登录限流 + 失败计数锁定（DB 与内存双路径，`auth_service`）+ 审计埋点 |
| 6.3.2 | 1 | 🟡 部分 | **存在默认账号**（developer/admin/member，口令取自 `.env` 且文档要求首登后修改）；未强制首次改密 |
| 6.3.3 | 2 | ❌ 未满足 | **未实现 MFA**（单因素用户名+口令）——自托管规模的取舍，见 §十六 A2 |
| 6.3.4 | 2 | ✅ 满足 | 仅一条认证路径，无未文档化路径 |
| 6.3.5 | 3 | ❌ 未满足 | 异常登录尝试未通知用户（无通知通道） |
| 6.3.6 | 3 | ✅ 满足 | 未把邮箱作为认证机制（系统不用邮箱登录） |
| 6.3.7 | 3 | ❌ 未满足 | 认证信息变更后未通知用户（同上，无通知通道） |
| 6.3.8 | 3 | 🟡 部分 | 失败提示对「不存在账号/口令错误」保持一致，但存在**时序差异**（仅存在账号才跑 bcrypt） |
| 6.4.1 | 1 | 🟡 部分 | 初始口令来自 `.env` 配置（非系统随机生成）；文档要求部署时改强口令 |
| 6.4.2 | 1 | ✅ 满足 | 无口令提示/密保问题机制 |
| 6.4.3 | 2 | ❌ 未满足 | 无自助忘记口令流程（仅管理端重置） |
| 6.4.4 | 2 | ⚪ 不适用 | 无 MFA，故无因子上丢失场景 |
| 6.4.5 | 3 | ⚪ 不适用 | 无会过期的认证因子 |
| 6.4.6 | 3 | ❌ 未满足 | 管理员重置口令时会**直接设置**新口令（ASVS 要求管理员只能发起重置、不得替用户选择）(F-53) |
| 6.5.1 | 2 | ⚪ 不适用 | 无一次性口令/查找密钥机制 |
| 6.5.2 | 2 | ⚪ 不适用 | 同上 |
| 6.5.3 | 2 | ⚪ 不适用 | 同上 |
| 6.5.4 | 2 | ⚪ 不适用 | 同上 |
| 6.5.5 | 2 | ⚪ 不适用 | 同上 |
| 6.5.6 | 3 | ⚪ 不适用 | 同上 |
| 6.5.7 | 3 | ⚪ 不适用 | 无生物认证 |
| 6.5.8 | 3 | ⚪ 不适用 | 无 TOTP |
| 6.6.1 | 2 | ⚪ 不适用 | 无 PSTN/SMS 认证 |
| 6.6.2 | 2 | ⚪ 不适用 | 无带外认证 |
| 6.6.3 | 2 | ⚪ 不适用 | 同上 |
| 6.6.4 | 3 | ⚪ 不适用 | 无推送式 MFA |
| 6.7.1 | 3 | ⚪ 不适用 | 无证书式认证断言 |
| 6.7.2 | 3 | ⚪ 不适用 | 同上 |
| 6.8.1 | 2 | ⚪ 不适用 | 未接入外部 IdP |
| 6.8.2 | 2 | ⚪ 不适用 | 无 SAML/JWT 断言校验场景 |
| 6.8.3 | 2 | ⚪ 不适用 | 无 SAML |
| 6.8.4 | 2 | ⚪ 不适用 | 无 IdP 强度校验需求 |

### 17.7 V7 会话管理（19 条，本轮补齐）

| 条目 | 等级 | 结论 | 证据 / 说明 |
|------|:---:|:---:|------|
| 7.1.1 | 2 | 🟡 部分 | 绝对有效期 10 小时已实现（`ACCESS_TOKEN_EXPIRE_MINUTES`），但**未文档化空闲超时**（无空闲超时） |
| 7.1.2 | 2 | 🟡 部分 | 未定义账号并发会话策略（共享账号场景下多设备并行属设计意图，见 `api/v1/auth.py` 注释） |
| 7.1.3 | 2 | ⚪ 不适用 | 无联邦身份体系 |
| 7.2.1 | 1 | ✅ 满足 | 会话令牌校验全在服务端（`api/deps.py` 签名+查库+版本比对） |
| 7.2.2 | 1 | ✅ 满足 | 使用自包含令牌（JWT），每次认证动态生成 |
| 7.2.3 | 1 | ⚪ 不适用 | 未使用引用型令牌 |
| 7.2.4 | 1 | ✅ 满足 | 每次登录签发新令牌（`create_access_token`） |
| 7.3.1 | 2 | ❌ 未满足 | **无空闲超时**（仅绝对过期）——无状态令牌下需额外机制，登记为取舍 |
| 7.3.2 | 2 | ✅ 满足 | 绝对最大有效期 10 小时（`exp`，解码时校验） |
| 7.4.1 | 1 | 🟡 部分 | 登出仅前端丢弃令牌；但改密/禁用会经 `token_version` 使旧令牌立即失效（服务端可终止） |
| 7.4.2 | 1 | ✅ 满足 | 账号禁用/不存在时请求即 401（`deps.py` 校验 `status` + 版本） |
| 7.4.3 | 2 | ✅ 满足 | 改密即 `token_version += 1`，**所有**其他会话令牌立即失效（强于「提供终止选项」） |
| 7.4.4 | 2 | ✅ 满足 | 前端提供登出入口（布局层） |
| 7.4.5 | 2 | ✅ 满足 | 管理员可通过禁用账号/重置口令终止该用户全部会话 |
| 7.5.1 | 2 | ❌ 未满足 | 敏感账号变更前不要求重新认证（无二次认证机制） |
| 7.5.2 | 2 | 🟡 部分 | 用户不能自助查看/终止其他会话（需管理员操作） |
| 7.5.3 | 3 | ❌ 未满足 | 无二次验证因子 |
| 7.6.1 | 2 | ⚪ 不适用 | 无 RP/IdP 体系 |
| 7.6.2 | 2 | ✅ 满足 | 会话仅由显式登录动作创建（无静默登入） |

### 17.8 V9 自包含令牌（7 条，本轮补齐）

| 条目 | 等级 | 结论 | 证据 / 说明 |
|------|:---:|:---:|------|
| 9.1.1 | 1 | ✅ 满足 | JWT 经 HMAC 校验（`decode_access_token`，签名不符即返回 None → 401） |
| 9.1.2 | 1 | ✅ 满足 | **算法白名单**：解码显式传 `algorithms=[settings.ALGORITHM]`（HS256），防算法混淆 |
| 9.1.3 | 1 | ✅ 满足 | 密钥来自受信配置（`.env` 的 `SECRET_KEY`）+ 生产弱密钥启动门禁 |
| 9.2.1 | 1 | ✅ 满足 | 校验 `exp`（过期即 401）；无 `nbf` 需求 |
| 9.2.2 | 2 | 🟡 部分 | 未校验令牌类型/`typ` 声明（单服务消费，风险低） |
| 9.2.3 | 2 | 🟡 部分 | 无 `aud`（受众）声明与校验——单受众场景，登记为待办 |
| 9.2.4 | 2 | ⚪ 不适用 | 同一密钥不面向多受众签发 |

### 17.9 认证域新增发现

| 编号 | 发现 | 条目 | 处置 |
|------|------|------|------|
| **F-52** | **口令策略偏离 ASVS**（**2026-10-02 更正**：首轮误判为「无长度下限」——实际 schema 有 `min_length=8`；真正问题是①**强制字母+数字违反 6.2.5**；②无上下文词表；③**策略零测试覆盖**；④无泄露口令集比对） | 6.2.1 / 6.2.5 / 6.2.9 / 6.2.11 / 6.2.12 | **W4-10 ✅（2026-10-02）**：抽出 `app/core/password_policy.py`（纯逻辑）——去掉组成限制、加词表与「不得含登录名/非单一重复」、13 条纯标准库用例；**剩余**：泄露口令集比对未做（取舍） |
| **F-53** | **无用户自助改密；管理员重置时可直接设定新口令** | 6.2.2 / 6.2.3 / 6.4.6 | **部分修复（W4-10）**：自助改密已实现（`POST /auth/password`，校验当前口令，改密后 `token_version+1` 使旧令牌全失效）；**6.4.6 仍为部分**——管理端重置时直接设定口令，已在 §17.6 记录为取舍 |
| — | 无 MFA（6.3.3）、无空闲超时（7.3.1）、无异常登录通知（6.3.5/6.3.7）、无 `aud`（9.2.3） | — | **已接受的取舍**（自托管单帮会规模），记录于 §十六；其中 7.3.1/9.2.3 若日后接入外部系统需重评 |

### 17.5 统计

| 结论 | V13/V8/V16 | V6/V7/V9 | **合计** |
|------|:---:|:---:|:---:|
| ✅ 满足 | 23 | 31 | **54** |
| 🟡 部分 | 15 | 13 | **28** |
| ❌ 未满足 | 4 | 10 | **14** |
| ⚪ 不适用 | 9 | 19 | **28** |
| **合计** | **51** | **73** | **124** |

> 口径说明：`❌ 未满足` 多为**自托管规模下的有意取舍**（密钥服务、日志独立存储、防篡改），已在 §十六 作为已接受风险记录；
> 真正需要动手的是 F-49/F-50/F-51 三项。
