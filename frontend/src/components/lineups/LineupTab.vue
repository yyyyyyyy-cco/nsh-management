<template>
  <div class="lineup-tab">
    <!-- 管理员：拖拽编排（保存后刷新总览） -->
    <LineupEditor v-if="isAdmin" :schedule-id="scheduleId" @saved="loadOverview" />

    <!-- 排表总览（管理员与帮众均可见） -->
    <el-card v-loading="loading" shadow="never" class="overview">
      <template #header>排表总览（帮众按姓名查找所在位置）</template>
      <el-empty v-if="!loading && !overview.length" description="排表中暂无成员" />
      <el-table v-else :data="overview" size="small" max-height="360">
        <el-table-column prop="member_name" label="姓名" width="140" />
        <el-table-column label="备注" min-width="120">
          <template #default="{ row }">{{ row.remark || '-' }}</template>
        </el-table-column>
        <el-table-column prop="position" label="位置" min-width="160" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { getLineup } from '@/api/lineups'
import { useAuthStore } from '@/stores/auth'
import type { LineupTeam } from '@/types/lineup'
import LineupEditor from './LineupEditor.vue'

const props = defineProps<{ scheduleId: number }>()

const auth = useAuthStore()
const isAdmin = computed(() => auth.isAdmin)
const loading = ref(false)
const teams = ref<LineupTeam[]>([])

const overview = computed(() =>
  teams.value.flatMap((t) =>
    t.slots
      .map((slot, si) => {
        if (!slot.member_name) return null
        return {
          member_name: slot.member_name,
          remark: slot.remark,
          position: `${t.category}${t.team_index + 1}队 · ${si + 1}号位`,
        }
      })
      .filter((x): x is { member_name: string; remark: string; position: string } => x !== null),
  ),
)

async function loadOverview() {
  loading.value = true
  try {
    const lineup = await getLineup(props.scheduleId)
    teams.value = lineup.data
  } finally {
    loading.value = false
  }
}

onMounted(loadOverview)
</script>

<style scoped>
.overview {
  border-radius: 8px;
}
</style>
