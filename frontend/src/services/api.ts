import axios, { AxiosInstance, AxiosError } from 'axios';

// ==========================================
// Axios Instance
// ==========================================

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 Minuten für große Video-Uploads
  headers: { 'Content-Type': 'application/json' },
});

// Request Interceptor – Auth Token anhängen
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error),
);

// Response Interceptor – 401 → Login Redirect
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

// ==========================================
// Auth API
// ==========================================

export const login = async (email: string, password: string) => {
  const response = await api.post('/api/auth/login', { email, password });
  return response.data;
};

export const register = async (email: string, password: string, username?: string) => {
  const response = await api.post('/api/auth/register', { email, password, username });
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};

export const updateMe = async (data: { username?: string }) => {
  const response = await api.patch('/api/auth/me', data);
  return response.data;
};

export const changePassword = async (currentPassword: string, newPassword: string) => {
  const response = await api.post('/api/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return response.data;
};

export const forgotPassword = async (email: string) => {
  const response = await api.post('/api/auth/forgot-password', { email });
  return response.data;
};

export const resetPassword = async (token: string, newPassword: string) => {
  const response = await api.post('/api/auth/reset-password', { token, new_password: newPassword });
  return response.data;
};

// ==========================================
// Video API
// ==========================================

export const getUserVideos = async (userId: string) => {
  const response = await api.get(`/api/upload/videos/user/${userId}`);
  return response.data;
};

export const getVideoStatus = async (videoId: string) => {
  const response = await api.get(`/api/upload/video/${videoId}`);
  return response.data;
};

export const uploadVideo = async (formData: FormData, onProgress?: (percent: number) => void) => {
  const response = await api.post('/api/upload/upload_video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
    },
  });
  return response.data;
};

export const updateVideo = async (
  videoId: string,
  data: { user_id: string; title?: string; description?: string; tags?: string; privacy_status?: string },
) => {
  const response = await api.patch(`/api/upload/video/${videoId}`, data);
  return response.data;
};

export const deleteVideo = async (videoId: string, userId: string) => {
  const response = await api.delete(`/api/upload/video/${videoId}`, {
    data: { user_id: userId },
  });
  return response.data;
};

// ==========================================
// Platform Connection API
// ==========================================

export const connectTikTok = async (userId: string) => {
  const response = await api.post('/api/tiktok/connect', { user_id: userId });
  return response.data;
};

export const connectYouTube = async (userId: string, clientSecretsFile: File) => {
  const formData = new FormData();
  formData.append('user_id', userId);
  formData.append('client_secrets_file', clientSecretsFile);
  const response = await api.post('/api/youtube/connect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const connectInstagram = async (userId: string) => {
  const response = await api.post('/api/instagram/connect', { user_id: userId });
  return response.data;
};

export const disconnectPlatform = async (userId: string, platform: string) => {
  const response = await api.post(`/api/${platform}/disconnect`, { user_id: userId });
  return response.data;
};

export const refreshPlatformToken = async (userId: string, platform: string) => {
  const response = await api.post(`/api/${platform}/refresh`, { user_id: userId });
  return response.data;
};

// ==========================================
// Optimizer API
// ==========================================

export const optimizeSuggest = async (data: {
  user_id: string;
  title_draft: string;
  description_draft: string;
  category: string;
  platforms: string[];
  video_duration?: number;
}) => {
  const response = await api.post('/api/optimizer/suggest', data);
  return response.data;
};

// ==========================================
// Simple Upload
// ==========================================

export const simpleUpload = async (formData: FormData, onProgress?: (percent: number) => void) => {
  const response = await api.post('/api/upload/simple', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
    },
  });
  return response.data;
};

export const finalizeUpload = async (videoId: string, data: {
  user_id: string;
  title: string;
  description: string;
  tags: string[];
  platforms: string[];
  privacy_status: string;
  schedule_type: string;
  scheduled_at?: string;
  group_id?: string;
}) => {
  const response = await api.post(`/api/upload/finalize/${videoId}`, data);
  return response.data;
};

// ==========================================
// Smart Upload
// ==========================================

export const startSmartAnalysis = async (formData: FormData, onProgress?: (percent: number) => void) => {
  const response = await api.post('/api/smart-upload/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
    },
  });
  return response.data;
};

export const getSmartAnalysis = async (videoId: string) => {
  const response = await api.get(`/api/smart-upload/analysis/${videoId}`);
  return response.data;
};

export const scheduleSmartUpload = async (videoId: string, data: {
  user_id: string;
  platforms: string[];
  privacy_status: string;
  schedule_type: string;
  scheduled_at?: string;
  group_id?: string;
  ai_context?: string;
}) => {
  const response = await api.post(`/api/smart-upload/schedule/${videoId}`, data);
  return response.data;
};

// ==========================================
// Upload Groups
// ==========================================

export const createUploadGroup = async (data: {
  user_id: string;
  name: string;
  platforms: string[];
  privacy_status?: string;
  category?: string;
}) => {
  const response = await api.post('/api/upload-groups/', data);
  return response.data;
};

export const listUploadGroups = async (userId: string) => {
  const response = await api.get('/api/upload-groups/', { params: { user_id: userId } });
  return response.data;
};

// ==========================================
// Admin — Trend Data
// ==========================================

export interface AdminTrendDataIn {
  platform: string;
  category: string;
  top_tags?: string[];
  title_words?: string[];
  title_starters?: string[];
  notes?: string;
}

export interface AdminTrendDataOut {
  id: string;
  platform: string;
  category: string;
  top_tags?: string[];
  title_words?: string[];
  title_starters?: string[];
  notes?: string;
  updated_at?: string;
}

export const listAdminTrendData = async (): Promise<AdminTrendDataOut[]> => {
  const response = await api.get('/api/admin/trend-data');
  return response.data;
};

export const upsertAdminTrendData = async (data: AdminTrendDataIn): Promise<AdminTrendDataOut> => {
  const response = await api.post('/api/admin/trend-data', data);
  return response.data;
};

export const deleteAdminTrendData = async (id: string): Promise<void> => {
  await api.delete(`/api/admin/trend-data/${id}`);
};

export interface ParseRawResult {
  top_tags: string[];
  title_words: string[];
  title_starters: string[];
}

export const parseAdminRawText = async (
  rawText: string,
  platform: string,
  category: string,
): Promise<ParseRawResult> => {
  const response = await api.post('/api/admin/parse-raw', {
    raw_text: rawText,
    platform,
    category,
  });
  return response.data;
};

export const getUploadGroup = async (groupId: string) => {
  const response = await api.get(`/api/upload-groups/${groupId}`);
  return response.data;
};

export const addVideoToGroup = async (groupId: string, formData: FormData, onProgress?: (percent: number) => void) => {
  const response = await api.post(`/api/upload-groups/${groupId}/videos`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
    },
  });
  return response.data;
};

export const removeVideoFromGroup = async (groupId: string, gvId: string, userId: string) => {
  const response = await api.delete(`/api/upload-groups/${groupId}/videos/${gvId}`, {
    params: { user_id: userId },
  });
  return response.data;
};

export const patchUploadGroup = async (groupId: string, data: {
  user_id: string;
  name?: string;
  status?: string;
}) => {
  const response = await api.patch(`/api/upload-groups/${groupId}`, data);
  return response.data;
};

export const deleteUploadGroup = async (groupId: string, userId: string) => {
  const response = await api.delete(`/api/upload-groups/${groupId}`, {
    data: { user_id: userId },
  });
  return response.data;
};

export const getGroupSchedulePreview = async (groupId: string) => {
  const response = await api.get(`/api/upload-groups/${groupId}/schedule-preview`);
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


