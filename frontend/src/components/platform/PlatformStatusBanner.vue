<template>
  <Message v-if="!hasConnectedPlatforms" severity="warn" :closable="false">
    <div class="platform-warning">
      <span>⚠️ Keine Plattformen verbunden!</span>
      <Button label="Jetzt verbinden" size="small" @click="$router.push('/platforms')" />
    </div>
  </Message>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import Message from 'primevue/message';
import Button from 'primevue/button';

const authStore = useAuthStore();
const hasConnectedPlatforms = computed(() => 
  (authStore.user?.connectedPlatforms?.length || 0) > 0
);
</script>

<style scoped>
.platform-warning {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 1rem;
}
</style>
