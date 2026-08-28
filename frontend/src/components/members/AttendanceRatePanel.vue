<template>
  <el-card shadow="never" class="rate-panel">
    <template #header>
      <div class="panel-header">
        <span>出勤率统计</span>
      </div>
    </template>
    <el-table :data="rateItems" size="small">
      <el-table-column prop="name" label="ID" min-width="110">
        <template #default="{ row }">
          <span class="member-name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="main_profession" label="职业" min-width="90">
        <template #default="{ row }">
          <span class="prof-name" :style="{ color: profColor(row.main_profession) }">{{ row.main_profession }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="attendance_rate" label="出勤率" min-width="180" sortable>
        <template #default="{ row }">
          <div v-if="row.attendance_rate !== null" class="rate-cell">
            <el-progress
              :percentage="row.attendance_rate * 100"
              :stroke-width="8"
              :show-text="false"
              :color="row.attendance_rate < 0.5 ? '#c0392b' : '#c9a13b'"
              class="rate-bar"
            />
            <span class="rate-num num" :class="{ warn: row.attendance_rate < 0.5 }">
              {{ (row.attendance_rate * 100).toFixed(1) }}%
            </span>
          </div>
          <span v-else class="none">无记录</span>
        </template>
      </el-table-column>
      <el-table-column label="正常/请假" min-width="100">
        <template #default="{ row }">
          <span class="counts"><em class="num">{{ row.normal_count }}</em> / <em class="num">{{ row.leave_count }}</em></span>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getAttendanceRate, type AttendanceRateItem } from '@/api/members'
import { profColor } from '@/utils/profession'

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

.member-name {
  font-weight: 600;
  color: var(--ink-900);
}

.prof-name {
  font-weight: 600;
  font-size: 12.5px;
}

.rate-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rate-bar {
  flex: 1;
}

.rate-num {
  width: 52px;
  text-align: right;
  font-weight: 700;
  color: var(--gold-700);
}

.warn {
  color: var(--cinnabar);
}

.none {
  color: var(--ink-400);
}

.counts {
  color: var(--ink-500);
}

.counts em {
  font-style: normal;
  font-weight: 600;
  color: var(--ink-700);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .panel-header {
    flex-wrap: wrap;
    gap: 4px 12px;
  }
}
</style>
