<template>
  <el-dialog v-model="visible" title="导入历史排表" width="760px" append-to-body :close-on-click-modal="false">
    <div v-if="loading" v-loading="loading" class="dialog-loading" />
    <el-empty v-else-if="!history.length" description="暂无其他赛程的排表数据" :image-size="80" />

    <template v-else>
      <!-- 第一步：选择历史赛程 -->
      <p class="dialog-tip">选择历史赛程：</p>
      <el-select v-model="selectedSchedule" placeholder="请选择历史赛程" style="width: 100%">
        <el-option v-for="h in history" :key="h.schedule_id" :value="h.schedule_id" :label="scheduleLabel(h)" />
      </el-select>

      <!-- 第二步：按小队多选 -->
      <template v-if="current">
        <div class="team-toolbar">
          <span class="dialog-tip">选择要导入的小队（可多选）：</span>
          <span class="team-toolbar__actions">
            <el-button link type="primary" size="small" @click="selectAll">全选</el-button>
            <el-button link size="small" @click="clearAll">清空</el-button>
          </span>
        </div>

        <div class="group-list">
          <div v-for="g in groups" :key="g.category" class="team-group" :class="`team-group--${g.type}`">
            <div class="team-group__header">
              <span class="team-group__dot" />
              {{ g.label }}
              <span class="team-group__meta">{{ g.teams.length }}队 · 6人</span>
            </div>
            <div class="team-grid">
              <label
                v-for="t in g.teams"
                :key="t.category + t.team_index"
                class="team-card"
                :class="{ selected: selectedTeams.has(teamKey(t.category, t.team_index)) }"
              >
                <el-checkbox
                  :model-value="selectedTeams.has(teamKey(t.category, t.team_index))"
                  @change="(v: boolean | string | number) => toggleTeam(t.category, t.team_index, !!v)"
                >
                  <span class="team-card__title">{{ t.category }} {{ t.team_index + 1 }} 队</span>
                </el-checkbox>
                <div class="team-card__slots">
                  <span v-for="(s, i) in t.slots" :key="i" class="slot-preview">
                    <span v-if="s.member_name" class="slot-chip">
                      <i class="prof-dot" :style="{ background: profColor(s.profession) }" />
                      {{ s.member_name }}
                    </span>
                    <span v-else class="slot-empty">—</span>
                  </span>
                </div>
              </label>
            </div>
          </div>
        </div>

        <p class="dialog-hint">导入规则：仅当前候选池（出勤正常）中出现的成员按原位置排入，未出现的槽位留空，其余小队不受影响。</p>
      </template>
    </template>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button
        type="primary"
        :disabled="selectedTeams.size === 0"
        :loading="saving"
        @click="onConfirm"
      >
        确认导入（{{ selectedTeams.size }} 个小队）
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

import { getLineupHistory, importLineup } from '@/api/lineups'
import type { LineupHistoryItem } from '@/types/lineup'
import { profColor } from '@/utils/profession'

const props = defineProps<{ scheduleId: number }>()
const emit = defineEmits<{ imported: [] }>()
const visible = defineModel<boolean>({ required: true })

const loading = ref(false)
const saving = ref(false)
const history = ref<LineupHistoryItem[]>([])
const selectedSchedule = ref<number | null>(null)
const selectedTeams = ref<Set<string>>(new Set())

/** 四大分组（与排表页一致）。 */
const GROUPS = [
  { category: '进攻1', label: '进攻一', type: 'attack' },
  { category: '进攻2', label: '进攻二', type: 'attack' },
  { category: '防守1', label: '防守一', type: 'defense' },
  { category: '防守2', label: '防守二', type: 'defense' },
]

const current = computed(() => history.value.find((h) => h.schedule_id === selectedSchedule.value) ?? null)

const groups = computed(() =>
  GROUPS.map((g) => ({
    ...g,
    teams: (current.value?.teams ?? [])
      .filter((t) => t.category === g.category)
      .sort((a, b) => a.team_index - b.team_index),
  })),
)

function scheduleLabel(h: LineupHistoryItem): string {
  return `vs ${h.opponent} · ${dayjs(h.match_time).format('MM-DD HH:mm')}`
}

function teamKey(category: string, teamIndex: number): string {
  return `${category}:${teamIndex}`
}

function toggleTeam(category: string, teamIndex: number, checked: boolean) {
  const next = new Set(selectedTeams.value)
  if (checked) next.add(teamKey(category, teamIndex))
  else next.delete(teamKey(category, teamIndex))
  selectedTeams.value = next
}

function selectAll() {
  const next = new Set<string>()
  for (const t of current.value?.teams ?? []) next.add(teamKey(t.category, t.team_index))
  selectedTeams.value = next
}

function clearAll() {
  selectedTeams.value = new Set()
}

/** 切换赛程时清空已选小队。 */
watch(selectedSchedule, () => {
  selectedTeams.value = new Set()
})

watch(visible, async (v) => {
  if (!v) return
  loading.value = true
  selectedSchedule.value = null
  selectedTeams.value = new Set()
  try {
    history.value = await getLineupHistory(props.scheduleId)
  } finally {
    loading.value = false
  }
})

async function onConfirm() {
  if (!selectedSchedule.value || selectedTeams.value.size === 0) return
  saving.value = true
  try {
    const res = await importLineup(props.scheduleId, {
      source_schedule_id: selectedSchedule.value,
      team_keys: [...selectedTeams.value],
    })
    ElMessage.success(res.message)
    visible.value = false
    emit('imported')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.dialog-loading {
  min-height: 120px;
}

.dialog-tip {
  color: var(--ink-500);
  font-size: 13px;
  margin: 0 0 8px;
}

.team-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
}

.team-toolbar .dialog-tip {
  margin: 0;
}

.team-toolbar__actions {
  display: flex;
  gap: 4px;
}

.group-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 10px;
  max-height: 380px;
  overflow: auto;
  padding-right: 4px;
}

.team-group {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--ink-bg-paper);
}

.team-group--attack {
  border-color: var(--gold-200);
}

.team-group--defense {
  border-color: #d5dfe8;
}

.team-group__header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--gold-50);
  border-bottom: 1px solid var(--gold-100);
  font-weight: 700;
  font-size: 13px;
  color: var(--gold-700);
  letter-spacing: 1px;
}

.team-group--defense .team-group__header {
  background: #eef3f8;
  border-bottom-color: #dde6ee;
  color: var(--indigo);
}

.team-group__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--gold-gradient);
}

.team-group--defense .team-group__dot {
  background: linear-gradient(135deg, #7b9cc0, var(--indigo));
}

.team-group__meta {
  margin-left: auto;
  font-size: 11px;
  font-weight: 400;
  color: var(--ink-400);
  letter-spacing: 0;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 12px 14px;
}

.team-group--defense .team-grid {
  grid-template-columns: repeat(2, 1fr);
}

.team-card {
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-md);
  padding: 8px 10px;
  background: var(--ink-bg-cream);
  cursor: pointer;
  transition: border-color var(--dur-fast), box-shadow var(--dur-fast);
}

.team-card:hover {
  border-color: var(--gold-300);
  box-shadow: var(--shadow-sm);
}

.team-card.selected {
  border-color: var(--gold-400);
  background: var(--gold-50);
}

.team-card__title {
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-700);
}

.team-card__slots {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-top: 6px;
}

.slot-preview {
  font-size: 11px;
  min-height: 18px;
}

.slot-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--ink-700);
  font-weight: 600;
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-xl);
  padding: 0 8px;
}

.prof-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.slot-empty {
  color: var(--ink-300);
}

.dialog-hint {
  margin-top: 12px;
  font-size: 12px;
  color: var(--ink-400);
  line-height: 1.6;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .team-toolbar {
    flex-wrap: wrap;
    gap: 4px;
  }

  .team-grid,
  .team-group--defense .team-grid {
    grid-template-columns: 1fr;
  }
}
</style>
