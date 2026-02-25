export interface User {
  id: string;
  email: string;
  username?: string;
  createdAt?: string;
  updatedAt?: string;
  connectedPlatforms?: Array<ConnectedPlatform>;
}

export interface ConnectedPlatform {
  platform: string;
  account_id?: string;
  connected_at?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  confirmPassword?: string;
}

// ✅ FIXIERT - Passt jetzt zum Backend Response
export interface AuthResponse {
  access_token: string;      // Backend sendet "access_token"
  token_type: string;         // Backend sendet "bearer"
  user: {
    user_id: string;          // Backend sendet "user_id"
    email: string;
    created_at: string;       // Backend sendet "created_at"
    connected_platforms: Array<ConnectedPlatform>;
  };
}

// Legacy Support (falls woanders noch verwendet)
export interface AuthResponseLegacy {
  user: User;
  token: string;
  refreshToken?: string;
  expiresIn?: number;
}

export interface UserProfile extends User {
  firstName?: string;
  lastName?: string;
  avatar?: string;
  bio?: string;
}

