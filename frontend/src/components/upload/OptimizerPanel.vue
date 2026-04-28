<template>
  <div class="optimizer-panel">
    <div class="optimizer-header">
      <span class="optimizer-title">KI-Vorschläge</span>
      <small class="optimizer-hint">Klicke "Übernehmen" um einen Vorschlag in das Formular zu übertragen</small>
    </div>

    <div class="platform-cards">
      <div
        v-for="(suggestion, platform) in suggestions"
        :key="platform"
        class="platform-card"
      >
        <!-- Platform Header -->
        <div class="platform-header">
          <span class="platform-badge" :class="`badge-${platform}`">
            {{ platformLabel(platform as string) }}
          </span>
        </div>

        <!-- Title -->
        <div class="suggestion-block">
          <div class="suggestion-label">Titel</div>
          <div class="suggestion-text">{{ suggestion.title }}</div>
          <Button
            label="Übernehmen"
            size="small"
            outlined
            class="apply-btn"
            @click="$emit('apply-title', suggestion.title)"
          />
        </div>

        <!-- Description -->
        <div class="suggestion-block">
          <div class="suggestion-label">Beschreibung</div>
          <div class="suggestion-text description-preview">{{ suggestion.description }}</div>
          <Button
            label="Übernehmen"
            size="small"
            outlined
            class="apply-btn"
            @click="$emit('apply-description', suggestion.description)"
          />
        </div>

        <!-- Hashtags -->
        <div class="suggestion-block">
          <div class="suggestion-label">Hashtags</div>
          <div class="tags-row">
            <span
              v-for="tag in suggestion.tags.slice(0, 12)"
              :key="tag"
              class="tag-chip"
            >#{{ tag }}</span>
          </div>
          <Button
            label="Übernehmen"
            size="small"
            outlined
            class="apply-btn"
            @click="$emit('apply-tags', suggestion.tags)"
          />
        </div>

        <!-- Upload times -->
        <div class="suggestion-block">
          <div class="suggestion-label">Beste Upload-Zeiten</div>
          <div class="times-list">
            <div
              v-for="time in suggestion.upload_times.slice(0, 3)"
              :key="time"
              class="time-entry"
            >
              {{ formatDateTime(time) }}
            </div>
            <div v-if="suggestion.upload_times.length === 0" class="time-entry muted">
              Keine Daten – nach mehr Uploads personalisiert
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

defineProps<{
  suggestions: OptimizerSuggestions
}>()

defineEmits<{
  'apply-title': [value: string]
  'apply-description': [value: string]
  'apply-tags': [value: string[]]
}>()

const platformLabel = (platform: string): string => {
  const labels: Record<string, string> = {
    youtube: 'YouTube',
    tiktok: 'TikTok',
    instagram: 'Instagram',
  }
  return labels[platform] ?? platform
}

const formatDateTime = (iso: string): string => {
  try {
    return new Intl.DateTimeFormat('de-DE', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}
</script>

<style scoped>
.optimizer-panel {
  margin-top: 1.5rem;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 10px;
  overflow: hidden;
}

.optimizer-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.optimizer-title {
  font-weight: 700;
  font-size: 0.95rem;
}

.optimizer-hint {
  opacity: 0.85;
  font-size: 0.78rem;
}

.platform-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0;
}

.platform-card {
  padding: 1rem;
  border-right: 1px solid var(--border-color, #e2e8f0);
}

.platform-card:last-child {
  border-right: none;
}

.platform-header {
  margin-bottom: 0.75rem;
}

.platform-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 700;
  color: white;
}

.badge-youtube  { background: #ff0000; }
.badge-tiktok   { background: #010101; }
.badge-instagram { background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); }

.suggestion-block {
  margin-bottom: 0.9rem;
  padding-bottom: 0.9rem;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.suggestion-block:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.suggestion-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary, #64748b);
  margin-bottom: 0.3rem;
}

.suggestion-text {
  font-size: 0.88rem;
  line-height: 1.4;
  color: var(--text-primary, #1e293b);
  margin-bottom: 0.4rem;
}

.description-preview {
  max-height: 3.5rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.apply-btn {
  font-size: 0.78rem !important;
  padding: 0.2rem 0.6rem !important;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-bottom: 0.4rem;
}

.tag-chip {
  background: #f1f5f9;
  color: #475569;
  border-radius: 4px;
  padding: 0.15rem 0.4rem;
  font-size: 0.75rem;
}

.times-list {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.time-entry {
  font-size: 0.85rem;
  color: var(--text-primary, #1e293b);
  padding: 0.2rem 0.4rem;
  background: #f8fafc;
  border-radius: 4px;
}

.time-entry.muted {
  color: var(--text-secondary, #94a3b8);
  font-style: italic;
}

@media (max-width: 640px) {
  .platform-cards {
    grid-template-columns: 1fr;
  }
  .platform-card {
    border-right: none;
    border-bottom: 1px solid var(--border-color, #e2e8f0);
  }
  .platform-card:last-child {
    border-bottom: none;
  }
  .optimizer-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
