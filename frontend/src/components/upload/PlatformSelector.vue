<template>
  <div class="platform-selector">
    <p class="selector-hint">Select where to publish your video</p>

    <div class="platforms-grid">
      <div
        v-for="platform in platforms"
        :key="platform.id"
        class="platform-card"
        :class="{
          selected:  isSelected(platform.id),
          disabled: !platform.connected,
        }"
        @click="togglePlatform(platform.id, platform.connected)"
      >
        <div class="platform-top">
          <i :class="platform.icon" class="platform-icon" :style="{ color: platform.color }"></i>
          <div class="platform-check" :class="{ checked: isSelected(platform.id) }">
            <i class="pi pi-check"></i>
          </div>
        </div>
        <div class="platform-name">{{ platform.name }}</div>
        <div class="platform-desc">{{ platform.description }}</div>
        <div class="platform-status">
          <span v-if="platform.connected" class="badge connected">Connected</span>
          <span v-else class="badge not-connected">Not connected</span>
        </div>

        <div v-if="!platform.connected" class="lock-overlay">
          <i class="pi pi-lock"></i>
          <span>Connect first</span>
        </div>
      </div>
    </div>

    <div v-if="localSelected.length === 0" class="selection-hint warn">
      <i class="pi pi-info-circle"></i>
      Select at least one platform to continue
    </div>
    <div v-else class="selection-hint success">
      <i class="pi pi-check-circle"></i>
      {{ localSelected.length }} platform{{ localSelected.length > 1 ? 's' : '' }} selected
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { usePlatformStore } from '@/stores/platformStore';

const props = defineProps<{ modelValue: string[] }>();
const emit  = defineEmits<{ 'update:modelValue': [value: string[]] }>();

const platformStore  = usePlatformStore();
const localSelected  = ref<string[]>([...props.modelValue]);

const platforms = [
  {
    id:          'youtube',
    name:        'YouTube',
    icon:        'pi pi-youtube',
    color:       '#FF0000',
    description: 'Reach millions on the world\'s largest video platform',
    connected:   platformStore.isConnected('youtube'),
  },
  {
    id:          'tiktok',
    name:        'TikTok',
    icon:        'pi pi-video',
    color:       '#010101',
    description: 'Share short-form content with a global audience',
    connected:   platformStore.isConnected('tiktok'),
  },
  {
    id:          'instagram',
    name:        'Instagram',
    icon:        'pi pi-instagram',
    color:       '#E4405F',
    description: 'Publish Reels and grow your following',
    connected:   platformStore.isConnected('instagram'),
  },
];

const isSelected = (id: string) => localSelected.value.includes(id);

const togglePlatform = (id: string, connected: boolean) => {
  if (!connected) return;
  const idx = localSelected.value.indexOf(id);
  if (idx > -1) localSelected.value.splice(idx, 1);
  else localSelected.value.push(id);
};

watch(localSelected, (val) => emit('update:modelValue', [...val]), { deep: true });

watch(() => props.modelValue, (newVal) => {
  const cur = localSelected.value;
  const same = newVal.length === cur.length && newVal.every((v, i) => v === cur[i]);
  if (!same) localSelected.value = [...newVal];
});

onMounted(() => {
  if (localSelected.value.length === 0) {
    const preselect = platforms.filter(p => p.connected).map(p => p.id);
    if (preselect.length > 0) localSelected.value = preselect;
  }
});
</script>

<style scoped>
.platform-selector { width: 100%; }

.selector-hint {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 1.25rem;
}

.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.875rem;
  margin-bottom: 1.25rem;
}

.platform-card {
  position: relative;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
  background: white;
  overflow: hidden;
}

.platform-card:hover:not(.disabled) {
  border-color: var(--primary-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.platform-card.selected {
  border-color: var(--primary-500);
  background: var(--primary-50);
}

.platform-card.disabled { cursor: not-allowed; }

.platform-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.875rem;
}

.platform-icon { font-size: 2.25rem; }

.platform-check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  color: transparent;
  font-size: 0.65rem;
}

.platform-check.checked {
  background: var(--primary-500);
  border-color: var(--primary-500);
  color: white;
}

.platform-name {
  font-weight: 700;
  font-size: 0.9375rem;
  color: var(--text-primary);
  margin-bottom: 0.3rem;
}

.platform-desc {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  line-height: 1.4;
  margin-bottom: 0.75rem;
}

.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 600;
}

.badge.connected {
  background: #dcfce7;
  color: #15803d;
}

.badge.not-connected {
  background: #fef3c7;
  color: #b45309;
}

.lock-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.82);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-secondary);
  border-radius: calc(var(--radius-lg) - 2px);
  backdrop-filter: blur(1px);
}

.lock-overlay i { font-size: 1.375rem; }

.selection-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
}

.selection-hint.warn {
  background: #fefce8;
  border: 1px solid #fde68a;
  color: #b45309;
}

.selection-hint.success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #15803d;
}

@media (max-width: 600px) {
  .platforms-grid { grid-template-columns: 1fr; }
}
</style>
