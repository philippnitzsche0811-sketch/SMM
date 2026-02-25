<template>
  <Dialog 
    v-model:visible="visible"
    :header="isEditMode ? 'Video bearbeiten' : 'Neues Video hochladen'"
    :modal="true"
    :closable="true"
    :style="{ width: '50vw' }"
    @hide="handleClose"
  >
    <div class="video-edit-form">
      
      <!-- 🆕 VIDEO FILE UPLOAD (nur bei neuem Video) -->
      <div v-if="!isEditMode" class="form-field">
        <label for="video-file">Video-Datei *</label>
        <FileUpload
          mode="basic"
          name="video"
          accept="video/*"
          :maxFileSize="500000000"
          chooseLabel="Video auswählen"
          :auto="false"
          @select="handleFileSelect"
          :class="{ 'p-invalid': errors.file }"
        />
        
        <!-- Selected File Info -->
        <div v-if="selectedFile" class="selected-file-info">
          <i class="pi pi-video"></i>
          <div class="file-details">
            <span class="file-name">{{ selectedFile.name }}</span>
            <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
          </div>
          <Button 
            icon="pi pi-times" 
            class="p-button-text p-button-sm p-button-danger"
            @click="clearFile"
          />
        </div>
        
        <small v-if="errors.file" class="p-error">{{ errors.file }}</small>
      </div>

      <!-- Video Preview (if editing) -->
      <div v-if="isEditMode && localVideo.thumbnail" class="video-preview">
        <img :src="localVideo.thumbnail" :alt="localVideo.title" />
      </div>

      <!-- Title -->
      <div class="form-field">
        <label for="title">Titel *</label>
        <InputText 
          id="title"
          v-model="localVideo.title" 
          placeholder="Video-Titel eingeben"
          :class="{ 'p-invalid': errors.title }"
        />
        <small v-if="errors.title" class="p-error">{{ errors.title }}</small>
      </div>

      <!-- Description -->
      <div class="form-field">
        <label for="description">Beschreibung</label>
        <Textarea 
          id="description"
          v-model="localVideo.description" 
          placeholder="Video-Beschreibung eingeben"
          rows="4"
          auto-resize
        />
      </div>

      <!-- Platforms -->
      <div class="form-field">
        <label>Plattformen *</label>
        <div class="platforms-selector">
          <div 
            v-for="platform in availablePlatforms" 
            :key="platform.id"
            class="platform-option"
            :class="{ 
              'selected': isPlatformSelected(platform.id),
              'disabled': !platform.connected
            }"
            @click="togglePlatform(platform.id)"
          >
            <Checkbox 
              :modelValue="isPlatformSelected(platform.id)" 
              :binary="true"
              :disabled="!platform.connected"
            />
            <i :class="platform.icon" :style="{ color: platform.color }"></i>
            <span>{{ platform.name }}</span>
            <Tag 
              v-if="!platform.connected" 
              value="Nicht verbunden" 
              severity="warning"
              size="small"
            />
          </div>
        </div>
        <small v-if="errors.platforms" class="p-error">{{ errors.platforms }}</small>
      </div>

      <!-- Tags -->
      <div class="form-field">
        <label for="tags">Tags (mit Komma getrennt)</label>
        <InputText 
          id="tags"
          v-model="localVideo.tags" 
          placeholder="z.B. tutorial, gaming, vlog"
        />
      </div>

      <!-- Category -->
      <div class="form-field">
        <label for="category">Kategorie</label>
        <Dropdown 
          id="category"
          v-model="localVideo.category" 
          :options="categories"
          placeholder="Kategorie auswählen"
          optionLabel="label"
          optionValue="value"
        />
      </div>

      <!-- Privacy -->
      <div class="form-field">
        <label>Sichtbarkeit</label>
        <div class="privacy-options">
          <div 
            v-for="option in privacyOptions" 
            :key="option.value"
            class="privacy-option"
            :class="{ 'selected': localVideo.privacy === option.value }"
            @click="localVideo.privacy = option.value"
          >
            <RadioButton 
              v-model="localVideo.privacy" 
              :value="option.value"
            />
            <div class="privacy-info">
              <span class="privacy-label">{{ option.label }}</span>
              <small class="privacy-description">{{ option.description }}</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Schedule (optional) -->
      <div class="form-field">
        <div class="schedule-toggle">
          <Checkbox v-model="scheduleEnabled" :binary="true" />
          <label>Upload planen</label>
        </div>

        <Calendar 
          v-if="scheduleEnabled"
          v-model="localVideo.scheduledDate"
          showTime
          hourFormat="24"
          placeholder="Datum und Uhrzeit auswählen"
        />
      </div>
      
      <!-- 🆕 Upload Progress -->
      <div v-if="uploading" class="upload-progress">
        <ProgressBar :value="uploadProgress" />
        <span class="progress-text">{{ uploadProgress }}% hochgeladen</span>
      </div>
    </div>

      <!-- In VideoEditModal.vue -->

<!-- 🆕 VIDEO FILE UPLOAD (nur bei neuem Video) -->
<div v-if="!isEditMode" class="form-field">
  <label for="video-file">Video-Datei *</label>
  <FileUpload
    mode="basic"
    name="video"
    accept="video/*"
    :maxFileSize="500000000"
    chooseLabel="Video auswählen"
    :auto="false"
    @select="handleFileSelect"
    :class="{ 'p-invalid': errors.file }"
  />
  
  <!-- Selected File Info -->
  <div v-if="selectedFile" class="selected-file-info">
    <i class="pi pi-video"></i>
    <div class="file-details">
      <span class="file-name">{{ selectedFile.name }}</span>
      <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
    </div>
    <Button 
      icon="pi pi-times" 
      class="p-button-text p-button-sm p-button-danger"
      @click="clearFile"
    />
  </div>
  
  <small v-if="errors.file" class="p-error">{{ errors.file }}</small>
</div>

    <template #footer>
      <div class="dialog-footer">
        <Button 
          label="Abbrechen" 
          icon="pi pi-times"
          class="p-button-text"
          :disabled="uploading"
          @click="handleClose"
        />
        <Button 
          :label="isEditMode ? 'Speichern' : 'Hochladen'"
          icon="pi pi-check"
          :loading="saving || uploading"
          @click="handleSave"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import RadioButton from 'primevue/radiobutton';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Tag from 'primevue/tag';
import FileUpload from 'primevue/fileupload'; // 🆕
import ProgressBar from 'primevue/progressbar'; // 🆕

type VideoPrivacy = 'public' | 'private' | 'unlisted';

interface Video {
  id?: string;
  title: string;
  description?: string;
  thumbnail?: string;
  platforms: string[];
  tags?: string;
  category?: string;
  privacy: VideoPrivacy;
  scheduledDate?: Date;
}

interface Props {
  modelValue: boolean;
  video?: Video | null;
}

const props = withDefaults(defineProps<Props>(), {
  video: null
});

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  'save': [video: Video, file?: File];
}>();

const authStore = useAuthStore();

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const isEditMode = computed(() => !!props.video?.id);

const localVideo = ref<Video>({
  title: '',
  description: '',
  platforms: [],
  privacy: 'public',
  tags: '',
  category: ''
});

// 🆕 File Upload State
const selectedFile = ref<File | null>(null);
const uploading = ref(false);
const uploadProgress = ref(0);

const scheduleEnabled = ref(false);
const saving = ref(false);
const errors = ref<Record<string, string>>({});

// Available Platforms
const availablePlatforms = computed(() => [
  {
    id: 'youtube',
    name: 'YouTube',
    icon: 'pi pi-youtube',
    color: '#FF0000',
    connected: authStore.user?.connectedPlatforms?.some(p => p.platform === 'youtube')
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: 'pi pi-video',
    color: '#000000',
    connected: authStore.user?.connectedPlatforms?.some(p => p.platform === 'tiktok')
  },
  {
    id: 'instagram',
    name: 'Instagram',
    icon: 'pi pi-instagram',
    color: '#E4405F',
    connected: authStore.user?.connectedPlatforms?.some(p => p.platform === 'instagram')
  }
]);

const categories = [
  { label: 'Gaming', value: 'gaming' },
  { label: 'Bildung', value: 'education' },
  { label: 'Unterhaltung', value: 'entertainment' },
  { label: 'Musik', value: 'music' },
  { label: 'Sport', value: 'sports' },
  { label: 'Technologie', value: 'technology' },
  { label: 'Vlog', value: 'vlog' },
  { label: 'Sonstiges', value: 'other' }
];

const privacyOptions: Array<{
  value: VideoPrivacy;
  label: string;
  description: string;
}> = [
  {
    value: 'public',
    label: 'Öffentlich',
    description: 'Jeder kann das Video sehen'
  },
  {
    value: 'unlisted',
    label: 'Nicht gelistet',
    description: 'Nur mit Link sichtbar'
  },
  {
    value: 'private',
    label: 'Privat',
    description: 'Nur du kannst das Video sehen'
  }
];

// 🆕 File Handling
const handleFileSelect = (event: any) => {
  if (event.files && event.files.length > 0) {
    selectedFile.value = event.files[0];
    errors.value.file = '';
    
    // Auto-fill title from filename if empty
    if (!localVideo.value.title) {
      const filename = selectedFile.value.name.replace(/\.[^/.]+$/, '');
      localVideo.value.title = filename;
    }
  }
};

const clearFile = () => {
  selectedFile.value = null;
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

// Watch for video prop changes
watch(() => props.video, (newVideo) => {
  if (newVideo) {
    localVideo.value = { ...newVideo };
    scheduleEnabled.value = !!newVideo.scheduledDate;
  }
}, { immediate: true, deep: true });

const isPlatformSelected = (platformId: string): boolean => {
  return localVideo.value.platforms.includes(platformId);
};

const togglePlatform = (platformId: string) => {
  const platform = availablePlatforms.value.find(p => p.id === platformId);
  if (!platform?.connected) return;

  const index = localVideo.value.platforms.indexOf(platformId);
  if (index > -1) {
    localVideo.value.platforms.splice(index, 1);
  } else {
    localVideo.value.platforms.push(platformId);
  }
};

const validate = (): boolean => {
  errors.value = {};

  // File required for new upload
  if (!isEditMode.value && !selectedFile.value) {
    errors.value.file = 'Bitte wähle eine Video-Datei aus';
  }

  if (!localVideo.value.title.trim()) {
    errors.value.title = 'Titel ist erforderlich';
  }

  if (localVideo.value.platforms.length === 0) {
    errors.value.platforms = 'Mindestens eine Plattform auswählen';
  }

  return Object.keys(errors.value).length === 0;
};

const handleSave = async () => {
  if (!validate()) return;

  saving.value = true;
  uploading.value = !isEditMode.value; // Show progress for new uploads
  
  try {
    // Simulate upload progress (replace with real upload later)
    if (!isEditMode.value && selectedFile.value) {
      uploadProgress.value = 0;
      const interval = setInterval(() => {
        uploadProgress.value += 10;
        if (uploadProgress.value >= 100) {
          clearInterval(interval);
        }
      }, 300);
    }
    
    emit('save', { ...localVideo.value }, selectedFile.value || undefined);
    
    // Wait a bit for progress animation
    if (uploading.value) {
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
    
    handleClose();
  } catch (error) {
    console.error('Save error:', error);
  } finally {
    saving.value = false;
    uploading.value = false;
    uploadProgress.value = 0;
  }
};

const handleClose = () => {
  visible.value = false;
  // Reset form
  localVideo.value = {
    title: '',
    description: '',
    platforms: [],
    privacy: 'public',
    tags: '',
    category: ''
  };
  selectedFile.value = null;
  scheduleEnabled.value = false;
  errors.value = {};
  uploadProgress.value = 0;
};
</script>

<style scoped>
.video-edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 🆕 File Upload Styles */
.selected-file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  margin-top: 0.5rem;
}

.selected-file-info i {
  font-size: 1.5rem;
  color: #0284c7;
}

.file-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  font-weight: 500;
  color: #0c4a6e;
}

.file-size {
  font-size: 0.875rem;
  color: #64748b;
}

.upload-progress {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #f0f9ff;
  border-radius: 8px;
}

.progress-text {
  text-align: center;
  font-weight: 500;
  color: #0284c7;
}

.video-preview {
  width: 100%;
  max-height: 200px;
  overflow: hidden;
  border-radius: 8px;
}

.video-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.875rem;
}

.platforms-selector {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.platform-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.platform-option:hover:not(.disabled) {
  border-color: #3b82f6;
  background: #eff6ff;
}

.platform-option.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.platform-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.platform-option i {
  font-size: 1.5rem;
}

.platform-option span {
  flex: 1;
  font-weight: 500;
}

.privacy-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.privacy-option {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.privacy-option:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.privacy-option.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.privacy-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.privacy-label {
  font-weight: 600;
  color: #1e293b;
}

.privacy-description {
  color: #64748b;
  font-size: 0.875rem;
}

.schedule-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.p-error {
  color: #dc2626;
  font-size: 0.875rem;
}
</style>
