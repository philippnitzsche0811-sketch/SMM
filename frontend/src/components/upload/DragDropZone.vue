<template>
  <div
    class="drop-zone"
    :class="{ 'drag-over': isDragging, 'has-file': videoFile }"
    @drop.prevent="handleDrop"
    @dragover.prevent="isDragging = true"
    @dragleave="isDragging = false"
  >
    <input
      type="file"
      ref="fileInput"
      accept="video/*"
      @change="handleFileSelect"
      style="display: none"
    />

    <div v-if="!videoFile" class="drop-prompt">
      <div class="upload-icon-wrap">
        <i class="pi pi-cloud-upload"></i>
      </div>
      <h3>Drag & drop your video here</h3>
      <p>or</p>
      <Button label="Browse files" icon="pi pi-folder-open" @click="openFilePicker" />
      <small class="file-hint">MP4, MOV, AVI, MKV, WEBM &mdash; max 500 MB</small>
    </div>

    <div v-else class="file-preview">
      <video
        :src="videoUrl"
        controls
        class="video-player"
        @loadedmetadata="handleVideoMetadata"
      ></video>
      <div class="file-info-bar">
        <div class="file-details">
          <div class="file-icon"><i class="pi pi-video"></i></div>
          <div class="file-text">
            <strong>{{ videoFile.name }}</strong>
            <small>{{ formatFileSize(videoFile.size) }} &bull; {{ videoDuration }}</small>
          </div>
        </div>
        <Button
          icon="pi pi-times"
          severity="danger"
          text
          rounded
          @click="removeFile"
          v-tooltip.top="'Remove'"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import Button from 'primevue/button';
import { formatFileSize, formatDuration } from '@/utils/formatters';
import { isValidVideoFile, isValidFileSize } from '@/utils/validators';

const emit = defineEmits<{ fileSelected: [file: File] }>();

const isDragging   = ref(false);
const videoFile    = ref<File | null>(null);
const fileInput    = ref<HTMLInputElement>();
const videoDuration = ref('--:--');

const videoUrl = computed(() =>
  videoFile.value ? URL.createObjectURL(videoFile.value) : ''
);

const handleDrop = (e: DragEvent) => {
  isDragging.value = false;
  const f = e.dataTransfer?.files?.[0];
  if (f) handleFile(f);
};

const handleFileSelect = (e: Event) => {
  const f = (e.target as HTMLInputElement).files?.[0];
  if (f) handleFile(f);
};

const handleFile = (file: File) => {
  if (!isValidVideoFile(file)) {
    alert('Invalid file type. Please select a video file (MP4, MOV, AVI, MKV, WEBM).');
    return;
  }
  if (!isValidFileSize(file, 500)) {
    alert('File too large. Maximum size: 500 MB.');
    return;
  }
  videoFile.value = file;
  emit('fileSelected', file);
};

const handleVideoMetadata = (e: Event) => {
  videoDuration.value = formatDuration((e.target as HTMLVideoElement).duration);
};

const removeFile = () => {
  if (videoUrl.value) URL.revokeObjectURL(videoUrl.value);
  videoFile.value = null;
  videoDuration.value = '--:--';
  if (fileInput.value) fileInput.value.value = '';
};

const openFilePicker = () => fileInput.value?.click();
</script>

<style scoped>
.drop-zone {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-lg);
  padding: 2.5rem 2rem;
  text-align: center;
  transition: all var(--transition-normal);
  background: var(--bg-secondary);
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone.drag-over {
  border-color: var(--primary-400);
  background: var(--primary-50);
  transform: scale(1.01);
}

.drop-zone.has-file {
  border-style: solid;
  border-color: #10b981;
  background: white;
  padding: 1.5rem;
  align-items: stretch;
}

.drop-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.upload-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--primary-50);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--primary-400);
  margin-bottom: 0.25rem;
}

.drop-prompt h3 {
  margin: 0;
  font-size: 1.0625rem;
  color: var(--text-primary);
}

.drop-prompt p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.file-hint {
  color: var(--text-disabled);
  font-size: 0.8125rem;
  margin-top: 0.25rem;
}

/* File preview */
.file-preview {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.video-player {
  width: 100%;
  max-height: 380px;
  border-radius: var(--radius-md);
  background: #000;
}

.file-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.file-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--primary-50);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-500);
  font-size: 1rem;
}

.file-text {
  display: flex;
  flex-direction: column;
}

.file-text strong {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.file-text small {
  font-size: 0.78rem;
  color: var(--text-secondary);
}
</style>
