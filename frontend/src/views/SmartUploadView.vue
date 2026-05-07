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

      <!-- Step 1: Upload + context (analysis starts immediately) -->
      <div v-show="currentStep === 1" class="step-content">
        <DragDropZone @file-selected="handleFileSelect" />

        <Transition name="slide-down">
          <div v-if="videoFile" class="step1-extra">
            <!-- Analyzing badge — non-blocking -->
            <div class="analysis-badge" :class="analysisStatusClass">
              <i :class="analysisIconClass"></i>
              {{ analysisStatusText }}
            </div>

            <div class="file-badge">
              <i class="pi pi-video"></i>
              {{ videoFile.name }}
            </div>

            <div class="divider"></div>

            <DescribeVideoStep v-model:context="aiContext" />

            <div class="divider"></div>

            <div class="field-group">
              <label>Upload to</label>
              <PlatformSelector v-model="selectedPlatforms" />
            </div>

            <div class="nav-buttons">
              <Button
                label="Continue to results"
                icon="pi pi-arrow-right"
                iconPos="right"
                :disabled="selectedPlatforms.length === 0"
                @click="goToResults"
              />
            </div>
          </div>
        </Transition>
      </div>

      <!-- Step 2: Analysis results + generated metadata -->
      <div v-if="currentStep === 2" class="step-content">

        <!-- Still analyzing -->
        <div v-if="isAnalyzing" class="analyzing-state">
          <div class="analyzing-icon">
            <i class="pi pi-spin pi-spinner"></i>
          </div>
          <div class="analyzing-text">
            <h3>Finishing analysis…</h3>
            <p>Claude Vision is examining your video frames. Just a moment.</p>
          </div>
        </div>

        <template v-else>
          <!-- Score + summary -->
          <div class="score-row" v-if="analysis?.result">
            <div class="score-badge" :class="scoreBadgeClass">
              {{ analysis.result.overall_score }}/10
            </div>
            <p class="score-summary">{{ analysis.result.summary }}</p>
          </div>

          <!-- Top 3 key insights (condensed) -->
          <div class="insights-row" v-if="topInsights.length">
            <div v-for="(insight, i) in topInsights" :key="i" class="insight-chip">
              <i class="pi pi-lightbulb"></i>
              {{ insight }}
            </div>
          </div>

          <div class="divider"></div>

          <!-- Title picker from video content -->
          <div class="review-section">
            <div class="review-header">
              <label class="review-label">Title</label>
              <span class="from-video-badge"><i class="pi pi-video"></i> generated from your video</span>
            </div>
            <TitlePickerPanel
              :options="titleOptions"
              v-model="meta.title"
            />
          </div>

          <div class="divider"></div>

          <!-- Description -->
          <div class="review-section">
            <label class="review-label">Description</label>
            <Textarea
              v-model="meta.description"
              :rows="4"
              class="w-full"
              placeholder="Video description…"
            />
          </div>

          <div class="divider"></div>

          <!-- Tags -->
          <div class="review-section">
            <label class="review-label">Tags</label>
            <div class="tags-row">
              <span v-for="(tag, i) in meta.tags" :key="i" class="tag-chip">
                #{{ tag }}
                <button class="tag-remove" @click="meta.tags.splice(i, 1)">×</button>
              </span>
              <input
                v-model="newTag"
                class="tag-input"
                placeholder="Add tag…"
                @keydown.enter.prevent="addTag"
                @keydown.comma.prevent="addTag"
              />
            </div>
          </div>
        </template>

        <div class="nav-buttons">
          <Button label="Back" severity="secondary" outlined @click="currentStep = 1" :disabled="isAnalyzing" />
          <Button label="Continue" @click="currentStep = 3" :disabled="!meta.title.trim() || isAnalyzing" />
        </div>
      </div>

      <!-- Step 3: Schedule -->
      <div v-if="currentStep === 3" class="step-content">
        <ScheduleStep
          v-model:scheduleType="scheduleType"
          v-model:scheduledAt="scheduledAt"
          v-model:selectedGroupId="selectedGroupId"
          :groups="groups"
          @create-group="showCreateGroupDialog = true"
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

  <!-- Inline: Create Upload Group dialog -->
  <Dialog
    v-model:visible="showCreateGroupDialog"
    header="Create Upload Group"
    :modal="true"
    :style="{ width: '400px' }"
    :closable="!isSaving"
  >
    <div class="dialog-field">
      <label>Group name</label>
      <InputText v-model="newGroupName" placeholder="e.g. Weekly Shorts" class="w-full" autofocus />
    </div>
    <template #footer>
      <Button label="Cancel" class="p-button-text" @click="showCreateGroupDialog = false" :disabled="isSaving" />
      <Button label="Create" icon="pi pi-plus" :loading="isSaving" :disabled="!newGroupName.trim()" @click="handleCreateGroup" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import { DragDropZone, PlatformSelector } from '@/components/upload';
import DescribeVideoStep from '@/components/upload/DescribeVideoStep.vue';
import ScheduleStep from '@/components/upload/ScheduleStep.vue';
import TitlePickerPanel from '@/components/upload/TitlePickerPanel.vue';
import { useSmartUpload } from '@/composables/useSmartUpload';
import { useUploadGroups } from '@/composables/useUploadGroups';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const {
  videoId, isUploading, uploadProgress, analysis, isAnalyzing, isScheduling, error,
  submitForAnalysis, schedule, reset: resetUpload,
} = useSmartUpload();
const { groups, fetchGroups, createGroup, isSaving } = useUploadGroups();

onMounted(() => {
  if (authStore.userId) fetchGroups(authStore.userId);
});

const steps = ['Upload', 'Review', 'Schedule'];
const currentStep = ref(1);
const videoFile = ref<File | null>(null);
const aiContext = ref('');
const newTag = ref('');

const meta = ref({
  title: '',
  description: '',
  tags: [] as string[],
});
const titleOptions = ref<string[]>([]);

const selectedPlatforms = ref<string[]>([]);
const scheduleType = ref('now');
const scheduledAt = ref<string | null>(null);
const selectedGroupId = ref<string | null>(null);
const showCreateGroupDialog = ref(false);
const newGroupName = ref('');
const done = ref(false);
const doneMessage = ref('');

// ── Analysis status UI ──────────────────────────────────────────────────────

const analysisStatusClass = computed(() => {
  if (isUploading.value) return 'status-uploading';
  if (isAnalyzing.value) return 'status-analyzing';
  if (analysis.value?.status === 'done') return 'status-done';
  if (analysis.value?.status === 'failed') return 'status-failed';
  return 'status-idle';
});

const analysisIconClass = computed(() => {
  if (isUploading.value || isAnalyzing.value) return 'pi pi-spin pi-spinner';
  if (analysis.value?.status === 'done') return 'pi pi-check-circle';
  if (analysis.value?.status === 'failed') return 'pi pi-times-circle';
  return 'pi pi-video';
});

const analysisStatusText = computed(() => {
  if (isUploading.value) return `Uploading… ${uploadProgress.value}%`;
  if (isAnalyzing.value) return 'Analyzing with Claude Vision…';
  if (analysis.value?.status === 'done') return 'Analysis complete';
  if (analysis.value?.status === 'failed') return 'Analysis failed — will use context only';
  return 'Analysis queued';
});

// ── Score + insights ────────────────────────────────────────────────────────

const scoreBadgeClass = computed(() => {
  const s = analysis.value?.result?.overall_score ?? 0;
  if (s >= 8) return 'score-green';
  if (s >= 6) return 'score-yellow';
  return 'score-red';
});

const topInsights = computed(() => {
  const r = analysis.value?.result;
  if (!r) return [];
  const all = [
    ...(r.pacing_suggestions ?? []),
    ...(r.content_quality ?? []),
  ];
  return all.slice(0, 3);
});

// ── Submit condition ────────────────────────────────────────────────────────

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

// ── File select — immediately start analysis ─────────────────────────────────

async function handleFileSelect(file: File) {
  videoFile.value = file;
  if (!authStore.userId) return;
  const title = file.name.replace(/\.[^.]+$/, '');
  await submitForAnalysis(file, authStore.userId, title);
}

// ── Step 1 → 2: populate metadata from analysis result ──────────────────────

function goToResults() {
  currentStep.value = 2;
  applyAnalysisMetadata();
}

function applyAnalysisMetadata() {
  const meta_sug = analysis.value?.result?.metadata_suggestions;
  if (meta_sug) {
    titleOptions.value = meta_sug.title_options?.length ? meta_sug.title_options : [];
    meta.value.title       = meta_sug.title_options?.[0] ?? meta.value.title;
    meta.value.description = meta_sug.description ?? '';
    meta.value.tags        = meta_sug.hashtags ?? [];
  }
}

// Watch for analysis completion and apply metadata if user is already on step 2
import { watch } from 'vue';
watch(() => analysis.value?.status, (status) => {
  if (status === 'done' && currentStep.value === 2 && !meta.value.title) {
    applyAnalysisMetadata();
  }
});

function addTag() {
  const t = newTag.value.replace(/^#/, '').trim();
  if (t && !meta.value.tags.includes(t)) meta.value.tags.push(t);
  newTag.value = '';
}

async function handleCreateGroup() {
  if (!newGroupName.value.trim() || !authStore.userId) return;
  try {
    const group = await createGroup(
      authStore.userId,
      newGroupName.value.trim(),
      selectedPlatforms.value.length ? selectedPlatforms.value : ['youtube'],
    );
    if (group) selectedGroupId.value = group.id;
    showCreateGroupDialog.value = false;
    newGroupName.value = '';
  } catch { /* composable handles error */ }
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
      title: meta.value.title,
      description: meta.value.description,
      tags: meta.value.tags,
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
  aiContext.value = '';
  meta.value = { title: '', description: '', tags: [] };
  titleOptions.value = [];
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
.back-link:hover { color: #8b5cf6; }

/* Step indicator */
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

/* Step 1 */
.step1-extra { margin-top: 1.25rem; display: flex; flex-direction: column; gap: 0; }

/* Analysis status badge */
.analysis-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.875rem;
  border-radius: 99px;
  font-size: 0.8rem;
  font-weight: 500;
  align-self: flex-start;
  margin-bottom: 0.75rem;
}
.status-idle      { background: rgba(255,255,255,0.05); color: var(--text-disabled); }
.status-uploading { background: rgba(79,127,255,0.12);  color: #7da5ff; }
.status-analyzing { background: rgba(139,92,246,0.12); color: #a78bfa; }
.status-done      { background: rgba(16,185,129,0.12); color: #34d399; }
.status-failed    { background: rgba(239,68,68,0.12);  color: #f87171; }

.file-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: rgba(139,92,246,0.06);
  border: 1px solid rgba(139,92,246,0.18);
  border-radius: 10px;
  font-size: 0.875rem;
  color: var(--text-secondary);
}
.file-badge i { color: #a78bfa; }

.field-group { display: flex; flex-direction: column; gap: 0.4rem; }
.field-group label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); }

/* Step 2 */
.analyzing-state {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 2rem;
  background: rgba(139,92,246,0.06);
  border: 1px solid rgba(139,92,246,0.2);
  border-radius: 14px;
  margin-bottom: 1rem;
}
.analyzing-icon { font-size: 2rem; color: #8b5cf6; flex-shrink: 0; }
.analyzing-text h3 { font-size: 1rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.25rem; }
.analyzing-text p  { font-size: 0.875rem; color: var(--text-secondary); margin: 0; }

.score-row {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
.score-badge {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9375rem;
  font-weight: 800;
  border: 2px solid;
}
.score-green  { background: rgba(16,185,129,0.12); color: #34d399; border-color: rgba(16,185,129,0.3); }
.score-yellow { background: rgba(245,158,11,0.12); color: #fbbf24; border-color: rgba(245,158,11,0.3); }
.score-red    { background: rgba(239,68,68,0.12);  color: #f87171; border-color: rgba(239,68,68,0.3); }

.score-summary { font-size: 0.875rem; color: var(--text-secondary); line-height: 1.55; margin: 0; }

.insights-row { display: flex; flex-direction: column; gap: 0.375rem; margin-bottom: 0.5rem; }
.insight-chip {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  padding: 0.375rem 0.625rem;
  background: rgba(255,255,255,0.02);
  border-radius: 8px;
}
.insight-chip i { color: #fbbf24; font-size: 0.75rem; flex-shrink: 0; margin-top: 2px; }

.review-section { display: flex; flex-direction: column; gap: 0.5rem; }
.review-header { display: flex; align-items: center; justify-content: space-between; }
.review-label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); display: block; margin-bottom: 0.25rem; }
.from-video-badge {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  color: #a78bfa;
  background: rgba(139,92,246,0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
}
.from-video-badge i { font-size: 0.65rem; }

/* Tags */
.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  min-height: 42px;
}
.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-radius: 6px;
  padding: 0.15rem 0.5rem;
  font-size: 0.8rem;
}
.tag-remove {
  background: none;
  border: none;
  color: var(--text-disabled);
  cursor: pointer;
  padding: 0;
  font-size: 1rem;
  line-height: 1;
  display: flex;
  align-items: center;
}
.tag-remove:hover { color: #f87171; }
.tag-input {
  flex: 1;
  min-width: 80px;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 0.875rem;
  padding: 0.15rem 0;
}

/* Shared */
.divider { height: 1px; background: var(--border-color); margin: 1.25rem 0; }

.nav-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.done-section { text-align: center; padding: 2.5rem 1rem; }
.done-icon { font-size: 3rem; color: #10b981; margin-bottom: 1rem; }
.done-section h3 { font-size: 1.1rem; color: var(--text-primary); margin: 0 0 1.5rem; }

/* Dialog */
.dialog-field { display: flex; flex-direction: column; gap: 0.4rem; padding: 0.25rem 0; }
.dialog-field label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); }

/* Slide-down transition */
.slide-down-enter-active { transition: all 0.3s ease; }
.slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from   { opacity: 0; transform: translateY(-8px); }
.slide-down-leave-to     { opacity: 0; transform: translateY(-8px); }

@media (max-width: 640px) {
  .upload-card { padding: 1.25rem; }
  .step-label   { display: none; }
  .nav-buttons  { flex-direction: column-reverse; }
}
</style>
