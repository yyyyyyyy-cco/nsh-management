<!-- 帮众：修改游戏 ID（选择本帮会常驻成员 → 提交改名申请 → 查看申请记录） -->
<template>
  <div class="game-id-change">
    <el-card shadow="never" class="notice">
      <el-icon class="notice__icon"><InfoFilled /></el-icon>
      <div class="notice__body">
        <p class="notice__title">共享账号说明</p>
        <p class="notice__text">
          帮众账号为共享账号，系统无法自动识别操作人，也无法把历史战绩直接认定为你本人。
          请选择你自己的常驻成员提交申请，管理员会线下核实身份后审核。
        </p>
      </div>
    </el-card>

    <GameIdRequestForm
      class="section"
      :selected="selectedMember"
      :pending="pendingRecord"
      @select="onSelectMember"
      @submitted="onSubmitted"
    />

    <GameIdRequestHistory
      class="section"
      :member-id="selectedMember?.id ?? null"
      :member-name="selectedMember?.name ?? null"
      :refresh-key="refreshKey"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'

import { listMemberGameIdRequests } from '@/api/gameIdRequests'
import type { GameIdOption, GameIdRequestItem } from '@/types/gameIdRequest'
import GameIdRequestForm from '@/components/members/GameIdRequestForm.vue'
import GameIdRequestHistory from '@/components/members/GameIdRequestHistory.vue'

const selectedMember = ref<GameIdOption | null>(null)
const pendingRecord = ref<GameIdRequestItem | null>(null)
const refreshKey = ref(0)

/** 切换成员：拉取其待审申请（用于禁用重复提交），并静默失败不打断选择。 */
async function onSelectMember(member: GameIdOption | null) {
  selectedMember.value = member
  pendingRecord.value = null
  if (!member) return
  try {
    const data = await listMemberGameIdRequests(member.id, { page: 1, page_size: 20 })
    // 选择器可能已被再次切换：仅在仍是同一成员时写入
    if (selectedMember.value?.id !== member.id) return
    pendingRecord.value = data.items.find((item) => item.status === 'pending') || null
  } catch {
    // 错误提示由 http 拦截器统一处理；待审状态未知时仍允许提交（后端会兜底拒绝重复申请）
  }
}

/** 提交成功：刷新记录列表并重新拉取待审状态。 */
async function onSubmitted() {
  refreshKey.value += 1
  if (selectedMember.value) {
    await onSelectMember(selectedMember.value)
  }
}
</script>

<style scoped>
.notice {
  margin-bottom: 16px;
}

.notice :deep(.el-card__body) {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px 16px;
}

.notice__icon {
  flex-shrink: 0;
  margin-top: 2px;
  font-size: 18px;
  color: var(--gold-600);
}

.notice__title {
  margin: 0 0 4px;
  font-size: 13.5px;
  font-weight: 700;
  color: var(--ink-900);
}

.notice__text {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.75;
  color: var(--ink-500);
}

.section {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .notice :deep(.el-card__body) {
    padding: 12px 14px;
  }
}
</style>
