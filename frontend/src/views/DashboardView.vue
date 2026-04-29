<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1>My Videos</h1>
        <p class="subtitle">{{ videos.length }} video{{ videos.length !== 1 ? 's' : '' }} total</p>
      </div>
      <Button label="Upload Video" icon="pi pi-upload" @click="router.push('/upload')" />
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
        <Button label="Upload Video" icon="pi pi-upload" @click="router.push('/upload')" outlined />
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

    <!-- Edit Dialog -->
    <Dialog
      v-model:visible="showDialog"
      header="Edit Video"
      :modal="true"
      :style="{ width: '560px' }"
      :closable="!saving"
    >
      <div class="dialog-form">
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
      </div>

      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="closeDialog" :disabled="saving" />
        <Button
          label="Save"
          icon="pi pi-check"
          :loading="saving"
          :disabled="!form.title.trim()"
          @click="handleSave"
        />
      </template>
    </Dialog>

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
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
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import api from '@/services/api';

const router    = useRouter();
const authStore = useAuthStore();
const toast     = useToast();
const confirm   = useConfirm();

const videos      = ref<any[]>([]);
const loading     = ref(true);
const showDialog  = ref(false);
const editingVideo = ref<any>(null);
const saving      = ref(false);
const searchQuery = ref('');

const form = ref({
  title: '',
  description: '',
  tags: '',
  privacy: 'private',
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

const platformIcon = (p: string) =>
  ({ youtube: 'pi pi-youtube', tiktok: 'pi pi-video', instagram: 'pi pi-instagram' }[p] || 'pi pi-globe');

const statusLabel = (s: string) =>
  ({ pending: 'Pending', processing: 'Processing', uploaded: 'Done', failed: 'Failed' }[s] || s);

const statusSeverity = (s: string): any =>
  ({ pending: 'secondary', processing: 'info', uploaded: 'success', failed: 'danger' }[s] || 'secondary');

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

const openEditDialog = (video: any) => {
  editingVideo.value = video;
  form.value = {
    title:       video.title || '',
    description: video.description || '',
    tags:        Array.isArray(video.tags) ? video.tags.join(', ') : (video.tags || ''),
    privacy:     video.privacy || 'private',
  };
  showDialog.value = true;
};

const closeDialog = () => {
  showDialog.value = false;
  editingVideo.value = null;
};

const handleSave = async () => {
  const userId = authStore.user?.id;
  if (!userId || !editingVideo.value) return;
  saving.value = true;
  try {
    await api.patch(`/api/upload/video/${editingVideo.value.id}`, {
      user_id: userId, title: form.value.title,
      description: form.value.description, tags: form.value.tags,
      privacy_status: form.value.privacy,
    });
    const idx = videos.value.findIndex(v => v.id === editingVideo.value.id);
    if (idx > -1) videos.value[idx] = { ...videos.value[idx], title: form.value.title, description: form.value.description, tags: form.value.tags.split(',').map((t: string) => t.trim()), privacy: form.value.privacy };
    toast.add({ severity: 'success', summary: 'Saved', detail: 'Video updated', life: 3000 });
    closeDialog();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || err.message, life: 5000 });
  } finally {
    saving.value = false;
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
.form-field { display: flex; flex-direction: column; gap: 0.35rem; }
.form-field label { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); }

@media (max-width: 900px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .dashboard-header { flex-direction: column; gap: 1rem; }
  .search-input { width: 100%; }
  .videos-card-header { flex-direction: column; gap: 0.75rem; align-items: stretch; }
}
</style>
