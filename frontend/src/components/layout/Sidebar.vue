<template>
  <!-- Mobile backdrop -->
  <div v-if="mobileOpen" class="sidebar-backdrop" @click="$emit('close')" />

  <aside
    class="sidebar"
    :class="{
      collapsed:   isCollapsed,
      'mobile-open': mobileOpen,
    }"
  >
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-mark">
        <img :src="logoUrl" alt="Decodu-SMM" class="logo-img" />
      </div>
      <span class="logo-name" v-show="!isCollapsed">Decodu-SMM</span>
      <button
        class="collapse-btn"
        @click="isCollapsed = !isCollapsed"
        :title="isCollapsed ? 'Expand' : 'Collapse'"
      >
        <i :class="isCollapsed ? 'pi pi-chevron-right' : 'pi pi-chevron-left'"></i>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
        :title="isCollapsed ? item.label : ''"
        @click="$emit('close')"
      >
        <i :class="item.icon" class="nav-icon"></i>
        <span class="nav-label" v-show="!isCollapsed">{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- User / Logout -->
    <div class="sidebar-footer">
      <div class="user-row" v-show="!isCollapsed">
        <div class="user-avatar-wrap">{{ userInitial }}</div>
        <div class="user-meta">
          <span class="user-name">{{ authStore.userName || 'Account' }}</span>
          <span class="user-email">{{ authStore.userEmail }}</span>
        </div>
      </div>
      <button class="logout-btn" @click="handleLogout" title="Sign out">
        <i class="pi pi-sign-out"></i>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import logoUrl from '@/assets/images/logo.png';

defineProps<{ mobileOpen: boolean }>();
defineEmits<{ close: [] }>();

const route     = useRoute();
const router    = useRouter();
const authStore = useAuthStore();

const isCollapsed = ref(false);

const navItems = [
  { name: 'dashboard',      path: '/dashboard',      icon: 'pi pi-home',        label: 'Dashboard' },
  { name: 'upload',         path: '/upload',         icon: 'pi pi-cloud-upload', label: 'Upload'    },
  { name: 'upload-groups',  path: '/upload/groups',  icon: 'pi pi-calendar',    label: 'Groups'    },
  { name: 'platforms',      path: '/platforms',      icon: 'pi pi-link',         label: 'Platforms' },
  { name: 'settings',       path: '/settings',       icon: 'pi pi-cog',          label: 'Settings'  },
];

const userInitial = computed(() =>
  (authStore.userName || authStore.userEmail || 'U').charAt(0).toUpperCase()
);

const isActive = (path: string) => {
  if (!route.path.startsWith(path)) return false;
  return !navItems.some(
    item => item.path !== path &&
            item.path.startsWith(path + '/') &&
            route.path.startsWith(item.path),
  );
};
const handleLogout = () => { authStore.logout(); router.push('/'); };
</script>

<style scoped>
/* Backdrop (mobile) */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.5);
  z-index: 190;
}

/* ── Desktop: in-flow ── */
.sidebar {
  width: 240px;
  min-width: 240px;
  height: 100vh;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.22s ease, min-width 0.22s ease;
  overflow: hidden;
  z-index: 200;
}

.sidebar.collapsed {
  width: 68px;
  min-width: 68px;
}

/* ── Mobile: off-canvas overlay ── */
@media (max-width: 767px) {
  .sidebar-backdrop { display: block; }

  .sidebar {
    position: fixed;
    top: 0; left: 0; bottom: 0;
    width: 260px;
    min-width: 260px;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }

  /* hide collapse button on mobile */
  .collapse-btn { display: none; }
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0 1rem;
  height: 64px;
  border-bottom: 1px solid var(--sidebar-border);
  flex-shrink: 0;
}

.logo-mark {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.logo-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 8px;
}

.logo-name {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
}

.collapse-btn {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--sidebar-text);
  cursor: pointer;
  padding: 0.35rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  transition: color 0.15s, background 0.15s;
  flex-shrink: 0;
}
.collapse-btn:hover { background: var(--sidebar-hover-bg); color: var(--sidebar-text-hover); }

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0.625rem;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6875rem 0.75rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--sidebar-text);
  font-weight: 500;
  font-size: 0.9rem;
  white-space: nowrap;
  transition: background 0.15s, color 0.15s;
  position: relative;
}

.nav-item:hover  { background: var(--sidebar-hover-bg); color: var(--sidebar-text-hover); }

.nav-item.active {
  background: var(--sidebar-active-bg);
  color: var(--sidebar-text-active);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0; top: 6px; bottom: 6px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--sidebar-active-accent);
}

.nav-icon {
  font-size: 1.0625rem;
  min-width: 1.0625rem;
  flex-shrink: 0;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 0.6875rem;
}

/* Footer */
.sidebar-footer {
  padding: 0.875rem 0.75rem;
  border-top: 1px solid var(--sidebar-border);
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-shrink: 0;
}

.user-row {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  overflow: hidden;
  min-width: 0;
}

.user-avatar-wrap {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--primary-600);
  color: white;
  font-size: 0.8125rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-meta { display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

.user-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #d4d4d8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: 0.72rem;
  color: var(--sidebar-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  background: none;
  border: none;
  color: var(--sidebar-text);
  cursor: pointer;
  padding: 0.4rem;
  border-radius: 6px;
  font-size: 0.9375rem;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  transition: color 0.15s, background 0.15s;
}
.logout-btn:hover { color: #f87171; background: rgba(239,68,68,.08); }
</style>
