<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar-header">
      <img src="@/assets/images/logo.png" alt="Logo" class="logo" />
      <h2>Social Hub</h2>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link to="/dashboard" class="nav-item">
        <i class="pi pi-home"></i>
        <span>Dashboard</span>
      </router-link>
      
      <router-link to="/platforms" class="nav-item">
        <i class="pi pi-link"></i>
        <span>Plattformen</span>
      </router-link>

      <router-link to="/settings" class="nav-item">
        <i class="pi pi-cog"></i>
        <span>Einstellungen</span>
      </router-link>
    </nav>

    <!-- User Info -->
    <div class="sidebar-footer">
      <div class="user-info">
        <i class="pi pi-user"></i>
        <span>{{ userEmail }}</span>
      </div>
      <Button 
        label="Logout" 
        icon="pi pi-sign-out" 
        class="p-button-text p-button-sm"
        @click="handleLogout"
      />
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuth } from '@/composables/useAuth';
import Button from 'primevue/button';

const { user, logout } = useAuth();

const userEmail = computed(() => user.value?.email || 'User');

const handleLogout = () => {
  logout();
};
</script>


<style scoped>
.sidebar {
  width: 260px;
  background: #1e293b;
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 2rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  width: 40px;
  height: 40px;
  border-radius: 8px;
}

.sidebar-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.nav-item.router-link-active {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border-left-color: #3b82f6;
}

.nav-item i {
  font-size: 1.25rem;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
}

.user-info i {
  font-size: 1.25rem;
}
</style>
