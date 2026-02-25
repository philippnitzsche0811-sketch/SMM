export type Platform = 'youtube' | 'tiktok' | 'instagram';

export interface PlatformStatus {
  connected: boolean;
  lastSync?: string;
  username?: string;
  channelId?: string;
}

export interface UserPlatforms {
  youtube?: PlatformStatus;
  tiktok?: PlatformStatus;
  instagram?: PlatformStatus;
}

export interface PlatformCredentials {
  platform: Platform;
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: string;
}

export interface ConnectPlatformRequest {
  userId: string;
  platform: Platform;
  authCode?: string;
  clientSecrets?: File;
}

export interface DisconnectPlatformRequest {
  userId: string;
  platform: Platform;
}

export interface PlatformInfo {
  id: Platform;
  name: string;
  icon: string;
  color: string;
  description: string;
  connected: boolean;
}
