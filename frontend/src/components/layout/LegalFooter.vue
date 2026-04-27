<template>
  <footer :class="['legal-footer', dark ? 'legal-footer--dark' : 'legal-footer--light']">
    <router-link to="/terms">Terms of Service</router-link>
    <span class="dot">·</span>
    <router-link to="/privacy">Privacy Policy</router-link>
    <span class="dot">·</span>
    <router-link to="/impressum">Impressum</router-link>
  </footer>
</template>

<script setup lang="ts">
defineProps<{ dark?: boolean }>();
</script>

<style scoped>
.legal-footer {
  text-align: center;
  padding: 1rem;
  font-size: 0.8rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.legal-footer a {
  text-decoration: none;
}

.legal-footer a:hover {
  text-decoration: underline;
}

.legal-footer--light a  { color: rgba(255, 255, 255, 0.7); }
.legal-footer--light a:hover { color: white; }
.legal-footer--light .dot { color: rgba(255, 255, 255, 0.3); }

.legal-footer--dark a { color: #94a3b8; }
.legal-footer--dark a:hover { color: #475569; }
.legal-footer--dark .dot { color: #cbd5e1; }
</style>
