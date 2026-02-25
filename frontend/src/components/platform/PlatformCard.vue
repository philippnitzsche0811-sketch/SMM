<template>
  <Card class="platform-card" :class="{ 'connected': isConnected }">
    <template #header>
      <div class="platform-card-header">
        <div class="platform-icon-wrapper" :style="{ backgroundColor: platform.color + '20' }">
          <i :class="platform.icon" :style="{ color: platform.color }"></i>
        </div>
        <div class="platform-info">
          <h3>{{ platform.name }}</h3>
          <Tag 
            :value="statusText" 
            :severity="statusSeverity"
            size="small"
          />
        </div>
      </div>
    </template>

    <template #content>
      <div class="platform-details">
        <!-- Connected Info -->
        <div v-if="isConnected && connectedData" class="connected-info">
          <div class="info-row">
            <span class="info-label">Account:</span>
            <span class="info-value">{{ connectedData.account_id || 'Verbunden' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Verbunden seit:</span>
            <span class="info-value">{{ formatDate(connectedData.connected_at) }}</span>
          </div>
        </div>

        <!-- Not Connected Info -->
        <div v-else class="not-connected-info">
          <p>{{ platform.description }}</p>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="platform-actions">
        <Button 
          v-if="!isConnected"
          :label="`${platform.name} verbinden`"
          icon="pi pi-link"
          class="p-button-primary"
          :loading="loading"
          @click="handleConnect"
        />
        <div v-else class="connected-actions">
          <Button 
            label="Neu verbinden"
            icon="pi pi-refresh"
            outlined
            :loading="loading"
            @click="handleReconnect"
          />
          <Button 
            label="Trennen"
            icon="pi pi-times"
            severity="danger"
            outlined
            :loading="loading"
            @click="handleDisconnect"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Tag from 'primevue/tag';

interface Platform {
  id: string;
  name: string;
  icon: string;
  color: string;
  description: string;
}

interface ConnectedPlatform {
  platform: string;
  account_id?: string;
  connected_at?: string;
}

const props = defineProps<{
  platform: Platform;
  connectedData?: ConnectedPlatform | null;
}>();

const emit = defineEmits<{
  connect: [];
  disconnect: [];
  reconnect: [];
}>();

const loading = ref(false);

const isConnected = computed(() => !!props.connectedData);

const statusText = computed(() => 
  isConnected.value ? 'Verbunden' : 'Nicht verbunden'
);

const statusSeverity = computed(() => 
  isConnected.value ? 'success' : 'warn'
);

const formatDate = (dateString?: string) => {
  if (!dateString) return 'Kürzlich';
  
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Heute';
    if (diffDays === 1) return 'Gestern';
    if (diffDays < 7) return `Vor ${diffDays} Tagen`;
    
    return date.toLocaleDateString('de-DE', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  } catch {
    return 'Kürzlich';
  }
};

const handleConnect = () => {
  emit('connect');
};

const handleDisconnect = () => {
  emit('disconnect');
};

const handleReconnect = () => {
  emit('reconnect');
};
</script>

<style scoped>
.platform-card {
  transition: all 0.3s;
  border: 2px solid transparent;
  height: 100%;
}

.platform-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.platform-card.connected {
  border-color: #10b981;
  background: linear-gradient(to bottom, rgba(16, 185, 129, 0.02), transparent);
}

.platform-card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
}

.platform-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.platform-icon-wrapper i {
  font-size: 2rem;
}

.platform-info {
  flex: 1;
}

.platform-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.platform-details {
  min-height: 80px;
}

.connected-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-weight: 500;
  color: #64748b;
  font-size: 0.875rem;
}

.info-value {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.875rem;
}

.not-connected-info p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.5;
}

.platform-actions {
  display: flex;
  gap: 0.5rem;
}

.platform-actions button {
  width: 100%;
}

.connected-actions {
  display: flex;
  gap: 0.5rem;
  width: 100%;
}

.connected-actions button {
  flex: 1;
}

@media (max-width: 768px) {
  .platform-card-header {
    flex-direction: column;
    text-align: center;
  }

  .connected-actions {
    flex-direction: column;
  }
}
</style>
