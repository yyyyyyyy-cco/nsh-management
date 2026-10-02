<template>
  <el-dialog v-model="visible" title="清理日志" width="420px">
    <p class="tip">删除指定天数之前的审计日志（文件日志按 10MB × 5 自动轮转，无需手动清理）。</p>
    <div class="clear-row">
      <span>清理</span>
      <el-input-number v-model="clearDays" :min="1" :max="3650" />
      <span>天前的日志</span>
    </div>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="danger" :loading="clearing" @click="$emit('confirm', clearDays)">确认清理</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ clearing: boolean }>()

defineEmits<{ confirm: [days: number] }>()

const visible = defineModel<boolean>({ required: true })

const clearDays = ref(90)
</script>

<style scoped>
.clear-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tip {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--ink-500, #8a8378);
}
</style>
