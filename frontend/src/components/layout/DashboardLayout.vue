<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="main-content">
      <!-- Top Bar -->
      <TopBar />

      <!-- Page Content -->
      <div class="page-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue';
import TopBar from './TopBar.vue';
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f5f5f5;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}
</style>
