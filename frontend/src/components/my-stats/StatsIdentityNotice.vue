<template>
  <div class="identity" :class="{ 'identity--conflict': !!conflict }">
    <!-- 冲突：停止自动合并，提供显式精确查询 -->
    <template v-if="conflict">
      <div class="identity__row">
        <el-icon class="identity__icon identity__icon--warn"><WarningFilled /></el-icon>
        <span class="identity__title">无法合并历史 ID</span>
      </div>
      <p class="identity__text">{{ conflict }}</p>
      <div class="identity__actions">
        <el-button size="small" type="primary" plain @click="emit('exact')">仅查此 ID</el-button>
      </div>
    </template>

    <!-- 合并成功 -->
    <template v-else-if="identity && identity.mode === 'merged'">
      <div class="identity__row">
        <el-icon class="identity__icon"><Connection /></el-icon>
        <span class="identity__title">已合并历史 ID</span>
      </div>
      <p class="identity__text">
        当前 ID <b class="identity__strong">{{ identity.current_game_id }}</b>；
        输入 <b class="identity__strong">{{ identity.query_player_name }}</b> 与全部关联 ID 查询结果一致，
        统计范围为合并后的最近 10 场（各场明细保留当时的 ID）。
      </p>
      <div class="identity__tags">
        <span class="identity__label">关联 ID</span>
        <el-tag
          v-for="alias in identity.aliases"
          :key="alias"
          size="small"
          effect="plain"
          :type="alias === identity.current_game_id ? 'success' : 'info'"
        >
          {{ alias }}{{ alias === identity.current_game_id ? '（当前）' : '' }}
        </el-tag>
      </div>
    </template>

    <!-- 原始按名查询 -->
    <template v-else-if="identity">
      <div class="identity__row">
        <el-icon class="identity__icon identity__icon--plain"><Search /></el-icon>
        <span class="identity__title">按记录 ID 查询</span>
      </div>
      <p class="identity__text">
        未找到该 ID 的已确认改名关系：结果按比赛记录中的原始 ID 查询，未确认个人归属，可能与同 ID 的其他玩家混合。
      </p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { Connection, Search, WarningFilled } from '@element-plus/icons-vue'

import type { PlayerIdentity } from '@/types/myStats'

defineProps<{
  identity: PlayerIdentity | null
  /** 合并冲突提示（非空时优先展示，并显示「仅查此 ID」入口） */
  conflict?: string | null
}>()

const emit = defineEmits<{ exact: [] }>()
</script>

<style scoped>
.identity {
  padding: 12px 14px;
  border: 1px solid var(--edge-soft);
  border-left: 3px solid var(--gold-400);
  border-radius: var(--radius-sm);
  background: var(--gold-50);
}

.identity--conflict {
  border-left-color: var(--cinnabar);
  background: #fdf3f1;
}

.identity__row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.identity__icon {
  font-size: 16px;
  color: var(--gold-600);
}

.identity__icon--warn {
  color: var(--cinnabar);
}

.identity__icon--plain {
  color: var(--ink-400);
}

.identity__title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--ink-900);
}

.identity__text {
  margin: 6px 0 0;
  font-size: 12.5px;
  line-height: 1.75;
  color: var(--ink-600);
  overflow-wrap: anywhere;
}

.identity__strong {
  color: var(--ink-900);
}

.identity__tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.identity__label {
  font-size: 12px;
  color: var(--ink-400);
}

.identity__actions {
  margin-top: 8px;
}
</style>
