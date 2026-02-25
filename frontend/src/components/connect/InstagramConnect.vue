<template>
  <Card class="platform-connect-card instagram">
    <template #header>
      <div class="platform-header">
        <i class="pi pi-instagram"></i>
        <h3>Instagram</h3>
      </div>
    </template>

    <template #content>
      <p class="description">
        Verbinde dein Instagram Business-Konto, um Reels zu posten.
      </p>

      <div class="status-section">
        <div class="status-badge">
          <Badge 
            :value="isConnected ? 'Verbunden' : 'Nicht verbunden'" 
            :severity="isConnected ? 'success' : 'warning'"
          />
        </div>

        <div v-if="isConnected" class="connection-info">
          <p><strong>Account:</strong> @{{ username || 'Unbekannt' }}</p>
          <p><strong>Letzte Synchronisierung:</strong> {{ lastSync }}</p>
        </div>
      </div>

      <Divider />

      <div class="instructions" v-if="!isConnected">
        <h4>Voraussetzungen:</h4>
        <ul>
          <li>Du benötigst ein Instagram <strong>Business</strong> oder <strong>Creator</strong> Konto</li>
          <li>Dein Instagram muss mit einer Facebook-Seite verbunden sein</li>
          <li>Du brauchst eine Facebook App mit Instagram Graph API</li>
        </ul>

        <Message severity="warn" :closable="false">
          Private Instagram-Konten werden nicht unterstützt
        </Message>
      </div>

      <div class="actions">
        <Button
          v-if="!isConnected"
          label="Mit Instagram verbinden"
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
import Message from 'primevue/message';
import { usePlatformStore } from '@/stores/platformStore';
import { useAuthStore } from '@/stores/authStore';
import { connectInstagram } from '@/services/api';
import { formatRelativeTime } from '@/utils/formatters';

const toast = useToast();
const platformStore = usePlatformStore();
const authStore = useAuthStore();

const connecting = ref(false);
const disconnecting = ref(false);

const isConnected = computed(() => platformStore.isConnected('instagram'));
const connectionStatus = computed(() => platformStore.getConnectionStatus('instagram'));
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
    const response = await connectInstagram(authStore.userId);

    // Öffne OAuth URL
    if (response.auth_url) {
      toast.add({
        severity: 'info',
        summary: 'Instagram Authentifizierung',
        detail: 'Du wirst zu Facebook weitergeleitet...',
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
      detail: 'Instagram-Verbindung fehlgeschlagen',
      life: 5000
    });
  } finally {
    connecting.value = false;
  }
};

const handleDisconnect = async () => {
  disconnecting.value = true;

  try {
    await platformStore.disconnectPlatform('instagram');

    toast.add({
      severity: 'success',
      summary: 'Getrennt',
      detail: 'Instagram wurde erfolgreich getrennt',
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
  background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
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
  margin-bottom: 1rem;
}

.instructions h4 {
  margin-top: 0;
  color: var(--primary-700);
}

.instructions ul {
  margin: 0;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
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
