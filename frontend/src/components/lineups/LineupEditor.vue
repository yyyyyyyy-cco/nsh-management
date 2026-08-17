<template>
  <div class="lineup-editor">
    <div class="toolbar">
      <span class="stat">已排 {{ board.placedCount.value }} / 60 槽位 · 候选池 {{ board.candidates.value.length }} 人</span>
      <el-button :loading="board.saving.value" type="primary" @click="onSave">保存排表</el-button>
      <el-button :loading="board.exporting.value" @click="board.onExport()">导出 PNG</el-button>
    </div>

    <div v-loading="board.loading.value" ref="board.editorRef" class="editor">
      <div class="pool">
        <div class="panel-title">候选池（出勤正常，可拖拽）</div>
        <draggable v-model="board.candidates.value" group="lineup" item-key="key" class="pool-list" :animation="150" @change="board.onCandidateChange">
          <template #item="{ element }">
            <div class="pool-item">
              <span class="name">{{ element.member_name }}</span>
              <span class="meta">{{ element.profession }}</span>
              <el-tag v-if="element.member_status === 'filler'" size="small" type="warning" effect="light">补</el-tag>
            </div>
          </template>
        </draggable>
      </div>

      <div class="teams">
        <div v-for="team in board.teams.value" :key="team.category + team.team_index" class="team">
          <div class="team-title">{{ team.category }} {{ team.team_index + 1 }} 队</div>
          <div class="slots">
            <draggable
              v-for="(box, si) in team.slots"
              :key="si"
              :list="box"
              group="lineup"
              item-key="key"
              class="slot"
              :animation="150"
              @change="(evt: any) => board.onSlotChange(evt, team, si)"
            >
              <template #item="{ element }">
                <div class="slot-card" :class="{ filled: element.member_name }" @dblclick="board.editRemark(team, si)">
                  <span class="name">{{ element.member_name || '空' }}</span>
                  <el-tooltip v-if="element.remark" :content="element.remark" placement="top">
                    <el-icon class="remark-icon"><EditPen /></el-icon>
                  </el-tooltip>
                </div>
              </template>
            </draggable>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { EditPen } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'

import { useLineupBoard } from '@/composables/lineupBoard'

const props = defineProps<{ scheduleId: number }>()
const emit = defineEmits<{ saved: [] }>()

const board = useLineupBoard(props.scheduleId)

async function onSave() {
  await board.onSave()
  emit('saved')
}

onMounted(() => board.load())
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.stat {
  color: #6b7280;
  font-size: 13px;
  margin-right: auto;
}

.editor {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.pool {
  width: 220px;
  flex-shrink: 0;
  border: 1px solid #e5ddc4;
  border-radius: 8px;
  padding: 10px;
  background: #fffdf6;
  max-height: 460px;
  overflow: auto;
}

.panel-title {
  font-weight: 600;
  color: #7a5c00;
  margin-bottom: 8px;
  font-size: 13px;
}

.pool-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  margin-bottom: 6px;
  background: #fff;
  border: 1px solid #ece5cf;
  border-radius: 6px;
  cursor: grab;
}

.pool-item .name {
  font-weight: 500;
}

.pool-item .meta {
  color: #9ca3af;
  font-size: 12px;
}

.teams {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(5, minmax(165px, 1fr));
  gap: 12px;
  max-height: 460px;
  overflow: auto;
}

.team {
  border: 1px solid #e5ddc4;
  border-radius: 8px;
  padding: 10px;
  background: #fffdf6;
}

.team-title {
  font-weight: 600;
  color: #7a5c00;
  font-size: 13px;
  margin-bottom: 8px;
}

.slots {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.slot {
  min-height: 44px;
  border: 1px dashed #d8cfa8;
  border-radius: 6px;
  background: #fff;
}

.slot-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  font-size: 13px;
  border-radius: 5px;
  cursor: grab;
}

.slot-card.filled {
  background: #f5e8b3;
  color: #6b5200;
  font-weight: 500;
}

.remark-icon {
  color: #b8960e;
  cursor: pointer;
}
</style>
