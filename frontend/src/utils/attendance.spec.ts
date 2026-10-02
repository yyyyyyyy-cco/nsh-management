import { describe, expect, it } from 'vitest'

import {
  ATTENDANCE_LOW_THRESHOLD,
  attendanceProgressColor,
  formatRatePercent,
  isLowAttendance,
} from './attendance'

describe('出勤率展示口径（utils/attendance.ts 为前端唯一来源）', () => {
  it('阈值常量为 0.5（此前散落在 3 个组件共 4 处）', () => {
    expect(ATTENDANCE_LOW_THRESHOLD).toBe(0.5)
  })

  it('isLowAttendance：严格小于阈值才算低，阈值本身不算；无记录不告警', () => {
    expect(isLowAttendance(0)).toBe(true)
    expect(isLowAttendance(0.4999)).toBe(true)
    expect(isLowAttendance(ATTENDANCE_LOW_THRESHOLD)).toBe(false) // 边界：0.5 不告警
    expect(isLowAttendance(0.5 + Number.EPSILON)).toBe(false)
    expect(isLowAttendance(1)).toBe(false)
    expect(isLowAttendance(null)).toBe(false)
    expect(isLowAttendance(undefined)).toBe(false)
  })

  it('attendanceProgressColor：低出勤告警红，其余雅金主色', () => {
    expect(attendanceProgressColor(0.3)).toBe('#c0392b')
    expect(attendanceProgressColor(0.5)).toBe('#c9a13b')
    expect(attendanceProgressColor(0.99)).toBe('#c9a13b')
    expect(attendanceProgressColor(null)).toBe('#c9a13b')
  })

  it('formatRatePercent 默认 1 位小数（常驻库列表 / 成员详情口径）', () => {
    expect(formatRatePercent(1)).toBe('100.0%')
    expect(formatRatePercent(0.5)).toBe('50.0%')
    expect(formatRatePercent(0.6667)).toBe('66.7%')
    expect(formatRatePercent(0)).toBe('0.0%')
  })

  it('formatRatePercent 传 0 位小数时取整（首页出勤排行口径）', () => {
    expect(formatRatePercent(0.6667, 0)).toBe('67%')
    expect(formatRatePercent(0.995, 0)).toBe('100%')
    expect(formatRatePercent(0.994, 0)).toBe('99%')
    expect(formatRatePercent(0, 0)).toBe('0%')
  })

  it('无记录返回 fallback（默认 -，可覆盖为「无记录」）', () => {
    expect(formatRatePercent(null)).toBe('-')
    expect(formatRatePercent(undefined)).toBe('-')
    expect(formatRatePercent(null, 1, '无记录')).toBe('无记录')
  })
})