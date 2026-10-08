# UI 审计修复计划

## 阶段一：P1 快速修复（预期工时：小）

### 1.1 ConfigView 硬编码颜色替换

**问题**: `.tip { color: #6b7280 }`、`.dialog-tip { color: #9ca3af }` 未使用 CSS 变量

**文件**: `frontend/src/views/config/ConfigView.vue`

**修改**:
```
-  .tip { color: #6b7280; }
+  .tip { color: var(--ink-400); }
-  .dialog-tip { color: #9ca3af; }
+  .dialog-tip { color: var(--ink-400); }
```

### 1.2 StatsOverview 渐变文字收敛

**问题**: 6 张数值卡均使用 `background-clip: text` 金色渐变，过量扩散

**文件**: `frontend/src/components/my-stats/StatsOverview.vue`

**修改**:
```
-  background: var(--gold-gradient);
-  -webkit-background-clip: text;
-  background-clip: text;
-  color: transparent;
+  color: var(--gold-700);
```

### 1.3 HomeView 空态 emoji 替换

**问题**: raw emoji `\u{1F4C5}`(📅)、`\u{1F465}`(👥) 作空状态图标

**文件**: `frontend/src/views/HomeView.vue`

**修改**: 将 `empty-state__icon` 中的 emoji 替换为 Element Plus 图标（Calendar、UserFilled），增大图标尺寸

### 1.4 MyStatsView 空态 emoji 替换

**问题**: raw emoji `\u{1F3C6}`(🏆) 作初始空态图标

**文件**: `frontend/src/views/member/MyStatsView.vue`

**修改**: 将 `empty-icon` 中的 emoji 替换为 Element Plus 图标（Trophy），移除 ElEmpty 的 #image slot

---

## 阶段二：P2 快速修复（预期工时：小）

### 2.1 MainLayout 顶栏毛玻璃去掉

**文件**: `frontend/src/layouts/MainLayout.vue`

**修改**: 
```
-  background: rgba(253, 250, 244, 0.9);
-  backdrop-filter: blur(8px);
+  background: var(--ink-bg-paper);
```

### 2.2 App.vue 路由过渡并行化

**文件**: `frontend/src/App.vue`

**修改**: `mode="out-in"` 改为 `mode=""`，缩短 transition-duration 到 0.15s

### 2.3 全局标题 overflow-wrap 保护

**涉及文件**:
- `frontend/src/views/LoginView.vue` — `.brand-title` 添加
- `frontend/src/views/HomeView.vue` — `.welcome-title` 添加
- `frontend/src/layouts/MainLayout.vue` — `.page-title` 添加

**修改**: 为上述选择器添加 `overflow-wrap: anywhere`

### 2.4 弹窗 body 滚动锁定

**涉及文件**: `frontend/src/styles/element-plus.css`

**修改**: 在 `.el-overlay-dialog` 出现时锁定 body 滚动；或在 `.el-dialog` 的 open/close 事件中设置 `document.body.style.overflow`

---

## 阶段三：P2 中工时修复（预期工时：中）

### 3.1 LogView 添加移动端行列表

**文件**: `frontend/src/views/logs/LogView.vue`

**修改**: 参照 AttendanceTab/RecordingTab 模式：
- 添加 `isMobile` 响应式检测（复用项目现有模式）
- ≤768px 渲染行列表（时间/级别/操作人/模块/动作摘要 + 点击展开详情）
- 行列表卡片内边距 14px，操作 32px 紧凑按钮
- 桌面端保持现有表格

### 3.2 ConfigView 账号管理 Tab 添加移动端行列表

**文件**: `frontend/src/views/config/ConfigView.vue`

**修改**: 
- 账号列表（按帮会分组）的 el-table 在 ≤768px 换为行列表
- 行列表显示：登录名 + 角色标签 + 状态标签 主行 / 操作按钮（编辑/禁用/删除）右对齐次行
- 帮会管理表格保持现有功能

### 3.3 骨架屏加载态（选择性）

**文件**: 
- `frontend/src/views/schedules/ScheduleListView.vue`
- `frontend/src/views/logs/LogView.vue`

**修改**: 为表格区域添加骨架屏占位替代 v-loading spinner

---

## 阶段四：P2 大工时（预期工时：大，可选延后）

### 4.1 SquadAnalysisTab 组件拆分

**文件**: `frontend/src/components/match-data/SquadAnalysisTab.vue` (1296 行)

**修改**: 拆分为 3-4 个子组件：
- `SquadOverviewCharts.vue` — 四张对比图
- `SquadDetailCards.vue` — 小队卡片网格 + 分组
- `SquadCompareDialog.vue` — 对比弹窗

### 4.2 深色模式（可选延后）

**文件**: `frontend/src/styles/theme.css` + 各组件

**修改**: 新增 `prefers-color-scheme: dark` 深色 CSS 变量集

---

## 执行顺序

1. 阶段一 P1 修复 → 4 项（硬编码颜色、渐变文字收敛、2 处 emoji 替换）
2. 阶段二 P2 快速修复 → 4 项（毛玻璃、路由过渡、overflow-wrap、滚动锁定）
3. 阶段三 P2 中工时 → 2 项（LogView 行列表、ConfigView 行列表）+ 骨架屏
4. 阶段四 → 视情况决定

## 验证方法

- 每项修复后运行 `npm run build` 确认编译通过
- ConfigView 颜色替换后肉眼确认提示文字与 ink-400 一致
- 移动端适配在 Chrome DevTools 320/375/414/768 四点验证
- 路由过渡在页面间快速切换查看是否有白闪
