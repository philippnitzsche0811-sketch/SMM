<template>
  <Card class="platform-connect-card tiktok">
    <template #header>
      <div class="platform-header">
        <i class="pi pi-video"></i>
        <h3>TikTok</h3>
      </div>
    </template>

    <template #content>
      <p class="description">
        Verbinde dein TikTok-Konto, um kurze Videos zu teilen.
      </p>

      <div class="status-section">
        <div class="status-badge">
          <Badge 
            :value="isConnected ? 'Verbunden' : 'Nicht verbunden'" 
            :severity="isConnected ? 'success' : 'warning'"
          />
        </div>

        <div v-if="isConnected" class="connection-info">
          <p><strong>Username:</strong> @{{ username || 'Unbekannt' }}</p>
          <p><strong>Letzte Synchronisierung:</strong> {{ lastSync }}</p>
        </div>
      </div>

      <Divider />

      <div class="instructions" v-if="!isConnected">
        <h4>Hinweise:</h4>
        <ul>
          <li>Du benötigst ein TikTok Developer Account</li>
          <li>Deine App muss "Content Posting API" aktiviert haben</li>
          <li>Die OAuth-Autorisierung öffnet sich in einem neuen Fenster</li>
        </ul>
      </div>

      <div class="actions">
        <Button
          v-if="!isConnected"
          label="Mit TikTok verbinden"
          icon="pi pi-sign-in"
          @click="handleConnect"
          :loading="connecting"
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
import { usePlatformStore } from '@/stores/platformStore';
import { useAuthStore } from '@/stores/authStore';
import { connectTikTok } from '@/services/api';
import { formatRelativeTime } from '@/utils/formatters';

const toast = useToast();
const platformStore = usePlatformStore();
const authStore = useAuthStore();

const connecting = ref(false);
const disconnecting = ref(false);

const isConnected = computed(() => platformStore.isConnected('tiktok'));
const connectionStatus = computed(() => platformStore.getConnectionStatus('tiktok'));
const username = computed(() => connectionStatus.value?.username);
const lastSync = computed(() => 
  connectionStatus.value?.lastSync 
    ? formatRelativeTime(connectionStatus.value.lastSync)
    : 'Nie'
);

const handleConnect = async () => {
  if (!authStore.userId) return;

  connecting.value = true;

  try {
    const response = await connectTikTok(authStore.userId);

    // Öffne OAuth URL
    if (response.auth_url) {
      toast.add({
        severity: 'info',
        summary: 'TikTok Authentifizierung',
        detail: 'Du wirst zu TikTok weitergeleitet...',
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
      detail: 'TikTok-Verbindung fehlgeschlagen',
      life: 5000
    });
  } finally {
    connecting.value = false;
  }
};

const handleDisconnect = async () => {
  disconnecting.value = true;

  try {
    await platformStore.disconnectPlatform('tiktok');

    toast.add({
      severity: 'success',
      summary: 'Getrennt',
      detail: 'TikTok wurde erfolgreich getrennt',
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
  background: linear-gradient(135deg, #000000 0%, #333333 100%);
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

.instructions ul {
  margin: 0;
  padding-left: 1.5rem;
}

.instructions li {
  margin: 0.5rem 0;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}
</style>
