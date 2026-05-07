<template>
  <UploadModeSelector @select="handleModeSelect" />
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import UploadModeSelector from '@/components/upload/UploadModeSelector.vue';

const router = useRouter();

function handleModeSelect(mode: 'simple' | 'smart' | 'groups') {
  if (mode === 'simple')  router.push('/upload/simple');
  if (mode === 'smart')   router.push('/upload/smart');
  if (mode === 'groups')  router.push('/upload/groups');
}
</script>
