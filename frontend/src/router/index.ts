/** 路由配置与守卫：未登录跳转登录页，已登录访问登录页跳回首页。 */
import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true, title: '登录' },
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
          meta: { title: '首页' },
        },
        {
          path: 'members',
          name: 'members',
          component: () => import('@/views/members/MemberListView.vue'),
          meta: { title: '常驻库', adminOnly: true },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (auth.isLoggedIn && !auth.user) {
    await auth.fetchMe().catch(() => auth.clear())
  }
  if (to.meta.adminOnly && !auth.isAdmin) {
    return { name: 'home' }
  }
  if (to.name === 'login' && auth.isLoggedIn) {
    return { name: 'home' }
  }
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${String(to.meta.title)} - 帮会联赛管理系统` : '帮会联赛管理系统'
})

export default router
