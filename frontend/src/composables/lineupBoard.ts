/** 排表编排状态与拖拽逻辑（LineupEditor 专用）。
 * 行数豁免（连续逻辑）：看板状态机——拖拽上下文、自动保存定时器与候选池回池逻辑共享内部可变状态。
 * 登记见 .agent/rules/file-length-rule.md 豁免清单。 */
import { computed, onScopeDispose, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { getLineup, getLineupCandidates, saveLineup } from '@/api/lineups'
import type { LineupCandidate, LineupSlot, LineupTeam } from '@/types/lineup'

export interface CandidateItem {
  key: string
  member_id: number | null
  member_name: string
  profession: string
  member_status: string
  attendance_remark: string
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
    attendance_remark: c.attendance_remark || '',
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
    attendance_remark: '', // 出勤库备注仅候选池展示：拖动（含拖回）后消失，不随槽位流转
  }
}

/** 空槽位占位元素：删除成员后补回，保持槽位可编辑备注、可作拖放目标（与初始加载一致）。 */
function emptySlot(si: number): SlotItem {
  return {
    key: keyOf(null, ''),
    slot_index: si,
    member_id: null,
    member_name: '',
    profession: '',
    member_status: 'filler',
    remark: '',
  }
}

export function useLineupBoard(scheduleId: number) {
  const loading = ref(false)
  const saving = ref(false)
  const teams = ref<TeamBox[]>([])
  const candidates = ref<CandidateItem[]>([])

  /** 填表模式：drag 拖拽 / input 输入（互斥，切换后行为一致：自动保存、备注等）。 */
  const mode = ref<'drag' | 'input'>('input')

  /** 自动保存状态：idle / pending（待保存） / saving（保存中） / saved（已保存）。 */
  const autoSaveStatus = ref<'idle' | 'pending' | 'saving' | 'saved'>('idle')
  let autoSaveTimer: ReturnType<typeof setTimeout> | null = null
  let savedTimer: ReturnType<typeof setTimeout> | null = null
  let editVersion = 0
  let savedVersion = 0
  let saveTask: Promise<void> | null = null
  let loadSeq = 0
  let disposed = false

  function clearSaveTimers() {
    if (autoSaveTimer !== null) clearTimeout(autoSaveTimer)
    if (savedTimer !== null) clearTimeout(savedTimer)
    autoSaveTimer = savedTimer = null
  }

  onScopeDispose(() => {
    disposed = true
    loadSeq++
    clearSaveTimers()
  })

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

  /** 所有保存共用一个任务；在途期间的新编辑按版本串行补存。 */
  async function persistChanges() {
    saving.value = true
    try {
      while (!disposed && savedVersion < editVersion) {
        clearSaveTimers()
        const version = editVersion
        autoSaveStatus.value = 'saving'
        await saveLineup(scheduleId, {
          data: buildPayload(),
          title_remark: titleRemark.value,
          groups_remark: { ...groupsRemark.value },
        })
        if (disposed) return
        savedVersion = version
      }
      if (disposed) return
      autoSaveStatus.value = 'saved'
      savedTimer = setTimeout(() => {
        savedTimer = null
        autoSaveStatus.value = 'idle'
      }, 2000)
    } catch (error) {
      if (!disposed) {
        clearSaveTimers()
        // 保留未保存版本；HTTP 层提示原因，用户可点击「保存排表」重试。
        autoSaveStatus.value = 'pending'
      }
      throw error
    } finally {
      if (!disposed) saving.value = false
    }
  }

  /** 重载、导入或离开页面前调用；失败向上传递，禁止用旧快照覆盖编辑。 */
  function flushSave(): Promise<void> {
    if (autoSaveTimer !== null) clearTimeout(autoSaveTimer)
    autoSaveTimer = null
    if (saveTask) return saveTask
    if (disposed || savedVersion === editVersion) return Promise.resolve()
    saveTask = persistChanges().finally(() => { saveTask = null })
    return saveTask
  }

  /** 变更后触发自动保存（防抖 3 秒）。 */
  function scheduleAutoSave() {
    if (disposed) return
    editVersion++
    clearSaveTimers()
    autoSaveStatus.value = 'pending'
    autoSaveTimer = setTimeout(() => {
      autoSaveTimer = null
      void flushSave().catch(() => { /* HTTP 层已提示，保留待保存状态 */ })
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

  /** 拖拽上下文：记录被拖成员来源（槽位或候选池），用于交换与回滚。 */
  let dragCtx: { key: string; team: TeamBox | null; si: number } | null = null

  /** 拖拽开始：记录被拖成员的来源槽位（元素上携带 data-key）。 */
  function onSlotDragStart(evt: any, team: TeamBox, si: number) {
    const key = evt.item?.dataset?.key as string | undefined
    if (!key) return
    dragCtx = { key, team, si }
  }

  /** 拖拽开始：来源为候选池（team 为 null，表示替换而非交换）。 */
  function onPoolDragStart(evt: any) {
    const key = evt.item?.dataset?.key as string | undefined
    if (!key) return
    dragCtx = { key, team: null, si: -1 }
  }

  /** 拖拽结束：清空上下文。 */
  function onDragEnd() {
    dragCtx = null
  }

  function onSlotChange(evt: any, team: TeamBox, si: number) {
    const box = team.slots[si]
    if (evt.added) {
      const el = evt.added.element
      // 防御：空占位被拖入（无成员名），恢复原槽位内容并忽略
      if (!el.member_name) {
        const keep = box.find((s) => s !== el && s.member_name)
        box.length = 0
        box.push(keep ? { ...keep } : emptySlot(si))
        return
      }
      const replaced = box.find((s) => s !== el && s.member_name)
      const ctx = dragCtx
      if (replaced && ctx && ctx.key === el.key && ctx.team) {
        // 槽位 → 已有成员的槽位：弹窗确认后交换，取消则回滚
        confirmSwap(el, replaced, { key: ctx.key, team: ctx.team, si: ctx.si }, box, si)
        return
      }
      // 其余情况：直接填入（来自候选池替换时原成员回池）
      if (replaced) backToCandidate(replaced)
      box.length = 0
      box.push({ ...toSlotItem(el), slot_index: si })
      scheduleAutoSave()
    }
    if (evt.removed) {
      // 源槽位：元素已移走，只补回空占位（去向由目标列表的 added 处理：进槽位或回候选池）
      if (!box.length) box.push(emptySlot(si))
    }
  }

  /** 槽位间拖拽交换：确认后双方互换位置，取消则回滚（双方维持原状）。 */
  async function confirmSwap(
    incoming: SlotItem | CandidateItem,
    replaced: SlotItem,
    ctx: { key: string; team: TeamBox; si: number },
    box: SlotItem[],
    si: number,
  ) {
    const srcBox = ctx.team.slots[ctx.si]
    const nameA = incoming.member_name
    const nameB = replaced.member_name
    const ok = await ElMessageBox.confirm(`将「${nameA}」与「${nameB}」交换位置？`, '交换确认', {
      type: 'warning',
      confirmButtonText: '交 换',
      cancelButtonText: '取 消',
    })
      .then(() => true)
      .catch(() => false)
    if (ok) {
      // 确认交换：目标槽位保留拖入者，被替换者回到来源槽位
      box.length = 0
      box.push({ ...toSlotItem(incoming), slot_index: si })
      srcBox.length = 0
      srcBox.push({ ...toSlotItem(replaced), slot_index: ctx.si })
      scheduleAutoSave()
    } else {
      // 取消：回滚拖拽，双方维持原状
      box.length = 0
      box.push({ ...toSlotItem(replaced), slot_index: si })
      srcBox.length = 0
      srcBox.push({ ...toSlotItem(incoming), slot_index: ctx.si })
    }
  }

  /** 候选池按姓名包含匹配（忽略大小写），供输入模式使用。 */
  function matchCandidates(keyword: string): CandidateItem[] {
    const kw = keyword.trim().toLowerCase()
    if (!kw) return []
    return candidates.value.filter((c) => c.member_name.toLowerCase().includes(kw))
  }

  /** 输入模式填入：替换槽位成员（原成员回池），候选池剔除，触发自动保存。 */
  function fillSlotByInput(team: TeamBox, si: number, item: CandidateItem) {
    const box = team.slots[si]
    box.filter((s) => s.member_name).forEach((o) => backToCandidate(o))
    box.length = 0
    box.push({ ...toSlotItem(item), slot_index: si })
    const idx = candidates.value.findIndex((c) => c.key === item.key)
    if (idx >= 0) candidates.value.splice(idx, 1)
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
    // 补回空占位元素，避免槽位变为空数组导致备注图标与拖放目标丢失
    box.push(emptySlot(si))
    scheduleAutoSave()
  }

  async function onSave() {
    if (disposed) return
    editVersion++
    clearSaveTimers()
    await flushSave()
    if (!disposed) ElMessage.success('排表已保存')
  }

  async function load(): Promise<boolean> {
    if (disposed) return false
    const seq = ++loadSeq
    loading.value = true
    try {
      await flushSave()
      if (disposed || seq !== loadSeq || savedVersion !== editVersion) return false
      const version = editVersion
      const [lineup, pool] = await Promise.all([
        getLineup(scheduleId),
        getLineupCandidates(scheduleId),
      ])
      // 旧请求、加载期间的新编辑以及卸载后的响应都不能覆盖看板。
      if (disposed || seq !== loadSeq || version !== editVersion) return false
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
      return true
    } catch {
      // 保存或加载失败都保留当前看板；统一错误提示由 HTTP 层负责。
      return false
    } finally {
      if (!disposed && seq === loadSeq) loading.value = false
    }
  }

  return {
    loading,
    saving,
    autoSaveStatus,
    mode,
    teams,
    candidates,
    placedCount,
    placedKeys,
    professionGroups,
    titleRemark,
    groupsRemark,
    flushSave,
    onSave,
    editRemark,
    editTitleRemark,
    editGroupRemark,
    onRemoveSlot,
    onSlotChange,
    onSlotDragStart,
    onPoolDragStart,
    onDragEnd,
    onCandidateChange,
    matchCandidates,
    fillSlotByInput,
    load,
  }
}
