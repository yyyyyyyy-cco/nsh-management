# 成员详情档案化设计（出勤明细 + 录屏记录 + 排表历史）

> 版本：v1.2（已实施，待浏览器验收）
> 更新日期：2026-10-12
> 状态：已实施（2026-10-12；代码与后端测试已完成，vitest 与浏览器验收由用户执行）
> 关联：`stats-report-plan.md` §6（二期规划「成员详情档案化」与「个人战绩→成员详情跳转」）、`design-game-id-change.md`（改名关联口径）、`ai-checklist.md` 第 87/92 条（删除路径防主键复用、排表导入语义）

---

## 1. 背景与目标

成员详情页（`/members/:id`，管理员专属，2026-09-17 随「成员详情战绩页」上线）当前仅「基本信息卡 + 出勤率 + 历史战绩（最近 10 场）」。管理员在成员考核、沟通反馈时缺少跨模块档案视角：哪天请假、录屏是否按时提交、历史排在哪一队。

本设计补齐三个档案区块，并落地个人战绩页的成员详情入口：

- **出勤档案**：该成员每场出勤明细（正常/请假）
- **录屏记录**：该成员每场每局的提交与审核状态（含「未提交」）
- **排表历史**：该成员每场被排入的分类/队号/位置
- **入口互通**：个人战绩查询命中常驻库成员时（仅管理员）可跳转成员详情

定位：管理员考核/沟通成员的单一入口；帮众不可访问（沿用成员详情页既有权限）。

---

## 2. 决策记录

### 2.1 已确认（2026-10-12 用户确认）

| # | 决策点 | 结论 |
|---|--------|------|
| D1 | 页面结构 | Tab 切换；三个档案按需懒加载（实现细化见 §6.1：信息卡固定顶部，Tabs 只切换内容区） |
| D2 | 录屏范围 | 包含「未提交」记录（完整呈现提交与审核状态，支持按状态筛选） |
| D3 | 时间范围 | 全量历史（自加入以来全部场次），前端分页 |

### 2.2 D4 裁决（2026-10-12 用户评审）

| # | 决策点 | 结论 | 说明 |
|---|--------|------|------|
| D4 | 排表 JSON 陈旧 `member_id` 的主动清理（配套修复） | **不纳入** | 排表历史原文不主动改写（与既定原则「历史出勤/排表/录屏/比赛数据原文不变」一致）；成员删除路径零改动；本功能自身仍正确（§3.2 查询层过滤兜底）；残余窗口登记见 §3.3 |

---

## 3. 数据口径与正确性设计（核心）

### 3.1 关联键：member_id（档案）与名称（战绩）是两条独立机制

- 三份数据均以 `member_id` 归属：`attendance_records.member_id`、`recordings.member_id`、`lineups.data` 槽位 `member_id`（正式成员）；补人（`is_filler=1` / 槽位 `member_id IS NULL`）不属于常驻库成员，不在档案范围。
- 改名（`design-game-id-change.md`）：审核通过只更新 `members.name`，历史行保持原文（`member_id` 不变）→ 档案按 `member_id` 查询**自动跨改名正确**，无需名称合并逻辑。
- 战绩区（最近 10 场）仍走名称关联（`player_identity_service`，支持合并新旧 ID 与 409 冲突），**本设计不改动**。
- 权限：三个新端点用 `require_admin`（与 `GET /members/{id}` 一致，含 developer）；成员详情路由本就 `adminOnly`。

### 3.2 防主键复用（F-78 口径）与排表 JSON 的查询层过滤

- 成员删除时 `detach_member`（`game_id_request_lifecycle.py`）已置空 `MemberGameIdRequest` / `AttendanceRecord` / `Recording` 的 `member_id` → 出勤/录屏查询天然不误算（已受 F-78 保护）。
- **排表 JSON 是例外**：`lineups.data` 槽位内的 `member_id` 没有数据库级清理；既有 `_purge_deleted_members`（`lineup_service.py`）是「读取该场排表时」的**惰性**清理。若成员删除后该场排表从未被再次打开，且新成员复用了 `members.id`（全库实态、复用机制与 2026-10-12 实测见 `database-design.md` §1.3「主键与 ID 复用口径」；与 F-78 同一事实前提），直接按 `member_id` 扫描 JSON 会把旧槽位计入新成员。
- **查询层过滤（本设计必选）**：排表历史仅收录「槽位命中 `member_id`」且「该场出勤库存在同 `member_id` 行」的记录——与 `_purge_deleted_members` 判定口径完全一致（不区分正常/请假）。实现为对命中 `schedule_id` 集合的一次附加存在性查询，成本可忽略。

### 3.3 D4 裁决：不做主动清理（用户评审，2026-10-12）

- **裁决**：**不纳入**。排表 JSON 属历史原文，**不主动改写**（与既定原则「历史出勤/排表/录屏/比赛数据原文不变」一致，见 `design-document-v2.md` §4.1）；保留 `_purge_deleted_members` 的既有惰性行为，成员删除路径（`detach_member` / `delete_member` / `batch_delete`）**零改动**。
- **残余窗口（登记在案）**：「成员删除 → 该场排表再次被打开」之间，旧槽位 `member_id` 仍留在 JSON；若该 id 被新成员复用**且**新成员出现在该旧场次的出勤库中，档案与该场排表编辑器会同样无法区分归属（与 `_purge_deleted_members` 同一盲区，属既有语义）。
- **兜底**：本功能自身正确性不受影响——§3.2 查询层双条件过滤与之同口径（槽位命中且该场出勤库存在同 `member_id`）。
- **备选（未提议）**：若未来希望从根上杜绝 id 复用，需迁移启用 `sqlite_autoincrement`（涉及全表重建），另行评估。

### 3.4 排表历史查询的性能取舍

- 实现：`lineups JOIN schedules WHERE guild_id = ?` 拉取本帮会全部排表 JSON，Python 侧扫描 60 槽匹配 `member_id`。
- 依据：单帮会赛程量级为个位数到百级，单行 JSON 约数 KB；`list_lineup_history` 已有全量 JSON 返回先例（限 50 条）。
- 后续可选（不在本期）：SQLite `json_each` 下推；若做，须保持 §3.2 过滤口径不变。

---

## 4. 接口设计（后端）

新增 3 个只读端点（`response_model=list[...]`，无分页参数——全量返回，前端分页）：

| 端点 | 返回 | 排序 |
|------|------|------|
| `GET /api/v1/members/{member_id}/attendance-history` | `AttendanceHistoryOut[]` | `match_time` 倒序（同场唯一） |
| `GET /api/v1/members/{member_id}/recording-history` | `RecordingHistoryOut[]` | `match_time` 倒序，同场 `round_number` 升序 |
| `GET /api/v1/members/{member_id}/lineup-history` | `LineupHistoryOut[]` | `match_time` 倒序（同场唯一，唯一占位由 F-85 校验保证） |

响应字段（snake_case）：

- `AttendanceHistoryOut`：`schedule_id`、`opponent`、`match_time`（naive 北京墙上时间，与赛程模块一致）、`schedule_result`（win/lose/draw/pending）、`status`（normal/leave）、`remark`（出勤行备注，可空）
- `RecordingHistoryOut`：`schedule_id`、`opponent`、`match_time`、`round_number`、`url`（可空；未提交为空）、`status`（pending/approved/rejected）、`review_remark`（可空）
- `LineupHistoryOut`：`schedule_id`、`opponent`、`match_time`、`category`（进攻1/进攻2/防守1/防守2）、`team_index`、`slot_index`、`slot_remark`（可空）

错误语义：`member_id` 不存在或不属于本帮会 → 404（复用 `member_service.get_member`，经全局 `MemberServiceError` 处理器）；未登录 → 401；帮众角色 → 403。

**路由注册**：新文件 `member_archive.py` 在 `router.py` 中注册于 `members.router` **之前**（与 `game_id_requests` 同区注释规则；`/members/{id}/xxx` 两段路径实际不会被单段 `/{member_id}` 捕获，前置注册仅为防御性顺序）。

---

## 5. 后端实现

### 5.1 文件与分层

| 文件 | 动作 | 内容 | 行数预算（上限） |
|------|------|------|------------------|
| `backend/app/api/v1/member_archive.py` | 新增 | 薄路由 3 端点（`require_admin`） | 49（150） |
| `backend/app/services/member_archive_service.py` | 新增 | 三个查询函数（含 §3.2 过滤） | 116（300） |
| `backend/app/schemas/member_archive.py` | 新增 | 三个响应模型 | 43（—） |
| `backend/app/api/v1/router.py` | 修改 | 注册 member_archive（members 之前） | +2 |
| `backend/app/services/game_id_request_lifecycle.py` | **不修改**（D4 不纳入） | 成员删除路径零改动 | 124（300） |

服务函数签名（各函数先 `member_service.get_member`（404）再查询）：

- `attendance_history(session, guild_id, member_id) -> list[dict]`
- `recording_history(session, guild_id, member_id) -> list[dict]`
- `lineup_history(session, guild_id, member_id) -> list[dict]`

### 5.2 关键实现要点

- 出勤：`select(AttendanceRecord, Schedule).join(...).where(Schedule.guild_id == …, AttendanceRecord.member_id == …)`；补人行 `member_id IS NULL` 天然排除。
- 录屏：同上（`Recording`）；「未提交」行（`url IS NULL`）照常返回（D2）。
- 排表：全量拉取 → 扫描 60 槽 → §3.2 双条件过滤（对命中 `schedule_id` 集合做一次 `AttendanceRecord.member_id` 存在性查询）。
- 不新增依赖；**无表结构变更、无 Alembic 迁移**。

---

## 6. 前端实现

### 6.1 成员详情页结构（D1 实现细化）

- 顶部**固定**成员信息卡（现有 `MemberDetailHeader` + 出勤率 + 返回按钮，始终可见——跨 Tab 保持成员上下文，返回入口不随 Tab 消失）。
- 信息卡下方 `el-tabs` 四个 Tab：
  1. 历史战绩（默认激活，现有组件区原样迁入）
  2. 出勤档案
  3. 录屏记录
  4. 排表历史
- 三个档案 Tab 使用 `lazy` 渲染：首次激活时才挂载子组件并请求，避免进入页面即发 3 个请求。

### 6.2 新增组件（`frontend/src/components/members/`）

| 组件 | 内容 | 行数预算（上限） |
|------|------|------------------|
| `MemberAttendanceHistory.vue` | 统计条（正常 X · 请假 Y，由全量数据前端统计）+ 桌面表格 + ≤768px 卡片列表 + 前端分页（el-pagination 20/50/100，默认 20；与录屏 Tab 口径一致） | 129（300） |
| `MemberRecordingHistory.vue` | 状态筛选（全部/未提交/待审核/已通过/已驳回）+ 表格/卡片 + 分页 + 链接（复制/新窗口打开） | 208（300） |
| `MemberLineupHistory.vue` | 表格/卡片（日期/对手/分类·第 N 队·第 M 位/槽位备注）+ 分页 | 108（300） |
| `member-archive-shared.css` | 三档案共享的卡片与工具行样式（沿用 `game-id-shared.css` 先例，`<style scoped src>` 引入） | 104（—） |

展示规则：

- 出勤状态标签：正常（success）/ 请假（warning），与出勤库一致。
- 录屏展示状态由 `url` + `status` 派生：`未提交 = status === 'pending' && !url`（与 `useRecordingList` 既有口径一致）；链接复用 `normalizeUrl`（补 `https://`）+ 复制按钮 + 新窗口打开。不展示帮众提交备注 `note`（保留在录屏审核页）。
- 日期格式与既有赛程列表一致；样式一律使用设计令牌（禁字面量色值）。
- 空态/加载态：各档案空态用 `EmptyState`；首载骨架沿用既有模式（`SkeletonTable`）。
- 若某组件实际超 300 行：按 recording 模式拆 `XxxMobileList.vue`（既有先例）。

### 6.3 跳转入口（stats-report-plan §6 小项）

- `StatsIdentityNotice.vue`：新增可选 prop `allowMemberLink`（默认 `false`）+ emit `view-member`；仅在 merged 分支且 `allowMemberLink && identity.member_id` 时显示「查看成员详情」按钮（成员详情页复用该组件时不传 prop → 不显示）。
- `MyStatsView.vue`：`:allow-member-link="auth.isAdmin"`（帮众隐藏——成员详情为管理员专属，避免 403/重定向）；点击 `router.push({ name: 'member-detail', params: { id } })`（引入 `useRouter`）。
- 后端零改动（`identity.member_id` 既有）。

### 6.4 UI 规范遵循

- 本项目 UI 任务遵循 finesse-ui skill 流程：register = product（管理后台，DENSITY 高、SPECTACLE 低）；实现前读取 `.finesse/log.json` 与 `ui-style-guide.md` 既有规范；交付前执行 cheapness blacklist 与 pre-flight 检查。
- 复用既有组件模式（桌面表格 + 移动卡片 + 分页）与设计令牌，不引入新视觉语言。

---

## 7. 文件清单（汇总）

**新增**：`backend/app/api/v1/member_archive.py`、`backend/app/services/member_archive_service.py`、`backend/app/schemas/member_archive.py`、`backend/tests/test_member_archive.py`、`frontend/src/types/memberArchive.ts`、`frontend/src/components/members/MemberAttendanceHistory.vue` / `MemberRecordingHistory.vue` / `MemberLineupHistory.vue` / `member-archive-shared.css`

**修改**：`backend/app/api/v1/router.py`、`frontend/src/api/members.ts`、`frontend/src/views/members/MemberDetailView.vue`、`frontend/src/components/my-stats/StatsIdentityNotice.vue`、`frontend/src/views/member/MyStatsView.vue`、`scripts/_pairs.py`（+3 组 PAIRS）

---

## 8. 测试与验证方案

### 8.1 后端 pytest（`backend/tests/test_member_archive.py`）

双向断言（该成员的都在、非该成员的不在）：

1. 出勤明细：正常/请假行齐全、`match_time` 倒序、补人行不出现
2. 录屏记录：含未提交行（`url=None`）；同场 `round_number` 升序
3. 排表历史：命中槽位；**陈旧 member_id 过滤**（删除成员且未重开该场排表的场景下不计入；新成员复用 id 不继承）
4. 改名场景：改名后三档案按 `member_id` 仍返回旧记录（历史行不变）
5. 隔离与权限：跨帮会 `member_id` → 404；帮众角色 → 403（参照 `tests/test_permissions.py` 既有模式）
6. 空数据返回 `[]`

### 8.2 前端验证（提示词与命令）

- 类型检查与构建：`vue-tsc` + `vite build` + `npm run lint`（vitest 由用户执行：`npm run test`）
- 手工清单（浏览器由用户执行）：4 Tab 切换与懒加载、录屏筛选（含未提交）、跳转按钮（管理员可见/帮众隐藏）、≤768px 卡片视图、空态、返回按钮

### 8.3 门禁与对账

- `scripts/_pairs.py` 新增 3 组 PAIRS（`check_type_drift` / `check_nullability` / `check_request_required` 共用）；可空性方向：`url` / `remark` / `review_remark` / `slot_remark` 后端可空 → 前端类型必须 `| null`（只把「后端可空 + 前端非空」视为失败，见 ai-checklist 第 110 条）
- `check_api_paths.py`（前端调用 ↔ 后端路由对账）自然覆盖新增端点
- `check_file_length.py` 新文件纳入全量扫描；`progress.md` 的 pytest 模块计数 30 → 31
- 全量复跑：`ruff check .`、`pytest`、行数门禁等（在**最后一次改动之后**，见 ai-checklist 第 28 条）

---

## 9. 文档联动清单（实施完成后）

| 文档 | 动作 |
|------|------|
| 本文件 | 状态更新为「已实施」+ 更新记录 |
| `design-document-v2.md` | §4.8.1 功能列表（三档案 Tab + 跳转）、§5.1 页面结构（成员详情） |
| `stats-report-plan.md` | §6「成员详情档案化」项标记已实施（引用本设计） |
| `backend/docs/README.md` / `frontend/docs/README.md` | 功能点 + 更新记录 |
| `progress.md` | 目录树 + 模块说明表（常驻库页面/常驻库 API）+ 更新记录 + tests 计数 |
| `architecture.md` | 更新记录（文档已在创建当日完成三处登记） |
| `CHANGELOG.md` | [Unreleased] 新增条目（使用者可见变更） |
| `ai-checklist.md` | 若出现新易错模式则补充 |

---

## 10. 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-10-12 | v1.0 草案创建：三项用户决策（Tab / 含未提交 / 全量）+ 数据口径核实（member_id 跨改名、F-78 保护、排表 JSON 双条件过滤与 D4 待评审）+ 接口 / 前后端实现 / 测试 / 文档联动设计 |
| 2026-10-12 | v1.1：D4 经用户评审**裁决不纳入**（排表历史原文不主动改写，成员删除路径零改动）——§2.2 改裁决记录、§3.3 改写为裁决 + 残余窗口登记、§5.1/§7 移除删除路径改动、§8.1 移除 D4 用例；§3.2 补充 id 复用本机实测依据 |
| 2026-10-12 | §3.2 的 id 复用实测明细收敛为引用（权威记录落位 `database-design.md` §1.3「主键与 ID 复用口径」，本文件只留摘要 + 引用） |
| 2026-10-12 | v1.2 实施交付：后端 3 端点（`api/v1/member_archive.py` + `services/member_archive_service.py` + `schemas/member_archive.py`，注册于 members 之前）+ 测试 `tests/test_member_archive.py`（9 用例：过滤/排序/改名可见/陈旧引用双条件过滤/跨帮会 404/帮众 403/接线/空数据）；前端 types + api 3 函数 + 三档案组件 + 共享样式 + MemberDetailView 档案 Tabs（lazy）+ StatsIdentityNotice/MyStatsView 跳转入口（仅管理员）；实现细化：分页口径对齐录屏 Tab（20/50/100 默认 20，替换原设计稿「10 条/页」）；验证：**pytest 276 passed + 89 subtests**、ruff check+format、前端 format:check / eslint / vue-tsc+vite build 全绿（vitest 与浏览器验收由用户执行），门禁（type-drift 19 对 / nullability / request-required / file-length 266 文件 / api-paths --strict）全过 |
