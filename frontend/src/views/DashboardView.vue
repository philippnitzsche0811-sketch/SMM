<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1>My Videos</h1>
        <p class="subtitle">{{ videos.length }} video{{ videos.length !== 1 ? 's' : '' }} total</p>
      </div>
      <Button label="Upload Video" icon="pi pi-upload" @click="openUploadDialog" />
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon-wrap" style="background:#eef2ff">
          <i class="pi pi-video" style="color:#6366f1"></i>
        </div>
        <div>
          <div class="stat-value">{{ videos.length }}</div>
          <div class="stat-label">Videos</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon-wrap" style="background:#ecfdf5">
          <i class="pi pi-share-alt" style="color:#10b981"></i>
        </div>
        <div>
          <div class="stat-value">{{ connectedCount }}</div>
          <div class="stat-label">Platforms</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon-wrap" style="background:#eff6ff">
          <i class="pi pi-check-circle" style="color:#3b82f6"></i>
        </div>
        <div>
          <div class="stat-value">{{ uploadedCount }}</div>
          <div class="stat-label">Published</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon-wrap" style="background:#fffbeb">
          <i class="pi pi-clock" style="color:#f59e0b"></i>
        </div>
        <div>
          <div class="stat-value">{{ processingCount }}</div>
          <div class="stat-label">Processing</div>
        </div>
      </div>
    </div>

    <!-- Video Library -->
    <div class="videos-card">
      <div class="videos-card-header">
        <span class="videos-title">Video Library</span>
        <InputText v-model="searchQuery" placeholder="Search..." class="search-input" />
      </div>

      <div v-if="loading" class="loading-state">
        <ProgressSpinner />
      </div>

      <div v-else-if="filteredVideos.length === 0" class="empty-state">
        <div class="empty-icon-wrap">
          <i class="pi pi-cloud-upload"></i>
        </div>
        <p class="empty-title">No videos yet</p>
        <p class="empty-sub">Upload your first video to get started</p>
        <Button label="Upload Video" icon="pi pi-upload" @click="openUploadDialog" outlined />
      </div>

      <DataTable
        v-else
        :value="filteredVideos"
        :rows="10"
        :paginator="filteredVideos.length > 10"
        stripedRows
        class="video-table"
      >
        <Column field="title" header="Title" sortable>
          <template #body="{ data }">
            <div class="video-title-cell">
              <div class="video-thumb"><i class="pi pi-video"></i></div>
              <div>
                <div class="video-name">{{ data.title }}</div>
                <div class="video-date">{{ formatDate(data.createdAt) }}</div>
              </div>
            </div>
          </template>
        </Column>

        <Column field="platforms" header="Platforms">
          <template #body="{ data }">
            <div class="platform-badges">
              <span v-for="p in data.platforms" :key="p" class="platform-badge" :class="p">
                <i :class="platformIcon(p)"></i> {{ p }}
              </span>
            </div>
          </template>
        </Column>

        <Column field="status" header="Status" sortable>
          <template #body="{ data }">
            <Tag :value="statusLabel(data.status)" :severity="statusSeverity(data.status)" />
          </template>
        </Column>

        <Column field="privacy" header="Visibility">
          <template #body="{ data }">
            <span class="privacy-badge">
              <i :class="data.privacy === 'public' ? 'pi pi-globe' : 'pi pi-lock'"></i>
              {{ data.privacy === 'public' ? 'Public' : data.privacy === 'unlisted' ? 'Unlisted' : 'Private' }}
            </span>
          </template>
        </Column>

        <Column header="Actions" style="width:110px">
          <template #body="{ data }">
            <div class="action-buttons">
              <Button icon="pi pi-pencil" class="p-button-text p-button-sm p-button-secondary" v-tooltip="'Edit'" @click="openEditDialog(data)" />
              <Button icon="pi pi-trash"  class="p-button-text p-button-sm p-button-danger"    v-tooltip="'Delete'" @click="confirmDelete(data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Upload / Edit Dialog -->
    <Dialog
      v-model:visible="showDialog"
      :header="editingVideo ? 'Edit Video' : 'Upload Video'"
      :modal="true"
      :style="{ width: '560px' }"
      :closable="!uploading"
    >
      <div class="dialog-form">
        <div v-if="!editingVideo" class="file-zone" :class="{ 'has-file': selectedFile }" @click="triggerFileInput" @dragover.prevent @drop.prevent="onFileDrop">
          <input ref="fileInput" type="file" accept="video/*" style="display:none" @change="onFileChange" />
          <template v-if="selectedFile">
            <i class="pi pi-check-circle file-zone-icon" style="color:#10b981"></i>
            <span class="file-zone-name">{{ selectedFile.name }}</span>
            <span class="file-zone-size">{{ formatFileSize(selectedFile.size) }}</span>
          </template>
          <template v-else>
            <i class="pi pi-cloud-upload file-zone-icon"></i>
            <span>Drop video here or click to browse</span>
            <span class="file-zone-hint">MP4, MOV, AVI, MKV up to 2 GB</span>
          </template>
        </div>

        <div v-if="uploading" class="upload-progress">
          <ProgressBar :value="uploadProgress" />
          <span>{{ uploadProgress }}% uploaded...</span>
        </div>

        <div class="form-field">
          <label>Title *</label>
          <InputText v-model="form.title" placeholder="Enter title" class="w-full" />
        </div>
        <div class="form-field">
          <label>Description</label>
          <Textarea v-model="form.description" placeholder="Enter description" rows="3" class="w-full" />
        </div>
        <div class="form-field">
          <label>Tags</label>
          <InputText v-model="form.tags" placeholder="tag1, tag2, tag3" class="w-full" />
        </div>
        <div class="form-field">
          <label>Visibility</label>
          <Dropdown v-model="form.privacy" :options="privacyOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>

        <div v-if="!editingVideo" class="form-field">
          <label>Platforms</label>
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
              <span v-if="!p.connected" class="not-connected">Not connected</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="closeDialog" :disabled="uploading" />
        <Button
          :label="editingVideo ? 'Save' : 'Upload'"
          icon="pi pi-upload"
          :loading="uploading"
          :disabled="!canSubmit"
          @click="handleSubmit"
        />
      </template>
    </Dialog>

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
  { label: 'Private',  value: 'private'  },
  { label: 'Unlisted', value: 'unlisted' },
  { label: 'Public',   value: 'public'   },
];

const connectedCount  = computed(() => authStore.user?.connectedPlatforms?.length || 0);
const uploadedCount   = computed(() => videos.value.filter(v => v.status === 'uploaded').length);
const processingCount = computed(() => videos.value.filter(v => ['processing','pending'].includes(v.status)).length);

const filteredVideos = computed(() => {
  if (!searchQuery.value) return videos.value;
  const q = searchQuery.value.toLowerCase();
  return videos.value.filter(v => v.title.toLowerCase().includes(q));
});

const availablePlatforms = computed(() => [
  { id: 'youtube',   name: 'YouTube',   icon: 'pi pi-youtube',   color: '#FF0000', connected: authStore.user?.connectedPlatforms?.some((p: any) => p.platform === 'youtube')   || false },
  { id: 'tiktok',    name: 'TikTok',    icon: 'pi pi-video',     color: '#000000', connected: authStore.user?.connectedPlatforms?.some((p: any) => p.platform === 'tiktok')    || false },
  { id: 'instagram', name: 'Instagram', icon: 'pi pi-instagram', color: '#E4405F', connected: authStore.user?.connectedPlatforms?.some((p: any) => p.platform === 'instagram') || false },
]);

const canSubmit = computed(() =>
  !!form.value.title.trim() && (!!editingVideo.value || !!selectedFile.value)
);

const platformIcon = (p: string) =>
  ({ youtube: 'pi pi-youtube', tiktok: 'pi pi-video', instagram: 'pi pi-instagram' }[p] || 'pi pi-globe');

const statusLabel = (s: string) =>
  ({ pending: 'Pending', processing: 'Processing', uploaded: 'Done', failed: 'Failed' }[s] || s);

const statusSeverity = (s: string): any =>
  ({ pending: 'secondary', processing: 'info', uploaded: 'success', failed: 'danger' }[s] || 'secondary');

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

const formatFileSize = (bytes: number) => {
  if (bytes >= 1_000_000_000) return (bytes / 1_000_000_000).toFixed(1) + ' GB';
  if (bytes >= 1_000_000) return (bytes / 1_000_000).toFixed(1) + ' MB';
  return (bytes / 1_000).toFixed(0) + ' KB';
};

const triggerFileInput = () => fileInput.value?.click();
const onFileChange = (e: Event) => { const f = (e.target as HTMLInputElement).files?.[0]; if (f) selectedFile.value = f; };
const onFileDrop   = (e: DragEvent) => { const f = e.dataTransfer?.files?.[0]; if (f?.type.startsWith('video/')) selectedFile.value = f; };
const togglePlatform = (id: string) => {
  const idx = form.value.platforms.indexOf(id);
  if (idx > -1) form.value.platforms.splice(idx, 1); else form.value.platforms.push(id);
};

const openUploadDialog = () => {
  editingVideo.value = null; selectedFile.value = null;
  form.value = { title: '', description: '', tags: '', privacy: 'private', platforms: [] };
  showDialog.value = true;
};

const openEditDialog = (video: any) => {
  editingVideo.value = video;
  form.value = {
    title:       video.title || '',
    description: video.description || '',
    tags:        Array.isArray(video.tags) ? video.tags.join(', ') : (video.tags || ''),
    privacy:     video.privacy || 'private',
    platforms:   [],
  };
  showDialog.value = true;
};

const closeDialog = () => {
  showDialog.value = false; editingVideo.value = null;
  selectedFile.value = null; uploadProgress.value = 0;
};

const handleSubmit = async () => {
  const userId = authStore.user?.id;
  if (!userId) return;
  uploading.value = true;
  try {
    if (editingVideo.value) {
      await api.patch(`/api/upload/video/${editingVideo.value.id}`, {
        user_id: userId, title: form.value.title,
        description: form.value.description, tags: form.value.tags,
        privacy_status: form.value.privacy,
      });
      const idx = videos.value.findIndex(v => v.id === editingVideo.value.id);
      if (idx > -1) videos.value[idx] = { ...videos.value[idx], title: form.value.title, description: form.value.description, tags: form.value.tags.split(',').map((t: string) => t.trim()), privacy: form.value.privacy };
      toast.add({ severity: 'success', summary: 'Saved', detail: 'Video updated', life: 3000 });
    } else {
      if (!selectedFile.value) return;
      const fd = new FormData();
      fd.append('user_id', userId);
      fd.append('video', selectedFile.value);
      fd.append('title', form.value.title);
      fd.append('description', form.value.description);
      fd.append('tags', form.value.tags);
      fd.append('privacy_status', form.value.privacy);
      fd.append('platforms', form.value.platforms.join(','));
      const res = await api.post('/api/upload/upload_video', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => { if (e.total) uploadProgress.value = Math.round((e.loaded * 100) / e.total); },
      });
      const result = res.data;
      videos.value.unshift({ id: result.video_id, title: form.value.title, description: form.value.description, status: result.status, platforms: form.value.platforms, tags: form.value.tags.split(',').map((t: string) => t.trim()), privacy: form.value.privacy, createdAt: new Date().toISOString() });
      toast.add({ severity: 'success', summary: 'Upload started', detail: `"${form.value.title}" is being uploaded`, life: 4000 });
      pollVideoStatus(result.video_id);
    }
    closeDialog();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || err.message, life: 5000 });
  } finally {
    uploading.value = false;
  }
};

const confirmDelete = (video: any) => {
  confirm.require({
    message: `Delete "${video.title}"? This will also remove it from all connected platforms.`,
    header: 'Delete Video',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Delete',
    rejectLabel: 'Cancel',
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
    toast.add({ severity: 'success', summary: 'Deleted', detail: `"${video.title}" was deleted`, life: 3000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Delete failed', life: 5000 });
  }
};

const pollVideoStatus = (videoId: string) => {
  const interval = setInterval(async () => {
    try {
      const res = await api.get(`/api/upload/video/${videoId}`);
      const idx = videos.value.findIndex(v => v.id === videoId);
      if (idx > -1) videos.value[idx].status = res.data.status;
      if (['uploaded','failed'].includes(res.data.status)) clearInterval(interval);
    } catch { clearInterval(interval); }
  }, 3000);
};

onMounted(async () => {
  const userId = authStore.user?.id;
  if (!userId) return;
  try {
    const res = await api.get(`/api/upload/videos/user/${userId}`);
    videos.value = res.data.videos.map((v: any) => ({
      id: v.video_id, title: v.title, description: v.description,
      status: v.status, platforms: v.platforms, tags: v.tags,
      privacy: v.privacy_status, createdAt: v.created_at,
    }));
  } catch (err) { console.error('Failed to load videos:', err); }
  finally { loading.value = false; }
});
</script>

<style scoped>
.dashboard { max-width: 1400px; margin: 0 auto; }

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}
.dashboard-header h1 { font-size: 1.625rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.2rem; }
.subtitle { color: var(--text-secondary); font-size: 0.875rem; margin: 0; }

/* Stats */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.125rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.stat-value { font-size: 1.625rem; font-weight: 700; color: var(--text-primary); line-height: 1; }
.stat-label { font-size: 0.8125rem; color: var(--text-secondary); margin-top: 0.2rem; }

/* Video card */
.videos-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.videos-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.125rem 1.375rem;
  border-bottom: 1px solid var(--border-color);
}

.videos-title { font-size: 0.9375rem; font-weight: 600; color: var(--text-primary); }
.search-input { width: 220px; }

/* Table */
.video-title-cell { display: flex; align-items: center; gap: 0.75rem; }
.video-thumb {
  width: 36px; height: 36px; border-radius: 8px;
  background: var(--bg-tertiary); display: flex;
  align-items: center; justify-content: center; color: var(--text-disabled); flex-shrink: 0;
}
.video-name { font-weight: 500; color: var(--text-primary); font-size: 0.875rem; }
.video-date { font-size: 0.78rem; color: var(--text-disabled); margin-top: 0.1rem; }

.platform-badges { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.platform-badge {
  display: inline-flex; align-items: center; gap: 0.2rem;
  padding: 0.15rem 0.45rem; border-radius: 4px;
  font-size: 0.72rem; font-weight: 600; text-transform: capitalize;
  background: var(--bg-tertiary); color: var(--text-secondary);
}
.platform-badge.youtube   { background: #fff5f5; color: #ef4444; }
.platform-badge.tiktok    { background: #f8fafc; color: #334155; }
.platform-badge.instagram { background: #fdf2f8; color: #ec4899; }

.privacy-badge { display: flex; align-items: center; gap: 0.35rem; font-size: 0.875rem; color: var(--text-secondary); }
.action-buttons { display: flex; gap: 0.2rem; }

/* Empty */
.loading-state, .empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 4rem 2rem; gap: 0.75rem;
}
.empty-icon-wrap {
  width: 60px; height: 60px; border-radius: 50%;
  background: var(--primary-50); display: flex;
  align-items: center; justify-content: center;
  font-size: 1.5rem; color: var(--primary-400);
  margin-bottom: 0.25rem;
}
.empty-title { font-size: 1.0625rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.empty-sub   { font-size: 0.875rem; color: var(--text-secondary); margin: 0; }

/* Dialog */
.dialog-form { display: flex; flex-direction: column; gap: 1.125rem; }
.file-zone {
  border: 2px dashed var(--border-color); border-radius: var(--radius-lg);
  padding: 1.75rem; text-align: center; cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  display: flex; flex-direction: column; align-items: center; gap: 0.4rem;
  color: var(--text-disabled);
}
.file-zone:hover { border-color: var(--primary-400); background: var(--primary-50); }
.file-zone.has-file { border-color: #10b981; background: #f0fdf4; color: #15803d; }
.file-zone-icon { font-size: 2.25rem; }
.file-zone-name { font-weight: 600; font-size: 0.875rem; }
.file-zone-size, .file-zone-hint { font-size: 0.78rem; }

.upload-progress { display: flex; flex-direction: column; gap: 0.4rem; font-size: 0.875rem; color: var(--text-secondary); }
.form-field { display: flex; flex-direction: column; gap: 0.35rem; }
.form-field label { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); }

.platform-select { display: flex; gap: 0.625rem; flex-wrap: wrap; }
.platform-option {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.5rem 0.875rem; border: 2px solid var(--border-color);
  border-radius: 8px; cursor: pointer; transition: all 0.15s;
  font-size: 0.875rem; font-weight: 500; user-select: none;
}
.platform-option:hover:not(.disabled) { border-color: var(--primary-400); }
.platform-option.selected { border-color: var(--primary-500); background: var(--primary-50); color: var(--primary-600); }
.platform-option.disabled { opacity: 0.45; cursor: not-allowed; }
.not-connected { font-size: 0.72rem; color: var(--text-disabled); }

@media (max-width: 900px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .dashboard-header { flex-direction: column; gap: 1rem; }
  .search-input { width: 100%; }
  .videos-card-header { flex-direction: column; gap: 0.75rem; align-items: stretch; }
}
</style>
