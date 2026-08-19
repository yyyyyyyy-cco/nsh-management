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
        {
          path: 'schedules',
          name: 'schedules',
          component: () => import('@/views/schedules/ScheduleListView.vue'),
          meta: { title: '联赛日程' },
        },
        {
          path: 'schedules/:id',
          name: 'schedule-detail',
          component: () => import('@/views/schedules/ScheduleDetailView.vue'),
          meta: { title: '赛程详情' },
        },
        {
          path: 'league-overview',
          name: 'league-overview',
          component: () => import('@/views/schedules/LeagueOverviewView.vue'),
          meta: { title: '联赛总览' },
        },
        {
          path: 'config',
          name: 'config',
          component: () => import('@/views/config/ConfigView.vue'),
          meta: { title: '系统配置', adminOnly: true },
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
    if (auth.isDeveloper) return { name: 'config' }
    if (auth.user?.role === 'member') return { name: 'league-overview' }
    return { name: 'home' }
  }
  // 开发者仅允许访问 首页、系统配置、登录页
  if (auth.isDeveloper && to.name !== 'home' && to.name !== 'config' && !to.meta.public) {
    return { name: 'config' }
  }
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${String(to.meta.title)} - 轻衫都会用的帮会联赛管理系统` : '轻衫都会用的帮会联赛管理系统'
})

export default router
