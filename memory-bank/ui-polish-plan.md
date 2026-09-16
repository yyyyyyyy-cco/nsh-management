# UI 优化方案文档

> 版本：v1.2  
> 创建日期：2026-08-26  
> 更新时间：2026-09-15  
> 前置文档：`ui-style-guide.md`（权威视觉规范，动画族/卡片层级/交互反馈最终规范见其 §10）  
> 实现位置：`frontend/src/styles/` + 各组件 `<style>` 区  
> **状态**：P0–P3 共 11 项 + §2.5 代码质量重构 2 项已完成（2026-09-15 代码核对）；3 项可选未做（§2.1.3 / §2.3.3 / §2.4.4）

---

## 1. 背景与目标

### 1.1 现状评估
当前 UI 基于「浅色雅金风（宣纸鎏金）」主题，已完成 Element Plus 深度定制和全站组件适配。经审查，基础骨架扎实，但在**视觉层次、交互反馈、情感化细节**三个维度仍有提升空间。

### 1.2 优化原则
- **不改主题方向** — 宣纸鎏金风格不变，只在现有框架内打磨
- **不引入新依赖** — 所有优化基于 CSS + Vue 过渡，不增加第三方库
- **渐进增强** — 每项优化独立可验收，不影响现有功能
- **保持响应式** — 所有优化在 768px / 480px 断点下同样生效

---

## 2. 优化清单

按优先级分为 P0（视觉层次）、P1（交互反馈）、P2（视觉细节）、P3（微动效）。

### 2.1 P0 · 视觉层次 & 信息密度（已完成）

#### 2.1.1 卡片层级区分
- **现状**：所有 `.card` 样式一致（宣纸白 + `edge-soft` + `shadow-sm`），视觉层次扁平
- **方案**：
  - 主内容卡片（表格/列表/编辑器）：保持现有样式
  - 统计卡片（`.stat-card`）：保持金色渐变底，已有区分
  - 辅助卡片（快捷操作/职业分布）：底色改为 `--ink-bg-cream`，阴影降为无或 `shadow-sm` 的 50%
  - 信息条（历史总览等）：底色 `--ink-bg-wash`，更内敛
- **涉及文件**：`HomeView.vue`、各 Tab 组件中的 `.card` 样式
- **实现位置**：各组件内 `<style scoped>`

#### 2.1.2 统计数字滚动动画
- **现状**：统计卡数字直接显示目标值，没有过渡
- **方案**：数字从 0 滚动到目标值，时长 800ms，ease-out 缓动
- **实现方式**：composable `useCountUp.ts`，基于 `requestAnimationFrame`，纯数字递增（不依赖第三方）
- **涉及文件**：新增 `composables/useCountUp.ts`，修改 `HomeView.vue`、`OverviewTab.vue` 统计卡
- **reduced-motion 适配**：检测 `prefers-reduced-motion: reduce` 时直接显示目标值

#### 2.1.3 表格密度切换（未做，可选）
- **现状**：统一 13.5px 字号 + 10px padding
- **方案**：提供「紧凑 / 标准」密度按钮，紧凑模式 12.5px + 6px padding
- **涉及文件**：`element-plus.css` 新增密度类、各表格页面增加切换按钮
- **优先级较低，可在其他优化完成后考虑**

---

### 2.2 P1 · 交互反馈 & 精致度（已完成）

#### 2.2.1 主按钮微光扫过增强
- **现状**：`element-plus.css` 中 `::after` 白色扫光 40% 宽，效果偏弱
- **方案**：
  - 扫光宽度 40% → 60%
  - 透明度增加：`rgba(255,255,255,0.45)` → `rgba(255,255,255,0.55)`
  - 扫过后保持短暂高光（`animation-fill-mode`）
- **涉及文件**：`element-plus.css`（`.el-button--primary::after`）
- **影响范围**：全站所有主按钮

#### 2.2.2 侧边栏菜单 hover 过渡
- **现状**：菜单项 hover 到激活态没有渐变中间状态
- **方案**：`background` 属性增加 `transition: background var(--dur-fast) var(--ease-out)`，hover 时先浅金底再变深
- **涉及文件**：`MainLayout.vue`（`.menu :deep(.el-menu-item)`）

#### 2.2.3 卡片入场动画差异化
- **现状**：所有卡片都用 `page-rise`（fade + translateY），只有 delay 不同
- **方案**：
  - 统计卡：`stat-pop` — scale(0.95) + fade → scale(1) + opacity(1)
  - 列表卡：`card-slide` — translateY(16px) + fade → translateY(0) + opacity(1)
  - 信息条：`bar-rise` — 保持现有 page-rise
- **涉及文件**：`index.css`（新增动画定义）、`HomeView.vue`（统计卡应用新动画）

#### 2.2.4 排行榜奖牌视觉冲击
- **现状**：金银铜牌只有渐变圆形，缺少视觉冲击
- **方案**：
  - 金牌：加微光 `shimmer` 动画（金色高光从左到右循环扫过），阴影增强为 `0 2px 8px rgba(212,160,23,0.5)`
  - 银牌：加微光（银色调），阴影 `0 2px 6px rgba(154,154,154,0.4)`
  - 铜牌：保持现有，阴影微调
- **涉及文件**：`HomeView.vue`（`.rank-item__number--1/2/3` 样式）
- **动画定义**：`@keyframes medal-shimmer` 在 `HomeView.vue` 内定义

---

### 2.3 P2 · 视觉细节打磨（已完成，2.3.3 未做）

#### 2.3.1 弹窗标题金线加宽
- **现状**：`.el-dialog__header::after` 固定 56px 宽
- **方案**：改为 `width: 100%`（与标题等宽），两端透明渐变，保持 2px 高度
- **涉及文件**：`element-plus.css`（`.el-dialog__header::after`）
- **影响范围**：全站所有弹窗

#### 2.3.2 滚动条配色优化
- **现状**：`::-webkit-scrollbar-thumb` 纯灰色 `#d8d0bd`
- **方案**：
  - thumb: `#d4c5a0`（金色调），hover: `#c4b28a`
  - track: `#f5f0e6`（宣纸底色调）
- **涉及文件**：`element-plus.css`（`::-webkit-scrollbar` 系列）

#### 2.3.3 空状态插画升级（未做，可选）
- **现状**：用 emoji（📅）+ 文字 + 按钮
- **方案**：SVG 手绘线条风格插画替代 emoji，保持宣纸金色调
- **涉及文件**：各组件空状态区域
- **优先级较低**

---

### 2.4 P3 · 微动效 & 情感化（已完成，2.4.4 未做）

#### 2.4.1 排表槽位放入反馈
- **现状**：拖拽到槽位只有 `ghost-class`
- **方案**：放入成功后，槽位卡片执行 `slot-bounce`（scale 1.05 → 1，0.3s）+ 金色边框闪烁一次
- **涉及文件**：`LineupEditor.vue`（槽位样式 + composable `lineupBoard.ts`）
- **实现方式**：拖拽 end 回调中给目标元素添加临时 class，`animationend` 移除

#### 2.4.2 保存成功正反馈
- **现状**：保存后只显示「✓ 已保存」文字
- **方案**：保存成功后，「✓ 已保存」文字加金色光晕扩散动画（`save-flash`，0.6s）
- **涉及文件**：`LineupEditor.vue`（`.auto-save` 样式）

#### 2.4.3 路由切换过渡
- **现状**：页面切换只有进入动画，无过渡
- **方案**：在 `App.vue` 用 `<Transition>` 包裹 `<router-view>`，fade 淡入淡出，时长 200ms
- **涉及文件**：`App.vue`
- **注意**：`prefers-reduced-motion` 时禁用

#### 2.4.4 职业标签 hover 效果（未做，可选）
- **现状**：职业标签是纯色胶囊，无交互反馈
- **方案**：hover 时加微光效果（与奖牌类似的 shimmer，但更克制）
- **涉及文件**：各组件中 `.el-tag` 职业色标签

### 2.5 P-R · 代码质量重构（已完成）

#### 2.5.1 职业色映射统一
- **方案**：抽取到 `utils/profession.ts`，全站一处维护
- **结果**：已实现（`utils/profession.ts` 存在并被各组件统一引用）

#### 2.5.2 结果类型函数统一
- **方案**：抽取到 `utils/constants.ts`，复用已有的 `SCHEDULE_RESULTS` 常量
- **结果**：已实现（`resultType` / `resultLabel` 统一从 `@/utils/constants` 引入）

---

## 3. CSS 令牌与动画落点汇总

实际落点（2026-09-15 代码核对）：

| 内容 | 定义位置 | 使用位置 |
|------|---------|---------|
| `stat-pop` / `card-slide` | `styles/index.css` | 统计卡 / 列表卡入场 |
| `medal-shimmer` | `HomeView.vue` | 排行榜金银奖牌 |
| `slot-bounce` / `save-flash` | `LineupEditor.vue` | 槽位放入 / 保存反馈 |
| 滚动条配色（thumb `#d4c5a0`） | `styles/element-plus.css` | 全局滚动条 |

> `theme.css` 无新增变量（所有新动画在组件内定义，避免全局污染）。

---

## 4. 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `frontend/src/styles/theme.css` | 修改 | 无新增变量（所有新动画在组件内定义，避免全局污染） |
| `frontend/src/styles/element-plus.css` | 修改 | ①按钮微光扫光加宽 ②弹窗金线加宽 ③滚动条配色 |
| `frontend/src/styles/index.css` | 修改 | 新增 `stat-pop` / `card-slide` 动画定义 |
| `frontend/src/composables/useCountUp.ts` | **新增** | 数字滚动 composable |
| `frontend/src/views/HomeView.vue` | 修改 | ①统计卡用 countUp + stat-pop ②奖牌微光 ③辅助卡片层级 |
| `frontend/src/layouts/MainLayout.vue` | 修改 | 菜单 hover 过渡 |
| `frontend/src/components/match-data/OverviewTab.vue` | 修改 | 统计卡用 countUp |
| `frontend/src/components/lineups/LineupEditor.vue` | 修改 | 槽位放入反馈 + 保存成功动效 |
| `frontend/src/App.vue` | 修改 | 路由切换过渡 |

---

## 5. 验收标准

每项优化完成后，按以下标准验收：

| 优化项 | 验收标准 |
|--------|---------|
| 卡片层级 | 辅助卡与主卡在视觉上有明显轻重之分 |
| 数字滚动 | 页面加载时数字从 0 滚到目标值，动画流畅无跳帧 |
| 按钮微光 | hover 主按钮时白色扫光清晰可见，扫过后有短暂高光 |
| 菜单过渡 | 侧边栏菜单 hover 有平滑渐变，无突兀跳变 |
| 卡片入场 | 统计卡和列表卡入场动画族不同，可肉眼区分 |
| 奖牌微光 | 金牌有持续金色高光扫过，银牌有银色微光 |
| 弹窗金线 | 所有弹窗标题下方金线与标题等宽，两端渐隐 |
| 滚动条 | 滚动条为金色调，与宣纸底色协调 |
| 槽位反馈 | 拖拽放入后槽位有弹跳 + 金光闪烁 |
| 保存反馈 | 保存成功后文字有金色光晕扩散 |
| 路由过渡 | 页面切换有平滑淡入淡出，无白屏闪烁 |

---

## 6. 移动端适配原则

- 所有动画在 `@media (max-width: 768px)` 下保持，但时长缩短（`var(--dur-normal)` 即 0.22s）
- `prefers-reduced-motion: reduce` 时**全部动画停用**，直接显示最终状态
- 触屏设备不使用 hover 依赖的微光效果（通过 `@media (hover: hover)` 门控）

---

## 更新记录

| 日期 | 更新内容 |
|------|---------|
| 2026-08-26 | 初始化 UI 优化方案文档（v1.0），4 优先级 11 项优化 |
| 2026-08-26 | v1.1 新增 §2.5 代码质量重构：职业色映射统一（utils/profession.ts，14→1 文件）、结果类型函数统一（utils/constants.ts，5→1 文件） |
| 2026-09-15 | v1.2：全部优化项标注完成状态（P0–P3 11 项 + §2.5 两项已完成；3 项可选未做已标注）；§2.5 归位至优化清单内；§3 更正动画/令牌实际落点（theme.css 无新增变量，最终规范以 ui-style-guide.md §10 为准） |
