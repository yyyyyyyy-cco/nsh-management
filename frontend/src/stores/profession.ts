/** 职业目录状态：全站职业清单/展示顺序的单一分发点。
 *
 * 权威源为数据库（GET /professions）。加载成功后把色彩缓存水合到 `utils/profession`
 * （含停用职业，历史数据仍需原色显示）；组件经 `activeNames` 取启用职业、
 * 经 `orderIndex` 取展示顺序，禁止任何组件自行维护职业清单。
 */
import { defineStore } from 'pinia'

import { getProfessions } from '@/api/professions'
import type { ProfessionOut } from '@/types/profession'
import { setProfessionColors } from '@/utils/profession'

export const useProfessionStore = defineStore('profession', {
  state: () => ({
    /** 全量目录（含停用），按后端 (sort_order, id) 顺序。 */
    list: [] as ProfessionOut[],
    loaded: false,
    /** 进行中的加载（并发去重；不进入响应式依赖的消费面）。 */
    loading: null as Promise<void> | null,
  }),
  getters: {
    /** 启用职业（按目录顺序）。 */
    activeList: (state) => state.list.filter((p) => p.is_active),
    /** 启用职业名（下拉/筛选/排表分组等消费面统一取此值）。 */
    activeNames(): string[] {
      return this.activeList.map((p) => p.name)
    },
    orderIndexMap(): Map<string, number> {
      return new Map(this.activeNames.map((name, index) => [name, index]))
    },
  },
  actions: {
    /** 展示顺序序号；未知职业返回末位大数（排序并列时保持稳定，不再出现 indexOf=-1 排最前）。 */
    orderIndex(name: string): number {
      return this.orderIndexMap.get(name) ?? Number.MAX_SAFE_INTEGER
    },
    async load() {
      const items = await getProfessions()
      this.list = items
      // 色彩缓存包含停用职业：历史记录（出勤/录屏/比赛数据）仍按原色显示
      setProfessionColors(Object.fromEntries(items.map((p) => [p.name, p.color])))
      this.loaded = true
    },
    /** 首次加载（并发去重）；失败不置 loaded，由下一次导航/调用自动重试。 */
    async ensureLoaded() {
      if (this.loaded) return
      if (!this.loading) {
        this.loading = this.load().finally(() => {
          this.loading = null
        })
      }
      return this.loading
    },
    /** 目录写操作后强制重拉。 */
    async refresh() {
      await this.load()
    },
  },
})
