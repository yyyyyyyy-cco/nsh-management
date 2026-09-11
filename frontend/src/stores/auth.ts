/** 认证状态管理：Token 持久化、用户信息、登录/登出。 */
import { defineStore } from 'pinia'

import { getMe, login as apiLogin } from '@/api/auth'
import type { UserInfo } from '@/types/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as UserInfo | null,
    // 最近一次 fetchMe 成功的时间戳（内存态）：用于短时间窗口内的重复调用去重
    meFetchedAt: 0,
  }),
  getters: {
    isAdmin: (state) => state.user?.role === 'admin' || state.user?.role === 'developer',
    isDeveloper: (state) => state.user?.role === 'developer',
    isLoggedIn: (state) => Boolean(state.token),
  },
  actions: {
    async login(username: string, password: string) {
      const data = await apiLogin(username, password)
      this.token = data.access_token
      this.user = data.user
      this.meFetchedAt = Date.now()
      localStorage.setItem('token', data.access_token)
    },
    async fetchMe(options?: { force?: boolean }) {
      if (!this.token) return
      // 路由守卫与 MainLayout 挂载会在刷新页面时先后调用：5 秒窗口内已有用户信息则跳过，
      // 避免 /auth/me 并发两次；force 用于强制刷新（如需）
      if (!options?.force && this.user && Date.now() - this.meFetchedAt < 5000) return
      this.user = await getMe()
      this.meFetchedAt = Date.now()
    },
    clear() {
      this.token = ''
      this.user = null
      this.meFetchedAt = 0
      localStorage.removeItem('token')
    },
  },
})
