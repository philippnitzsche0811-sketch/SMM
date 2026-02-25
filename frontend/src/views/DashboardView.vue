<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <Button 
        label="Video hochladen" 
        icon="pi pi-upload"
        class="p-button-lg"
        @click="openUploadModal"
      />
    </div>

    <div class="dashboard-content">
      <!-- Stats Cards -->
      <div class="stats-grid">
        <Card class="stat-card">
          <template #content>
            <div class="stat-content">
              <div class="stat-icon" style="background: #3b82f615;">
                <i class="pi pi-video" style="color: #3b82f6; font-size: 2rem;"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.totalVideos }}</span>
                <span class="stat-title">Gesamte Videos</span>
              </div>
            </div>
          </template>
        </Card>

        <Card class="stat-card">
          <template #content>
            <div class="stat-content">
              <div class="stat-icon" style="background: #10b98115;">
                <i class="pi pi-globe" style="color: #10b981; font-size: 2rem;"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.activePlatforms }}</span>
                <span class="stat-title">Aktive Plattformen</span>
              </div>
            </div>
          </template>
        </Card>

        <Card class="stat-card">
          <template #content>
            <div class="stat-content">
              <div class="stat-icon" style="background: #f59e0b15;">
                <i class="pi pi-eye" style="color: #f59e0b; font-size: 2rem;"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ formatNumber(stats.totalViews) }}</span>
                <span class="stat-title">Gesamte Aufrufe</span>
              </div>
            </div>
          </template>
        </Card>

        <Card class="stat-card">
          <template #content>
            <div class="stat-content">
              <div class="stat-icon" style="background: #8b5cf615;">
                <i class="pi pi-cloud-upload" style="color: #8b5cf6; font-size: 2rem;"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.uploadsToday }}</span>
                <span class="stat-title">Uploads heute</span>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Recent Videos -->
      <Card class="recent-videos-card">
        <template #title>
          <div class="card-header">
            <span>Neueste Videos</span>
            <Button 
              label="Alle anzeigen" 
              icon="pi pi-arrow-right" 
              iconPos="right"
              class="p-button-text p-button-sm"
              @click="goToUploads"
            />
          </div>
        </template>
        <template #content>
          <VideoList 
            :videos="recentVideos" 
            :limit="5"
            @edit="handleEdit"
            @delete="handleDelete"
          />
        </template>
      </Card>
    </div>

    <!-- Upload Modal -->
    <VideoEditModal 
      v-model="showUploadModal" 
      :video="editingVideo"
      @save="handleSave" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import Card from 'primevue/card';
import VideoList from '@/components/video/VideoList.vue';
import VideoEditModal from '@/components/video/VideoEditModal.vue';
import api, { deleteVideo as deleteVideoApi } from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const showUploadModal = ref(false);
const editingVideo = ref<any>(null);
const recentVideos = ref<any[]>([]);

// Stats berechnen
const stats = computed(() => ({
  totalVideos: recentVideos.value.length,
  activePlatforms: authStore.user?.connectedPlatforms?.length || 0,
  totalViews: recentVideos.value.reduce((sum, v) => sum + (v.views || 0), 0),
  uploadsToday: recentVideos.value.filter((v) => {
    const today = new Date().toDateString();
    return new Date(v.createdAt).toDateString() === today;
  }).length,
}));

// Helper für Zahlen formatierung
const formatNumber = (num: number): string => {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M';
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'K';
  return num.toString();
};

// Upload Modal öffnen
const openUploadModal = () => {
  editingVideo.value = null;
  showUploadModal.value = true;
};

// Edit Handler
const handleEdit = (video: any) => {
  console.log('Edit video:', video);
  editingVideo.value = { ...video };
  showUploadModal.value = true;
};

// Delete Handler (Backend + lokale Liste)
const handleDelete = async (video: any) => {
  try {
    const userId = authStore.user?.id;
    if (!userId) {
      toast.add({
        severity: 'error',
        summary: 'Fehler',
        detail: 'User nicht eingeloggt',
        life: 3000,
      });
      return;
    }

    await deleteVideoApi(video.id, userId);

    const index = recentVideos.value.findIndex((v) => v.id === video.id);
    if (index > -1) {
      recentVideos.value.splice(index, 1);
    }

    toast.add({
      severity: 'success',
      summary: 'Gelöscht',
      detail: 'Video wurde gelöscht',
      life: 3000,
    });
  } catch (error: any) {
    console.error('Delete error:', error);
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: error.message || 'Löschen fehlgeschlagen',
      life: 3000,
    });
  }
};

// Zu Uploads navigieren
const goToUploads = () => {
  router.push({ name: 'uploads' });
};

// Save Handler
const handleSave = async (videoData: any, file?: File) => {
  try {
    const userId = authStore.user?.id;

    if (!userId) {
      toast.add({
        severity: 'error',
        summary: 'Fehler',
        detail: 'User nicht eingeloggt',
        life: 3000,
      });
      return;
    }

    if (editingVideo.value?.id) {
      // Update existing video
      const response = await api.patch(`/api/upload/video/${editingVideo.value.id}`, {
        user_id: userId,
        title: videoData.title,
        description: videoData.description,
        tags: videoData.tags,
        privacy_status: videoData.privacy,
      });

      const index = recentVideos.value.findIndex((v) => v.id === editingVideo.value?.id);
      if (index > -1) {
        recentVideos.value[index] = {
          ...recentVideos.value[index],
          ...videoData,
          status: response.data.status ?? recentVideos.value[index].status,
          updatedAt: new Date().toISOString(),
        };
      }

      toast.add({
        severity: 'success',
        summary: 'Aktualisiert',
        detail: 'Video wurde aktualisiert',
        life: 3000,
      });
    } else {
      // Neues Video
      if (!file) {
        toast.add({
          severity: 'error',
          summary: 'Fehler',
          detail: 'Keine Video-Datei ausgewählt',
          life: 3000,
        });
        return;
      }

      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('video', file);
      formData.append('title', videoData.title || 'Untitled');
      formData.append('description', videoData.description || '');
      formData.append('tags', videoData.tags || '');
      formData.append('privacy_status', videoData.privacy || 'private');
      formData.append('platforms', videoData.platforms?.join(',') || '');

      const response = await api.post('/api/upload/upload_video', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const result = response.data;

      const newVideo = {
        id: result.video_id,
        title: videoData.title || 'Untitled',
        description: videoData.description,
        status: result.status,
        platforms: videoData.platforms || [],
        tags: videoData.tags,
        privacy: videoData.privacy || 'public',
        createdAt: new Date().toISOString(),
        views: 0,
      };
      recentVideos.value.unshift(newVideo);

      toast.add({
        severity: 'success',
        summary: 'Upload gestartet',
        detail: `Video "${videoData.title}" wird hochgeladen`,
        life: 3000,
      });

      pollVideoStatus(result.video_id);
    }

    showUploadModal.value = false;
    editingVideo.value = null;
  } catch (error: any) {
    console.error('Save error:', error);
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: error.message || 'Aktion fehlgeschlagen',
      life: 3000,
    });
  }
};

// Status Polling
const pollVideoStatus = (videoId: string) => {
  const interval = setInterval(async () => {
    try {
      const response = await api.get(`/api/upload/video/${videoId}`);
      if (response.status !== 200) {
        clearInterval(interval);
        return;
      }

      const videoStatus = response.data;

      const index = recentVideos.value.findIndex((v) => v.id === videoId);
      if (index > -1) {
        recentVideos.value[index].status = videoStatus.status;

        if (videoStatus.status === 'uploaded') {
          toast.add({
            severity: 'success',
            summary: 'Upload abgeschlossen',
            detail: `Video "${recentVideos.value[index].title}" wurde hochgeladen`,
            life: 5000,
          });
          clearInterval(interval);
        } else if (videoStatus.status === 'failed') {
          toast.add({
            severity: 'error',
            summary: 'Upload fehlgeschlagen',
            detail: `Video "${recentVideos.value[index].title}" konnte nicht hochgeladen werden`,
            life: 5000,
          });
          clearInterval(interval);
        }
      }
    } catch (error) {
      clearInterval(interval);
    }
  }, 3000);
};

// Videos laden
onMounted(async () => {
  try {
    const userId = authStore.user?.id;
    if (!userId) return;

    const response = await api.get(`/api/upload/videos/user/${userId}`);
    if (response.status === 200) {
      const data = response.data;
      recentVideos.value = data.videos.map((v: any) => ({
        id: v.video_id,
        title: v.title,
        description: v.description,
        status: v.status,
        platforms: v.platforms,
        tags: v.tags,
        privacy: v.privacy_status,
        createdAt: v.created_at,
        views: 0,
      }));
    }
  } catch (error) {
    console.error('Failed to load videos:', error);
  }
});
</script>


<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.5rem;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.stat-title {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Recent Videos Card */
.recent-videos-card {
  margin-top: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .dashboard-header h1 {
    font-size: 1.5rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-content {
    flex-direction: column;
    text-align: center;
  }

  .stat-value {
    font-size: 1.75rem;
  }
}
</style>


