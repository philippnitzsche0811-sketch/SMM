<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <div class="logo" v-if="!isCollapsed">
        <i class="pi pi-play-circle logo-icon"></i>
        <span class="logo-text">SMM</span>
      </div>
      <Button
        :icon="isCollapsed ? 'pi pi-chevron-right' : 'pi pi-chevron-left'"
        class="p-button-text p-button-rounded collapse-btn"
        @click="isCollapsed = !isCollapsed"
      />
    </div>

    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <i :class="item.icon" class="nav-icon"></i>
        <span class="nav-label" v-if="!isCollapsed">{{ item.label }}</span>
        <Tooltip v-if="isCollapsed" :target="`.nav-item[data-name='${item.name}']`" :content="item.label" />
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <div class="user-info" v-if="!isCollapsed">
        <Avatar :label="userInitial" class="user-avatar" shape="circle" />
        <div class="user-details">
          <span class="user-name">{{ authStore.userName || authStore.userEmail }}</span>
          <span class="user-email">{{ authStore.userEmail }}</span>
        </div>
      </div>
      <Button
        icon="pi pi-sign-out"
        class="p-button-text p-button-rounded logout-btn"
        :class="{ 'p-button-sm': !isCollapsed }"
        @click="handleLogout"
        v-tooltip="isCollapsed ? 'Logout' : ''"
      />
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const isCollapsed = ref(false);

const navItems = [
  { name: 'dashboard', path: '/dashboard', icon: 'pi pi-home', label: 'Dashboard' },
  { name: 'platforms', path: '/platforms', icon: 'pi pi-share-alt', label: 'Plattformen' },
  { name: 'settings', path: '/settings', icon: 'pi pi-cog', label: 'Einstellungen' },
];

const userInitial = authStore.userName?.charAt(0).toUpperCase()
  || authStore.userEmail?.charAt(0).toUpperCase()
  || 'U';

const isActive = (path: string) => route.path === path;

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.sidebar {
  width: 240px;
  min-width: 240px;
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease, min-width 0.25s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 68px;
  min-width: 68px;
}

/* Header */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  min-height: 68px;
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.logo-icon {
  font-size: 1.5rem;
  color: #6366f1;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.025em;
}

.collapse-btn {
  color: #94a3b8 !important;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.875rem;
  border-radius: 8px;
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  font-size: 0.9375rem;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}

.nav-item:hover {
  background: #f8fafc;
  color: #334155;
}

.nav-item.active {
  background: #eef2ff;
  color: #4f46e5;
}

.nav-item.active .nav-icon {
  color: #4f46e5;
}

.nav-icon {
  font-size: 1.125rem;
  min-width: 1.125rem;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 0.75rem;
}

/* Footer */
.sidebar-footer {
  padding: 1rem 0.75rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar.collapsed .sidebar-footer {
  justify-content: center;
}

.user-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  overflow: hidden;
}

.user-avatar {
  background: #6366f1 !important;
  color: white !important;
  font-weight: 600;
  flex-shrink: 0;
  width: 2rem !important;
  height: 2rem !important;
  font-size: 0.875rem !important;
}

.user-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.user-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: 0.75rem;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  color: #94a3b8 !important;
  flex-shrink: 0;
}

.logout-btn:hover {
  color: #ef4444 !important;
}
</style>
