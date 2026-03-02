<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1>Meine Videos</h1>
        <p class="subtitle">{{ videos.length }} Video{{ videos.length !== 1 ? 's' : '' }} gesamt</p>
      </div>
      <Button
        label="Video hochladen"
        icon="pi pi-upload"
        @click="openUploadDialog"
      />
    </div>

    <!-- Stats Row -->
    <div class="stats-row">
      <div class="stat-card">
        <i class="pi pi-video stat-icon" style="color:#6366f1"></i>
        <div>
          <div class="stat-value">{{ videos.length }}</div>
          <div class="stat-label">Videos</div>
        </div>
      </div>
      <div class="stat-card">
        <i class="pi pi-share-alt stat-icon" style="color:#10b981"></i>
        <div>
          <div class="stat-value">{{ connectedCount }}</div>
          <div class="stat-label">Plattformen</div>
        </div>
      </div>
      <div class="stat-card">
        <i class="pi pi-check-circle stat-icon" style="color:#3b82f6"></i>
        <div>
          <div class="stat-value">{{ uploadedCount }}</div>
          <div class="stat-label">Hochgeladen</div>
        </div>
      </div>
      <div class="stat-card">
        <i class="pi pi-clock stat-icon" style="color:#f59e0b"></i>
        <div>
          <div class="stat-value">{{ processingCount }}</div>
          <div class="stat-label">In Bearbeitung</div>
        </div>
      </div>
    </div>

    <!-- Video Table -->
    <div class="videos-card">
      <div class="videos-card-header">
        <span class="videos-title">Video-Bibliothek</span>
        <InputText v-model="searchQuery" placeholder="Suchen..." class="search-input" />
      </div>

      <div v-if="loading" class="loading-state">
        <ProgressSpinner />
      </div>

      <div v-else-if="filteredVideos.length === 0" class="empty-state">
        <i class="pi pi-video empty-icon"></i>
        <p>Noch keine Videos vorhanden</p>
        <Button label="Erstes Video hochladen" icon="pi pi-upload" @click="openUploadDialog" class="p-button-outlined" />
      </div>

      <DataTable
        v-else
        :value="filteredVideos"
        :rows="10"
        :paginator="filteredVideos.length > 10"
        stripedRows
        class="video-table"
      >
        <Column field="title" header="Titel" sortable>
          <template #body="{ data }">
            <div class="video-title-cell">
              <div class="video-thumb">
                <i class="pi pi-video"></i>
              </div>
              <div>
                <div class="video-name">{{ data.title }}</div>
                <div class="video-date">{{ formatDate(data.createdAt) }}</div>
              </div>
            </div>
          </template>
        </Column>

        <Column field="platforms" header="Plattformen">
          <template #body="{ data }">
            <div class="platform-badges">
              <span
                v-for="p in data.platforms"
                :key="p"
                class="platform-badge"
                :class="p"
              >
                <i :class="platformIcon(p)"></i>
                {{ p }}
              </span>
            </div>
          </template>
        </Column>

        <Column field="status" header="Status" sortable>
          <template #body="{ data }">
            <Tag
              :value="statusLabel(data.status)"
              :severity="statusSeverity(data.status)"
            />
          </template>
        </Column>

        <Column field="privacy" header="Sichtbarkeit">
          <template #body="{ data }">
            <span class="privacy-badge">
              <i :class="data.privacy === 'public' ? 'pi pi-globe' : 'pi pi-lock'"></i>
              {{ data.privacy === 'public' ? 'Öffentlich' : data.privacy === 'unlisted' ? 'Nicht gelistet' : 'Privat' }}
            </span>
          </template>
        </Column>

        <Column header="Aktionen" style="width: 120px">
          <template #body="{ data }">
            <div class="action-buttons">
              <Button
                icon="pi pi-pencil"
                class="p-button-text p-button-sm p-button-secondary"
                v-tooltip="'Bearbeiten'"
                @click="openEditDialog(data)"
              />
              <Button
                icon="pi pi-trash"
                class="p-button-text p-button-sm p-button-danger"
                v-tooltip="'Löschen'"
                @click="confirmDelete(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Upload / Edit Dialog -->
    <Dialog
      v-model:visible="showDialog"
      :header="editingVideo ? 'Video bearbeiten' : 'Video hochladen'"
      :modal="true"
      :style="{ width: '560px' }"
      :closable="!uploading"
    >
      <div class="dialog-form">
        <!-- File Drop Zone (nur bei neu) -->
        <div v-if="!editingVideo" class="file-zone" :class="{ 'has-file': selectedFile }" @click="triggerFileInput" @dragover.prevent @drop.prevent="onFileDrop">
          <input ref="fileInput" type="file" accept="video/*" style="display:none" @change="onFileChange" />
          <template v-if="selectedFile">
            <i class="pi pi-check-circle file-zone-icon" style="color:#10b981"></i>
            <span class="file-zone-name">{{ selectedFile.name }}</span>
            <span class="file-zone-size">{{ formatFileSize(selectedFile.size) }}</span>
          </template>
          <template v-else>
            <i class="pi pi-cloud-upload file-zone-icon"></i>
            <span>Video hier ablegen oder klicken</span>
            <span class="file-zone-hint">MP4, MOV, AVI, MKV bis 2 GB</span>
          </template>
        </div>

        <!-- Upload Progress -->
        <div v-if="uploading" class="upload-progress">
          <ProgressBar :value="uploadProgress" />
          <span>{{ uploadProgress }}% hochgeladen...</span>
        </div>

        <!-- Metadata -->
        <div class="form-field">
          <label>Titel *</label>
          <InputText v-model="form.title" placeholder="Titel eingeben" class="w-full" />
        </div>
        <div class="form-field">
          <label>Beschreibung</label>
          <Textarea v-model="form.description" placeholder="Beschreibung eingeben" rows="3" class="w-full" />
        </div>
        <div class="form-field">
          <label>Tags</label>
          <InputText v-model="form.tags" placeholder="tag1, tag2, tag3" class="w-full" />
        </div>
        <div class="form-field">
          <label>Sichtbarkeit</label>
          <Dropdown v-model="form.privacy" :options="privacyOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>

        <!-- Platforms (nur bei neu) -->
        <div v-if="!editingVideo" class="form-field">
          <label>Plattformen</label>
          <div class="platform-select">
            <div
              v-for="p in availablePlatforms"
              :key="p.id"
              class="platform-option"
              :class="{ selected: form.platforms.includes(p.id), disabled: !p.connected }"
              @click="p.connected && togglePlatform(p.id)"
            >
              <i :class="p.icon" :style="{ color: p.color }"></i>
              <span>{{ p.name }}</span>
              <span v-if="!p.connected" class="not-connected">Nicht verbunden</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Abbrechen" class="p-button-text" @click="closeDialog" :disabled="uploading" />
        <Button
          :label="editingVideo ? 'Speichern' : 'Hochladen'"
          icon="pi pi-upload"
          :loading="uploading"
          :disabled="!canSubmit"
          @click="handleSubmit"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation -->
    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import ProgressSpinner from 'primevue/progressspinner';
import ProgressBar from 'primevue/progressbar';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import api from '@/services/api';

const authStore = useAuthStore();
const toast = useToast();
const confirm = useConfirm();

// State
const videos = ref<any[]>([]);
const loading = ref(true);
const showDialog = ref(false);
const editingVideo = ref<any>(null);
const selectedFile = ref<File | null>(null);
const uploading = ref(false);
const uploadProgress = ref(0);
const searchQuery = ref('');
const fileInput = ref<HTMLInputElement>();

const form = ref({
  title: '',
  description: '',
  tags: '',
  privacy: 'private',
  platforms: [] as string[],
});

const privacyOptions = [
  { label: 'Privat', value: 'private' },
  { label: 'Nicht gelistet', value: 'unlisted' },
  { label: 'Öffentlich', value: 'public' },
];

// Computed
const connectedCount = computed(() => authStore.user?.connectedPlatforms?.length || 0);
const uploadedCount = computed(() => videos.value.filter(v => v.status === 'uploaded').length);
const processingCount = computed(() => videos.value.filter(v => v.status === 'processing' || v.status === 'pending').length);

const filteredVideos = computed(() => {
  if (!searchQuery.value) return videos.value;
  const q = searchQuery.value.toLowerCase();
  return videos.value.filter(v => v.title.toLowerCase().includes(q));
});

const availablePlatforms = computed(() => [
  {
    id: 'youtube',
    name: 'YouTube',
    icon: 'pi pi-youtube',
    color: '#FF0000',
    connected: authStore.user?.connectedPlatforms?.some(p => p.platform === 'youtube') || false,
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: 'pi pi-video',
    color: '#000000',
    connected: authStore.user?.connectedPlatforms?.some(p => p.platform === 'tiktok') || false,
  },
  {
    id: 'instagram',
    name: 'Instagram',
    icon: 'pi pi-instagram',
    color: '#E4405F',
    connected: authStore.user?.connectedPlatforms?.some(p => p.platform === 'instagram') || false,
  },
]);

const canSubmit = computed(() => {
  if (!form.value.title.trim()) return false;
  if (!editingVideo.value && !selectedFile.value) return false;
  return true;
});

// Methods
const platformIcon = (p: string) => {
  const map: Record<string, string> = { youtube: 'pi pi-youtube', tiktok: 'pi pi-video', instagram: 'pi pi-instagram' };
  return map[p] || 'pi pi-globe';
};

const statusLabel = (s: string) => {
  const map: Record<string, string> = { pending: 'Ausstehend', processing: 'Läuft', uploaded: 'Fertig', failed: 'Fehler' };
  return map[s] || s;
};

const statusSeverity = (s: string): "success" | "info" | "warn" | "danger" | "secondary" | "contrast" | undefined => {
  const map: Record<string, any> = { pending: 'secondary', processing: 'info', uploaded: 'success', failed: 'danger' };
  return map[s] || 'secondary';
};

const formatDate = (d: string) => {
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
};

const formatFileSize = (bytes: number) => {
  if (bytes >= 1_000_000_000) return (bytes / 1_000_000_000).toFixed(1) + ' GB';
  if (bytes >= 1_000_000) return (bytes / 1_000_000).toFixed(1) + ' MB';
  return (bytes / 1_000).toFixed(0) + ' KB';
};

const triggerFileInput = () => fileInput.value?.click();

const onFileChange = (e: Event) => {
  const f = (e.target as HTMLInputElement).files?.[0];
  if (f) selectedFile.value = f;
};

const onFileDrop = (e: DragEvent) => {
  const f = e.dataTransfer?.files?.[0];
  if (f && f.type.startsWith('video/')) selectedFile.value = f;
};

const togglePlatform = (id: string) => {
  const idx = form.value.platforms.indexOf(id);
  if (idx > -1) form.value.platforms.splice(idx, 1);
  else form.value.platforms.push(id);
};

const openUploadDialog = () => {
  editingVideo.value = null;
  selectedFile.value = null;
  form.value = { title: '', description: '', tags: '', privacy: 'private', platforms: [] };
  showDialog.value = true;
};

const openEditDialog = (video: any) => {
  editingVideo.value = video;
  form.value = {
    title: video.title || '',
    description: video.description || '',
    tags: Array.isArray(video.tags) ? video.tags.join(', ') : (video.tags || ''),
    privacy: video.privacy || 'private',
    platforms: [],
  };
  showDialog.value = true;
};

const closeDialog = () => {
  showDialog.value = false;
  editingVideo.value = null;
  selectedFile.value = null;
  uploadProgress.value = 0;
};

const handleSubmit = async () => {
  const userId = authStore.user?.id;
  if (!userId) return;

  uploading.value = true;
  try {
    if (editingVideo.value) {
      await api.patch(`/api/upload/video/${editingVideo.value.id}`, {
        user_id: userId,
        title: form.value.title,
        description: form.value.description,
        tags: form.value.tags,
        privacy_status: form.value.privacy,
      });

      const idx = videos.value.findIndex(v => v.id === editingVideo.value.id);
      if (idx > -1) {
        videos.value[idx] = {
          ...videos.value[idx],
          title: form.value.title,
          description: form.value.description,
          tags: form.value.tags.split(',').map(t => t.trim()),
          privacy: form.value.privacy,
        };
      }

      toast.add({ severity: 'success', summary: 'Gespeichert', detail: 'Video aktualisiert', life: 3000 });
    } else {
      if (!selectedFile.value) return;

      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('video', selectedFile.value);
      formData.append('title', form.value.title);
      formData.append('description', form.value.description);
      formData.append('tags', form.value.tags);
      formData.append('privacy_status', form.value.privacy);
      formData.append('platforms', form.value.platforms.join(','));

      const response = await api.post('/api/upload/upload_video', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) uploadProgress.value = Math.round((e.loaded * 100) / e.total);
        },
      });

      const result = response.data;
      videos.value.unshift({
        id: result.video_id,
        title: form.value.title,
        description: form.value.description,
        status: result.status,
        platforms: form.value.platforms,
        tags: form.value.tags.split(',').map((t: string) => t.trim()),
        privacy: form.value.privacy,
        createdAt: new Date().toISOString(),
      });

      toast.add({ severity: 'success', summary: 'Upload gestartet', detail: `"${form.value.title}" wird hochgeladen`, life: 4000 });
      pollVideoStatus(result.video_id);
    }
    closeDialog();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || err.message, life: 5000 });
  } finally {
    uploading.value = false;
  }
};

const confirmDelete = (video: any) => {
  confirm.require({
    message: `"${video.title}" wirklich löschen? Das Video wird auch von allen verbundenen Plattformen entfernt.`,
    header: 'Video löschen',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Löschen',
    rejectLabel: 'Abbrechen',
    acceptClass: 'p-button-danger',
    accept: () => deleteVideo(video),
  });
};

const deleteVideo = async (video: any) => {
  const userId = authStore.user?.id;
  if (!userId) return;
  try {
    await api.delete(`/api/upload/video/${video.id}`, { data: { user_id: userId } });
    videos.value = videos.value.filter(v => v.id !== video.id);
    toast.add({ severity: 'success', summary: 'Gelöscht', detail: `"${video.title}" wurde gelöscht`, life: 3000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || 'Löschen fehlgeschlagen', life: 5000 });
  }
};

const pollVideoStatus = (videoId: string) => {
  const interval = setInterval(async () => {
    try {
      const res = await api.get(`/api/upload/video/${videoId}`);
      const data = res.data;
      const idx = videos.value.findIndex(v => v.id === videoId);
      if (idx > -1) videos.value[idx].status = data.status;
      if (data.status === 'uploaded' || data.status === 'failed') clearInterval(interval);
    } catch {
      clearInterval(interval);
    }
  }, 3000);
};

// Load videos
onMounted(async () => {
  const userId = authStore.user?.id;
  if (!userId) return;
  try {
    const res = await api.get(`/api/upload/videos/user/${userId}`);
    videos.value = res.data.videos.map((v: any) => ({
      id: v.video_id,
      title: v.title,
      description: v.description,
      status: v.status,
      platforms: v.platforms,
      tags: v.tags,
      privacy: v.privacy_status,
      createdAt: v.created_at,
    }));
  } catch (err) {
    console.error('Failed to load videos:', err);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.dashboard { max-width: 1400px; margin: 0 auto; }

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.75rem;
}

.dashboard-header h1 { font-size: 1.75rem; font-weight: 700; color: #1e293b; margin: 0 0 0.25rem 0; }
.subtitle { color: #64748b; font-size: 0.9rem; margin: 0; }

/* Stats */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon { font-size: 1.75rem; }
.stat-value { font-size: 1.75rem; font-weight: 700; color: #1e293b; line-height: 1; }
.stat-label { font-size: 0.8125rem; color: #64748b; margin-top: 0.25rem; }

/* Videos Card */
.videos-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.videos-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.videos-title { font-size: 1rem; font-weight: 600; color: #1e293b; }
.search-input { width: 220px; }

/* Table */
.video-title-cell { display: flex; align-items: center; gap: 0.875rem; }

.video-thumb {
  width: 40px; height: 40px; border-radius: 8px;
  background: #f1f5f9; display: flex; align-items: center; justify-content: center;
  color: #94a3b8; flex-shrink: 0;
}

.video-name { font-weight: 500; color: #1e293b; font-size: 0.9rem; }
.video-date { font-size: 0.8rem; color: #94a3b8; margin-top: 0.125rem; }

.platform-badges { display: flex; gap: 0.375rem; flex-wrap: wrap; }
.platform-badge {
  display: inline-flex; align-items: center; gap: 0.25rem;
  padding: 0.2rem 0.5rem; border-radius: 4px;
  font-size: 0.75rem; font-weight: 500; text-transform: capitalize;
  background: #f1f5f9; color: #475569;
}
.platform-badge.youtube { background: #fff5f5; color: #ef4444; }
.platform-badge.tiktok { background: #f8fafc; color: #334155; }
.platform-badge.instagram { background: #fdf2f8; color: #ec4899; }

.privacy-badge { display: flex; align-items: center; gap: 0.375rem; font-size: 0.875rem; color: #64748b; }
.action-buttons { display: flex; gap: 0.25rem; }

/* Empty / Loading */
.loading-state, .empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 4rem; gap: 1rem;
}
.empty-icon { font-size: 3rem; color: #cbd5e1; }
.empty-state p { color: #94a3b8; font-size: 1rem; margin: 0; }

/* Dialog Form */
.dialog-form { display: flex; flex-direction: column; gap: 1.25rem; }

.file-zone {
  border: 2px dashed #e2e8f0; border-radius: 12px;
  padding: 2rem; text-align: center; cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
  color: #94a3b8;
}
.file-zone:hover { border-color: #6366f1; background: #f8f7ff; }
.file-zone.has-file { border-color: #10b981; background: #f0fdf4; color: #15803d; }
.file-zone-icon { font-size: 2.5rem; }
.file-zone-name { font-weight: 600; font-size: 0.9rem; }
.file-zone-size { font-size: 0.8rem; }
.file-zone-hint { font-size: 0.8rem; }

.upload-progress { display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.875rem; color: #64748b; }

.form-field { display: flex; flex-direction: column; gap: 0.375rem; }
.form-field label { font-size: 0.875rem; font-weight: 500; color: #374151; }

.platform-select { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.platform-option {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.625rem 1rem; border: 2px solid #e2e8f0;
  border-radius: 8px; cursor: pointer; transition: all 0.2s;
  font-size: 0.875rem; font-weight: 500; user-select: none;
}
.platform-option:hover:not(.disabled) { border-color: #6366f1; }
.platform-option.selected { border-color: #6366f1; background: #eef2ff; color: #4f46e5; }
.platform-option.disabled { opacity: 0.45; cursor: not-allowed; }
.not-connected { font-size: 0.75rem; color: #94a3b8; }

@media (max-width: 768px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .search-input { width: 160px; }
}
</style>
