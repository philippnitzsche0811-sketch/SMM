<template>
  <Card class="video-card">
    <template #header>
      <div class="video-thumbnail">
        <img 
          v-if="video.thumbnail" 
          :src="video.thumbnail" 
          :alt="video.title"
          @error="handleImageError"
        />
        <div v-else class="thumbnail-placeholder">
          <i class="pi pi-video"></i>
        </div>

        <!-- Status Badge -->
        <div class="status-badge">
          <Tag :value="statusText" :severity="statusSeverity" />
        </div>

        <!-- Duration Badge -->
        <div v-if="video.duration" class="duration-badge">
          {{ formatDuration(video.duration) }}
        </div>
      </div>
    </template>

    <template #content>
      <div class="video-info">
        <h4 class="video-title">{{ video.title }}</h4>

        <p v-if="video.description" class="video-description">
          {{ truncateText(video.description, 100) }}
        </p>

        <!-- Platforms -->
        <div class="video-platforms">
          <Tag 
            v-for="platform in video.platforms" 
            :key="platform"
            :value="platform"
            size="small"
            class="platform-badge"
          >
            <i :class="getPlatformIcon(platform)"></i>
            {{ platform }}
          </Tag>
        </div>

        <!-- Metadata -->
        <div class="video-metadata">
          <span class="metadata-item">
            <i class="pi pi-calendar"></i>
            {{ formatDate(video.createdAt) }}
          </span>
          <span v-if="video.views" class="metadata-item">
            <i class="pi pi-eye"></i>
            {{ formatNumber(video.views) }} Views
          </span>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="video-actions">
        <Button 
          icon="pi pi-eye"
          label="Ansehen"
          class="p-button-text p-button-sm"
          @click="$emit('view', video)"
        />
        <Button 
          icon="pi pi-pencil"
          label="Bearbeiten"
          class="p-button-text p-button-sm"
          @click="$emit('edit', video)"
        />
        <Button 
          icon="pi pi-trash"
          label="Löschen"
          class="p-button-text p-button-danger p-button-sm"
          @click="$emit('delete', video)"
        />
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Tag from 'primevue/tag';

interface Video {
  id: string;
  title: string;
  description?: string;
  thumbnail?: string;
  duration?: number;
  platforms: string[];
  status: 'uploaded' | 'pending' | 'failed' | 'processing';
  createdAt: string;
  views?: number;
}

const props = defineProps<{
  video: Video;
}>();

defineEmits<{
  view: [video: Video];
  edit: [video: Video];
  delete: [video: Video];
}>();

const statusText = computed(() => {
  const statusMap: Record<string, string> = {
    'uploaded': 'Hochgeladen',
    'pending': 'Ausstehend',
    'failed': 'Fehlgeschlagen',
    'processing': 'Verarbeitung'
  };
  return statusMap[props.video.status] || props.video.status;
});

const statusSeverity = computed(() => {
  const severityMap: Record<string, string> = {
    'uploaded': 'success',
    'pending': 'warning',
    'failed': 'danger',
    'processing': 'info'
  };
  return severityMap[props.video.status] || 'info';
});

const getPlatformIcon = (platform: string): string => {
  const icons: Record<string, string> = {
    'youtube': 'pi pi-youtube',
    'tiktok': 'pi pi-video',
    'instagram': 'pi pi-instagram'
  };
  return icons[platform.toLowerCase()] || 'pi pi-link';
};

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

const formatNumber = (num: number): string => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
};

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement;
  target.style.display = 'none';
};
</script>

<style scoped>
.video-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
}

.video-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.video-thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 aspect ratio */
  background: #f1f5f9;
  overflow: hidden;
}

.video-thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.thumbnail-placeholder i {
  font-size: 3rem;
  color: white;
  opacity: 0.5;
}

.status-badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
}

.duration-badge {
  position: absolute;
  bottom: 0.75rem;
  right: 0.75rem;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.video-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

.video-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;  /* ✅ Standard Property */
  -webkit-box-orient: vertical;
  overflow: hidden;
}


.video-description {
  margin: 0;
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.5;
}

.video-platforms {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.platform-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.video-metadata {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: auto;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.video-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .video-actions {
    flex-direction: column;
  }

  .video-actions button {
    width: 100%;
  }
}
</style>
