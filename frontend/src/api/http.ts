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

http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.message || '网络错误，请稍后重试'
    if (status === 401) {
      const auth = useAuthStore()
      auth.clear()
      window.location.assign('/login')
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  },
)

export default http
