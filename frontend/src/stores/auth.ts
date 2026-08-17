/** 认证状态管理：Token 持久化、用户信息、登录/登出。 */
import { defineStore } from 'pinia'

import { getMe, login as apiLogin } from '@/api/auth'
import type { UserInfo } from '@/types/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as UserInfo | null,
  }),
  getters: {
    isAdmin: (state) => state.user?.role === 'admin' || state.user?.role === 'developer',
    isLoggedIn: (state) => Boolean(state.token),
  },
  actions: {
    async login(username: string, password: string) {
      const data = await apiLogin(username, password)
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('token', data.access_token)
    },
    async fetchMe() {
      if (!this.token) return
      this.user = await getMe()
    },
    clear() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    },
  },
})
