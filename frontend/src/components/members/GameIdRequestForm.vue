<template>
  <el-card shadow="never" class="req-card">
    <template #header>
      <div class="card-head">
        <span class="card-title">提交改名申请</span>
        <span class="card-sub">共享账号：请选择你自己的常驻成员</span>
      </div>
    </template>

    <el-alert type="warning" :closable="false" class="tip" show-icon>
      <template #title>
        帮众账号为共享账号，系统无法识别操作人。管理员会线下核实身份后审核；审核意见不要填写隐私信息。
      </template>
    </el-alert>

    <div class="field">
      <label class="field__label">常驻成员</label>
      <el-select
        v-model="selectedId"
        filterable
        remote
        clearable
        reserve-keyword
        :remote-method="searchMembers"
        :loading="optionsLoading"
        placeholder="输入 ID 搜索并选择"
        class="field__control"
        @change="onSelectChange"
      >
        <el-option v-for="item in options" :key="item.id" :value="item.id" :label="item.name">
          <span class="opt-name">{{ item.name }}</span>
          <span class="prof-tag opt-prof" :style="profTagStyle(item.main_profession)">{{ item.main_profession }}</span>
        </el-option>
      </el-select>
    </div>

    <div class="field">
      <label class="field__label">当前游戏 ID</label>
      <div class="field__control current">
        <span v-if="selected" class="current__value">{{ selected.name }}</span>
        <span v-else class="current__empty">请先选择成员</span>
      </div>
    </div>

    <div class="field">
      <label class="field__label">新游戏 ID</label>
      <el-input
        v-model="newGameId"
        maxlength="32"
        show-word-limit
        clearable
        :disabled="hasPending"
        placeholder="请输入新的游戏 ID（1～32 个字符）"
        class="field__control"
        @keyup.enter="onSubmit"
      />
    </div>

    <div v-if="selected" class="arrow-line">
      <span class="arrow-line__old">{{ selected.name }}</span>
      <span class="arrow-line__icon">→</span>
      <span class="arrow-line__new">{{ newGameId.trim() || '新 ID' }}</span>
    </div>

    <p class="hint">
      审核通过后更新常驻库名称，并支持按新旧 ID 查询合并后的战绩；已有出勤、排表、录屏与比赛记录不会被改写。
      若发现名称归属冲突，将停止自动合并，可改用「仅查此 ID」。
    </p>

    <div v-if="pending" class="pending">
      <el-tag type="warning" effect="light">该成员已有待审核申请</el-tag>
      <span class="pending__text">
        {{ pending.old_game_id }} → {{ pending.new_game_id }}（{{ formatTime(pending.created_at) }}
        提交），请等待审核结果
      </span>
    </div>

    <el-button type="primary" class="submit" :loading="submitting" :disabled="!canSubmit" @click="onSubmit">
      提交申请
    </el-button>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

import { createGameIdRequest, listGameIdOptions } from '@/api/gameIdRequests'
import type { GameIdOption, GameIdRequestItem } from '@/types/gameIdRequest'
import { profTagStyle } from '@/utils/profession'

const props = defineProps<{
  selected: GameIdOption | null
  pending: GameIdRequestItem | null
}>()

const emit = defineEmits<{
  select: [member: GameIdOption | null]
  submitted: []
}>()

const options = ref<GameIdOption[]>([])
const optionsLoading = ref(false)
const selectedId = ref<number | null>(null)
const newGameId = ref('')
const submitting = ref(false)

const hasPending = computed(() => props.pending !== null)
const canSubmit = computed(() => !!props.selected && !!newGameId.value.trim() && !hasPending.value && !submitting.value)

function formatTime(value: string): string {
  return dayjs(value).format('YYYY-MM-DD HH:mm')
}

// 请求序号：快速输入时丢弃过期响应
let searchSeq = 0

async function searchMembers(keyword: string) {
  const seq = ++searchSeq
  optionsLoading.value = true
  try {
    const page = await listGameIdOptions({ q: keyword.trim() || undefined, page: 1, page_size: 50 })
    if (seq !== searchSeq) return
    options.value = page.items
  } catch {
    // 错误提示由 http 拦截器统一处理
  } finally {
    if (seq === searchSeq) optionsLoading.value = false
  }
}

function onSelectChange(id: number | null) {
  const member = options.value.find((item) => item.id === id) || null
  newGameId.value = ''
  emit('select', member)
}

async function onSubmit() {
  if (!props.selected) {
    ElMessage.warning('请先选择要改名的常驻成员')
    return
  }
  const newId = newGameId.value.trim()
  if (!newId) {
    ElMessage.warning('请输入新的游戏 ID')
    return
  }
  if (newId === props.selected.name) {
    ElMessage.warning('新 ID 与当前 ID 相同')
    return
  }
  submitting.value = true
  try {
    await createGameIdRequest(props.selected.id, {
      expected_old_game_id: props.selected.name,
      new_game_id: newId,
    })
    ElMessage.success('申请已提交，等待管理员审核')
    newGameId.value = ''
    emit('submitted')
  } catch {
    // 错误提示由 http 拦截器统一处理；输入保留，便于核对后重试
  } finally {
    submitting.value = false
  }
}

// 切换成员时同步下拉选中值（父组件可能因提交后刷新而重置选择）
watch(
  () => props.selected,
  (member) => {
    selectedId.value = member ? member.id : null
    if (member && !options.value.some((item) => item.id === member.id)) {
      options.value = [member, ...options.value]
    }
  },
)

onMounted(() => searchMembers(''))
</script>

<style scoped src="./game-id-shared.css"></style>
