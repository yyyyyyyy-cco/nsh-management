/** 表格密度偏好：标准 / 紧凑（顶栏全局开关切换，localStorage 持久化）。 */
import { ref } from 'vue'

export type TableDensity = 'standard' | 'compact'

const STORAGE_KEY = 'table-density'

/** 模块级单例：全站共享同一份密度偏好 */
const density = ref<TableDensity>(localStorage.getItem(STORAGE_KEY) === 'compact' ? 'compact' : 'standard')

/** 应用到 <html data-table-density>，element-plus.css 按档位覆盖 el-table 密度 */
document.documentElement.dataset.tableDensity = density.value

export function useTableDensity() {
  function toggle() {
    density.value = density.value === 'compact' ? 'standard' : 'compact'
    localStorage.setItem(STORAGE_KEY, density.value)
    document.documentElement.dataset.tableDensity = density.value
  }
  return { density, toggle }
}
