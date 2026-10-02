<template>
  <div class="filter-bar">
    <el-input
      v-model="filters.username"
      placeholder="账号名"
      clearable
      style="width: 150px"
      @keyup.enter="$emit('search')"
    />
    <el-select v-model="filters.guild_id" placeholder="全部帮会" clearable style="width: 160px">
      <el-option
        v-for="g in guilds"
        :key="g.id"
        :label="g.name"
        :value="g.id"
      />
    </el-select>
    <el-select v-model="filters.module" placeholder="全部模块" clearable style="width: 140px">
      <el-option v-for="(label, key) in moduleLabels" :key="key" :label="label" :value="key" />
    </el-select>
    <el-select v-model="filters.level" placeholder="全部级别" clearable style="width: 120px">
      <el-option label="信息" value="info" />
      <el-option label="警告" value="warning" />
      <el-option label="错误" value="error" />
    </el-select>
    <el-date-picker
      v-model="dateRange"
      type="datetimerange"
      range-separator="至"
      start-placeholder="开始时间"
      end-placeholder="结束时间"
      style="width: 340px"
    />
    <el-button type="primary" @click="$emit('search')">查询</el-button>
    <el-button @click="$emit('reset')">重置</el-button>
  </div>
</template>

<script setup lang="ts">
import type { Guild } from '@/types/config'

import { moduleLabels } from './logLabels'

defineProps<{
  guilds: Guild[]
  filters: {
    username: string
    guild_id: number | null
    module: string | null
    level: string | null
  }
}>()

defineEmits<{ search: []; reset: [] }>()

const dateRange = defineModel<[Date, Date] | null>('dateRange', { required: true })
</script>

<style scoped>
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
</style>
