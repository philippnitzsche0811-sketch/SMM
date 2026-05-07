<template>
  <div class="app-shell">
    <Sidebar :mobile-open="sidebarOpen" @close="sidebarOpen = false" />

    <div class="app-main">
      <TopBar @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <div class="page-content" :class="`route--${routeName}`">
        <router-view />
      </div>
      <LegalFooter :dark="true" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from './Sidebar.vue';
import TopBar from './TopBar.vue';
import LegalFooter from './LegalFooter.vue';

const sidebarOpen = ref(false);
const route = useRoute();
const routeName = computed(() => String(route.name || 'dashboard').toLowerCase());
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
  position: relative;
}

/* Orb pulse animation */
@keyframes orb-pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.45; }
}

/* Shared orb base */
.page-content::before,
.page-content::after {
  content: '';
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  filter: blur(130px);
  animation: orb-pulse 8s ease-in-out infinite;
}
.page-content::after {
  animation-delay: 4s; /* offset so they pulse out of sync */
}

/* ── Dashboard ── */
.route--dashboard::before {
  top: -80px; right: -40px;
  width: 620px; height: 620px;
  background: radial-gradient(ellipse, rgba(79,127,255,0.22) 0%, transparent 60%);
}
.route--dashboard::after {
  bottom: -100px; left: calc(30% - 200px);
  width: 600px; height: 480px;
  background: radial-gradient(ellipse, rgba(139,92,246,0.13) 0%, transparent 60%);
}

/* ── Upload ── */
.route--upload::before {
  top: -60px; left: calc(50% - 300px);
  width: 600px; height: 500px;
  background: radial-gradient(ellipse, rgba(79,127,255,0.18) 0%, transparent 60%);
}
.route--upload::after {
  bottom: -80px; right: -40px;
  width: 520px; height: 420px;
  background: radial-gradient(ellipse, rgba(139,92,246,0.11) 0%, transparent 60%);
}

/* ── Platforms ── */
.route--platforms::before {
  top: -80px; left: 80px;
  width: 600px; height: 560px;
  background: radial-gradient(ellipse, rgba(79,127,255,0.18) 0%, transparent 60%);
}
.route--platforms::after {
  bottom: -80px; right: -40px;
  width: 540px; height: 460px;
  background: radial-gradient(ellipse, rgba(139,92,246,0.11) 0%, transparent 60%);
}

/* ── Settings ── */
.route--settings::before {
  bottom: -100px; right: 100px;
  width: 580px; height: 480px;
  background: radial-gradient(ellipse, rgba(79,127,255,0.18) 0%, transparent 60%);
}
.route--settings::after {
  top: -80px; left: 60px;
  width: 560px; height: 500px;
  background: radial-gradient(ellipse, rgba(139,92,246,0.11) 0%, transparent 60%);
}

/* ── Uploads history ── */
.route--uploads::before {
  top: -80px; right: -40px;
  width: 600px; height: 560px;
  background: radial-gradient(ellipse, rgba(79,127,255,0.18) 0%, transparent 60%);
}
.route--uploads::after {
  bottom: -80px; left: 60px;
  width: 540px; height: 440px;
  background: radial-gradient(ellipse, rgba(139,92,246,0.11) 0%, transparent 60%);
}

/* Fallback for any other route */
.page-content:not([class*="route--"])::before,
[class*="route--"]:not(.route--dashboard):not(.route--upload):not(.route--platforms):not(.route--settings):not(.route--uploads)::before {
  top: -80px; right: -40px;
  width: 600px; height: 600px;
  background: radial-gradient(ellipse, rgba(79,127,255,0.18) 0%, transparent 60%);
}

.page-content > * { position: relative; z-index: 1; }

@media (max-width: 767px) {
  .page-content { padding: 1rem; }
}
</style>
