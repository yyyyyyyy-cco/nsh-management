<template>
  <el-dialog v-model="visible" title="导入请假" width="480px" append-to-body>
    <p class="dialog-tip">粘贴请假名单（纯文本，每行一个，支持「1.ID 原因」序号格式）：</p>
    <el-input
      v-model="rawText"
      type="textarea"
      :rows="6"
      placeholder="1.11 有事情&#10;2.秋与 有事情"
    />
    <template v-if="result.matched.length">
      <div class="match-block">
        <div class="match-title">
          识别到 {{ result.matched.length }} 人
          <el-tag size="small" type="warning" effect="light">将设为请假</el-tag>
        </div>
        <div class="match-list">
          <span
            v-for="m in result.matched"
            :key="m.id"
            class="match-chip"
            :class="{ selected: selected.has(m.id), unselected: !selected.has(m.id) }"
            @click="toggleSelect(m.id)"
          >
            {{ m.member_name }}
            <em class="num">{{ m.profession }}</em>
          </span>
        </div>
        <div class="match-hint">点击可取消/恢复选中，取消的不纳入请假</div>
      </div>
    </template>
    <div v-if="result.unmatched.length" class="unmatch-block">
      <div class="unmatch-title">未匹配到 {{ result.unmatched.length }} 行（请检查名字）</div>
      <div v-for="line in result.unmatched" :key="line" class="unmatch-line">{{ line }}</div>
    </div>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="selected.size === 0" :loading="saving" @click="onConfirm">
        确认请假（{{ selected.size }}）
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { batchStatus } from '@/api/attendance'
import type { AttendanceRecord } from '@/types/attendance'

const props = defineProps<{ scheduleId: number; records: AttendanceRecord[] }>()
const emit = defineEmits<{ success: [] }>()
const visible = defineModel<boolean>({ required: true })

const rawText = ref('')
const saving = ref(false)
/** 选中的匹配成员 ID（识别结果默认全选，可点击取消）。 */
const selected = ref<Set<number>>(new Set())

watch(visible, (v) => {
  if (v) rawText.value = ''
})

/** 解析纯文本：跳过行首序号（如 "1.姓名 原因"），取姓名关键词按包含关系匹配出勤成员。 */
const result = computed(() => {
  const lines = rawText.value.split(/\r?\n/).map((l) => l.trim()).filter(Boolean)
  const matched: AttendanceRecord[] = []
  const unmatched: string[] = []
  for (const line of lines) {
    // 仅当行首数字后紧跟序号标记（.、,．)）时视为序号并去掉，纯数字姓名（如 "11 有事情"）不受影响
    const cleaned = line.replace(/^\d+\s*[.、．)]\s*/, '')
    const keyword = cleaned.split(/[\s,，.。、;；:：]+/)[0]
    if (!keyword) continue
    const hits = props.records.filter((r) => r.member_name.includes(keyword))
    if (hits.length) {
      for (const h of hits) {
        if (!matched.some((m) => m.id === h.id)) matched.push(h)
      }
    } else {
      unmatched.push(line)
    }
  }
  return { matched, unmatched }
})

// 识别结果变化时默认全选
watch(
  result,
  (r) => {
    selected.value = new Set(r.matched.map((m) => m.id))
  },
  { immediate: true },
)

/** 点击切换选中状态（取消的不纳入请假）。 */
function toggleSelect(id: number) {
  const next = new Set(selected.value)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  selected.value = next
}

async function onConfirm() {
  saving.value = true
  try {
    const ids = [...selected.value]
    const res = await batchStatus(props.scheduleId, ids, 'leave')
    ElMessage.success(res.message)
    visible.value = false
    emit('success')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.dialog-tip {
  color: var(--ink-500);
  font-size: 13px;
  margin: 0 0 8px;
}

.match-block {
  margin-top: 14px;
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-md);
  background: var(--gold-50);
  padding: 10px 12px;
}

.match-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink-700);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.match-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.match-chip {
  font-size: 12px;
  background: var(--ink-bg-paper);
  border: 1px solid var(--gold-300);
  border-radius: var(--radius-xl);
  padding: 2px 10px;
  color: var(--ink-800);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--dur-fast);
}

.match-chip:hover {
  box-shadow: var(--shadow-sm);
}

.match-chip.unselected {
  opacity: 0.45;
  border-style: dashed;
  text-decoration: line-through;
}

.match-chip em {
  font-style: normal;
  font-weight: 400;
  color: var(--ink-400);
  margin-left: 4px;
}

.match-hint {
  margin-top: 8px;
  font-size: 11px;
  color: var(--ink-400);
}

.unmatch-block {
  margin-top: 12px;
  border: 1px solid var(--el-color-danger-light-7);
  border-radius: var(--radius-md);
  background: var(--el-color-danger-light-9);
  padding: 10px 12px;
}

.unmatch-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--cinnabar);
  margin-bottom: 6px;
}

.unmatch-line {
  font-size: 12px;
  color: var(--ink-500);
  padding: 1px 0;
}
</style>
