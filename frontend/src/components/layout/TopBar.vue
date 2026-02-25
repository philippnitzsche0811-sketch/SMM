<template>
  <header class="topbar">
    <div class="topbar-content">
      <!-- Page Title -->
      <h1 class="page-title">{{ pageTitle }}</h1>

      <!-- Actions -->
      <div class="topbar-actions">
        <!-- Notifications -->
        <Button 
          icon="pi pi-bell" 
          class="p-button-text p-button-rounded"
          :badge="notificationCount > 0 ? String(notificationCount) : undefined"
          badgeSeverity="danger"
          @click="toggleNotifications"
        />

        <!-- User Menu -->
        <div class="user-menu">
          <Avatar 
            :label="userInitials" 
            class="user-avatar"
            shape="circle"
            @click="toggleUserMenu"
          />
          
          <!-- 🆕 User Dropdown Menu -->
          <Menu 
            ref="userMenuRef" 
            :model="userMenuItems" 
            :popup="true"
          />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
import Menu from 'primevue/menu'; // 🆕

const route = useRoute();
const router = useRouter();
const { user, logout } = useAuth();
const toast = useToast();

const userMenuRef = ref();

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    'dashboard': 'Dashboard',
    'uploads': 'Video Uploads',
    'platforms': 'Plattformen',
    'settings': 'Einstellungen'
  };
  return titles[route.name as string] || 'Dashboard';
});

const userInitials = computed(() => {
  if (!user.value?.email) return 'U';
  return user.value.email.substring(0, 2).toUpperCase();
});

const notificationCount = computed(() => 0); // TODO: Implement notifications

// 🆕 User Menu Items
const userMenuItems = computed(() => [
  {
    label: user.value?.email || 'User',
    items: [
      {
        label: 'Profil',
        icon: 'pi pi-user',
        command: () => router.push('/settings')
      },
      {
        label: 'Einstellungen',
        icon: 'pi pi-cog',
        command: () => router.push('/settings')
      },
      {
        separator: true
      },
      {
        label: 'Abmelden',
        icon: 'pi pi-sign-out',
        command: () => handleLogout()
      }
    ]
  }
]);

// 🆕 Toggle User Menu
const toggleUserMenu = (event: Event) => {
  userMenuRef.value.toggle(event);
};

const toggleNotifications = () => {
  toast.add({
    severity: 'info',
    summary: 'Benachrichtigungen',
    detail: 'Keine neuen Benachrichtigungen',
    life: 3000
  });
};

const handleLogout = () => {
  logout();
};
</script>

<style scoped>
.topbar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 2rem;
}

.topbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-menu {
  position: relative;
}

.user-avatar {
  background: #3b82f6;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.user-avatar:hover {
  transform: scale(1.1);
}
</style>

