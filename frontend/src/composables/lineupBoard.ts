/** 排表编排状态与拖拽逻辑（LineupEditor 专用）。 */
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { getLineup, getLineupCandidates, saveLineup } from '@/api/lineups'
import type { LineupCandidate, LineupSlot, LineupTeam } from '@/types/lineup'

export interface CandidateItem {
  key: string
  member_id: number | null
  member_name: string
  profession: string
  member_status: string
}
export interface SlotItem {
  key: string
  slot_index: number
  member_id: number | null
  member_name: string
  profession: string
  member_status: string
  remark: string
}
export interface TeamBox {
  category: string
  team_index: number
  slots: SlotItem[][]
}

/** 职业展示顺序（依据 ui-style-guide）。 */
export const PROF_ORDER = ['铁衣', '素问', '神相', '碎梦', '血河', '玄机', '九灵', '潮光', '龙吟', '鸿音', '沧澜']

function keyOf(memberId: number | null, name: string): string {
  return memberId != null ? `m${memberId}` : `f${name}`
}

function toSlot(s: LineupSlot): SlotItem {
  return {
    key: keyOf(s.member_id, s.member_name),
    slot_index: s.slot_index,
    member_id: s.member_id,
    member_name: s.member_name,
    profession: s.profession || '',
    member_status: s.member_id == null ? 'filler' : 'formal',
    remark: s.remark || '',
  }
}

function toCandidate(c: LineupCandidate): CandidateItem {
  return {
    key: keyOf(c.member_id, c.member_name),
    member_id: c.member_id,
    member_name: c.member_name,
    profession: c.profession,
    member_status: c.member_status,
  }
}

function toSlotItem(el: SlotItem | CandidateItem): SlotItem {
  return {
    key: el.key,
    slot_index: 'slot_index' in el ? el.slot_index : 0,
    member_id: el.member_id,
    member_name: el.member_name,
    profession: 'profession' in el ? el.profession || '' : '',
    member_status: 'member_status' in el ? el.member_status || 'filler' : 'filler',
    remark: 'remark' in el ? el.remark || '' : '',
  }
}

function toCandidateItem(el: SlotItem | CandidateItem): CandidateItem {
  return {
    key: el.key,
    member_id: el.member_id ?? null,
    member_name: el.member_name || '',
    profession: 'profession' in el ? el.profession || '' : '',
    member_status: 'member_status' in el ? el.member_status || 'filler' : 'filler',
  }
}

export function useLineupBoard(scheduleId: number) {
  const loading = ref(false)
  const saving = ref(false)
  const teams = ref<TeamBox[]>([])
  const candidates = ref<CandidateItem[]>([])

  /** 自动保存状态：idle / pending（待保存） / saving（保存中） / saved（已保存）。 */
  const autoSaveStatus = ref<'idle' | 'pending' | 'saving' | 'saved'>('idle')
  let autoSaveTimer: ReturnType<typeof setTimeout> | null = null

  /** 构建保存载荷（槽位数据 + 团/标题备注）。 */
  function buildPayload(): LineupTeam[] {
    return teams.value.map((t) => ({
      category: t.category,
      team_index: t.team_index,
      slots: t.slots.map((box, i) => ({
        slot_index: i,
        member_id: box[0]?.member_id ?? null,
        member_name: box[0]?.member_name ?? '',
        remark: box[0]?.remark ?? '',
      })),
    }))
  }

  /** 变更后触发自动保存（防抖 3 秒）。 */
  function scheduleAutoSave() {
    autoSaveStatus.value = 'pending'
    if (autoSaveTimer) clearTimeout(autoSaveTimer)
    autoSaveTimer = setTimeout(() => {
      autoSaveStatus.value = 'saving'
      saveLineup(scheduleId, {
        data: buildPayload(),
        title_remark: titleRemark.value,
        groups_remark: { ...groupsRemark.value },
      })
        .then(() => {
          autoSaveStatus.value = 'saved'
          setTimeout(() => {
            autoSaveStatus.value = 'idle'
          }, 2000)
        })
        .catch(() => {
          autoSaveStatus.value = 'idle'
        })
    }, 3000)
  }

  // 仅统计已填入成员的槽位（空槽位也包装成数组，需按 member_name 过滤）
  const placedCount = computed(() =>
    teams.value.reduce((n, t) => n + t.slots.filter((b) => b.length > 0 && b[0].member_name).length, 0),
  )

  /** 已排入槽位的成员 key 集合（正式按 ID、补人按姓名）。 */
  const placedKeys = computed(() => {
    const set = new Set<string>()
    for (const t of teams.value) {
      for (const b of t.slots) {
        if (b.length > 0 && b[0].member_name) set.add(b[0].key)
      }
    }
    return set
  })

  /** 候选池按职业分组（按 ui-style-guide 顺序，仅未排成员）。 */
  const professionGroups = computed(() => {
    const map = new Map<string, CandidateItem[]>()
    for (const c of candidates.value) {
      const prof = c.profession || '未分类'
      if (!map.has(prof)) map.set(prof, [])
      map.get(prof)!.push(c)
    }
    return [...map.entries()].sort(([a], [b]) => PROF_ORDER.indexOf(a) - PROF_ORDER.indexOf(b))
  })

  function backToCandidate(el: SlotItem | CandidateItem) {
    if (!el.member_name) return
    if (candidates.value.some((c) => c.key === el.key)) return
    candidates.value.push(toCandidateItem(el))
  }

  function onCandidateChange(evt: { added?: { element: SlotItem | CandidateItem }; removed?: { element: SlotItem | CandidateItem } }) {
    // 候选池分组列表是派生数组，vuedraggable 的增删不会反映到源数据，这里手动同步
    if (evt.removed) {
      // 拖出候选池：从源数据删除（补人/正式成员填入槽位后不再显示）
      const el = evt.removed.element
      const idx = candidates.value.findIndex((c) => c.key === el.key)
      if (idx >= 0) candidates.value.splice(idx, 1)
    }
    if (evt.added) {
      // 拖回候选池：加回源数据（避免派生分组重算后丢失）
      const el = evt.added.element
      if (!candidates.value.some((c) => c.key === el.key)) {
        candidates.value.push(toCandidateItem(el))
      }
    }
  }

  function onSlotChange(evt: any, team: TeamBox, si: number) {
    const box = team.slots[si]
    if (evt.added) {
      box.filter((s) => s !== evt.added.element).forEach((o) => backToCandidate(o))
      box.length = 0
      box.push({ ...toSlotItem(evt.added.element), slot_index: si })
    }
    if (evt.removed) {
      backToCandidate(evt.removed.element)
    }
    scheduleAutoSave()
  }

  async function editRemark(team: TeamBox, si: number) {
    const box = team.slots[si]
    if (!box.length) return
    try {
      const { value } = await ElMessageBox.prompt('为槽位添加角色备注（如：主T、指挥、治疗）', '角色备注', {
        inputValue: box[0].remark,
        inputPlaceholder: '输入备注',
      })
      box[0].remark = value.trim()
      scheduleAutoSave()
    } catch {
      /* 取消 */
    }
  }

  /** 保存函数引用，供外部调用。 */
  const titleRemark = ref('')
  const groupsRemark = ref<Record<string, string>>({
    '进攻1': '', '进攻2': '', '防守1': '', '防守2': '',
  })

  async function editTitleRemark() {
    try {
      const { value } = await ElMessageBox.prompt('为本次排表添加标题备注', '标题备注', {
        inputValue: titleRemark.value,
        inputPlaceholder: '输入标题备注（如：本周主力阵容）',
      })
      titleRemark.value = value.trim()
      scheduleAutoSave()
    } catch { /* 取消 */ }
  }

  async function editGroupRemark(groupCategory: string) {
    const label = groupCategory === '进攻1' ? '进攻一' : groupCategory === '进攻2' ? '进攻二' : groupCategory === '防守1' ? '防守一' : '防守二'
    try {
      const { value } = await ElMessageBox.prompt(`为「${label}」添加备注`, '团备注', {
        inputValue: groupsRemark.value[groupCategory] || '',
        inputPlaceholder: '输入团备注（如：主力输出组）',
      })
      groupsRemark.value = { ...groupsRemark.value, [groupCategory]: value.trim() }
      scheduleAutoSave()
    } catch { /* 取消 */ }
  }

  /** 清除槽位成员（放回候选池）。 */
  function onRemoveSlot(team: TeamBox, si: number) {
    const box = team.slots[si]
    if (!box.length) return
    backToCandidate(box[0])
    box.length = 0
    scheduleAutoSave()
  }

  async function onSave() {
    // 取消待执行的自动保存
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer)
      autoSaveTimer = null
    }
    autoSaveStatus.value = 'idle'
    saving.value = true
    try {
      await saveLineup(scheduleId, {
        data: buildPayload(),
        title_remark: titleRemark.value,
        groups_remark: { ...groupsRemark.value },
      })
      ElMessage.success('排表已保存')
    } finally {
      saving.value = false
    }
  }

  async function load() {
    loading.value = true
    try {
      const [lineup, pool] = await Promise.all([
        getLineup(scheduleId),
        getLineupCandidates(scheduleId),
      ])
      teams.value = lineup.data.map((t) => ({
        category: t.category,
        team_index: t.team_index,
        slots: t.slots.map((s) => [toSlot(s)]),
      }))
      // 读取团/标题备注
      titleRemark.value = lineup.title_remark || ''
      const gr = lineup.groups_remark || {}
      groupsRemark.value = { '进攻1': '', '进攻2': '', '防守1': '', '防守2': '', ...gr }
      // 候选池剔除已排成员（正式按 ID、补人按姓名）
      const placed = new Set<string>()
      for (const t of teams.value) {
        for (const b of t.slots) {
          if (b.length > 0 && b[0].member_name) placed.add(b[0].key)
        }
      }
      candidates.value = pool.map((c) => toCandidate(c)).filter((c) => !placed.has(c.key))
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    saving,
    autoSaveStatus,
    teams,
    candidates,
    placedCount,
    placedKeys,
    professionGroups,
    titleRemark,
    groupsRemark,
    onSave,
    editRemark,
    editTitleRemark,
    editGroupRemark,
    onRemoveSlot,
    onSlotChange,
    onCandidateChange,
    load,
  }
}
