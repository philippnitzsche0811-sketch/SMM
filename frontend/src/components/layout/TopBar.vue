<template>
  <header class="topbar">
    <div class="topbar-left">
      <h2 class="page-title">{{ pageTitle }}</h2>
    </div>
    <div class="topbar-right">
      <span class="topbar-user">
        <i class="pi pi-user"></i>
        {{ authStore.userName || authStore.userEmail }}
      </span>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const route = useRoute();
const authStore = useAuthStore();

const titles: Record<string, string> = {
  dashboard: 'Dashboard',
  platforms: 'Plattformen',
  settings: 'Einstellungen',
};

const pageTitle = computed(() => titles[route.name as string] || 'SMM');
</script>

<style scoped>
.topbar {
  height: 64px;
  min-height: 64px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
}

.page-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.topbar-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}
</style>
