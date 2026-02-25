/**
 * Validation utilities
 */

export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isStrongPassword = (password: string): boolean => {
  // Mindestens 8 Zeichen, 1 Großbuchstabe, 1 Kleinbuchstabe, 1 Zahl
  const minLength = password.length >= 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);

  return minLength && hasUpperCase && hasLowerCase && hasNumber;
};

export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const isValidVideoFile = (file: File): boolean => {
  const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm'];
  return validTypes.includes(file.type);
};

export const isValidFileSize = (file: File, maxSizeMB: number = 500): boolean => {
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  return file.size <= maxSizeBytes;
};

export const validateVideoMetadata = (title: string, description: string, tags: string[]): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (!title || title.trim().length === 0) {
    errors.push('Titel ist erforderlich');
  }

  if (title.length > 100) {
    errors.push('Titel darf maximal 100 Zeichen lang sein');
  }

  if (description.length > 5000) {
    errors.push('Beschreibung darf maximal 5000 Zeichen lang sein');
  }

  if (tags.length > 30) {
    errors.push('Maximal 30 Tags erlaubt');
  }

  return {
    valid: errors.length === 0,
    errors
  };
};
