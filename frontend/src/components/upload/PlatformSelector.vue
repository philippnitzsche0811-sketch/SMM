<template>
  <div class="platform-selector">
    <h3>Plattformen auswählen</h3>
    <p class="subtitle">Wähle aus, wo dein Video veröffentlicht werden soll</p>

    <div class="platforms-grid">
      <div 
        v-for="platform in platforms" 
        :key="platform.id" 
        class="platform-card"
        :class="{ 
          'selected': isSelected(platform.id), 
          'disabled': !platform.connected 
        }"
        @click="togglePlatform(platform.id, platform.connected)"
      >
        <div class="platform-content">
          <div class="platform-icon-wrapper">
            <i :class="platform.icon" :style="{ color: platform.color }"></i>
            <Checkbox 
              v-model="localSelected" 
              :value="platform.id"
              :disabled="!platform.connected"
              @click.stop
            />
          </div>

          <div class="platform-info">
            <h4>{{ platform.name }}</h4>
            <p class="platform-description">{{ platform.description }}</p>

            <div class="platform-status">
              <Badge 
                v-if="platform.connected" 
                value="Verbunden" 
                severity="success"
              />
              <Badge 
                v-else 
                value="Nicht verbunden" 
                severity="warning"
              />

              />
            </div>
          </div>
        </div>

        <div v-if="!platform.connected" class="overlay">
          <i class="pi pi-lock"></i>
          <span>Erst verbinden</span>
        </div>
      </div>
    </div>

    <Message v-if="localSelected.length === 0" severity="warn" :closable="false">
      Bitte wähle mindestens eine Plattform aus
    </Message>

    <div class="selection-summary" v-else>
      <i class="pi pi-check-circle"></i>
      <span>{{ localSelected.length }} Plattform{{ localSelected.length > 1 ? 'en' : '' }} ausgewählt</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import Checkbox from 'primevue/checkbox';
import Badge from 'primevue/badge';
import Message from 'primevue/message';
import { usePlatformStore } from '@/stores/platformStore';

const props = defineProps<{
  modelValue: string[];
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string[]];
}>();

const platformStore = usePlatformStore();
const localSelected = ref<string[]>([...props.modelValue]);

const platforms = [
  { 
    id: 'youtube', 
    name: 'YouTube', 
    icon: 'pi pi-youtube', 
    color: '#FF0000',
    description: 'Erreiche Millionen auf der größten Video-Plattform',
    connected: platformStore.isConnected('youtube')
  },
  { 
    id: 'tiktok', 
    name: 'TikTok', 
    icon: 'pi pi-video', 
    color: '#000000',
    description: 'Teile Kurzvideos mit einer jungen Zielgruppe',
    connected: platformStore.isConnected('tiktok')
  },
  { 
    id: 'instagram', 
    name: 'Instagram', 
    icon: 'pi pi-instagram', 
    color: '#E4405F',
    description: 'Veröffentliche Reels und Stories',
    connected: platformStore.isConnected('instagram')
  }
];

const isSelected = (platformId: string): boolean => {
  return localSelected.value.includes(platformId);
};

const togglePlatform = (platformId: string, connected: boolean) => {
  if (!connected) return;

  const index = localSelected.value.indexOf(platformId);
  if (index > -1) {
    localSelected.value.splice(index, 1);
  } else {
    localSelected.value.push(platformId);
  }
};

watch(localSelected, (newValue) => {
  emit('update:modelValue', newValue);
}, { deep: true });

watch(() => props.modelValue, (newValue) => {
  localSelected.value = [...newValue];
});

onMounted(() => {
  if (localSelected.value.length === 0) {
    const availablePlatforms = platforms
      .filter(p => p.connected)
      .map(p => p.id);

    if (availablePlatforms.length > 0) {
      localSelected.value = [...availablePlatforms];
    }
  }
});
</script>

<style scoped>
.platform-selector {
  width: 100%;
}

.subtitle {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.platform-card {
  position: relative;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: white;
}

.platform-card:hover:not(.disabled) {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.platform-card.selected {
  border-color: var(--primary-color);
  background: rgba(33, 150, 243, 0.05);
}

.platform-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.platform-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.platform-icon-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-icon-wrapper i.pi {
  font-size: 2.5rem;
}

.platform-info h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.platform-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

.platform-status {
  display: flex;
  align-items: center;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  color: var(--text-secondary);
}

.overlay i {
  font-size: 1.5rem;
}

.selection-summary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(76, 175, 80, 0.1);
  border-radius: var(--radius-md);
  color: var(--success-color);
  font-weight: 600;
}

.selection-summary i {
  font-size: 1.25rem;
}

@media (max-width: 768px) {
  .platforms-grid {
    grid-template-columns: 1fr;
  }
}
</style>
