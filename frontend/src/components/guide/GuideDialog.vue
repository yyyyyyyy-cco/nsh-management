<template>
  <el-dialog
    v-model="visible"
    title="使用指南"
    width="min(860px, 94vw)"
    top="4vh"
    :fullscreen="isMobile"
    destroy-on-close
  >
    <div class="guide">
      <!-- 当前角色以文字呈现（不靠颜色区分），读屏可读 -->
      <p class="guide__role">当前角色：{{ roleLabel }}</p>

      <el-tabs v-model="tab">
        <el-tab-pane v-for="section in visibleSections" :key="section.key" :label="section.label" :name="section.key">
          <p v-if="section.intro" class="guide__intro">{{ section.intro }}</p>

          <!-- 步骤清单（快速上手） -->
          <template v-if="section.kind === 'steps'">
            <div v-for="(item, i) in section.items" :key="i" class="guide-block">
              <h4 class="guide-block__title">{{ item.title }}</h4>
              <ol class="guide-steps">
                <li v-for="(step, j) in item.steps" :key="j">{{ step }}</li>
              </ol>
            </div>
          </template>

          <!-- 页面详解（分组折叠；「打开该页面」仅独立路由页面显示，Tab 型页面看「入口」说明） -->
          <template v-else-if="section.kind === 'pages'">
            <div v-for="group in visiblePageGroups" :key="group.key" class="guide-page-group">
              <h4 class="guide-block__title">{{ group.label }}</h4>
              <el-collapse>
                <el-collapse-item v-for="page in group.pages" :key="page.key" :name="page.key">
                  <template #title>
                    <span class="page-guide__name">{{ page.name }}</span>
                    <span class="page-guide__entry">{{ page.entry }}</span>
                  </template>
                  <p class="page-guide__intro">{{ page.intro }}</p>
                  <ol class="guide-steps">
                    <li v-for="(step, j) in page.steps" :key="j">{{ step }}</li>
                  </ol>
                  <ul class="page-guide__points">
                    <li v-for="(point, k) in page.points" :key="k">{{ point }}</li>
                  </ul>
                  <p v-for="(tip, m) in page.tips || []" :key="m" class="page-guide__tip">小贴士：{{ tip }}</p>
                  <el-button
                    v-if="page.path"
                    class="page-guide__open"
                    size="small"
                    type="primary"
                    plain
                    @click="openPage(page.path)"
                  >
                    打开该页面
                  </el-button>
                </el-collapse-item>
              </el-collapse>
            </div>
          </template>

          <!-- FAQ 折叠（el-collapse 标题为可聚焦按钮，Enter/Space 展开） -->
          <template v-else-if="section.kind === 'faq'">
            <el-collapse>
              <el-collapse-item v-for="(item, i) in section.items" :key="i" :title="item.title">
                <p class="guide-block__body">{{ item.body }}</p>
              </el-collapse-item>
            </el-collapse>
          </template>

          <!-- 角色差异表（当前角色列加粗高亮） -->
          <template v-else-if="section.kind === 'roles'">
            <el-table :data="ROLE_MATRIX" size="small" border>
              <el-table-column prop="area" label="功能范围" min-width="180" />
              <el-table-column label="开发者" min-width="120">
                <template #default="{ row }">
                  <span :class="{ 'is-self': role === 'developer' }">{{ row.developer }}</span>
                </template>
              </el-table-column>
              <el-table-column label="管理员" min-width="150">
                <template #default="{ row }">
                  <span :class="{ 'is-self': role === 'admin' }">{{ row.admin }}</span>
                </template>
              </el-table-column>
              <el-table-column label="帮众" min-width="150">
                <template #default="{ row }">
                  <span :class="{ 'is-self': role === 'member' }">{{ row.member }}</span>
                </template>
              </el-table-column>
            </el-table>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { GUIDE_SECTIONS, ROLE_LABELS, ROLE_MATRIX, type Role } from './guideContent'
import { GUIDE_PAGE_GROUPS } from './pageGuides'

const auth = useAuthStore()
const router = useRouter()
const visible = ref(false)
const tab = ref('quick-start')

/** 移动端全屏（≤768px，与 MainLayout / EChart 共用同一断点口径） */
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
function onMqChange(e: MediaQueryListEvent) {
  isMobile.value = e.matches
}
onMounted(() => mq.addEventListener('change', onMqChange))
onBeforeUnmount(() => mq.removeEventListener('change', onMqChange))

const role = computed<Role | undefined>(() => auth.user?.role)
const roleLabel = computed(() => (role.value ? ROLE_LABELS[role.value] : '未登录'))

/** 章节条目按角色过滤：不适用的直接不渲染（读屏不会读到无关内容） */
const visibleSections = computed(() =>
  GUIDE_SECTIONS.map((section) => ({
    ...section,
    items: section.items.filter((item) => !item.roles || (role.value !== undefined && item.roles.includes(role.value))),
  })),
)

/** 页面详解：按角色过滤页面，再过滤空分组 */
const visiblePageGroups = computed(() =>
  GUIDE_PAGE_GROUPS.map((group) => ({
    ...group,
    pages: group.pages.filter((page) => role.value !== undefined && page.roles.includes(role.value)),
  })).filter((group) => group.pages.length > 0),
)

/** 供入口组件调用（与「指标说明」弹窗同款 defineExpose 模式） */
function open() {
  visible.value = true
  tab.value = 'quick-start'
}
defineExpose({ open })

/** 「打开该页面」：关闭弹窗并跳转（条目已按角色过滤，路由守卫兜底） */
function openPage(path?: string) {
  if (!path) return
  visible.value = false
  router.push(path)
}
</script>

<style scoped>
.guide {
  max-height: 74vh;
  overflow-y: auto;
  padding-right: 4px;
}

.guide__role {
  font-size: 12px;
  color: var(--ink-500);
  margin-bottom: 10px;
}

.guide__intro {
  font-size: 13px;
  color: var(--ink-600);
  margin-bottom: 12px;
  line-height: 1.6;
}

/* 条目标题：与「指标说明」弹窗同款金色左边条分组风格 */
.guide-block__title {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink-800);
  margin: 16px 0 8px;
  padding-left: 8px;
  border-left: 3px solid var(--gold-500);
}

.guide-block__title:first-child {
  margin-top: 4px;
}

.guide-block__body {
  font-size: 13px;
  color: var(--ink-600);
  line-height: 1.7;
  margin: 0;
}

.guide-steps,
.page-guide__points {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: var(--ink-600);
  line-height: 1.9;
}

/* ===== 页面详解 ===== */
.guide-page-group + .guide-page-group {
  margin-top: 6px;
}

.page-guide__name {
  font-weight: 600;
  color: var(--ink-800);
  margin-right: 8px;
}

.page-guide__entry {
  font-size: 12px;
  color: var(--ink-400);
}

.page-guide__intro {
  font-size: 13px;
  color: var(--ink-600);
  line-height: 1.7;
  margin: 0 0 8px;
}

.page-guide__points {
  margin-top: 8px;
}

.page-guide__tip {
  font-size: 12px;
  color: var(--ink-500);
  line-height: 1.7;
  margin: 8px 0 0;
  padding: 6px 10px;
  border-left: 2px solid var(--gold-300);
  background: var(--gold-50);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.page-guide__open {
  margin-top: 10px;
}

/* 当前角色列文字加粗（非仅颜色提示） */
.is-self {
  font-weight: 700;
  color: var(--ink-900);
}

/* 移动端全屏时交由弹窗主体滚动，避免嵌套滚动条 */
@media (max-width: 768px) {
  .guide {
    max-height: none;
    overflow-y: visible;
    padding-right: 0;
  }
}
</style>
