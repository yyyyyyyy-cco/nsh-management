/**
 * 自助改密对话框组件测试（合规化计划 W4-11）。
 *
 * 覆盖：渲染、四条前端校验（必填 / 长度 / 两次不一致 / 与当前密码相同）、
 * **成功路径的接口参数与事件契约**、失败路径不上报成功。
 * 接口通过 `vi.mock` 替换，不做真实网络请求。
 *
 * 实现说明：`el-dialog` 的内容经 teleport 渲染且组件为多根节点，VTU 的 `findAll('input')`
 * 不可靠；这里改为**直接驱动 document.body 中的真实 DOM 节点**（Element Plus 的表单校验仍真实执行），
 * 每个用例结束清空 body，避免用例间相互污染。
 */
import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import PasswordChangeDialog from './PasswordChangeDialog.vue'

const changePassword = vi.fn()

vi.mock('@/api/auth', () => ({
  changePassword: (...args: unknown[]) => changePassword(...args),
}))

let wrapper: ReturnType<typeof mount> | undefined

function mountDialog() {
  wrapper = mount(PasswordChangeDialog, {
    props: { modelValue: true },
    global: { plugins: [ElementPlus], stubs: { teleport: true } },
    attachTo: document.body,
  })
  return wrapper
}

function inputs(): HTMLInputElement[] {
  return Array.from(document.body.querySelectorAll('input'))
}

async function typeInto(index: number, value: string) {
  const input = inputs()[index]
  if (!input) throw new Error(`未找到第 ${index + 1} 个输入框（当前 ${inputs().length} 个）`)
  input.value = value
  input.dispatchEvent(new Event('input', { bubbles: true }))
  // 必须是 FocusEvent：Element Plus 的 `blur` 事件声明带参数校验，普通 Event 会触发
  // 「Invalid event arguments」告警
  input.dispatchEvent(new FocusEvent('blur', { bubbles: true }))
  await flushPromises()
}

async function fill(current: string, next: string, confirm = next) {
  await typeInto(0, current)
  await typeInto(1, next)
  await typeInto(2, confirm)
}

async function clickSubmit() {
  const button = Array.from(document.body.querySelectorAll('button')).find((b) =>
    (b.textContent || '').includes('确定修改'),
  )
  if (!button) throw new Error('未找到「确定修改」按钮')
  button.click()
  await flushPromises()
}

describe('PasswordChangeDialog', () => {
  beforeEach(() => {
    changePassword.mockReset()
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
    document.body.innerHTML = ''
  })

  it('渲染标题与三个口令输入框', async () => {
    mountDialog()
    await flushPromises()
    expect(document.body.textContent).toContain('修改密码')
    expect(inputs()).toHaveLength(3)
    expect(document.body.textContent).toContain('不得为常见弱口令')
  })

  it('必填校验：空表单不调用接口', async () => {
    mountDialog()
    await flushPromises()
    await clickSubmit()
    expect(changePassword).not.toHaveBeenCalled()
  })

  it('长度校验：新密码短于 8 位不调用接口', async () => {
    mountDialog()
    await flushPromises()
    await fill('old-pass-2026', 'short7x')
    await clickSubmit()
    expect(changePassword).not.toHaveBeenCalled()
  })

  it('两次输入不一致时不调用接口', async () => {
    mountDialog()
    await flushPromises()
    await fill('old-pass-2026', 'new-pass-2026', 'new-pass-2027')
    await clickSubmit()
    expect(changePassword).not.toHaveBeenCalled()
  })

  it('新密码与当前密码相同时不调用接口', async () => {
    mountDialog()
    await flushPromises()
    await fill('same-pass-2026', 'same-pass-2026')
    await clickSubmit()
    expect(changePassword).not.toHaveBeenCalled()
  })

  it('成功路径：按后端字段名提交并关闭 + 通知父组件', async () => {
    changePassword.mockResolvedValue({ message: 'ok' })
    const local = mountDialog()
    await flushPromises()
    await fill('old-pass-2026', 'new-pass-2026')
    await clickSubmit()

    expect(changePassword).toHaveBeenCalledTimes(1)
    expect(changePassword).toHaveBeenCalledWith({
      current_password: 'old-pass-2026',
      new_password: 'new-pass-2026',
    })
    expect(local.emitted('update:modelValue')?.at(-1)).toEqual([false])
    expect(local.emitted('changed')).toHaveLength(1)
  })

  it('失败路径：接口报错时不通知父组件（错误提示由 http 拦截器统一给出）', async () => {
    changePassword.mockRejectedValue(new Error('当前密码不正确'))
    const local = mountDialog()
    await flushPromises()
    await fill('wrong-pass-2026', 'new-pass-2026')
    await clickSubmit()

    expect(changePassword).toHaveBeenCalledTimes(1)
    expect(local.emitted('changed')).toBeUndefined()
  })
})
