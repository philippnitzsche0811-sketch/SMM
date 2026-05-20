<template>
  <div class="upload-view">
    <div class="upload-card">

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

      <!-- ── Schritt 1: Video + Plattformen ── -->
      <div v-show="currentStep === 1" class="step-content">
        <DragDropZone @file-selected="handleFileSelect" />

        <Transition name="slide-down">
          <div v-if="videoFile" class="step1-extra">
            <div class="file-badge">
              <i class="pi pi-video"></i>
              {{ videoFile.name }}
            </div>

            <div class="divider"></div>

            <div class="field-group">
              <label>Video title <span class="required">*</span></label>
              <InputText
                v-model="meta.title"
                placeholder="What's your video called?"
                class="w-full"
                :maxlength="200"
              />
            </div>

            <div class="divider"></div>

            <DescribeVideoStep v-model:context="aiContext" />

            <div class="divider"></div>

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

            <div class="field-group">
              <label>Upload to <span class="required">*</span></label>
              <PlatformSelector v-model="selectedPlatforms" />
            </div>

            <!-- Free/Pro split für Schritt-1-Navigation -->
            <div class="nav-buttons step1-nav">
              <template v-if="isProUser">
                <button
                  class="manual-link"
                  :disabled="selectedPlatforms.length === 0 || !meta.title.trim()"
                  @click="goToManual"
                >
                  Fill in manually
                </button>
                <Button
                  label="Generate with AI"
                  icon="pi pi-sparkles"
                  iconPos="right"
                  :loading="isOptimizing"
                  :disabled="selectedPlatforms.length === 0 || !meta.title.trim()"
                  @click="goToReview"
                />
              </template>
              <template v-else>
                <div style="flex:1">
                  <UpgradePrompt
                    title="AI optimization is Pro"
                    description="Title, description and hashtags are auto-generated for each platform."
                    @upgrade="$router.push('/settings')"
                  />
                </div>
                <Button
                  label="Continue"
                  icon="pi pi-arrow-right"
                  iconPos="right"
                  :disabled="selectedPlatforms.length === 0 || !meta.title.trim()"
                  @click="goToManual"
                />
              </template>
            </div>
          </div>
        </Transition>
      </div>

      <!-- ── Schritt 2: Metadaten (AI oder manuell) ── -->
      <div v-show="currentStep === 2" class="step-content">
        <div v-if="isOptimizing" class="ai-loading">
          <i class="pi pi-spin pi-spinner"></i>
          <span>AI is optimizing your metadata…</span>
        </div>

        <template v-else>
          <div v-if="liveDataAge && isProUser" class="live-data-badge">
            <i class="pi pi-globe"></i>
            Live YouTube data · Updated {{ liveDataAge }}
          </div>

          <!-- Shared Metadata (manual mode, multiple platforms) -->
          <div v-if="isManualMode && selectedPlatforms.length > 1" class="shared-meta-box">
            <div class="shared-meta-header">
              <i class="pi pi-link"></i>
              <span>For all platforms</span>
              <span class="shared-meta-hint">Fields are applied to all platform tabs — customize per platform afterwards</span>
            </div>
            <div class="shared-fields">
              <div class="review-section">
                <label class="review-label">Description</label>
                <Textarea
                  v-model="sharedDescription"
                  :rows="3"
                  class="w-full"
                  placeholder="Description for all platforms…"
                  @update:modelValue="syncSharedToAll"
                />
              </div>
              <div class="review-section" style="margin-top: 0.875rem;">
                <label class="review-label">Hashtags</label>
                <div class="tags-row">
                  <span v-for="(tag, i) in sharedTags" :key="i" class="tag-chip">
                    #{{ tag }}
                    <button class="tag-remove" @click="removeSharedTag(i)">×</button>
                  </span>
                  <input
                    v-model="sharedNewTag"
                    class="tag-input"
                    placeholder="Add tag…"
                    @keydown.enter.prevent="addSharedTag"
                    @keydown.comma.prevent="addSharedTag"
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-if="selectedPlatforms.length > 1" class="platform-tabs">
            <button
              v-for="p in selectedPlatforms"
              :key="p"
              class="platform-tab"
              :class="['tab-' + p, { active: activeTab === p }]"
              @click="activeTab = p"
            >
              <i :class="platformTabIcon(p)"></i>
              {{ platformLabel(p) }}
            </button>
          </div>

          <div v-if="currentMeta" class="tab-content">
            <!-- Titel -->
            <div class="review-section">
              <TitlePickerPanel
                v-if="isProUser && currentMeta.titleOptions?.length > 1"
                :options="currentMeta.titleOptions"
                v-model="currentMeta.title"
              />
              <div v-else class="field-group">
                <label class="review-label">Title <span class="required">*</span></label>
                <InputText v-model="currentMeta.title" class="w-full" placeholder="Video title…" />
              </div>
            </div>

            <div class="divider"></div>

            <div class="review-section">
              <label class="review-label">Description</label>
              <Textarea
                v-model="currentMeta.description"
                :rows="4"
                class="w-full"
                placeholder="Video description…"
              />
            </div>

            <div class="divider"></div>

            <div class="review-section">
              <label class="review-label">Hashtags</label>
              <div class="tags-row">
                <span v-for="(tag, i) in currentMeta.tags" :key="i" class="tag-chip">
                  #{{ tag }}
                  <button class="tag-remove" @click="currentMeta.tags.splice(i, 1)">×</button>
                </span>
                <input
                  v-model="currentMeta.newTag"
                  class="tag-input"
                  placeholder="Add tag…"
                  @keydown.enter.prevent="addTagToCurrentPlatform"
                  @keydown.comma.prevent="addTagToCurrentPlatform"
                />
              </div>
            </div>

            <div class="divider"></div>

            <div class="field-group">
              <label class="review-label">
                Visibility
                <span v-if="activeTab === 'tiktok'" class="required">*</span>
              </label>
              <Dropdown
                v-if="activeTab === 'tiktok'"
                v-model="currentMeta.privacyStatus"
                :options="tiktokPrivacyOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select visibility…"
                style="width: 260px"
              />
              <Dropdown
                v-else
                v-model="currentMeta.privacyStatus"
                :options="privacyOptions"
                optionLabel="label"
                optionValue="value"
                style="width: 220px"
              />
            </div>

            <!-- TikTok-spezifische Felder -->
            <template v-if="activeTab === 'tiktok' && currentMeta">
              <div class="divider"></div>
              <div class="tiktok-section">
                <label class="review-label">Allow interactions</label>
                <div class="checkbox-group">
                  <div class="checkbox-row">
                    <Checkbox v-model="currentMeta.allowComment" :binary="true" inputId="ck-comment" />
                    <label for="ck-comment">Comments</label>
                  </div>
                  <div class="checkbox-row">
                    <Checkbox v-model="currentMeta.allowDuet" :binary="true" inputId="ck-duet" />
                    <label for="ck-duet">Duet</label>
                  </div>
                  <div class="checkbox-row">
                    <Checkbox v-model="currentMeta.allowStitch" :binary="true" inputId="ck-stitch" />
                    <label for="ck-stitch">Stitch</label>
                  </div>
                </div>
              </div>
              <div class="divider"></div>
              <div class="tiktok-section">
                <div class="disclosure-header">
                  <div>
                    <label class="review-label">Disclose content</label>
                    <p class="disclosure-hint">Enable if the video promotes products or services</p>
                  </div>
                  <InputSwitch v-model="currentMeta.contentDisclosure" />
                </div>
                <template v-if="currentMeta.contentDisclosure">
                  <div class="disclosure-options">
                    <div class="checkbox-row">
                      <Checkbox v-model="currentMeta.yourBrand" :binary="true" inputId="ck-your-brand" />
                      <div>
                        <label for="ck-your-brand" class="disclosure-option-label">Your Brand</label>
                        <p class="disclosure-hint">You are promoting yourself or your own business</p>
                      </div>
                    </div>
                    <div class="checkbox-row">
                      <Checkbox v-model="currentMeta.brandedContent" :binary="true" inputId="ck-branded" />
                      <div>
                        <label for="ck-branded" class="disclosure-option-label">Branded Content</label>
                        <p class="disclosure-hint">You are promoting another brand or third party</p>
                      </div>
                    </div>
                  </div>
                  <p class="compliance-text" v-if="currentMeta.brandedContent">
                    By uploading you agree to TikTok's Branded Content Policy.
                  </p>
                </template>
              </div>
            </template>

            <div v-if="isProUser" class="regen-row">
              <Button
                label="Regenerate"
                icon="pi pi-refresh"
                severity="secondary"
                outlined
                size="small"
                :loading="isRegenerating"
                @click="regenerate"
              />
              <span class="regen-hint">Same context, new AI suggestions</span>
            </div>
          </div>
        </template>

        <div class="nav-buttons">
          <Button label="Back" severity="secondary" outlined @click="currentStep = 1" :disabled="isOptimizing" />
          <Button label="Next" @click="currentStep = 3" :disabled="!canProceedFromStep2 || isOptimizing" />
        </div>
      </div>

      <!-- ── Schritt 3: Zeitpunkt ── -->
      <div v-show="currentStep === 3" class="step-content">
        <ScheduleStep
          v-model:scheduleType="scheduleType"
          v-model:scheduledAt="scheduledAt"
          v-model:selectedGroupId="selectedGroupId"
          :groups="groups"
          :recommendedAt="recommendedAt"
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

      <!-- Upload-Fortschritt -->
      <div v-if="isSubmitting" class="progress-section">
        <div class="progress-header">
          <i class="pi pi-spin pi-spinner"></i>
          <span>Uploading…</span>
        </div>
        <ProgressBar :value="uploadProgress" />
      </div>
    </div>
  </div>

  <!-- Create-Group-Dialog -->
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
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { usePlan } from '@/composables/usePlan';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import ProgressBar from 'primevue/progressbar';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';
import InputSwitch from 'primevue/inputswitch';
import { DragDropZone, PlatformSelector } from '@/components/upload';
import DescribeVideoStep from '@/components/upload/DescribeVideoStep.vue';
import ScheduleStep from '@/components/upload/ScheduleStep.vue';
import TitlePickerPanel from '@/components/upload/TitlePickerPanel.vue';
import UpgradePrompt from '@/components/common/UpgradePrompt.vue';
import { simpleUpload, optimizeSuggest } from '@/services/api';
import { useUploadGroups } from '@/composables/useUploadGroups';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { isProUser } = usePlan();
const toast = useToast();
const { groups, fetchGroups, createGroup, isSaving } = useUploadGroups();

onMounted(() => {
  if (authStore.userId) fetchGroups(authStore.userId);
  // Pre-fill from Ideas board query params
  const q = route.query;
  if (q.title) meta.value.title = String(q.title);
  if (q.description) aiContext.value = String(q.description);
  if (q.platforms) selectedPlatforms.value = String(q.platforms).split(',').filter(Boolean);
  if (q.tags) {
    const prefilledTags = String(q.tags).split(',').map(t => t.trim()).filter(Boolean);
    if (prefilledTags.length > 0) {
      sharedTags.value = prefilledTags;
      // Will be synced to platform metas when initPlatformMetas() runs
      prefillTags.value = prefilledTags;
    }
  }
});

const steps = ['Video', 'Metadata', 'Schedule'];
const currentStep = ref(1);
const videoFile = ref<File | null>(null);

const meta = ref({ title: '', category: 'default' });

type PlatformMeta = {
  title: string;
  titleOptions: string[];
  description: string;
  tags: string[];
  privacyStatus: string | null;
  newTag: string;
  allowComment: boolean;
  allowDuet: boolean;
  allowStitch: boolean;
  contentDisclosure: boolean;
  yourBrand: boolean;
  brandedContent: boolean;
};

const platformMetas = ref<Record<string, PlatformMeta>>({});
const activeTab = ref('');
const currentMeta = computed(() => platformMetas.value[activeTab.value] ?? null);

const aiContext = ref('');
const isManualMode = ref(false);
const sharedDescription = ref('');
const sharedTags = ref<string[]>([]);
const sharedNewTag = ref('');
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

const selectedPlatforms = ref<string[]>([]);
const prefillTags = ref<string[]>([]);
const scheduleType = ref('now');
const scheduledAt = ref<string | null>(null);
const selectedGroupId = ref<string | null>(null);
const showCreateGroupDialog = ref(false);
const newGroupName = ref('');
const isSubmitting = ref(false);
const uploadProgress = ref(0);

const privacyOptions = [
  { label: 'Private',    value: 'private'  },
  { label: 'Unlisted',   value: 'unlisted' },
  { label: 'Public',     value: 'public'   },
];
const tiktokPrivacyOptions = [
  { label: 'Private (only me)',  value: 'SELF_ONLY'             },
  { label: 'Friends',            value: 'MUTUAL_FOLLOW_FRIENDS' },
  { label: 'Public',             value: 'PUBLIC_TO_EVERYONE'    },
];
const categoryOptions = [
  { label: 'Default',          value: 'default'       },
  { label: 'Entertainment',   value: 'entertainment' },
  { label: 'Education',       value: 'education'     },
  { label: 'Gaming',          value: 'gaming'        },
  { label: 'Music',            value: 'music'         },
  { label: 'Sport',           value: 'sports'        },
  { label: 'Tech',            value: 'tech'          },
  { label: 'Lifestyle',       value: 'lifestyle'     },
];

const platformLabels: Record<string, string> = { youtube: 'YouTube', tiktok: 'TikTok', instagram: 'Instagram' };
const platformTabIcons: Record<string, string> = { youtube: 'pi pi-youtube', tiktok: 'pi pi-mobile', instagram: 'pi pi-instagram' };
function platformLabel(p: string) { return platformLabels[p] ?? p; }
function platformTabIcon(p: string) { return platformTabIcons[p] ?? 'pi pi-video'; }

const canProceedFromStep2 = computed(() => {
  if (selectedPlatforms.value.length === 0) return false;
  for (const p of selectedPlatforms.value) {
    const m = platformMetas.value[p];
    if (!m?.title?.trim()) return false;
    if (p === 'tiktok' && !m.privacyStatus) return false;
  }
  return true;
});

const canSubmit = computed(() => {
  if (scheduleType.value === 'datetime' && !scheduledAt.value) return false;
  if (scheduleType.value === 'recommended' && !recommendedAt.value) return false;
  if (scheduleType.value === 'group' && !selectedGroupId.value) return false;
  return true;
});

const submitLabel = computed(() => ({
  now:         'Publish Now',
  datetime:    'Schedule Upload',
  recommended: 'Schedule for Recommended Time',
  group:       'Add to Group',
}[scheduleType.value] ?? 'Upload'));

function handleFileSelect(file: File) {
  videoFile.value = file;
  if (!meta.value.title) {
    const raw = file.name.replace(/\.[^.]+$/, '');
    meta.value.title = raw.replace(/[_\-]+/g, ' ').replace(/\s+/g, ' ').trim()
      .replace(/\b\w/g, c => c.toUpperCase());
  }
}

function initPlatformMetas() {
  const metas: Record<string, PlatformMeta> = {};
  for (const p of selectedPlatforms.value) {
    metas[p] = platformMetas.value[p] ?? {
      title: meta.value.title,
      titleOptions: [],
      description: '',
      tags: prefillTags.value.length > 0 ? [...prefillTags.value] : [],
      privacyStatus: p === 'tiktok' ? null : 'private',
      newTag: '',
      allowComment: false,
      allowDuet: false,
      allowStitch: false,
      contentDisclosure: false,
      yourBrand: false,
      brandedContent: false,
    };
  }
  platformMetas.value = metas;
  if (!activeTab.value || !selectedPlatforms.value.includes(activeTab.value)) {
    activeTab.value = selectedPlatforms.value[0] ?? '';
  }
}

// Compute recommended upload time from selected platforms
const recommendedAt = computed<string | null>(() => {
  if (selectedPlatforms.value.length === 0) return null;
  // Best days (0=Sun,1=Mon,...,6=Sat) and hour per platform
  const bestSlots: Record<string, { days: number[]; hour: number }> = {
    tiktok:    { days: [2, 4], hour: 19 }, // Tue, Thu 19:00
    instagram: { days: [1, 3], hour: 18 }, // Mon, Wed 18:00
    youtube:   { days: [2, 4], hour: 18 }, // Tue, Thu 18:00
  };
  // Pick the first platform's slot as the recommendation
  const platform = selectedPlatforms.value[0];
  const slot = bestSlots[platform] ?? { days: [2, 4], hour: 19 };
  const now = new Date();
  const nowDay = now.getDay();
  // Find next occurrence of a best day (must be at least 2h from now)
  for (let offset = 1; offset <= 7; offset++) {
    const candidate = new Date(now);
    candidate.setDate(now.getDate() + offset);
    candidate.setHours(slot.hour, 0, 0, 0);
    if (slot.days.includes(candidate.getDay())) {
      return candidate.toISOString();
    }
  }
  // Fallback: tomorrow same hour
  const fallback = new Date(now);
  fallback.setDate(now.getDate() + 1);
  fallback.setHours(slot.hour, 0, 0, 0);
  return fallback.toISOString();
});

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
      niche: authStore.user?.niche || 'default',
      creator_tone: authStore.user?.creatorTone || 'informative',
    });
    const suggestions = data.suggestions ?? {};
    trendRefreshedAt.value = data.trend_refreshed_at ?? null;
    for (const platform of selectedPlatforms.value) {
      const sug: any = suggestions[platform] ?? Object.values(suggestions)[0] ?? null;
      if (sug && platformMetas.value[platform]) {
        platformMetas.value[platform].titleOptions = sug.title_options?.length
          ? sug.title_options : [sug.title ?? meta.value.title];
        platformMetas.value[platform].title = sug.title_options?.[0] ?? sug.title ?? meta.value.title;
        platformMetas.value[platform].description = sug.description ?? '';
        platformMetas.value[platform].tags = sug.tags ?? [];
      }
    }
  } catch {
    toast.add({ severity: 'warn', summary: 'AI unavailable', detail: 'Please fill in manually.', life: 4000 });
  } finally {
    isOptimizing.value = false;
    isRegenerating.value = false;
  }
}

function syncSharedToAll() {
  for (const p of selectedPlatforms.value) {
    if (platformMetas.value[p]) {
      platformMetas.value[p].description = sharedDescription.value;
      platformMetas.value[p].tags = [...sharedTags.value];
    }
  }
}

function addSharedTag() {
  const t = sharedNewTag.value.replace(/^#/, '').trim();
  if (t && !sharedTags.value.includes(t)) {
    sharedTags.value.push(t);
    syncSharedToAll();
  }
  sharedNewTag.value = '';
}

function removeSharedTag(i: number) {
  sharedTags.value.splice(i, 1);
  syncSharedToAll();
}

async function goToReview() {
  isManualMode.value = false;
  initPlatformMetas();
  currentStep.value = 2;
  await runOptimize(false);
}

function goToManual() {
  isManualMode.value = true;
  sharedDescription.value = aiContext.value || '';
  if (prefillTags.value.length > 0 && sharedTags.value.length === 0) {
    sharedTags.value = [...prefillTags.value];
  }
  initPlatformMetas();
  currentStep.value = 2;
}

async function regenerate() { await runOptimize(true); }

function addTagToCurrentPlatform() {
  if (!currentMeta.value) return;
  const t = currentMeta.value.newTag.replace(/^#/, '').trim();
  if (t && !currentMeta.value.tags.includes(t)) currentMeta.value.tags.push(t);
  currentMeta.value.newTag = '';
}

async function handleCreateGroup() {
  if (!newGroupName.value.trim() || !authStore.userId) return;
  try {
    const firstPlatform = selectedPlatforms.value[0];
    const primaryMeta = platformMetas.value[firstPlatform];
    const group = await createGroup(
      authStore.userId,
      newGroupName.value.trim(),
      selectedPlatforms.value.length ? selectedPlatforms.value : ['youtube'],
      primaryMeta?.privacyStatus || 'private',
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
  try {
    const firstPlatform = selectedPlatforms.value[0];
    const primaryMeta = platformMetas.value[firstPlatform] ?? {
      title: meta.value.title, description: '', tags: [], privacyStatus: 'private',
    };
    const platformMetaJson: Record<string, any> = {};
    for (const [platform, m] of Object.entries(platformMetas.value)) {
      platformMetaJson[platform] = {
        title: m.title,
        description: m.description,
        tags: m.tags,
        privacy_status: m.privacyStatus ?? (platform === 'tiktok' ? 'SELF_ONLY' : 'private'),
        ...(platform === 'tiktok' ? {
          allow_comment: m.allowComment,
          allow_duet: m.allowDuet,
          allow_stitch: m.allowStitch,
        } : {}),
      };
    }
    const formData = new FormData();
    formData.append('video', videoFile.value);
    formData.append('user_id', authStore.userId);
    formData.append('title', primaryMeta.title || meta.value.title);
    formData.append('description', primaryMeta.description || '');
    formData.append('tags', (primaryMeta.tags || []).join(','));
    formData.append('platforms', selectedPlatforms.value.join(','));
    formData.append('privacy_status', primaryMeta.privacyStatus || 'private');
    formData.append('upload_mode', 'simple');
    const effectiveScheduleType = scheduleType.value === 'recommended' ? 'datetime' : scheduleType.value;
    const effectiveScheduledAt  = scheduleType.value === 'recommended' ? recommendedAt.value : scheduledAt.value;
    formData.append('schedule_type', effectiveScheduleType);
    formData.append('platform_metadata', JSON.stringify(platformMetaJson));
    if (effectiveScheduledAt) formData.append('scheduled_at', effectiveScheduledAt);
    if (selectedGroupId.value) formData.append('group_id', selectedGroupId.value);

    await simpleUpload(formData, (pct) => { uploadProgress.value = pct; });

    const detail =
      scheduleType.value === 'now'         ? 'Upload started — your video is being processed.' :
      scheduleType.value === 'group'        ? 'Video added to group.' :
      scheduleType.value === 'recommended'  ? 'Scheduled for the recommended time.' :
                                              'Upload scheduled.';
    toast.add({ severity: 'success', summary: 'Done!', detail, life: 6000 });
    router.push('/dashboard');
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Upload failed', detail: err.response?.data?.detail || 'Something went wrong', life: 5000 });
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.upload-view { max-width: 860px; margin: 0 auto; padding: 1.5rem 1rem; }

.upload-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 2rem;
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
.step-item.current .step-label,
.step-item.active .step-label { color: var(--text-primary); font-weight: 600; }
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

.category-row { display: flex; align-items: center; gap: 0.75rem; }
.category-row label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); white-space: nowrap; flex-shrink: 0; }
.category-dropdown { width: 200px; }

.nav-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.step1-nav { justify-content: space-between; align-items: center; }

.manual-link {
  background: none;
  border: none;
  color: var(--text-disabled);
  font-size: 0.825rem;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color 0.15s;
}
.manual-link:hover:not(:disabled) { color: var(--text-secondary); }
.manual-link:disabled { opacity: 0.4; cursor: not-allowed; }

/* Step 2 */
.review-section { display: flex; flex-direction: column; gap: 0.5rem; }
.review-label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); display: block; margin-bottom: 0.25rem; }

.shared-meta-box {
  background: rgba(79,127,255,0.05);
  border: 1px solid rgba(79,127,255,0.2);
  border-radius: 10px;
  padding: 1rem 1.125rem;
  margin-bottom: 1.25rem;
}
.shared-meta-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.875rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: #93c5fd;
}
.shared-meta-hint {
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--text-secondary);
}
.shared-fields { display: flex; flex-direction: column; }

.platform-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}
.platform-tab {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.625rem 1.25rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: -1px;
  transition: color 0.15s, border-color 0.15s;
}
.platform-tab:hover { color: var(--text-primary); }
.platform-tab.active { color: var(--text-primary); border-bottom-color: #4f7fff; }
.tab-youtube.active   { border-bottom-color: #ff4444; color: #ff6666; }
.tab-tiktok.active    { border-bottom-color: #69c9d0; color: #69c9d0; }
.tab-instagram.active { border-bottom-color: #e1306c; color: #e1306c; }

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
.tag-remove { background: none; border: none; color: var(--text-disabled); cursor: pointer; padding: 0; font-size: 1rem; line-height: 1; display: flex; align-items: center; }
.tag-remove:hover { color: #f87171; }
.tag-input { flex: 1; min-width: 80px; background: transparent; border: none; outline: none; color: var(--text-primary); font-size: 0.875rem; padding: 0.15rem 0; }

.regen-row { display: flex; align-items: center; gap: 0.75rem; margin-top: 0.5rem; }
.regen-hint { font-size: 0.78rem; color: var(--text-disabled); }

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

.ai-loading { display: flex; align-items: center; gap: 0.75rem; padding: 2rem; color: var(--text-secondary); font-size: 0.9rem; justify-content: center; }

/* TikTok */
.tiktok-section { display: flex; flex-direction: column; gap: 0.75rem; }
.checkbox-group { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.25rem; }
.checkbox-row { display: flex; align-items: flex-start; gap: 0.625rem; }
.checkbox-row label { font-size: 0.875rem; color: var(--text-primary); cursor: pointer; line-height: 1.4; }
.disclosure-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
.disclosure-hint { font-size: 0.78rem; color: var(--text-disabled); margin: 0.15rem 0 0; }
.disclosure-options { display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem; padding: 0.75rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; }
.disclosure-option-label { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); cursor: pointer; display: block; }
.compliance-text { font-size: 0.78rem; color: var(--text-secondary); margin: 0.5rem 0 0; padding: 0.5rem 0.75rem; background: rgba(105, 201, 208, 0.06); border-left: 2px solid #69c9d0; border-radius: 0 4px 4px 0; line-height: 1.5; }

.progress-section { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color); }
.progress-header { display: flex; align-items: center; gap: 0.625rem; margin-bottom: 0.75rem; color: var(--text-secondary); font-weight: 500; }

.dialog-field { display: flex; flex-direction: column; gap: 0.4rem; padding: 0.25rem 0; }
.dialog-field label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); }

.divider { height: 1px; background: var(--border-color); margin: 1.25rem 0; }

.slide-down-enter-active { transition: all 0.3s ease; }
.slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from   { opacity: 0; transform: translateY(-8px); }
.slide-down-leave-to     { opacity: 0; transform: translateY(-8px); }

@media (max-width: 640px) {
  .upload-card { padding: 1.25rem; }
  .step-label   { display: none; }
  .nav-buttons  { flex-direction: column-reverse; }
  .nav-buttons .p-button { width: 100%; justify-content: center; }
  .category-row { flex-wrap: wrap; }
  .category-dropdown { width: 100%; }
  .platform-tabs { overflow-x: auto; }
  .platform-tab  { padding: 0.5rem 0.875rem; font-size: 0.8rem; }
}
</style>
