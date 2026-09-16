<template>
  <div class="lineup-tab">
    <!-- 管理员：拖拽编排（保存后刷新总览） -->
    <LineupEditor ref="editorRef" v-if="isAdmin" :schedule-id="scheduleId" @saved="overviewRef?.reload()" />

    <!-- 排表总览（管理员与帮众均可见） -->
    <LineupOverviewPanel ref="overviewRef" :schedule-id="scheduleId" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import { useAuthStore } from '@/stores/auth'
import LineupEditor from './LineupEditor.vue'
import LineupOverviewPanel from './LineupOverviewPanel.vue'

defineProps<{ scheduleId: number }>()

const auth = useAuthStore()
const isAdmin = computed(() => auth.isAdmin)

const editorRef = ref<InstanceType<typeof LineupEditor>>()
const overviewRef = ref<InstanceType<typeof LineupOverviewPanel>>()

/** Tab 重新激活时刷新（出勤库变动后补人/成员可同步到候选池与总览）。 */
function reload() {
  overviewRef.value?.reload()
  editorRef.value?.reload()
}

defineExpose({ reload })
</script>
