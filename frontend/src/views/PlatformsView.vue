<template>
  <div class="platforms-view">
    <div class="page-header">
      <h1>Connected Platforms</h1>
      <p class="subtitle">Connect your social media accounts to start publishing videos</p>
    </div>

    <div v-if="loading" class="loading-state">
      <ProgressSpinner />
    </div>

    <div v-else class="platforms-grid">
      <!-- YouTube -->
      <div class="platform-card" :class="{ connected: isConnected('youtube') }">
        <div class="platform-card-header">
          <div class="platform-brand youtube"><i class="pi pi-youtube"></i></div>
          <div class="platform-info">
            <h3>YouTube</h3>
            <p>Upload videos to your channel</p>
          </div>
          <div class="platform-status" :class="isConnected('youtube') ? 'status-connected' : 'status-disconnected'">
            <i :class="isConnected('youtube') ? 'pi pi-check-circle' : 'pi pi-circle'"></i>
            {{ isConnected('youtube') ? 'Connected' : 'Not connected' }}
          </div>
        </div>

        <div v-if="isConnected('youtube')" class="platform-account-info">
          <i class="pi pi-user"></i>
          <span>{{ getAccount('youtube')?.username || getAccount('youtube')?.channelId || 'YouTube Account' }}</span>
          <span class="connected-since">Connected {{ formatDate(getAccount('youtube')?.connectedAt) }}</span>
        </div>

        <div class="platform-card-footer">
          <template v-if="isConnected('youtube')">
            <Button label="Disconnect" icon="pi pi-unlink" severity="danger" outlined size="small" :loading="disconnecting === 'youtube'" @click="confirmDisconnect('youtube', 'YouTube')" />
          </template>
          <template v-else>
            <Button label="Connect" icon="pi pi-link" size="small" :loading="connecting === 'youtube'" @click="showYouTubeDialog = true" />
          </template>
        </div>
      </div>

      <!-- TikTok -->
      <div class="platform-card" :class="{ connected: isConnected('tiktok') }">
        <div class="platform-card-header">
          <div class="platform-brand tiktok"><i class="pi pi-video"></i></div>
          <div class="platform-info">
            <h3>TikTok</h3>
            <p>Share short-form videos</p>
          </div>
          <div class="platform-status" :class="isConnected('tiktok') ? 'status-connected' : 'status-disconnected'">
            <i :class="isConnected('tiktok') ? 'pi pi-check-circle' : 'pi pi-circle'"></i>
            {{ isConnected('tiktok') ? 'Connected' : 'Not connected' }}
          </div>
        </div>

        <div v-if="isConnected('tiktok')" class="platform-account-info">
          <i class="pi pi-user"></i>
          <span>{{ getAccount('tiktok')?.username || 'TikTok Account' }}</span>
          <span class="connected-since">Connected {{ formatDate(getAccount('tiktok')?.connectedAt) }}</span>
        </div>

        <div class="platform-card-footer">
          <template v-if="isConnected('tiktok')">
            <Button label="Disconnect" icon="pi pi-unlink" severity="danger" outlined size="small" :loading="disconnecting === 'tiktok'" @click="confirmDisconnect('tiktok', 'TikTok')" />
          </template>
          <template v-else>
            <Button label="Connect" icon="pi pi-link" size="small" :loading="connecting === 'tiktok'" @click="handleTikTokConnect" />
          </template>
        </div>
      </div>

      <!-- Instagram -->
      <div class="platform-card" :class="{ connected: isConnected('instagram') }">
        <div class="platform-card-header">
          <div class="platform-brand instagram"><i class="pi pi-instagram"></i></div>
          <div class="platform-info">
            <h3>Instagram</h3>
            <p>Publish Reels and grow your following</p>
          </div>
          <div class="platform-status" :class="isConnected('instagram') ? 'status-connected' : 'status-disconnected'">
            <i :class="isConnected('instagram') ? 'pi pi-check-circle' : 'pi pi-circle'"></i>
            {{ isConnected('instagram') ? 'Connected' : 'Not connected' }}
          </div>
        </div>

        <div v-if="isConnected('instagram')" class="platform-account-info">
          <i class="pi pi-user"></i>
          <span>{{ getAccount('instagram')?.username || 'Instagram Account' }}</span>
          <span class="connected-since">Connected {{ formatDate(getAccount('instagram')?.connectedAt) }}</span>
        </div>

        <div class="platform-card-footer">
          <template v-if="isConnected('instagram')">
            <Button label="Disconnect" icon="pi pi-unlink" severity="danger" outlined size="small" :loading="disconnecting === 'instagram'" @click="confirmDisconnect('instagram', 'Instagram')" />
          </template>
          <template v-else>
            <Button label="Connect" icon="pi pi-link" size="small" :loading="connecting === 'instagram'" @click="handleInstagramConnect" />
          </template>
        </div>
      </div>
    </div>

    <!-- YouTube OAuth Dialog -->
    <Dialog v-model:visible="showYouTubeDialog" header="Connect YouTube" :modal="true" :style="{ width: '480px' }">
      <div class="yt-dialog">
        <Message severity="info" :closable="false">
          Upload your <strong>client_secrets.json</strong> from the
          <a href="https://console.cloud.google.com/apis/credentials" target="_blank">Google Cloud Console</a>.
        </Message>

        <div class="file-zone" :class="{ 'has-file': youtubeFile }" @click="triggerYtInput" @dragover.prevent @drop.prevent="onYtFileDrop">
          <input ref="ytFileInput" type="file" accept=".json" style="display:none" @change="onYtFileChange" />
          <template v-if="youtubeFile">
            <i class="pi pi-file-check" style="font-size:2rem;color:#10b981"></i>
            <span>{{ youtubeFile.name }}</span>
          </template>
          <template v-else>
            <i class="pi pi-cloud-upload" style="font-size:2rem"></i>
            <span>Drop client_secrets.json here or click to browse</span>
          </template>
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="showYouTubeDialog = false" />
        <Button label="Connect" icon="pi pi-link" :loading="connecting === 'youtube'" :disabled="!youtubeFile" @click="submitYouTubeConnect" />
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

const route    = useRoute();
const router   = useRouter();
const authStore = useAuthStore();
const toast    = useToast();
const confirm  = useConfirm();

const loading           = ref(true);
const connecting        = ref<string | null>(null);
const disconnecting     = ref<string | null>(null);
const showYouTubeDialog = ref(false);
const youtubeFile       = ref<File | null>(null);
const ytFileInput       = ref<HTMLInputElement>();

const isConnected = (platform: string) =>
  authStore.user?.connectedPlatforms?.some((p: any) => p.platform === platform) || false;

const getAccount = (platform: string) =>
  authStore.user?.connectedPlatforms?.find((p: any) => p.platform === platform) || null;

const formatDate = (d?: string) => {
  if (!d) return '';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const triggerYtInput  = () => ytFileInput.value?.click();
const onYtFileChange  = (e: Event) => { youtubeFile.value = (e.target as HTMLInputElement).files?.[0] || null; };
const onYtFileDrop    = (e: DragEvent) => { youtubeFile.value = e.dataTransfer?.files?.[0] || null; };

const submitYouTubeConnect = async () => {
  if (!youtubeFile.value || !authStore.userId) return;
  connecting.value = 'youtube';
  try {
    const fd = new FormData();
    fd.append('user_id', authStore.userId);
    fd.append('client_secrets_file', youtubeFile.value);
    const res = await api.post('/api/youtube/connect', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
    if (res.data.auth_url) window.location.href = res.data.auth_url;
    showYouTubeDialog.value = false;
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'YouTube connection failed', life: 5000 });
  } finally { connecting.value = null; }
};

const handleTikTokConnect = async () => {
  if (!authStore.userId) return;
  connecting.value = 'tiktok';
  try {
    const res = await api.post('/api/tiktok/connect', { user_id: authStore.userId });
    if (res.data.auth_url) window.location.href = res.data.auth_url;
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'TikTok connection failed', life: 5000 });
    connecting.value = null;
  }
};

const handleInstagramConnect = async () => {
  if (!authStore.userId) return;
  connecting.value = 'instagram';
  try {
    const res = await api.post('/api/instagram/connect', { user_id: authStore.userId });
    if (res.data.auth_url) window.location.href = res.data.auth_url;
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Instagram connection failed', life: 5000 });
    connecting.value = null;
  }
};

const confirmDisconnect = (platformId: string, platformName: string) => {
  confirm.require({
    message: `Disconnect ${platformName}? You can reconnect at any time.`,
    header:  `Disconnect ${platformName}`,
    icon:    'pi pi-exclamation-triangle',
    acceptLabel: 'Disconnect',
    rejectLabel: 'Cancel',
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
      authStore.user.connectedPlatforms = authStore.user.connectedPlatforms.filter((p: any) => p.platform !== platformId);
      localStorage.setItem('user', JSON.stringify(authStore.user));
    }
    toast.add({ severity: 'success', summary: 'Disconnected', detail: `${platformId} was disconnected`, life: 3000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Disconnect failed', life: 5000 });
  } finally { disconnecting.value = null; }
};

onMounted(async () => {
  try { await authStore.refreshUser(); }
  catch (e) { console.error('Failed to refresh user:', e); }
  finally { loading.value = false; }

  const success = route.query.success as string | undefined;
  const error   = route.query.error   as string | undefined;
  const message = route.query.message as string | undefined;

  if (success) {
    toast.add({ severity: 'success', summary: 'Connected!', detail: `${success.toUpperCase()} connected successfully.`, life: 5000 });
    router.replace({ query: {} });
  }
  if (error) {
    toast.add({ severity: 'error', summary: 'Connection failed', detail: message || `Could not connect ${error}.`, life: 5000 });
    router.replace({ query: {} });
  }
});
</script>

<style scoped>
.platforms-view { max-width: 1100px; margin: 0 auto; }

.page-header { margin-bottom: 1.75rem; }
.page-header h1 { font-size: 1.625rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.2rem; }
.subtitle { color: var(--text-secondary); font-size: 0.875rem; margin: 0; }

.loading-state { display: flex; justify-content: center; padding: 4rem; }

.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
}

.platform-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.platform-card.connected {
  border-color: #bbf7d0;
  box-shadow: 0 0 0 3px #f0fdf4;
}

.platform-card-header {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
}

.platform-brand {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.375rem; flex-shrink: 0;
}
.platform-brand.youtube   { background: #fff5f5; color: #ef4444; }
.platform-brand.tiktok    { background: #f8fafc; color: #1e293b; }
.platform-brand.instagram { background: #fdf2f8; color: #ec4899; }

.platform-info { flex: 1; }
.platform-info h3 { margin: 0 0 0.2rem; font-size: 1rem; font-weight: 600; color: var(--text-primary); }
.platform-info p  { margin: 0; font-size: 0.8125rem; color: var(--text-secondary); }

.platform-status {
  display: flex; align-items: center; gap: 0.35rem;
  font-size: 0.78rem; font-weight: 600; white-space: nowrap;
  padding: 0.25rem 0.6rem; border-radius: 99px;
}
.status-connected    { background: #dcfce7; color: #16a34a; }
.status-disconnected { background: var(--bg-tertiary); color: var(--text-disabled); }

.platform-account-info {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.625rem 0.875rem; background: var(--bg-secondary);
  border-radius: var(--radius-md); font-size: 0.8125rem; color: var(--text-secondary);
}
.platform-account-info i { color: var(--text-disabled); }
.connected-since { margin-left: auto; font-size: 0.75rem; color: var(--text-disabled); }

.platform-card-footer { display: flex; justify-content: flex-end; }

/* YouTube dialog */
.yt-dialog { display: flex; flex-direction: column; gap: 1.125rem; }
.file-zone {
  border: 2px dashed var(--border-color); border-radius: var(--radius-lg);
  padding: 1.75rem; text-align: center; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
  color: var(--text-disabled); transition: all 0.2s;
}
.file-zone:hover { border-color: var(--primary-400); background: var(--primary-50); }
.file-zone.has-file { border-color: #10b981; background: #f0fdf4; color: #15803d; }

@media (max-width: 768px) {
  .platforms-grid { grid-template-columns: 1fr; }
}
</style>
