<template>
  <div class="app-shell">
    <Sidebar :mobile-open="sidebarOpen" @close="sidebarOpen = false" />

    <div class="app-main">
      <TopBar @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <div class="page-content">
        <router-view />
      </div>
      <LegalFooter :dark="true" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Sidebar from './Sidebar.vue';
import TopBar from './TopBar.vue';
import LegalFooter from './LegalFooter.vue';

const sidebarOpen = ref(false);
</script>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-secondary);
}

.app-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

@media (max-width: 767px) {
  .page-content { padding: 1rem; }
}
</style>
