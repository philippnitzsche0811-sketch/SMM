<template>
  <div class="simple-upload-view">
    <div class="upload-card">
      <!-- Back link -->
      <button class="back-link" @click="router.push('/upload')">
        <i class="pi pi-arrow-left"></i> Upload modes
      </button>

      <!-- Step indicator -->
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

      <!-- Step 1: Select file -->
      <div v-show="currentStep === 1" class="step-content">
        <DragDropZone @file-selected="handleFileSelect" />
      </div>

      <!-- Step 2: Describe + AI toggle -->
      <div v-show="currentStep === 2" class="step-content">
        <VideoMetaForm
          v-model:title="meta.title"
          v-model:description="meta.description"
          v-model:tags="meta.tags"
          v-model:privacyStatus="meta.privacyStatus"
          v-model:category="meta.category"
        />
        <div class="divider"></div>
        <DescribeVideoStep
          v-model:context="aiContext"
          v-model:aiEnabled="aiEnabled"
        />
        <div class="nav-buttons">
          <Button label="Back" severity="secondary" outlined @click="currentStep = 1" />
          <Button label="Continue" @click="goToReview" :disabled="!meta.title" />
        </div>
      </div>

      <!-- Step 3: Review AI suggestions -->
      <div v-show="currentStep === 3" class="step-content">
        <div v-if="aiEnabled">
          <div v-if="isOptimizing" class="ai-loading">
            <i class="pi pi-spin pi-spinner"></i>
            <span>Claude is optimizing your content…</span>
          </div>
          <div v-else-if="aiSuggestions">
            <OptimizerPanel
              :suggestions="aiSuggestions"
              @apply-title="meta.title = $event"
              @apply-description="meta.description = $event"
              @apply-tags="meta.tags = $event"
            />
          </div>
        </div>
        <div v-else class="no-ai-note">
          <i class="pi pi-info-circle"></i>
          AI optimization is off — using your title and description as-is.
        </div>

        <div class="divider"></div>
        <PlatformSelector v-model="selectedPlatforms" />

        <div class="nav-buttons">
          <Button label="Back" severity="secondary" outlined @click="currentStep = 2" />
          <Button label="Continue" @click="currentStep = 4" :disabled="selectedPlatforms.length === 0" />
        </div>
      </div>

      <!-- Step 4: Schedule -->
      <div v-show="currentStep === 4" class="step-content">
        <ScheduleStep
          v-model:scheduleType="scheduleType"
          v-model:scheduledAt="scheduledAt"
          v-model:selectedGroupId="selectedGroupId"
          :groups="groups"
        />

        <div class="nav-buttons">
          <Button label="Back" severity="secondary" outlined @click="currentStep = 3" />
          <Button
            :label="submitLabel"
            icon="pi pi-check"
            iconPos="right"
            :loading="isSubmitting"
            :disabled="!canSubmit"
            @click="handleSubmit"
          />
        </div>
      </div>

      <!-- Upload progress -->
      <div v-if="isSubmitting" class="progress-section">
        <div class="progress-header">
          <i class="pi pi-spin pi-spinner"></i>
          <span>Uploading…</span>
        </div>
        <ProgressBar :value="uploadProgress" />
      </div>

      <!-- Done state -->
      <div v-if="done" class="done-section">
        <div class="done-icon"><i class="pi pi-check-circle"></i></div>
        <h3>{{ doneMessage }}</h3>
        <Button label="Upload another video" icon="pi pi-plus" outlined @click="reset" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import ProgressBar from 'primevue/progressbar';
import { DragDropZone, VideoMetaForm, PlatformSelector, OptimizerPanel } from '@/components/upload';
import DescribeVideoStep from '@/components/upload/DescribeVideoStep.vue';
import ScheduleStep from '@/components/upload/ScheduleStep.vue';
import { simpleUpload } from '@/services/api';
import { optimizeSuggest } from '@/services/api';
import { useUploadGroups } from '@/composables/useUploadGroups';
import type { VideoMetadata } from '@/types/video.types';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();
const { groups, fetchGroups } = useUploadGroups();

onMounted(() => {
  if (authStore.userId) fetchGroups(authStore.userId);
});

const steps = ['Select Video', 'Describe', 'Review', 'Schedule'];
const currentStep = ref(1);
const videoFile = ref<File | null>(null);

const meta = ref<VideoMetadata>({
  title: '',
  description: '',
  tags: [],
  privacyStatus: 'private',
  category: 'default',
});
const aiContext = ref('');
const aiEnabled = ref(true);
const aiSuggestions = ref<any>(null);
const isOptimizing = ref(false);

const selectedPlatforms = ref<string[]>([]);
const scheduleType = ref('now');
const scheduledAt = ref<string | null>(null);
const selectedGroupId = ref<string | null>(null);

const isSubmitting = ref(false);
const uploadProgress = ref(0);
const done = ref(false);
const doneMessage = ref('');

const canSubmit = computed(() => {
  if (scheduleType.value === 'datetime' && !scheduledAt.value) return false;
  if (scheduleType.value === 'group' && !selectedGroupId.value) return false;
  return true;
});

const submitLabel = computed(() => ({
  now: 'Publish Now',
  datetime: 'Schedule Upload',
  group: 'Add to Group',
}[scheduleType.value] ?? 'Submit'));

function handleFileSelect(file: File) {
  videoFile.value = file;
  if (!meta.value.title) meta.value.title = file.name.replace(/\.[^.]+$/, '');
  currentStep.value = 2;
}

async function goToReview() {
  currentStep.value = 3;
  if (aiEnabled.value && !aiSuggestions.value) {
    isOptimizing.value = true;
    try {
      const data = await optimizeSuggest({
        user_id: authStore.userId!,
        title_draft: meta.value.title,
        description_draft: aiContext.value || meta.value.description,
        category: meta.value.category || 'default',
        platforms: selectedPlatforms.value.length ? selectedPlatforms.value : ['youtube', 'tiktok', 'instagram'],
      });
      aiSuggestions.value = data.suggestions;
    } catch {
      // non-fatal — user can continue without suggestions
    } finally {
      isOptimizing.value = false;
    }
  }
}

async function handleSubmit() {
  if (!videoFile.value || !authStore.userId) return;
  isSubmitting.value = true;
  done.value = false;

  try {
    const formData = new FormData();
    formData.append('video', videoFile.value);
    formData.append('user_id', authStore.userId);
    formData.append('title', meta.value.title);
    formData.append('description', meta.value.description || '');
    formData.append('tags', (meta.value.tags || []).join(','));
    formData.append('platforms', selectedPlatforms.value.join(','));
    formData.append('privacy_status', meta.value.privacyStatus || 'private');
    formData.append('upload_mode', 'simple');
    formData.append('schedule_type', scheduleType.value);
    if (scheduledAt.value) formData.append('scheduled_at', scheduledAt.value);
    if (selectedGroupId.value) formData.append('group_id', selectedGroupId.value);

    await simpleUpload(formData, (pct) => { uploadProgress.value = pct; });

    done.value = true;
    doneMessage.value = scheduleType.value === 'now'
      ? 'Upload started! Your video is being processed.'
      : scheduleType.value === 'group'
        ? 'Video added to group — it will upload at the scheduled time.'
        : 'Upload scheduled successfully.';

    toast.add({ severity: 'success', summary: 'Done!', detail: doneMessage.value, life: 5000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Upload failed', detail: err.response?.data?.detail || 'Something went wrong', life: 5000 });
  } finally {
    isSubmitting.value = false;
  }
}

function reset() {
  videoFile.value = null;
  meta.value = { title: '', description: '', tags: [], privacyStatus: 'private', category: 'default' };
  aiContext.value = '';
  aiSuggestions.value = null;
  selectedPlatforms.value = [];
  scheduleType.value = 'now';
  scheduledAt.value = null;
  selectedGroupId.value = null;
  uploadProgress.value = 0;
  done.value = false;
  currentStep.value = 1;
}
</script>

<style scoped>
.simple-upload-view { max-width: 860px; margin: 0 auto; }

.upload-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 2rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.825rem;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-bottom: 1.5rem;
  transition: color 0.2s;
}
.back-link:hover { color: #4f7fff; }

/* Step indicator — reused from old UploadView */
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
  background: var(--bg-tertiary);
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
.step-item.current .step-dot { border-color: #4f7fff; background: #4f7fff; color: white; box-shadow: 0 0 14px rgba(79,127,255,0.4); }
.step-item.active .step-dot  { border-color: #10b981; background: #10b981; color: white; }
.step-label {
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  text-align: center;
  white-space: nowrap;
}
.step-item.current .step-label, .step-item.active .step-label { color: var(--text-primary); font-weight: 600; }
.step-connector {
  position: absolute;
  top: 17px;
  left: calc(50% + 18px);
  right: calc(-50% + 18px);
  height: 2px;
  background: var(--border-color);
  transition: background var(--transition-normal);
}
.step-connector.active { background: #10b981; }

.step-content { min-height: 260px; }

.divider { height: 1px; background: var(--border-color); margin: 1.5rem 0; }

.nav-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.ai-loading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.no-ai-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  padding: 0.75rem 1rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  margin-bottom: 1rem;
}
.no-ai-note i { color: var(--text-disabled); }

.progress-section { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color); }
.progress-header { display: flex; align-items: center; gap: 0.625rem; margin-bottom: 0.75rem; color: var(--text-secondary); font-weight: 500; }

.done-section { text-align: center; padding: 2.5rem 1rem; }
.done-icon { font-size: 3rem; color: #10b981; margin-bottom: 1rem; }
.done-section h3 { font-size: 1.1rem; color: var(--text-primary); margin: 0 0 1.5rem; }

@media (max-width: 640px) {
  .upload-card { padding: 1.25rem; }
  .step-label   { display: none; }
  .nav-buttons  { flex-direction: column-reverse; }
  .nav-buttons .p-button { width: 100%; justify-content: center; }
}
</style>
