<template>
  <el-dialog
    v-model="visible"
    :title="mode === 'approve' ? '通过改名申请' : '驳回改名申请'"
    width="460px"
    :close-on-click-modal="false"
    @closed="onClosed"
  >
    <div v-if="record" class="dialog-body">
      <div class="pair">
        <span class="pair__label">原 ID</span>
        <span class="pair__value">{{ record.old_game_id }}</span>
      </div>
      <div class="pair">
        <span class="pair__label">新 ID</span>
        <span class="pair__value pair__value--new">{{ record.new_game_id }}</span>
      </div>
      <div class="pair">
        <span class="pair__label">提交账号</span>
        <span class="pair__value">{{ record.requester_username }}</span>
      </div>

      <template v-if="mode === 'approve'">
        <el-alert type="warning" :closable="false" show-icon class="alert">
          <template #title>
            将更新常驻库名称，并建立新旧 ID 查询关联；历史出勤、排表、录屏与比赛记录原文不变。
          </template>
        </el-alert>
        <p class="note">若该 ID 已被其他成员占用，或存在名称归属冲突，审核会被拒绝并保持待审状态。</p>
        <el-checkbox v-model="identityConfirmed" class="confirm">
          我已核实申请人身份（游戏内或群内确认）
        </el-checkbox>
      </template>

      <template v-else>
        <el-input
          v-model="remark"
          type="textarea"
          :rows="3"
          maxlength="255"
          show-word-limit
          placeholder="请填写驳回原因（帮众可见，请勿填写隐私信息）"
        />
      </template>
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button
        :type="mode === 'approve' ? 'primary' : 'danger'"
        :loading="submitting"
        :disabled="mode === 'approve' && !identityConfirmed"
        @click="onConfirm"
      >
        {{ mode === 'approve' ? '确认通过' : '确认驳回' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { auditGameIdRequest } from '@/api/gameIdRequests'
import type { GameIdRequestAdminItem } from '@/types/gameIdRequest'

const props = defineProps<{
  modelValue: boolean
  record: GameIdRequestAdminItem | null
  mode: 'approve' | 'reject'
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  reviewed: []
}>()

const identityConfirmed = ref(false)
const remark = ref('')
const submitting = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      identityConfirmed.value = false
      remark.value = ''
    }
  },
)

async function onConfirm() {
  if (!props.record) return
  const payload =
    props.mode === 'approve'
      ? { action: 'approve' as const, identity_confirmed: true }
      : { action: 'reject' as const, review_remark: remark.value.trim() }
  if (props.mode === 'reject' && !payload.review_remark) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  submitting.value = true
  try {
    await auditGameIdRequest(props.record.id, payload)
    ElMessage.success(props.mode === 'approve' ? '已通过，常驻库名称已更新' : '已驳回')
    visible.value = false
    emit('reviewed')
  } catch {
    // 冲突（409）等错误提示由 http 拦截器统一处理；保持弹窗开启便于复核
  } finally {
    submitting.value = false
  }
}

function onClosed() {
  identityConfirmed.value = false
  remark.value = ''
}
</script>

<style scoped>
.dialog-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pair {
  display: flex;
  align-items: baseline;
  gap: 10px;
  font-size: 13.5px;
}

.pair__label {
  flex-shrink: 0;
  width: 68px;
  color: var(--ink-400);
}

.pair__value {
  font-weight: 700;
  color: var(--ink-900);
  overflow-wrap: anywhere;
}

.pair__value--new {
  color: var(--gold-700);
}

.alert {
  margin-top: 4px;
}

.note {
  margin: 0;
  font-size: 12px;
  line-height: 1.7;
  color: var(--ink-400);
}

.confirm {
  margin-top: 2px;
}
</style>
