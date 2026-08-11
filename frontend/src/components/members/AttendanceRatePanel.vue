<template>
  <el-card shadow="never" class="rate-panel">
    <template #header>
      <div class="panel-header">
        <span>出勤率统计</span>
        <span class="sub">正常 / (正常 + 请假)，低于 50% 标红预警</span>
      </div>
    </template>
    <el-table :data="rateItems" size="small" max-height="240">
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="main_profession" label="职业" width="100" />
      <el-table-column label="出勤率" min-width="140">
        <template #default="{ row }">
          <span v-if="row.attendance_rate === null" class="none">无记录</span>
          <span v-else :class="{ warn: row.attendance_rate < 0.5 }">
            {{ (row.attendance_rate * 100).toFixed(1) }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column label="正常/请假" width="110">
        <template #default="{ row }">{{ row.normal_count }} / {{ row.leave_count }}</template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getAttendanceRate, type AttendanceRateItem } from '@/api/members'

const rateItems = ref<AttendanceRateItem[]>([])

onMounted(async () => {
  rateItems.value = await getAttendanceRate()
})
</script>

<style scoped>
.panel-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.sub {
  font-size: 12px;
  color: #6b7280;
  font-weight: normal;
}

.warn {
  color: #ef4444;
  font-weight: 600;
}

.none {
  color: #9ca3af;
}
</style>
