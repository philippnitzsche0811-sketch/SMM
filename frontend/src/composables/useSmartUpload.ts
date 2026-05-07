import { ref } from 'vue';
import { startSmartAnalysis, getSmartAnalysis, scheduleSmartUpload } from '@/services/api';
import type { VideoAnalysis } from '@/types/analysis.types';

export function useSmartUpload() {
  const videoId = ref<string | null>(null);
  const isUploading = ref(false);
  const uploadProgress = ref(0);
  const analysis = ref<VideoAnalysis | null>(null);
  const isAnalyzing = ref(false);
  const isScheduling = ref(false);
  const error = ref<string | null>(null);

  let pollInterval: ReturnType<typeof setInterval> | null = null;

  async function submitForAnalysis(file: File, userId: string, title: string) {
    isUploading.value = true;
    uploadProgress.value = 0;
    error.value = null;

    const formData = new FormData();
    formData.append('video', file);
    formData.append('user_id', userId);
    formData.append('title', title);

    try {
      const result = await startSmartAnalysis(formData, (pct) => {
        uploadProgress.value = pct;
      });
      videoId.value = result.video_id;
      isUploading.value = false;
      isAnalyzing.value = true;
      startPolling(result.video_id);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Upload failed';
      isUploading.value = false;
    }
  }

  function startPolling(vid: string) {
    pollInterval = setInterval(async () => {
      try {
        const data = await getSmartAnalysis(vid);
        analysis.value = data;
        if (data.status === 'done' || data.status === 'failed') {
          stopPolling();
          isAnalyzing.value = false;
        }
      } catch {
        // keep polling
      }
    }, 3000);
  }

  function stopPolling() {
    if (pollInterval !== null) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }

  async function schedule(userId: string, options: {
    platforms: string[];
    privacy_status: string;
    schedule_type: string;
    scheduled_at?: string;
    group_id?: string;
  }) {
    if (!videoId.value) return;
    isScheduling.value = true;
    error.value = null;
    try {
      const result = await scheduleSmartUpload(videoId.value, {
        user_id: userId,
        ...options,
      });
      return result;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Scheduling failed';
      throw err;
    } finally {
      isScheduling.value = false;
    }
  }

  function reset() {
    stopPolling();
    videoId.value = null;
    analysis.value = null;
    isUploading.value = false;
    isAnalyzing.value = false;
    isScheduling.value = false;
    uploadProgress.value = 0;
    error.value = null;
  }

  return {
    videoId,
    isUploading,
    uploadProgress,
    analysis,
    isAnalyzing,
    isScheduling,
    error,
    submitForAnalysis,
    schedule,
    reset,
  };
}
