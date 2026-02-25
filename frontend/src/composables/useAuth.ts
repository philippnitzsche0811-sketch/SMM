// composables/useAuth.ts
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { computed } from 'vue';

export const useAuth = () => {
  const authStore = useAuthStore();
  const router = useRouter();
  const toast = useToast();

  const login = async (email: string, password: string) => {
    try {
      await authStore.login(email, password);  // ✅ Zwei Parameter
      toast.add({
        severity: 'success',
        summary: 'Willkommen!',
        detail: 'Login erfolgreich',
        life: 3000
      });
      router.push('/dashboard');
    } catch (error: any) {
      toast.add({
        severity: 'error',
        summary: 'Login fehlgeschlagen',
        detail: error.response?.data?.detail || 'Ungültige Anmeldedaten',
        life: 5000
      });
    }
  };

  const register = async (data: { email: string; password: string }) => {
    try {
      await authStore.register(data.email, data.password);  // ✅ Zwei Parameter
      toast.add({
        severity: 'success',
        summary: 'Registrierung erfolgreich!',
        detail: 'Bitte prüfe deine E-Mails zur Verifizierung',
        life: 3000
      });
      router.push('/login');  // ✅ Zur Login-Seite nach Registrierung
    } catch (error: any) {
      toast.add({
        severity: 'error',
        summary: 'Registrierung fehlgeschlagen',
        detail: error.response?.data?.detail || 'Ein Fehler ist aufgetreten',
        life: 5000
      });
    }
  };

  const logout = () => {
    authStore.logout();
    toast.add({
      severity: 'info',
      summary: 'Abgemeldet',
      detail: 'Du wurdest erfolgreich abgemeldet',
      life: 3000
    });
    router.push('/login');
  };

  return {
    login,
    register,
    logout,
    user: computed(() => authStore.user),
    isAuthenticated: computed(() => authStore.isAuthenticated)
  };
};
