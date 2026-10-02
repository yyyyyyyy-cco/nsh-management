import { describe, expect, it } from 'vitest'

import { MEMBER_STATUSES, PROFESSIONS, SCHEDULE_RESULTS, resultLabel, resultType } from './constants'

describe('业务常量（权威源：utils/constants.ts）', () => {
  it('职业共 11 种且无重复', () => {
    expect(PROFESSIONS).toHaveLength(11)
    expect(new Set(PROFESSIONS).size).toBe(11)
  })

  it('成员状态与赛程结果取值完整', () => {
    expect(MEMBER_STATUSES.map((s) => s.value)).toEqual(['formal', 'substitute'])
    expect(SCHEDULE_RESULTS.map((r) => r.value)).toEqual(['pending', 'win', 'lose', 'draw'])
  })
})

describe('resultLabel', () => {
  it('已知取值返回中文标签', () => {
    expect(resultLabel('pending')).toBe('待定')
    expect(resultLabel('win')).toBe('胜')
    expect(resultLabel('lose')).toBe('负')
    expect(resultLabel('draw')).toBe('平')
  })

  it('未知取值原样返回（便于暴露后端新增枚举）', () => {
    expect(resultLabel('unknown')).toBe('unknown')
    expect(resultLabel('')).toBe('')
  })
})

describe('resultType', () => {
  it('胜 success、负 danger、其余 info', () => {
    expect(resultType('win')).toBe('success')
    expect(resultType('lose')).toBe('danger')
    expect(resultType('draw')).toBe('info')
    expect(resultType('pending')).toBe('info')
    expect(resultType('unknown')).toBe('info')
  })
})
