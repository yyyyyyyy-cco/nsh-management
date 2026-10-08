<template>
  <!-- 表格/行列表骨架：与最终形态同形状（reserves space，防布局抖动），装饰性元素对读屏隐藏 -->
  <div class="sk-table" :class="`sk-table--${variant}`" aria-hidden="true">
    <div v-if="variant === 'table'" class="sk-table__head">
      <span v-for="c in columns" :key="c" class="sk sk-line sk-table__cell" :style="{ width: cellWidth(c) }" />
    </div>
    <div v-for="i in rows" :key="i" class="sk-table__row">
      <template v-if="variant === 'table'">
        <span v-for="c in columns" :key="c" class="sk sk-line sk-table__cell" :style="{ width: cellWidth(c) }" />
      </template>
      <template v-else>
        <span class="sk sk-line sk-table__main" />
        <span class="sk sk-line sk-table__sub" />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    /** 行数 */
    rows?: number
    /** table：桌面表格行；rows：窄屏行列表（两行式） */
    variant?: 'table' | 'rows'
    /** 表格列数（table 变体） */
    columns?: number
  }>(),
  { rows: 5, variant: 'table', columns: 5 },
)

// 列宽循环预设（首个为窄列，模拟序号/标签列），避免每列等宽的死板感
const widths = ['9%', '26%', '18%', '22%', '10%']

function cellWidth(c: number): string {
  return widths[(c - 1) % widths.length]
}
</script>

<style scoped>
.sk-table {
  width: 100%;
}

/* ===== 桌面表格变体 ===== */
.sk-table__head {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 40px;
  padding: 0 12px;
  border-bottom: 1px solid var(--edge-soft);
}

.sk-table__head .sk {
  height: 10px;
  opacity: 0.75;
}

.sk-table--table .sk-table__row {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 44px;
  padding: 0 12px;
  border-bottom: 1px solid var(--edge-faint);
}

.sk-table--table .sk-table__row:last-child {
  border-bottom: none;
}

/* ===== 窄屏行列表变体（两行式） ===== */
.sk-table--rows .sk-table__row {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  gap: 10px;
  min-height: 64px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--edge-faint);
}

.sk-table--rows .sk-table__row:last-child {
  border-bottom: none;
}

.sk-table__main {
  width: 62%;
}

.sk-table__sub {
  width: 38%;
}

@media (max-width: 768px) {
  .sk-table--table .sk-table__row,
  .sk-table__head {
    gap: 10px;
  }
}
</style>
