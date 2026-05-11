<template>
  <div class="simple-upload-view">
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

      <!-- Step 1: Drop file → fields appear inline -->
      <div v-show="currentStep === 1" class="step-content">
        <DragDropZone @file-selected="handleFileSelect" />

        <Transition name="slide-down">
          <div v-if="videoFile" class="step1-extra">
            <div class="file-badge">
              <i class="pi pi-video"></i>
              {{ videoFile.name }}
            </div>

            <div class="divider"></div>

            <!-- Title -->
            <div class="field-group">
              <label>Video title <span class="required">*</span></label>
              <InputText
                v-model="meta.title"
                placeholder="Your video title…"
                class="w-full"
                :maxlength="200"
              />
              <small class="field-hint">The AI will use this as a starting point to generate better titles.</small>
            </div>

            <div class="divider"></div>

            <!-- Context (AI input) -->
            <DescribeVideoStep v-model:context="aiContext" />

            <div class="divider"></div>

            <!-- Category inline (compact row) -->
            <div class="category-row">
              <label>Category</label>
              <Dropdown
                v-model="meta.category"
                :options="categoryOptions"
                optionLabel="label"
                optionValue="value"
                class="category-dropdown"
              />
            </div>

            <div class="divider"></div>

            <!-- Platforms -->
            <div class="field-group">
              <label>Upload to <span class="required">*</span></label>
              <PlatformSelector v-model="selectedPlatforms" />
            </div>

            <div class="nav-buttons">
              <Button
                label="Generate with AI"
                icon="pi pi-sparkles"
                iconPos="right"
                :loading="isOptimizing"
                :disabled="selectedPlatforms.length === 0 || !meta.title.trim()"
                @click="goToReview"
              />
            </div>
          </div>
        </Transition>
      </div>

      <!-- Step 2: AI review — title picker + desc + tags -->
      <div v-show="currentStep === 2" class="step-content">
        <div v-if="isOptimizing" class="ai-loading">
          <i class="pi pi-spin pi-spinner"></i>
          <span>Generating optimized content…</span>
        </div>

        <template v-else>
          <!-- Live data badge -->
          <div v-if="liveDataAge" class="live-data-badge">
            <i class="pi pi-globe"></i>
            Powered by live YouTube data · Updated {{ liveDataAge }}
          </div>

          <!-- Title picker -->
          <div class="review-section">
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
              <span
                v-for="(tag, i) in meta.tags"
                :key="i"
                class="tag-chip"
              >
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

          <div class="divider"></div>

          <!-- Visibility -->
          <div class="field-group">
            <label class="review-label">Visibility</label>
            <Dropdown
              v-model="meta.privacyStatus"
              :options="privacyOptions"
              optionLabel="label"
              optionValue="value"
              style="width: 220px"
            />
          </div>

          <div class="regen-row">
            <Button
              label="Regenerate"
              icon="pi pi-refresh"
              severity="secondary"
              outlined
              size="small"
              :loading="isRegenerating"
              @click="regenerate"
            />
            <span class="regen-hint">Re-runs AI with the same context</span>
          </div>
        </template>

        <div class="nav-buttons">
          <Button label="Back" severity="secondary" outlined @click="currentStep = 1" :disabled="isOptimizing" />
          <Button label="Continue" @click="currentStep = 3" :disabled="!meta.title.trim() || isOptimizing" />
        </div>
      </div>

      <!-- Step 3: Schedule -->
      <div v-show="currentStep === 3" class="step-content">
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
import ProgressBar from 'primevue/progressbar';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import { DragDropZone, PlatformSelector } from '@/components/upload';
import DescribeVideoStep from '@/components/upload/DescribeVideoStep.vue';
import ScheduleStep from '@/components/upload/ScheduleStep.vue';
import TitlePickerPanel from '@/components/upload/TitlePickerPanel.vue';
import { simpleUpload, optimizeSuggest } from '@/services/api';
import { useUploadGroups } from '@/composables/useUploadGroups';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();
const { groups, fetchGroups, createGroup, isSaving } = useUploadGroups();

onMounted(() => {
  if (authStore.userId) fetchGroups(authStore.userId);
});

const steps = ['Upload', 'Review', 'Schedule'];
const currentStep = ref(1);
const videoFile = ref<File | null>(null);

const meta = ref({
  title: '',
  description: '',
  tags: [] as string[],
  privacyStatus: 'private',
  category: 'default',
});
const titleOptions = ref<string[]>([]);
const aiContext = ref('');
const isOptimizing = ref(false);
const isRegenerating = ref(false);
const trendRefreshedAt = ref<string | null>(null);

const liveDataAge = computed(() => {
  if (!trendRefreshedAt.value) return null;
  const ageMs = Date.now() - new Date(trendRefreshedAt.value).getTime();
  const ageHours = Math.floor(ageMs / 3_600_000);
  if (ageHours >= 6) return null;
  return ageHours === 0 ? 'just now' : `${ageHours}h ago`;
});
const newTag = ref('');

const selectedPlatforms = ref<string[]>([]);
const scheduleType = ref('now');
const scheduledAt = ref<string | null>(null);
const selectedGroupId = ref<string | null>(null);
const showCreateGroupDialog = ref(false);
const newGroupName = ref('');

const isSubmitting = ref(false);
const uploadProgress = ref(0);
const done = ref(false);
const doneMessage = ref('');

const privacyOptions = [
  { label: 'Private',  value: 'private'  },
  { label: 'Unlisted', value: 'unlisted' },
  { label: 'Public',   value: 'public'   },
];

const categoryOptions = [
  { label: 'Default',        value: 'default'        },
  { label: 'Entertainment',  value: 'entertainment'  },
  { label: 'Education',      value: 'education'      },
  { label: 'Gaming',         value: 'gaming'         },
  { label: 'Music',          value: 'music'          },
  { label: 'Sports',         value: 'sports'         },
  { label: 'Tech',           value: 'tech'           },
  { label: 'Lifestyle',      value: 'lifestyle'      },
];

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
  if (!meta.value.title) {
    const raw = file.name.replace(/\.[^.]+$/, '');
    meta.value.title = raw.replace(/[_\-]+/g, ' ').replace(/\s+/g, ' ').trim()
      .replace(/\b\w/g, c => c.toUpperCase());
  }
}

async function runOptimize(isRegen = false) {
  if (isRegen) isRegenerating.value = true;
  else isOptimizing.value = true;

  try {
    const data = await optimizeSuggest({
      user_id: authStore.userId!,
      title_draft: meta.value.title,
      description_draft: aiContext.value || meta.value.title,
      category: meta.value.category || 'default',
      platforms: selectedPlatforms.value,
    });

    const sug: any = data.suggestions?.youtube
      ?? Object.values(data.suggestions || {})[0];

    trendRefreshedAt.value = data.trend_refreshed_at ?? null;

    if (sug) {
      titleOptions.value = sug.title_options?.length ? sug.title_options : [sug.title];
      meta.value.title       = sug.title_options?.[0] ?? sug.title ?? meta.value.title;
      meta.value.description = sug.description ?? meta.value.description;
      meta.value.tags        = sug.tags ?? meta.value.tags;
    }
  } catch {
    // non-fatal
    toast.add({ severity: 'warn', summary: 'AI unavailable', detail: 'Could not generate suggestions — fill in manually.', life: 4000 });
  } finally {
    isOptimizing.value = false;
    isRegenerating.value = false;
  }
}

async function goToReview() {
  currentStep.value = 2;
  await runOptimize(false);
}

async function regenerate() {
  await runOptimize(true);
}

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
      meta.value.privacyStatus || 'private',
      meta.value.category || 'default',
    );
    if (group) selectedGroupId.value = group.id;
    showCreateGroupDialog.value = false;
    newGroupName.value = '';
  } catch { /* composable handles error */ }
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
  titleOptions.value = [];
  aiContext.value = '';
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

/* Step 1 extras */
.step1-extra { margin-top: 1.25rem; }

.file-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: rgba(79,127,255,0.06);
  border: 1px solid rgba(79,127,255,0.2);
  border-radius: 10px;
  font-size: 0.875rem;
  color: var(--text-secondary);
}
.file-badge i { color: #7da5ff; }

.field-group { display: flex; flex-direction: column; gap: 0.4rem; }
.field-group label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); }
.required { color: #f87171; }
.field-hint { font-size: 0.78rem; color: var(--text-disabled); }

.category-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.category-row label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
  flex-shrink: 0;
}
.category-dropdown { width: 200px; }

/* Step 2 review */
.review-section { display: flex; flex-direction: column; gap: 0.5rem; }
.review-label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); display: block; margin-bottom: 0.25rem; }

.review-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

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

/* Regenerate row */
.regen-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}
.regen-hint { font-size: 0.78rem; color: var(--text-disabled); }

/* Live data badge */
.live-data-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.75rem;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 20px;
  font-size: 0.75rem;
  color: #10b981;
  margin-bottom: 1rem;
}
.live-data-badge i { font-size: 0.7rem; }

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

.ai-loading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  justify-content: center;
}

.progress-section { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color); }
.progress-header { display: flex; align-items: center; gap: 0.625rem; margin-bottom: 0.75rem; color: var(--text-secondary); font-weight: 500; }

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
  .nav-buttons .p-button { width: 100%; justify-content: center; }
  .review-row { grid-template-columns: 1fr; }
  .category-row { flex-wrap: wrap; }
  .category-dropdown { width: 100%; }
}
</style>
