<template>
  <div class="platforms-view">
    <div class="page-header">
      <h1>Plattformen verwalten</h1>
      <p class="subtitle">Verbinde deine Social-Media-Accounts, um Videos hochzuladen</p>
    </div>

    <div v-if="loading" class="loading-state">
      <ProgressSpinner />
    </div>

    <div v-else class="platforms-grid">
      <!-- YouTube -->
      <div class="platform-card" :class="{ connected: isConnected('youtube') }">
        <div class="platform-card-header">
          <div class="platform-brand youtube">
            <i class="pi pi-youtube"></i>
          </div>
          <div class="platform-info">
            <h3>YouTube</h3>
            <p>Videos auf deinen Kanal hochladen</p>
          </div>
          <div class="platform-status" :class="isConnected('youtube') ? 'status-connected' : 'status-disconnected'">
            <i :class="isConnected('youtube') ? 'pi pi-check-circle' : 'pi pi-circle'"></i>
            {{ isConnected('youtube') ? 'Verbunden' : 'Nicht verbunden' }}
          </div>
        </div>

        <div v-if="isConnected('youtube')" class="platform-account-info">
          <i class="pi pi-user"></i>
          <span>{{ getAccount('youtube')?.username || getAccount('youtube')?.channelId || 'YouTube Account' }}</span>
          <span class="connected-since">Verbunden seit {{ formatDate(getAccount('youtube')?.connectedAt) }}</span>
        </div>

        <div class="platform-card-footer">
          <template v-if="isConnected('youtube')">
            <Button
              label="Trennen"
              icon="pi pi-unlink"
              class="p-button-outlined p-button-danger p-button-sm"
              :loading="disconnecting === 'youtube'"
              @click="confirmDisconnect('youtube', 'YouTube')"
            />
          </template>
          <template v-else>
            <Button
              label="Verbinden"
              icon="pi pi-link"
              class="p-button-sm"
              :loading="connecting === 'youtube'"
              @click="showYouTubeDialog = true"
            />
          </template>
        </div>
      </div>

      <!-- TikTok -->
      <div class="platform-card" :class="{ connected: isConnected('tiktok') }">
        <div class="platform-card-header">
          <div class="platform-brand tiktok">
            <i class="pi pi-video"></i>
          </div>
          <div class="platform-info">
            <h3>TikTok</h3>
            <p>Kurze Videos auf TikTok posten</p>
          </div>
          <div class="platform-status" :class="isConnected('tiktok') ? 'status-connected' : 'status-disconnected'">
            <i :class="isConnected('tiktok') ? 'pi pi-check-circle' : 'pi pi-circle'"></i>
            {{ isConnected('tiktok') ? 'Verbunden' : 'Nicht verbunden' }}
          </div>
        </div>

        <div v-if="isConnected('tiktok')" class="platform-account-info">
          <i class="pi pi-user"></i>
          <span>{{ getAccount('tiktok')?.username || 'TikTok Account' }}</span>
          <span class="connected-since">Verbunden seit {{ formatDate(getAccount('tiktok')?.connectedAt) }}</span>
        </div>

        <div class="platform-card-footer">
          <template v-if="isConnected('tiktok')">
            <Button
              label="Trennen"
              icon="pi pi-unlink"
              class="p-button-outlined p-button-danger p-button-sm"
              :loading="disconnecting === 'tiktok'"
              @click="confirmDisconnect('tiktok', 'TikTok')"
            />
          </template>
          <template v-else>
            <Button
              label="Verbinden"
              icon="pi pi-link"
              class="p-button-sm"
              :loading="connecting === 'tiktok'"
              @click="handleTikTokConnect"
            />
          </template>
        </div>
      </div>

      <!-- Instagram -->
      <div class="platform-card" :class="{ connected: isConnected('instagram') }">
        <div class="platform-card-header">
          <div class="platform-brand instagram">
            <i class="pi pi-instagram"></i>
          </div>
          <div class="platform-info">
            <h3>Instagram</h3>
            <p>Videos auf Instagram veröffentlichen</p>
          </div>
          <div class="platform-status" :class="isConnected('instagram') ? 'status-connected' : 'status-disconnected'">
            <i :class="isConnected('instagram') ? 'pi pi-check-circle' : 'pi pi-circle'"></i>
            {{ isConnected('instagram') ? 'Verbunden' : 'Nicht verbunden' }}
          </div>
        </div>

        <div v-if="isConnected('instagram')" class="platform-account-info">
          <i class="pi pi-user"></i>
          <span>{{ getAccount('instagram')?.username || 'Instagram Account' }}</span>
          <span class="connected-since">Verbunden seit {{ formatDate(getAccount('instagram')?.connectedAt) }}</span>
        </div>

        <div class="platform-card-footer">
          <template v-if="isConnected('instagram')">
            <Button
              label="Trennen"
              icon="pi pi-unlink"
              class="p-button-outlined p-button-danger p-button-sm"
              :loading="disconnecting === 'instagram'"
              @click="confirmDisconnect('instagram', 'Instagram')"
            />
          </template>
          <template v-else>
            <Button
              label="Verbinden"
              icon="pi pi-link"
              class="p-button-sm"
              :loading="connecting === 'instagram'"
              @click="handleInstagramConnect"
            />
          </template>
        </div>
      </div>
    </div>

    <!-- YouTube OAuth Dialog -->
    <Dialog
      v-model:visible="showYouTubeDialog"
      header="YouTube verbinden"
      :modal="true"
      :style="{ width: '480px' }"
    >
      <div class="yt-dialog">
        <Message severity="info" :closable="false">
          Lade deine <strong>client_secrets.json</strong> aus der
          <a href="https://console.cloud.google.com/apis/credentials" target="_blank">Google Cloud Console</a> hoch.
        </Message>

        <div class="file-zone" :class="{ 'has-file': youtubeFile }" @click="triggerYtInput" @dragover.prevent @drop.prevent="onYtFileDrop">
          <input ref="ytFileInput" type="file" accept=".json" style="display:none" @change="onYtFileChange" />
          <template v-if="youtubeFile">
            <i class="pi pi-file-check" style="font-size:2rem; color:#10b981"></i>
            <span>{{ youtubeFile.name }}</span>
          </template>
          <template v-else>
            <i class="pi pi-cloud-upload" style="font-size:2rem"></i>
            <span>client_secrets.json hier ablegen oder klicken</span>
          </template>
        </div>
      </div>

      <template #footer>
        <Button label="Abbrechen" class="p-button-text" @click="showYouTubeDialog = false" />
        <Button
          label="Verbinden"
          icon="pi pi-link"
          :loading="connecting === 'youtube'"
          :disabled="!youtubeFile"
          @click="submitYouTubeConnect"
        />
      </template>
    </Dialog>

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import api from '@/services/api';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();
const confirm = useConfirm();

const loading = ref(true);
const connecting = ref<string | null>(null);
const disconnecting = ref<string | null>(null);
const showYouTubeDialog = ref(false);
const youtubeFile = ref<File | null>(null);
const ytFileInput = ref<HTMLInputElement>();

const isConnected = (platform: string) =>
  authStore.user?.connectedPlatforms?.some(p => p.platform === platform) || false;

const getAccount = (platform: string) =>
  authStore.user?.connectedPlatforms?.find(p => p.platform === platform) || null;

const formatDate = (d?: string) => {
  if (!d) return '–';
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
};

// YouTube File Handling
const triggerYtInput = () => ytFileInput.value?.click();
const onYtFileChange = (e: Event) => {
  youtubeFile.value = (e.target as HTMLInputElement).files?.[0] || null;
};
const onYtFileDrop = (e: DragEvent) => {
  youtubeFile.value = e.dataTransfer?.files?.[0] || null;
};

const submitYouTubeConnect = async () => {
  if (!youtubeFile.value || !authStore.userId) return;
  connecting.value = 'youtube';
  try {
    const formData = new FormData();
    formData.append('user_id', authStore.userId);
    formData.append('client_secrets_file', youtubeFile.value);

    const response = await api.post('/api/youtube/connect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    if (response.data.auth_url) {
      window.location.href = response.data.auth_url;
    }
    showYouTubeDialog.value = false;
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || 'YouTube-Verbindung fehlgeschlagen', life: 5000 });
  } finally {
    connecting.value = null;
  }
};

// TikTok Connect
const handleTikTokConnect = async () => {
  if (!authStore.userId) return;
  connecting.value = 'tiktok';
  try {
    const response = await api.post('/api/tiktok/connect', { user_id: authStore.userId });
    if (response.data.auth_url) window.location.href = response.data.auth_url;
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || 'TikTok-Verbindung fehlgeschlagen', life: 5000 });
    connecting.value = null;
  }
};

// Instagram Connect
const handleInstagramConnect = async () => {
  if (!authStore.userId) return;
  connecting.value = 'instagram';
  try {
    const response = await api.post('/api/instagram/connect', { user_id: authStore.userId });
    if (response.data.auth_url) window.location.href = response.data.auth_url;
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || 'Instagram-Verbindung fehlgeschlagen', life: 5000 });
    connecting.value = null;
  }
};

// Disconnect with Confirmation
const confirmDisconnect = (platformId: string, platformName: string) => {
  confirm.require({
    message: `${platformName} wirklich trennen? Du kannst den Account jederzeit wieder verbinden.`,
    header: `${platformName} trennen`,
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Trennen',
    rejectLabel: 'Abbrechen',
    acceptClass: 'p-button-danger',
    accept: () => handleDisconnect(platformId),
  });
};

const handleDisconnect = async (platformId: string) => {
  if (!authStore.userId) return;
  disconnecting.value = platformId;
  try {
    await api.post(`/api/${platformId}/disconnect`, { user_id: authStore.userId });

    if (authStore.user?.connectedPlatforms) {
      authStore.user.connectedPlatforms = authStore.user.connectedPlatforms.filter(
        p => p.platform !== platformId
      );
      localStorage.setItem('user', JSON.stringify(authStore.user));
    }

    toast.add({ severity: 'success', summary: 'Getrennt', detail: `${platformId} wurde getrennt`, life: 3000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || 'Trennen fehlgeschlagen', life: 5000 });
  } finally {
    disconnecting.value = null;
  }
};

// Mount: refresh user + handle OAuth callback
onMounted(async () => {
  try {
    await authStore.refreshUser();
  } catch (e) {
    console.error('Failed to refresh user:', e);
  } finally {
    loading.value = false;
  }

  const success = route.query.success as string | undefined;
  const error = route.query.error as string | undefined;
  const message = route.query.message as string | undefined;

  if (success) {
    toast.add({ severity: 'success', summary: 'Verbunden!', detail: `${success.toUpperCase()} wurde verbunden.`, life: 5000 });
    router.replace({ query: {} });
  }
  if (error) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: message || `${error} konnte nicht verbunden werden.`, life: 5000 });
    router.replace({ query: {} });
  }
});
</script>

<style scoped>
.platforms-view { max-width: 1200px; margin: 0 auto; }

.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 1.75rem; font-weight: 700; color: #1e293b; margin: 0 0 0.25rem 0; }
.subtitle { color: #64748b; font-size: 0.9rem; margin: 0; }

.loading-state { display: flex; justify-content: center; padding: 4rem; }

.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 1.5rem;
}

/* Platform Card */
.platform-card {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.platform-card.connected {
  border-color: #bbf7d0;
  box-shadow: 0 0 0 4px #f0fdf4;
}

.platform-card-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

/* Brand Icons */
.platform-brand {
  width: 52px; height: 52px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem; flex-shrink: 0;
}
.platform-brand.youtube { background: #fff5f5; color: #ef4444; }
.platform-brand.tiktok { background: #f8fafc; color: #1e293b; }
.platform-brand.instagram { background: #fdf2f8; color: #ec4899; }

.platform-info { flex: 1; }
.platform-info h3 { margin: 0 0 0.25rem 0; font-size: 1.0625rem; font-weight: 600; color: #1e293b; }
.platform-info p { margin: 0; font-size: 0.875rem; color: #64748b; }

.platform-status {
  display: flex; align-items: center; gap: 0.375rem;
  font-size: 0.8125rem; font-weight: 600; white-space: nowrap;
  padding: 0.3rem 0.625rem; border-radius: 20px;
}
.status-connected { background: #dcfce7; color: #16a34a; }
.status-disconnected { background: #f1f5f9; color: #94a3b8; }

/* Account Info */
.platform-account-info {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.75rem 1rem; background: #f8fafc; border-radius: 8px;
  font-size: 0.875rem; color: #475569;
}
.platform-account-info i { color: #94a3b8; }
.connected-since { margin-left: auto; font-size: 0.75rem; color: #94a3b8; }

.platform-card-footer { display: flex; justify-content: flex-end; }

/* YT Dialog */
.yt-dialog { display: flex; flex-direction: column; gap: 1.25rem; }

.file-zone {
  border: 2px dashed #e2e8f0; border-radius: 10px;
  padding: 1.75rem; text-align: center; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
  color: #94a3b8; transition: all 0.2s;
}
.file-zone:hover { border-color: #6366f1; background: #f8f7ff; }
.file-zone.has-file { border-color: #10b981; background: #f0fdf4; color: #15803d; }

@media (max-width: 768px) {
  .platforms-grid { grid-template-columns: 1fr; }
}
</style>
