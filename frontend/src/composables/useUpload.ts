import { ref } from 'vue';
import axios from 'axios';
import { useToast } from 'primevue/usetoast';
import type { VideoMetadata, VideoUploadResponse, UploadResult } from '@/types/video.types';

export function useUpload() {
  const toast = useToast();
  const isUploading = ref(false);
  const uploadProgress = ref(0);
  const uploadResults = ref<UploadResult[]>([]);

  const uploadVideo = async (
    file: File,
    metadata: VideoMetadata,
    platforms: string[]
  ): Promise<VideoUploadResponse | null> => {
    isUploading.value = true;
    uploadProgress.value = 0;
    uploadResults.value = [];

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', metadata.title);
      
      if (metadata.description) {
        formData.append('description', metadata.description);
      }
      
      if (metadata.tags && metadata.tags.length > 0) {
        formData.append('tags', metadata.tags.join(','));
      }
      
      if (metadata.privacyStatus) {
        formData.append('privacy', metadata.privacyStatus);
      }
      
      if (metadata.category) {
        formData.append('category', metadata.category);
      }
      
      formData.append('platforms', JSON.stringify(platforms));

      const response = await axios.post<VideoUploadResponse>('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            uploadProgress.value = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
          }
        },
      });

      if (response.data.results) {
        uploadResults.value = response.data.results;
      }

      toast.add({
        severity: 'success',
        summary: 'Upload erfolgreich',
        detail: response.data.message || 'Dein Video wurde hochgeladen',
        life: 3000,
      });

      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Upload fehlgeschlagen';
      
      toast.add({
        severity: 'error',
        summary: 'Upload fehlgeschlagen',
        detail: errorMessage,
        life: 5000,
      });
      
      return null;
    } finally {
      isUploading.value = false;
      uploadProgress.value = 0;
    }
  };

  const resetUpload = () => {
    isUploading.value = false;
    uploadProgress.value = 0;
    uploadResults.value = [];
  };

  return {
    isUploading,
    uploadProgress,
    uploadResults,
    uploadVideo,
    resetUpload,
  };
}


