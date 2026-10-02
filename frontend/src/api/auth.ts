/** 认证相关接口。 */
import http from './http'
import type { UserInfo } from '@/types/auth'

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export function login(username: string, password: string): Promise<LoginResponse> {
  return http.post('/auth/login', { username, password })
}

export function getMe(): Promise<UserInfo> {
  return http.get('/auth/me')
}

export function logout(): Promise<{ message: string }> {
  return http.post('/auth/logout')
}

/** 自助修改口令（需提供当前口令）。成功后后端会使**所有旧令牌失效**，调用方需重新登录。 */
export function changePassword(payload: {
  current_password: string
  new_password: string
}): Promise<{ message: string }> {
  return http.post('/auth/password', payload)
}
