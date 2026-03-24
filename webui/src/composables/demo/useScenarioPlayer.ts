import { ref, computed } from 'vue'
import type { ScenarioData, ScenarioEvent, AgentDef } from './types'
import { useSimulationStore } from './useSimulationStore'

// 原始 JSON——用于获取未改名的 Agent 名字
import contentCompany from './scenarios/content-company.json'
import ecommerce from './scenarios/ecommerce.json'
import devTeam from './scenarios/dev-team.json'
import researchLab from './scenarios/research-lab.json'
import chaos from './scenarios/chaos.json'

const origMap: Record<string, AgentDef[]> = {
  'content-company': (contentCompany as any).agents,
  'ecommerce': (ecommerce as any).agents,
  'dev-team': (devTeam as any).agents,
  'research-lab': (researchLab as any).agents,
  'chaos': (chaos as any).agents,
}

function getOriginalAgents(scenarioId: string): AgentDef[] | undefined {
  return origMap[scenarioId]
}

// =============================================
// ScenarioPlayer — JSON 剧本回放引擎
// 加载一个 ScenarioData，按时间轴逐条 emit 事件
// =============================================

export function useScenarioPlayer() {
  const store = useSimulationStore()

  const scenario = ref<ScenarioData | null>(null)
  const playing = ref(false)
  const speed = ref(0.5)       // 0.5x / 1x / 2x / 3x
  const elapsed = ref(0)       // 已播放秒数

  let eventIndex = 0
  let timer: ReturnType<typeof setInterval> | null = null
  let nameMap = new Map<string, string>()

  const progress = computed(() => {
    if (!scenario.value) return 0
    return Math.min(elapsed.value / scenario.value.duration, 1)
  })

  const isFinished = computed(() => {
    if (!scenario.value) return false
    return eventIndex >= scenario.value.events.length
  })

  /** 加载场景 */
  function load(data: ScenarioData) {
    stop()
    store.reset()

    scenario.value = data
    store.state.duration = data.duration
    store.initAgents(data.agents)

    // 构建「原始名 → 用户改名」映射
    nameMap = new Map()
    const originalAgents = getOriginalAgents(data.id)
    if (originalAgents) {
      for (const orig of originalAgents) {
        const renamed = data.agents.find(a => a.id === orig.id)
        if (renamed && renamed.name !== orig.name) {
          nameMap.set(orig.name, renamed.name)
        }
      }
    }

    eventIndex = 0
    elapsed.value = 0
  }

  /** 替换事件文本中的原始名字 */
  function substituteNames(text: string): string {
    let result = text
    for (const [orig, renamed] of nameMap) {
      result = result.split(orig).join(renamed)
    }
    return result
  }

  /** 对事件中所有文本字段做名字替换 */
  function patchEvent(evt: ScenarioEvent): ScenarioEvent {
    if (nameMap.size === 0) return evt
    const patched = { ...evt }
    if (patched.message) patched.message = substituteNames(patched.message)
    if (patched.content) patched.content = substituteNames(patched.content)
    if (patched.comment) patched.comment = substituteNames(patched.comment)
    return patched
  }

  /** 开始播放 */
  function play() {
    if (!scenario.value) return
    if (isFinished.value) return

    playing.value = true
    store.state.phase = 'playing'

    // 100ms tick
    timer = setInterval(() => {
      elapsed.value += 0.1 * speed.value
      store.state.elapsed = elapsed.value

      // 消费所有 t <= elapsed 的事件
      const events = scenario.value!.events
      while (eventIndex < events.length) {
        const evt = events[eventIndex]
        if (!evt || evt.t > elapsed.value) break
        store.pushEvent(patchEvent(evt))
        eventIndex++
      }

      // 播放完毕
      if (eventIndex >= events.length) {
        pause()
        // 如果最后一个事件不是 summary，自动触发 result phase
        if (store.state.phase !== 'result') {
          store.state.phase = 'result'
        }
      }
    }, 100)
  }

  /** 暂停 */
  function pause() {
    playing.value = false
    store.state.phase = 'paused'
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  /** 停止并重置 */
  function stop() {
    pause()
    elapsed.value = 0
    eventIndex = 0
    scenario.value = null
  }

  /** 设置播放速度 */
  function setSpeed(s: number) {
    speed.value = s
  }

  /** 重新开始当前场景 */
  function restart() {
    if (!scenario.value) return
    const data = scenario.value
    load(data)
    play()
  }

  return {
    scenario,
    playing,
    speed,
    elapsed,
    progress,
    isFinished,
    load,
    play,
    pause,
    stop,
    setSpeed,
    restart,
  }
}
