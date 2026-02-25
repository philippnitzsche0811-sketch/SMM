<template>
  <div class="upload-view">
    <!-- Header / Navigation -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <i class="pi pi-video"></i>
          <h2>Social Media Manager</h2>
        </div>

        <div class="header-right">
          <Button 
            label="Plattformen"
            icon="pi pi-link"
            severity="secondary"
            text
            @click="router.push('/connect')"
          />
          <Avatar 
            :label="userInitial" 
            shape="circle"
            style="background-color: #667eea; color: white"
          />
          <Button
            icon="pi pi-sign-out"
            severity="danger"
            text
            @click="handleLogout"
            v-tooltip.bottom="'Abmelden'"
          />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="upload-container">
      <Card class="upload-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-cloud-upload"></i>
            <span>Video hochladen</span>
          </div>
        </template>

        <template #content>
          <!-- Step Indicator -->
          <div class="steps">
            <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
              <div class="step-number">1</div>
              <span>Video auswählen</span>
            </div>
            <div class="step-line" :class="{ active: currentStep > 1 }"></div>
            <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
              <div class="step-number">2</div>
              <span>Details eingeben</span>
            </div>
            <div class="step-line" :class="{ active: currentStep > 2 }"></div>
            <div class="step" :class="{ active: currentStep >= 3 }">
              <div class="step-number">3</div>
              <span>Plattformen</span>
            </div>
          </div>

          <!-- Video Upload -->
          <div v-show="currentStep === 1">
            <DragDropZone @file-selected="handleFileSelect" />
          </div>

          <!-- Video Metadata -->
          <div v-show="currentStep === 2">
            <VideoMetaForm 
              v-model:title="videoMeta.title"
              v-model:description="videoMeta.description"
              v-model:tags="videoMeta.tags"
              v-model:privacyStatus="videoMeta.privacyStatus"
            />
            <div class="button-group">
              <Button label="Zurück" severity="secondary" @click="currentStep = 1" />
              <Button label="Weiter" @click="currentStep = 3" :disabled="!videoMeta.title" />
            </div>
          </div>

          <!-- Platform Selection -->
          <div v-show="currentStep === 3">
            <PlatformSelector v-model="selectedPlatforms" />
            <div class="button-group">
              <Button label="Zurück" severity="secondary" @click="currentStep = 2" />
              <Button 
                label="Jetzt hochladen"
                icon="pi pi-upload"
                iconPos="right"
                severity="success"
                @click="handleUpload"
                :loading="isUploading"
                :disabled="!canUpload"
              />
            </div>
          </div>

          <!-- Upload Progress -->
          <div v-if="isUploading" class="upload-progress-section">
            <Divider />
            <h3>Upload läuft...</h3>
            <ProgressBar :value="uploadProgress" />
            <p class="progress-text">{{ uploadProgress }}% hochgeladen</p>
          </div>

          <!-- Upload Results -->
          <div v-if="uploadResults.length > 0" class="upload-results">
            <Divider />
            <h3>Upload-Ergebnisse</h3>
            <div class="results-list">
              <Message 
                v-for="result in uploadResults" 
                :key="result.platform"
                :severity="result.success ? 'success' : 'error'"
                :closable="false"
              >
                <div class="result-content">
                  <strong>{{ capitalizeFirst(result.platform) }}</strong>
                  <span v-if="result.success && result.url">
                    <a :href="result.url" target="_blank">Video ansehen</a>
                  </span>
                  <span v-else-if="!result.success">{{ result.error }}</span>
                </div>
              </Message>
            </div>
            <Button 
              label="Neues Video hochladen" 
              icon="pi pi-plus"
              @click="resetUpload"
              class="mt-3"
            />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
import Divider from 'primevue/divider';
import ProgressBar from 'primevue/progressbar';
import Message from 'primevue/message';
import { DragDropZone, VideoMetaForm, PlatformSelector } from '@/components/upload';
import { useAuth } from '@/composables/useAuth';
import { useUpload } from '@/composables/useUpload';
import { capitalizeFirst } from '@/utils/formatters';
import type { VideoMetadata } from '@/types/video.types';

const router = useRouter();
const { user, logout } = useAuth();
const { upload, isUploading, uploadProgress, uploadResults, reset } = useUpload();

const currentStep = ref(1);
const videoFile = ref<File | null>(null);
const videoMeta = ref<VideoMetadata>({
  title: '',
  description: '',
  tags: [],
  privacyStatus: 'private'
});
const selectedPlatforms = ref<string[]>([]);

const userInitial = computed(() => {
  return user.value?.email?.charAt(0).toUpperCase() || 'U';
});

const canUpload = computed(() => {
  return videoFile.value && 
         videoMeta.value.title && 
         selectedPlatforms.value.length > 0;
});

const handleFileSelect = (file: File) => {
  videoFile.value = file;
  currentStep.value = 2;
};

const handleUpload = async () => {
  if (!canUpload.value || !videoFile.value) return;

  try {
    await upload(videoFile.value, videoMeta.value, selectedPlatforms.value);
  } catch (error) {
    console.error('Upload error:', error);
  }
};

const resetUpload = () => {
  videoFile.value = null;
  videoMeta.value = {
    title: '',
    description: '',
    tags: [],
    privacyStatus: 'private'
  };
  selectedPlatforms.value = [];
  currentStep.value = 1;
  reset();
};

const handleLogout = () => {
  logout();
};
</script>

<style scoped>
.upload-view {
  min-height: 100vh;
  background: var(--bg-secondary);
}

.app-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left i {
  font-size: 2rem;
  color: var(--primary-color);
}

.header-left h2 {
  margin: 0;
  font-size: 1.5rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.upload-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.upload-card {
  box-shadow: var(--shadow-md);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--primary-color);
}

.card-title i {
  font-size: 1.8rem;
}

.steps {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
  padding: 2rem 0;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  transition: all var(--transition-normal);
}

.step.active {
  color: var(--primary-color);
}

.step.completed {
  color: var(--success-color);
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  transition: all var(--transition-normal);
}

.step.active .step-number {
  border-color: var(--primary-color);
  background: var(--primary-color);
  color: white;
}

.step.completed .step-number {
  border-color: var(--success-color);
  background: var(--success-color);
  color: white;
}

.step-line {
  width: 100px;
  height: 2px;
  background: var(--border-color);
  margin: 0 1rem;
  transition: all var(--transition-normal);
}

.step-line.active {
  background: var(--primary-color);
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.upload-progress-section {
  margin-top: 2rem;
}

.progress-text {
  text-align: center;
  margin-top: 0.5rem;
  color: var(--text-secondary);
}

.upload-results {
  margin-top: 2rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.result-content a {
  color: var(--primary-color);
  text-decoration: underline;
}

@media (max-width: 768px) {
  .header-content {
    padding: 1rem;
  }

  .header-left h2 {
    display: none;
  }

  .upload-container {
    padding: 0 1rem;
  }

  .steps {
    font-size: 0.85rem;
  }

  .step-line {
    width: 50px;
  }

  .button-group {
    flex-direction: column;
  }
}
</style>
