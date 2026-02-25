<template>
  <div class="platforms-view">
    <div class="platforms-header">
      <h2>Plattformen verwalten</h2>
      <p class="subtitle">Verbinde deine Social Media Accounts, um Videos hochzuladen</p>
    </div>

    <!-- Platforms Grid -->
    <div class="platforms-grid">
      <!-- YouTube -->
      <PlatformCard
        :platform="platforms.youtube"
        :connected-data="getConnectedPlatform('youtube')"
        @connect="handleYouTubeConnect"
        @disconnect="handleDisconnect('youtube')"
        @reconnect="handleYouTubeConnect"
      />

      <!-- TikTok -->
      <PlatformCard
        :platform="platforms.tiktok"
        :connected-data="getConnectedPlatform('tiktok')"
        @connect="handleTikTokConnect"
        @disconnect="handleDisconnect('tiktok')"
        @reconnect="handleTikTokConnect"
      />

      <!-- Instagram -->
      <PlatformCard
        :platform="platforms.instagram"
        :connected-data="getConnectedPlatform('instagram')"
        @connect="handleInstagramConnect"
        @disconnect="handleDisconnect('instagram')"
        @reconnect="handleInstagramConnect"
      />
    </div>

    <!-- YouTube File Upload Dialog -->
    <Dialog 
      v-model:visible="showYouTubeDialog" 
      header="YouTube verbinden"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="youtube-connect-dialog">
        <Message severity="info" :closable="false">
          <div class="info-content">
            <i class="pi pi-info-circle"></i>
            <div>
              <strong>Client Secrets benötigt</strong>
              <p>Lade deine <code>client_secrets.json</code> Datei hoch. Diese bekommst du in der Google Cloud Console.</p>
            </div>
          </div>
        </Message>

        <div class="file-upload-section">
          <FileUpload
            ref="fileUpload"
            mode="basic"
            accept=".json"
            :maxFileSize="1000000"
            :auto="false"
            chooseLabel="JSON-Datei auswählen"
            @select="handleYouTubeFileSelect"
          />

          <div v-if="youtubeFile" class="selected-file">
            <i class="pi pi-file"></i>
            <span>{{ youtubeFile.name }}</span>
            <Button 
              icon="pi pi-times" 
              class="p-button-text p-button-sm"
              @click="clearYouTubeFile"
            />
          </div>
        </div>

        <a 
          href="https://console.cloud.google.com/apis/credentials" 
          target="_blank"
          class="help-link"
        >
          <i class="pi pi-external-link"></i>
          Wie bekomme ich die Client Secrets?
        </a>
      </div>

      <template #footer>
        <Button 
          label="Abbrechen" 
          icon="pi pi-times"
          class="p-button-text"
          @click="showYouTubeDialog = false"
        />
        <Button 
          label="Verbinden" 
          icon="pi pi-link"
          :loading="connecting"
          :disabled="!youtubeFile"
          @click="submitYouTubeConnect"
        />
      </template>
    </Dialog>

    <!-- Toast für Benachrichtigungen -->
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import * as api from '@/services/api';
import PlatformCard from '@/components/platform/PlatformCard.vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import FileUpload from 'primevue/fileupload';
import Message from 'primevue/message';
import Toast from 'primevue/toast';
import { connectYouTube, connectTikTok, connectInstagram, disconnectPlatform } from '@/services/api';


const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const toast = useToast();

const connecting = ref(false);
const showYouTubeDialog = ref(false);
const youtubeFile = ref<File | null>(null);

// Platform Definitions
const platforms = {
  youtube: {
    id: 'youtube',
    name: 'YouTube',
    icon: 'pi pi-youtube',
    color: '#FF0000',
    description: 'Verbinde deinen YouTube Kanal, um Videos direkt hochzuladen.'
  },
  tiktok: {
    id: 'tiktok',
    name: 'TikTok',
    icon: 'pi pi-video',
    color: '#000000',
    description: 'Verbinde dein TikTok Profil, um kurze Videos zu teilen.'
  },
  instagram: {
    id: 'instagram',
    name: 'Instagram',
    icon: 'pi pi-instagram',
    color: '#E4405F',
    description: 'Verbinde dein Instagram Business Account für Video-Posts.'
  }
};

// Get connected platform data
const getConnectedPlatform = (platformId: string) => {
  return authStore.user?.connectedPlatforms?.find(
    (p) => p.platform === platformId
  ) || null;
};

// YouTube Connect
const handleYouTubeConnect = () => {
  showYouTubeDialog.value = true;
};

const handleYouTubeFileSelect = (event: any) => {
  console.log('📁 File select event:', event);
  
  // PrimeVue FileUpload gibt files in event.files zurück
  if (event.files && event.files.length > 0) {
    youtubeFile.value = event.files[0];
    console.log('✅ File selected:', youtubeFile.value.name);
  } else {
    console.error('❌ No files in event');
  }
};


const clearYouTubeFile = () => {
  youtubeFile.value = null;
};

const submitYouTubeConnect = async () => {
  if (!youtubeFile.value || !authStore.userId) return;

  connecting.value = true;
  try {
    // ✅ Verwende die dedizierte API Funktion!
    const response = await connectYouTube(authStore.userId, youtubeFile.value);

    // Redirect zu OAuth URL
    if (response.auth_url) {
      window.location.href = response.auth_url;
      
      toast.add({
        severity: 'info',
        summary: 'Authentifizierung gestartet',
        detail: 'Du wirst zu Google weitergeleitet...',
        life: 3000
      });
    }

    showYouTubeDialog.value = false;
    youtubeFile.value = null;

  } catch (error: any) {
    console.error('YouTube connect error:', error);
    toast.add({
      severity: 'error',
      summary: 'Verbindung fehlgeschlagen',
      detail: error.response?.data?.detail || 'YouTube konnte nicht verbunden werden.',
      life: 5000
    });
  } finally {
    connecting.value = false;
  }
};



// TikTok Connect (OAuth)
const handleTikTokConnect = async () => {
  if (!authStore.userId) return;

  connecting.value = true;
  try {
    const response = await api.connectTikTok(authStore.userId);

    if (response.auth_url) {
      window.location.href = response.auth_url;
    }
  } catch (error: any) {
    console.error('TikTok connect error:', error);
    toast.add({
      severity: 'error',
      summary: 'Verbindung fehlgeschlagen',
      detail: error.response?.data?.detail || 'TikTok konnte nicht verbunden werden.',
      life: 5000
    });
    connecting.value = false;
  }
};

// Instagram Connect (OAuth)
const handleInstagramConnect = async () => {
  if (!authStore.userId) return;

  connecting.value = true;
  try {
    const response = await api.connectInstagram(authStore.userId);

    if (response.auth_url) {
      window.location.href = response.auth_url;
    }
  } catch (error: any) {
    console.error('Instagram connect error:', error);
    toast.add({
      severity: 'error',
      summary: 'Verbindung fehlgeschlagen',
      detail: error.response?.data?.detail || 'Instagram konnte nicht verbunden werden.',
      life: 5000
    });
    connecting.value = false;
  }
};

// Disconnect Platform
const handleDisconnect = async (platformId: string) => {
  if (!authStore.userId) return;

  try {
    await api.disconnectPlatform(authStore.userId, platformId);

    // Update local state
    if (authStore.user?.connectedPlatforms) {
      authStore.user.connectedPlatforms = authStore.user.connectedPlatforms.filter(
        (p) => p.platform !== platformId
      );
    }

    toast.add({
      severity: 'success',
      summary: 'Getrennt',
      detail: `${platforms[platformId as keyof typeof platforms].name} wurde getrennt.`,
      life: 3000
    });
  } catch (error: any) {
    console.error('Disconnect error:', error);
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Trennung fehlgeschlagen.',
      life: 5000
    });
  }
};

// Check for OAuth callback success/error
onMounted(async () => {
  const success = route.query.success as string | undefined;
  const error = route.query.error as string | undefined;
  const message = route.query.message as string | undefined;

  if (success) {
    console.log('✅ OAuth Success detected for:', success);
    
    // 🆕 Refresh User Data from Backend
    try {
      await authStore.refreshUser();
      
      toast.add({
        severity: 'success',
        summary: 'Erfolgreich verbunden!',
        detail: `${success.toUpperCase()} wurde erfolgreich verbunden.`,
        life: 5000
      });
    } catch (error) {
      console.error('Failed to refresh user data after OAuth:', error);
    }

    // Remove query params
    router.replace({ query: {} });
  }

  if (error) {
    console.error('❌ OAuth Error:', error, message);
    
    toast.add({
      severity: 'error',
      summary: 'Verbindung fehlgeschlagen',
      detail: message || `${error} konnte nicht verbunden werden.`,
      life: 5000
    });

    router.replace({ query: {} });
  }
});

</script>

<style scoped>
.platforms-view {
  max-width: 1400px;
  margin: 0 auto;
}

.platforms-header {
  margin-bottom: 2rem;
}

.platforms-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #64748b;
  font-size: 1rem;
}

.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.youtube-connect-dialog {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-content {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.info-content i {
  font-size: 1.5rem;
  margin-top: 0.25rem;
}

.info-content p {
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
}

.info-content code {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-family: monospace;
}

.file-upload-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.selected-file i {
  color: #3b82f6;
  font-size: 1.25rem;
}

.selected-file span {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
}

.help-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.help-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .platforms-grid {
    grid-template-columns: 1fr;
  }
}
</style>

