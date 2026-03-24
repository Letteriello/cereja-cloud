<script setup lang="ts">
import type { ScenarioData } from '@/composables/demo/types'
import { Newspaper, ShoppingCart, Code, Megaphone, ShieldAlert } from 'lucide-vue-next'
import { markRaw, type Component } from 'vue'

import contentCompany from '@/composables/demo/scenarios/content-company.json'
import ecommerce from '@/composables/demo/scenarios/ecommerce.json'
import devTeam from '@/composables/demo/scenarios/dev-team.json'
import researchLab from '@/composables/demo/scenarios/research-lab.json'
import chaos from '@/composables/demo/scenarios/chaos.json'

const contentGroup = [contentCompany, ecommerce, researchLab] as unknown as ScenarioData[]
const techGroup = [devTeam] as unknown as ScenarioData[]
const systemGroup = [chaos] as unknown as ScenarioData[]

const iconMap: Record<string, Component> = {
  Newspaper: markRaw(Newspaper),
  ShoppingCart: markRaw(ShoppingCart),
  Code: markRaw(Code),
  Megaphone: markRaw(Megaphone),
  ShieldAlert: markRaw(ShieldAlert),
}

const emit = defineEmits<{
  select: [scenario: ScenarioData]
}>()
</script>

<template>
  <div class="scenario-sections">
    <div class="scenario-group">
      <h3 class="group-label">内容 & 营销</h3>
      <div class="scenario-grid scenario-grid--3">
        <button
          v-for="(s, i) in contentGroup"
          :key="s.id"
          class="scenario-card"
          :class="`scenario-card--${s.id}`"
          :style="{ animationDelay: `${i * 0.06}s` }"
          @click="emit('select', s)"
        >
          <div class="scenario-icon-wrap">
            <component :is="iconMap[s.icon]" :size="28" :stroke-width="1.5" />
          </div>
          <h3 class="scenario-name">{{ s.name }}</h3>
          <p class="scenario-desc">{{ s.description }}</p>
          <a
            v-if="s.id === 'content-company'"
            href="https://1m-reviews.com"
            target="_blank"
            class="scenario-link"
            @click.stop
          >
            🔗 1M-Reviews.com — 正由 OpenMOSS 自主运行
          </a>
          <span class="scenario-meta">
            {{ s.agents.length }} 个 AI 员工 · {{ s.duration }}s
          </span>
        </button>
      </div>
    </div>

    <div class="scenario-row">
      <div class="scenario-group scenario-group--half">
        <h3 class="group-label">技术 & 开发</h3>
        <div class="scenario-grid scenario-grid--1">
          <button
            v-for="s in techGroup"
            :key="s.id"
            class="scenario-card"
            :class="`scenario-card--${s.id}`"
            :style="{ animationDelay: '0.18s' }"
            @click="emit('select', s)"
          >
            <div class="scenario-icon-wrap">
              <component :is="iconMap[s.icon]" :size="28" :stroke-width="1.5" />
            </div>
            <h3 class="scenario-name">{{ s.name }}</h3>
            <p class="scenario-desc">{{ s.description }}</p>
            <span class="scenario-meta">
              {{ s.agents.length }} 个 AI 员工 · {{ s.duration }}s
            </span>
          </button>
        </div>
      </div>

      <div class="scenario-group scenario-group--half">
        <h3 class="group-label">系统能力</h3>
        <div class="scenario-grid scenario-grid--1">
          <button
            v-for="s in systemGroup"
            :key="s.id"
            class="scenario-card"
            :class="`scenario-card--${s.id}`"
            :style="{ animationDelay: '0.24s' }"
            @click="emit('select', s)"
          >
            <div class="scenario-icon-wrap">
              <component :is="iconMap[s.icon]" :size="28" :stroke-width="1.5" />
            </div>
            <h3 class="scenario-name">{{ s.name }}</h3>
            <p class="scenario-desc">{{ s.description }}</p>
            <span class="scenario-meta">
              {{ s.agents.length }} 个 AI 员工 · {{ s.duration }}s
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scenario-sections {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.scenario-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.group-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  font-weight: 600;
  color: #8C8A84;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding-left: 4px;
  margin: 0;
}

.scenario-row {
  display: flex;
  gap: 12px;
}

.scenario-group--half {
  flex: 1;
}

.scenario-grid {
  display: grid;
  gap: 12px;
}

.scenario-grid--3 {
  grid-template-columns: repeat(3, 1fr);
}

.scenario-grid--1 {
  grid-template-columns: 1fr;
}

.scenario-card {
  background: #FFFFFF;
  border: 1px solid #E8E6E0;
  border-radius: 10px;
  padding: 24px 20px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  text-align: center;
  animation: cardUp 0.35s ease both;
}

.scenario-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.scenario-card:active {
  transform: translateY(0);
}

/* 个性色 hover（降饱和度） */
.scenario-card--content-company:hover {
  border-color: #8B6F4E;
}
.scenario-card--ecommerce:hover {
  border-color: #C08040;
}
.scenario-card--dev-team:hover {
  border-color: #4A7FA5;
}
.scenario-card--research-lab:hover {
  border-color: #4A7A5E;
}
.scenario-card--chaos:hover {
  border-color: #A05252;
}

.scenario-icon-wrap {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: #F5F4F0;
  border: 1px solid #E8E6E0;
  color: #4A4845;
  margin-bottom: 0.3rem;
}

.scenario-name {
  font-family: 'Lora', serif;
  font-size: 1.15rem;
  font-weight: 600;
  color: #1A1917;
  margin: 0;
  letter-spacing: -0.3px;
}

.scenario-desc {
  font-size: 0.85rem;
  color: #4A4845;
  line-height: 1.6;
  margin: 0;
}

.scenario-link {
  font-size: 0.72rem;
  color: #8B6F4E;
  font-weight: 500;
  text-decoration: none;
  padding: 0.2rem 0.6rem;
  background: #F5F4F0;
  border: 1px solid #E8E6E0;
  border-radius: 4px;
  font-family: 'IBM Plex Mono', monospace;
  transition: all 0.15s;
}

.scenario-link:hover {
  background: #1A1917;
  color: #FAFAF8;
  border-color: #1A1917;
}

.scenario-meta {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  color: #8C8A84;
  margin-top: 0.4rem;
  padding: 0.2rem 0.6rem;
  background: #F5F4F0;
  border-radius: 4px;
  letter-spacing: 0.3px;
}

@media (max-width: 768px) {
  .scenario-grid--3 {
    grid-template-columns: 1fr 1fr;
  }
  .scenario-row {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .scenario-grid--3 {
    grid-template-columns: 1fr;
  }
  .scenario-card {
    padding: 20px 16px;
  }
  .scenario-icon-wrap {
    width: 40px;
    height: 40px;
  }
  .scenario-name {
    font-size: 1.05rem;
  }
}

@keyframes cardUp {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: none; }
}
</style>



