/** 排表编排状态与拖拽逻辑（LineupEditor 专用）。 */
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import html2canvas from 'html2canvas'

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
  remark: string
}
export interface TeamBox {
  category: string
  team_index: number
  slots: SlotItem[][]
}

function keyOf(memberId: number | null, name: string): string {
  return memberId != null ? `m${memberId}` : `f${name}`
}

function toSlot(s: LineupSlot): SlotItem {
  return {
    key: keyOf(s.member_id, s.member_name),
    slot_index: s.slot_index,
    member_id: s.member_id,
    member_name: s.member_name,
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
  const exporting = ref(false)
  const editorRef = ref<HTMLElement | null>(null)
  const teams = ref<TeamBox[]>([])
  const candidates = ref<CandidateItem[]>([])

  const placedCount = computed(() => teams.value.reduce((n, t) => n + t.slots.filter((b) => b.length > 0).length, 0))

  function backToCandidate(el: SlotItem | CandidateItem) {
    if (!el.member_name) return
    if (candidates.value.some((c) => c.key === el.key)) return
    candidates.value.push(toCandidateItem(el))
  }

  function onCandidateChange(evt: { added?: { element: SlotItem | CandidateItem } }) {
    if (evt.added) {
      const idx = candidates.value.indexOf(evt.added.element as CandidateItem)
      if (idx >= 0) candidates.value[idx] = toCandidateItem(evt.added.element)
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
    } catch {
      /* 取消 */
    }
  }

  async function onSave() {
    saving.value = true
    try {
      const payload: LineupTeam[] = teams.value.map((t) => ({
        category: t.category,
        team_index: t.team_index,
        slots: t.slots.map((box, i) => ({
          slot_index: i,
          member_id: box[0]?.member_id ?? null,
          member_name: box[0]?.member_name ?? '',
          remark: box[0]?.remark ?? '',
        })),
      }))
      await saveLineup(scheduleId, payload)
      ElMessage.success('排表已保存')
    } finally {
      saving.value = false
    }
  }

  async function onExport() {
    if (!editorRef.value) return
    exporting.value = true
    try {
      const canvas = await html2canvas(editorRef.value, { backgroundColor: '#ffffff', scale: 2 })
      const link = document.createElement('a')
      link.download = `排表_${scheduleId}.png`
      link.href = canvas.toDataURL('image/png')
      link.click()
    } finally {
      exporting.value = false
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
      candidates.value = pool.map((c) => toCandidate(c))
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    saving,
    exporting,
    editorRef,
    teams,
    candidates,
    placedCount,
    onSave,
    onExport,
    editRemark,
    onSlotChange,
    onCandidateChange,
    load,
  }
}
