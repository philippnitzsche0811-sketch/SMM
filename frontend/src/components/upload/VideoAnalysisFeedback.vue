<template>
  <div class="feedback">
    <div class="feedback-header">
      <div class="score-badge" :class="scoreClass">
        <span class="score-value">{{ result.overall_score }}</span>
        <span class="score-max">/10</span>
      </div>
      <div class="feedback-summary">
        <h3>AI Video Analysis</h3>
        <p>{{ result.summary }}</p>
      </div>
    </div>

    <div class="feedback-panels">
      <div class="panel">
        <div class="panel-header panel-header--pacing">
          <i class="pi pi-chart-line"></i>
          Pacing
        </div>
        <ul>
          <li v-for="(s, i) in result.pacing_suggestions" :key="i">{{ s }}</li>
        </ul>
      </div>

      <div class="panel">
        <div class="panel-header panel-header--quality">
          <i class="pi pi-star"></i>
          Content Quality
        </div>
        <ul>
          <li v-for="(s, i) in result.content_quality" :key="i">{{ s }}</li>
        </ul>
      </div>

      <div class="panel">
        <div class="panel-header panel-header--cuts">
          <i class="pi pi-sliders-h"></i>
          Cut Suggestions
        </div>
        <ul>
          <li v-for="(s, i) in result.cut_suggestions" :key="i">{{ s }}</li>
        </ul>
      </div>

      <div class="panel">
        <div class="panel-header panel-header--sound">
          <i class="pi pi-volume-up"></i>
          Sound
        </div>
        <ul>
          <li v-for="(s, i) in result.sound_recommendations" :key="i">{{ s }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AnalysisResult } from '@/types/analysis.types';

const props = defineProps<{ result: AnalysisResult }>();

const scoreClass = computed(() => {
  if (props.result.overall_score >= 8) return 'score--high';
  if (props.result.overall_score >= 5) return 'score--mid';
  return 'score--low';
});
</script>

<style scoped>
.feedback { display: flex; flex-direction: column; gap: 1.25rem; }

.feedback-header {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  padding: 1.25rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
}

.score-badge {
  display: flex;
  align-items: baseline;
  gap: 2px;
  padding: 0.5rem 0.875rem;
  border-radius: 10px;
  flex-shrink: 0;
}
.score--high  { background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3); }
.score--mid   { background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.3); }
.score--low   { background: rgba(239,68,68,0.15);  border: 1px solid rgba(239,68,68,0.3);  }

.score-value {
  font-size: 2rem;
  font-weight: 800;
  font-family: 'Poppins', sans-serif;
  line-height: 1;
}
.score--high .score-value  { color: #6ee7b7; }
.score--mid  .score-value  { color: #fcd34d; }
.score--low  .score-value  { color: #fca5a5; }
.score-max { font-size: 0.875rem; color: var(--text-disabled); }

.feedback-summary h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.35rem;
}
.feedback-summary p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.55;
  margin: 0;
}

.feedback-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.875rem;
}

.panel {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.panel-header--pacing  { background: rgba(79,127,255,0.12);  color: #93c5fd; }
.panel-header--quality { background: rgba(16,185,129,0.12);  color: #6ee7b7; }
.panel-header--cuts    { background: rgba(139,92,246,0.12);  color: #c4b5fd; }
.panel-header--sound   { background: rgba(245,158,11,0.12);  color: #fcd34d; }

ul {
  list-style: none;
  margin: 0;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
li {
  font-size: 0.825rem;
  color: var(--text-secondary);
  line-height: 1.45;
  padding-left: 1rem;
  position: relative;
}
li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--text-disabled);
  font-size: 0.75rem;
}

@media (max-width: 640px) {
  .feedback-panels { grid-template-columns: 1fr; }
  .feedback-header { flex-direction: column; }
}
</style>
