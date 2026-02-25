import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  LoginCredentials,
  RegisterData,
  AuthResponse,
} from '@/types/user.types';
import type {
  VideoUploadRequest,
  VideoUploadResponse,
} from '@/types/video.types';

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create Axios Instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 Minuten für große Video-Uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor - Add Auth Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response Interceptor - Handle Errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status;

      if (status === 401) {
        console.error('🔒 Unauthorized - Token abgelaufen');
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      } else if (status === 403) {
        console.error('🚫 Forbidden - Keine Berechtigung');
      } else if (status >= 500) {
        console.error('💥 Server Error:', error.response.data);
      }
    } else if (error.request) {
      console.error('📡 Keine Antwort vom Server');
    } else {
      console.error('❌ Request Error:', error.message);
    }

    return Promise.reject(error);
  },
);

// ==========================================
// Authentication API
// ==========================================

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await api.post('/auth/login', credentials);
  return response.data;
};

export const register = async (data: RegisterData): Promise<AuthResponse> => {
  const { email, password } = data;
  const payload = { email, password };

  console.log('📤 Sending to backend:', payload);

  const response = await api.post('/auth/register', payload);
  return response.data;
};

export const logout = async (): Promise<void> => {
  await api.post('/auth/logout');
};

// Passwort vergessen
export const forgotPassword = async (email: string) => {
  const response = await api.post('/auth/forgot-password', { email });
  return response.data;
};

// Passwort zurücksetzen
export const resetPassword = async (token: string, newPassword: string) => {
  const response = await api.post('/auth/reset-password', {
    token,
    new_password: newPassword,
  });
  return response.data;
};

// ==========================================
// User API
// ==========================================

export const getUserStatus = async (userId: string) => {
  const response = await api.get(`/user/${userId}/status`);
  return response.data;
};

// ==========================================
// Video Upload API
// ==========================================

export const uploadVideo = async (formData: FormData): Promise<VideoUploadResponse> => {
  const response = await api.post('/api/upload/upload_video', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`📤 Upload Progress: ${percentCompleted}%`);
      }
    },
  });

  return response.data;
};

// ==========================================
// Video Management API
// ==========================================

export const getVideoStatus = async (videoId: string) => {
  const response = await api.get(`/api/upload/video/${videoId}`);
  return response.data;
};

export const getUserVideos = async (userId: string) => {
  const response = await api.get(`/api/upload/videos/user/${userId}`);
  return response.data;
};

export const updateVideo = async (
  videoId: string,
  data: {
    user_id: string;
    title?: string;
    description?: string;
    tags?: string;
    privacy_status?: string;
  },
) => {
  const response = await api.patch(`/api/upload/video/${videoId}`, data);
  return response.data;
};

/**
 * Löscht ein Video
 */
export const deleteVideo = async (videoId: string, userId: string) => {
  const response = await api.delete(`/api/upload/video/${videoId}`, {
    data: { user_id: userId },
  });
  return response.data;
};

// ==========================================
// Platform Connection API
// ==========================================

export const connectYouTube = async (userId: string, clientSecretsFile: File) => {
  const formData = new FormData();
  formData.append('user_id', userId);
  formData.append('client_secrets_file', clientSecretsFile);

  const response = await api.post('/api/youtube/connect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const connectTikTok = async (userId: string) => {
  const response = await api.post('/api/tiktok/connect', { user_id: userId });
  return response.data;
};

export const connectInstagram = async (userId: string) => {
  const response = await api.post('/api/instagram/connect', { user_id: userId });
  return response.data;
};

export const disconnectPlatform = async (userId: string, platform: string) => {
  const response = await api.post(`/${platform}/disconnect`, { user_id: userId });
  return response.data;
};

export const refreshPlatformToken = async (userId: string, platform: string) => {
  const response = await api.post(`/${platform}/refresh`, { user_id: userId });
  return response.data;
};

// ==========================================
// Health Check
// ==========================================

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;


