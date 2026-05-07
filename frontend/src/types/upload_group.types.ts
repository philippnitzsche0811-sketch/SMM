export interface UploadGroup {
  id: string;
  name: string;
  platforms: string[];
  privacy_status: string;
  category: string;
  status: 'active' | 'paused' | 'completed';
  video_count: number;
  next_upload: string | null;
  created_at: string;
  updated_at: string | null;
  videos?: GroupVideo[];
}

export interface GroupVideo {
  id: string;
  video_id: string;
  position: number;
  status: 'queued' | 'uploading' | 'done' | 'failed';
  scheduled_at: string | null;
  uploaded_at: string | null;
  ai_context: string | null;
  title: string | null;
  created_at: string;
}
