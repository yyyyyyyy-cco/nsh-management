# 帮会管理系统 - 数据库设计

> 版本：v1.8
> 更新日期：2026-09-15
> 依据：design-document-v2.md（产品设计 v2）、tech-stack.md（技术栈）

## 1. 设计总览

### 1.1 技术选型

| 项 | 选择 | 说明 |
|----|------|------|
| 数据库 | SQLite 3.x | 单文件存储，零配置 |
| ORM | SQLAlchemy 2.x | 异步支持，迁移方便 |
| 迁移工具 | Alembic | 表结构变更管理 |
| 数据库文件 | `data/nsh.db` | 由后端服务管理 |

### 1.2 表清单与关联关系

```
guilds（帮会）
 ├── users（账号）                    guild_id
 ├── profession_configs（职业配置）      guild_id
 ├── members（常驻库成员）              guild_id
 └── schedules（赛程）                guild_id
     ├── attendance_records（出勤记录）  schedule_id, member_id（可空）
     ├── lineups（排表）                schedule_id（1:1）
     ├── recordings（录屏）             schedule_id, member_id（可空）
     ├── match_data（比赛数据）          schedule_id
     └── squad_adjustments（分析调整）    schedule_id（1:1）
operation_logs（操作审计日志）          guild_id（可空）
```

| # | 表名 | 用途 | 关联 |
|---|------|------|------|
| 1 | guilds | 帮会 | users 多对一 |
| 2 | users | 登录账号（开发者/管理员/帮众） | guilds |
| 3 | profession_configs | 职业目标人数配置 | guilds |
| 4 | members | 常驻库成员 | guilds、attendance_records、recordings |
| 5 | schedules | 联赛赛程 | guilds、出勤/排表/录屏/分析/分析调整 |
| 6 | attendance_records | 单场出勤记录（含补人） | schedules、members |
| 7 | lineups | 排表（JSON 存储） | schedules（1:1） |
| 8 | recordings | 录屏提交与审核 | schedules、members |
| 9 | match_data | 比赛数据（CSV 导入） | schedules |
| 10 | squad_adjustments | 分析调整（小队分析内临时分配） | schedules（1:1） |
| 11 | operation_logs | 操作审计日志（写操作/异常落库，仅开发者可查） | guilds（guild_id 可空） |

### 1.3 设计决策

| 决策 | 方案 | 理由 |
|------|------|------|
| 多帮会支持 | 建 guilds 表；账号、成员、赛程、职业配置均按 guild_id 隔离 | v2 §6.7 账号管理支持“创建帮会，自动生成管理员账号和帮众账号” |
| 补人成员 | 出勤/录屏表存 `member_name` 快照，不关联 members | v2 §6.2 补人不录入常驻库、下场自动消失 |
| 排表存储 | 单条 JSON 存储 60 槽位 | 结构固定（10队×6人），JSON 便于前后端直接交换；实施计划已定 |
| 局数结果 | schedules.round_results 用 JSON | 局数 1-3 可变 |
| 比赛数据扩展列 | match_data.extra_data 用 JSON | v2 注明 CSV 格式样例待开发阶段提供，预留扩展 |
| 级联删除 | 应用层（Service）实现 | 实施计划已定，避免 DB 外键级联影响日志审计 |
| 登录限流 | users.failed_attempts + locked_until | 安全验收：5 次失败锁定 5 分钟 |
| 时间戳 | 所有表含 created_at；变更表含 updated_at | 出勤、录屏等含审核/更新语义 |

---

## 2. 数据表详细设计

### 2.1 guilds — 帮会表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| name | TEXT | NOT NULL, UNIQUE | 帮会名称 |
| created_at | DATETIME | NOT NULL, default now | 创建时间 |

### 2.2 users — 账号表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| guild_id | INTEGER | NULL, FK → guilds.id | 所属帮会（developer 角色可为 NULL） |
| username | TEXT | NOT NULL, UNIQUE | 登录名 |
| password_hash | TEXT | NOT NULL | bcrypt 哈希 |
| plain_password | TEXT | NULL | 明文密码（仅限本地管理工具查看，不对外暴露） |
| role | TEXT | NOT NULL, default 'member' | `developer` 开发者 / `admin` 管理员 / `member` 帮众 |
| status | TEXT | NOT NULL, default 'active' | `active` 启用 / `disabled` 禁用 |
| failed_attempts | INTEGER | NOT NULL, default 0 | 连续登录失败次数 |
| locked_until | DATETIME | NULL | 锁定截止时间（限流） |
| created_at | DATETIME | NOT NULL, default now | 创建时间 |

索引：`guild_id`。
关系属性：`guild`（joined 加载），`guild_name`（只读 property，返回 guild.name 或 None）。
角色说明：developer 不绑定帮会（guild_id=NULL），可创建帮会、派发账号、删除帮会；admin 绑定帮会，管理本帮会全部功能；member 绑定帮会，有限查看权限。

### 2.3 profession_configs — 职业配置表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| guild_id | INTEGER | NOT NULL, FK → guilds.id | 所属帮会 |
| profession | TEXT | NOT NULL | 职业名（11种：铁衣、血河、沧澜、龙吟、潮光、玄机、碎梦、神相、九灵、鸿音、素问） |
| target_count | INTEGER | NOT NULL, default 0 | 目标人数（用于出勤库职业缺口分析） |
| remark | TEXT | NULL, max 255 | 职业说明（可编辑，默认空） |

唯一约束：`(guild_id, profession)`。

### 2.4 members — 常驻库成员表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| guild_id | INTEGER | NOT NULL, FK → guilds.id | 所属帮会 |
| name | TEXT | NOT NULL | 姓名 |
| main_profession | TEXT | NOT NULL | 主职业 |
| sub_profession | TEXT | NULL | 副职业（可选） |
| status | TEXT | NOT NULL, default 'formal' | `formal` 正式 / `substitute` 替补 |
| remark | TEXT | NULL | 备注 |
| created_at | DATETIME | NOT NULL, default now | 创建时间 |

索引：`guild_id`、`name`、`main_profession`、`status`。
业务约束：同一帮会内重名跳过导入（Excel 导入时校验 `name` 重复，不强制 UNIQUE，便于历史数据容错）。

### 2.5 schedules — 赛程表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| guild_id | INTEGER | NOT NULL, FK → guilds.id | 所属帮会 |
| opponent | TEXT | NOT NULL | 对手 |
| match_time | DATETIME | NOT NULL | 比赛时间 |
| location | TEXT | NULL | 地点 |
| rounds | INTEGER | NOT NULL, CHECK 1-3 | 局数（创建后不可修改） |
| result | TEXT | NOT NULL, default 'pending' | `win` / `lose` / `draw` / `pending` |
| round_results | TEXT (JSON) | NULL | 每局结果，如 `["win","lose","pending"]` |
| created_at | DATETIME | NOT NULL, default now | 创建时间 |

索引：`guild_id`、`match_time`。
业务规则：删除赛程时由 Service 级联删除 attendance_records、lineups、recordings、match_data、squad_adjustments。

### 2.6 attendance_records — 出勤记录表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| schedule_id | INTEGER | NOT NULL, FK → schedules.id | 所属赛程 |
| member_id | INTEGER | NULL, FK → members.id | 常驻成员；补人为 NULL |
| member_name | TEXT | NOT NULL | 姓名快照（补人必须，正式/替补冗余存储便于展示） |
| profession | TEXT | NOT NULL | 职业快照 |
| status | TEXT | NOT NULL, default 'normal' | `normal` 正常 / `leave` 请假 |
| is_filler | BOOLEAN | NOT NULL, default 0 | 是否补人 |
| created_at | DATETIME | NOT NULL, default now | 创建时间 |

索引：`schedule_id`、`member_id`。
唯一约束：`(schedule_id, member_id)`（常驻成员每场一条）；`(schedule_id, member_name, is_filler=1)`（补人按姓名每场一条，SQLite 通过部分唯一索引实现）。
业务规则：正常状态人数上限 60 人（应用层校验）；补人下次比赛自动消失（按赛程独立存储天然满足）。

### 2.7 lineups — 排表表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| schedule_id | INTEGER | NOT NULL, FK → schedules.id, UNIQUE | 所属赛程（1:1） |
| data | TEXT (JSON) | NOT NULL | 排表数据（60 槽位） |
| title_remark | TEXT | NULL, max 255 | 标题备注（排表页面顶部显示） |
| groups_remark | TEXT (JSON) | NULL | 各组备注（如 `{"进攻1": "主攻", "防守1": "坚守"}`） |
| updated_at | DATETIME | NOT NULL, default now | 最后更新时间 |

JSON 结构示例：

```json
[
  {
    "category": "进攻1",
    "team_index": 0,
    "slots": [
      { "slot_index": 0, "member_id": 1, "member_name": "张三", "remark": "主T" },
      { "slot_index": 1, "member_id": null, "member_name": "", "remark": "" }
    ]
  }
]
```

共 10 个 team（进攻1×3、进攻2×3、防守1×2、防守2×2），每队 6 个 slot，合计 60 槽位。

### 2.8 recordings — 录屏表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| schedule_id | INTEGER | NOT NULL, FK → schedules.id | 所属赛程 |
| member_id | INTEGER | NULL, FK → members.id | 常驻成员；补人为 NULL |
| member_name | TEXT | NOT NULL | 姓名快照 |
| round_number | INTEGER | NOT NULL, CHECK 1-3 | 第几局 |
| url | TEXT | NULL | 录屏链接（提交前为空） |
| status | TEXT | NOT NULL, default 'pending' | `pending` 待审核 / `approved` 已通过 / `rejected` 已驳回 |
| review_remark | TEXT | NULL | 审核备注 |
| reviewed_at | DATETIME | NULL | 审核时间 |
| created_at | DATETIME | NOT NULL, default now | 提交时间 |

索引：`schedule_id`、`status`。
唯一约束：`(schedule_id, member_id, round_number)`；补人按 `(schedule_id, member_name, round_number)`。
业务规则：创建赛程时按局数批量初始化录屏占位记录（每人每局一条）；URL 校验支持 B站、YouTube 等。

### 2.9 match_data — 比赛数据表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| schedule_id | INTEGER | NOT NULL, FK → schedules.id | 所属赛程 |
| player_name | TEXT | NOT NULL | 玩家名字 |
| profession | TEXT | NULL | 职业 |
| camp | TEXT | NOT NULL | 阵营（CSV 区块标题，第一块为己方） |
| kills | INTEGER | NOT NULL, default 0 | 击败数（击败+清泉合计，见 §3.5） |
| springs | INTEGER | NOT NULL, default 0 | 清泉数（原始分量，仅供追溯） |
| assists | INTEGER | NOT NULL, default 0 | 助攻 |
| resource | INTEGER | NOT NULL, default 0 | 资源 |
| player_damage | INTEGER | NOT NULL, default 0 | 对玩家伤害 |
| armor_break_damage | INTEGER | NOT NULL, default 0 | 人伤卸甲 |
| building_damage | INTEGER | NOT NULL, default 0 | 对建筑伤害 |
| tower_break_damage | INTEGER | NOT NULL, default 0 | 破塔卸甲 |
| healing | INTEGER | NOT NULL, default 0 | 治疗值 |
| damage_taken | INTEGER | NOT NULL, default 0 | 承受伤害 |
| deaths | INTEGER | NOT NULL, default 0 | 重伤（死亡数） |
| revives | INTEGER | NOT NULL, default 0 | 复活/清泉（单值） |
| fen_gu | INTEGER | NOT NULL, default 0 | 焚骨（独立统计项，独立“焚骨榜”展示，不并入 kills） |
| extra_data | TEXT (JSON) | NULL | 预留：后续 CSV 新增列 |
| created_at | DATETIME | NOT NULL, default now | 导入时间 |

索引：`schedule_id`。
业务规则：CSV 导入 5MB 上限；一局一表，重新导入同局数据即覆盖该局全部记录（不保留历史）；列映射与解析见 §3.5。

### 2.10 squad_adjustments — 分析调整表

> 小队分析 Tab 内，管理员手动将"未排表成员"分配到指定队伍的临时数据。与正式排表（lineups）完全独立，修改仅作用于小队分析视图。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| schedule_id | INTEGER | NOT NULL, UNIQUE, FK → schedules.id | 所属赛程（1:1） |
| data | TEXT (JSON) | NOT NULL, default `{}` | 分配方案 `{player_name: "category:team_index"}` |
| updated_at | DATETIME | NOT NULL, default now, onupdate now | 最后更新时间 |

索引：`schedule_id`（UNIQUE）。
业务规则：每赛程最多一条记录；保存时覆盖式替换 `data` 字段；仅管理员可写，帮众可读。

### 2.11 operation_logs — 操作审计日志表

> 审计中间件（`main.py`）自动落库：所有写操作（POST/PUT/DELETE/PATCH）与 5xx 错误自动记录，登录成功/失败手动埋点；`detail` 为 JSON 文本，敏感字段（password/token 等）已脱敏。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| user_id | INTEGER | NULL | 操作账号 ID（匿名请求为空） |
| username | STRING(64) | NULL, index | 操作账号名 |
| role | STRING(16) | NULL | 角色（developer/admin/member） |
| guild_id | INTEGER | NULL, index | 所属帮会（开发者全局操作为空） |
| module | STRING(32) | NOT NULL, index | 业务模块（member/schedule/login/…/other） |
| action | STRING(32) | NOT NULL | 操作类型（create/update/delete/login/…/other） |
| method | STRING(8) | NOT NULL | HTTP 方法 |
| path | STRING(255) | NOT NULL | 请求路径 |
| status_code | INTEGER | NULL | 响应状态码（异常中断时为空） |
| level | STRING(16) | NOT NULL, index | info / warning / error |
| detail | TEXT | NULL | JSON 文本（敏感字段已脱敏） |
| ip | STRING(64) | NULL | 客户端 IP |
| created_at | DATETIME | NOT NULL, default now, index | 记录时间（UTC） |

索引：`username`、`guild_id`、`module`、`level`、`created_at`。
业务规则：默认保留 90 天（启动时自动清理过期记录，页面亦可手动清理，清理操作本身会被审计）；仅开发者可在「系统日志」页查看。

---

## 3. 关键业务规则落表方案

### 3.1 出勤率计算

```
出勤率 = 正常次数 / (正常次数 + 请假次数) × 100%
```

- 按 `members.id` 聚合 attendance_records（排除补人）
- 仅统计该成员被导入出勤表的场次，未被导入不计入
- 中途加入的成员，之前赛程无记录，天然不计为缺勤
- 低于 50% 前端标红预警

### 3.2 级联删除

删除赛程时按顺序删除：recordings → match_data → squad_adjustments → attendance_records → lineups → schedules（Service 层事务内完成）。

### 3.3 登录限流

- 登录失败：`failed_attempts + 1`；达到 5 次设置 `locked_until = now + 5分钟`
- 登录成功或锁定到期：重置 `failed_attempts = 0`、`locked_until = NULL`

### 3.4 录屏按局数初始化

创建赛程（rounds=N）时，为候选池成员批量生成 N 条录屏占位记录（status=pending），补人由出勤库确定后补充。

### 3.5 CSV 导入解析（依据真实样例）

样例文件：`.agent/docs/20260630_21037_横戈_仗剑.csv`（127 行）

- 一个 CSV 含多个阵营区块，每块结构：`"阵营名","人数"` 标题行 → 表头行 → N 条数据行
- 第一个区块为己方阵营，其余为对手阵营；区块标题“人数”用于完整性校验（60）
- 表头 14 列：玩家名字、职业、击败/清泉、助攻、资源、对玩家伤害、人伤卸甲、对建筑伤害、破塔卸甲、治疗值、承受伤害、重伤、复活/清泉、焚骨
- “击败/清泉”值形如 `" 15/3"`（前导空格需 strip）：斜杠前=击败，斜杠后=清泉；**击败数 kills = 击败 + 清泉**（清泉计入击败），springs 字段保留清泉原始分量仅供追溯
- “复活/清泉”列为单值（如 `"0"`、`"17"`），直接存 revives

### 3.6 帮众操作归属（共享账号）

帮众使用共享账号登录后，无需选择/输入身份：录屏列表按姓名展示全部人员（含补人），帮众找到自己的姓名所在行提交录屏链接（链接对帮众脱敏展示）。出勤库与排表 Tab 当前仅管理员可见，出勤状态由管理员维护。系统不绑定“当前操作者”，归属由行本身确定。

---

## 4. 更新记录

| 日期 | 更新内容 |
|------|---------|
| 2026-08-05 | 初始化数据库设计 v1.0，依据 design-document-v2.md |
| 2026-08-05 | v1.1：多帮会隔离（guild_id）、出勤率公式修正、match_data 按真实 CSV 样例重设计、补充帮众操作归属说明 |
| 2026-08-05 | v1.2：击败数修正为击败+清泉合计，springs 保留原始分量供追溯 |
| 2026-08-05 | v1.3：确认重伤=死亡数、复活/清泉为单值、焚骨为独立榜单统计项 |
| 2026-08-11 | v1.4：术语”客人”统一改为”补人”（is_guest → is_filler，含 Alembic 迁移） |
| 2026-08-17 | v1.5a：profession_configs 新增 remark 字段（职业说明，可编辑，Alembic 迁移 a1b2c3d4e5f6） |
| 2026-08-18 | v1.5b：users 表 guild_id 允许 NULL（developer 角色不绑定帮会）、新增 plain_password 字段（明文密码，仅本地管理工具查看）、role 新增 developer 选项（Alembic 迁移 e5f6a7b8c9d0） |
| 2026-08-18 | v1.5c：lineups 表新增 title_remark（标题备注）、groups_remark（各组备注 JSON）字段（Alembic 迁移 dbb752d924fe） |
| 2026-08-26 | v1.6：修正 match_data 导入业务规则为按局覆盖（一局一表，重导覆盖该局数据），与实现一致 |
| 2026-08-26 | v1.6：新增 squad_adjustments 表（分析调整，小队分析内临时分配，1:1 关联赛程，Alembic 迁移 i3j4k5l6m7n8）；表清单从 9 张更新为 10 张；级联删除规则补充 squad_adjustments |
| 2026-09-15 | v1.7：术语统一（客人→补人）；CSV 样例引用路径更正为 `.agent/docs`（.claude→.agent 改名）；§3.6 帮众操作归属校正（出勤/排表 Tab 仅管理员，帮众经录屏列表归属） |
| 2026-09-15 | v1.8：补全 operation_logs 操作审计日志表（§1.2 表清单 + §2.11 字段级设计），表数 10 张更新为 11 张 |
