# 安全与性能审查报告

> 审查日期：2026-08-20
> 审查范围：nsh-management 全栈（FastAPI 后端 + Vue3 前端 + Nginx/Docker 部署）
> 审查方式：静态代码审查（未修改任何代码）
> 结论：**存在 2 个严重问题、7 个中等问题、7 个低危/建议项，1 项依赖已知漏洞**
> 状态：**修复方案已定稿并完成代码实施（2026-08-20），待部署到服务器验证**

---

## 一、总体评价

项目在基础安全上做得不错：bcrypt 密码哈希、JWT 认证、登录失败锁定、全接口角色权限校验（`require_admin`/`require_developer`）、SQL 全参数化（无注入）、前端无 `v-html`（无存储型 XSS）、Docker 非 root 运行 + 资源限制、HTTPS + 安全响应头均已具备。

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
| 已定方案 | **不删除数据库列**（用户决策：开发者需可查看）。接口按角色收窄：`list_accounts` 仅 `developer` 返回 `plain_password`，admin/member 置 None；前端密码列仅 `auth.isDeveloper` 显示，其余显示 "-"。残余风险：数据库文件本身仍含明文，依赖服务器与备份文件安全（M-7 修复后 `_backup` 不再随部署包上传）。 |

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
| 已定方案 | 健康检查改为无凭据探活根路径（`curl http://127.0.0.1/`）；tar exclude 增加 `--exclude='_backup'`、`--exclude='DEPLOY.md'`、`--exclude='SECURITY-REVIEW.md'`，**删除 `--exclude='nginx.conf'`**（否则 B1 限流配置无法随部署包上传生效）；服务器 IP/用户名暂留脚本顶部（脚本已 gitignore）。已完成：服务器遗留 `_backup`/`DEPLOY.md`/`SECURITY-REVIEW.md` 已清理（2026-08-20，用户授权）。 |

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
- ✅ 前端无 `v-html`/`innerHTML`/`eval`，Vue 默认转义，无存储型 XSS
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

- 后端：`app/main.py`、`app/core/config.py`、`app/core/security.py`、`app/core/database.py`、`app/api/deps.py`、`app/api/v1/*.py`（auth/members/match_data/config/attendance/lineups/recording/schedules）、`app/services/*.py`、`app/utils/excel_import.py`、`app/utils/attendance_import.py`、`app/schemas/*.py`、`app/models/*.py`、`app/init_db.py`、`requirements.txt`
- 前端：`src/api/http.ts`、`src/stores/auth.ts`、`src/components/recording/RecordingTab.vue`、`index.html`、`package.json`、`vite.config.ts`
- 部署：`nginx.conf`、`docker-compose.yml`、`backend/Dockerfile`、`frontend/Dockerfile`、`entrypoint.sh`、`deploy.sh`、`.env`（仅检查强度，未输出值）、`.gitignore`
