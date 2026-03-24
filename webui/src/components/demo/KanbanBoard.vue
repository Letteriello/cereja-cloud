<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useSimulationStore } from '@/composables/demo/useSimulationStore'
import { ROLE_COLORS } from '@/composables/demo/types'

const store = useSimulationStore()
const kanbanRef = ref<HTMLElement | null>(null)

const columns = [
  { key: 'pending', label: '📋 待分配', color: '#94a3b8' },
  { key: 'working', label: '⚡ 执行中', color: '#38BDF8' },
  { key: 'review', label: '🔍 审查中', color: '#FBBF24' },
  { key: 'done', label: '✅ 已完成', color: '#4ADE80' },
]

// 合并 assigned→pending, rework→working 以简化显示
const columnTasks = computed(() => {
  const tasks = store.tasksByStatus.value
  return {
    pending: [...(tasks.pending || []), ...(tasks.assigned || [])],
    working: [...(tasks.working || []), ...(tasks.rework || [])],
    review: tasks.review || [],
    done: tasks.done || [],
  }
})

function getAgentName(agentId: string) {
  return store.state.agents.get(agentId)?.name || agentId
}

function getAgentColor(agentId: string) {
  const agent = store.state.agents.get(agentId)
  return agent ? ROLE_COLORS[agent.role] : '#94a3b8'
}

function isReworking(taskId: string) {
  const tasks = store.tasksByStatus.value
  return (tasks.rework || []).some(t => t.id === taskId)
}

// ─── 返工弧线箭头动画 ───────────────────────
const showArrow = ref(false)
const arrowPath = ref('')
const arrowViewBox = ref('0 0 100 100')
const arrowStyle = ref<Record<string, string>>({})

function animateReworkArrow() {
  if (!kanbanRef.value) return

  const reviewCol = kanbanRef.value.querySelectorAll('.kanban-col')[2]
  const workingCol = kanbanRef.value.querySelectorAll('.kanban-col')[1]
  if (!reviewCol || !workingCol) return

  const kanbanRect = kanbanRef.value.getBoundingClientRect()
  const reviewRect = reviewCol.getBoundingClientRect()
  const workingRect = workingCol.getBoundingClientRect()

  // 弧线起点：审查列中间偏上
  const startX = reviewRect.left + reviewRect.width / 2 - kanbanRect.left
  const startY = reviewRect.top + 50 - kanbanRect.top
  // 弧线终点：执行列中间偏上（同一高度）
  const endX = workingRect.left + workingRect.width / 2 - kanbanRect.left

  const width = Math.abs(startX - endX) + 40
  const height = 80

  const svgStartX = 20
  const svgEndX = width - 20
  const svgStartY = height - 10
  const svgEndY = height - 10
  const cpX = width / 2
  const cpY = 10

  arrowViewBox.value = `0 0 ${width} ${height}`
  arrowPath.value = `M ${svgStartX} ${svgStartY} Q ${cpX} ${cpY} ${svgEndX} ${svgEndY}`

  arrowStyle.value = {
    position: 'absolute',
    left: `${Math.min(endX, startX) - 20}px`,
    top: `${startY - height + 10}px`,
    width: `${width}px`,
    height: `${height}px`,
    pointerEvents: 'none',
    zIndex: '20',
  }

  showArrow.value = true
  setTimeout(() => { showArrow.value = false }, 1500)
}

// 监听 rework 事件
watch(
  () => store.state.timeline.length,
  () => {
    const latest = store.state.timeline[0]
    if (!latest) return
    if (
      (latest.event.type === 'review' && latest.event.result === 'rejected') ||
      (latest.event.type === 'agent_status' && latest.event.status === 'reworking')
    ) {
      nextTick(() => animateReworkArrow())
    }
  }
)

// 处理 resize
function handleResize() { showArrow.value = false }
onMounted(() => window.addEventListener('resize', handleResize))
onUnmounted(() => window.removeEventListener('resize', handleResize))
</script>

<template>
  <div class="kanban" ref="kanbanRef">
    <!-- 返工弧线箭头 -->
    <Transition name="arrow-fade">
      <svg
        v-if="showArrow"
        :viewBox="arrowViewBox"
        :style="arrowStyle"
        fill="none"
      >
        <path
          :d="arrowPath"
          stroke="#F87171"
          stroke-width="2.5"
          stroke-dasharray="6 4"
          fill="none"
          class="rework-arrow-path"
        />
        <!-- 箭头头 -->
        <circle
          :cx="arrowPath.split(' ').slice(-2, -1)[0]"
          :cy="arrowPath.split(' ').slice(-1)[0]"
          r="4"
          fill="#F87171"
        />
        <!-- 标签 -->
        <text
          :x="Number(arrowViewBox.split(' ')[2]) / 2"
          :y="20"
          text-anchor="middle"
          fill="#F87171"
          font-size="11"
          font-weight="700"
          font-family="Nunito, sans-serif"
        >🔄 返工</text>
      </svg>
    </Transition>

    <div
      v-for="col in columns"
      :key="col.key"
      class="kanban-col"
    >
      <div class="kanban-col-header" :style="{ borderColor: col.color }">
        <span class="col-label">{{ col.label }}</span>
        <span class="col-count">{{ columnTasks[col.key as keyof typeof columnTasks]?.length || 0 }}</span>
      </div>

      <TransitionGroup name="task-card" tag="div" class="kanban-col-body">
        <div
          v-for="task in columnTasks[col.key as keyof typeof columnTasks]"
          :key="task.id"
          class="task-card"
          :class="{
            'task-card--rework': isReworking(task.id),
            'task-card--done': task.status === 'done',
          }"
          :style="{ '--agent-color': getAgentColor(task.assignee) }"
        >
          <div class="task-name">{{ task.name }}</div>
          <div class="task-meta">
            <span class="task-assignee" :style="{ color: getAgentColor(task.assignee) }">
              → {{ getAgentName(task.assignee) }}
            </span>
            <span v-if="task.score" class="task-score">
              {{ task.score }}/5
            </span>
          </div>
          <div v-if="task.comment" class="task-comment">
            {{ task.comment }}
          </div>
          <div v-if="isReworking(task.id)" class="rework-badge">
            🔄 返工中
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<style scoped>
.kanban {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
  position: relative;
}

@media (max-width: 768px) {
  .kanban {
    grid-template-columns: repeat(2, 1fr);
  }
}

.kanban-col {
  min-height: 120px;
}

.kanban-col-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-bottom: 3px solid;
  margin-bottom: 0.75rem;
}

.col-label {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: #4A4845;
}

.col-count {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.7rem;
  font-weight: 500;
  color: #8C8A84;
  background: #F5F4F0;
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
}

.kanban-col-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  position: relative;
}

.task-card {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 0.75rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid #E8E6E0;
  border-left: 3px solid var(--agent-color);
  transition: all 0.2s ease;
}

.task-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.task-card--rework {
  animation: shake 0.5s ease-in-out;
  border-left-color: #A05252;
  background: #FBF5F5;
}

.task-card--done {
  opacity: 0.8;
  background: #F5FAF7;
}

.task-name {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  color: #1A1917;
  margin-bottom: 0.35rem;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-assignee {
  font-size: 0.72rem;
  font-weight: 500;
  color: #4A4845;
}

.task-score {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  font-weight: 500;
  color: #8B6F4E;
}

.task-comment {
  font-size: 0.68rem;
  color: #8C8A84;
  margin-top: 0.35rem;
  padding-top: 0.35rem;
  border-top: 1px dashed #E8E6E0;
  line-height: 1.4;
}

.rework-badge {
  display: inline-block;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.65rem;
  color: #A05252;
  font-weight: 500;
  margin-top: 0.35rem;
}

/* Card transitions */
.task-card-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.task-card-leave-active {
  transition: all 0.3s ease;
}
.task-card-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}
.task-card-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
.task-card-move {
  transition: transform 0.4s ease;
}

/* 返工弧线箭头 */
.rework-arrow-path {
  animation: dashFlow 0.8s linear infinite;
}

@keyframes dashFlow {
  to { stroke-dashoffset: -20; }
}

/* Arrow fade */
.arrow-fade-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.arrow-fade-leave-active {
  transition: all 0.5s ease;
}
.arrow-fade-enter-from {
  opacity: 0;
  transform: scale(0.8);
}
.arrow-fade-leave-to {
  opacity: 0;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-3px); }
  20%, 40%, 60%, 80% { transform: translateX(3px); }
}
</style>
