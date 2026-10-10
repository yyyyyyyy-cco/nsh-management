# 职业目录动态化（方案 B）开发计划

> 分支：`profession` ｜ 前置决策（已确认）：**全局目录、开发者维护**；可编辑属性 = **名称 + 排序 + 颜色 + 启停**
> 状态：**待实施**（规划完成，编码未开始；实施后进度由 `progress.md` 记录）
> 规划日期：2026-10-10 ｜ 登记：实施启动时补 `AGENTS.md` §2.2 一行

## 0. 设计基线与总原则

- **数据库为职业清单唯一权威源**：后端不再有 `PROFESSIONS` 常量；前端不再有 `PROFESSIONS / PROF_ORDER / PROF_COLORS` 硬编码。
- **前端单点分发**：所有组件经 `useProfessionStore()`（列表/排序）与 `utils/profession.ts`（响应式色彩缓存）取数，禁止任何组件自行维护职业清单。
- **停用代替物理删除**：历史快照（出勤/排片/录屏/比赛数据的 `profession` 字符串）永不改写；不提供 DELETE 接口。
- **旧值豁免（存量可编辑）**：任何"变更新值"必须为启用职业；"保持不变的值"允许为停用职业，保证存量成员/记录可继续编辑其他字段。
- **明确排除项**（本计划不做）：评分权重表（`PROFESSION_WEIGHTS`）、坦克/辅助分类特判（`TANK_PROFESSIONS`、`铁衣`判定）保持代码内硬编码，新职业走既有兜底（击杀/人伤各半、非坦克非辅助）；改名不级联历史快照；不做实时推送。

## 1. 架构总览

```
professions 表（全局，无 guild_id；迁移种子 = 现有 11 职业）
   │ GET /professions（全角色，返回全量含停用）
   ▼
Pinia store（activeList 过滤 + 排序）──► 下拉/筛选/排表/配置弹窗/职业分布
   │ setProfessionColors(全量 name→color)
   ▼
utils/profession.ts（reactive PROF_COLORS 缓存；亮度 0.35 定文字色）
   └─ profColor/profTagStyle/profFillStyle 签名不变 → ~20 处调用点零改动
写操作：POST/PUT /professions（require_developer）→ 开发者「系统配置 → 职业目录」Tab
```

## 2. 数据层

### 2.1 模型（修改 `backend/app/models/profession.py`）

同文件新增第二个类（`check_schema_drift.parse_models` 支持单文件多表），模块 docstring 更新为"职业目录表 + 职业配置表"：

`class Profession(Base)` — `__tablename__ = "professions"`：

| 字段 | 定义 |
|---|---|
| id | `Mapped[int]` primary_key, autoincrement |
| name | `Mapped[str]` String(16), nullable=False, **unique=True, index=True** |
| sort_order | `Mapped[int]` Integer, nullable=False, default=0 |
| color | `Mapped[str]` String(9), nullable=False, default="#c9a13b"（`#RRGGBB`） |
| is_active | `Mapped[bool]` Boolean, nullable=False, default=True |
| created_at | `Mapped[datetime]` DateTime(timezone=True), default now(UTC), nullable=False（照 `member.py` 写法） |

同步 `backend/app/models/__init__.py`：导入 `Profession` + 加入 `__all__`。

### 2.2 Alembic 迁移（新建 `backend/alembic/versions/q1r2s3t4u5v6_add_professions.py`）

- `revision="q1r2s3t4u5v6"`，`down_revision="p0q1r2s3t4u5"`（当前 head）。
- `upgrade()`：`op.create_table("professions", ...)`（列与模型逐列一致）+ 唯一索引；随后**种子 11 行**（`op.execute` INSERT，迁移**自包含、禁止 import app 代码**）：
  - sort_order 按现 `PROF_ORDER`：铁衣1 素问2 神相3 碎梦4 血河5 玄机6 九灵7 潮光8 龙吟9 鸿音10 沧澜11；
  - color 取现 `PROF_COLORS` **原样大小写字符串**（`#ffc800`、`#FF9CF2`、`#3E6BF4`、`#00FFFB`、`#F04545`、`#f6ff00`、`#8B5CF6`、`#4F95FF`、`#3fe155`、`#C6834D`、`#605EF0`）；
  - `is_active = 1`。
- `downgrade()`：`op.drop_table("professions")`。
- 迁移头注释按项目风格写"背景 + 种子来源（ui-style-guide §7 / 旧 PROFESSIONS 常量）"。

## 3. 后端改造

### 3.1 新服务 `backend/app/services/profession_service.py`（新建）

异常**沿用 `ConfigServiceError`**（先例：`guild_service` 由 config 域拆出时即沿用，`main.py` 已有全局处理器，无需新增 handler）。核心函数：

- `list_professions(session, include_inactive=True) -> list[Profession]`：按 `(sort_order, id)` 排序。
- `active_names(session) -> set[str]` / `known_names(session) -> set[str]`（供各消费点校验）。
- `ensure_active(session, name, *, grandfathered: set[str] | None = None)`：不通过则 `ConfigServiceError(f"无效的职业：{name}（不存在或已停用）")`；`grandfathered` 命中时放行（旧值豁免）。
- `create_profession(session, data) -> Profession`：name 去空白、查重（含停用）；`sort_order` 缺省 = max+1；color 默认 `#c9a13b`。
- `update_profession(session, profession_id, data) -> Profession`：
  - `sort_order` / `color` / `is_active` 直接更新；
  - **停用守卫**：`is_active=False` 且该职业是当前唯一启用 → 400"至少保留一个启用职业"；
  - **改名级联（单事务，见 §3.5）**。

### 3.2 现有消费点逐一改造（含豁免规则）

| 文件 | 现状 | 改法 |
|---|---|---|
| `backend/app/utils/constants.py` | `PROFESSIONS` 常量 | **删除**；保留 `MAX_PROFESSION_TARGET`（注释更新） |
| `member_service.validate_profession` | 同步比对常量 | 改 `async`，接 `session`；`create_member` → 仅启用；`update_member`（L172 处）→ 提供值须 (启用) 或 (== 该成员现值才算未变更) |
| `attendance_service.add_filler` | 比对常量 | 仅启用 |
| `attendance_service.update_record_profession` | 比对常量 + 成员允许集 | 新值须 ∈ 成员主/副集合 且 (启用 或 == 记录现值) |
| `schedule_service.update_profession_config` | 键 ∈ 常量 | 键须 (启用 或 ∈ 该赛程既有 override 键)；0–60 界不变 |
| `config_service.get_profession_configs` | 用常量补全 + 按名排序 | 仅取**启用**目录：过滤既有行至启用集 → 缺者补默认 → 按目录 `sort_order` 排序 |
| `config_service.update/batch_update` | 键 ∈ 常量 | 键须 ∈ 启用集（既有"缺失行跳过"语义保留） |
| `guild_service.create_guild` | 按常量初始化配置行 | 按**启用目录**初始化 |
| `excel_import` | 比对常量 | 比对启用集；错误文案改 `{name}：无效职业「{prof}」（不存在或已停用）` |
| `excel_export._group_members / build_members_xlsx` | 按常量排序 | 函数加可选参 `profession_order: list[str] | None = None`；None → `sorted(buckets)` 兜底；**既有 7 处调用（3 测试 + 4 自检）保持位置参数兼容，零改动** |
| `api/v1/members.py`（导出端点 L136） | 直接调用 | 先 `profession_service.list_professions`（含停用，保持原位次），把名称列表作第 4 参数传入 `asyncio.to_thread`（+约 4 行；该文件已在行数豁免清单，余量充足） |
| 图片导出（image_export）、录屏快照、比赛数据 CSV、`match_data_stats` | 不依赖常量 | **不改**（明确维持） |

### 3.3 新接口（新建 `backend/app/api/v1/professions.py`，路由 ≤150 行）

`router = APIRouter(prefix="/professions", tags=["职业目录"])`：

| 方法/路径 | 守卫 | 行为 |
|---|---|---|
| `GET ""` | `get_current_user` | 返回**全量**（含停用）`list[ProfessionOut]`，按 `(sort_order, id)` |
| `POST ""`（201） | `require_developer` | 创建，返回 `ProfessionOut` |
| `PUT "/{profession_id}"` | `require_developer` | 局部更新（name/color/sort_order/is_active），返回 `ProfessionOut` |

- `backend/app/api/v1/router.py`：import + `include_router`（与既有清单风格一致）。
- 停用即 `PUT {"is_active": false}`；无 DELETE 端点。

### 3.4 Schemas（新建 `backend/app/schemas/profession.py`）

- `ProfessionOut`：id/name/sort_order/color/is_active/created_at(UtcDatetime)，`from_attributes`。
- `ProfessionCreate`：name `Field(..., min_length=1, max_length=16)`；color `Field("#c9a13b", pattern=r"^#[0-9a-fA-F]{6}$")`；sort_order `int | None = Field(None, ge=0)`。
- `ProfessionUpdate`：name/color/sort_order/is_active **全可选**（`*Update 类全可选` 与 PAIRS_REQ 约定一致）。
- name 去空白逻辑放服务层（用 `field_validator` 或服务 `strip()`；实现时与既有 schema 风格统一）。

### 3.5 改名级联（单事务，仅活跃数据）

1. 目录内查重（新旧名不得冲突，含停用行）→ 409/400；
2. 预查冲突：任一帮会 `profession_configs` 已存在新名行 → 400"目标职业名已被职业配置使用"；
3. 级联 SQL：`members.main_profession`、`members.sub_profession`、`profession_configs.profession` 三处 UPDATE；
4. `schedules.profession_config`（JSON）：查出非空行，Python 侧逐条替换键后写回；
5. **不触碰** `attendance_records / recordings / match_data` 快照（历史语义，测试锁定该行为）；
6. 单次 `commit()`；路由/服务错误走既有 `ConfigServiceError` 全局处理。

## 4. 前端改造

### 4.1 类型与接口（新建）

- `frontend/src/types/profession.ts`：
  - `ProfessionOut { id: number; name: string; sort_order: number; color: string; is_active: boolean; created_at: string }`
  - `ProfessionCreateRequest { name: string; color?: string; sort_order?: number }`
  - `ProfessionUpdateRequest { name?: string | null; color?: string | null; sort_order?: number | null; is_active?: boolean | null }`
  - **可空性口径**：与 Pydantic 对齐（后端可空字段前端用 `?` 或 `| null`），确保 `check_nullability / check_request_required` 零告警。
- `frontend/src/api/professions.ts`：`getProfessions()`（GET `/professions`）、`createProfession()`（POST）、`updateProfession(id, data)`（PUT）。
- `scripts/_pairs.py` 登记：`PAIRS["ProfessionOut"] = ["ProfessionOut"]`；`PAIRS_REQ["ProfessionCreateRequest"] = ["ProfessionCreate"]`、`["ProfessionUpdateRequest"] = ["ProfessionUpdate"]`。

### 4.2 新 store（新建 `frontend/src/stores/profession.ts`，约 90 行）

- state：`list: ProfessionOut[]`、`loaded`、`loading`。
- getters：`activeList`（`is_active` 过滤 + `(sort_order, id)` 排序）、`activeNames: string[]`、`orderIndex(): Map<string, number>`（activeNames 序号；未知 → Infinity）。
- actions：`load()`（GET → 写 state → **`setProfessionColors(全量 name→color)`**）、`ensureLoaded()`（`loaded` 后短路）、`refresh()`（变更后强制重拉）。
- 加载失败：静默（http 拦截器已提示），`loaded` 保持 false，下次导航重试。

### 4.3 工具函数改造（修改 `frontend/src/utils/profession.ts`）

- `export const PROF_COLORS = reactive<Record<string, string>>({})` —— **保持导出名与对象身份**（`analysis.ts` 再导出、`ANALYSIS_COLORS === PROF_COLORS` 断言不破）。
- 新增 `setProfessionColors(next: Record<string, string>)`：原地 `Object.assign` + 删除多余键（保持响应式追踪；组件模板/计算属性中调用 `profColor` 即自动重渲染）。
- 文字对比色：删除 `DARK_PROF_COLORS` 硬编码，改为 **WCAG 相对亮度**计算：`lum > 0.35 → '#333'，否则 '#fff'`。
  - 已逐色演算验证：11 个规范色（深字最小 lum=0.555 龙吟；白字最大 lum=0.288 鸿音）与两级兜底（胶囊灰底 → `#333`、全底色金 `#c9a13b` → `#333`）**全部与现行规范一致**；阈值 0.35 写入代码注释与单测锁定。
- `profColor / profTagStyle / profFillStyle` **签名不变**（~20 处调用点零改动，含 `ProfessionTab.vue / professionDetailCharts.ts / analysis.ts` 的 `PROF_COLORS[p] || '#999'` 直取用法）。

### 4.4 列表消费点迁移（共 10 个文件）

统一替换为 store：`const professionStore = useProfessionStore()`（均处于 setup 上下文）：

| 文件 | 现引用 | 改为 |
|---|---|---|
| `components/members/MemberFormDialog.vue` | `PROFESSIONS` | `professionStore.activeNames`（编辑态：现值若不在列表 → 追加"（已停用）"标注选项，value 保持原字符串） |
| `components/members/MemberToolbar.vue` | `PROFESSIONS` | `activeNames` |
| `components/attendance/FillerDialog.vue` | `PROFESSIONS` | `activeNames` |
| `components/attendance/AttendanceToolbar.vue` | `PROF_ORDER` | `activeNames` |
| `components/attendance/ProfessionConfigDialog.vue` | `PROF_ORDER`（template L17 + initForm L66） | `activeNames` |
| `components/lineups/LineupOverviewPanel.vue` | `PROF_ORDER` | `activeNames` |
| `composables/useAttendanceList.ts` | `PROF_ORDER`（缺口 chips L94） | `activeNames` |
| `composables/lineupBoard.ts` | `@/utils/constants` 的 `PROF_ORDER`（L8/L36 转出 + L241 排序） | store `orderIndex`（未知 → 末尾；修掉旧 `indexOf=-1` 排最前行为）；删除 L36 转出 |
| `utils/constants.ts` | `PROFESSIONS / PROF_ORDER` | **删除两常量**（保留状态/结果常量） |
| `utils/profession.ts` | 静态色表 | §4.3 改造 |

### 4.5 开发者 UI（系统配置）

- `views/config/ConfigView.vue`：developer 可见新增 Tab「**职业目录**」（与「账号管理」并列，`v-if="auth.isDeveloper"`；默认 activeTab 仍为 account）。
- 新建 `views/config/ConfigProfessionCatalogPanel.vue`（≤300 行）：
  - 顶部新增表单：名称输入 + `el-color-picker`（默认 `#c9a13b`）+ 排序 `el-input-number`（可空=自动末位）+「新增」按钮；
  - 表格：职业名（编辑 → `ElMessageBox` 确认"重命名将同步更新成员/职业配置/单场覆盖，历史记录不变"）、颜色（picker 变更即 PUT）、排序（变更即 PUT）、启用（`el-switch`；关闭时二次确认"停用后新数据不可选，历史数据保留"）；
  - 每次写操作成功后 `professionStore.refresh()` 并 `ElMessage` 提示；
  - 视觉完全复用现有 Config 面板范式（`el-card` + 表格 + 雅金按钮），不引入新视觉语言；移动端按 `ConfigProfessionPanel` 的行列表模式做简版适配（接收 `isMobile` prop）。
- 管理员「职业配置」面板**零改动**（数据源自动变为启用目录并按目录序排列）。

### 4.6 全局加载时机（修改 `frontend/src/router/index.ts`）

`router.beforeEach` 在既有鉴权逻辑后追加：`await useProfessionStore().ensureLoaded()`（包 try/catch，失败不阻塞导航；仅首次真实发请求）。

## 5. 测试计划

### 5.1 后端

- `backend/tests/support.py`：新增 `PROFESSION_SEED`（11 元组，与迁移种子逐字段一致）+ `seed_professions()`；`DbTestCase.asyncSetUp` 默认调用（既有服务级用例零改保持绿）。
- `backend/tests/test_profession_config_rules.py`：删除 `PROFESSIONS` 常量导入（L26/L29），改用种子名。
- **新建 `backend/tests/test_profession_catalog_rules.py`**（服务级 + 端点权限矩阵，参照既有用例风格）：
  1. 创建：成功/重名（含停用重名）拒绝/color 格式/排序缺省 = max+1；
  2. 停用：最后一个启用职业拒绝；停用后 `ensure_active` 拒绝、旧值豁免放行；
  3. 改名级联：members（主/副）、profession_configs、schedules override 键全部更新；attendance/recordings/match_data 快照**不变**（锁定行为）；目标名冲突拒绝；
  4. 消费点豁免：成员更新（不改职业可保存）、出勤记录（=记录现值放行、换成停用拒绝）、单场覆盖（既有键放行）；
  5. Excel 导入：停用职业行计入 errors 跳过；
  6. 端点：member 调 PUT → 403；GET 返回含停用全量；developer PUT 生效。
- `backend/scripts/selfcheck_security_fixes.py`：其内建库需补目录种子（有 API POST /members）；实施时逐个自检脚本核对是否触达校验路径（已知 `selfcheck_member_exports.py` 调用签名兼容、无需改）。

### 5.2 前端（修改既有 3 个 spec + 新建 1 个；**遵循约定不由助手执行 vitest，仅告知命令**）

- `utils/profession.spec.ts`：改为"先 `setProfessionColors(SEED)` 再断言"；新增亮度规则用例（11 色映射 + 灰/金兜底 + 边界）；删除 `Object.keys(PROF_COLORS).toHaveLength(11)` 静态断言。
- `utils/professionSource.spec.ts`：保留 GUIDE 11 色表（作为**规范↔种子**锁定）+ `TANK_PROFESSIONS` 断言；删除"与后端常量顺序一致"；新增"store 水合驱动 profColor"与"排序纯函数"用例。
- `utils/constants.spec.ts`：移除 `PROFESSIONS` 相关两断言。
- 新建 `stores/profession.spec.ts`：mock `@/api/professions` —— active 过滤、排序、色彩水合（含停用色保留）、失败不置 loaded。

## 6. 文档同步清单（AGENTS §3.3 全覆盖）

> 说明：本清单刻意使用"表数 12→13 / 迁移数 16→17 / 版本 1.10→1.11"等**箭头式表述**而非"N 张表""N 个迁移"字面量——`check_doc_numbers.py` 会扫描 `.agent/plans/*.md`，字面量会在实施前后两个阶段各触发一次误报（同理适用于下表对合规计划的改写要求）。

| 文档 | 精确改动 |
|---|---|
| `memory-bank/database-design.md` | 头部版本号 1.10→1.11；§1.2 树 + 清单表新增第 13 行 `professions`；§2.3 L107 职业名说明改"取值见 §2.13 职业目录"；**新增 §2.13 professions**（字段表 6 列与迁移逐列一致；唯一约束/说明作正文行）；注明"职业清单权威源自 2026-10 起为本表（全局）"；更新记录追加 1.11 行 |
| `memory-bank/design-document-v2.md` | §2 摘要 L37 职业色行；§3.2 矩阵：**新增行「职业目录管理」开发者✅/管理员❌/帮众❌、「职业目录读取」✅✅✅**；顺带修正既有「职业配置」行（写操作实为管理员专属，developer 无帮会被服务层拒）并备注；§4.1 L126–127「职业列表（11种）」改为"由职业目录维护（初始内置 11 种，开发者在系统配置中增删/排序/配色/停用）"；更新记录 + 版本行 |
| `memory-bank/ui-style-guide.md` | §7 标题「（不变）」→「（初始内置色板；以职业目录数据为准）」；表后补一行说明：文字色按相对亮度自动对比（阈值 0.35）；新职业颜色由开发者在职业目录设定 |
| `AGENTS.md` | L47 表数声明 12→13；§2.2 增补本计划文档登记行 |
| `memory-bank/progress.md` | L11 树行表数 12→13 + 注释含 professions；L92 版本引用 1.10→1.11；L159 表数 12→13、迁移数 16→17；模块表补职业目录模块（后端 service/api/前端 store/panel）；更新记录 2–3 行（后端实施 / 前端实施 / 文档同步） |
| `memory-bank/architecture.md` | 更新记录 1 行（本轮文档变更 + 关联 database-design 新版本） |
| `memory-bank/ai-context.md` | L53、L103 表数声明 12→13（L53 标题同步） |
| `backend/docs/README.md` | L12/L25/L43 版本引用 1.10→1.11；L59 表数 12→13、迁移数 16→17；L134 表数 12→13；功能清单/接口清单补 professions；更新记录行 |
| `frontend/docs/README.md` | L36 系统配置描述补「职业目录（开发者）」；勾选清单加一条功能点 |
| `README.md` | L18 系统配置功能行补「职业目录（开发者专属）」 |
| `CHANGELOG.md` | `[Unreleased]` 新增「### 新增」：职业目录动态化（开发者可增删/停用/排序/配色，全站即时生效） |
| `memory-bank/ai-checklist.md` | 新增条目：①职业清单权威源已迁至 DB，禁止重新引入前端硬编码清单（否则触发 professionSource 测试与半适配）；②迁移种子必须自包含（不 import app 常量） |
| `.agent/plans/compliance-remediation-plan.md` | L378/L501/L502/L820 的表数声明（12）随本轮改为 13，并改写为**不触发数字声明的措辞**（如箭头式表述）——实施时以 `check_doc_numbers.py` 实际输出为准逐条清零 |
| 其他（GIT-GUIDE / DEPLOY 等） | 以 `check_stale_paths` / `check_doc_refs` 输出为准补缺 |

## 7. 实施步骤（顺序 + 依赖）

| # | 步骤 | 依赖 | 验证 |
|---|---|---|---|
| 1 | 数据层：模型 + 迁移（含种子）+ `__init__` 注册 | — | `alembic upgrade head`（临时库）；`check_schema_drift` / `check_schema_vs_db` 双绿 |
| 2 | 后端服务：`profession_service` + §3.2 全部消费点改造 | 1 | `pytest`（种子就绪前允许红，随 3 修正） |
| 3 | 新接口 + schemas + router 注册 | 2 | 手工 `GET/POST/PUT` + `check_api_paths`（前端调用后） |
| 4 | 后端测试：`support.py` 种子 + 既有用例修正 + 新用例 | 2,3 | `pytest` 全绿；`ruff check .`；`python -m mypy app`（报告型） |
| 5 | 前端核心：`types/profession.ts`、`api/professions.ts`、`stores/profession.ts`、`utils/profession.ts`、`utils/constants.ts` 清理、router 守卫、`_pairs.py` 登记 | 3 | `vue-tsc --noEmit`；`check_type_drift` 自检 |
| 6 | 前端消费点迁移（§4.4 十文件） | 5 | 类型检查 + 目视核对 |
| 7 | 开发者 UI：`ConfigView` Tab + `ConfigProfessionCatalogPanel.vue` | 5,6 | 类型检查；`check_file_length`（注意 `lineupBoard.ts` 若因 +行触发豁免清单 ≥20% 警告 → 按规则更新豁免清单基线行数） |
| 8 | 前端测试重写/新增（§5.2） | 5–7 | 告知用户执行 `npm run test`（助手不代跑） |
| 9 | 文档同步（§6 全表） | 1–8 | 逐文件核对 |
| 10 | 全量门禁 + 手工验收（§9） | all | 全部通过后交付用户审核（不提交，走用户主导提交流程） |

## 8. 风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| 半适配（只改了部分引用） | 新职业在下拉可见但排表/筛选缺位 | 常量彻底删除（编译期暴露所有引用点）；store 单点；`professionSource` 测试守卫 |
| store 加载失败/时序 | 下拉空、颜色兜底金 | 守卫 `ensureLoaded` 先于渲染 + 失败静默重试；颜色缓存缺失时兜底 `#c9a13b`（可接受退化） |
| 命名冲突/误操作停用在用职业 | 存量成员编辑被卡 | 旧值豁免三分规则（成员/出勤/单场覆盖）；停用二次确认 + 影响面提示；"最后一个启用职业"守卫 |
| 改名产生历史分裂（快照保留旧名） | 录屏/出勤/分析新旧名并存 | 明确为**预期语义**（历史真相）；确认弹窗文案说明；文档记录 |
| 门禁耦合（表数/迁移数/版本号/豁免清单） | CI 红 | §6 清单 + 以 `check_doc_numbers` 输出为准清零；`lineupBoard.ts` 基线更新预警 |
| 迁移种子与前端规范色不一致 | 单测断言失败 | 种子色值与 GUIDE 表同为字面量三处对照（迁移/测试种子/spec GUIDE），spec 锁定 |
| `DbTestCase` 默认种子影响既有断言 | 用例红 | 种子=原 11 常量，语义等价；仅在个别计数断言处微调 |
| 并发写目录（两名开发者同时编辑） | 后写覆盖 | 目录写入低频；接受 LWW，不做乐观锁（记录为已知限制） |

## 9. 验证清单

**功能验收（本地 `backend/data/nsh-server-20261009.db` 快照副本 + `start.bat` prod 模式，不动生产）**
1. 空库与快照库 `alembic upgrade head` 一次通过，`professions` 11 行种子、ID 自增正常；
2. 开发者登录 → 系统配置「职业目录」新增职业「测试职业」（色 #123456、指定排序）→ 保存成功且立即出现在：成员表单/筛选、补人弹窗、出勤职业筛选与单场配置弹窗、排表候选池与总览、职业配置面板、导出的 Excel 分组、各页职业色；
3. 排序调整后，全站展示顺序同步变更；颜色调整后全站同步（无需刷新/发版）；重新登录后保持；
4. 停用「测试职业」→ 从所有选择器消失；历史数据（若已产生）仍按原色显示；重新启用恢复；
5. 停用"最后一个启用职业"被拒；停用职业时部分成员仍持有时，成员编辑其他字段可保存（职业不变），切换职业必须选启用职业；
6. 重命名既有职业：成员列表、职业配置、单场覆盖同步更名；出勤/录屏/比赛数据历史字符串不变（抽查验证）；
7. Excel 导入含停用职业的行被跳过并报"不存在或已停用"；导出 Sheet 顺序按目录排序；
8. 权限：管理员/帮众调用 POST/PUT `/professions` → 403；GET 正常返回；开发者可用；
9. 管理员「职业配置」目标人数功能回归正常（新增职业自动出现待配置行）。

**门禁/检查（提交前全量）**
- 后端：`pytest`（backend/）、`ruff check .`、`alembic upgrade head`（空库）、`check_schema_drift --strict`、`check_schema_vs_db --strict`；
- 前端：`npm run lint`、`npx prettier --check`（或既有脚本）、`vue-tsc --noEmit`、`vite build`；`npm run test`（**由用户执行**）；
- 仓库门禁：`check_file_length`、`check_doc_numbers`、`check_doc_refs`、`check_stale_paths`、`check_tree_coverage`、`check_api_paths`、`check_type_drift`、`check_nullability`、`check_request_required`、`check_plan_integrity`、`check_requirements_pins`、`check_env_docs`（CI `repo-hygiene` 一致口径）；
- 文档一致性抽查：grep 确认无残留 `PROFESSIONS` / `PROF_ORDER` / `DARK_PROF_COLORS` 引用（前端源码、旧 spec、docs 注释）。

## 10. Rejected Alternatives（否决备选）

1. **每帮会独立职业目录** —— 用户已否决；跨帮会口径分裂、迁移/前端/测试改动显著更大。
2. **仅后端改 DB、前端保留硬编码** —— "半适配"：新职业能导入但下拉/排表缺位；且双重权威源必漂移。
3. **物理删除职业（DELETE）** —— 破坏历史数据一致性叙事（快照悬空、配置残留）；以停用替代，误建职业可停用处理。
4. **改名级联历史快照**（出勤/录屏/比赛数据同步改写）—— 篡改历史真相，且比赛数据来自外部 CSV 无法可靠回写；明确保留"快照不动"语义。
5. **前端 API 失败时回退硬编码种子清单** —— 重新引入第二权威源，违背单一来源目标；改为优雅降级（金色兜底 + 重试）。
6. **服务端目录缓存/推送（TTL cache / WebSocket）** —— 数据量十余行、写入罕见，失效复杂度大于收益；保持每请求直查 + 前端单次加载。
7. **评分权重/坦克辅助分类一并数据化** —— 权重由 1440 条历史数据推导、分路判定含数据驱动规则（潮光/鸿音），属产品口径问题；本轮明确保留代码兜底，记为后续专项。
