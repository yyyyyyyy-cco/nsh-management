<template>
  <div class="lineup-editor">
    <div class="toolbar">
      <div class="stat">
        已排 <em class="num">{{ board.placedCount.value }}</em> / 60 槽位
        <el-progress
          :percentage="Math.round((board.placedCount.value / 60) * 100)"
          :stroke-width="6"
          :show-text="false"
          class="stat-bar"
        />
        <span class="stat-sub">候选池 {{ board.candidates.value.length }} 人</span>
      </div>
      <el-tag
        class="title-remark-tag"
        :type="board.titleRemark.value ? 'warning' : 'info'"
        effect="light"
        :closable="false"
        @click="board.editTitleRemark()"
      >
        {{ board.titleRemark.value || '标题备注' }}
      </el-tag>
      <span v-if="board.autoSaveStatus.value !== 'idle'" class="auto-save" :class="board.autoSaveStatus.value">
        <template v-if="board.autoSaveStatus.value === 'pending'">● 待保存</template>
        <template v-else-if="board.autoSaveStatus.value === 'saving'">◉ 保存中</template>
        <template v-else>✓ 已保存</template>
      </span>
      <el-radio-group v-model="board.mode.value" size="small" class="mode-switch" @change="onModeChange">
        <el-radio-button value="drag">拖拽</el-radio-button>
        <el-radio-button value="input">输入</el-radio-button>
      </el-radio-group>
      <div class="spacer" />
      <el-button :icon="Download" @click="importVisible = true">导入历史排表</el-button>
      <el-button :loading="board.saving.value" type="primary" :icon="Check" @click="onSave">保存排表</el-button>
    </div>

    <div v-loading="board.loading.value" class="editor">
      <div class="pool" :class="{ 'pool--open': poolOpen }">
        <div class="panel-title">
          <span class="panel-title__dot" />
          帮众候选池
          <el-icon class="pool-close" @click="poolOpen = false"><Close /></el-icon>
        </div>
        <el-input
          v-model="poolKeyword"
          size="small"
          placeholder="搜索成员"
          clearable
          :prefix-icon="Search"
          class="pool-search"
        />
        <div v-for="[prof, list] in filteredPoolGroups" :key="prof" class="prof-group">
          <div class="prof-group__label" :style="{ color: profColor(prof) }" @click="toggleProf(prof)">
            <el-icon class="collapse-arrow" :class="{ expanded: !collapsedProfs.has(prof) }"><ArrowRight /></el-icon>
            {{ prof }} <em class="num">{{ list.length }}</em>
          </div>
          <draggable v-show="!collapsedProfs.has(prof)" :list="list" group="lineup" item-key="key" class="pool-list" :animation="150" ghost-class="pool-ghost" :disabled="board.mode.value === 'input'" @start="(evt: any) => board.onPoolDragStart(evt)" @end="board.onDragEnd" @change="board.onCandidateChange">
            <template #item="{ element }">
              <div class="pool-item" :data-key="element.key" @click="onPoolItemClick(element)">
                <span class="prof-dot" :style="{ background: profColor(element.profession) }" />
                <span class="name">{{ element.member_name }}</span>
                <el-tag v-if="element.member_status === 'filler'" size="small" type="warning" effect="light">补</el-tag>
                <el-tag v-else-if="element.member_status === 'substitute'" size="small" type="info" effect="plain">替</el-tag>
              </div>
            </template>
          </draggable>
        </div>
        <div v-if="!filteredPoolGroups.length" class="pool-empty">
          <el-icon class="pool-empty__icon"><User /></el-icon>
          <span>{{ board.candidates.value.length ? '没有匹配的成员' : '暂无可用成员' }}</span>
        </div>
      </div>

      <div class="teams">
        <div v-for="group in teamGroups" :key="group.category" class="team-row" :class="`team-row--${group.type}`">
          <div class="team-row__header">
            <span class="team-row__label">{{ group.label }}</span>
            <el-tag
              class="group-remark-tag"
              :type="board.groupsRemark.value[group.category] ? 'warning' : 'info'"
              effect="light"
              size="small"
              @click="board.editGroupRemark(group.category)"
            >
              {{ board.groupsRemark.value[group.category] || '备注' }}
            </el-tag>
          </div>
          <div v-for="team in group.teams" :key="team.category + team.team_index" class="team" :class="`team--${teamKey(team.category)}`">
            <div class="team-title">
              <span class="team-title__index num">{{ team.team_index + 1 }}</span>
              <span>{{ team.category }} {{ team.team_index + 1 }} 队</span>
            </div>
            <div class="slots">
              <draggable
                v-for="(box, si) in team.slots"
                :key="si"
                :list="box"
                group="lineup"
                item-key="key"
                class="slot"
                :animation="150"
                :disabled="board.mode.value === 'input'"
                @start="(evt: any) => board.onSlotDragStart(evt, team, si)"
                @end="board.onDragEnd"
                @change="(evt: any) => onSlotChangeWithBounce(evt, team, si)"
              >
                <template #item="{ element }">
                  <div v-if="isEditing(team, si)" :data-key="element.key" class="slot-card slot-card--edit">
                    <el-input
                      v-model="inputName"
                      size="small"
                      placeholder="输入姓名"
                      autofocus
                      class="slot-input"
                      @keyup.enter="onInputEnter"
                      @keyup.esc="cancelInput"
                      @blur="onInputBlur"
                    />
                  </div>
                  <div v-else :data-key="element.key" class="slot-card" :class="{ filled: element.member_name }" @click="onSlotClick(team, si)" @dblclick="board.editRemark(team, si)">
                    <span v-if="element.member_name" class="slot-prof-dot" :style="{ background: profColor(element.profession) }" />
                    <span v-if="element.member_name" class="slot-name">{{ element.member_name }}</span>
                    <span v-else-if="board.mode.value === 'input'" class="slot-name slot-name--hint">点击输入</span>
                    <el-tag
                      v-if="element.member_name && element.profession"
                      size="small"
                      class="slot-prof-tag"
                      :style="{ color: profColor(element.profession), borderColor: profColor(element.profession) }"
                    >
                      {{ element.profession }}
                    </el-tag>
                    <el-tooltip :content="element.remark ? '编辑备注：' + element.remark : '添加备注'" placement="top">
                      <el-icon class="remark-icon" :class="{ 'has-remark': !!element.remark }" @click.stop="board.editRemark(team, si)">
                        <EditPen />
                      </el-icon>
                    </el-tooltip>
                    <el-icon
                      v-if="element.member_name"
                      class="slot-remove"
                      @click.stop="onRemoveSlotClick(team, si)"
                    >
                      <Close />
                    </el-icon>
                  </div>
                </template>
              </draggable>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 窄屏：候选池浮动小球 + 遮罩（点击小球展开候选池浮层） -->
    <div class="pool-fab" @click="poolOpen = true">
      <el-icon class="pool-fab__icon"><User /></el-icon>
      <span class="pool-fab__count num">{{ board.candidates.value.length }}</span>
    </div>
    <div v-if="poolOpen" class="pool-mask" @click="poolOpen = false" />

    <ImportHistoryDialog v-model="importVisible" :schedule-id="scheduleId" @imported="onImported" />
    <MatchConfirmDialog
      v-model="matchVisible"
      :matches="matchResults"
      :keyword="matchKeyword"
      @confirm="onMatchConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ArrowRight, Check, Close, Download, EditPen, Search, User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import draggable from 'vuedraggable'

import { useLineupBoard, type CandidateItem, type TeamBox } from '@/composables/lineupBoard'
import ImportHistoryDialog from './ImportHistoryDialog.vue'
import MatchConfirmDialog from './MatchConfirmDialog.vue'

const props = defineProps<{ scheduleId: number }>()
const emit = defineEmits<{ saved: [] }>()

const board = useLineupBoard(props.scheduleId)
const importVisible = ref(false)

// ===== 输入模式：槽位点击输入 → 候选池匹配 → 确认填入 =====
/** 当前编辑中的槽位（输入模式）。 */
const editingSlot = ref<{ team: TeamBox; si: number } | null>(null)
const inputName = ref('')
const matchVisible = ref(false)
const matchKeyword = ref('')
const matchResults = ref<CandidateItem[]>([])

function isEditing(team: TeamBox, si: number) {
  return editingSlot.value?.team === team && editingSlot.value?.si === si
}

/** 输入模式下点击槽位进入编辑态。 */
function onSlotClick(team: TeamBox, si: number) {
  if (board.mode.value !== 'input') return
  editingSlot.value = { team, si }
  inputName.value = ''
}

/** 槽位放入后触发弹跳动画 */
function onSlotChangeWithBounce(evt: any, team: TeamBox, si: number) {
  board.onSlotChange(evt, team, si)
  if (evt.added) {
    // 找到目标槽位的 DOM 元素，添加临时动画 class
    const slotEls = document.querySelectorAll(`.team--${teamKey(team.category)} .slot`)
    const slotEl = slotEls[si]
    if (slotEl) {
      const card = slotEl.querySelector('.slot-card')
      if (card) {
        card.classList.remove('slot-bounce')
        // 强制 reflow 以重新触发动画
        void (card as HTMLElement).offsetWidth
        card.classList.add('slot-bounce')
        card.addEventListener('animationend', () => card.classList.remove('slot-bounce'), { once: true })
      }
    }
  }
}

function cancelInput() {
  editingSlot.value = null
  inputName.value = ''
}

/** 失焦取消编辑（点击候选池条目或匹配确认框导致的失焦除外）。 */
function onInputBlur(e: FocusEvent) {
  if (matchVisible.value) return
  const target = e.relatedTarget as HTMLElement | null
  if (target?.closest('.pool, .el-overlay')) return
  cancelInput()
}

/** 回车触发候选池匹配。 */
function onInputEnter() {
  const slot = editingSlot.value
  const kw = inputName.value.trim()
  if (!slot || !kw) return
  const matches = board.matchCandidates(kw)
  if (!matches.length) {
    ElMessage.warning(`候选池中未匹配到「${kw}」`)
    return
  }
  matchKeyword.value = kw
  matchResults.value = matches
  matchVisible.value = true
}

/** 确认填入：与拖拽一致（原成员回池、候选池剔除、自动保存）。 */
function onMatchConfirm(item: CandidateItem) {
  const slot = editingSlot.value
  if (slot) board.fillSlotByInput(slot.team, slot.si, item)
  cancelInput()
}

/** 切换模式时退出编辑态。 */
function onModeChange() {
  cancelInput()
}

// 匹配框被取消关闭时，同样退出槽位编辑态
watch(matchVisible, (v) => {
  if (!v) cancelInput()
})

// ===== 候选池搜索过滤（输入模式下点击条目可直接填入当前编辑槽位）=====
const poolKeyword = ref('')
const poolOpen = ref(false) // 窄屏候选池浮层开关（桌面端不生效）

const filteredPoolGroups = computed(() => {
  const kw = poolKeyword.value.trim().toLowerCase()
  if (!kw) return board.professionGroups.value
  return board.professionGroups.value
    .map(([prof, list]) => [prof, list.filter((c) => c.member_name.toLowerCase().includes(kw))] as [string, CandidateItem[]])
    .filter(([, list]) => list.length > 0)
})

/** 输入模式下点击候选池条目：直接填入当前编辑中的槽位。 */
function onPoolItemClick(item: CandidateItem) {
  if (board.mode.value !== 'input') return
  const slot = editingSlot.value
  if (!slot) {
    ElMessage.info('请先点击一个槽位，再选择要填入的成员')
    return
  }
  board.fillSlotByInput(slot.team, slot.si, item)
  cancelInput()
}

/** 候选池职业折叠状态：记录已折叠的职业（默认全部展开）。 */
const collapsedProfs = ref(new Set<string>())

function toggleProf(prof: string) {
  if (collapsedProfs.value.has(prof)) {
    collapsedProfs.value.delete(prof)
    collapsedProfs.value = new Set(collapsedProfs.value)
  } else {
    collapsedProfs.value.add(prof)
    collapsedProfs.value = new Set(collapsedProfs.value)
  }
}

// 自动保存完成后通知父级刷新总览
watch(
  () => board.autoSaveStatus.value,
  (status) => {
    if (status === 'saved') emit('saved')
  },
)

/** 职业色映射。 */
const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

function profColor(prof: string) {
  return PROF_COLORS[prof] || '#c9a13b'
}

function teamKey(category: string) {
  return category.startsWith('进攻') ? 'attack' : 'defense'
}

/** 按组分行：进攻1/进攻2 每行 3 队，防守1/防守2 每行 2 队。 */
const teamGroups = computed(() => {
  const order = ['进攻1', '进攻2', '防守1', '防守2']
  const map = new Map<string, TeamBox[]>()
  for (const t of board.teams.value) {
    if (!map.has(t.category)) map.set(t.category, [])
    map.get(t.category)!.push(t)
  }
  return order
    .filter((c) => map.has(c))
    .map((c) => ({
      category: c,
      type: c.startsWith('进攻') ? 'attack' : 'defense',
      label: c === '进攻1' ? '进攻一' : c === '进攻2' ? '进攻二' : c === '防守1' ? '防守一' : '防守二',
      teams: map.get(c)!.sort((a, b) => a.team_index - b.team_index),
    }))
})

async function onSave() {
  await board.onSave()
  emit('saved')
}

/** 移除槽位成员：确认后再从排表下掉。 */
async function onRemoveSlotClick(team: TeamBox, si: number) {
  const name = team.slots[si][0]?.member_name
  if (!name) return
  await ElMessageBox.confirm(`确定将「${name}」从排表中移除吗？`, '移除确认', { type: 'warning' })
  board.onRemoveSlot(team, si)
}

/** 历史排表导入成功后：刷新编辑器数据并通知父级刷新总览。 */
function onImported() {
  board.load()
  emit('saved')
}

defineExpose({ reload: () => board.load() })

onMounted(() => board.load())
</script>

<style scoped>
/* ===== 填表模式切换 ===== */
.mode-switch {
  margin-left: 12px;
  flex-shrink: 0;
}

/* ===== 输入模式：槽位编辑态与提示 ===== */
.slot-card--edit {
  padding: 4px 6px;
  cursor: default;
}

.slot-input :deep(.el-input__wrapper) {
  padding: 1px 8px;
}

.slot-name--hint {
  color: var(--ink-300);
  font-weight: 400;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--ink-500);
  font-size: 13px;
  margin-right: auto;
}

.stat em {
  font-style: normal;
  font-weight: 800;
  color: var(--gold-700);
  font-size: 16px;
}

.stat-bar {
  width: 160px;
}

.stat-sub {
  color: var(--ink-400);
  font-size: 12px;
}

.auto-save {
  font-size: 12px;
  white-space: nowrap;
  padding: 2px 10px;
  border-radius: var(--radius-xl);
}

.auto-save.pending {
  color: var(--gold-700);
  background: var(--gold-100);
}

.auto-save.saving {
  color: var(--gold-700);
  background: var(--gold-100);
  animation: auto-save-pulse 1s ease-in-out infinite;
}

.auto-save.saved {
  color: var(--jade);
  background: var(--el-color-success-light-9);
  animation: save-flash 0.6s ease-out;
}

@keyframes save-flash {
  0% { box-shadow: 0 0 0 0 rgba(46, 139, 87, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(46, 139, 87, 0); }
  100% { box-shadow: 0 0 0 0 rgba(46, 139, 87, 0); }
}

@keyframes auto-save-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.55;
  }
}

/* ===== 标题备注 + 团备注标签（紧凑行内） ===== */
.title-remark-tag {
  cursor: pointer;
  user-select: none;
  flex-shrink: 0;
  font-size: 13px;
  padding: 2px 12px;
  height: auto;
}

.title-remark-tag .el-tag__content {
  font-size: 13px;
}

.title-remark-tag.is-warning {
  --el-tag-bg-color: var(--gold-50);
  border-color: var(--gold-300);
  color: var(--gold-700);
}

.title-remark-tag.is-info {
  --el-tag-bg-color: var(--ink-bg-wash);
  border-color: var(--edge-soft);
  color: var(--ink-500);
}

.team-row__header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 12px;
  margin-bottom: 10px;
  grid-column: 1 / -1;
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--gold-50) 0%, var(--ink-bg-paper) 100%);
}

.team-row--defense .team-row__header {
  border-color: #c8d6e5;
  background: linear-gradient(135deg, #eef3f8 0%, var(--ink-bg-paper) 100%);
}

.team-row__label {
  font-weight: 700;
  font-size: 13px;
  color: var(--ink-700);
  letter-spacing: 2px;
}

.group-remark-tag {
  cursor: pointer;
  user-select: none;
  font-size: 11px;
  line-height: 1.6;
}

.group-remark-tag.is-warning {
  --el-tag-bg-color: var(--gold-50);
  border-color: var(--gold-300);
  color: var(--gold-700);
}

.group-remark-tag.is-info {
  --el-tag-bg-color: var(--ink-bg-wash);
  border-color: var(--edge-soft);
  color: var(--ink-500);
}

/* ===== 工具栏 ===== */
.toolbar .spacer {
  flex: 1;
}

/* ===== 编辑区 ===== */
.editor {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

/* 候选池 */
.pool {
  width: 224px;
  flex-shrink: 0;
  border: 1px solid var(--edge-strong);
  border-radius: var(--radius-lg);
  padding: 12px;
  background: var(--ink-bg-cream);
  max-height: 480px;
  overflow: auto;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  color: var(--gold-700);
  margin-bottom: 10px;
  font-size: 13px;
  letter-spacing: 1px;
}

.panel-title__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--gold-gradient);
}

.pool-search {
  margin-bottom: 10px;
}

.prof-group {
  margin-bottom: 10px;
}

.prof-group__label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 5px;
  letter-spacing: 1px;
  cursor: pointer;
  user-select: none;
}

.collapse-arrow {
  font-size: 11px;
  transition: transform var(--dur-fast);
}

.collapse-arrow.expanded {
  transform: rotate(90deg);
}

.prof-group__label em {
  font-style: normal;
  font-weight: 600;
  opacity: 0.7;
}

.pool-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--ink-300);
  font-size: 12px;
  padding: 24px 0;
}

.pool-empty__icon {
  font-size: 26px;
  opacity: 0.5;
}

.pool-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  margin-bottom: 6px;
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-md);
  cursor: grab;
  transition: border-color var(--dur-fast), box-shadow var(--dur-fast), transform var(--dur-fast);
}

.pool-item:hover {
  border-color: var(--gold-300);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.pool-item:active {
  cursor: grabbing;
}

/* 拖拽幽灵占位样式 */
.pool-ghost {
  opacity: 0.4;
  border-style: dashed;
}

.prof-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.pool-item .name {
  font-weight: 500;
  color: var(--ink-900);
  font-size: 13px;
}

.pool-item .meta {
  color: var(--ink-400);
  font-size: 11px;
  margin-left: auto;
}

/* 队伍区域：按组分行（进攻 3 队/行，防守 2 队/行） */
.teams {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 480px;
  overflow: auto;
}

.team-row {
  display: grid;
  gap: 12px;
}

.team-row--attack {
  grid-template-columns: repeat(3, minmax(165px, 1fr));
}

.team-row--defense {
  grid-template-columns: repeat(2, minmax(165px, 1fr));
}

.team {
  border-radius: var(--radius-lg);
  padding: 12px;
  transition: box-shadow var(--dur-normal);
}

.team--attack {
  background: linear-gradient(180deg, #fdf8ec 0%, var(--ink-bg-paper) 80%);
  border: 1px solid var(--gold-200);
}

.team--defense {
  background: linear-gradient(180deg, #f2f5f8 0%, var(--ink-bg-paper) 80%);
  border: 1px solid #d5dfe8;
}

.team-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  color: var(--ink-700);
  font-size: 13px;
  margin-bottom: 10px;
}

.team--attack .team-title {
  color: var(--gold-700);
}

.team--defense .team-title {
  color: var(--indigo);
}

.team-title__index {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--gold-gradient);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.team--defense .team-title__index {
  background: linear-gradient(135deg, #7b9cc0, var(--indigo));
}

.slots {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.slot {
  height: 44px;
  min-height: 44px;
  overflow: hidden;
  border: 1px dashed var(--edge-strong);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 248, 0.7);
  transition: border-color var(--dur-fast), background var(--dur-fast);
}

.slot:hover {
  border-color: var(--gold-400);
  background: var(--gold-50);
}

.slot-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  font-size: 13px;
  border-radius: var(--radius-sm);
  cursor: grab;
  transition: transform var(--dur-fast), box-shadow var(--dur-fast);
}

.slot-card:active {
  cursor: grabbing;
}

.slot-card.filled {
  background: linear-gradient(135deg, #f6ecd0 0%, #f3e6c4 100%);
  border-left: 3px solid var(--gold-400);
  color: var(--gold-700);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.slot-card.filled:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 槽位放入反馈：弹跳 + 金光闪烁 */
.slot-card.slot-bounce {
  animation: slot-bounce 0.35s var(--ease-out);
}

@keyframes slot-bounce {
  0% { transform: scale(1); box-shadow: var(--shadow-sm); }
  40% { transform: scale(1.06); box-shadow: 0 0 0 3px rgba(201, 161, 59, 0.35), var(--shadow-md); }
  100% { transform: scale(1); box-shadow: var(--shadow-sm); }
}

.slot-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.slot-prof-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.slot-prof-tag {
  flex-shrink: 0;
  font-size: 11px;
  line-height: 16px;
  height: 18px;
  padding: 0 5px;
  background: transparent;
  border: 1px solid;
}

.remark-icon {
  color: var(--gold-400);
  cursor: pointer;
  flex-shrink: 0;
  font-size: 14px;
  transition: color var(--dur-fast), transform var(--dur-fast);
}

.remark-icon:hover {
  color: var(--gold-600);
  transform: scale(1.15);
}

.remark-icon.has-remark {
  color: var(--gold-600);
}

.slot-remove {
  color: var(--ink-400);
  cursor: pointer;
  flex-shrink: 0;
  font-size: 13px;
  border-radius: 50%;
  transition: all var(--dur-fast);
}

.slot-remove:hover {
  color: var(--cinnabar);
  background: var(--el-color-danger-light-9);
}

/* ===== 候选池浮球/遮罩（默认隐藏，仅窄屏显示） ===== */
.pool-close {
  display: none;
}

.pool-fab {
  display: none;
}

.pool-mask {
  display: none;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }

  .stat {
    width: 100%;
    margin-right: 0;
  }

  .stat-bar {
    width: 120px;
  }

  .auto-save {
    order: 3;
  }

  /* 编辑区纵向堆叠：候选池在上，队伍区在下 */
  .editor {
    flex-direction: column;
    gap: 12px;
  }

  /* 候选池：窄屏改为浮动小球 + 展开浮层（视口居中） */
  .pool {
    display: none;
    width: calc(100vw - 24px);
    max-width: 420px;
    max-height: 70vh;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 1001;
    box-shadow: var(--shadow-lg);
  }

  .pool.pool--open {
    display: block;
  }

  .pool-close {
    display: inline-flex;
    margin-left: auto;
    cursor: pointer;
    color: var(--ink-500);
    font-size: 15px;
  }

  .pool-close:hover {
    color: var(--cinnabar);
  }

  .pool-fab {
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    right: 16px;
    bottom: 24px;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #fdf6e3 0%, #f0e0a8 100%);
    border: 1px solid var(--gold-300);
    color: var(--gold-700);
    box-shadow: 0 4px 14px -2px rgba(201, 161, 59, 0.3);
    cursor: pointer;
    z-index: 1002;
  }

  .pool-fab__icon {
    font-size: 22px;
  }

  .pool-fab__count {
    position: absolute;
    top: -4px;
    right: -4px;
    min-width: 20px;
    height: 20px;
    line-height: 20px;
    padding: 0 5px;
    border-radius: 10px;
    background: var(--cinnabar);
    color: #fff;
    font-size: 11px;
    text-align: center;
    box-sizing: border-box;
  }

  .pool-mask {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.35);
    z-index: 1000;
  }

  .teams {
    max-height: none;
    overflow: visible;
  }

  .team-row--attack,
  .team-row--defense {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .toolbar .el-button {
    flex: 1;
    margin-left: 0 !important;
  }

  .slot-card {
    padding: 10px 8px;
  }

  .pool-item {
    padding: 10px 8px; /* 增大拖拽项触控区 */
  }
}
</style>
