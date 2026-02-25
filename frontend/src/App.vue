<template>
  <div id="app">
    <router-view />
    <Toast />
    <ConfirmDialog />  <!-- ✅ ADD THIS -->
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';  // ✅ ADD THIS

const authStore = useAuthStore();

onMounted(() => {
  authStore.initAuth();
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
</style>
