<template>
  <div class="smart-upload-view">
    <div class="upload-card">
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

      <!-- Step 1: Upload file -->
      <div v-show="currentStep === 1" class="step-content">
        <DragDropZone @file-selected="handleFileSelect" />
        <div v-if="videoFile" class="file-selected">
          <i class="pi pi-video"></i>
          {{ videoFile.name }}
        </div>
        <div class="nav-buttons">
          <Button
            label="Analyze with AI"
            icon="pi pi-sparkles"
            iconPos="right"
            :disabled="!videoFile"
            :loading="isUploading"
            @click="handleStartAnalysis"
          />
        </div>
      </div>

      <!-- Step 2: Analyzing -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="analyzing-state">
          <div class="analyzing-icon">
            <i class="pi pi-spin pi-spinner" v-if="isAnalyzing"></i>
            <i class="pi pi-check-circle" v-else-if="analysis?.status === 'done'" style="color:#10b981;"></i>
            <i class="pi pi-times-circle" v-else-if="analysis?.status === 'failed'" style="color:#ef4444;"></i>
          </div>
          <div class="analyzing-text">
            <h3 v-if="isAnalyzing">Analyzing your video…</h3>
            <h3 v-else-if="analysis?.status === 'done'">Analysis complete!</h3>
            <h3 v-else>Analysis failed</h3>
            <p v-if="isAnalyzing">
              Claude Vision is examining {{ analysis?.frames_extracted || 0 }} frames for pacing, content quality, cuts, and sound.
            </p>
            <p v-else-if="analysis?.status === 'failed'">
              Something went wrong during analysis. You can still continue without feedback.
            </p>
          </div>
        </div>

        <!-- Upload progress bar (file transfer phase) -->
        <div v-if="uploadProgress > 0 && uploadProgress < 100" class="progress-section">
          <ProgressBar :value="uploadProgress" />
          <p class="progress-pct">Uploading file… {{ uploadProgress }}%</p>
        </div>

        <div class="nav-buttons" v-if="!isAnalyzing">
          <Button label="Continue to schedule" icon="pi pi-arrow-right" iconPos="right" @click="currentStep = 3" />
        </div>
      </div>

      <!-- Step 3: Feedback + schedule -->
      <div v-if="currentStep === 3" class="step-content">
        <div v-if="analysis?.result" class="feedback-wrap">
          <VideoAnalysisFeedback :result="analysis.result" />
          <div class="divider"></div>
        </div>

        <PlatformSelector v-model="selectedPlatforms" />

        <div class="divider"></div>

        <ScheduleStep
          v-model:scheduleType="scheduleType"
          v-model:scheduledAt="scheduledAt"
          v-model:selectedGroupId="selectedGroupId"
          :groups="groups"
        />

        <div class="nav-buttons">
          <Button label="Back" severity="secondary" outlined @click="currentStep = 2" />
          <Button
            :label="submitLabel"
            icon="pi pi-check"
            iconPos="right"
            :loading="isScheduling"
            :disabled="!canSubmit"
            @click="handleSchedule"
          />
        </div>
      </div>

      <!-- Done -->
      <div v-if="done" class="done-section">
        <div class="done-icon"><i class="pi pi-check-circle"></i></div>
        <h3>{{ doneMessage }}</h3>
        <Button label="Upload another video" icon="pi pi-plus" outlined @click="reset" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import ProgressBar from 'primevue/progressbar';
import { DragDropZone, PlatformSelector } from '@/components/upload';
import VideoAnalysisFeedback from '@/components/upload/VideoAnalysisFeedback.vue';
import ScheduleStep from '@/components/upload/ScheduleStep.vue';
import { useSmartUpload } from '@/composables/useSmartUpload';
import { useUploadGroups } from '@/composables/useUploadGroups';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const { videoId, isUploading, uploadProgress, analysis, isAnalyzing, isScheduling, error, submitForAnalysis, schedule, reset: resetUpload } = useSmartUpload();
const { groups, fetchGroups } = useUploadGroups();

onMounted(() => {
  if (authStore.userId) fetchGroups(authStore.userId);
});

const steps = ['Upload', 'Analyzing', 'Schedule'];
const currentStep = ref(1);
const videoFile = ref<File | null>(null);

const selectedPlatforms = ref<string[]>([]);
const scheduleType = ref('now');
const scheduledAt = ref<string | null>(null);
const selectedGroupId = ref<string | null>(null);
const done = ref(false);
const doneMessage = ref('');

const canSubmit = computed(() => {
  if (selectedPlatforms.value.length === 0) return false;
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
}

async function handleStartAnalysis() {
  if (!videoFile.value || !authStore.userId) return;
  const title = videoFile.value.name.replace(/\.[^.]+$/, '');
  await submitForAnalysis(videoFile.value, authStore.userId, title);
  currentStep.value = 2;
}

async function handleSchedule() {
  if (!videoId.value || !authStore.userId) return;
  try {
    await schedule(authStore.userId, {
      platforms: selectedPlatforms.value,
      privacy_status: 'private',
      schedule_type: scheduleType.value,
      scheduled_at: scheduledAt.value || undefined,
      group_id: selectedGroupId.value || undefined,
    });

    done.value = true;
    doneMessage.value = scheduleType.value === 'now'
      ? 'Upload started! Your video is being processed.'
      : scheduleType.value === 'group'
        ? 'Video added to group — it will upload at the scheduled time.'
        : 'Upload scheduled successfully.';

    toast.add({ severity: 'success', summary: 'Done!', detail: doneMessage.value, life: 5000 });
    currentStep.value = 1;
  } catch {
    toast.add({ severity: 'error', summary: 'Failed', detail: error.value || 'Something went wrong', life: 5000 });
  }
}

function reset() {
  resetUpload();
  videoFile.value = null;
  selectedPlatforms.value = [];
  scheduleType.value = 'now';
  scheduledAt.value = null;
  selectedGroupId.value = null;
  done.value = false;
  currentStep.value = 1;
}
</script>

<style scoped>
.smart-upload-view { max-width: 860px; margin: 0 auto; }

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

.steps {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  margin-bottom: 2.5rem;
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
.step-item.current .step-dot { border-color: #8b5cf6; background: #8b5cf6; color: white; box-shadow: 0 0 14px rgba(139,92,246,0.4); }
.step-item.active .step-dot  { border-color: #10b981; background: #10b981; color: white; }
.step-label { font-size: 0.78rem; font-weight: 500; color: var(--text-secondary); margin-top: 0.5rem; text-align: center; }
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

.file-selected {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  font-size: 0.875rem;
  color: var(--text-secondary);
}
.file-selected i { color: #7da5ff; }

.nav-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.analyzing-state {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  padding: 1.5rem;
  background: rgba(139,92,246,0.06);
  border: 1px solid rgba(139,92,246,0.2);
  border-radius: 14px;
  margin-bottom: 1.5rem;
}
.analyzing-icon { font-size: 2rem; color: #8b5cf6; flex-shrink: 0; }
.analyzing-text h3 { font-family: 'Poppins', sans-serif; font-size: 1rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.375rem; }
.analyzing-text p  { font-size: 0.875rem; color: var(--text-secondary); margin: 0; line-height: 1.5; }

.progress-section { margin: 1rem 0; }
.progress-pct { font-size: 0.8rem; color: var(--text-disabled); text-align: center; margin-top: 0.375rem; }

.feedback-wrap { margin-bottom: 0; }
.divider { height: 1px; background: var(--border-color); margin: 1.5rem 0; }

.done-section { text-align: center; padding: 2.5rem 1rem; }
.done-icon { font-size: 3rem; color: #10b981; margin-bottom: 1rem; }
.done-section h3 { font-size: 1.1rem; color: var(--text-primary); margin: 0 0 1.5rem; }

@media (max-width: 640px) {
  .upload-card { padding: 1.25rem; }
  .step-label   { display: none; }
  .nav-buttons  { flex-direction: column-reverse; }
}
</style>
