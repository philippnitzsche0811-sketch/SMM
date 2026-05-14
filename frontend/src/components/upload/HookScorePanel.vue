<template>
  <div class="hook-panel">
    <!-- Loading state -->
    <div v-if="loading" class="hook-loading">
      <i class="pi pi-spin pi-spinner"></i>
      <span>Analyzing hook…</span>
    </div>

    <!-- No result yet -->
    <div v-else-if="!hookResult" class="hook-empty">
      <i class="pi pi-clock"></i>
      <span>Hook analysis pending</span>
    </div>

    <!-- Result -->
    <template v-else>
      <div class="hook-header">
        <div class="hook-score-wrap">
          <div class="hook-score" :class="scoreClass">
            <span class="score-num">{{ hookResult.hook_score }}</span>
            <span class="score-max">/10</span>
          </div>
          <div class="hook-meta">
            <span class="hook-label">Hook Score</span>
            <div class="hook-badges">
              <span v-if="hookResult.hook_type" class="badge badge-type">
                <i class="pi pi-tag"></i> {{ hookTypeLabel }}
              </span>
              <span v-if="hookResult.audio_energy && hookResult.audio_energy !== 'unknown'" class="badge" :class="energyClass">
                <i class="pi pi-volume-up"></i> Audio: {{ audioEnergyLabel }}
              </span>
            </div>
          </div>
        </div>
        <div v-if="hookResult.audio_transcript" class="hook-transcript">
          <i class="pi pi-microphone"></i>
          <span class="transcript-text">"{{ hookResult.audio_transcript }}"</span>
        </div>
      </div>

      <div class="hook-grid">
        <!-- Strengths -->
        <div v-if="hookResult.strengths?.length" class="hook-section strengths">
          <div class="section-head">
            <i class="pi pi-check-circle"></i> Strengths
          </div>
          <ul class="feedback-list">
            <li v-for="(s, i) in hookResult.strengths" :key="i">{{ s }}</li>
          </ul>
        </div>

        <!-- Weaknesses -->
        <div v-if="hookResult.weaknesses?.length" class="hook-section weaknesses">
          <div class="section-head">
            <i class="pi pi-times-circle"></i> Weaknesses
          </div>
          <ul class="feedback-list">
            <li v-for="(w, i) in hookResult.weaknesses" :key="i">{{ w }}</li>
          </ul>
        </div>
      </div>

      <!-- Improvements -->
      <div v-if="hookResult.improvements?.length" class="hook-improvements">
        <div class="section-head improvements-head">
          <i class="pi pi-sparkles"></i> How to improve your hook
        </div>
        <ol class="improvement-list">
          <li v-for="(imp, i) in hookResult.improvements" :key="i">{{ imp }}</li>
        </ol>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface HookResult {
  hook_score: number;
  hook_type?: string;
  audio_energy?: string;
  audio_transcript?: string;
  strengths?: string[];
  weaknesses?: string[];
  improvements?: string[];
}

const props = defineProps<{
  hookResult: HookResult | null;
  loading?: boolean;
}>();

const scoreClass = computed(() => {
  if (!props.hookResult) return '';
  const s = props.hookResult.hook_score;
  if (s >= 8) return 'score-high';
  if (s >= 5) return 'score-mid';
  return 'score-low';
});

const energyClass = computed(() => {
  const e = props.hookResult?.audio_energy;
  if (e === 'high') return 'badge-energy-high';
  if (e === 'medium') return 'badge-energy-mid';
  if (e === 'low') return 'badge-energy-low';
  return 'badge-energy-none';
});

const hookTypeLabel = computed(() => {
  const map: Record<string, string> = {
    verbal: 'Verbal Hook',
    visual: 'Visual Hook',
    text_overlay: 'Text Overlay',
    music: 'Music Hook',
    combo: 'Combo Hook',
  };
  return map[props.hookResult?.hook_type || ''] || props.hookResult?.hook_type || '';
});

const audioEnergyLabel = computed(() => {
  const map: Record<string, string> = {
    high: 'High', medium: 'Medium', low: 'Low', none: 'Silent',
  };
  return map[props.hookResult?.audio_energy || ''] || props.hookResult?.audio_energy || '';
});
</script>

<style scoped>
.hook-panel {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
}

.hook-loading,
.hook-empty {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  padding: 0.5rem 0;
}

.hook-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.hook-score-wrap {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.hook-score {
  display: flex;
  align-items: baseline;
  gap: 0.1rem;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  border-radius: var(--radius-md);
  padding: 0.3rem 0.75rem;
  min-width: 70px;
  justify-content: center;
}
.score-num { font-size: 1.75rem; line-height: 1; }
.score-max { font-size: 0.875rem; color: inherit; opacity: 0.7; }

.score-high { background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.score-mid  { background: rgba(234,179,8,0.15);   color: #eab308; border: 1px solid rgba(234,179,8,0.3); }
.score-low  { background: rgba(239,68,68,0.15);   color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

.hook-meta {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.hook-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.hook-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.2rem 0.5rem;
  border-radius: 20px;
  border: 1px solid;
}
.badge-type           { background: rgba(99,102,241,0.12); color: #818cf8; border-color: rgba(99,102,241,0.25); }
.badge-energy-high    { background: rgba(34,197,94,0.1);   color: #22c55e; border-color: rgba(34,197,94,0.25); }
.badge-energy-mid     { background: rgba(234,179,8,0.1);   color: #eab308; border-color: rgba(234,179,8,0.25); }
.badge-energy-low     { background: rgba(148,163,184,0.1); color: #94a3b8; border-color: rgba(148,163,184,0.25); }
.badge-energy-none    { background: rgba(239,68,68,0.1);   color: #ef4444; border-color: rgba(239,68,68,0.25); }

.hook-transcript {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 0.6rem 0.875rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}
.hook-transcript .pi { margin-top: 0.1rem; flex-shrink: 0; }
.transcript-text { font-style: italic; line-height: 1.5; }

.hook-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.875rem;
  margin-bottom: 0.875rem;
}

.hook-section {
  border-radius: var(--radius-md);
  padding: 0.75rem;
}
.strengths  { background: rgba(34,197,94,0.06);  border: 1px solid rgba(34,197,94,0.15); }
.weaknesses { background: rgba(239,68,68,0.06);  border: 1px solid rgba(239,68,68,0.15); }

.section-head {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}
.strengths  .section-head .pi { color: #22c55e; }
.weaknesses .section-head .pi { color: #ef4444; }

.feedback-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.feedback-list li {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  line-height: 1.45;
  padding-left: 0.875rem;
  position: relative;
}
.feedback-list li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--text-disabled);
}

.hook-improvements {
  background: rgba(99,102,241,0.06);
  border: 1px solid rgba(99,102,241,0.15);
  border-radius: var(--radius-md);
  padding: 0.875rem;
}
.improvements-head {
  color: #818cf8;
  margin-bottom: 0.625rem;
}
.improvements-head .pi { color: #818cf8; }

.improvement-list {
  padding-left: 1.25rem;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.improvement-list li {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

@media (max-width: 640px) {
  .hook-grid { grid-template-columns: 1fr; }
}
</style>
