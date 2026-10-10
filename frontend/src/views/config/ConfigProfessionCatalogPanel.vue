<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>职业目录</span>
        <el-button type="primary" :disabled="!createName.trim()" :loading="creating" @click="onCreate"
          >新增职业</el-button
        >
      </div>
    </template>
    <p class="tip">
      职业清单为全局共享（所有帮会）。新增/调整后全站下拉、筛选、排表与配色即时生效（无需发版）；停用的职业不再出现在选择器，历史数据保留原样。重命名会同步更新成员、职业配置与单场覆盖（出勤/录屏/比赛数据的历史记录保持原名）。
    </p>

    <div class="create-row">
      <el-input v-model="createName" maxlength="16" placeholder="职业名（≤16 字符）" class="create-name" />
      <el-color-picker v-model="createColor" aria-label="职业色" />
      <el-input-number
        v-model="createSort"
        :min="0"
        aria-label="排序（留空=末位）"
        placeholder="排序"
        class="create-sort"
      />
      <span class="create-hint">排序留空 = 追加末位</span>
    </div>

    <el-table :data="professionStore.list" border>
      <el-table-column label="职业名" :min-width="isMobile ? 96 : 140">
        <template #default="{ row }">
          <span class="prof-cell">
            <i class="prof-dot" :style="{ background: row.color }" />
            {{ row.name }}
            <el-tag v-if="!row.is_active" size="small" type="info">已停用</el-tag>
          </span>
        </template>
      </el-table-column>
      <el-table-column label="颜色" width="76" align="center">
        <template #default="{ row }">
          <el-color-picker :model-value="row.color" aria-label="职业色" @change="onColorChange(row, $event)" />
        </template>
      </el-table-column>
      <el-table-column label="排序" width="128">
        <template #default="{ row }">
          <el-input-number
            :model-value="row.sort_order"
            :min="0"
            size="small"
            style="width: 100px"
            @change="onSortChange(row, $event)"
          />
        </template>
      </el-table-column>
      <el-table-column label="启用" width="72" align="center">
        <template #default="{ row }">
          <el-switch :model-value="row.is_active" @change="onToggleActive(row, $event)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="88" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="onRename(row)">重命名</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { createProfession, updateProfession } from '@/api/professions'
import { useProfessionStore } from '@/stores/profession'
import type { ProfessionOut } from '@/types/profession'

defineProps<{ isMobile: boolean }>()

const professionStore = useProfessionStore()

const creating = ref(false)
const createName = ref('')
const createColor = ref('#c9a13b')
const createSort = ref<number | undefined>(undefined)

onMounted(() => {
  // 兜底：极端情况（直开本页）下目录尚未加载时补一次（失败静默，下次导航自动重试）
  void professionStore.ensureLoaded().catch(() => {})
})

/** 统一收口：执行写操作并刷新目录；失败（http 拦截器已提示）返回 false，不弹成功提示。 */
async function run(action: () => Promise<unknown>): Promise<boolean> {
  try {
    await action()
    await professionStore.refresh()
    return true
  } catch {
    return false
  }
}

async function onCreate() {
  const name = createName.value.trim()
  if (!name) return
  creating.value = true
  try {
    const payload = {
      name,
      color: createColor.value,
      ...(createSort.value == null ? {} : { sort_order: createSort.value }),
    }
    if (await run(() => createProfession(payload))) {
      ElMessage.success(`已新增职业「${name}」`)
      createName.value = ''
      createSort.value = undefined
    }
  } finally {
    creating.value = false
  }
}

async function onColorChange(row: ProfessionOut, value: unknown) {
  if (typeof value !== 'string' || !value || value === row.color) return
  if (await run(() => updateProfession(row.id, { color: value }))) {
    ElMessage.success(`「${row.name}」颜色已更新`)
  }
}

async function onSortChange(row: ProfessionOut, value: unknown) {
  if (typeof value !== 'number' || value === row.sort_order) return
  if (await run(() => updateProfession(row.id, { sort_order: value }))) {
    ElMessage.success('排序已更新')
  }
}

async function onToggleActive(row: ProfessionOut, value: unknown) {
  if (typeof value !== 'boolean' || value === row.is_active) return
  if (!value) {
    try {
      await ElMessageBox.confirm(
        `停用「${row.name}」后，新数据不可再选择该职业（历史数据保留）。确认停用？`,
        '停用职业',
        { type: 'warning' },
      )
    } catch {
      return // 取消：`:model-value` 绑定不会翻转开关
    }
  }
  if (await run(() => updateProfession(row.id, { is_active: value }))) {
    ElMessage.success(value ? `已启用「${row.name}」` : `已停用「${row.name}」`)
  }
}

async function onRename(row: ProfessionOut) {
  let newName: string
  try {
    const result = await ElMessageBox.prompt(
      '重命名将同步更新成员、职业配置与单场覆盖；出勤/录屏/比赛数据的历史记录保持原名。',
      `重命名「${row.name}」`,
      {
        inputValue: row.name,
        inputValidator: (v: string) => {
          const trimmed = (v || '').trim()
          if (!trimmed) return '职业名不能为空'
          if (trimmed.length > 16) return '职业名不超过 16 字符'
          return true
        },
      },
    )
    newName = result.value.trim()
  } catch {
    return // 取消
  }
  if (newName === row.name) return
  if (await run(() => updateProfession(row.id, { name: newName }))) {
    ElMessage.success(`已重命名为「${newName}」`)
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

.create-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.create-name {
  width: 200px;
}

.create-sort {
  width: 130px;
}

.create-hint {
  color: var(--ink-400);
  font-size: 12px;
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

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .card-header {
    flex-wrap: wrap;
    gap: 8px;
  }

  .create-name {
    flex: 1 1 100%;
    width: 100%;
  }
}
</style>
