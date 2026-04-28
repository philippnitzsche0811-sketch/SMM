<template>
  <header class="topbar">
    <div class="topbar-left">
      <button class="hamburger" @click="$emit('toggle-sidebar')" aria-label="Menu">
        <i class="pi pi-bars"></i>
      </button>
      <h2 class="page-title">{{ pageTitle }}</h2>
    </div>

    <div class="topbar-right">
      <router-link to="/upload" class="upload-btn" v-if="route.name !== 'upload'">
        <i class="pi pi-cloud-upload"></i>
        <span>Upload</span>
      </router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

defineEmits<{ 'toggle-sidebar': [] }>();

const route = useRoute();

const titles: Record<string, string> = {
  dashboard: 'Dashboard',
  upload:    'Upload Video',
  uploads:   'My Videos',
  connect:   'Connect Accounts',
  platforms: 'Platforms',
  settings:  'Settings',
};

const pageTitle = computed(() => titles[route.name as string] || 'SocialHub');
</script>

<style scoped>
.topbar {
  height: 64px;
  min-height: 64px;
  background: #ffffff;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  position: sticky;
  top: 0;
  z-index: var(--z-topbar);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.hamburger {
  display: none;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.375rem;
  border-radius: 6px;
  font-size: 1.125rem;
  transition: color var(--transition-fast);
}
.hamburger:hover { color: var(--text-primary); }

@media (max-width: 767px) {
  .hamburger { display: flex; align-items: center; }
}

.page-title {
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.875rem;
  background: var(--primary-500);
  color: white;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  transition: background var(--transition-fast);
}
.upload-btn:hover { background: var(--primary-600); color: white; }

@media (max-width: 480px) {
  .upload-btn span { display: none; }
  .upload-btn { padding: 0.5rem; }
}
</style>
