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
