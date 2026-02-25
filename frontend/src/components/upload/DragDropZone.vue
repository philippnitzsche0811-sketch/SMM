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
      <i class="pi pi-cloud-upload"></i>
      <h3>Video hierher ziehen</h3>
      <p>oder</p>
      <Button 
        label="Datei auswählen" 
        icon="pi pi-folder-open"
        @click="openFilePicker"
      />
      <small class="file-info">
        Unterstützte Formate: MP4, MOV, AVI, MKV, WEBM (max. 500 MB)
      </small>
    </div>

    <div v-else class="file-preview">
      <video 
        :src="videoUrl" 
        controls 
        class="video-player"
        @loadedmetadata="handleVideoMetadata"
      ></video>
      <div class="file-info-box">
        <div class="file-details">
          <i class="pi pi-file"></i>
          <div class="file-text">
            <strong>{{ videoFile.name }}</strong>
            <small>{{ formatFileSize(videoFile.size) }} • {{ videoDuration }}</small>
          </div>
        </div>
        <Button 
          icon="pi pi-times"
          severity="danger"
          text
          rounded
          @click="removeFile"
          v-tooltip.top="'Entfernen'"
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

const emit = defineEmits<{
  fileSelected: [file: File];
}>();

const isDragging = ref(false);
const videoFile = ref<File | null>(null);
const fileInput = ref<HTMLInputElement>();
const videoDuration = ref('--:--');

const videoUrl = computed(() => 
  videoFile.value ? URL.createObjectURL(videoFile.value) : ''
);

const handleDrop = (e: DragEvent) => {
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    handleFile(files[0]);
  }
};

const handleFileSelect = (e: Event) => {
  const files = (e.target as HTMLInputElement).files;
  if (files && files.length > 0) {
    handleFile(files[0]);
  }
};

const handleFile = (file: File) => {
  // Validate file
  if (!isValidVideoFile(file)) {
    alert('Ungültiger Dateityp! Bitte wähle eine Video-Datei (MP4, MOV, AVI, MKV, WEBM).');
    return;
  }

  if (!isValidFileSize(file, 500)) {
    alert('Datei zu groß! Maximale Größe: 500 MB');
    return;
  }

  videoFile.value = file;
  emit('fileSelected', file);
};

const handleVideoMetadata = (e: Event) => {
  const video = e.target as HTMLVideoElement;
  videoDuration.value = formatDuration(video.duration);
};

const removeFile = () => {
  if (videoUrl.value) {
    URL.revokeObjectURL(videoUrl.value);
  }
  videoFile.value = null;
  videoDuration.value = '--:--';
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

const openFilePicker = () => {
  fileInput.value?.click();
};
</script>

<style scoped>
.drop-zone {
  border: 3px dashed var(--border-color);
  border-radius: var(--radius-lg);
  padding: 3rem 2rem;
  text-align: center;
  transition: all var(--transition-normal);
  background: var(--bg-secondary);
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone.drag-over {
  border-color: var(--primary-color);
  background: rgba(33, 150, 243, 0.05);
  transform: scale(1.02);
}

.drop-zone.has-file {
  border-style: solid;
  border-color: var(--success-color);
}

.drop-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.drop-prompt i {
  font-size: 4rem;
  color: var(--primary-color);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.drop-prompt h3 {
  margin: 0;
  color: var(--text-primary);
}

.drop-prompt p {
  margin: 0;
  color: var(--text-secondary);
}

.file-info {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-top: 1rem;
}

.file-preview {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.video-player {
  width: 100%;
  max-height: 400px;
  border-radius: var(--radius-md);
  background: black;
}

.file-info-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.file-details {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-details i {
  font-size: 2rem;
  color: var(--primary-color);
}

.file-text {
  display: flex;
  flex-direction: column;
}

.file-text strong {
  color: var(--text-primary);
}

.file-text small {
  color: var(--text-secondary);
}
</style>
