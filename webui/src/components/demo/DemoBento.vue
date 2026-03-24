<script setup lang="ts">
import { Users, RefreshCcw, ShieldCheck, Trophy, Repeat } from 'lucide-vue-next'
import { markRaw, type Component } from 'vue'

const features: {
  title: string
  icon: Component
  desc: string
  span: string
  accent: string
  bg?: string
  color?: string
}[] = [
  {
    title: '多 Agent 自组织协作',
    icon: markRaw(Users),
    desc: '规划者拆需求、执行者干活、审查者把关、巡查者兜底——4 种角色各司其职，全程零人工编排，像一家真正的公司一样自主运转。',
    span: 'wide',
    accent: '#1A1917',
    bg: '#1A1917',
    color: '#FAFAF8',
  },
  {
    title: '闭环质量控制',
    icon: markRaw(RefreshCcw),
    desc: '逐条批注 + 打分，不达标自动驳回返工。「提交 → 审查 → 返工 → 再审」循环往复，直到产出合格，交付物质量有保障。',
    span: 'normal',
    accent: '#8B6F4E',
  },
  {
    title: '自愈巡检 · 永不嬕机',
    icon: markRaw(ShieldCheck),
    desc: '巡查者持续扫描系统全局，卡死的任务自动标记修复、异常流程自动告警——Agent「死亡率」降至 0%，7×24 无人值守。',
    span: 'normal',
    accent: '#4A7A5E',
  },
  {
    title: '积分排行 · 数据驱动',
    icon: markRaw(Trophy),
    desc: '审查结果实时写入积分排行榜。谁干得好一目了然——用数据代替管理，让 AI 团队自我进化。',
    span: 'normal',
    accent: '#C09840',
  },
  {
    title: '循环任务 · 持续运营',
    icon: markRaw(Repeat),
    desc: '内置 recurring 任务类型，设定目标后自动循环执行。实测两天自动产出 20+ 篇文章——适合资讯采集、内容发布等 7×24 持续运营场景。',
    span: 'wide',
    accent: '#4A7FA5',
  },
]
</script>

<template>
  <section class="bento-section">
    <h2 class="bento-heading">核心能力</h2>
    <p class="bento-sub">一个完整的 AI 组织需要什么？</p>
    <div class="bento-grid">
      <div
        v-for="(f, i) in features"
        :key="f.title"
        class="bento-card"
        :class="{ 'bento-card--wide': f.span === 'wide', 'bento-card--dark': f.bg }"
        :style="{
          '--bento-accent': f.accent,
          backgroundColor: f.bg || '#FFFFFF',
          color: f.color || '#1A1917',
          animationDelay: `${i * 0.06}s`,
        }"
      >
        <div class="bento-icon" :class="{ 'bento-icon--dark': f.bg }">
          <component :is="f.icon" :size="22" :stroke-width="1.8" />
        </div>
        <h3 class="bento-title">{{ f.title }}</h3>
        <p class="bento-desc">{{ f.desc }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.bento-section {
  max-width: 900px;
  margin: 0 auto;
  padding: 48px 40px 56px;
  text-align: center;
}

.bento-heading {
  font-family: 'Lora', serif;
  font-size: 28px;
  font-weight: 700;
  color: #1A1917;
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}

.bento-sub {
  font-size: 15px;
  color: #8C8A84;
  margin: 0 0 28px;
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 10px;
}

.bento-card {
  border: 1px solid #E8E6E0;
  border-radius: 12px;
  padding: 28px 24px;
  text-align: left;
  grid-column: span 4;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: fadeUp 0.4s ease both;
}

.bento-card--wide {
  grid-column: span 8;
}

.bento-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.bento-card--dark {
  border-color: transparent;
}

.bento-card--dark:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.2);
}

.bento-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9px;
  background: #F5F4F0;
  border: 1px solid #E8E6E0;
  color: var(--bento-accent);
  margin-bottom: 14px;
}

.bento-icon--dark {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.15);
  color: #FAFAF8;
}

.bento-title {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 6px;
  letter-spacing: -0.3px;
}

.bento-desc {
  font-size: 13.5px;
  line-height: 1.7;
  opacity: 0.78;
  margin: 0;
}

.bento-card--dark .bento-desc {
  opacity: 0.7;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: none; }
}

@media (max-width: 768px) {
  .bento-grid {
    grid-template-columns: 1fr 1fr;
  }
  .bento-card,
  .bento-card--wide {
    grid-column: span 1;
  }
  .bento-section {
    padding: 32px 20px 40px;
  }
}

@media (max-width: 480px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }
}
</style>
