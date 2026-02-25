<template>
  <Card class="platform-connect-card youtube">
    <template #header>
      <div class="platform-header">
        <i class="pi pi-youtube"></i>
        <h3>YouTube</h3>
      </div>
    </template>

    <template #content>
      <p class="description">
        Verbinde deinen YouTube-Kanal, um Videos direkt hochzuladen.
      </p>

      <div class="status-section">
        <div class="status-badge">
          <Badge 
            :value="isConnected ? 'Verbunden' : 'Nicht verbunden'" 
            :severity="isConnected ? 'success' : 'warning'"
          />
        </div>

        <div v-if="isConnected" class="connection-info">
          <p><strong>Kanal:</strong> {{ channelName || 'Unbekannt' }}</p>
          <p><strong>Letzte Synchronisierung:</strong> {{ lastSync }}</p>
        </div>
      </div>

      <Divider />

      <div class="instructions" v-if="!isConnected">
        <h4>So funktioniert's:</h4>
        <ol>
          <li>Gehe zur <a href="https://console.cloud.google.com/" target="_blank">Google Cloud Console</a></li>
          <li>Erstelle ein neues Projekt oder wähle ein bestehendes</li>
          <li>Aktiviere die YouTube Data API v3</li>
          <li>Erstelle OAuth 2.0 Credentials</li>
          <li>Lade die <code>client_secret.json</code> herunter</li>
          <li>Lade sie hier hoch</li>
        </ol>
      </div>

      <div class="actions">
        <FileUpload
          v-if="!isConnected"
          mode="basic"
          accept="application/json"
          :maxFileSize="1000000"
          chooseLabel="Client Secret hochladen"
          customUpload
          @uploader="handleUpload"
          :auto="false"
          :disabled="uploading"
        />

        <Button 
          v-else
          label="Trennen"
          severity="danger"
          icon="pi pi-times"
          @click="handleDisconnect"
          :loading="disconnecting"
        />
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Badge from 'primevue/badge';
import Divider from 'primevue/divider';
import FileUpload from 'primevue/fileupload';
import { usePlatformStore } from '@/stores/platformStore';
import { useAuthStore } from '@/stores/authStore';
import { connectYouTube } from '@/services/api';
import { formatRelativeTime } from '@/utils/formatters';

const toast = useToast();
const platformStore = usePlatformStore();
const authStore = useAuthStore();

const uploading = ref(false);
const disconnecting = ref(false);

const isConnected = computed(() => platformStore.isConnected('youtube'));
const connectionStatus = computed(() => platformStore.getConnectionStatus('youtube'));
const channelName = computed(() => connectionStatus.value?.username);
const lastSync = computed(() => 
  connectionStatus.value?.lastSync 
    ? formatRelativeTime(connectionStatus.value.lastSync)
    : 'Nie'
);

const handleUpload = async (event: any) => {
  const file = event.files[0];
  if (!file || !authStore.userId) return;

  uploading.value = true;

  try {
    const response = await connectYouTube(authStore.userId, file);

    // Öffne OAuth URL
    if (response.auth_url) {
      toast.add({
        severity: 'info',
        summary: 'YouTube Authentifizierung',
        detail: 'Du wirst zur Google-Anmeldung weitergeleitet...',
        life: 3000
      });

      setTimeout(() => {
        window.location.href = response.auth_url;
      }, 1000);
    }
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'YouTube-Verbindung fehlgeschlagen',
      life: 5000
    });
  } finally {
    uploading.value = false;
  }
};

const handleDisconnect = async () => {
  disconnecting.value = true;

  try {
    await platformStore.disconnectPlatform('youtube');

    toast.add({
      severity: 'success',
      summary: 'Getrennt',
      detail: 'YouTube wurde erfolgreich getrennt',
      life: 3000
    });
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Trennen fehlgeschlagen',
      life: 5000
    });
  } finally {
    disconnecting.value = false;
  }
};
</script>

<style scoped>
.platform-connect-card {
  height: 100%;
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%);
  color: white;
}

.platform-header i {
  font-size: 2.5rem;
}

.platform-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.description {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.status-section {
  margin-bottom: 1rem;
}

.status-badge {
  margin-bottom: 1rem;
}

.connection-info {
  background: var(--bg-secondary);
  padding: 1rem;
  border-radius: var(--radius-md);
}

.connection-info p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.instructions {
  background: var(--info-50);
  padding: 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
}

.instructions h4 {
  margin-top: 0;
  color: var(--primary-700);
}

.instructions ol {
  margin: 0;
  padding-left: 1.5rem;
}

.instructions li {
  margin: 0.5rem 0;
}

.instructions a {
  color: var(--primary-600);
  text-decoration: underline;
}

.instructions code {
  background: white;
  padding: 0.2rem 0.4rem;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}
</style>
