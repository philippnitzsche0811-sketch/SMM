// src/types/video.types.ts

export type VideoPrivacy = 'public' | 'private' | 'unlisted';
export type VideoStatus = 'uploaded' | 'pending' | 'failed' | 'processing';

export interface Video {
  id: string;
  title: string;
  description?: string;
  thumbnail?: string;
  platforms: string[];
  tags?: string;
  category?: string;
  privacy: VideoPrivacy;
  status: VideoStatus;
  createdAt: string;
  updatedAt?: string;
  views?: number;
  duration?: number;
  scheduledDate?: Date;
}

export interface VideoUploadRequest {
  title: string;
  description?: string;
  platforms: string[];
  tags?: string;
  category?: string;
  privacy: VideoPrivacy;
  scheduledDate?: Date;
}

// ✅ Upload-Ergebnis für einzelne Plattform
export interface UploadResult {
  platform: string;
  success: boolean;
  url?: string;
  error?: string;
  videoId?: string;
}

// ✅ Erweiterte Response
export interface VideoUploadResponse {
  success: boolean;
  videoId: string;
  message: string;
  results?: UploadResult[];  // ✅ Array von Ergebnissen
  status?: VideoStatus;
}

// ✅ Form-Daten für Upload-Interface
export interface VideoMetadata {
  title: string;
  description?: string;
  tags?: string[];
  privacyStatus?: VideoPrivacy;
  category?: string;
  scheduledDate?: Date;
}



