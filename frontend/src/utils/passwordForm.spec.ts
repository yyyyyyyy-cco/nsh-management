/**
 * 改密表单纯校验用例（合规化计划 W4-11）。
 * 纯逻辑、无 DOM、无第三方运行时依赖，可稳定真跑。
 */
import { describe, expect, it } from 'vitest'

import {
  PASSWORD_MAX_LENGTH,
  PASSWORD_MIN_LENGTH,
  lengthError,
  validatePasswordForm,
  type PasswordFormValues,
} from './passwordForm'

const ok: PasswordFormValues = {
  currentPassword: 'old-pass-2026',
  newPassword: 'new-pass-2026',
  confirmPassword: 'new-pass-2026',
}

function values(patch: Partial<PasswordFormValues>): PasswordFormValues {
  return { ...ok, ...patch }
}

describe('validatePasswordForm', () => {
  it('合法输入返回 null', () => {
    expect(validatePasswordForm(ok)).toBeNull()
  })

  it('当前密码为空时提示', () => {
    expect(validatePasswordForm(values({ currentPassword: '' }))).toBe('请输入当前密码')
  })

  it('新密码为空时提示', () => {
    expect(validatePasswordForm(values({ newPassword: '', confirmPassword: '' }))).toBe('请输入新密码')
  })

  it('新密码短于下限时提示', () => {
    expect(validatePasswordForm(values({ newPassword: 'short7x', confirmPassword: 'short7x' }))).toContain(
      `${PASSWORD_MIN_LENGTH}–${PASSWORD_MAX_LENGTH}`,
    )
  })

  it('新密码超过上限时提示', () => {
    const tooLong = 'a'.repeat(PASSWORD_MAX_LENGTH + 1)
    expect(validatePasswordForm(values({ newPassword: tooLong, confirmPassword: tooLong }))).toContain(
      '长度',
    )
  })

  it('恰好等于下限/上限时通过', () => {
    const min = 'a'.repeat(PASSWORD_MIN_LENGTH)
    expect(validatePasswordForm(values({ newPassword: min, confirmPassword: min }))).toBeNull()
    const max = 'b'.repeat(PASSWORD_MAX_LENGTH)
    expect(validatePasswordForm(values({ newPassword: max, confirmPassword: max }))).toBeNull()
  })

  it('新密码与当前密码相同时提示', () => {
    const same = 'same-pass-2026'
    expect(
      validatePasswordForm(values({ currentPassword: same, newPassword: same, confirmPassword: same })),
    ).toBe('新密码不能与当前密码相同')
  })

  it('两次输入不一致时提示', () => {
    expect(validatePasswordForm(values({ confirmPassword: 'other-pass-2026' }))).toBe(
      '两次输入的新密码不一致',
    )
  })

  it('长度校验不吞掉纯字母/纯数字口令（与服务端 6.2.5 口径一致）', () => {
    for (const pw of ['abcdefgh', '92713465', '!@#$%^&*']) {
      expect(lengthError(pw)).toBeNull()
      expect(validatePasswordForm(values({ newPassword: pw, confirmPassword: pw }))).toBeNull()
    }
  })
})