<!-- frontend/src/components/upload/OptimizerPanel.vue -->

<script setup lang="ts">
import { computed } from 'vue'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import ProgressSpinner from 'primevue/progressspinner'
import Message from 'primevue/message'
import { useOptimizer } from '@/composables/useOptimizer'
import type { OptimizerPlatform } from '@/types/optimizer.types'

// ─── Props ───────────────────────────────────────────────────────────────────

const props = defineProps<{
  titleDraft: string
  descriptionDraft: string
  category: string
  platforms: string[]
  videoDuration?: number
}>()

// ─── Emits ───────────────────────────────────────────────────────────────────

const emit = defineEmits<{
  (e: 'apply', payload: { title: string; description: string; tags: string[] }): void
  (e: 'apply-time', isoTime: string): void
}>()

// ─── Optimizer Composable ────────────────────────────────────────────────────

const { isLoading, error, suggestions, selectedPlatform, currentSuggestion, hasSuggestions, optimize, reset } =
  useOptimizer()

// ─── Computed ────────────────────────────────────────────────────────────────

const availablePlatforms = computed(() => {
  if (!suggestions.value) return []
  return Object.keys(suggestions.value.suggestions) as OptimizerPlatform[]
})

const platformLabel: Record<string, string> = {
  youtube: 'YouTube',
  tiktok: 'TikTok',
  instagram: 'Instagram',
}

const platformIcon: Record<string, string> = {
  youtube: 'pi pi-youtube',
  tiktok: 'pi pi-mobile',
  instagram: 'pi pi-camera',
}

const bestTime = computed(() => {
  if (!suggestions.value?.best_overall_time) return null
  return new Date(suggestions.value.best_overall_time).toLocaleString('de-DE', {
    weekday: 'long',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Europe/Berlin',
  })
})

const platformUploadTimes = computed(() => {
  if (!currentSuggestion.value) return []
  return currentSuggestion.value.upload_times.map((iso) =>
    new Date(iso).toLocaleString('de-DE', {
      weekday: 'short',
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Europe/Berlin',
    }),
  )
})

// ─── Handlers ────────────────────────────────────────────────────────────────

async function runOptimizer() {
  await optimize({
    titleDraft: props.titleDraft,
    descriptionDraft: props.descriptionDraft,
    category: props.category,
    platforms: props.platforms,
    videoDuration: props.videoDuration,
  })
}

function applyAll() {
  if (!currentSuggestion.value) return
  emit('apply', {
    title: currentSuggestion.value.title,
    description: currentSuggestion.value.description,
    tags: currentSuggestion.value.tags,
  })
}

function applyBestTime() {
  if (suggestions.value?.best_overall_time) {
    emit('apply-time', suggestions.value.best_overall_time)
  }
}
</script>

<template>
  <div class="optimizer-panel">
    <!-- Trigger Button -->
    <div v-if="!hasSuggestions && !isLoading" class="optimizer-trigger">
      <Button
        label="✨ KI-Optimierung starten"
        icon="pi pi-bolt"
        severity="secondary"
        outlined
        :disabled="platforms.length === 0"
        @click="runOptimizer"
        class="optimizer-btn"
      />
      <span class="optimizer-hint">
        Titel, Beschreibung & Hashtags werden plattformspezifisch optimiert
      </span>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="optimizer-loading">
      <ProgressSpinner style="width: 32px; height: 32px" stroke-width="4" />
      <span>KI analysiert deinen Content…</span>
    </div>

    <!-- Error State -->
    <Message v-if="error" severity="error" :closable="true" @close="reset">
      {{ error }}
    </Message>

    <!-- Results -->
    <div v-if="hasSuggestions && !isLoading" class="optimizer-results">
      <div class="optimizer-results-header">
        <span class="optimizer-results-title">✨ Optimierungsvorschläge</span>
        <Button
          label="Neu generieren"
          icon="pi pi-refresh"
          size="small"
          text
          @click="runOptimizer"
        />
      </div>

      <!-- Best Overall Time Banner -->
      <div v-if="bestTime" class="best-time-banner">
        <i class="pi pi-clock" />
        <span>Bester Upload-Zeitpunkt: <strong>{{ bestTime }}</strong></span>
        <Button label="Übernehmen" size="small" text @click="applyBestTime" />
      </div>

      <!-- Platform Tabs -->
      <TabView v-model:activeIndex="selectedPlatformIndex">
        <TabPanel
          v-for="platform in availablePlatforms"
          :key="platform"
          :header="platformLabel[platform] ?? platform"
        >
          <div class="suggestion-content">
            <!-- Title -->
            <div class="suggestion-section">
              <label class="suggestion-label">Titel</label>
              <div class="suggestion-value">{{ suggestions!.suggestions[platform]!.title }}</div>
            </div>

            <!-- Description -->
            <div class="suggestion-section">
              <label class="suggestion-label">Beschreibung</label>
              <div class="suggestion-value description">
                {{ suggestions!.suggestions[platform]!.description }}
              </div>
            </div>

            <!-- Tags -->
            <div class="suggestion-section">
              <label class="suggestion-label">Hashtags</label>
              <div class="tags-list">
                <Tag
                  v-for="tag in suggestions!.suggestions[platform]!.tags"
                  :key="tag"
                  :value="'#' + tag"
                  severity="secondary"
                  class="tag-chip"
                />
              </div>
            </div>

            <!-- Upload Times -->
            <div class="suggestion-section">
              <label class="suggestion-label">Beste Upload-Zeiten (nächste 7 Tage)</label>
              <div class="times-list">
                <Tag
                  v-for="(time, idx) in suggestions!.suggestions[platform]!.upload_times.map(
                    (iso) =>
                      new Date(iso).toLocaleString('de-DE', {
                        weekday: 'short',
                        day: '2-digit',
                        month: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        timeZone: 'Europe/Berlin',
                      }),
                  )"
                  :key="idx"
                  :value="time"
                  severity="info"
                  icon="pi pi-clock"
                  class="time-chip"
                />
              </div>
            </div>

            <!-- Apply Button -->
            <Button
              label="Alle Vorschläge übernehmen"
              icon="pi pi-check"
              class="apply-btn"
              @click="applyAll"
            />
          </div>
        </TabPanel>
      </TabView>
    </div>
  </div>
</template>



<style scoped>
.optimizer-panel {
  margin-top: 1rem;
  border-top: 1px solid var(--surface-border);
  padding-top: 1rem;
}

.optimizer-trigger {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.optimizer-btn {
  white-space: nowrap;
}

.optimizer-hint {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
}

.optimizer-loading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.optimizer-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.optimizer-results-title {
  font-weight: 600;
  font-size: 0.95rem;
}

.best-time-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--surface-section);
  border: 1px solid var(--primary-color);
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  flex-wrap: wrap;
}

.best-time-banner i {
  color: var(--primary-color);
}

.suggestion-section {
  margin-bottom: 0.875rem;
}

.suggestion-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-color-secondary);
  letter-spacing: 0.05em;
  margin-bottom: 0.35rem;
}

.suggestion-value {
  background: var(--surface-ground);
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  font-size: 0.9rem;
  line-height: 1.5;
}

.suggestion-value.description {
  white-space: pre-wrap;
  max-height: 120px;
  overflow-y: auto;
  font-size: 0.85rem;
}

.tags-list,
.times-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.tag-chip,
.time-chip {
  font-size: 0.78rem;
}

.apply-btn {
  width: 100%;
  margin-top: 0.25rem;
}
</style>
