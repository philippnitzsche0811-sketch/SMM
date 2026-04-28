<template>
  <div class="optimizer-panel">
    <div class="optimizer-header">
      <i class="pi pi-sparkles"></i>
      <span class="optimizer-title">AI Suggestions</span>
      <small class="optimizer-hint">Click "Apply" to use a suggestion in the form</small>
    </div>

    <div class="platform-cards">
      <div
        v-for="(suggestion, platform) in suggestions"
        :key="platform"
        class="platform-card"
      >
        <div class="platform-header">
          <span class="platform-badge" :class="`badge-${platform}`">
            {{ platformLabel(platform as string) }}
          </span>
        </div>

        <div class="suggestion-block">
          <div class="suggestion-label">Title</div>
          <div class="suggestion-text">{{ suggestion.title }}</div>
          <Button label="Apply" size="small" outlined class="apply-btn" @click="$emit('apply-title', suggestion.title)" />
        </div>

        <div class="suggestion-block">
          <div class="suggestion-label">Description</div>
          <div class="suggestion-text description-preview">{{ suggestion.description }}</div>
          <Button label="Apply" size="small" outlined class="apply-btn" @click="$emit('apply-description', suggestion.description)" />
        </div>

        <div class="suggestion-block">
          <div class="suggestion-label">Hashtags</div>
          <div class="tags-row">
            <span v-for="tag in suggestion.tags.slice(0, 12)" :key="tag" class="tag-chip">#{{ tag }}</span>
          </div>
          <Button label="Apply" size="small" outlined class="apply-btn" @click="$emit('apply-tags', suggestion.tags)" />
        </div>

        <div class="suggestion-block">
          <div class="suggestion-label">Best Upload Times</div>
          <div class="times-list">
            <div v-for="time in suggestion.upload_times.slice(0, 3)" :key="time" class="time-entry">
              {{ formatDateTime(time) }}
            </div>
            <div v-if="suggestion.upload_times.length === 0" class="time-entry muted">
              No data yet &mdash; improves after more uploads
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from 'primevue/button'
import type { OptimizerSuggestions } from '@/types/optimizer.types'

defineProps<{ suggestions: OptimizerSuggestions }>()
defineEmits<{
  'apply-title':       [value: string]
  'apply-description': [value: string]
  'apply-tags':        [value: string[]]
}>()

const platformLabel = (platform: string) =>
  ({ youtube: 'YouTube', tiktok: 'TikTok', instagram: 'Instagram' }[platform] ?? platform)

const formatDateTime = (iso: string) => {
  try {
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'short', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    }).format(new Date(iso))
  } catch { return iso }
}
</script>

<style scoped>
.optimizer-panel {
  margin-top: 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.optimizer-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
}

.optimizer-header i { font-size: 1rem; }

.optimizer-title {
  font-weight: 700;
  font-size: 0.9375rem;
  flex: 1;
}

.optimizer-hint {
  opacity: 0.8;
  font-size: 0.78rem;
}

.platform-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.platform-card {
  padding: 1rem;
  border-right: 1px solid var(--border-color);
}
.platform-card:last-child { border-right: none; }

.platform-header { margin-bottom: 0.75rem; }

.platform-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 99px;
  font-size: 0.78rem;
  font-weight: 700;
  color: white;
}
.badge-youtube   { background: #ff0000; }
.badge-tiktok    { background: #010101; }
.badge-instagram { background: linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); }

.suggestion-block {
  margin-bottom: 0.875rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid #f1f5f9;
}
.suggestion-block:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }

.suggestion-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 0.3rem;
}

.suggestion-text {
  font-size: 0.875rem;
  line-height: 1.45;
  color: var(--text-primary);
  margin-bottom: 0.4rem;
}

.description-preview {
  max-height: 3.5rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.apply-btn { font-size: 0.75rem !important; padding: 0.2rem 0.55rem !important; }

.tags-row { display: flex; flex-wrap: wrap; gap: 0.25rem; margin-bottom: 0.4rem; }

.tag-chip {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-radius: 4px;
  padding: 0.15rem 0.4rem;
  font-size: 0.75rem;
}

.times-list { display: flex; flex-direction: column; gap: 0.2rem; }

.time-entry {
  font-size: 0.825rem;
  color: var(--text-primary);
  padding: 0.2rem 0.4rem;
  background: var(--bg-secondary);
  border-radius: 4px;
}

.time-entry.muted { color: var(--text-secondary); font-style: italic; }

@media (max-width: 640px) {
  .platform-cards { grid-template-columns: 1fr; }
  .platform-card { border-right: none; border-bottom: 1px solid var(--border-color); }
  .platform-card:last-child { border-bottom: none; }
  .optimizer-header { flex-direction: column; align-items: flex-start; gap: 0.2rem; }
}
</style>
