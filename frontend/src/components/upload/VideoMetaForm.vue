<template>
  <div class="video-meta-form">
    <h3>Video-Details</h3>

    <div class="field">
      <label for="title">Titel *</label>
      <InputText
        id="title"
        v-model="localTitle"
        placeholder="Gib einen Titel ein..."
        :class="{ 'p-invalid': !localTitle }"
      />
    </div>

    <div class="field">
      <label for="description">Beschreibung</label>
      <Textarea
        id="description"
        v-model="localDescription"
        rows="5"
        placeholder="Beschreibe dein Video..."
      />
    </div>

    <div class="field">
      <label for="tags">Tags (komma-getrennt)</label>
      <Chips v-model="localTags" separator="," />
    </div>

    <div class="fields-row">
      <div class="field field-half">
        <label for="category">Kategorie</label>
        <Dropdown
          id="category"
          v-model="localCategory"
          :options="categoryOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Kategorie wählen"
        />
      </div>

      <div class="field field-half">
        <label for="privacy">Sichtbarkeit</label>
        <Dropdown
          id="privacy"
          v-model="localPrivacyStatus"
          :options="privacyOptions"
          optionLabel="label"
          optionValue="value"
        />
      </div>
    </div>

    <!-- Optimizer trigger -->
    <div class="optimizer-trigger">
      <Button
        label="KI-Optimierung"
        icon="pi pi-sparkles"
        :loading="optimizerLoading"
        :disabled="!localTitle"
        severity="secondary"
        @click="runOptimizer"
      />
      <small v-if="!localTitle" class="hint">Bitte zuerst einen Titel eingeben</small>
      <small v-else class="hint">Vorschläge für Titel, Beschreibung, Hashtags und Upload-Zeiten</small>
    </div>

    <Message v-if="optimizerError" severity="error" :closable="true" class="mt-2" @close="optimizerError = ''">
      {{ optimizerError }}
    </Message>

    <OptimizerPanel
      v-if="optimizerResult"
      :suggestions="optimizerResult.suggestions"
      @apply-title="applyTitle"
      @apply-description="applyDescription"
      @apply-tags="applyTags"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Chips from 'primevue/chips'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import Message from 'primevue/message'
import OptimizerPanel from './OptimizerPanel.vue'
import { useAuthStore } from '@/stores/authStore'
import { optimizeSuggest } from '@/services/api'
import type { OptimizerResponse } from '@/types/optimizer.types'

const props = defineProps<{
  title: string
  description: string
  tags: string[]
  privacyStatus: string
  category: string
}>()

const emit = defineEmits<{
  'update:title': [value: string]
  'update:description': [value: string]
  'update:tags': [value: string[]]
  'update:privacyStatus': [value: string]
  'update:category': [value: string]
}>()

const localTitle = ref(props.title)
const localDescription = ref(props.description)
const localTags = ref(props.tags)
const localPrivacyStatus = ref(props.privacyStatus)
const localCategory = ref(props.category || 'default')

watch(localTitle, (val) => emit('update:title', val))
watch(localDescription, (val) => emit('update:description', val))
watch(localTags, (val) => emit('update:tags', val))
watch(localPrivacyStatus, (val) => emit('update:privacyStatus', val))
watch(localCategory, (val) => emit('update:category', val))

const privacyOptions = [
  { label: 'Privat', value: 'private' },
  { label: 'Öffentlich', value: 'public' },
  { label: 'Nicht gelistet', value: 'unlisted' },
]

const categoryOptions = [
  { label: 'Standard', value: 'default' },
  { label: 'Gaming', value: 'gaming' },
  { label: 'Bildung', value: 'education' },
  { label: 'Musik', value: 'music' },
  { label: 'Entertainment', value: 'entertainment' },
  { label: 'Lifestyle', value: 'lifestyle' },
  { label: 'Technologie', value: 'tech' },
  { label: 'Sport', value: 'sports' },
  { label: 'Essen', value: 'food' },
]

// Optimizer state
const authStore = useAuthStore()
const optimizerLoading = ref(false)
const optimizerResult = ref<OptimizerResponse | null>(null)
const optimizerError = ref('')

const runOptimizer = async () => {
  const userId = authStore.user?.id
  if (!userId || !localTitle.value) return

  optimizerLoading.value = true
  optimizerError.value = ''
  optimizerResult.value = null

  try {
    optimizerResult.value = await optimizeSuggest({
      user_id: userId,
      title_draft: localTitle.value,
      description_draft: localDescription.value,
      category: localCategory.value,
      platforms: ['youtube', 'tiktok', 'instagram'],
    })
  } catch {
    optimizerError.value = 'KI-Optimierung fehlgeschlagen. Bitte erneut versuchen.'
  } finally {
    optimizerLoading.value = false
  }
}

const applyTitle = (title: string) => {
  localTitle.value = title
}

const applyDescription = (desc: string) => {
  localDescription.value = desc
}

const applyTags = (tags: string[]) => {
  localTags.value = tags
}
</script>

<style scoped>
.field {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.fields-row {
  display: flex;
  gap: 1rem;
}

.field-half {
  flex: 1;
}

.optimizer-trigger {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.hint {
  color: var(--text-secondary, #64748b);
  font-size: 0.82rem;
}

.mt-2 {
  margin-top: 0.75rem;
}

@media (max-width: 600px) {
  .fields-row {
    flex-direction: column;
  }
}
</style>
