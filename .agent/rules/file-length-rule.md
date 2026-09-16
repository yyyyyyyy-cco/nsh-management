---
trigger: always_on
---
# 代码文件长度规则

## 文件行数限制

| 文件类型 | 建议行数 | 强制上限 |
|---------|---------|---------|
| 组件文件（Vue） | 100-200行 | 300行 |
| 服务文件（Python） | 100-200行 | 300行 |
| 工具函数文件 | 50-150行 | 200行 |
| 路由文件 | 50-100行 | 150行 |

## 拆分触发条件

当文件出现以下情况时，必须进行拆分：
- 行数超过强制上限
- 包含3个以上不相关的功能
- 出现多个独立的业务逻辑块
- 同一文件中有多个类或多个大型函数

## 拆分策略

```
❌ 错误示例：所有功能集中在一个文件
utils.ts (500行)
  ├── formatDate()
  ├── validateEmail()
  ├── parseCSV()
  ├── formatCurrency()
  └── generateReport()

✅ 正确示例：按功能模块拆分
utils/
  ├── date.ts        # 日期相关
  ├── validation.ts  # 验证相关
  ├── csv.ts         # CSV解析
  ├── currency.ts    # 货币格式化
  └── report.ts      # 报告生成
```

## 行数豁免机制（连续逻辑）

拆分不是唯一解：文件内容为**单一连续逻辑**（同一状态机 / 同一数据流 / 同一交互面）时，拆分必然引入大量跨组件状态转发与回调，此时允许超限保留，但必须满足两条：**① 文件头部打「行数豁免」标记 ② 登记到下方豁免清单**。

### 标记格式（grep 关键词：`行数豁免`）

| 文件类型 | 标记写法与位置 |
|---------|---------------|
| Vue | `<!-- 行数豁免（连续逻辑）：<理由>｜登记见 .agent/rules/file-length-rule.md 豁免清单 -->`，置于 `<template>` 之前 |
| TS / JS | `/** 行数豁免（连续逻辑）：<理由> */`，并入文件头部注释 |
| Python | `# 行数豁免（连续逻辑）：<理由>`，紧随模块 docstring |

### 判定口径

- 文件内存在 **≥2 个「可独立修改且接口清晰」的单元** → 拆分（不豁免）；超限倍数仅作辅助（建议 >1.5 倍优先评估拆分）
- 围绕同一状态的控制器、单一日历/表格式组件、单资源薄路由、同源数据的多视图/弹窗 → 可豁免
- 豁免文件**再增长时应重新评估**；新增豁免必须登记，不得只打标记

### 豁免清单（2026-09-15 登记；行数为打标记前实测值）

| 文件 | 行数 | 超限原因（连续逻辑） |
|------|------|---------------------|
| `frontend/src/components/lineups/LineupEditor.vue` | 1029 | 候选池↔槽位共享同一拖拽看板状态，拆分需跨组件转发拖拽处理器与槽位数据形态 |
| `frontend/src/composables/lineupBoard.ts` | 431 | 看板状态机：拖拽上下文 / 自动保存定时器 / 候选池回池逻辑共享内部可变状态 |
| `frontend/src/components/match-data/MatchDataTab.vue` | 417 | 分析页控制器：导入 / 切局 / 筛选 / 加载围绕同一数据流（子 Tab 已组件化） |
| `frontend/src/views/LoginView.vue` | 357 | 登录表单、锁定倒计时、错误映射围绕同一登录流程 |
| `frontend/src/components/my-stats/StatsMatchTable.vue` | 356 | 同一「各场明细」数据的三种视图（基础 / 战斗 / 占比与排名） |
| `frontend/src/components/match-data/ScoreTab.vue` | 351 | 综合评分表与得分分解弹窗围绕同一评分视图 |
| `frontend/src/views/schedules/LeagueOverviewView.vue` | 342 | 赛程总览页响应式双视图（移动卡片 / 桌面表格）同源数据 |
| `frontend/src/views/schedules/ScheduleListView.vue` | 339 | 赛程列表页单职责（月/全部模式 + 新建编辑弹窗） |
| `frontend/src/components/schedules/ScheduleCalendar.vue` | 328 | 单一日历组件（格子计算 + 月份切换 + 事件派发） |
| `frontend/src/components/lineups/ImportHistoryDialog.vue` | 310 | 导入历史排表两步流程（选赛程 → 按小队多选）一体化 |
| `frontend/src/components/match-data/OverviewTab.vue` | 301 | 单场比赛数据总览面板（统计卡 / 占比条 / 阵营卡 / 图表区同源） |
| `backend/app/api/v1/members.py` | 188 | 单资源薄路由（CRUD + 导入导出端点声明同质） |
| `backend/app/api/v1/attendance.py` | 173 | 单资源薄路由（列表操作 + 导入端点声明同质） |
