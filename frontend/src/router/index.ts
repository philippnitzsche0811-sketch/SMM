import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    // 🏠 PUBLIC LANDING PAGE
    {
      path: '/',
      name: 'landing',
      component: () => import('@/views/LandingView.vue'),
      meta: { requiresAuth: false },
    },

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
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/auth/ForgotPasswordView.vue'),
      meta: { guest: true },
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('@/views/auth/ResetPasswordView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/verify-email',
      name: 'verify-email',
      component: () => import('@/views/auth/VerifyEmailView.vue'),
      meta: { requiresAuth: false },
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
      path: '/impressum',
      name: 'impressum',
      component: () => import('@/views/ImpressumView.vue'),
      meta: { requiresAuth: false },
    },

    // 🔒 APP ROUTES (with DashboardLayout)
    {
      path: '/',
      component: () => import('@/components/layout/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },
        {
          path: 'upload',
          name: 'upload',
          component: () => import('@/views/UploadView.vue'),
        },
        {
          path: 'upload/simple',
          name: 'upload-simple',
          component: () => import('@/views/SimpleUploadView.vue'),
        },
        {
          path: 'upload/smart',
          name: 'upload-smart',
          component: () => import('@/views/SmartUploadView.vue'),
        },
        {
          path: 'upload/groups',
          name: 'upload-groups',
          component: () => import('@/views/UploadGroupsView.vue'),
        },
        {
          path: 'upload/groups/:id',
          name: 'upload-group-detail',
          component: () => import('@/views/UploadGroupsView.vue'),
        },
        {
          path: 'uploads',
          name: 'uploads',
          component: () => import('@/views/UploadsView.vue'),
        },
        {
          path: 'connect',
          name: 'connect',
          component: () => import('@/views/ConnectView.vue'),
        },
        {
          path: 'platforms',
          name: 'platforms',
          component: () => import('@/views/PlatformsView.vue'),
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/SettingsView.vue'),
        },
        {
          path: 'calendar',
          name: 'calendar',
          component: () => import('@/views/CalendarView.vue'),
        },
        {
          path: 'plan',
          name: 'plan',
          component: () => import('@/views/IdeasView.vue'),
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: () => import('@/views/AnalyticsView.vue'),
        },
        {
          path: 'admin',
          name: 'admin',
          component: () => import('@/views/AdminView.vue'),
          meta: { requiresAdmin: true },
        },
      ],
    },
  ],
});

// Navigation Guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  // Landing page and guest routes: redirect authenticated users to dashboard
  if (to.meta.requiresAuth === false || to.meta.guest) {
    if ((to.name === 'landing' || to.meta.guest) && authStore.isAuthenticated) {
      return next('/dashboard');
    }
    return next();
  }

  // Protected routes: redirect unauthenticated users to login
  if (!authStore.isAuthenticated) {
    return next('/login');
  }

  // Admin guard
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next('/dashboard');
  }

  return next();
});

export default router;
