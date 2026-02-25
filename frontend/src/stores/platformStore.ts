import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { getUserStatus } from '@/services/api';
import type { UserPlatforms } from '@/types/platform.types';

export const usePlatformStore = defineStore('platform', () => {
  // State
  const platforms = ref<UserPlatforms>({});
  const loading = ref(false);
  const error = ref<string | null>(null);
  const lastFetch = ref<Date | null>(null);

  // Getters
  const connectedPlatforms = computed(() => {
    return Object.entries(platforms.value)
      .filter(([_, status]) => status?.connected)
      .map(([platform]) => platform);
  });

  const connectedCount = computed(() => connectedPlatforms.value.length);

  const hasAnyConnection = computed(() => connectedCount.value > 0);

  const isConnected = (platform: string): boolean => {
    return platforms.value[platform as keyof UserPlatforms]?.connected || false;
  };

  const getConnectionStatus = (platform: string) => {
    return platforms.value[platform as keyof UserPlatforms] || null;
  };

  // Actions
  const fetchPlatformStatus = async (userId: string, force: boolean = false) => {
    // Cache für 5 Minuten
    if (!force && lastFetch.value) {
      const timeSinceLastFetch = Date.now() - lastFetch.value.getTime();
      if (timeSinceLastFetch < 5 * 60 * 1000) {
        console.log('📦 Using cached platform status');
        return;
      }
    }

    loading.value = true;
    error.value = null;

    try {
      // TODO: API Call zum Backend
      // const response = await getUserStatus(userId);

      // Mock für Entwicklung
      const mockPlatforms: UserPlatforms = {
        youtube: {
          connected: false,
          lastSync: undefined
        },
        tiktok: {
          connected: false,
          lastSync: undefined
        },
        instagram: {
          connected: false,
          lastSync: undefined
        }
      };

      platforms.value = mockPlatforms;
      lastFetch.value = new Date();

      console.log('✅ Platform status geladen:', connectedPlatforms.value);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Fehler beim Laden';
      console.error('❌ Platform status laden fehlgeschlagen:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const connectPlatform = (platform: string, username?: string) => {
    if (platforms.value[platform as keyof UserPlatforms]) {
      platforms.value[platform as keyof UserPlatforms] = {
        connected: true,
        lastSync: new Date().toISOString(),
        username
      };
      console.log(`✅ ${platform} verbunden`);
    }
  };

  const disconnectPlatform = async (platform: string) => {
    try {
      // TODO: API Call zum Backend
      // await api.delete(`/user/${userId}/disconnect/${platform}`);

      if (platforms.value[platform as keyof UserPlatforms]) {
        platforms.value[platform as keyof UserPlatforms] = {
          connected: false,
          lastSync: undefined
        };
      }

      console.log(`🔌 ${platform} getrennt`);
    } catch (err) {
      console.error(`❌ ${platform} trennen fehlgeschlagen:`, err);
      throw err;
    }
  };

  const reset = () => {
    platforms.value = {};
    loading.value = false;
    error.value = null;
    lastFetch.value = null;
  };

  return {
    // State
    platforms,
    loading,
    error,
    lastFetch,

    // Getters
    connectedPlatforms,
    connectedCount,
    hasAnyConnection,

    // Actions
    isConnected,
    getConnectionStatus,
    fetchPlatformStatus,
    connectPlatform,
    disconnectPlatform,
    reset
  };
});
