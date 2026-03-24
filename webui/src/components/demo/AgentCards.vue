<script setup lang="ts">
import { useSimulationStore } from '@/composables/demo/useSimulationStore'
import { ROLE_COLORS } from '@/composables/demo/types'

const store = useSimulationStore()

const statusLabels: Record<string, string> = {
  idle: '空闲',
  thinking: '思考中',
  working: '工作中',
  reviewing: '审查中',
  reworking: '返工中',
  patrolling: '巡逻中',
  done: '完成',
}
</script>

<template>
  <div class="agents-row">
    <div
      v-for="agent in store.agentList.value"
      :key="agent.id"
      class="agent-card"
      :class="`agent-card--${agent.status}`"
      :style="{ '--accent': ROLE_COLORS[agent.role] }"
    >
      <!-- 头像 + 表情 -->
      <div class="agent-avatar-area">
        <div class="agent-avatar-circle">
          <span class="agent-avatar">{{ agent.avatar }}</span>
        </div>
        <span class="agent-expression">{{ agent.expression }}</span>
      </div>

      <!-- 名字 -->
      <div class="agent-name">{{ agent.name }}</div>

      <!-- 状态 -->
      <div class="agent-status-badge" :class="`status--${agent.status}`">
        <span v-if="agent.status === 'thinking' || agent.status === 'working' || agent.status === 'reviewing' || agent.status === 'patrolling'" class="thinking-dots">
          <span class="dot" />
          <span class="dot" />
          <span class="dot" />
        </span>
        {{ statusLabels[agent.status] || agent.status }}
      </div>

      <!-- 气泡消息 -->
      <Transition name="bubble">
        <div v-if="agent.message" class="agent-bubble">
          {{ agent.message }}
        </div>
      </Transition>

      <!-- 飘分动画会在 Step 6 加 -->
    </div>
  </div>
</template>

<style scoped>
.agents-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.agent-card {
  background: #FFFFFF;
  border-radius: 10px;
  padding: 1rem 0.75rem 0.75rem;
  width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
  position: relative;
  border: 1px solid #E8E6E0;
}

.agent-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.agent-card--working,
.agent-card--thinking,
.agent-card--reviewing,
.agent-card--patrolling {
  border-color: var(--accent);
  box-shadow: 0 2px 16px color-mix(in srgb, var(--accent) 15%, transparent);
}

.agent-card--reworking {
  border-color: #F87171;
  animation: shake 0.5s ease;
}

.agent-card--done {
  opacity: 0.7;
}

.agent-avatar-area {
  position: relative;
}

.agent-avatar-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent) 12%, white);
  display: flex;
  align-items: center;
  justify-content: center;
}

.agent-avatar {
  font-size: 1.6rem;
}

.agent-expression {
  position: absolute;
  bottom: -4px;
  right: -6px;
  font-size: 1rem;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.1));
  transition: all 0.3s ease;
}

.agent-name {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  color: #1A1917;
}

.agent-status-badge {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.6rem;
  font-weight: 500;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  letter-spacing: 0.3px;
}

.status--idle { background: #F5F4F0; color: #8C8A84; }
.status--thinking { background: #FBF3DC; color: #7A6020; }
.status--working { background: #E8F0F8; color: #4A7FA5; }
.status--reviewing { background: #FBF3DC; color: #8B6F4E; }
.status--reworking { background: #F8E8E8; color: #A05252; }
.status--patrolling { background: #E8F4ED; color: #4A7A5E; }
.status--done { background: #E8F4ED; color: #4A7A5E; }

.thinking-dots {
  display: inline-flex;
  gap: 2px;
}

.dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: currentColor;
  animation: dotBounce 1.2s ease-in-out infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

.agent-bubble {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: #FFFFFF;
  border: 1px solid #E8E6E0;
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  font-size: 0.68rem;
  color: #4A4845;
  white-space: nowrap;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  z-index: 10;
}

.agent-bubble::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: #FFFFFF;
}

/* Transitions */
.bubble-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.bubble-leave-active { transition: all 0.2s ease; }
.bubble-enter-from { opacity: 0; transform: translateX(-50%) translateY(6px) scale(0.9); }
.bubble-leave-to { opacity: 0; transform: translateX(-50%) translateY(-4px); }

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
  20%, 40%, 60%, 80% { transform: translateX(2px); }
}

@keyframes dotBounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-4px); opacity: 1; }
}

@media (max-width: 640px) {
  .agents-row {
    gap: 0.6rem;
  }
  .agent-card {
    width: 90px;
    padding: 0.75rem 0.5rem 0.6rem;
  }
  .agent-avatar-circle {
    width: 40px;
    height: 40px;
  }
  .agent-avatar {
    font-size: 1.3rem;
  }
  .agent-name {
    font-size: 0.72rem;
  }
  .agent-bubble {
    display: none;
  }
}
</style>
