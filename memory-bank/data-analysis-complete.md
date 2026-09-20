# 数据分析模块完整方案

> 本文档整合数据规格（CSV 字段 / 小队结构）、指标公式、开发方案、ECharts 图表规划与实施记录

## 参考文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 原始CSV数据 | `.agent/docs/20260630_21037_横戈_仗剑.csv` | 比赛数据样本 |
| Excel分析表 | `.agent/docs/联赛数据表Plus3.0.xlsm` | 原始分析逻辑参考 |

---

## 一、项目概述

### 1.1 目标
将 Excel 联赛数据表 Plus3.0 的完整分析能力迁移到 nsh-management 系统，包括：
- 16项衍生指标计算
- 阵营对比分析
- 职业深度分析
- 小队维度分析
- ECharts 可视化图表

### 1.2 技术栈

> **权威源**：`tech-stack.md`（完整版本与依赖列表）。本模块图表库为 ECharts 6.x。

---

## 二、原始数据结构

### 2.1 CSV 文件格式

```
"阵营名","人数"
"玩家名字","职业","击败/清泉","助攻","资源","对玩家伤害","人伤卸甲","对建筑伤害","破塔卸甲","治疗值","承受伤害","重伤","复活/清泉","焚骨"
"玩家1","玄机"," 16/5","82","0","3189843","0","3289538","0","0","4196936","12","0","0"
```

### 2.2 字段映射关系

| CSV 字段 | 系统字段 | 说明 |
|---------|---------|------|
| 玩家名字 | player_name | - |
| 职业 | profession | - |
| 击败/清泉 | kills, springs | "16/5" → kills=21(击败+清泉), springs=5(清泉) |
| 助攻 | assists | - |
| 资源 | - | **忽略，不显示** |
| 对玩家伤害 | player_damage | - |
| 人伤卸甲 | armor_break_damage | - |
| 对建筑伤害 | building_damage | - |
| 破塔卸甲 | tower_break_damage | - |
| 治疗值 | healing | - |
| 承受伤害 | damage_taken | - |
| 重伤 | deaths | - |
| 复活/清泉 | revives | 对应 Excel 的「化羽/清泉」 |
| 焚骨 | fen_gu | - |

### 2.3 关键约束

- springs = 破泉次数（来自击败/清泉的右边）
- kills = 击败 + 清泉（系统现有逻辑，不拆分）
- 
revives = 化羽/清泉（来自复活/清泉字段）
- **忽略「资源」字段**，整个系统不显示
- **破泉率不需要添加**
- **比赛时长固定 23 分钟**

---

## 三、小队结构

### 3.1 系统排表结构（10队 × 6人）

```python
LINEUP_LAYOUT = [("进攻1", 3), ("进攻2", 3), ("防守1", 2), ("防守2", 2)]
SLOTS_PER_TEAM = 6
```

### 3.2 小队对应关系（系统 → Excel）

| 系统排表 | Excel |
|---------|-------|
| 进攻1 第1队 | 进攻1队 |
| 进攻1 第2队 | 保镖1队 |
| 进攻1 第3队 | 进攻2队 |
| 进攻2 第1队 | 进攻3队 |
| 进攻2 第2队 | 保镖2队 |
| 进攻2 第3队 | 进攻4队 |
| 防守1 第1队 | 防守1队 |
| 防守1 第2队 | 防守2队 |
| 防守2 第1队 | 防守3队 |
| 防守2 第2队 | 防守4队 |

**原则：命名以系统为准，仅参考 Excel 的底层分析逻辑**

### 3.3 JSON 数据结构

```json
{
  "category": "进攻1",
  "team_index": 0,
  "remark": "",
  "slots": [
    {"slot_index": 0, "member_id": 123, "member_name": "玩家名", "remark": ""}
  ]
}
```

---

## 四、当前系统现状（历史快照）

> 原「已有功能 / 已有组件」清单为实施前快照，所有功能已于 2026-08-26 实现并验证，详见「十、实施记录」。

---

## 五、指标公式与功能定义（已全部实现）

### 5.1 指标公式与功能定义

#### 衍生指标（16项）

**效率指标（3项）**

| 指标 | 公式 | 精度 |
|------|------|------|
| KDA | (击杀+助攻)/max(死亡,1) | 2位小数 |
| 秒伤 | (人伤+拆塔)/(23×60) | 整数 |
| 参与击杀均伤 | (人伤+拆塔)/max(击杀+助攻,1) | 整数 |

**生存指标（4项）**

| 指标 | 公式 | 精度 |
|------|------|------|
| 每死输出值 | (人伤+拆塔)/max(死亡,1) | 整数 |
| 每死承伤 | 承伤/max(死亡,1) | 整数 |
| 死亡治疗量 | 治疗/max(死亡,1) | 整数 |
| 治疗转化率 | 死亡治疗量/max(每死承伤,1) | 2位小数 |

**占比指标（7项）- 分母为整个阵营**

| 指标 | 公式 | 精度 |
|------|------|------|
| 击杀占比 | 个人击杀/全队总击杀 | 百分比 |
| 助攻占比 | 个人助攻/全队总助攻 | 百分比 |
| 人伤占比 | 个人人伤/全队总人伤 | 百分比 |
| 拆塔占比 | 个人拆塔/全队总拆塔 | 百分比 |
| 承伤率 | 个人承伤/全队总承伤 | 百分比 |
| 死亡占比 | 个人死亡/全队总死亡 | 百分比 |
| 治疗占比 | 个人治疗/全队总治疗 | 百分比 |

**技能指标（2项）**

| 指标 | 公式 | 精度 |
|------|------|------|
| 清泉/羽化使用率 | revives/(23×60) | 百分比 |
| 焚骨使用率 | fen_gu/(23×60) | 百分比 |

#### 阵营对比分析

- 敌方 vs 我方宏观对比、差值、波动值（已实现：`camp-compare` 接口 + CampCompareTab 对比图）

#### 职业深度分析

- 11 职业 × 17 项指标（人数 + 16 项均值）、职业对比、差值/波动值、承伤率、技能使用率（已实现：`get_profession_stats` + ProfessionDetailTab）

#### 小队维度分析

- 进攻/防守小队分析、小队×职业交叉、小队塔伤贡献、差值/波动值（已实现：`squad-analysis` 接口 + SquadAnalysisTab，仅分析我方阵营）

---

## 六、开发方案

### 6.1 API 设计

#### 新增接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /schedules/{id}/match-data/indicators | GET | 获取带衍生指标的数据列表 |
| /schedules/{id}/match-data/camp-compare | GET | 获取阵营对比数据 |
| /schedules/{id}/match-data/squad-analysis | GET | 获取小队分析数据 |

#### 删除接口

| 接口 | 说明 |
|------|------|
| /schedules/{id}/match-data/report | 删除HTML报告导出 |

#### 响应格式

**indicators 响应：**
```json
{
  "items": [
    {
      "id": 1,
      "player_name": "玩家名",
      "profession": "玄机",
      "camp": "横戈",
      "kills": 21,
      "assists": 82,
      "deaths": 12,
      "kda": 8.58,
      "dps": 4693,
      "kill_ratio": 0.0523,
      ...
    }
  ],
  "camps": [...]
}
```

**camp-compare 响应：**
```json
{
  "camps": {
    "横戈": {"player_count": 59, "kills": 402, ...},
    "仗剑": {"player_count": 60, "kills": 380, ...}
  },
  "comparison": {
    "总击杀": {"横戈": 402, "仗剑": 380, "差值": 22, "波动值": 5.79},
    ...
  }
}
```

**squad-analysis 响应：**
```json
{
  "squads": [
    {
      "squad_name": "进攻1 第1队",
      "category": "进攻1",
      "team_index": 0,
      "members": [...],
      "totals": {"player_count": 6, "kills": 85, ...},
      "indicators": {"kda": 15.48, "dps": 2415, ...}
    }
  ]
}
```

### 6.2 后端实现要点

#### 新增函数

```python
def calculate_indicators(record: dict, team_totals: dict) -> dict:
    """计算单条记录的衍生指标（16项）"""
    ...

def get_team_totals(records: list[dict]) -> dict:
    """计算阵营汇总数据"""
    ...

async def get_camp_comparison(session, guild_id, schedule_id, round_no) -> dict:
    """获取阵营对比数据"""
    ...

async def get_squad_analysis(session, guild_id, schedule_id, round_no) -> dict:
    """获取小队维度分析数据"""
    ...
```

#### 扩展函数

```python
async def get_profession_stats(...) -> list[dict]:
    """扩展为17项指标"""
    ...
```

#### 删除函数

```python
async def generate_html_report(...) -> str:
    """删除 HTML 报告导出功能"""
```

#### 注意事项

- MatchData 模型没有 guild_id 字段，通过 schedule_id 关联
- 需要导入 
from app.models.lineup import Lineup
- 占比指标分母为整个阵营，不是单个小队

### 6.3 前端组件设计

#### 新增组件

| 组件 | 文件 | 功能 |
|------|------|------|
| IndicatorsTab.vue | 
frontend/src/components/match-data/ | 带指标的数据列表 |
| CampCompareTab.vue | 
frontend/src/components/match-data/ | 阵营对比（含图表） |
| SquadAnalysisTab.vue | 
frontend/src/components/match-data/ | 小队分析（含图表） |
| ProfessionDetailTab.vue | 
frontend/src/components/match-data/ | 职业深度分析（含图表） |

#### 修改组件

| 组件 | 修改内容 |
|------|---------|
| MatchDataTab.vue | 添加标签页、删除导出按钮 |
| OverviewTab.vue | 添加衍生指标卡片 |
| ProfessionTab.vue | 扩展为17项指标 |
| matchData.ts | 添加新API调用函数 |

#### 标签页结构

```
数据总览 | 数据列表 | 排行榜 | 阵营对比 | 小队分析 | 职业分析 | 综合评分
```

---

## 七、ECharts 图表规划

### 7.1 大盘维度可视化

#### 图表1：阵营击杀对比柱状图
```ypescript
{
  xAxis: { type: 'category', data: ['击杀', '助攻', '死亡', '破泉'] },
  yAxis: { type: 'value' },
  series: [
    { name: '我方', type: 'bar', data: [402, 5800, 320, 180] },
    { name: '敌方', type: 'bar', data: [380, 5600, 350, 165] }
  ]
}
```

#### 图表2：伤害分布饼图
```ypescript
{
  series: [{
    type: 'pie',
    data: [
      { name: '玩家伤害', value: 280000000 },
      { name: '建筑伤害', value: 45000000 },
      { name: '治疗', value: 95000000 }
    ]
  }]
}
```

#### 图表3：击杀占比条形图
```ypescript
{
  series: [{
    type: 'bar',
    data: [
      { name: '我方', value: 51.4 },
      { name: '敌方', value: 48.6 }
    ]
  }]
}
```

### 7.2 职业维度可视化

#### 图表4：职业人数分布饼图
```ypescript
{
  series: [{
    type: 'pie',
    data: [
      { name: '铁衣', value: 8 },
      { name: '血河', value: 6 },
      { name: '沧澜', value: 5 },
      { name: '龙吟', value: 7 },
      { name: '潮光', value: 6 },
      { name: '玄机', value: 5 },
      { name: '碎梦', value: 4 },
      { name: '神相', value: 5 },
      { name: '九灵', value: 4 },
      { name: '鸿音', value: 6 },
      { name: '素问', value: 4 }
    ]
  }]
}
```

#### 图表5：职业平均击杀柱状图
```ypescript
{
  xAxis: { type: 'category', data: ['铁衣', '血河', '沧澜', ...] },
  yAxis: { type: 'value' },
  series: [
    { name: '我方', type: 'bar', data: [2.5, 8.3, 6.2, ...] },
    { name: '敌方', type: 'bar', data: [2.8, 7.9, 5.8, ...] }
  ]
}
```

#### 图表6：职业平均伤害柱状图
```ypescript
{
  xAxis: { type: 'category', data: ['铁衣', '血河', '沧澜', ...] },
  yAxis: { type: 'value' },
  series: [
    { name: '我方', type: 'bar', data: [1200000, 4500000, 3200000, ...] },
    { name: '敌方', type: 'bar', data: [1100000, 4200000, 3000000, ...] }
  ]
}
```

#### 图表7：职业平均治疗柱状图（治疗职业）
```ypescript
{
  xAxis: { type: 'category', data: ['素问', '鸿音', '潮光'] },
  yAxis: { type: 'value' },
  series: [
    { name: '我方', type: 'bar', data: [8500000, 6200000, 950000] },
    { name: '敌方', type: 'bar', data: [8200000, 5800000, 900000] }
  ]
}
```

#### 图表8：职业平均承伤柱状图（承伤职业）
```ypescript
{
  xAxis: { type: 'category', data: ['铁衣', '血河', '沧澜'] },
  yAxis: { type: 'value' },
  series: [
    { name: '我方', type: 'bar', data: [12000000, 5500000, 7200000] },
    { name: '敌方', type: 'bar', data: [11500000, 5200000, 6800000] }
  ]
}
```

### 7.3 小队维度可视化

#### 图表9：小队击杀对比柱状图
```ypescript
{
  xAxis: { type: 'category', data: ['进攻1-1', '进攻1-2', '进攻1-3', '进攻2-1', ...] },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: [85, 72, 68, 90, ...] }]
}
```

#### 图表10：小队伤害对比柱状图
```ypescript
{
  xAxis: { type: 'category', data: ['进攻1-1', '进攻1-2', '进攻1-3', '进攻2-1', ...] },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: [25000000, 22000000, 20000000, 28000000, ...] }]
}
```

#### 图表11：小队塔伤贡献柱状图
```ypescript
{
  xAxis: { type: 'category', data: ['进攻1-1', '进攻1-2', '进攻1-3', '进攻2-1', ...] },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: [8500000, 7200000, 6800000, 9000000, ...] }]
}
```

#### 图表12：小队职业分布饼图（每个小队）
```ypescript
{
  series: [{
    type: 'pie',
    data: [
      { name: '铁衣', value: 1 },
      { name: '血河', value: 1 },
      { name: '碎梦', value: 2 },
      { name: '神相', value: 1 },
      { name: '素问', value: 1 }
    ]
  }]
}
```

### 7.4 玩家维度可视化

#### 图表13：玩家KDA分布散点图
```ypescript
{
  xAxis: { name: '击杀', type: 'value' },
  yAxis: { name: '死亡', type: 'value' },
  series: [{
    type: 'scatter',
    data: [
      [21, 12],  // [击杀, 死亡]
      [15, 8],
      [30, 6]
    ]
  }]
}
```

#### 图表14：玩家伤害-治疗气泡图
```ypescript
{
  xAxis: { name: '伤害', type: 'value' },
  yAxis: { name: '治疗', type: 'value' },
  series: [{
    type: 'scatter',
    symbolSize: (data) => Math.sqrt(data[2]) / 100,  // 气泡大小=承伤
    data: [
      [3189843, 0, 4196936],  // [伤害, 治疗, 承伤]
      [5136329, 125710, 6320362]
    ]
  }]
}
```

#### 图表15：玩家雷达图（综合能力）
```ypescript
{
  radar: {
    indicator: [
      { name: '击杀', max: 50 },
      { name: '助攻', max: 300 },
      { name: '伤害', max: 10000000 },
      { name: '治疗', max: 15000000 },
      { name: '承伤', max: 20000000 },
      { name: 'KDA', max: 15 }
    ]
  },
  series: [{
    type: 'radar',
    data: [{
      value: [21, 82, 3189843, 0, 4196936, 8.58],
      name: '玩家1'
    }]
  }]
}
```

### 7.5 图表集成方案

| 组件 | 图表 |
|------|------|
| OverviewTab | 阵营击杀对比柱状图、伤害分布饼图 |
| CampCompareTab | 双方指标对比柱状图、差值/波动值进度条 |
| SquadAnalysisTab | 小队击杀对比柱状图、伤害对比柱状图、塔伤贡献柱状图、职业分布饼图 |
| ProfessionDetailTab | 职业人数分布饼图、平均击杀/伤害/治疗/承伤柱状图 |

---

## 八、实施计划（已执行）

> 原六阶段实施计划已全部执行完毕（2026-08-26），结果见「十、实施记录」与 `progress.md` 更新记录。

---

## 九、已知问题与解决方案

### 9.1 模板字符串转义问题

**问题：** PowerShell Here-String 会转义模板字符串的反引号

**解决：** 使用正则表达式替换，或手动编写代码

### 9.2 Promise.all 错误处理

**问题：** 使用 Promise.all 时，任一请求失败会导致全部失败

**解决：** 使用 Promise.allSettled，或先加载基础数据再并行加载其他数据

### 9.3 MatchData 无 guild_id

**问题：** MatchData 模型没有 guild_id 字段

**解决：** 查询时只使用 schedule_id，不使用 guild_id

---

## 十、实施记录（2026-08-26 已完成）

> 按本方案完整重实施并完成；验证结果与口径确认如下。

### 已实现

- [x] 16 项衍生指标：`calculate_indicators()` + `get_camp_totals()`（backend/app/services/match_data_service.py）
- [x] 接口：`GET /schedules/{id}/match-data/indicators`、`/camp-compare`、`/squad-analysis`（backend/app/api/v1/match_data.py）
- [x] 职业深度：`get_profession_stats()` 扩展为 17 项指标（人数 + 16 项衍生指标均值），含分阵营均值与差值/波动值
- [x] 小队维度分析：按 `player_name + schedule_id` 关联排表（10 队 × 6 人），**仅分析我方阵营**（命中排表人数最多的阵营），未匹配归入「未排表」，敌方玩家不参与
- [x] 删除 HTML 报告导出：`generate_html_report()`、`/report` 接口、前端「导出报告」按钮全部移除
- [x] 前端：`IndicatorsTab.vue`（数据列表 + 指标列 + 排序）、`CampCompareTab.vue`（对比柱状图 + 差值/波动值进度条）、`SquadAnalysisTab.vue`（击杀/伤害/塔伤柱状图 + 职业分布饼图）、`ProfessionDetailTab.vue`（职业深度 17 项 + 对比图表）
- [x] 玩家维度图表：`PlayerAnalysis.vue` 补 KDA 散点、伤害-治疗气泡、综合雷达图；`OverviewTab.vue` 补伤害分布饼图
- [x] 自检脚本：`backend/scripts/selfcheck_indicators.py`（纯函数断言）；端到端验证当时使用临时脚本（`verify_e2e.py`），已不在仓库

### 验证状态

- [x] 16 项指标纯函数断言（含文档示例玩家）通过
- [x] FastAPI 应用导入冒烟通过
- [x] 端到端服务层验证（真实数据库副本）：240 条数据 → 指标交叉校验、阵营对比 11 项、小队分析仅含我方（10 组 + 我方未排表，敌方已排除）、11 个职业 × 17 项全部通过
- [x] 前端 `vue-tsc -b && vite build` 构建通过
- [ ] 与 Excel 逐值比对、页面视觉验收需人工在真实环境确认（本轮未做浏览器端截图验证）

### 口径确认（与需求方对齐）

- 拆塔/塔伤 = 对建筑伤害（building_damage），不含破塔卸甲
- 波动值 = 差值 ÷ min(我方, 敌方)（由样本 22/380 ≈ 5.79 反推）
- 清泉/羽化使用率仅用 revives（复活/清泉字段）
- 比赛时长固定 23 分钟（1380 秒）
- 职业深度为独立标签页；17 项 = 人数 + 16 项衍生指标均值
- 个人战绩名称关联（2026-09-20）：`match_data.player_name` 仍为比赛当时 ID，不改写；个人战绩/成员详情按经审核确认的改名关系合并新旧 ID 查询最近 10 场，指标公式、单局排名与阵营分母口径不变。冲突时停止自动合并（见 `design-game-id-change.md`）

---

*文档版本：v2.0*
*最后更新：2026-09-15（瘦身归档：移除过时状态/计划章节，修复代码块格式与残缺字符）*
