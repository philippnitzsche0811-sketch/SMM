import { computed } from 'vue';
import { useAuthStore } from '@/stores/authStore';

export function usePlan() {
  const authStore = useAuthStore();

  const isProUser = computed(() =>
    authStore.user?.plan === 'pro' || authStore.isAdmin
  );

  const canUseAI = computed(() => isProUser.value);

  return { isProUser, canUseAI };
}
