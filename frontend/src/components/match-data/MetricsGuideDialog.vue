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
          <p class="section-desc">纯前端计算，基于全队最大值归一化到 0~100 分，按职业类型差异化加权。</p>
          <h4 class="group-title">职业类型判定</h4>
          <el-table :data="roleTypes" size="small" border stripe>
            <el-table-column prop="name" label="类型" min-width="80" />
            <el-table-column prop="condition" label="判定条件" min-width="350" />
          </el-table>
          <h4 class="group-title">五维评分</h4>
          <el-table :data="scoreDims" size="small" border stripe>
            <el-table-column prop="name" label="维度" min-width="80" />
            <el-table-column prop="formula" label="计算公式" min-width="350" />
          </el-table>
          <h4 class="group-title">各职业权重</h4>
          <el-table :data="scoreWeights" size="small" border stripe>
            <el-table-column prop="type" label="职业类型" min-width="80" />
            <el-table-column prop="output" label="输出" min-width="55" align="center" />
            <el-table-column prop="building" label="建筑" min-width="55" align="center" />
            <el-table-column prop="healing" label="治疗" min-width="55" align="center" />
            <el-table-column prop="survival" label="生存" min-width="55" align="center" />
            <el-table-column prop="special" label="特殊" min-width="55" align="center" />
          </el-table>
          <h4 class="group-title">总分</h4>
          <p class="note"><code>总分 = 输出×W₁ + 建筑×W₂ + 治疗×W₃ + 生存×W₄ + 特殊×W₅</code></p>
          <h4 class="group-title">前端 KDA（散点图/雷达图专用）</h4>
          <p class="note">治疗职业（治疗量 > 伤害量）：助攻 ×0.8 折算、死亡 ×1.2 加重。</p>
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
const tab = ref('raw')

function open() {
  visible.value = true
  tab.value = 'raw'
}

defineExpose({ open })

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
  { name: 'KDA', formula: '(击杀 + 助攻) ÷ max(重伤, 1)', note: '保留 2 位小数' },
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

const roleTypes = [
  { name: '治疗', condition: '治疗量 ÷ 全队平均治疗量 ≥ 1' },
  { name: '进攻', condition: '(建筑伤害+破塔卸甲) ÷ 全队平均建筑伤害 ≥ 1' },
  { name: '防守', condition: '(玩家伤害+人伤卸甲) ÷ 全队平均玩家伤害 ≥ 1' },
  { name: '承伤', condition: '以上均不满足（默认）' },
]

const scoreDims = [
  { name: '输出', formula: '击杀得分×0.35 + 助攻得分×0.15 + 伤害得分×0.50' },
  { name: '建筑', formula: '(建筑伤害+破塔卸甲) ÷ 全场最大值 × 100' },
  { name: '治疗', formula: 'healing ÷ 全场最大healing × 100' },
  { name: '生存', formula: '承伤得分×0.40 + (1-死亡/max死亡)×100×0.60' },
  { name: '特殊', formula: '(清泉羽化得分 + 焚骨得分) ÷ 2' },
]

const scoreWeights = [
  { type: '治疗', output: 0, building: 0, healing: '0.50', survival: '0.30', special: '0.20' },
  { type: '承伤', output: '0.05', building: '0.05', healing: '0.05', survival: '0.75', special: '0.10' },
  { type: '进攻', output: '0.10', building: '0.60', healing: 0, survival: '0.25', special: '0.05' },
  { type: '防守', output: '0.75', building: '0.05', healing: 0, survival: '0.10', special: '0.10' },
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
