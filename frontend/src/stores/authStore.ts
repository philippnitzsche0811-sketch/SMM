import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import axios from 'axios';

export interface ConnectedPlatform {
  platform: string;
  username?: string;
  channelId?: string;
  connectedAt?: string;
}

export interface User {
  id: string;  // ✅ NUR string
  email: string;
  username?: string | null;
  isVerified: boolean;
  connectedPlatforms?: ConnectedPlatform[];
  createdAt?: string;
  updatedAt?: string;
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  
  // Getters
  const isAuthenticated = computed(() => {
    const hasToken = !!token.value;
    const hasUser = !!user.value;
    return hasToken && hasUser;
  });
  
  const userId = computed(() => user.value?.id || null);
  const userEmail = computed(() => user.value?.email || null);
  const userName = computed(() => user.value?.username || null);
  const isVerified = computed(() => user.value?.isVerified || false);
  
  // Actions
  const setAuth = (userData: User, accessToken: string) => {
    console.log('📝 Setting auth:', { userData, token: accessToken.substring(0, 20) + '...' });
    
    user.value = userData;
    token.value = accessToken;
    
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('access_token', accessToken);
    
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
    
    console.log('✅ Auth set complete. isAuthenticated:', isAuthenticated.value);
  };
  
  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post('/api/auth/login', {
        email,
        password
      });

      console.log('✅ Login Response:', response.data);

      const userData: User = {
        id: String(response.data.user.id),
        email: response.data.user.email,
        username: response.data.user.username,
        isVerified: response.data.user.is_verified,
        connectedPlatforms: response.data.user.connected_platforms || [],
        createdAt: response.data.user.created_at,
        updatedAt: response.data.user.updated_at
      };

      setAuth(userData, response.data.access_token);

      return { success: true, user: userData };
      
    } catch (error: any) {
      console.error('❌ Login error:', error);
      
      token.value = null;
      user.value = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
      
      throw error;
    }
  };
  
  const register = async (email: string, password: string, username?: string) => {
    try {
      console.log('📝 Registering user...', email);
      
      const response = await axios.post('/api/auth/register', {
        email,
        password,
        username
      });

      console.log('✅ Registration Response:', response.data);

      return { 
        success: true, 
        message: response.data.message || 'Registrierung erfolgreich. Bitte prüfe deine Emails.'
      };
      
    } catch (error: any) {
      console.error('❌ Registration error:', error);
      throw error;
    }
  };
  
  const logout = () => {
    console.log('🚪 Logging out...');
    token.value = null;
    user.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
  };
  
  const initAuth = () => {
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    
    console.log('🔄 Initializing auth from localStorage...', { 
      hasToken: !!storedToken, 
      hasUser: !!storedUser 
    });
    
    if (storedToken && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        
        // Ensure ID is string
        if (userData.id) {
          userData.id = String(userData.id);
        }
        
        token.value = storedToken;
        user.value = userData;
        axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        console.log('✅ Auth initialized:', { user: userData.email, isAuth: isAuthenticated.value });
      } catch (e) {
        console.error('❌ Failed to parse stored user:', e);
        logout();
      }
    } else {
      console.log('ℹ️  No stored auth found');
    }
  };
  
  const refreshUser = async () => {
    try {
      const response = await axios.get('/api/auth/me');
      
      const userData: User = {
        id: String(response.data.id),
        email: response.data.email,
        username: response.data.username,
        isVerified: response.data.is_verified,
        connectedPlatforms: response.data.connected_platforms || [],
        createdAt: response.data.created_at,
        updatedAt: response.data.updated_at
      };
      
      user.value = userData;
      localStorage.setItem('user', JSON.stringify(userData));
      
      return userData;
    } catch (error) {
      console.error('❌ Failed to refresh user:', error);
      throw error;
    }
  };
  
  return {
    // State
    user,
    token,
    
    // Getters
    isAuthenticated,
    userId,
    userEmail,
    userName,
    isVerified,
    
    // Actions
    login,
    register,
    logout,
    setAuth,
    initAuth,
    refreshUser
  };
});




