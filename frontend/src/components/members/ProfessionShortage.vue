<template>
  <div v-if="shortages.length" class="prof-shortage">
    <div class="prof-shortage__title">
      <el-icon><WarningFilled /></el-icon>
      <span>缺少职业</span>
    </div>
    <div class="prof-shortage__items">
      <span v-for="s in shortages" :key="s.profession" class="prof-shortage__chip">
        <i class="prof-shortage__dot" :style="{ background: profColor(s.profession) }" />
        <span class="prof-shortage__name">{{ s.profession }}</span>
        <em class="prof-shortage__num num">缺 {{ s.missing }} 人</em>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'

import { getProfessionConfigs } from '@/api/config'
import { getProfessionStats, type ProfessionStat } from '@/api/members'
import type { ProfessionConfig } from '@/types/config'

/** 父组件数据变更后通过递增 refreshKey 触发本组件重新拉取。 */
const props = defineProps<{ refreshKey?: number }>()

/** 职业色映射（依据 ui-style-guide §9，全站一致）。 */
const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

const configs = ref<ProfessionConfig[]>([])
const stats = ref<ProfessionStat[]>([])

/** 缺少的职业：系统配置目标人数 > 常驻库主职业实际人数。 */
const shortages = computed(() => {
  const actual = new Map(stats.value.map((s) => [s.profession, s.count]))
  return configs.value
    .filter((c) => c.target_count > 0)
    .map((c) => ({
      profession: c.profession,
      missing: c.target_count - (actual.get(c.profession) ?? 0),
    }))
    .filter((s) => s.missing > 0)
})

function profColor(prof: string) {
  return PROF_COLORS[prof] || '#999'
}

async function load() {
  try {
    const [c, p] = await Promise.all([getProfessionConfigs(), getProfessionStats()])
    configs.value = c
    stats.value = p
  } catch {
    // 错误提示已由 http 拦截器统一处理
  }
}

watch(() => props.refreshKey, load, { immediate: true })
</script>

<style scoped>
.prof-shortage {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px 12px;
  margin-bottom: 14px;
  padding: 10px 14px;
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-lg);
  background: linear-gradient(90deg, var(--gold-50), var(--ink-bg-paper));
}

.prof-shortage__title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-serif);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--gold-700);
}

.prof-shortage__items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.prof-shortage__chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: var(--radius-xl);
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  font-size: 12px;
  color: var(--ink-800);
}

.prof-shortage__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.prof-shortage__num {
  font-style: normal;
  font-weight: 700;
  color: var(--gold-600);
}
</style>
