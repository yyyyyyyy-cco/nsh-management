<!-- 成员详情页信息卡：ID + 职业色标签（主/副）+ 状态 + 出勤率 + 备注 -->
<template>
  <div class="detail-header">
    <div class="dh-main">
      <span class="dh-name">{{ member.name }}</span>
      <span class="dh-profs">
        <span class="prof-tag" :style="profTagStyle(member.main_profession)">{{ member.main_profession }}</span>
        <span v-if="member.sub_profession" class="prof-tag prof-tag--sub" :style="profTagStyle(member.sub_profession)">
          {{ member.sub_profession }}
        </span>
      </span>
      <el-tag class="dh-status" :type="member.status === 'formal' ? 'primary' : 'info'" effect="light" size="small">
        {{ member.status === 'formal' ? '正式' : '替补' }}
      </el-tag>
      <span class="dh-rate">
        <span class="dh-rate-label">出勤率</span>
        <span v-if="attendanceRate !== null" class="dh-rate-value num" :class="{ warn: attendanceRate < 0.5 }">
          {{ (attendanceRate * 100).toFixed(1) }}%
        </span>
        <span v-else class="dh-rate-none">无记录</span>
      </span>
    </div>
    <div v-if="member.remark" class="dh-remark">备注：{{ member.remark }}</div>
  </div>
</template>

<script setup lang="ts">
import type { MemberInfo } from '@/types/member'
import { profTagStyle } from '@/utils/profession'

defineProps<{
  member: MemberInfo
  /** 出勤率（0~1），无出勤记录时为 null */
  attendanceRate: number | null
}>()
</script>

<style scoped>
.detail-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dh-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.dh-name {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: var(--ink-900);
}

.dh-profs {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* 职业色标签（与常驻库列表同款） */
.prof-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-xl);
  font-size: 12px;
  font-weight: 600;
  line-height: 1.7;
}

.prof-tag--sub {
  opacity: 0.75;
}

.dh-status {
  flex-shrink: 0;
}

.dh-rate {
  margin-left: auto;
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
}

.dh-rate-label {
  font-size: 12px;
  letter-spacing: 1px;
  color: var(--ink-500);
}

.dh-rate-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--gold-700);
}

.dh-rate-value.warn {
  color: var(--cinnabar);
}

.dh-rate-none {
  font-size: 13px;
  color: var(--ink-400);
}

.dh-remark {
  font-size: 12.5px;
  color: var(--ink-500);
  overflow-wrap: anywhere;
}

/* finesse · register=product · shell=member-detail: 信息卡（ID + 职业标签 + 状态 + 出勤率）；≤768px flex-wrap 自动换行 */
</style>
