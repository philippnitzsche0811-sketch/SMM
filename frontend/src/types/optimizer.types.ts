// frontend/src/types/optimizer.types.ts

export interface PlatformSuggestion {
  title: string
  title_options?: string[]  // [hook, seo, curiosity]
  description: string
  tags: string[]
  upload_times: string[] // ISO 8601 UTC strings
}

export interface OptimizerSuggestions {
  youtube?: PlatformSuggestion
  tiktok?: PlatformSuggestion
  instagram?: PlatformSuggestion
}

export interface OptimizerResponse {
  suggestions: OptimizerSuggestions
  best_overall_time: string // ISO 8601
}

export interface OptimizeRequest {
  user_id: string
  title_draft: string
  description_draft: string
  category: string
  platforms: string[]
  video_duration?: number
}

export type OptimizerPlatform = 'youtube' | 'tiktok' | 'instagram'
