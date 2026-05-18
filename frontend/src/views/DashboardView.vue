<template>
  <div class="dashboard">

    <!-- Begrüßung + Quick Action -->
    <div class="dashboard-hero">
      <div class="hero-left">
        <h1>Hallo, {{ authStore.userName || 'Creator' }} 👋</h1>
        <p class="subtitle">Was willst du heute hochladen?</p>
      </div>
      <button class="btn-upload-hero" @click="router.push('/upload')">
        <i class="pi pi-cloud-upload"></i>
        Video hochladen
      </button>
    </div>

    <!-- Smart Cards -->
    <div class="smart-row">
      <!-- Bereit zum Hochladen (Ready-Ideen) -->
      <div class="smart-card ready-card" v-if="readyIdeas.length > 0">
        <div class="smart-card-header">
          <i class="pi pi-lightbulb smart-icon ready"></i>
          <span class="smart-card-title">Bereit zum Hochladen</span>
          <span class="smart-badge">{{ readyIdeas.length }}</span>
        </div>
        <div class="ready-ideas-list">
          <div
            v-for="idea in readyIdeas.slice(0, 3)"
            :key="idea.id"
            class="ready-idea-item"
          >
            <span class="ready-idea-title">{{ idea.title }}</span>
            <button class="btn-upload-idea" @click="uploadIdea(idea)">
              <i class="pi pi-cloud-upload"></i> Hochladen
            </button>
          </div>
        </div>
        <button class="smart-card-link" @click="router.push('/plan')">
          Alle Ideen ansehen <i class="pi pi-arrow-right"></i>
        </button>
      </div>

      <!-- Leere Ideen-Card -->
      <div class="smart-card ready-card empty" v-else>
        <div class="smart-card-header">
          <i class="pi pi-lightbulb smart-icon ready"></i>
          <span class="smart-card-title">Ideen planen</span>
        </div>
        <p class="smart-empty-text">Noch keine fertigen Ideen. Erstelle eine im Planen-Tab.</p>
        <button class="smart-card-link" @click="router.push('/plan')">
          Zu Planen <i class="pi pi-arrow-right"></i>
        </button>
      </div>

      <!-- Letzte Performance -->
      <div class="smart-card perf-card">
        <div class="smart-card-header">
          <i class="pi pi-chart-bar smart-icon perf"></i>
          <span class="smart-card-title">Letzte Performance</span>
        </div>
        <div v-if="recentVideos.length > 0" class="perf-list">
          <div v-for="v in recentVideos.slice(0, 3)" :key="v.id" class="perf-item">
            <div class="perf-item-info">
              <span class="perf-title">{{ v.title }}</span>
              <div class="platform-pills">
                <span v-for="p in v.platforms" :key="p" class="platform-pill" :class="p">
                  <i :class="platformIcon(p)"></i>
                </span>
              </div>
            </div>
            <Tag :value="statusLabel(v.status)" :severity="statusSeverity(v.status)" />
          </div>
        </div>
        <p v-else class="smart-empty-text">Noch keine Videos hochgeladen.</p>
        <button class="smart-card-link" @click="activeTab = 'videos'">
          Alle Videos <i class="pi pi-arrow-right"></i>
        </button>
      </div>

      <!-- Stats -->
      <div class="smart-card stats-card">
        <div class="smart-card-header">
          <i class="pi pi-info-circle smart-icon stats"></i>
          <span class="smart-card-title">Überblick</span>
        </div>
        <div class="stats-list">
          <div class="stats-row-item">
            <span class="stats-label">Videos gesamt</span>
            <span class="stats-value">{{ videos.length }}</span>
          </div>
          <div class="stats-row-item">
            <span class="stats-label">Veröffentlicht</span>
            <span class="stats-value success">{{ uploadedCount }}</span>
          </div>
          <div class="stats-row-item">
            <span class="stats-label">Plattformen</span>
            <span class="stats-value">{{ connectedCount }}</span>
          </div>
          <div class="stats-row-item">
            <span class="stats-label">In Bearbeitung</span>
            <span class="stats-value warn">{{ processingCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: Alle Videos -->
    <div class="videos-section">
      <div class="videos-card">
        <div class="videos-card-header">
          <span class="videos-title">Meine Videos</span>
          <InputText v-model="searchQuery" placeholder="Suchen…" class="search-input" />
        </div>

        <div v-if="loading" class="loading-state">
          <ProgressSpinner />
        </div>

        <div v-else-if="filteredVideos.length === 0" class="empty-state">
          <div class="empty-icon-wrap"><i class="pi pi-cloud-upload"></i></div>
          <p class="empty-title">Noch keine Videos</p>
          <p class="empty-sub">Lade dein erstes Video hoch</p>
          <Button label="Video hochladen" icon="pi pi-upload" @click="router.push('/upload')" outlined />
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
                <div class="video-thumb"><i class="pi pi-video"></i></div>
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
          <Column field="privacy" header="Sichtbarkeit">
            <template #body="{ data }">
              <span class="privacy-badge">
                <i :class="data.privacy === 'public' ? 'pi pi-globe' : 'pi pi-lock'"></i>
                {{ data.privacy === 'public' ? 'Öffentlich' : data.privacy === 'unlisted' ? 'Nicht gelistet' : 'Privat' }}
              </span>
            </template>
          </Column>
          <Column header="Aktionen" style="width:110px">
            <template #body="{ data }">
              <div class="action-buttons">
                <Button icon="pi pi-pencil" class="p-button-text p-button-sm p-button-secondary" v-tooltip="'Bearbeiten'" @click="openEditDialog(data)" />
                <Button icon="pi pi-trash"  class="p-button-text p-button-sm p-button-danger"    v-tooltip="'Löschen'" @click="confirmDelete(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Edit Dialog -->
    <Dialog v-model:visible="showDialog" header="Video bearbeiten" :modal="true" :style="{ width: '560px' }" :closable="!saving">
      <div class="dialog-form">
        <div class="form-field">
          <label>Titel *</label>
          <InputText v-model="form.title" placeholder="Titel eingeben" class="w-full" />
        </div>
        <div class="form-field">
          <label>Beschreibung</label>
          <Textarea v-model="form.description" placeholder="Beschreibung" rows="3" class="w-full" />
        </div>
        <div class="form-field">
          <label>Tags</label>
          <InputText v-model="form.tags" placeholder="tag1, tag2, tag3" class="w-full" />
        </div>
        <div class="form-field">
          <label>Sichtbarkeit</label>
          <Dropdown v-model="form.privacy" :options="privacyOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" class="p-button-text" @click="closeDialog" :disabled="saving" />
        <Button label="Speichern" icon="pi pi-check" :loading="saving" :disabled="!form.title.trim()" @click="handleSave" />
      </template>
    </Dialog>

    <!-- Delete Dialog -->
    <Dialog v-model:visible="showDeleteDialog" header="Video löschen" :modal="true" :style="{ width: '420px' }" :closable="!deleting">
      <div class="delete-confirm-body">
        <i class="pi pi-exclamation-triangle delete-warn-icon"></i>
        <p>„<strong>{{ deleteTarget?.title }}</strong>" wirklich löschen?</p>
      </div>
      <template #footer>
        <Button label="Abbrechen" class="p-button-text" @click="showDeleteDialog = false" :disabled="deleting" />
        <Button label="Löschen" icon="pi pi-trash" severity="danger" :loading="deleting" @click="handleDeleteConfirmed" />
      </template>
    </Dialog>

    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';
import api, { listIdeas } from '@/services/api';

const router    = useRouter();
const authStore = useAuthStore();
const toast     = useToast();

const videos      = ref<any[]>([]);
const ideas       = ref<any[]>([]);
const loading     = ref(true);
const showDialog  = ref(false);
const editingVideo = ref<any>(null);
const saving      = ref(false);
const searchQuery = ref('');
const showDeleteDialog = ref(false);
const deleteTarget     = ref<any>(null);
const deleting         = ref(false);
const activeTab        = ref<'overview' | 'videos'>('overview');

const form = ref({ title: '', description: '', tags: '', privacy: 'private' });

const privacyOptions = [
  { label: 'Privat',         value: 'private'  },
  { label: 'Nicht gelistet', value: 'unlisted' },
  { label: 'Öffentlich',     value: 'public'   },
];

const connectedCount  = computed(() => authStore.user?.connectedPlatforms?.length || 0);
const uploadedCount   = computed(() => videos.value.filter(v => v.status === 'uploaded').length);
const processingCount = computed(() => videos.value.filter(v => ['processing','pending'].includes(v.status)).length);
const recentVideos    = computed(() => [...videos.value].slice(0, 5));
const readyIdeas      = computed(() => ideas.value.filter(i => i.status === 'ready'));

const filteredVideos = computed(() => {
  if (!searchQuery.value) return videos.value;
  const q = searchQuery.value.toLowerCase();
  return videos.value.filter(v => v.title.toLowerCase().includes(q));
});

const platformIcon = (p: string) =>
  ({ youtube: 'pi pi-youtube', tiktok: 'pi pi-video', instagram: 'pi pi-instagram' }[p] || 'pi pi-globe');

const statusLabel = (s: string) =>
  ({ pending: 'Ausstehend', processing: 'Verarbeitung', uploaded: 'Fertig', failed: 'Fehler' }[s] || s);

const statusSeverity = (s: string): any =>
  ({ pending: 'secondary', processing: 'info', uploaded: 'success', failed: 'danger' }[s] || 'secondary');

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('de-DE', { month: 'short', day: 'numeric', year: 'numeric' });

function uploadIdea(idea: any) {
  router.push({
    path: '/upload',
    query: { title: idea.title, description: idea.concept || '', platforms: (idea.target_platforms || []).join(',') },
  });
}

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

const closeDialog = () => { showDialog.value = false; editingVideo.value = null; };

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
    toast.add({ severity: 'success', summary: 'Gespeichert', detail: 'Video aktualisiert', life: 3000 });
    closeDialog();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || err.message, life: 5000 });
  } finally { saving.value = false; }
};

const confirmDelete = (video: any) => { deleteTarget.value = video; showDeleteDialog.value = true; };

const handleDeleteConfirmed = async () => {
  const video = deleteTarget.value;
  const userId = authStore.user?.id;
  if (!video || !userId) return;
  deleting.value = true;
  try {
    await api.delete(`/api/upload/video/${video.id}`, { data: { user_id: userId } });
    videos.value = videos.value.filter(v => v.id !== video.id);
    toast.add({ severity: 'success', summary: 'Gelöscht', detail: `„${video.title}" wurde gelöscht`, life: 3000 });
    showDeleteDialog.value = false;
    deleteTarget.value = null;
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || 'Löschen fehlgeschlagen', life: 5000 });
  } finally { deleting.value = false; }
};

onMounted(async () => {
  const userId = authStore.user?.id;
  if (!userId) return;
  try {
    const [videosRes] = await Promise.all([
      api.get(`/api/upload/videos/user/${userId}`),
      listIdeas(userId).then(data => { ideas.value = data; }).catch(() => {}),
    ]);
    videos.value = videosRes.data.videos.map((v: any) => ({
      id: v.video_id, title: v.title, description: v.description,
      status: v.status, platforms: v.platforms, tags: v.tags,
      privacy: v.privacy_status, createdAt: v.created_at,
    }));
  } catch (err) { console.error('Dashboard laden fehlgeschlagen:', err); }
  finally { loading.value = false; }
});
</script>

<style scoped>
.dashboard { max-width: 1400px; margin: 0 auto; padding: 1.5rem 1rem; }

/* Hero */
.dashboard-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.dashboard-hero h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.2rem;
  letter-spacing: -0.025em;
}
.subtitle { color: var(--text-secondary); font-size: 0.875rem; margin: 0; }

.btn-upload-hero {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, #4f7fff, #7c3aed);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.15s;
  flex-shrink: 0;
}
.btn-upload-hero:hover { opacity: 0.88; transform: translateY(-1px); }

/* Smart Cards Row */
.smart-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr) 200px;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 1100px) {
  .smart-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .smart-row { grid-template-columns: 1fr; }
}

.smart-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.125rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 160px;
}

.smart-card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.smart-icon {
  font-size: 1rem;
  width: 28px;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.smart-icon.ready { background: rgba(16,185,129,0.12); color: #10b981; }
.smart-icon.perf  { background: rgba(79,127,255,0.12); color: #4f7fff; }
.smart-icon.stats { background: rgba(139,92,246,0.12); color: #8b5cf6; }

.smart-card-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--text-primary);
  flex: 1;
}

.smart-badge {
  background: rgba(16,185,129,0.15);
  color: #10b981;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 10px;
}

.smart-empty-text {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  margin: 0;
  flex: 1;
}

.smart-card-link {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  transition: color 0.15s;
  margin-top: auto;
}
.smart-card-link:hover { color: #4f7fff; }

/* Ready Ideas */
.ready-ideas-list { display: flex; flex-direction: column; gap: 0.4rem; flex: 1; }
.ready-idea-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.4rem 0.625rem;
  background: rgba(16,185,129,0.05);
  border: 1px solid rgba(16,185,129,0.15);
  border-radius: 7px;
}
.ready-idea-title {
  font-size: 0.8125rem;
  color: var(--text-primary);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.btn-upload-idea {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.625rem;
  background: rgba(16,185,129,0.12);
  color: #10b981;
  border: 1px solid rgba(16,185,129,0.3);
  border-radius: 5px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}
.btn-upload-idea:hover { background: rgba(16,185,129,0.2); }

/* Performance list */
.perf-list { display: flex; flex-direction: column; gap: 0.5rem; flex: 1; }
.perf-item { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.perf-item-info { flex: 1; min-width: 0; }
.perf-title { font-size: 0.8125rem; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
.platform-pills { display: flex; gap: 3px; margin-top: 2px; }
.platform-pill { font-size: 0.75rem; }
.platform-pill.youtube { color: #f87171; }
.platform-pill.tiktok  { color: #94a3b8; }
.platform-pill.instagram { color: #f9a8d4; }

/* Stats list */
.stats-list { display: flex; flex-direction: column; gap: 0.5rem; flex: 1; }
.stats-row-item { display: flex; justify-content: space-between; align-items: center; }
.stats-label { font-size: 0.8125rem; color: var(--text-secondary); }
.stats-value { font-size: 0.875rem; font-weight: 700; color: var(--text-primary); }
.stats-value.success { color: #10b981; }
.stats-value.warn    { color: #f59e0b; }

/* Videos Section */
.videos-section { margin-top: 0.5rem; }

.videos-card {
  background: rgba(255,255,255,0.03);
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

.videos-title {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}
.search-input { width: 220px; }

/* Table */
.video-title-cell { display: flex; align-items: center; gap: 0.75rem; }
.video-thumb { width: 36px; height: 36px; border-radius: 8px; background: var(--bg-tertiary); display: flex; align-items: center; justify-content: center; color: var(--text-disabled); flex-shrink: 0; }
.video-name { font-weight: 500; color: var(--text-primary); font-size: 0.875rem; }
.video-date { font-size: 0.78rem; color: var(--text-disabled); margin-top: 0.1rem; }

.platform-badges { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.platform-badge { display: inline-flex; align-items: center; gap: 0.2rem; padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.72rem; font-weight: 600; text-transform: capitalize; background: var(--bg-tertiary); color: var(--text-secondary); }
.platform-badge.youtube   { background: rgba(239,68,68,0.12);  color: #f87171; }
.platform-badge.tiktok    { background: rgba(255,255,255,0.07); color: #cbd5e1; }
.platform-badge.instagram { background: rgba(236,72,153,0.12); color: #f9a8d4; }

.privacy-badge { display: flex; align-items: center; gap: 0.35rem; font-size: 0.875rem; color: var(--text-secondary); }
.action-buttons { display: flex; gap: 0.2rem; }

/* Empty */
.loading-state, .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; gap: 0.75rem; }
.empty-icon-wrap { width: 60px; height: 60px; border-radius: 50%; background: var(--primary-50); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: var(--primary-400); margin-bottom: 0.25rem; }
.empty-title { font-size: 1.0625rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.empty-sub   { font-size: 0.875rem; color: var(--text-secondary); margin: 0; }

/* Dialog */
.dialog-form { display: flex; flex-direction: column; gap: 1.125rem; }
.form-field { display: flex; flex-direction: column; gap: 0.35rem; }
.form-field label { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); }
.delete-confirm-body { display: flex; align-items: flex-start; gap: 0.875rem; padding: 0.25rem 0; }
.delete-warn-icon { font-size: 1.5rem; color: #f59e0b; flex-shrink: 0; margin-top: 2px; }
.delete-confirm-body p { margin: 0; color: var(--text-secondary); line-height: 1.5; font-size: 0.9rem; }

@media (max-width: 640px) {
  .dashboard-hero { flex-direction: column; align-items: flex-start; }
  .search-input { width: 100%; }
  .videos-card-header { flex-direction: column; gap: 0.75rem; align-items: stretch; }
}
</style>
