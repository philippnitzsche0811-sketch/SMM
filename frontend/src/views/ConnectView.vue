<template>
  <div class="connect-view">
    <Card class="connect-card">
      <template #title>
        <h2>Plattformen verbinden</h2>
      </template>
      <template #content>
        <div class="platforms-grid">
          <YouTubeConnect />
          <TikTokConnect />
          <InstagramConnect />
        </div>

        <Divider />

        <div class="actions">
          <Button
            label="Weiter zum Upload"
            icon="pi pi-arrow-right"
            iconPos="right"
            @click="router.push('/upload')"
            :disabled="!platformStore.hasAnyConnection"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Divider from 'primevue/divider';
import { YouTubeConnect, TikTokConnect, InstagramConnect } from '@/components/connect';
import { usePlatformStore } from '@/stores/platformStore';

const router = useRouter();
const platformStore = usePlatformStore();
</script>

