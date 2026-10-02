<template>
  <el-dialog v-model="visible" title="分配未排表成员" width="560px" append-to-body>
    <div class="adjust-tip">
      将未排表成员手动分配到目标队伍。调整保存在<b>分析副本</b>中，不会修改正式排表。
    </div>
    <el-select aria-label="选择目标队伍" v-model="adjustTarget" placeholder="选择目标队伍" size="small" style="width: 100%">
      <el-option
        v-for="t in teams"
        :key="`${t.category}:${t.team_index}`"
        :label="t.squad_name"
        :value="`${t.category}:${t.team_index}`"
      />
    </el-select>
    <div class="adjust-members">
      <template v-if="members.length">
        <el-checkbox-group v-model="adjustSelected">
          <el-checkbox v-for="m in members" :key="m.player_name" :value="m.player_name">
            <span class="adjust-member__name">{{ m.player_name }}</span>
            <span class="adjust-member__prof" :style="{ color: profColor(m.profession ?? '') }">{{ m.profession || '未知' }}</span>
          </el-checkbox>
        </el-checkbox-group>
      </template>
      <EmptyState v-else description="未排表成员已全部调整" :image-size="60" />
    </div>
    <template #footer>
      <el-button size="small" @click="visible = false">取消</el-button>
      <el-button
        size="small"
        type="primary"
        :disabled="!adjustTarget || !adjustSelected.length"
        :loading="saving"
        @click="onConfirm"
      >确定分配</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

import type { SquadAnalysis, SquadMember } from '@/types/matchData'

import { profColor } from './analysis'
import EmptyState from '@/components/common/EmptyState.vue'

defineProps<{ members: SquadMember[]; teams: SquadAnalysis[]; saving: boolean }>()

const emit = defineEmits<{ confirm: [names: string[], target: string] }>()

const visible = defineModel<boolean>({ required: true })

const adjustTarget = ref('')
const adjustSelected = ref<string[]>([])

// 打开时重置表单（与父组件原 openAdjustDialog 行为一致）
watch(visible, (v) => {
  if (v) {
    adjustTarget.value = ''
    adjustSelected.value = []
  }
})

function onConfirm() {
  if (!adjustTarget.value || !adjustSelected.value.length) return
  emit('confirm', adjustSelected.value, adjustTarget.value)
}
</script>

<style scoped>
/* ===== 分配未排表成员 ===== */
.adjust-tip {
  font-size: 12px;
  color: var(--ink-500);
  margin-bottom: 10px;
  line-height: 1.6;
}

.adjust-tip b {
  color: var(--gold-700);
}

.adjust-members {
  margin-top: 12px;
  max-height: 260px;
  overflow-y: auto;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  background: var(--ink-bg-cream);
}

.adjust-member__name {
  font-size: 13px;
}

.adjust-member__prof {
  font-size: 12px;
  margin-left: 6px;
}
</style>
