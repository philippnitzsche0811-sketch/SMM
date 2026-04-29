<template>
  <div class="upload-view">
    <div class="upload-card">
      <!-- Step Indicator -->
      <div class="steps">
        <div
          v-for="(step, idx) in steps"
          :key="idx"
          class="step-item"
          :class="{ active: currentStep > idx, current: currentStep === idx + 1 }"
        >
          <div class="step-dot">
            <i v-if="currentStep > idx + 1" class="pi pi-check"></i>
            <span v-else>{{ idx + 1 }}</span>
          </div>
          <span class="step-label">{{ step }}</span>
          <div v-if="idx < steps.length - 1" class="step-connector" :class="{ active: currentStep > idx + 1 }"></div>
        </div>
      </div>

      <!-- Step 1: Select Video -->
      <div v-show="currentStep === 1" class="step-content">
        <DragDropZone @file-selected="handleFileSelect" />
      </div>

      <!-- Step 2: Video Details -->
      <div v-show="currentStep === 2" class="step-content">
        <VideoMetaForm
          v-model:title="videoMeta.title"
          v-model:description="videoMeta.description"
          v-model:tags="videoMeta.tags"
          v-model:privacyStatus="videoMeta.privacyStatus"
          v-model:category="videoMeta.category"
        />
        <div class="nav-buttons">
          <Button label="Back" severity="secondary" outlined @click="currentStep = 1" />
          <Button label="Continue" @click="currentStep = 3" :disabled="!videoMeta.title" />
        </div>
      </div>

      <!-- Step 3: Choose Platforms -->
      <div v-show="currentStep === 3" class="step-content">
        <PlatformSelector v-model="selectedPlatforms" />
        <div class="nav-buttons">
          <Button label="Back" severity="secondary" outlined @click="currentStep = 2" />
          <Button
            label="Publish Now"
            icon="pi pi-upload"
            iconPos="right"
            @click="handleUpload"
            :loading="isUploading"
            :disabled="!canUpload"
          />
        </div>
      </div>

      <!-- Upload Progress -->
      <div v-if="isUploading" class="progress-section">
        <div class="progress-header">
          <i class="pi pi-spin pi-spinner"></i>
          <span>Uploading to your platforms...</span>
        </div>
        <ProgressBar :value="uploadProgress" />
        <p class="progress-pct">{{ uploadProgress }}% complete</p>
      </div>

      <!-- Upload Results -->
      <div v-if="uploadResults.length > 0" class="results-section">
        <h3 class="results-title">Upload Results</h3>
        <div class="results-list">
          <div
            v-for="result in uploadResults"
            :key="result.platform"
            class="result-item"
            :class="result.success ? 'success' : 'error'"
          >
            <i :class="result.success ? 'pi pi-check-circle' : 'pi pi-times-circle'"></i>
            <div class="result-body">
              <strong>{{ capitalizeFirst(result.platform) }}</strong>
              <a v-if="result.success && result.url" :href="result.url" target="_blank">View video</a>
              <span v-else-if="!result.success" class="result-error">{{ result.error }}</span>
            </div>
          </div>
        </div>
        <Button label="Upload Another Video" icon="pi pi-plus" outlined @click="resetUpload" class="mt-4" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import Button from 'primevue/button';
import ProgressBar from 'primevue/progressbar';
import { DragDropZone, VideoMetaForm, PlatformSelector } from '@/components/upload';
import { useUpload } from '@/composables/useUpload';
import { capitalizeFirst } from '@/utils/formatters';
import type { VideoMetadata } from '@/types/video.types';

const { uploadVideo, isUploading, uploadProgress, uploadResults, resetUpload: resetUploadState } = useUpload();

const steps = ['Select Video', 'Video Details', 'Platforms'];
const currentStep = ref(1);
const videoFile = ref<File | null>(null);
const videoMeta = ref<VideoMetadata>({
  title: '',
  description: '',
  tags: [],
  privacyStatus: 'private',
  category: 'default',
});
const selectedPlatforms = ref<string[]>([]);

const canUpload = computed(() =>
  !!videoFile.value && !!videoMeta.value.title && selectedPlatforms.value.length > 0
);

const handleFileSelect = (file: File) => {
  videoFile.value = file;
  currentStep.value = 2;
};

const handleUpload = async () => {
  if (!canUpload.value || !videoFile.value) return;
  try {
    await uploadVideo(videoFile.value, videoMeta.value, selectedPlatforms.value);
  } catch (error) {
    console.error('Upload error:', error);
  }
};

const resetUpload = () => {
  videoFile.value = null;
  videoMeta.value = { title: '', description: '', tags: [], privacyStatus: 'private', category: 'default' };
  selectedPlatforms.value = [];
  currentStep.value = 1;
  resetUploadState();
};
</script>

<style scoped>
.upload-view {
  max-width: 860px;
  margin: 0 auto;
}

.upload-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 2rem;
  box-shadow: var(--shadow-sm);
}

/* Step indicator */
.steps {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  margin-bottom: 2.5rem;
  gap: 0;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
  max-width: 140px;
}

.step-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-disabled);
  transition: all var(--transition-normal);
  position: relative;
  z-index: 1;
}

.step-item.current .step-dot {
  border-color: var(--primary-500);
  background: var(--primary-500);
  color: white;
}

.step-item.active .step-dot {
  border-color: #10b981;
  background: #10b981;
  color: white;
}

.step-label {
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  text-align: center;
  white-space: nowrap;
}

.step-item.current .step-label,
.step-item.active .step-label {
  color: var(--text-primary);
  font-weight: 600;
}

.step-connector {
  position: absolute;
  top: 17px;
  left: calc(50% + 18px);
  right: calc(-50% + 18px);
  height: 2px;
  background: var(--border-color);
  transition: background var(--transition-normal);
}

.step-connector.active {
  background: #10b981;
}

/* Content */
.step-content {
  min-height: 300px;
}

.nav-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

/* Progress */
.progress-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  margin-bottom: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.progress-pct {
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

/* Results */
.results-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.results-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.result-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
}

.result-item.success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #15803d;
}

.result-item.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.result-item i { font-size: 1.125rem; margin-top: 1px; }

.result-body {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.result-body a {
  font-size: 0.825rem;
  text-decoration: underline;
}

.result-error { font-size: 0.825rem; opacity: 0.85; }

.mt-4 { margin-top: 1rem; }

@media (max-width: 640px) {
  .upload-card { padding: 1.25rem; }
  .step-label  { display: none; }
  .nav-buttons { flex-direction: column-reverse; }
  .nav-buttons .p-button { width: 100%; justify-content: center; }
}
</style>
