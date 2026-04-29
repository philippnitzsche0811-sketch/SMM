import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useAuthStore } from '@/stores/authStore';
import api from '@/services/api';
import type { VideoMetadata, VideoUploadResponse, UploadResult } from '@/types/video.types';

export function useUpload() {
  const toast     = useToast();
  const authStore = useAuthStore();

  const isUploading   = ref(false);
  const uploadProgress = ref(0);
  const uploadResults  = ref<UploadResult[]>([]);

  const uploadVideo = async (
    file: File,
    metadata: VideoMetadata,
    platforms: string[]
  ): Promise<VideoUploadResponse | null> => {
    const userId = authStore.user?.id;
    if (!userId) {
      toast.add({ severity: 'error', summary: 'Error', detail: 'Not logged in', life: 4000 });
      return null;
    }

    isUploading.value   = true;
    uploadProgress.value = 0;
    uploadResults.value  = [];

    try {
      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('video', file);
      formData.append('title', metadata.title);
      if (metadata.description) formData.append('description', metadata.description);
      if (metadata.tags?.length)  formData.append('tags', metadata.tags.join(','));
      if (metadata.privacyStatus) formData.append('privacy_status', metadata.privacyStatus);
      formData.append('platforms', platforms.join(','));

      const response = await api.post<VideoUploadResponse>('/api/upload/upload_video', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) uploadProgress.value = Math.round((e.loaded * 100) / e.total);
        },
      });

      if (response.data.results) uploadResults.value = response.data.results;

      toast.add({ severity: 'success', summary: 'Upload started', detail: `"${metadata.title}" is being uploaded`, life: 4000 });
      return response.data;
    } catch (error: any) {
      toast.add({ severity: 'error', summary: 'Upload failed', detail: error.response?.data?.detail || 'Upload failed', life: 5000 });
      return null;
    } finally {
      isUploading.value   = false;
      uploadProgress.value = 0;
    }
  };

  const resetUpload = () => {
    isUploading.value   = false;
    uploadProgress.value = 0;
    uploadResults.value  = [];
  };

  return {
    isUploading,
    uploadProgress,
    uploadResults,
    uploadVideo,
    resetUpload,
  };
}


