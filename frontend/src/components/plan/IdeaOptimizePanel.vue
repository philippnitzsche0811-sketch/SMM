<template>
  <div class="optimize-panel">
    <div class="panel-header">
      <div class="panel-title-row">
        <i class="pi pi-sparkles panel-icon"></i>
        <div>
          <h3 class="panel-title">{{ idea.title }}</h3>
          <p class="panel-sub" v-if="idea.concept">{{ idea.concept }}</p>
        </div>
      </div>
      <button class="panel-close" @click="$emit('close')"><i class="pi pi-times"></i></button>
    </div>

    <!-- Loading AI -->
    <div v-if="loading" class="panel-loading">
      <i class="pi pi-spin pi-spinner"></i>
      <span>Generating ideas…</span>
    </div>

    <template v-else>

      <!-- ── Video Structure (Free + Pro) ──────────────────────── -->
      <div class="panel-section">
        <div class="section-label"><i class="pi pi-list"></i> Recommended Structure</div>
        <div class="structure-list">
          <div v-for="(step, i) in videoStructure" :key="i" class="structure-step">
            <span class="structure-time">{{ step.time }}</span>
            <span class="structure-desc">{{ step.desc }}</span>
          </div>
        </div>
      </div>

      <!-- ── Hook Suggestions (Pro AI) ─────────────────────────── -->
      <template v-if="isProUser && suggestions">
        <div class="panel-section">
          <div class="section-label"><i class="pi pi-bolt"></i> Hook Ideas</div>
          <div class="hook-list">
            <div v-for="(hook, i) in hookSuggestions" :key="i" class="hook-item">
              <span class="hook-num">{{ i + 1 }}</span>
              <span class="hook-text">{{ hook }}</span>
            </div>
          </div>
        </div>

        <div class="panel-section" v-if="titleOptions.length > 0">
          <div class="section-label"><i class="pi pi-pen-to-square"></i> Title Ideas</div>
          <div class="title-list">
            <div
              v-for="(title, i) in titleOptions"
              :key="i"
              class="title-chip"
              @click="copyText(title)"
              title="Copy"
            >
              {{ title }}
              <i class="pi pi-copy copy-icon"></i>
            </div>
          </div>
        </div>
      </template>

      <!-- ── Pro Upgrade Teaser (Free only) ────────────────────── -->
      <div v-if="!isProUser" class="panel-section">
        <div class="pro-teaser">
          <i class="pi pi-sparkles pro-teaser-icon"></i>
          <div class="pro-teaser-text">
            <span class="pro-teaser-title">Pro: AI-generated hook ideas</span>
            <span class="pro-teaser-sub">Get 3 hook suggestions + title ideas tailored to this concept</span>
          </div>
          <button class="pro-teaser-btn" @click="$router.push('/settings?tab=account')">Upgrade</button>
        </div>
      </div>

      <!-- ── Script Feedback (Planning status, Pro) ─────────────── -->
      <div v-if="idea.status === 'planning'" class="panel-section">
        <div class="section-label"><i class="pi pi-file-edit"></i> Script Feedback</div>

        <div v-if="!isProUser" class="pro-teaser pro-teaser--small">
          <i class="pi pi-lock pro-teaser-icon"></i>
          <div class="pro-teaser-text">
            <span class="pro-teaser-title">Pro: Script analysis</span>
            <span class="pro-teaser-sub">Paste your script or upload audio to get AI feedback before you film</span>
          </div>
          <button class="pro-teaser-btn" @click="$router.push('/settings?tab=account')">Upgrade</button>
        </div>

        <template v-else>
          <div class="script-input-toggle">
            <button
              class="toggle-btn"
              :class="{ active: scriptInputMode === 'text' }"
              @click="scriptInputMode = 'text'"
            >Text</button>
            <button
              class="toggle-btn"
              :class="{ active: scriptInputMode === 'audio' }"
              @click="scriptInputMode = 'audio'"
            >Audio / Video</button>
          </div>

          <div v-if="scriptInputMode === 'text'" class="script-text-section">
            <textarea
              v-model="scriptText"
              class="script-textarea"
              placeholder="Paste your script, bullet points, or rough notes here…"
              rows="5"
            ></textarea>
          </div>

          <div v-else class="script-audio-section">
            <label class="audio-upload-label">
              <i class="pi pi-upload"></i>
              <span v-if="!audioFile">Upload audio or video (MP3, MP4, MOV · max 25 MB)</span>
              <span v-else class="audio-filename">{{ audioFile.name }}</span>
              <input
                type="file"
                accept="audio/*,video/mp4,video/quicktime"
                class="audio-input-hidden"
                @change="onAudioFile"
              />
            </label>
          </div>

          <button
            class="btn-analyze"
            :disabled="!canAnalyze || scriptAnalyzing"
            @click="runScriptAnalysis"
          >
            <i v-if="scriptAnalyzing" class="pi pi-spin pi-spinner"></i>
            <i v-else class="pi pi-search"></i>
            {{ scriptAnalyzing ? 'Analyzing…' : 'Analyze Script' }}
          </button>

          <!-- Analysis result -->
          <div v-if="scriptResult" class="script-result">
            <div class="hook-score-row">
              <span class="score-label">Hook score</span>
              <div class="score-dots">
                <span
                  v-for="n in 5"
                  :key="n"
                  class="score-dot"
                  :class="{ filled: n <= scriptResult.hook_score }"
                ></span>
              </div>
              <span class="score-num">{{ scriptResult.hook_score }}/5</span>
            </div>

            <div class="result-block">
              <div class="result-block-label"><i class="pi pi-bolt"></i> Hook</div>
              <p class="result-text">{{ scriptResult.hook_feedback }}</p>
            </div>

            <div class="result-block">
              <div class="result-block-label"><i class="pi pi-list"></i> Structure</div>
              <p class="result-text">{{ scriptResult.structure_feedback }}</p>
            </div>

            <div class="result-block">
              <div class="result-block-label"><i class="pi pi-lightbulb"></i> Tips</div>
              <ul class="tips-list">
                <li v-for="(tip, i) in scriptResult.tips" :key="i">{{ tip }}</li>
              </ul>
            </div>
          </div>
        </template>
      </div>

      <!-- ── Actions ─────────────────────────────────────────────── -->
      <div class="panel-actions">
        <button v-if="isProUser" class="btn-regen" @click="loadSuggestions" :disabled="loading">
          <i class="pi pi-refresh"></i> Regenerate
        </button>
        <button
          v-if="idea.status === 'ready'"
          class="btn-upload-idea"
          @click="goToUpload"
        >
          <i class="pi pi-cloud-upload"></i> Upload Now
        </button>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { usePlan } from '@/composables/usePlan';
import { optimizeSuggest, analyzeScriptText, analyzeScriptAudio } from '@/services/api';
import { useToast } from 'primevue/usetoast';

interface Idea {
  id: string;
  title: string;
  concept?: string;
  target_platforms: string[];
  status: string;
  tags?: string[];
}

const props = defineProps<{ idea: Idea }>();
const emit = defineEmits<{ close: [] }>();

const router    = useRouter();
const authStore = useAuthStore();
const toast     = useToast();
const { isProUser } = usePlan();

const loading     = ref(false);
const suggestions = ref<any>(null);

// Script analysis state
const scriptInputMode = ref<'text' | 'audio'>('text');
const scriptText      = ref('');
const audioFile       = ref<File | null>(null);
const scriptAnalyzing = ref(false);
const scriptResult    = ref<{
  hook_score: number;
  hook_feedback: string;
  structure_feedback: string;
  tips: string[];
} | null>(null);

const canAnalyze = computed(() =>
  scriptInputMode.value === 'text' ? scriptText.value.trim().length > 20 : !!audioFile.value
);

const hookSuggestions = computed<string[]>(() => {
  if (!suggestions.value) return [];
  const firstPlatform = props.idea.target_platforms[0] || 'youtube';
  const sug = suggestions.value[firstPlatform] ?? Object.values(suggestions.value)[0] as any;
  if (!sug) return [];
  const opts: string[] = sug.title_options ?? [];
  return opts.slice(0, 3).map((t: string) => {
    if (t.includes('?')) return t;
    if (t.startsWith('Wie') || t.startsWith('Warum') || t.startsWith('Was')) return t + '?';
    return t;
  });
});

const titleOptions = computed<string[]>(() => {
  if (!suggestions.value) return [];
  const firstPlatform = props.idea.target_platforms[0] || 'youtube';
  const sug = suggestions.value[firstPlatform] ?? Object.values(suggestions.value)[0] as any;
  return sug?.title_options ?? [sug?.title ?? props.idea.title];
});

const videoStructure = computed(() => {
  const concept = (props.idea.concept || '').toLowerCase();
  const platforms = props.idea.target_platforms;
  const isShort = platforms.includes('tiktok') || platforms.includes('instagram');
  if (isShort) {
    return [
      { time: '0–3s',  desc: 'Hook — surprise or ask a question' },
      { time: '3–15s', desc: 'Show the problem or context' },
      { time: '15–45s', desc: 'Solution, tip, or main content' },
      { time: '45–60s', desc: 'CTA — follow, comment, save' },
    ];
  }
  if (concept.includes('tutorial') || concept.includes('how to') || concept.includes('anleitung')) {
    return [
      { time: '0–15s',  desc: 'Hook — preview the result' },
      { time: '15–60s', desc: 'Explain the problem and why it matters' },
      { time: '1–8min', desc: 'Step-by-step walkthrough' },
      { time: 'End',    desc: 'Summary + CTA' },
    ];
  }
  return [
    { time: '0–30s',  desc: 'Hook — why should they keep watching?' },
    { time: '30s–2min', desc: 'Main content — core message' },
    { time: '2–5min', desc: 'Detail, examples, or context' },
    { time: 'End',    desc: 'CTA — like, comment, subscribe' },
  ];
});

async function loadSuggestions() {
  if (!isProUser.value || !authStore.userId) return;
  loading.value = true;
  try {
    const platforms = props.idea.target_platforms.length > 0
      ? props.idea.target_platforms : ['youtube'];
    const data = await optimizeSuggest({
      user_id: authStore.userId,
      title_draft: props.idea.title,
      description_draft: props.idea.concept || props.idea.title,
      category: 'default',
      platforms,
    });
    suggestions.value = data.suggestions ?? null;
  } catch {
    toast.add({ severity: 'warn', summary: 'AI unavailable', detail: 'Please try again later.', life: 4000 });
  } finally {
    loading.value = false;
  }
}

function onAudioFile(event: Event) {
  const input = event.target as HTMLInputElement;
  audioFile.value = input.files?.[0] ?? null;
}

async function runScriptAnalysis() {
  if (!authStore.userId || !canAnalyze.value) return;
  scriptAnalyzing.value = true;
  scriptResult.value = null;
  try {
    const platforms = props.idea.target_platforms.length > 0 ? props.idea.target_platforms : ['youtube'];
    if (scriptInputMode.value === 'text') {
      scriptResult.value = await analyzeScriptText({
        user_id: authStore.userId,
        idea_title: props.idea.title,
        text: scriptText.value,
        platforms,
      });
    } else if (audioFile.value) {
      scriptResult.value = await analyzeScriptAudio({
        user_id: authStore.userId,
        idea_title: props.idea.title,
        platforms,
        file: audioFile.value,
      });
    }
  } catch (err: any) {
    if (err?.response?.status === 403) {
      toast.add({ severity: 'warn', summary: 'Pro required', detail: 'Script analysis requires a Pro plan.', life: 4000 });
    } else {
      toast.add({ severity: 'error', summary: 'Analysis failed', detail: 'Please try again.', life: 4000 });
    }
  } finally {
    scriptAnalyzing.value = false;
  }
}

function copyText(text: string) {
  navigator.clipboard.writeText(text).catch(() => {});
  toast.add({ severity: 'success', summary: 'Copied', life: 1500 });
}

function goToUpload() {
  router.push({
    path: '/upload',
    query: {
      title: props.idea.title,
      description: props.idea.concept || '',
      platforms: (props.idea.target_platforms || []).join(','),
      tags: (props.idea.tags || []).join(','),
    },
  });
}

onMounted(() => { if (isProUser.value) loadSuggestions(); });
watch(() => props.idea.id, () => {
  suggestions.value = null;
  scriptResult.value = null;
  scriptText.value = '';
  audioFile.value = null;
  if (isProUser.value) loadSuggestions();
});
</script>

<style scoped>
.optimize-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 1.25rem 1.25rem 0.875rem;
  border-bottom: 1px solid var(--border-color, #3f3f46);
  position: sticky;
  top: 0;
  background: var(--surface-card, #27272a);
  z-index: 1;
}

.panel-title-row {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  flex: 1;
  min-width: 0;
}

.panel-icon { font-size: 1rem; color: #a78bfa; margin-top: 2px; flex-shrink: 0; }
.panel-title { font-size: 0.9rem; font-weight: 700; color: var(--text-primary, #f4f4f5); margin: 0; line-height: 1.3; }
.panel-sub {
  font-size: 0.75rem; color: var(--text-muted, #71717a); margin: 0.2rem 0 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

.panel-close {
  background: none; border: none; color: var(--text-muted, #71717a);
  cursor: pointer; font-size: 0.9rem; padding: 2px; flex-shrink: 0;
}

.panel-loading {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.75rem; padding: 3rem 1rem; color: var(--text-muted, #71717a); font-size: 0.875rem;
}

.panel-section {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color, #3f3f46);
}
.panel-section:last-of-type { border-bottom: none; }

.section-label {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--text-muted, #71717a); margin-bottom: 0.625rem;
}

/* Structure */
.structure-list { display: flex; flex-direction: column; gap: 0.35rem; }
.structure-step { display: flex; align-items: flex-start; gap: 0.625rem; font-size: 0.8125rem; }
.structure-time { min-width: 55px; font-size: 0.72rem; font-weight: 700; color: #a78bfa; padding-top: 1px; }
.structure-desc { color: var(--text-primary, #f4f4f5); line-height: 1.4; }

/* Hooks */
.hook-list { display: flex; flex-direction: column; gap: 0.5rem; }
.hook-item {
  display: flex; align-items: flex-start; gap: 0.5rem;
  background: rgba(124,58,237,0.07); border: 1px solid rgba(124,58,237,0.15);
  border-radius: 7px; padding: 0.5rem 0.625rem;
}
.hook-num {
  width: 18px; height: 18px; border-radius: 50%;
  background: rgba(124,58,237,0.2); color: #a78bfa;
  font-size: 0.7rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px;
}
.hook-text { font-size: 0.8125rem; color: var(--text-primary, #f4f4f5); line-height: 1.4; }

/* Titles */
.title-list { display: flex; flex-direction: column; gap: 0.35rem; }
.title-chip {
  display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
  padding: 0.4rem 0.625rem;
  background: rgba(255,255,255,0.03); border: 1px solid var(--border-color, #3f3f46);
  border-radius: 7px; font-size: 0.8rem; color: var(--text-primary, #f4f4f5);
  cursor: pointer; transition: background 0.15s;
}
.title-chip:hover { background: rgba(255,255,255,0.06); }
.copy-icon { font-size: 0.7rem; color: var(--text-muted, #71717a); flex-shrink: 0; }

/* Pro teaser */
.pro-teaser {
  display: flex; align-items: center; gap: 0.75rem;
  background: rgba(124,58,237,0.06); border: 1px solid rgba(124,58,237,0.2);
  border-radius: 10px; padding: 0.75rem 0.875rem;
}
.pro-teaser--small { padding: 0.625rem 0.75rem; }
.pro-teaser-icon { font-size: 1rem; color: #a78bfa; flex-shrink: 0; }
.pro-teaser-text { flex: 1; min-width: 0; }
.pro-teaser-title { display: block; font-size: 0.8125rem; font-weight: 700; color: var(--text-primary, #f4f4f5); }
.pro-teaser-sub { display: block; font-size: 0.74rem; color: var(--text-muted, #71717a); margin-top: 0.15rem; }
.pro-teaser-btn {
  padding: 0.3rem 0.75rem; background: rgba(124,58,237,0.2);
  border: 1px solid rgba(124,58,237,0.35); border-radius: 6px;
  color: #c4b5fd; font-size: 0.75rem; font-weight: 600; cursor: pointer;
  white-space: nowrap; transition: background 0.15s;
}
.pro-teaser-btn:hover { background: rgba(124,58,237,0.35); }

/* Script analysis */
.script-input-toggle {
  display: flex; gap: 0; margin-bottom: 0.75rem;
  border: 1px solid var(--border-color, #3f3f46); border-radius: 8px; overflow: hidden;
}
.toggle-btn {
  flex: 1; padding: 0.4rem 0; background: none; border: none;
  color: var(--text-muted, #71717a); font-size: 0.8rem; font-weight: 500; cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.toggle-btn.active { background: rgba(124,58,237,0.15); color: #a78bfa; }

.script-textarea {
  width: 100%; box-sizing: border-box;
  background: rgba(255,255,255,0.03); border: 1px solid var(--border-color, #3f3f46);
  border-radius: 8px; color: var(--text-primary, #f4f4f5); font-size: 0.8125rem;
  padding: 0.625rem 0.75rem; resize: vertical; outline: none; font-family: inherit;
}
.script-textarea:focus { border-color: rgba(124,58,237,0.4); }

.audio-upload-label {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 1rem; background: rgba(255,255,255,0.02);
  border: 1px dashed var(--border-color, #3f3f46); border-radius: 8px;
  cursor: pointer; font-size: 0.8125rem; color: var(--text-muted, #71717a);
  transition: border-color 0.15s;
}
.audio-upload-label:hover { border-color: rgba(124,58,237,0.4); color: var(--text-secondary); }
.audio-filename { color: var(--text-primary); font-weight: 600; }
.audio-input-hidden { display: none; }

.btn-analyze {
  display: inline-flex; align-items: center; gap: 0.4rem;
  margin-top: 0.75rem; padding: 0.45rem 1rem;
  background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.3);
  border-radius: 8px; color: #c4b5fd; font-size: 0.8125rem; font-weight: 600;
  cursor: pointer; transition: background 0.15s;
}
.btn-analyze:not(:disabled):hover { background: rgba(124,58,237,0.25); }
.btn-analyze:disabled { opacity: 0.5; cursor: not-allowed; }

/* Script result */
.script-result { margin-top: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }

.hook-score-row {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 0.5rem 0.75rem; background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color); border-radius: 8px;
}
.score-label { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); flex-shrink: 0; }
.score-dots { display: flex; gap: 4px; flex: 1; }
.score-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: rgba(255,255,255,0.1); transition: background 0.15s;
}
.score-dot.filled { background: #a78bfa; }
.score-num { font-size: 0.8rem; font-weight: 700; color: #a78bfa; flex-shrink: 0; }

.result-block { display: flex; flex-direction: column; gap: 0.3rem; }
.result-block-label {
  display: flex; align-items: center; gap: 0.35rem;
  font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--text-muted, #71717a);
}
.result-text { font-size: 0.8125rem; color: var(--text-primary); line-height: 1.5; margin: 0; }

.tips-list { margin: 0; padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.3rem; }
.tips-list li { font-size: 0.8125rem; color: var(--text-primary); line-height: 1.4; }

/* Actions */
.panel-actions {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 1rem 1.25rem; border-top: 1px solid var(--border-color, #3f3f46);
  margin-top: auto;
}

.btn-regen {
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.4rem 0.875rem; background: none;
  border: 1px solid var(--border-color, #3f3f46); border-radius: 7px;
  color: var(--text-secondary, #a1a1aa); font-size: 0.8rem; font-weight: 600;
  cursor: pointer; transition: background 0.15s;
}
.btn-regen:hover { background: rgba(255,255,255,0.04); }
.btn-regen:disabled { opacity: 0.5; cursor: default; }

.btn-upload-idea {
  flex: 1; display: inline-flex; align-items: center; justify-content: center; gap: 0.4rem;
  padding: 0.5rem 1rem; background: linear-gradient(135deg, #4f7fff, #7c3aed);
  color: white; border: none; border-radius: 8px;
  font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s;
}
.btn-upload-idea:hover { opacity: 0.85; }
</style>
