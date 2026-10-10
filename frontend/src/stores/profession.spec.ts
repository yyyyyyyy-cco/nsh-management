/** 职业目录 store：加载、启用过滤、排序序号与色彩水合（mock API）。 */
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { getProfessions } from '@/api/professions'
import type { ProfessionOut } from '@/types/profession'
import { profColor } from '@/utils/profession'
import { useProfessionStore } from './profession'

vi.mock('@/api/professions', () => ({ getProfessions: vi.fn() }))

const mockedGet = vi.mocked(getProfessions)

function item(name: string, sortOrder: number, color: string, isActive = true): ProfessionOut {
  return { id: sortOrder, name, sort_order: sortOrder, color, is_active: isActive, created_at: '2026-10-10T00:00:00Z' }
}

const CATALOG: ProfessionOut[] = [
  item('铁衣', 1, '#ffc800'),
  item('素问', 2, '#FF9CF2'),
  item('旧职业', 3, '#123456', false),
]

beforeEach(() => {
  setActivePinia(createPinia())
  mockedGet.mockReset()
})

describe('useProfessionStore', () => {
  it('load：全量列表 + 启用过滤（顺序由后端目录给定）', async () => {
    mockedGet.mockResolvedValue(CATALOG)
    const store = useProfessionStore()
    await store.load()
    expect(store.list).toHaveLength(3)
    expect(store.activeNames).toEqual(['铁衣', '素问'])
    expect(store.orderIndex('素问')).toBe(1)
  })

  it('load：色彩缓存水合包含停用职业（历史数据仍需原色显示）', async () => {
    mockedGet.mockResolvedValue(CATALOG)
    await useProfessionStore().load()
    expect(profColor('铁衣')).toBe('#ffc800')
    expect(profColor('旧职业')).toBe('#123456')
  })

  it('orderIndex：未知职业排在末尾（大数，不再是 indexOf=-1 排最前）', async () => {
    mockedGet.mockResolvedValue(CATALOG)
    const store = useProfessionStore()
    await store.load()
    expect(store.orderIndex('素问')).toBeLessThan(store.orderIndex('不存在的职业'))
  })

  it('ensureLoaded：并发去重且成功后短路', async () => {
    mockedGet.mockResolvedValue(CATALOG)
    const store = useProfessionStore()
    await Promise.all([store.ensureLoaded(), store.ensureLoaded()])
    await store.ensureLoaded()
    expect(mockedGet).toHaveBeenCalledTimes(1)
    expect(store.loaded).toBe(true)
  })

  it('ensureLoaded：失败不置 loaded（下次调用自动重试）', async () => {
    mockedGet.mockRejectedValueOnce(new Error('network'))
    const store = useProfessionStore()
    await expect(store.ensureLoaded()).rejects.toThrow('network')
    expect(store.loaded).toBe(false)
    mockedGet.mockResolvedValue(CATALOG)
    await store.ensureLoaded()
    expect(store.loaded).toBe(true)
  })
})
