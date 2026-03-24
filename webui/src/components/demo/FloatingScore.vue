<script setup lang="ts">
import { ref, watch } from 'vue'
import { useSimulationStore } from '@/composables/demo/useSimulationStore'
import confetti from 'canvas-confetti'

const store = useSimulationStore()

interface FloatItem {
  id: string
  text: string
  color: string
  x: number
}

const floats = ref<FloatItem[]>([])
let floatId = 0

watch(
  () => store.state.timeline.length,
  () => {
    const latest = store.state.timeline[0]
    if (!latest) return

    const e = latest.event

    // 积分变化 → 飘字
    if (e.type === 'score_change' && e.delta !== undefined) {
      const isPositive = e.delta > 0
      const item: FloatItem = {
        id: `f-${++floatId}`,
        text: isPositive ? `+${e.delta} ⭐` : `${e.delta} 💔`,
        color: isPositive ? '#4A7A5E' : '#A05252',
        x: 30 + Math.random() * 40, // 随机水平位置 (30%-70%)
      }
      floats.value.push(item)
      setTimeout(() => {
        floats.value = floats.value.filter(f => f.id !== item.id)
      }, 1800)

      // 通过时撒花
      if (isPositive && e.delta >= 5) {
        confetti({
          particleCount: 40,
          spread: 60,
          origin: { x: 0.5, y: 0.7 },
          colors: ['#818CF8', '#4ADE80', '#FBBF24', '#F472B6'],
          gravity: 0.8,
          scalar: 0.8,
        })
      }
    }

    // 审查通过 → 撒花
    if (e.type === 'review' && e.result === 'approved') {
      confetti({
        particleCount: 30,
        spread: 50,
        origin: { x: 0.5, y: 0.6 },
        colors: ['#4ADE80', '#34D399', '#6EE7B7'],
        gravity: 0.9,
        scalar: 0.7,
      })
    }
  }
)
</script>

<template>
  <div class="float-container">
    <TransitionGroup name="float">
      <div
        v-for="item in floats"
        :key="item.id"
        class="float-item"
        :style="{
          color: item.color,
          left: `${item.x}%`,
        }"
      >
        {{ item.text }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.float-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 100;
}

.float-item {
  position: absolute;
  top: 40%;
  font-family: 'Lora', serif;
  font-size: 1.4rem;
  font-weight: 700;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  animation: floatUp 1.8s ease-out forwards;
}

.float-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.float-leave-active {
  transition: all 0.5s ease;
}
.float-enter-from {
  opacity: 0;
  transform: scale(0.5) translateY(20px);
}
.float-leave-to {
  opacity: 0;
}

@keyframes floatUp {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  50% {
    opacity: 1;
    transform: translateY(-40px) scale(1.2);
  }
  100% {
    opacity: 0;
    transform: translateY(-80px) scale(0.8);
  }
}
</style>
