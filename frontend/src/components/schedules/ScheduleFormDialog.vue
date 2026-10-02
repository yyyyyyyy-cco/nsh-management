<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑赛程' : '创建赛程'" width="520px" destroy-on-close append-to-body>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="对手" prop="opponent">
        <el-input v-model="form.opponent" maxlength="64" placeholder="请输入对手名称" />
      </el-form-item>
      <el-form-item label="比赛时间" prop="match_time">
        <el-date-picker
          v-model="form.match_time"
          type="datetime"
          placeholder="选择比赛时间"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="地点" prop="location">
        <el-input v-model="form.location" maxlength="128" placeholder="可选" />
      </el-form-item>
      <el-form-item label="局数" prop="rounds">
        <el-radio-group v-model="form.rounds" :disabled="isEdit">
          <el-radio :value="1">1局</el-radio>
          <el-radio :value="2">2局</el-radio>
          <el-radio :value="3">3局</el-radio>
        </el-radio-group>
        <div v-if="isEdit" class="hint">局数创建后不可修改</div>
      </el-form-item>
      <template v-if="isEdit">
        <el-form-item label="比赛结果" prop="result">
          <el-select v-model="form.result" placeholder="选择结果" style="width: 100%">
            <el-option v-for="r in SCHEDULE_RESULTS" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-for="i in roundsCount" :key="i" :label="`第${i}局结果`" prop="round_results">
          <el-select v-model="form.round_results[i - 1]" placeholder="选择结果" style="width: 100%">
            <el-option v-for="r in SCHEDULE_RESULTS" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>
      </template>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

import { createSchedule, updateSchedule } from '@/api/schedules'
import type { ScheduleInfo } from '@/types/schedule'
import { SCHEDULE_RESULTS } from '@/utils/constants'

const props = defineProps<{ modelValue: boolean; schedule: ScheduleInfo | null; defaultDate?: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; success: [] }>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const isEdit = computed(() => Boolean(props.schedule))
const roundsCount = computed(() => props.schedule?.rounds || 3)

const form = reactive({
  opponent: '',
  match_time: '',
  location: '',
  rounds: 3 as number,
  result: 'pending' as string,
  round_results: [] as string[],
})

const rules: FormRules = {
  opponent: [{ required: true, message: '请输入对手名称', trigger: 'blur' }],
  match_time: [{ required: true, message: '请选择比赛时间', trigger: 'change' }],
  rounds: [{ required: true, message: '请选择局数', trigger: 'change' }],
}

watch(
  () => props.modelValue,
  (value) => {
    if (!value) return
    const schedule = props.schedule
    form.opponent = schedule?.opponent || ''
    form.match_time = schedule?.match_time || (props.defaultDate ? `${props.defaultDate}T19:00:00` : '')
    form.location = schedule?.location || ''
    form.rounds = schedule?.rounds || 3
    form.result = schedule?.result || 'pending'
    form.round_results = schedule?.round_results ? [...schedule.round_results] : []
  },
)

async function onSubmit() {
  if (!formRef.value) return
  await formRef.value.validate()
  loading.value = true
  try {
    if (isEdit.value && props.schedule) {
      await updateSchedule(props.schedule.id, {
        opponent: form.opponent,
        match_time: form.match_time,
        location: form.location || null,
        result: form.result,
        round_results: form.round_results.length === roundsCount.value ? form.round_results : null,
      })
    } else {
      await createSchedule({
        opponent: form.opponent,
        match_time: form.match_time,
        location: form.location || null,
        rounds: form.rounds,
      })
    }
    ElMessage.success('保存成功')
    visible.value = false
    emit('success')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.hint {
  font-size: 12px;
  color: #9ca3af;
  margin-left: 12px;
}
</style>
