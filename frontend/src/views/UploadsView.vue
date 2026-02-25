<template>
  <div class="uploads-view">
    <div class="uploads-header">
      <h2>Meine Videos</h2>
      <Button label="+ Neues Video" icon="pi pi-plus" @click="openNewVideoDialog" />
    </div>

    <Card>
      <template #content>
        <VideoList 
          :videos="videos" 
          @edit="handleEdit" 
          @delete="handleDelete" 
        />
      </template>
    </Card>

    <!-- Upload/Edit Modal -->
    <VideoEditModal 
      v-model="showUploadDialog" 
      :video="editingVideo"
      @save="handleSave" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';
import VideoList from '@/components/video/VideoList.vue';
import VideoEditModal from '@/components/video/VideoEditModal.vue';
import type { Video } from '@/types/video.types';
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();
const toast = useToast();

const videos = ref<Video[]>([]);
const showUploadDialog = ref(false);
const editingVideo = ref<Video | null>(null);

const openNewVideoDialog = () => {
  editingVideo.value = null;
  showUploadDialog.value = true;
};

// ✅ handleEdit öffnet Modal mit Video-Daten
const handleEdit = (video: Video) => {
  console.log('Edit video:', video);
  editingVideo.value = { ...video };  // ✅ Video-Daten laden
  showUploadDialog.value = true;       // ✅ Modal öffnen
};

const handleDelete = async (video: Video) => {
  // Delete wird von VideoList handled
  const index = videos.value.findIndex(v => v.id === video.id);
  if (index > -1) {
    videos.value.splice(index, 1);
  }
};

const handleSave = async (videoData: Partial<Video>, file?: File) => {
  try {
    if (editingVideo.value?.id) {
      // ✅ Update existing video
      const userId = authStore.user?.id;
      
      if (!userId) {
        toast.add({
          severity: 'error',
          summary: 'Fehler',
          detail: 'User nicht eingeloggt',
          life: 3000
        });
        return;
      }

      const response = await fetch(`/upload/video/${editingVideo.value.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          title: videoData.title,
          description: videoData.description,
          tags: videoData.tags,
          privacy_status: videoData.privacy
        })
      });

      if (!response.ok) {
        throw new Error('Update fehlgeschlagen');
      }

      const result = await response.json();

      // Update in Liste
      const index = videos.value.findIndex(v => v.id === editingVideo.value?.id);
      if (index > -1) {
        videos.value[index] = { 
          ...videos.value[index], 
          ...videoData,
          updatedAt: new Date().toISOString()
        };
      }

      toast.add({
        severity: 'success',
        summary: 'Aktualisiert',
        detail: 'Video wurde aktualisiert',
        life: 3000
      });

    } else {
      // ✅ Create new video WITH file upload
      if (!file) {
        toast.add({
          severity: 'error',
          summary: 'Fehler',
          detail: 'Keine Video-Datei ausgewählt',
          life: 3000
        });
        return;
      }

      const formData = new FormData();
      formData.append('user_id', authStore.user?.id || 'unknown');
      formData.append('video', file);
      formData.append('title', videoData.title || 'Untitled');
      formData.append('description', videoData.description || '');
      formData.append('tags', videoData.tags || '');
      formData.append('privacy_status', videoData.privacy || 'private');
      formData.append('platforms', videoData.platforms?.join(',') || '');

      const response = await fetch('/api/upload/upload_video', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload fehlgeschlagen');
      }

      const result = await response.json();
      
      const newVideo: Video = {
        id: result.video_id,
        title: videoData.title || 'Untitled',
        description: videoData.description,
        platforms: videoData.platforms || [],
        tags: videoData.tags,
        category: videoData.category,
        privacy: videoData.privacy || 'public',
        status: result.status,
        createdAt: new Date().toISOString(),
        views: 0
      };
      videos.value.unshift(newVideo);

      pollVideoStatus(result.video_id);

      toast.add({
        severity: 'success',
        summary: 'Upload gestartet',
        detail: `Video "${videoData.title}" wird hochgeladen`,
        life: 3000
      });
    }
    
    // Reset
    editingVideo.value = null;
    showUploadDialog.value = false;
    
  } catch (error) {
    console.error('Save error:', error);
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Aktion fehlgeschlagen',
      life: 3000
    });
  }
};

const pollVideoStatus = (videoId: string) => {
  const interval = setInterval(async () => {
    try {
      const response = await fetch(`/upload/video/${videoId}`);
      if (!response.ok) {
        clearInterval(interval);
        return;
      }

      const videoStatus = await response.json();
      
      const index = videos.value.findIndex(v => v.id === videoId);
      if (index > -1) {
        videos.value[index].status = videoStatus.status;
        
        if (videoStatus.status === 'uploaded' || videoStatus.status === 'failed') {
          clearInterval(interval);
        }
      }
      
    } catch (error) {
      console.error('Status polling error:', error);
      clearInterval(interval);
    }
  }, 3000);
};

onMounted(async () => {
  try {
    const userId = authStore.user?.id;
    if (!userId) return;

    const response = await fetch(`/api/videos/user/${userId}`);
    if (response.ok) {
      const data = await response.json();
      videos.value = data.videos.map((v: any) => ({
        id: v.video_id,
        title: v.title,
        description: v.description,
        status: v.status,
        platforms: v.platforms,
        tags: v.tags,
        privacy: v.privacy_status,
        createdAt: v.created_at,
        views: 0
      }));
    }
  } catch (error) {
    console.error('Failed to load videos:', error);
  }
});
</script>

<style scoped>
.uploads-view {
  max-width: 1400px;
  margin: 0 auto;
}

.uploads-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.uploads-header h2 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
}
</style>
