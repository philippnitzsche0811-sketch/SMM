<template>
  <Card class="platform-card" :class="{ 'connected': isConnected }">
    <template #content>
      <div class="platform-content">
        <!-- Platform Icon & Info -->
        <div class="platform-header">
          <div class="platform-icon" :style="{ background: platformColor + '15' }">
            <i :class="platformIcon" :style="{ color: platformColor }"></i>
          </div>
          <div class="platform-info">
            <h3>{{ platformName }}</h3>
            <span v-if="isConnected" class="status-badge connected">
              <i class="pi pi-check-circle"></i>
              Verbunden
            </span>
            <span v-else class="status-badge not-connected">
              <i class="pi pi-times-circle"></i>
              Nicht verbunden
            </span>
          </div>
        </div>

        <!-- Stats (if connected) -->
        <div v-if="isConnected && stats" class="platform-stats">
          <div class="stat-item">
            <span class="stat-label">Videos</span>
            <span class="stat-value">{{ stats.videos || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Aufrufe</span>
            <span class="stat-value">{{ formatNumber(stats.views || 0) }}</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="platform-actions">
          <Button
            v-if="!isConnected"
            :label="`${platformName} verbinden`"
            :icon="connecting ? 'pi pi-spin pi-spinner' : 'pi pi-link'"
            :loading="connecting"
            :style="{ background: platformColor, borderColor: platformColor }"
            @click="handleConnect"
          />
          <template v-else>
            <Button
              label="Trennen"
              icon="pi pi-times"
              class="p-button-outlined p-button-secondary"
              :loading="disconnecting"
              @click="handleDisconnect"
            />
            <Button
              label="Token erneuern"
              icon="pi pi-refresh"
              class="p-button-text"
              :loading="refreshing"
              @click="handleRefresh"
            />
          </template>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';

interface Props {
  platform: 'youtube' | 'tiktok' | 'instagram';
  isConnected: boolean;
  stats?: {
    videos: number;
    views: number;
  };
}

const props = defineProps<Props>();
const emit = defineEmits<{
  connect: [];
  disconnect: [];
  refresh: [];
}>();

const connecting = ref(false);
const disconnecting = ref(false);
const refreshing = ref(false);

const platformConfig = {
  youtube: {
    name: 'YouTube',
    icon: 'pi pi-youtube',
    color: '#FF0000'
  },
  tiktok: {
    name: 'TikTok',
    icon: 'pi pi-video',
    color: '#000000'
  },
  instagram: {
    name: 'Instagram',
    icon: 'pi pi-instagram',
    color: '#E4405F'
  }
};

const platformName = computed(() => platformConfig[props.platform].name);
const platformIcon = computed(() => platformConfig[props.platform].icon);
const platformColor = computed(() => platformConfig[props.platform].color);

const formatNumber = (num: number): string => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
};

const handleConnect = async () => {
  connecting.value = true;
  try {
    emit('connect');
  } finally {
    connecting.value = false;
  }
};

const handleDisconnect = async () => {
  disconnecting.value = true;
  try {
    emit('disconnect');
  } finally {
    disconnecting.value = false;
  }
};

const handleRefresh = async () => {
  refreshing.value = true;
  try {
    emit('refresh');
  } finally {
    refreshing.value = false;
  }
};
</script>

<style scoped>
.platform-card {
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.platform-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.platform-card.connected {
  border: 2px solid #10b981;
}

.platform-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.platform-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 12px;
  flex-shrink: 0;
}

.platform-icon i {
  font-size: 2rem;
}

.platform-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.platform-info h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  width: fit-content;
}

.status-badge.connected {
  background: #dcfce7;
  color: #166534;
}

.status-badge.not-connected {
  background: #fee2e2;
  color: #991b1b;
}

.platform-stats {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.platform-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.platform-actions button {
  flex: 1;
  min-width: 120px;
}
</style>
