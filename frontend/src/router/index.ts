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
          meta: { title: '首页', adminOnly: true },
        },
        {
          path: 'member-home',
          name: 'member-home',
          component: () => import('@/views/member-home/MemberHomeView.vue'),
          meta: { title: '首页', memberOnly: true },
        },
        {
          path: 'members',
          name: 'members',
          component: () => import('@/views/members/MemberListView.vue'),
          meta: { title: '常驻库', adminOnly: true },
        },
        {
          path: 'members/:id',
          name: 'member-detail',
          component: () => import('@/views/members/MemberDetailView.vue'),
          meta: { title: '成员详情', adminOnly: true },
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
          meta: { title: '录屏上传' },
        },
        {
          path: 'config',
          name: 'config',
          component: () => import('@/views/config/ConfigView.vue'),
          meta: { title: '系统配置', adminOnly: true },
        },
        {
          path: 'logs',
          name: 'logs',
          component: () => import('@/views/logs/LogView.vue'),
          meta: { title: '系统日志', developerOnly: true },
        },
        {
          path: 'my-stats',
          name: 'my-stats',
          component: () => import('@/views/member/MyStatsView.vue'),
          meta: { title: '个人战绩' },
        },
        {
          path: 'game-id-change',
          name: 'game-id-change',
          component: () => import('@/views/member/GameIdChangeView.vue'),
          meta: { title: '修改游戏 ID', memberOnly: true },
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
    try {
      await auth.fetchMe()
    } catch {
      // Token 失效或网络异常：清除凭证并回到登录页，避免悬空在受保护页
      auth.clear()
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }
  if (to.meta.adminOnly && !auth.isAdmin) {
    // 帮众访问管理员页面：跳转帮众首页（回退到 home 会因 home 也是 adminOnly 而死循环）
    return { name: auth.user?.role === 'member' ? 'member-home' : 'config' }
  }
  if (to.meta.developerOnly && !auth.isDeveloper) {
    // 仅开发者页面：管理员/帮众按角色回退
    return { name: auth.user?.role === 'member' ? 'member-home' : 'home' }
  }
  if (to.meta.memberOnly && auth.user?.role !== 'member') {
    // 仅帮众页面（修改游戏 ID）：管理员回首页，开发者由下方规则跳系统配置
    return { name: 'home' }
  }
  if (to.name === 'login' && auth.isLoggedIn) {
    if (auth.isDeveloper) return { name: 'config' }
    if (auth.user?.role === 'member') return { name: 'member-home' }
    return { name: 'home' }
  }
  // 开发者仅允许访问 首页、系统配置、系统日志、登录页
  if (auth.isDeveloper && to.name !== 'home' && to.name !== 'config' && to.name !== 'logs' && !to.meta.public) {
    return { name: 'config' }
  }
})

router.afterEach((to) => {
  document.title = to.meta.title
    ? `${String(to.meta.title)} - 轻衫都会用的帮会联赛管理系统`
    : '轻衫都会用的帮会联赛管理系统'
})

/** 预取路由懒加载分包：菜单 hover 时预热，冷启动切换更跟手。
 *  静默失败；重复调用自动去重。 */
const prefetched = new Set<string>()
export function prefetchRoute(to: string | { name: string }): void {
  const key = typeof to === 'string' ? to : to.name
  if (!key || prefetched.has(key)) return
  prefetched.add(key)

  const resolved = router.resolve(to)
  const record = resolved.matched[resolved.matched.length - 1]
  const comp = record?.components?.default
  if (typeof comp === 'function') {
    void (comp as () => Promise<unknown>)().catch(() => prefetched.delete(key))
  }
}

export default router
