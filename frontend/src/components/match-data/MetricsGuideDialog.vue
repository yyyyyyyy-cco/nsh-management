<template>
  <el-dialog
    v-model="visible"
    title="数据指标说明"
    width="820px"
    top="4vh"
    destroy-on-close
  >
    <div class="guide">
      <el-tabs v-model="tab" class="guide-tabs">
        <!-- CSV 原始字段 -->
        <el-tab-pane label="原始字段" name="raw">
          <p class="section-desc">CSV 导入的原始数据字段，直接存储于数据库。</p>
          <el-table :data="rawFields" size="small" border stripe>
            <el-table-column prop="name" label="字段" min-width="120" />
            <el-table-column prop="csv" label="CSV 列名" min-width="110" />
            <el-table-column prop="desc" label="说明" min-width="260" />
          </el-table>
        </el-tab-pane>

        <!-- 衍生指标 -->
        <el-tab-pane label="衍生指标" name="derived">
          <p class="section-desc">基于原始字段计算的 16 项指标，计算基准时长 = <b>23 分钟</b>（固定比赛时长）。</p>

          <h4 class="group-title">效率指标</h4>
          <el-table :data="efficiencyFields" size="small" border stripe>
            <el-table-column prop="name" label="指标" min-width="120" />
            <el-table-column prop="formula" label="计算公式" min-width="300" />
            <el-table-column prop="note" label="说明" min-width="200" />
          </el-table>

          <h4 class="group-title">生存指标</h4>
          <el-table :data="survivalFields" size="small" border stripe>
            <el-table-column prop="name" label="指标" min-width="120" />
            <el-table-column prop="formula" label="计算公式" min-width="300" />
            <el-table-column prop="note" label="说明" min-width="200" />
          </el-table>

          <h4 class="group-title">占比指标</h4>
          <p class="note">分母 = 该玩家所属<b>整个阵营</b>的对应汇总值。</p>
          <el-table :data="ratioFields" size="small" border stripe>
            <el-table-column prop="name" label="指标" min-width="120" />
            <el-table-column prop="formula" label="计算公式" min-width="300" />
          </el-table>

          <h4 class="group-title">技能指标</h4>
          <el-table :data="skillFields" size="small" border stripe>
            <el-table-column prop="name" label="指标" min-width="120" />
            <el-table-column prop="formula" label="计算公式" min-width="300" />
            <el-table-column prop="note" label="说明" min-width="200" />
          </el-table>
        </el-tab-pane>

        <!-- 阵营对比 -->
        <el-tab-pane label="阵营对比" name="camp">
          <p class="section-desc">两阵营汇总值的差值与波动分析。</p>
          <el-table :data="campFields" size="small" border stripe>
            <el-table-column prop="name" label="派生值" min-width="100" />
            <el-table-column prop="formula" label="计算公式" min-width="350" />
          </el-table>
        </el-tab-pane>

        <!-- 小队分析 -->
        <el-tab-pane label="小队分析" name="squad">
          <p class="section-desc">仅分析我方阵营，按 player_name 精确匹配排表，敌方不参与。</p>
          <h4 class="group-title">小队汇总（totals）</h4>
          <p class="note">队员原始字段的 SUM（击杀、助攻、伤害、治疗、承伤等）。</p>
          <h4 class="group-title">小队均值指标（indicators）</h4>
          <p class="note">队员单人衍生指标的 AVG（KDA、秒伤、每死承伤等 9 项）。</p>
          <h4 class="group-title">我方阵营判定</h4>
          <p class="note">哪个阵营的玩家命中排表人数最多 → 该阵营为我方。</p>
        </el-tab-pane>

        <!-- 职业深度 -->
        <el-tab-pane label="职业深度" name="profession">
          <p class="section-desc">按职业分组，统计 17 项指标均值 + 分阵营对比。</p>
          <h4 class="group-title">17 项指标</h4>
          <p class="note">人数 + 16 项衍生指标的<b>职业级均值</b>（该职业所有玩家的 AVG）。</p>
          <h4 class="group-title">差值 / 波动值</h4>
          <el-table :data="campFields" size="small" border stripe>
            <el-table-column prop="name" label="派生值" min-width="100" />
            <el-table-column prop="formula" label="计算公式" min-width="350" />
          </el-table>
          <p class="note" style="margin-top: 8px;">对比维度：平均击杀、平均伤害、平均塔伤、平均治疗、平均承伤、平均 KDA。</p>
        </el-tab-pane>

        <!-- 综合评分 -->
        <el-tab-pane label="综合评分" name="score">
          <p class="section-desc">贡献倍数法（纯前端计算）：评分 = Σ 权重×(个人指标 ÷ 本轮同职业分路均值)×100 − 15×重伤倍数。100 分 = 达到本轮同职业(分路)平均贡献水平，扣除重伤惩罚后的期望基准为 85 分。</p>
          <h4 class="group-title">职业分路判定</h4>
          <el-table :data="archRules" size="small" border stripe>
            <el-table-column prop="name" label="职业" min-width="80" />
            <el-table-column prop="condition" label="判定条件" min-width="380" />
          </el-table>
          <h4 class="group-title">权重推导规则（rs = 该职业指标均值 ÷ 全体均值，基于 1440 条历史数据）</h4>
          <el-table :data="weightRules" size="small" border stripe>
            <el-table-column prop="name" label="层级" min-width="70" />
            <el-table-column prop="condition" label="条件" min-width="130" />
            <el-table-column prop="note" label="说明" min-width="280" />
          </el-table>
          <h4 class="group-title">各职业(分路)权重（正向和 = 1.0，— 表示不计分）</h4>
          <el-table :data="scoreWeightRows" size="small" border stripe>
            <el-table-column prop="prof" label="职业(分路)" min-width="90" />
            <el-table-column v-for="m in scoreMetrics" :key="m" :prop="m" :label="m" min-width="52" align="center" />
          </el-table>
          <h4 class="group-title">重伤负向与边界处理</h4>
          <p class="note">重伤每高出同职业均值 1 倍扣 15 分；本轮内某指标全组为 0（无数据）时，该项权重按比例摊给其余指标，保证基准恒为 100。未知职业兜底：击杀/人伤各半。</p>
          <h4 class="group-title">KDA 加权规则（前后端统一）</h4>
          <p class="note">辅助型（治疗职业：治疗量 > 伤害量；或坦克职业铁衣）：助攻 ×0.8 折算、死亡 ×1.2 加重（仅影响 KDA）。</p>
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import { PROFESSION_WEIGHTS, SCORE_METRICS } from './analysis'

const visible = ref(false)
const tab = ref('raw')

function open() {
  visible.value = true
  tab.value = 'raw'
}

defineExpose({ open })

const scoreMetrics = SCORE_METRICS

const archRules = [
  { name: '潮光', condition: '建筑折算（建筑伤害+破塔卸甲×0.7）≥ 人伤折算（玩家伤害+人伤卸甲）→ 拆塔路；否则输出路' },
  { name: '鸿音', condition: '治疗量 > 建筑折算 → 治疗路；否则拆塔路' },
  { name: '其他职业', condition: '职业即分路，无需判定' },
]

const weightRules = [
  { name: '核心', condition: 'rs ≥ 1.5', note: '占 85% 份额，按 rs 占比分配；复活/焚骨稀缺指标权重 cap 0.30' },
  { name: '次要', condition: '1.0 ≤ rs < 1.5', note: '合计 15% 份额均分' },
  { name: '边际', condition: '0.5 ≤ rs < 1 且职业内非零占比 ≥ 50%', note: '每项 0.05，且贡献倍数封顶 2.0（防止小均值指标倍数爆炸）' },
  { name: '归一化', condition: '—', note: '正向权重和归一化到 1.0' },
]

const scoreWeightRows = Object.entries(PROFESSION_WEIGHTS).map(([prof, w]) => ({
  prof,
  ...Object.fromEntries(SCORE_METRICS.map((m) => [m, w[m] > 0 ? String(w[m]) : '—'])),
}))

const rawFields = [
  { name: 'player_name', csv: '玩家名字', desc: '玩家 ID' },
  { name: 'profession', csv: '职业', desc: '职业名' },
  { name: 'camp', csv: '区块标题', desc: '阵营名，第一个区块 = 己方' },
  { name: 'kills', csv: '击败/清泉', desc: '击败 + 清泉合计（CSV "15/3" → kills=18, springs=3）' },
  { name: 'springs', csv: '击败/清泉', desc: '清泉原始分量' },
  { name: 'assists', csv: '助攻', desc: '助攻数' },
  { name: 'player_damage', csv: '对玩家伤害', desc: '玩家伤害' },
  { name: 'armor_break_damage', csv: '人伤卸甲', desc: '人伤卸甲值' },
  { name: 'building_damage', csv: '对建筑伤害', desc: '建筑伤害（= 拆塔）' },
  { name: 'tower_break_damage', csv: '破塔卸甲', desc: '破塔卸甲值' },
  { name: 'healing', csv: '治疗值', desc: '治疗量' },
  { name: 'damage_taken', csv: '承受伤害', desc: '承伤量' },
  { name: 'deaths', csv: '重伤', desc: '重伤 = 死亡数' },
  { name: 'revives', csv: '复活/清泉', desc: '清泉羽化次数' },
  { name: 'fen_gu', csv: '焚骨', desc: '焚骨次数' },
]

const efficiencyFields = [
  { name: 'KDA', formula: '(击杀 + 助攻) ÷ max(重伤, 1)', note: '保留 2 位小数；辅助型按下方加权规则折算' },
  { name: '秒伤 (dps)', formula: '(玩家伤害 + 建筑伤害) ÷ 1380 秒', note: '取整' },
  { name: '参与击杀均伤', formula: '总伤害 ÷ max(击杀+助攻, 1)', note: '取整' },
]

const survivalFields = [
  { name: '每死输出值', formula: '总伤害 ÷ max(死亡, 1)', note: '取整' },
  { name: '每死承伤', formula: '承伤 ÷ max(死亡, 1)', note: '取整' },
  { name: '每死治疗量', formula: '治疗 ÷ max(死亡, 1)', note: '取整' },
  { name: '治疗转化率', formula: '每死治疗量 ÷ max(每死承伤, 1)', note: '保留 2 位小数' },
]

const ratioFields = [
  { name: '击杀占比', formula: '个人击杀 ÷ 阵营总击杀' },
  { name: '助攻占比', formula: '个人助攻 ÷ 阵营总助攻' },
  { name: '人伤占比', formula: '个人玩家伤害 ÷ 阵营总玩家伤害' },
  { name: '拆塔占比', formula: '个人建筑伤害 ÷ 阵营总建筑伤害' },
  { name: '承伤占比', formula: '个人承伤 ÷ 阵营总承伤' },
  { name: '死亡占比', formula: '个人死亡 ÷ 阵营总死亡' },
  { name: '治疗占比', formula: '个人治疗 ÷ 阵营总治疗' },
]

const skillFields = [
  { name: '清泉羽化率', formula: '清泉羽化次数 ÷ 23（分钟）', note: '次/分钟，保留 2 位' },
  { name: '焚骨率', formula: '焚骨次数 ÷ 23（分钟）', note: '次/分钟，保留 2 位' },
]

const campFields = [
  { name: '差值', formula: '我方值 - 敌方值' },
  { name: '波动值', formula: '|差值| ÷ min(我方值, 敌方值) × 100%' },
]
</script>

<style scoped>
.guide {
  max-height: 72vh;
  overflow-y: auto;
  padding-right: 4px;
}

.guide-tabs :deep(.el-tabs__header) {
  margin-bottom: 12px;
}

.section-desc {
  font-size: 13px;
  color: var(--ink-600);
  margin-bottom: 12px;
  line-height: 1.6;
}

.group-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink-800);
  margin: 16px 0 8px;
  padding-left: 8px;
  border-left: 3px solid var(--gold-500);
}

.note {
  font-size: 12px;
  color: var(--ink-500);
  margin-bottom: 8px;
  line-height: 1.6;
}

.note code {
  background: var(--ink-bg-wash);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}
</style>
