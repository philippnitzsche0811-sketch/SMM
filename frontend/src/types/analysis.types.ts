export interface VideoAnalysis {
  video_id: string;
  status: 'pending' | 'processing' | 'done' | 'failed';
  frames_extracted: number;
  result: AnalysisResult | null;
}

export interface AnalysisResult {
  overall_score: number;
  summary: string;
  pacing_suggestions: string[];
  content_quality: string[];
  cut_suggestions: string[];
  sound_recommendations: string[];
}
