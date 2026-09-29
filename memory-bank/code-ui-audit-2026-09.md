# 代码审查与 UI 评估报告（2026-09）

> 本文档为 2026-09-28 一次全项目深度审查的结论快照，覆盖后端代码质量/安全/性能与前端 UI/UX 两大维度。
> 审查方式：代码审查（correctness / 安全 / 性能 / 质量）覆盖 backend/app 全层 + frontend/src 逻辑层；UI 评估基于 `ui-style-guide.md`、`ui-polish-plan.md` 做纯静态分析（未执行浏览器操作）。
> 基准文档：AGENTS.md、memory-bank/ai-checklist.md、ui-style-guide.md、security-review.md、.agent/rules/file-length-rule.md。
> 问题总计：严重 3、高 19、中 34、低 12，另有 8 处需同步修订的规范文档缺陷。

## 一、严重（立即修复）

### C-1 账号写接口向 admin 泄露他人明文密码
- 位置：`backend/app/api/v1/accounts.py`
- 问题：`list_accounts` 已对非 developer 清空 `plain_password`，但 `create_account` / `update_account` / `update_account_status` 三个写接口直接返回未脱敏对象。admin 切换任意同帮会账号状态即可获取其明文密码，违反最小权限原则。
- 修复：抽取公共函数 `_build_account_out(account, current_user)`，在三处 return 前统一按 `role != "developer"` 清空 `plain_password`。
- ✅ 已修复（2026-09-28）：新增统一辅助函数 `_build_account_out(account, current_user)`，list/create/update/update_status 四条响应路径全部经它构造，对非 developer 角色置空 `plain_password`（developer 仍可见，明文列按既定决策保留）。

### C-2 SECRET_KEY 使用硬编码弱默认值
- 位置：`backend/app/core/config.py`
- 问题：`SECRET_KEY` 默认 `"dev-secret-key-change-in-production"`。生产漏配环境变量时，任何人可伪造含 developer 角色的合法 JWT，彻底绕过认证。
- 修复：生产环境启动时校验该值非默认，否则拒绝启动（`sys.exit(1)`）。
- ✅ 已修复（2026-09-28）：config.py 生产弱密钥启动门禁（APP_ENV 主判据 + 容器特征兜底 + 弱片段/年份黑名单 + 64 位 hex 豁免，开发环境 fail-open 仅 WARNING）；docker-compose 固定 APP_ENV=production，deploy.sh 健康检查失败改非零退出并打印容器日志；详见 security-review.md 门禁专节。

### C-3 主按钮文字对比度仅 1.18:1，且禁用态与启用态像素级一致
- 位置：`frontend/src/styles/element-plus.css`
- 问题：`.el-button--primary` 背景改为浅鎏金渐变，但文字仍为 `--el-color-white`（白字 vs 浅金 = 1.18–1.57:1，远低于 WCAG AA 4.5:1）；`background-image` 无条件覆盖使 EP 禁用底色永不显现，禁用态仅 cursor 变化。
- 冲突规范：ui-style-guide §4.1、§2.2；WCAG 2.1 SC 1.4.3 / 1.4.1。
- 修复：文字改墨色 `--ink-900`（≈8.6:1 达 AAA），为 `.is-disabled` 显式声明无渐变 + 灰底 + 无阴影；同步修订 §4.1「白色文字」表述。
- ↩️ 已回退（2026-09-28）：经用户决定保留「白字 + 浅金渐变」观感，对比度不达标作为已知接受项，不再修复。深色文字方案（`--ink-900`）与自定义禁用态已完整撤销，`element-plus.css` 恢复原样；ui-style-guide.md §4.1 已同步并注明用户决策。后续审查勿再将其改为深色/墨色文字。

## 二、高（本迭代修复）

### 后端逻辑与健壮性
- H-1 CSV 上传 `file.filename` 为 None 触发 500：`backend/app/api/v1/match_data.py` 用 `file.filename.endswith(...)`，应改 `(file.filename or "").lower()`（对齐 `members.py` 已有写法）。
- H-2 登录失败计数并发竞态：`backend/app/services/auth_service.py` 用 ORM 读-改-写 `failed_attempts += 1`，并发下锁定阈值可被放大绕过。应改 SQL 原子自增 `update(...).values(failed_attempts=User.failed_attempts+1)`。
- H-3 个人战绩除零隐患：`backend/app/services/my_stats_service.py` 汇总以 `total_rounds` 为除数，依赖前置非空判断，重构易破。应在使用点前显式 `if not records: return`。
- H-4 审计日志 fire-and-forget 任务未持引用：`backend/app/main.py` 的 `asyncio.create_task(...)` 返回值未被引用，高负载 GC 下任务可能静默消失。应用 background task 集合持有 + `add_done_callback(discard)`。
- H-5 出勤职业校验 allowed 可能为空集：`backend/app/services/attendance_service.py` 成员已删且 `record.profession` 为 None 时任何职业都通不过。应加兜底 `allowed = set(PROFESSIONS)`。
- H-6 LIKE 查询未转义通配符：`backend/app/services/player_identity_service.py`、`backend/app/services/log_service.py` 直接拼 `%{keyword}%`，传 `%` 可枚举本帮会全部玩家名。应加 `escape_like()` 并配 `.ilike(..., escape="\\")`。

### 前端视觉与交互
- H-7 34 处引用未定义令牌：`--ink-800`（28 处，含 `frontend/src/components/match-data/PlayerAnalysis.vue`、`RankingTab.vue` 卡片标题）在 `theme.css` 无定义且无 fallback → 标题降级为正文色、层级消失。建议补 `--ink-800: #4a4238`；`--gold-800/--paper-100/--line-300/--green-600` 替换为现有令牌。
- H-8 `prefers-reduced-motion` 对 ECharts 完全失效，且 infinite 动画被压成 0.01ms 死循环：`frontend/src/styles/index.css` 全局回退只改 duration（canvas 动画不受 CSS 控制），`EChart.vue` 无 animation 配置。建议全局块改 `animation: none`，并在 EChart 注入 `animation: !reduceMotion`。
- H-9 `medal-shimmer` 动画驱动 `left` 布局属性：`frontend/src/views/home/HomeAttendanceRanking.vue` 每帧重排，而 `skeleton.css` 已用 transform 正确实现。应统一改 `translateX`。
- H-10 `PROF_COLORS` 双权威源：`frontend/src/utils/profession.ts` 与 `frontend/src/components/match-data/analysis.ts` 逐字节重复定义，且 fallback 有三种（`#c9a13b`/`#e5e7eb`/`#999`）；`ui-polish-plan.md §2.5.1`「已实现」为虚假声明。应让 analysis.ts 转出 profession.ts 并统一 fallback。
- H-11 6 套互不一致的分类色板 + 不可见系列色：`frontend/src/components/match-data/squadCharts.ts` 等含 `#f6ff00`（vs 宣纸白 1.07:1）、`#FF9CF2`（1.83:1），雷达图系列近乎不可见；`CAMP_COLORS` 红绿顺序与 `CONTRIB_COLORS` 相反。应在 `chartTheme.ts` 建单一 `CHART_SERIES_COLORS`（全部 ≥3:1）。
- H-12 769px–1100px 断点真空导致工具栏溢出：`frontend/src/components/match-data/MatchDataTab.vue` `.toolbar` 基础态无 flex-wrap，仅 ≤768px 才换行，iPad 竖屏/分屏必现横向滚动。应把 `flex-wrap: wrap` 提到基础态并新增 1100px 中间断点。
- H-13 Grid 缺 `minmax(0,1fr)` + `.chart-card` 无 overflow → canvas 撑破栅格：`frontend/src/components/match-data/PlayerAnalysis.vue` 裸 `1fr`（RankingTab 已做对）。全站 grid 轨道应统一 `minmax(0,1fr)`，卡片补 `overflow: hidden`。
- H-14 移动端抽屉关闭态仍可 Tab 聚焦 + 多处点击热区无键盘可达：`frontend/src/layouts/AppSidebar.vue`（关闭态未 visibility:hidden）、`AppHeader.vue`（用户下拉是 span、collapse-btn 无 aria-expanded）、`LineupEditor.vue`（pool-fab/pool-close 是 div/el-icon）。应补 inert、Esc 关闭、焦点管理、`role="button"` 或改 `<button>`。
- H-15 触控目标普遍 <44px 且"增大点击区"规则实际无效：`.el-switch { min-height: 28px }` 小于 EP 默认 32px（注释与实现相反），collapse-btn 34px、pool-close 15px。应建 `--touch-target: 44px` 令牌并用负外边距扩命中区。
- H-16 加载期显示"假空态"：`frontend/src/components/match-data/MatchDataTab.vue` `v-if="items.length===0"` 在首次请求未返回时即成立，用户在 loading 期看到"暂无数据请导入 CSV"+ 可点按钮。应三态分离（骨架屏/空态/无筛选结果），复用现有 skeleton.css。
- H-17 主按钮微光 animation-fill-mode 未实现、反向回扫、未做 hover 门控：`frontend/src/styles/element-plus.css` 用 `transition: left`（布局属性）而非 `@keyframes forwards`，移出时倒放，触屏粘滞。应改 transform + forwards + `@media (hover: hover)`（对齐 index.css 的 `.prof-tag::after` 正确范式）。

## 三、中（排期修复）

### 后端（性能 / 债务）
- M-1 录屏 `ensure_recordings` 两次全表查询（`backend/app/services/recording_service.py`）：应仅补查新增记录。
- M-2 个人战绩排名 O(n²)（`backend/app/services/my_stats_service.py`）：极端数据约 260 万次比较，建议预排序 + bisect。
- M-3 日志脱敏对 str 型 detail 不扫描（`backend/app/services/log_service.py`）：异常消息含密码/token 会明文落库，应加正则脱敏。
- M-4 JWT 有效期 10 小时且无刷新机制（`backend/app/core/config.py`）：被盗攻击窗口长，建议缩短 + refresh（需权衡共享账号体验）。
- M-5 `@app.on_event("startup")` 已弃用（`backend/app/main.py`）：应迁 lifespan。
- M-6 文件行数超豁免登记/逼近硬限：`frontend/src/composables/lineupBoard.ts`（485 vs 登记 431）、`frontend/src/components/match-data/MatchDataTab.vue`（444 vs 417）、`backend/app/services/game_id_request_service.py`（297/300）。建议预防性拆分并更新登记。

### 前端（设计系统一致性）
- M-7 `CHART_THEME` 5 色全离群且用冷黑（`frontend/src/components/match-data/chartTheme.ts`）：splitLine/阴影用 `rgba(0,0,0,…)`，tooltip 纯白，违反暖色规范。应改运行时读 CSS 变量或建同源 TS 常量。
- M-8 弹窗标题金线仅右端渐隐（`frontend/src/styles/element-plus.css`）：左端实色，不符「两端渐隐」。
- M-9 顶栏非半透明无毛玻璃 + padding 26px≠规范 24px（`frontend/src/layouts/AppHeader.vue`）。
- M-10 `frontend/src/views/logs/` 整套 Bootstrap 3 残留（`LogStatsCards.vue` 等）：`#d9534f/#c9302c` 冲突朱砂色、fallback 值错误、monospace 未用 `--font-num`、筛选栏无 media query。需系统性令牌化。
- M-11 靛青浅色族未令牌化跨 5 文件重复（`--indigo` 无浅色阶）。
- M-12 奖牌渐变 4 文件重复且阴影分叉（应抽 `styles/medals.css`）。
- M-13 图表 option 未包 computed 致动画重放（`PlayerAnalysis.vue`、`frontend/src/components/my-stats/StatsTrendChart.vue`）：切换下拉框时全页图表集体闪烁。RankingTab 已正确包 computed，为项目正面范式。
- M-14 `hideOverlap` 静默丢弃 Top-20 玩家名（`frontend/src/components/match-data/paretoChart.ts`）：信息丢失，建议改横向条形图。
- M-15 `interval:0` + 28 个 10px 柱顶标签移动端碰撞（`frontend/src/components/match-data/squadCompareCharts.ts`）。
- M-16 同弹窗内 legend 位置不一致；多系列图无 legend（颜色无法解码）。
- M-17 移动端高度钳制破坏内容驱动高度（`frontend/src/components/match-data/EChart.vue`）：11 职业热力图需 388px 被钳到 280px 致标签重叠。
- M-18 emoji 充当功能图标（`RankingTab.vue` 的 🏅）：跨平台字形不一、无法着色，应改 `@element-plus/icons-vue`。
- M-19 56 处字号 <12px（最小 9px）+ 对比度不足：`AppSidebar.vue`（9px）、`frontend/src/views/member-home/DataHighlightCard.vue`（`.king-cell__label` 11px + `--ink-400` 3.10:1 双重失效；`.mvp-block__badge` 白字金底 1.4:1）；`--gold-700` 3.96:1、鎏金渐变文字 1.92–3.10:1 用于强调数值均不达 AA。应建字号令牌 + 收窄 `--ink-400` 用途 + 渐变压深至 `--gold-600→700`。
- M-20 `.page-enter` 是死文档 + 两层路由过渡叠加 + z-index 冲突：`frontend/src/App.vue` 外层 route-fade 与 `MainLayout.vue` 内层 page-switch 同时生效；LineupEditor 的 FAB(1002) 浮于抽屉遮罩(1000) 之上。应只保留一层过渡 + 建 z-index 令牌。
- M-21 零间距令牌 + 24 处圆角脱离标度 + 19 处硬编码阴影 + 离群金 `#d4af37`：全站间距皆魔法数字（卡片内边距有 4 种），`--radius-full` 不存在（代码用 999px），`frontend/src/styles/theme.css` 的 `#d4af37` 不在鎏金色板。应补间距/圆角/阴影令牌族并清理离群色。

## 四、低（择机优化）

- L-1 `AppHeader.vue` `.collapse-btn { transition: all }` 触发 layout，应显式列属性。
- L-2 `rankingCharts.ts`/`squadCharts.ts`/`paretoChart.ts` x 轴 rotate 35/30/25、fontSize 10/11/12 无统一，应导出单一常量。
- L-3 `rankingCharts.ts` 双 y 轴 nameTextStyle padding 魔法数，应用 nameGap + nameLocation。
- L-4 tooltip 展开顺序不一致（脆弱），应统一 `{ ...CHART_THEME.tooltip, trigger:'axis' }`。
- L-5 `squadCharts.ts` 堆叠柱圆角仅单系列，应移到最顶层系列或全去掉。
- L-6 `HomeStatCards.vue` 900px 断点用裸 1fr（480px 已用 minmax），应统一。
- L-7 全站断点全为魔法数字（768×57/480×16/900×5）无令牌无文档，应在 §8 登记唯一允许值集合。
- L-8 4 个 `*-shared.css` 未登记于 ui-style-guide §9。
- L-9 `HomeStatCards.vue` `.stat-card__number` 长文本静默裁切无省略号，应补 text-overflow + title。
- L-10 `HomeStatCards.vue` 渐变文字未用 `var(--gold-gradient)` 令牌而重写 hex。
- L-11 `chartTheme.ts` 未用 `echarts.registerTheme`，每个 option 都要内联展开易漏。
- L-12（正面确认）`HomeStatCards.vue` 入场延迟 60ms 实现正确，无需修改。

## 五、需同步修订的规范文档（8 处）

依 AGENTS.md「先核实代码事实，再修正文档」，代码整改须与以下文档修订同步：
- D-1 `ui-style-guide §4.3 vs §10.3` 金线宽度自相矛盾（56px vs 等宽），代码采纳 §10.3。
- D-2 `§6/§9` 的 `.page-enter`/0.35s/12px 与实现（`.page-switch`/0.18s/8px）三项全不符，`.page-enter` 类不存在。
- D-3 `§8.2` `full:50%` 应拆为 `999px`(胶囊)/`50%`(正圆)，theme.css 无 `--radius-full`。
- D-4 `§4.1`「白色文字」在浅金底上物理不可行（1.18:1），应改墨色文字。
- D-5 `§5.3` 渐变文字未标色值下限，实际 1.92–3.10:1 不满足大字 AA 3:1。
- D-6 `§3.2` 12px 下限与 56 处违例（含 9px），应严格执行或新增装饰性例外条款。
- D-7 `§2.4` `--ink-400` 用途应收窄为 placeholder/禁用/纯装饰，辅助说明改指 `--ink-500`。
- D-8 `ui-polish-plan §2.5.1` 虚假「已实现」+ §3 落点失效（HomeView 已拆分）；§2.2.1（animation-fill-mode）与 §5 验收（扫过后高光、两端渐隐）应标记未通过。
- 建议：将 polish-plan 回退为 `v1.4-draft（部分未完成）`，避免后续以"已完成"为前提决策。

## 六、值得保留的优秀实践（重构时务必保护）

1. `frontend/src/styles/skeleton.css`：transform 单属性动画（合成层 60fps）+ 正确的 reduced-motion 终态。
2. `frontend/src/components/common/EmptyState.vue`：全令牌零硬编码、4 变体齐全，`el-empty` 替换已真实达成（全站仅剩 1 处在 EmptyState 内部）。
3. `frontend/src/components/match-data/EChart.vue`：rAF + ResizeObserver + clientWidth/Height>0 三重初始化守卫，正确处理弹窗内 0 尺寸挂载；卸载完整清理无泄漏。
4. `element-plus.css` 固定列不透明背景修补 + 解释性注释；loading 遮罩浅色化并界定用途；≤480px 表格行内按钮扩命中区。
5. `index.css` `.prof-tag::after` 正确使用 `@media (hover: hover)` 门控；移动端块防 iOS Safari 自动缩放（input 16px）。
6. `RankingTab.vue` 全部 5 个图表 option 正确包 computed（M-13 正面范式）。
7. `LoginView.vue` 登录限流三要素齐备（倒计时 + 剩余时间 + 提交拦截）。
8. `el-tabs` 全量 lazy（MatchDataTab 8 个 tab-pane），避免进入即并发加载。
9. 28 处 `:disabled` 绑定语义分类整体正确，未发现逻辑错误。

## 七、建议整改顺序（按 ROI）

1. 安全合规批（1–2 天）：C-1、C-2、C-3、H-7（补 --ink-800）、M-19 徽章白字。多为单点改动，直接消除越权/认证/WCAG 违规。
2. 色彩单源批（3–5 天）：H-10、H-11、M-7、M-12、M-21。建立色彩单一权威源，消除大部分硬编码。
3. 响应式布局批（3–4 天）：H-12、H-13、M-17、M-21 间距/圆角令牌。需先建令牌再批量替换。
4. 动画与可访问性批（2–3 天）：H-8、H-9、H-17、H-14、M-20。共享 reduced-motion / hover 门控基础设施。
5. 图表细节与文档批（2–3 天）：M-13/14/15/16 + 低优先项 + D-1…D-8 文档修订（放最后以记录真实状态）。

## 八、风险与说明

- 前端为纯静态分析（遵守浏览器操作约定）。C-3 实际渲染对比度、H-12 溢出量、M-14/15 标签碰撞程度依赖真实数据与构建产物，建议后续授权一次浏览器视觉复核确认。
- 后端 C-1、C-2、H-1~H-6 建议优先验证复现再修（遵循「先验证后修复」原则）。
- 本报告为只读审查结论，未修改任何代码，未执行 git 操作。

## 更新记录

| 日期 | 更新内容 | 关联模块 |
|------|----------|----------|
| 2026-09-28 | 首次创建：全项目代码审查 + UI 评估整合报告 | 全栈（backend/app、frontend/src） |
