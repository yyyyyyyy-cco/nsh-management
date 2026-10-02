/** Axios 封装：Token 注入、统一错误处理、401 跳转登录。 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

/** 从响应体中提取错误消息（兼容 {message} 与 {detail} 两种格式）。 */
function extractErrorMessage(error: unknown): string {
  const data = (error as { response?: { data?: { message?: string; detail?: string } } })?.response?.data
  return data?.message || data?.detail || '网络错误，请稍后重试'
}

/** 401 跳转去重锁：并发 401 只处理一次，避免重复提示与重复跳转（短暂置位后自动复位）。 */
let authRedirectPending = false

http.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const status = error.response?.status
    // 这两个接口的 401 表示**凭证本身不对**（登录失败 / 改密时当前密码错误），
    // 不是「登录已过期」——若按过期处理会把用户强行登出并给出误导提示。
    const url = String(error.config?.url ?? '')
    const isCredentialCheck = url.includes('/auth/login') || url.includes('/auth/password')

    // 登录请求的错误（凭证错误、账号锁定、网络异常等）统一交由登录页展示
    if (isCredentialCheck) {
      return Promise.reject(error)
    }

    if (status === 401) {
      if (authRedirectPending) return Promise.reject(error)
      authRedirectPending = true
      setTimeout(() => {
        authRedirectPending = false
      }, 1000)
      // 非登录接口 401：Token 过期，清除本地凭证并跳转登录页
      const auth = useAuthStore()
      auth.clear()
      ElMessage.error('登录已过期，请重新登录')
      const { default: router } = await import('@/router')
      router.push({ name: 'login', query: { redirect: window.location.pathname + window.location.search } })
    } else {
      ElMessage.error(extractErrorMessage(error))
    }
    return Promise.reject(error)
  },
)

export default http
