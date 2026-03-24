<script setup lang="ts">
import { ref } from 'vue'
import type { AgentDef } from '@/composables/demo/types'
import { ROLE_COLORS } from '@/composables/demo/types'

const props = defineProps<{
  agents: AgentDef[]
}>()

const emit = defineEmits<{
  launch: [agents: AgentDef[]]
}>()

// 可编辑的 Agent 名字副本
const editableNames = ref<Record<string, string>>({})

function initNames() {
  for (const a of props.agents) {
    editableNames.value[a.id] = a.name
  }
}
initNames()

// 角色中文名
const roleLabels: Record<string, string> = {
  planner: '规划者',
  executor: '执行者',
  reviewer: '审查者',
  patrol: '巡查员',
}

function handleLaunch() {
  const updated = props.agents.map((a) => ({
    ...a,
    name: editableNames.value[a.id] || a.name,
  }))
  emit('launch', updated)
}
</script>

<template>
  <div class="team-preview">
    <div class="agent-grid">
      <div
        v-for="agent in props.agents"
        :key="agent.id"
        class="agent-card"
        :style="{ '--accent': ROLE_COLORS[agent.role] }"
      >
        <div class="agent-avatar-wrap">
          <span class="agent-avatar">{{ agent.avatar }}</span>
        </div>
        <input
          v-model="editableNames[agent.id]"
          class="agent-name-input"
          maxlength="8"
          :placeholder="agent.name"
        />
        <span class="agent-role">{{ roleLabels[agent.role] || agent.role }}</span>
      </div>
    </div>

    <button class="launch-btn" @click="handleLaunch">
      <span class="launch-icon">🚀</span>
      启动 AI 团队
    </button>
  </div>
</template>

<style scoped>
.team-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.agent-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.25rem;
}

.agent-card {
  background: #FFFFFF;
  border-radius: 10px;
  padding: 1.5rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  width: 130px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
  border: 1px solid #E8E6E0;
}

.agent-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.agent-avatar-wrap {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent) 15%, white);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: breathe 3s ease-in-out infinite;
}

.agent-avatar {
  font-size: 2rem;
}

.agent-name-input {
  width: 100%;
  text-align: center;
  border: none;
  border-bottom: 1.5px dashed #D4D0C8;
  background: transparent;
  font-family: 'Instrument Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: #1A1917;
  padding: 0.25rem 0;
  outline: none;
  transition: border-color 0.15s;
}

.agent-name-input:focus {
  border-bottom-color: var(--accent);
}

.agent-role {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.65rem;
  color: var(--accent);
  background: transparent;
  border: 1px solid var(--accent);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.launch-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 10px 28px;
  font-size: 1rem;
  font-weight: 600;
  font-family: 'Instrument Sans', sans-serif;
  color: #FAFAF8;
  background: #1A1917;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1);
}

.launch-btn:hover {
  background: #2e2b27;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2), 0 6px 20px rgba(0, 0, 0, 0.12);
}

.launch-btn:active {
  transform: translateY(0);
}

.launch-icon {
  font-size: 1.4rem;
}

@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@media (max-width: 640px) {
  .agent-grid {
    gap: 0.75rem;
  }
  .agent-card {
    width: 100px;
    padding: 1rem 0.75rem;
  }
  .agent-avatar-wrap {
    width: 48px;
    height: 48px;
  }
  .agent-avatar {
    font-size: 1.6rem;
  }
  .agent-name-input {
    font-size: 0.85rem;
  }
  .launch-btn {
    padding: 9px 22px;
    font-size: 0.9rem;
  }
}
</style>
