<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useSimulationStore } from '@/composables/demo/useSimulationStore'
import type { TimelineEntry } from '@/composables/demo/types'

const store = useSimulationStore()
const logRef = ref<HTMLElement | null>(null)

// 逐字打出效果：追踪正在打字的条目
const typingEntryId = ref<string | null>(null)
const typingText = ref('')
let typingTimer: ReturnType<typeof setTimeout> | null = null

function getLogIcon(entry: TimelineEntry): string {
  switch (entry.event.type) {
    case 'review':
      return entry.event.result === 'approved' ? '✅' : '❌'
    case 'reflection':
      return '💭'
    case 'score_change':
      return (entry.event.delta ?? 0) > 0 ? '⭐' : '💔'
    case 'task_created':
      return '📋'
    default:
      return entry.agentAvatar || '💬'
  }
}

function getLogMessage(entry: TimelineEntry): string {
  const e = entry.event
  switch (e.type) {
    case 'log':
      return e.content || e.message || ''
    case 'agent_status':
      return e.message || `${entry.agentName} 状态变更为 ${e.status}`
    case 'task_created': {
      const taskName = typeof e.task === 'object' ? e.task.name : e.task
      return e.message || `创建任务：${taskName}`
    }
    case 'review':
      return `${e.result === 'approved' ? '通过' : '驳回'}（${e.score}/5）${e.comment || ''}`
    case 'reflection':
      return `反思：${e.content}`
    case 'score_change':
      return `${(e.delta ?? 0) > 0 ? '+' : ''}${e.delta} ${e.reason || ''}`
    default:
      return e.message || e.content || ''
  }
}

function getLogClass(entry: TimelineEntry): string {
  const e = entry.event
  if (e.type === 'review' && e.result === 'rejected') return 'log-entry--rejected'
  if (e.type === 'review' && e.result === 'approved') return 'log-entry--approved'
  if (e.type === 'reflection') return 'log-entry--reflection'
  if (e.type === 'score_change' && (e.delta ?? 0) < 0) return 'log-entry--negative'
  if (e.type === 'score_change' && (e.delta ?? 0) > 0) return 'log-entry--positive'
  return ''
}

// 监听新日志，触发打字效果
watch(
  () => store.state.timeline.length,
  () => {
    const latest = store.state.timeline[0]
    if (!latest) return

    // 只对 log / reflection / review 做打字效果
    const typableTypes = ['log', 'reflection', 'review']
    if (typableTypes.includes(latest.event.type)) {
      startTyping(latest)
    }

    nextTick(() => {
      if (logRef.value) {
        logRef.value.scrollTop = 0
      }
    })
  }
)

function startTyping(entry: TimelineEntry) {
  if (typingTimer) clearTimeout(typingTimer)

  const fullText = getLogMessage(entry)
  typingEntryId.value = entry.id
  typingText.value = ''

  let i = 0
  function typeChar() {
    if (i < fullText.length) {
      typingText.value += fullText[i]
      i++
      typingTimer = setTimeout(typeChar, 30 + Math.random() * 20)
    } else {
      typingEntryId.value = null
    }
  }
  typeChar()
}

function getDisplayText(entry: TimelineEntry): string {
  if (typingEntryId.value === entry.id) {
    return typingText.value
  }
  return getLogMessage(entry)
}
</script>

<template>
  <div class="live-log" ref="logRef">
    <div class="log-header">
      <span class="log-title">💬 实时日志</span>
      <span class="log-count">{{ store.state.timeline.length }} 条</span>
    </div>

    <TransitionGroup name="log-entry" tag="div" class="log-list">
      <div
        v-for="entry in store.state.timeline.slice(0, 30)"
        :key="entry.id"
        class="log-entry"
        :class="getLogClass(entry)"
      >
        <span class="log-icon">{{ getLogIcon(entry) }}</span>
        <span v-if="entry.agentName" class="log-agent">{{ entry.agentName }}：</span>
        <span class="log-text">
          {{ getDisplayText(entry) }}
          <span v-if="typingEntryId === entry.id" class="typing-cursor">▌</span>
        </span>
      </div>
    </TransitionGroup>

    <div v-if="store.state.timeline.length === 0" class="log-empty">
      等待 AI 团队开始工作...
    </div>
  </div>
</template>

<style scoped>
.live-log {
  background: #FFFFFF;
  border: 1px solid #E8E6E0;
  border-radius: 10px;
  padding: 1rem;
  max-height: 280px;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #E8E6E0;
}

.log-title {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  color: #1A1917;
}

.log-count {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.65rem;
  color: #8C8A84;
  background: #F5F4F0;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  position: relative;
}

.log-entry {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  font-size: 0.78rem;
  line-height: 1.5;
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  background: #FAFAF8;
}

.log-entry--rejected {
  background: #FBF5F5;
  color: #A05252;
}

.log-entry--approved {
  background: #F5FAF7;
  color: #4A7A5E;
}

.log-entry--reflection {
  background: #FBF3DC;
  color: #7A6020;
  font-style: italic;
}

.log-entry--negative {
  color: #A05252;
}

.log-entry--positive {
  color: #4A7A5E;
}

.log-icon {
  flex-shrink: 0;
  font-size: 0.85rem;
}

.log-agent {
  font-weight: 600;
  color: #1A1917;
  flex-shrink: 0;
}

.log-text {
  color: inherit;
}

.typing-cursor {
  animation: blink 0.8s step-end infinite;
  color: #8B6F4E;
}

.log-empty {
  text-align: center;
  color: #8C8A84;
  padding: 2rem 0;
  font-size: 0.85rem;
}

/* Transitions */
.log-entry-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.log-entry-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}
.log-entry-move {
  transition: transform 0.3s ease;
}

@keyframes blink {
  50% { opacity: 0; }
}

@media (max-width: 640px) {
  .live-log {
    max-height: 220px;
    padding: 0.75rem;
  }
  .log-entry {
    font-size: 0.72rem;
    padding: 0.25rem 0.4rem;
  }
  .log-agent {
    font-size: 0.72rem;
  }
}
</style>
