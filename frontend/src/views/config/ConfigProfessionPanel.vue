<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>职业目标人数配置</span>
        <el-button type="primary" :loading="saving" @click="onSave">保存配置</el-button>
      </div>
    </template>
    <p class="tip">配置各职业的目标人数，用于出勤库的职业缺口分析。</p>

    <!-- 移动端（≤768px）：职业配置行列表（目标人数 + 说明） -->
    <div v-if="isMobile" class="cfg-rows">
      <div v-for="row in professionConfigs" :key="row.profession" class="cfg-row">
        <div class="cfg-row__main">
          <span class="prof-cell">
            <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
            {{ row.profession }}
          </span>
          <el-input-number aria-label="目标人数" v-model="row.target_count" :min="0" :max="999" size="small" class="cfg-num" />
        </div>
        <el-input
          v-model="row.remark"
          placeholder="说明（可选）"
          size="small"
          maxlength="255"
          clearable
          class="cfg-remark"
        />
      </div>
    </div>

    <!-- 桌面端：表格形态保持不变 -->
    <el-table v-else :data="professionConfigs" border>
      <el-table-column prop="profession" label="职业" min-width="100">
        <template #default="{ row }">
          <span class="prof-cell">
            <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
            {{ row.profession }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="目标人数" min-width="150">
        <template #default="{ row }">
          <el-input-number
            v-model="row.target_count"
            :min="0"
            :max="999"
            size="small"
            style="width: 120px"
          />
        </template>
      </el-table-column>
      <el-table-column label="说明">
        <template #default="{ row }">
          <el-input
            v-model="row.remark"
            placeholder="说明（可选）"
            size="small"
            maxlength="255"
            clearable
          />
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { batchUpdateProfessionConfigs, getProfessionConfigs } from '@/api/config'
import type { ProfessionConfig } from '@/types/config'
import { profColor } from '@/utils/profession'

defineProps<{ isMobile: boolean }>()

const saving = ref(false)
const professionConfigs = ref<ProfessionConfig[]>([])

onMounted(async () => {
  professionConfigs.value = await getProfessionConfigs()
})

async function onSave() {
  saving.value = true
  try {
    const configs = professionConfigs.value.map((c) => ({
      profession: c.profession,
      target_count: c.target_count,
      remark: c.remark,
    }))
    const result = await batchUpdateProfessionConfigs(configs)
    ElMessage.success(result.message)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tip {
  color: var(--ink-400);
  font-size: 13px;
  margin-bottom: 16px;
}

.prof-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--ink-900);
}

.prof-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ===== 移动端行列表（isMobile 时渲染，替换表格） ===== */
.cfg-rows {
  display: flex;
  flex-direction: column;
  touch-action: manipulation;
}

.cfg-row {
  padding: 12px 2px;
  border-bottom: 1px solid var(--edge-faint);
}

.cfg-row:last-child {
  border-bottom: none;
}

.cfg-row__main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.cfg-row__main .prof-cell {
  font-weight: 600;
  color: var(--ink-800);
}

.cfg-num {
  width: 120px;
  flex-shrink: 0;
}

.cfg-remark {
  margin-top: 8px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .card-header {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
