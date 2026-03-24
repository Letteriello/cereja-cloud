<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useSimulationStore } from '@/composables/demo/useSimulationStore'
import { ROLE_COLORS } from '@/composables/demo/types'

const emit = defineEmits<{
  restart: []
}>()

const store = useSimulationStore()
const summary = computed(() => store.state.summary)
const agents = computed(() => store.agentList.value)

// 数字滚动动画
function useCountUp(target: number, duration = 1500) {
  const current = ref(0)
  let startTime: number | null = null
  let raf: number | null = null

  function animate(timestamp: number) {
    if (!startTime) startTime = timestamp
    const progress = Math.min((timestamp - startTime) / duration, 1)
    // easeOutQuart
    const ease = 1 - Math.pow(1 - progress, 4)
    current.value = Math.round(target * ease)
    if (progress < 1) {
      raf = requestAnimationFrame(animate)
    }
  }

  onMounted(() => { raf = requestAnimationFrame(animate) })
  onUnmounted(() => { if (raf) cancelAnimationFrame(raf) })

  return current
}

const tasksCount = computed(() => summary.value?.tasks_completed ?? 0)
const avgScore = computed(() => summary.value?.average_score ?? 0)
const reworkCount = computed(() => summary.value?.rework_count ?? 0)
const tokensUsed = computed(() => summary.value?.tokens_used ?? 0)
const tokenCost = computed(() => {
  // 1元/百万Token
  const cost = tokensUsed.value / 1000000
  return cost < 0.01 ? '< ¥0.01' : `¥${cost.toFixed(2)}`
})

const animTasks = useCountUp(tasksCount.value)
const animTokens = useCountUp(tokensUsed.value, 2000)

// 为每个 Agent 生成成长评语
function getAgentComment(agent: { score: number; role: string; name: string }): string {
  if (agent.score >= 105) return '表现优秀！持续高质量输出 🌟'
  if (agent.score >= 100) return '稳定发挥，按时完成任务 ✓'
  if (agent.score >= 95) return '经历返工后有所成长 📈'
  return '需要更多训练和指导 💪'
}
</script>

<template>
  <div class="result-page" v-if="summary">
    <h2 class="result-title">🎉 AI 公司任务完成！</h2>
    <p class="result-subtitle">以下是本次工作的总结报告</p>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card stat-card--purple">
        <div class="stat-value">{{ animTasks }}</div>
        <div class="stat-label">完成任务</div>
      </div>
      <div class="stat-card stat-card--yellow">
        <div class="stat-value">{{ avgScore.toFixed(1) }}</div>
        <div class="stat-label">平均评分</div>
      </div>
      <div class="stat-card stat-card--red">
        <div class="stat-value">{{ reworkCount }}</div>
        <div class="stat-label">返工次数</div>
      </div>
      <div class="stat-card stat-card--blue">
        <div class="stat-value">{{ animTokens.toLocaleString() }}</div>
        <div class="stat-label">Token 消耗</div>
        <div class="stat-cost">≈ {{ tokenCost }}</div>
      </div>
    </div>

    <!-- 节省人力 -->
    <div class="time-saved">
      <span class="time-saved-icon">⏱️</span>
      <span class="time-saved-text">估算节省：<strong>{{ summary.time_saved }}</strong></span>
    </div>

    <!-- Agent 成绩单 -->
    <h3 class="section-title">👥 团队成绩单</h3>
    <div class="agent-results">
      <div
        v-for="agent in agents"
        :key="agent.id"
        class="agent-result-card"
        :style="{ '--accent': ROLE_COLORS[agent.role] }"
      >
        <div class="ar-avatar">{{ agent.avatar }}</div>
        <div class="ar-info">
          <div class="ar-name">{{ agent.name }}</div>
          <div class="ar-score">
            <span class="ar-score-num">{{ agent.score }}</span>
            <span class="ar-score-label">分</span>
          </div>
          <div class="ar-comment">{{ getAgentComment(agent) }}</div>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div class="cta-section">
      <a
        href="https://github.com/uluckyXH/OpenMOSS"
        target="_blank"
        class="cta-btn cta-btn--primary"
      >
        🚀 部署你自己的 AI 公司
      </a>
      <button class="cta-btn cta-btn--secondary" @click="emit('restart')">
        🔄 再试一个场景
      </button>
    </div>
  </div>
</template>

<style scoped>
.result-page {
  animation: fadeIn 0.5s ease;
}

.result-title {
  text-align: center;
  font-family: 'Lora', serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: #1A1917;
  margin: 0 0 0.5rem;
  letter-spacing: -0.5px;
}

.result-subtitle {
  text-align: center;
  color: #8C8A84;
  margin: 0 0 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  background: #FFFFFF;
  border: 1px solid #E8E6E0;
  border-radius: 10px;
  padding: 1.25rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.stat-card:nth-child(2) { animation-delay: 0.1s; }
.stat-card:nth-child(3) { animation-delay: 0.2s; }
.stat-card:nth-child(4) { animation-delay: 0.3s; }

.stat-card--purple { border-top: 3px solid #8B6F4E; }
.stat-card--yellow { border-top: 3px solid #C09840; }
.stat-card--red { border-top: 3px solid #A05252; }
.stat-card--blue { border-top: 3px solid #4A7FA5; }

.stat-value {
  font-family: 'Lora', serif;
  font-size: 2rem;
  font-weight: 700;
  color: #1A1917;
}

.stat-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  color: #8C8A84;
  font-weight: 500;
  margin-top: 0.25rem;
  letter-spacing: 0.3px;
}

.stat-cost {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.7rem;
  color: #4A7A5E;
  font-weight: 500;
  margin-top: 0.15rem;
}

.time-saved {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #FBF3DC;
  border: 1px solid #E8D89A;
  border-radius: 6px;
  margin-bottom: 2rem;
}

.time-saved-icon { font-size: 1.2rem; }
.time-saved-text {
  font-size: 0.9rem;
  color: #4A4845;
}

.section-title {
  font-family: 'Lora', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #1A1917;
  margin: 0 0 1rem;
  letter-spacing: -0.2px;
}

.agent-results {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
}

.agent-result-card {
  background: #FFFFFF;
  border: 1px solid #E8E6E0;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1 1 200px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border-left: 3px solid var(--accent);
  animation: slideIn 0.4s ease both;
}
.agent-result-card:nth-child(2) { animation-delay: 0.1s; }
.agent-result-card:nth-child(3) { animation-delay: 0.2s; }
.agent-result-card:nth-child(4) { animation-delay: 0.3s; }
.agent-result-card:nth-child(5) { animation-delay: 0.4s; }

.ar-avatar {
  font-size: 2rem;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent) 12%, white);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ar-info {
  min-width: 0;
}

.ar-name {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 0.88rem;
  font-weight: 600;
  color: #1A1917;
}

.ar-score {
  display: flex;
  align-items: baseline;
  gap: 0.2rem;
  margin: 0.15rem 0;
}

.ar-score-num {
  font-family: 'Lora', serif;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--accent);
}

.ar-score-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.65rem;
  color: #8C8A84;
}

.ar-comment {
  font-size: 0.75rem;
  color: #4A4845;
}

.cta-section {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 10px 22px;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: 'Instrument Sans', sans-serif;
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.15s;
  text-decoration: none;
}

.cta-btn--primary {
  background: #1A1917;
  color: #FAFAF8;
  border: none;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1);
}
.cta-btn--primary:hover {
  background: #2e2b27;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2), 0 6px 20px rgba(0, 0, 0, 0.12);
}

.cta-btn--secondary {
  background: #FFFFFF;
  color: #4A4845;
  border: 1px solid #D4D0C8;
}
.cta-btn--secondary:hover {
  border-color: #4A4845;
  color: #1A1917;
  background: #F5F4F0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.8) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }
  .stat-card {
    padding: 1rem;
  }
  .stat-value {
    font-size: 1.5rem;
  }
  .agent-result-card {
    flex: 1 1 100%;
  }
  .result-actions {
    flex-direction: column;
    gap: 0.75rem;
  }
  .result-actions .btn {
    width: 100%;
    justify-content: center;
  }
  .time-saved {
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
  }
}
</style>
