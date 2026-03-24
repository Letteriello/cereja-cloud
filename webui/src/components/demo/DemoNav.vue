<script setup lang="ts">
import { Star, Play } from 'lucide-vue-next'

defineProps<{
  showCta?: boolean
}>()

const emit = defineEmits<{
  startDemo: []
}>()

function scrollToBento() {
  const el = document.querySelector('.bento-section')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <nav class="demo-nav">
    <div class="nav-left">
      <a href="/" class="nav-logo">
        <span class="nav-logo-icon">M</span>
        OpenMOSS
      </a>
      <ul class="nav-links">
        <li><a href="https://github.com/uluckyXH/OpenMOSS" target="_blank">GitHub</a></li>
        <li><a href="#bento" @click.prevent="scrollToBento">功能</a></li>
        <li><a href="https://github.com/uluckyXH/OpenMOSS#quick-start" target="_blank">文档</a></li>
        <li><a href="https://1m-reviews.com" target="_blank">案例</a></li>
      </ul>
    </div>
    <div class="nav-right">
      <a
        class="nav-btn nav-btn--ghost"
        href="https://github.com/uluckyXH/OpenMOSS"
        target="_blank"
      >
        <Star :size="14" :stroke-width="2" />
        Star
      </a>
      <button
        v-if="showCta"
        class="nav-btn nav-btn--dark"
        @click="emit('startDemo')"
      >
        <Play :size="13" :stroke-width="2.5" fill="currentColor" />
        开始体验
      </button>
    </div>
  </nav>
</template>

<style scoped>
.demo-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(250, 250, 248, 0.88);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #E8E6E0;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 28px;
}

.nav-logo {
  font-family: 'Lora', serif;
  font-weight: 700;
  font-size: 17px;
  color: #1A1917;
  letter-spacing: -0.3px;
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.nav-logo-icon {
  width: 24px;
  height: 24px;
  background: #1A1917;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Lora', serif;
  font-size: 13px;
  font-weight: 700;
  color: #FAFAF8;
}

.nav-links {
  display: flex;
  gap: 0;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-links a {
  color: #4A4845;
  text-decoration: none;
  font-family: 'Instrument Sans', sans-serif;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 5px;
  transition: background 0.15s, color 0.15s;
}

.nav-links a:hover {
  background: #EEECEA;
  color: #1A1917;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-btn {
  padding: 6px 14px;
  border-radius: 6px;
  font-family: 'Instrument Sans', sans-serif;
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  text-decoration: none;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.nav-btn--ghost {
  background: none;
  color: #4A4845;
}

.nav-btn--ghost:hover {
  background: #EEECEA;
  color: #1A1917;
}

.nav-btn--dark {
  background: #1A1917;
  color: #FAFAF8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.nav-btn--dark:hover {
  background: #2e2b27;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
}

/* 移动端隐藏链接 */
@media (max-width: 640px) {
  .nav-links {
    display: none;
  }
  .demo-nav {
    padding: 0 16px;
  }
}
</style>
