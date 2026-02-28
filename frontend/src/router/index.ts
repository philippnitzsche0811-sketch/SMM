import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    // Root leitet abhängig vom Auth-Status um, das machen wir im Guard
    // oder lässt man komplett weg – wichtig ist nur, dass es keine zweite
    // Route mit path: '/' neben dem Layout gibt.

    // 🔓 AUTH ROUTES
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { guest: true },
    },

    // 📄 LEGAL PAGES (Public)
    {
      path: '/terms',
      name: 'terms',
      component: () => import('@/views/TermsView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('@/views/PrivacyView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/verify-email',
      name: 'verify-email',
      component: () => import('@/views/auth/VerifyEmailView.vue'),
      meta: { requiresAuth: false }
    },


    // 🔒 APP ROUTES (MIT DashboardLayout) – OHNE /app Prefix
    {
      path: '/', // Layout hängt an Root
      component: () => import('@/components/layout/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',              // '/' → redirect auf /dashboard
          redirect: '/dashboard',
        },
        {
          path: 'dashboard',     // /dashboard
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },
        {
          path: 'upload',        // /upload
          name: 'upload',
          component: () => import('@/views/UploadView.vue'),
        },
        {
          path: 'uploads',       // /uploads
          name: 'uploads',
          component: () => import('@/views/UploadView.vue'),
        },
        {
          path: 'platforms',     // /platforms
          name: 'platforms',
          component: () => import('@/views/PlatformsView.vue'),
        },
        {
          path: 'settings',      // /settings
          name: 'settings',
          component: () => import('@/views/SettingsView.vue'),
        },
      ],
    },
  ],
});

// Navigation Guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  // Public routes explizit erlauben
  if (to.meta.requiresAuth === false || to.meta.guest) {
    if (to.meta.guest && authStore.isAuthenticated) {
      // Eingeloggt, aber will auf /login → ab auf Dashboard
      return next('/dashboard');
    }
    return next();
  }

  // Alle anderen Routes: Auth benötigt
  if (!authStore.isAuthenticated) {
    return next('/login');
  }

  return next();
});

export default router;
