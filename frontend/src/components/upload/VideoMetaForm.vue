<template>
  <div class="video-meta-form">
    <div class="field">
      <label for="title">Title *</label>
      <InputText
        id="title"
        v-model="localTitle"
        placeholder="Enter a title..."
        :class="{ 'p-invalid': !localTitle }"
      />
    </div>

    <div class="field">
      <label for="description">Description</label>
      <Textarea
        id="description"
        v-model="localDescription"
        rows="5"
        placeholder="Describe your video..."
      />
    </div>

    <div class="field">
      <label for="tags">Tags (comma-separated)</label>
      <Chips v-model="localTags" separator="," />
    </div>

    <div class="fields-row">
      <div class="field field-half">
        <label for="category">Category</label>
        <Dropdown
          id="category"
          v-model="localCategory"
          :options="categoryOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Select category"
        />
      </div>

      <div class="field field-half">
        <label for="privacy">Visibility</label>
        <Dropdown
          id="privacy"
          v-model="localPrivacyStatus"
          :options="privacyOptions"
          optionLabel="label"
          optionValue="value"
        />
      </div>
    </div>

    <!-- AI Optimizer -->
    <div class="optimizer-trigger">
      <Button
        label="AI Suggestions"
        icon="pi pi-sparkles"
        :loading="optimizerLoading"
        :disabled="!localTitle"
        severity="secondary"
        @click="runOptimizer"
      />
      <small v-if="!localTitle" class="hint">Enter a title first</small>
      <small v-else class="hint">Get AI-powered title, description, hashtags &amp; upload times</small>
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
  'update:title':         [value: string]
  'update:description':   [value: string]
  'update:tags':          [value: string[]]
  'update:privacyStatus': [value: string]
  'update:category':      [value: string]
}>()

const localTitle         = ref(props.title)
const localDescription   = ref(props.description)
const localTags          = ref(props.tags)
const localPrivacyStatus = ref(props.privacyStatus)
const localCategory      = ref(props.category || 'default')

watch(localTitle,         (val) => emit('update:title', val))
watch(localDescription,   (val) => emit('update:description', val))
watch(localTags,          (val) => emit('update:tags', val))
watch(localPrivacyStatus, (val) => emit('update:privacyStatus', val))
watch(localCategory,      (val) => emit('update:category', val))

const privacyOptions = [
  { label: 'Private',  value: 'private'  },
  { label: 'Public',   value: 'public'   },
  { label: 'Unlisted', value: 'unlisted' },
]

const categoryOptions = [
  { label: 'General',       value: 'default'       },
  { label: 'Gaming',        value: 'gaming'        },
  { label: 'Education',     value: 'education'     },
  { label: 'Music',         value: 'music'         },
  { label: 'Entertainment', value: 'entertainment' },
  { label: 'Lifestyle',     value: 'lifestyle'     },
  { label: 'Technology',    value: 'tech'          },
  { label: 'Sports',        value: 'sports'        },
  { label: 'Food',          value: 'food'          },
]

const authStore       = useAuthStore()
const optimizerLoading = ref(false)
const optimizerResult  = ref<OptimizerResponse | null>(null)
const optimizerError   = ref('')

const runOptimizer = async () => {
  const userId = authStore.user?.id
  if (!userId || !localTitle.value) return

  optimizerLoading.value = true
  optimizerError.value   = ''
  optimizerResult.value  = null

  try {
    optimizerResult.value = await optimizeSuggest({
      user_id:          userId,
      title_draft:      localTitle.value,
      description_draft: localDescription.value,
      category:         localCategory.value,
      platforms:        ['youtube', 'tiktok', 'instagram'],
    })
  } catch {
    optimizerError.value = 'AI optimization failed. Please try again.'
  } finally {
    optimizerLoading.value = false
  }
}

const applyTitle       = (title: string)  => { localTitle.value       = title }
const applyDescription = (desc: string)   => { localDescription.value = desc  }
const applyTags        = (tags: string[]) => { localTags.value        = tags  }
</script>

<style scoped>
.field {
  margin-bottom: 1.375rem;
}

label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--text-primary);
}

.fields-row {
  display: flex;
  gap: 1rem;
}

.field-half { flex: 1; }

.optimizer-trigger {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  margin-top: 0.25rem;
  margin-bottom: 0.25rem;
  padding: 0.875rem;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.hint {
  color: var(--text-secondary);
  font-size: 0.8125rem;
}

.mt-2 { margin-top: 0.75rem; }

@media (max-width: 600px) {
  .fields-row { flex-direction: column; }
}
</style>
