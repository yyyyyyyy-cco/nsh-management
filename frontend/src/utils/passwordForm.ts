/**
 * 自助改密表单的**纯校验逻辑**（合规化计划 W4-11）。
 *
 * 为什么单独抽出：`el-form` 的 `validate()` 在不同版本下的返回值语义不一致（本轮实测 Promise 形式下
 * 校验失败仍会走到提交），把**闸门**放在这个纯函数里，行为确定且可脱离 DOM 测试；
 * Element Plus 的 `rules` 只负责界面错误提示（同一批谓词，避免口径分叉）。
 *
 * 与服务端 `app/core/password_policy.py` 的关系：此处只做**前端即时反馈**，
 * 权威判定仍在服务端（长度 8–128、弱口令词表、不得含登录名）。前端不做词表校验，
 * 只做长度 / 必填 / 两次一致 / 与当前不同——避免把服务端口径复制到前端（AGENTS §2.1）。
 */
import type { FormItemRule } from 'element-plus'

export const PASSWORD_MIN_LENGTH = 8
export const PASSWORD_MAX_LENGTH = 128

export interface PasswordFormValues {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

export function requiredError(value: string, label: string): string | null {
  return value ? null : `请输入${label}`
}

export function lengthError(value: string, label = '新密码'): string | null {
  if (!value) return null
  return value.length >= PASSWORD_MIN_LENGTH && value.length <= PASSWORD_MAX_LENGTH
    ? null
    : `${label}长度需为 ${PASSWORD_MIN_LENGTH}–${PASSWORD_MAX_LENGTH} 位`
}

export function sameAsCurrentError(value: string, current: string): string | null {
  return value && value === current ? '新密码不能与当前密码相同' : null
}

export function mismatchError(value: string, next: string): string | null {
  return value !== next ? '两次输入的新密码不一致' : null
}

/** 返回首个错误消息；`null` 表示可以提交。 */
export function validatePasswordForm(values: PasswordFormValues): string | null {
  return (
    requiredError(values.currentPassword, '当前密码') ??
    requiredError(values.newPassword, '新密码') ??
    lengthError(values.newPassword) ??
    sameAsCurrentError(values.newPassword, values.currentPassword) ??
    requiredError(values.confirmPassword, '新密码') ??
    mismatchError(values.confirmPassword, values.newPassword)
  )
}

/** 构建 el-form 展示用规则（谓词与上面完全一致，只做界面提示）。 */
export function buildPasswordRules(values: () => PasswordFormValues): Record<string, FormItemRule[]> {
  const rule = (validate: (value: string) => string | null): FormItemRule => ({
    validator: (_rule, value, callback) => {
      const message = validate(String(value ?? ''))
      if (message) callback(new Error(message))
      else callback()
    },
    trigger: ['blur', 'change'],
  })
  return {
    currentPassword: [rule((v) => requiredError(v, '当前密码'))],
    newPassword: [
      rule((v) => requiredError(v, '新密码')),
      rule(lengthError),
      rule((v) => sameAsCurrentError(v, values().currentPassword)),
    ],
    confirmPassword: [
      rule((v) => requiredError(v, '新密码')),
      rule((v) => mismatchError(v, values().newPassword)),
    ],
  }
}