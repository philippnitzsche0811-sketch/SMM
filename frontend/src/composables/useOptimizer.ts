// frontend/src/composables/useOptimizer.ts

import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import api from '@/services/api'
import type {
  OptimizerResponse,
  OptimizeRequest,
  PlatformSuggestion,
  OptimizerPlatform,
} from '@/types/optimizer.types'

export function useOptimizer() {
  const authStore = useAuthStore()

  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const suggestions = ref<OptimizerResponse | null>(null)
  const selectedPlatform = ref<OptimizerPlatform>('youtube')

  const currentSuggestion = computed((): PlatformSuggestion | null => {
    if (!suggestions.value) return null
    return suggestions.value.suggestions[selectedPlatform.value] ?? null
  })

  const hasSuggestions = computed(() => suggestions.value !== null)

  async function optimize(params: {
    titleDraft: string
    descriptionDraft: string
    category: string
    platforms: string[]
    videoDuration?: number
  }): Promise<OptimizerResponse | null> {
    if (!authStore.userId) {
      error.value = 'Nicht authentifiziert.'
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const request: OptimizeRequest = {
        user_id: authStore.userId,
        title_draft: params.titleDraft,
        description_draft: params.descriptionDraft,
        category: params.category,
        platforms: params.platforms,
        video_duration: params.videoDuration,
      }

      const { data } = await api.post<OptimizerResponse>('/api/optimizer/suggest', request)
      suggestions.value = data

      // Auto-select first available platform
      const availablePlatforms = Object.keys(data.suggestions) as OptimizerPlatform[]
      if (availablePlatforms.length > 0) {
        selectedPlatform.value = availablePlatforms[0]
      }

      return data
    } catch (err: any) {
      error.value = err?.response?.data?.detail ?? 'Optimierung fehlgeschlagen. Bitte erneut versuchen.'
      return null
    } finally {
      isLoading.value = false
    }
  }

  function applySuggestion(
    onApply: (title: string, description: string, tags: string[]) => void,
    platform?: OptimizerPlatform,
  ) {
    const target = platform ?? selectedPlatform.value
    const suggestion = suggestions.value?.suggestions[target]
    if (!suggestion) return
    onApply(suggestion.title, suggestion.description, suggestion.tags)
  }

  function reset() {
    suggestions.value = null
    error.value = null
    isLoading.value = false
  }

  return {
    isLoading,
    error,
    suggestions,
    selectedPlatform,
    currentSuggestion,
    hasSuggestions,
    optimize,
    applySuggestion,
    reset,
  }
}
