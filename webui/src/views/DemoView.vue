<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ScenarioData, AgentDef } from '@/composables/demo/types'
import { useScenarioPlayer, useSimulationStore } from '@/composables/demo'
import ScenarioSelector from '@/components/demo/ScenarioSelector.vue'
import TeamPreview from '@/components/demo/TeamPreview.vue'
import KanbanBoard from '@/components/demo/KanbanBoard.vue'
import AgentCards from '@/components/demo/AgentCards.vue'
import LiveLog from '@/components/demo/LiveLog.vue'
import FloatingScore from '@/components/demo/FloatingScore.vue'
import ResultPage from '@/components/demo/ResultPage.vue'
import DemoNav from '@/components/demo/DemoNav.vue'
import DemoHero from '@/components/demo/DemoHero.vue'
import DemoBento from '@/components/demo/DemoBento.vue'
import DemoFooter from '@/components/demo/DemoFooter.vue'

type Phase = 'select' | 'preview' | 'simulation' | 'result'

const phase = ref<Phase>('select')
const selectedScenario = ref<ScenarioData | null>(null)
const player = useScenarioPlayer()
const store = useSimulationStore()

// 自动切到结果页
watch(() => store.state.phase, (p) => {
  if (p === 'result') phase.value = 'result'
})

// Phase 切换时滚回顶部
watch(phase, () => {
  nextTick(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  })
})

function onSelectScenario(scenario: ScenarioData) {
  selectedScenario.value = scenario
  phase.value = 'preview'
}

function onLaunch(agents: AgentDef[]) {
  if (!selectedScenario.value) return
  // 用用户可能修改过的名字更新场景
  const updated: ScenarioData = {
    ...selectedScenario.value,
    agents,
  }
  player.load(updated)
  phase.value = 'simulation'
  player.play()
}

function goBack() {
  if (phase.value === 'preview') {
    phase.value = 'select'
    selectedScenario.value = null
  }
}

function restart() {
  player.stop()
  store.reset()
  phase.value = 'select'
  selectedScenario.value = null
}

function togglePlay() {
  if (player.playing.value) {
    player.pause()
  } else {
    player.play()
  }
}

function cycleSpeed() {
  const speeds = [0.5, 1, 2, 3]
  const idx = speeds.indexOf(player.speed.value)
  const next = speeds[(idx + 1) % speeds.length] ?? 0.5
  player.setSpeed(next)
}

function scrollToDemo() {
  const demoMain = document.querySelector('.demo-main');
  if (demoMain) {
    demoMain.scrollIntoView({ behavior: 'smooth' });
  }
}
</script>

<template>
  <div class="demo-page">
    <DemoNav :show-cta="phase !== 'select'" @start-demo="scrollToDemo" />

    <Transition name="hero-fade">
      <div v-if="phase === 'select'" class="hero-area">
        <DemoHero @start-demo="scrollToDemo" />
        <hr class="hero-divider" />
      </div>
    </Transition>

    <main class="demo-main">
      <Transition name="fade-slide" mode="out-in">
        <!-- Phase 1: 选择场景 -->
        <div v-if="phase === 'select'" key="select" class="demo-phase">
          <h2 class="phase-title">选择你的 AI 公司类型</h2>
          <p class="phase-desc">选一个场景，看看 AI 团队怎么干活</p>
          <ScenarioSelector @select="onSelectScenario" />

          <DemoBento />
        </div>

        <!-- Phase 2: 团队预览 -->
        <div v-else-if="phase === 'preview' && selectedScenario" key="preview" class="demo-phase">
          <button class="back-btn" @click="goBack">← 重新选择</button>
          <h2 class="phase-title">{{ selectedScenario.name }}</h2>
          <p class="phase-desc">{{ selectedScenario.description }}</p>
          <p class="phase-desc phase-instruction">你可以修改 AI 员工的名字，然后点击启动 AI 团队，探索 AI 公司里的 Agent 是如何自主高效完成工作的。</p>
          <TeamPreview :agents="selectedScenario.agents" @launch="onLaunch" />
        </div>

        <!-- Phase 3: 工作流模拟 -->
        <div v-else-if="phase === 'simulation'" key="simulation" class="demo-phase">
          <div class="sim-header">
            <h2 class="phase-title">AI 团队工作中...</h2>
            <div class="sim-controls">
              <button class="ctrl-btn" @click="togglePlay">
                {{ player.playing.value ? '⏸️' : '▶️' }}
              </button>
              <button class="ctrl-btn" @click="cycleSpeed">{{ player.speed.value }}x</button>
              <button class="ctrl-btn" @click="restart">🔄</button>
            </div>
          </div>

          <!-- 进度条 -->
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${(player.progress.value * 100).toFixed(1)}%` }" />
          </div>

          <!-- Agent 卡片排 -->
          <AgentCards />

          <!-- 看板 -->
          <KanbanBoard />

          <!-- 实时日志 -->
          <LiveLog />

          <!-- 飘分动画 -->
          <FloatingScore />
        </div>

        <!-- Phase 4: 结果页 -->
        <div v-else-if="phase === 'result'" key="result" class="demo-phase">
          <ResultPage @restart="restart" />
        </div>
      </Transition>
    </main>

    <DemoFooter />
  </div>
</template>

<style scoped>
/* ── Notion-style Design Tokens ── */
.demo-page {
  --demo-bg: #FAFAF8;
  --demo-bg2: #F5F4F0;
  --demo-surface: #FFFFFF;
  --demo-border: #E8E6E0;
  --demo-border2: #D4D0C8;
  --demo-text: #1A1917;
  --demo-text2: #4A4845;
  --demo-muted: #8C8A84;
  --demo-accent: #2F2C28;
  --demo-tag-bg: #EEECEA;
  --demo-brown: #8B6F4E;
  --demo-blue: #4A7FA5;
  --demo-green: #4A7A5E;
  --demo-red: #A05252;
  --demo-yellow-bg: #FBF3DC;
  --demo-yellow-border: #E8D89A;

  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--demo-bg);
  font-family: 'Instrument Sans', 'Nunito', sans-serif;
  padding: 0;
  position: relative;
}

/* subtle grain texture */
.demo-page::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.025;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}

.demo-header {
  text-align: center;
  padding: 60px 40px 40px;
  position: relative;
  z-index: 1;
}

.demo-title {
  font-family: 'Lora', serif;
  font-size: clamp(1.8rem, 4vw, 2.6rem);
  font-weight: 700;
  color: var(--demo-text);
  letter-spacing: -0.5px;
  margin: 0 0 0.75rem;
  line-height: 1.2;
}

.demo-logo {
  font-size: 2.2rem;
  margin-right: 0.5rem;
}

.demo-subtitle {
  font-size: 1rem;
  color: var(--demo-text2);
  font-weight: 400;
  margin: 0 auto;
  max-width: 560px;
  line-height: 1.7;
}

.demo-main {
  flex: 1;
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
  padding: 0 40px 60px;
  position: relative;
  z-index: 1;
}

.demo-phase {
  min-height: 200px;
}

.phase-title {
  font-family: 'Lora', serif;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--demo-text);
  text-align: center;
  margin: 0 0 0.5rem;
  letter-spacing: -0.3px;
}

.phase-desc {
  text-align: center;
  color: var(--demo-muted);
  margin: 0 auto 0.5rem;
  max-width: 600px;
  line-height: 1.6;
  font-size: 0.95rem;
}

.phase-instruction {
  font-size: 0.85rem;
  color: var(--demo-text2);
  margin-bottom: 2rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  background: none;
  border: none;
  color: var(--demo-brown);
  font-family: 'Instrument Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.5rem 0;
  margin-bottom: 1rem;
  transition: color 0.15s;
}

.back-btn:hover {
  color: var(--demo-text);
}

.sim-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.restart-btn {
  background: none;
  border: 1px solid var(--demo-border2);
  border-radius: 6px;
  padding: 0.4rem 0.9rem;
  font-family: 'Instrument Sans', sans-serif;
  font-weight: 500;
  font-size: 0.85rem;
  color: var(--demo-text2);
  cursor: pointer;
  transition: all 0.15s;
}

.restart-btn:hover {
  border-color: var(--demo-text2);
  color: var(--demo-text);
  background: var(--demo-tag-bg);
}

.sim-controls {
  display: flex;
  gap: 0.5rem;
}

.ctrl-btn {
  background: var(--demo-surface);
  border: 1px solid var(--demo-border);
  border-radius: 6px;
  padding: 0.4rem 0.75rem;
  font-family: 'IBM Plex Mono', monospace;
  font-weight: 500;
  font-size: 0.8rem;
  color: var(--demo-text2);
  cursor: pointer;
  transition: all 0.15s;
}

.ctrl-btn:hover {
  border-color: var(--demo-text2);
  color: var(--demo-text);
  background: var(--demo-tag-bg);
}

.progress-bar {
  width: 100%;
  height: 3px;
  background: var(--demo-border);
  border-radius: 2px;
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--demo-text);
  border-radius: 2px;
  transition: width 0.2s linear;
}

.sim-placeholder {
  text-align: center;
  padding: 6rem 2rem;
  background: var(--demo-surface);
  border: 1px solid var(--demo-border);
  border-radius: 10px;
  color: var(--demo-muted);
  font-size: 1rem;
}

/* Phase transition */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Hero area transition */
.hero-area {
  overflow: hidden;
}

.hero-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.hero-fade-leave-active {
  transition: all 0.25s ease-in;
}

.hero-fade-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.hero-fade-leave-to {
  opacity: 0;
  max-height: 0;
  margin: 0;
  padding: 0;
}

.hero-divider {
  border: none;
  border-top: 1px solid #E8E6E0;
  max-width: 900px;
  margin: 0 auto 24px;
}

@media (max-width: 768px) {
  .demo-main {
    padding: 0 20px 40px;
  }
  .phase-title {
    font-size: 1.15rem;
  }
  .sim-header {
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .demo-main {
    padding: 0 16px 32px;
  }
  .phase-title {
    font-size: 1.05rem;
  }
  .phase-desc {
    font-size: 0.85rem;
  }
}
</style>
