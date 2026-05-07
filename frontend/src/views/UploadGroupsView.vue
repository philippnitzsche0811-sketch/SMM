<template>
  <div class="groups-view">

    <!-- ── Group detail view ── -->
    <div v-if="currentGroup" class="group-detail">
      <button class="back-link" @click="currentGroup = null; fetchGroups(authStore.userId!)">
        <i class="pi pi-arrow-left"></i> All Groups
      </button>

      <div class="detail-header">
        <div class="detail-title-row">
          <h2>{{ currentGroup.name }}</h2>
          <Tag :value="currentGroup.status" :severity="statusSeverity(currentGroup.status)" />
        </div>
        <div class="detail-meta">
          <span><i class="pi pi-link"></i> {{ platformsLabel(currentGroup.platforms) }}</span>
          <span><i class="pi pi-video"></i> {{ (currentGroup.videos || []).length }} videos</span>
        </div>
        <div class="detail-actions">
          <Button
            :label="currentGroup.status === 'active' ? 'Pause' : 'Resume'"
            :icon="currentGroup.status === 'active' ? 'pi pi-pause' : 'pi pi-play'"
            size="small"
            severity="secondary"
            @click="toggleGroupStatus"
          />
          <Button
            label="Delete Group"
            icon="pi pi-trash"
            size="small"
            severity="danger"
            outlined
            @click="confirmDeleteGroup"
          />
        </div>
      </div>

      <!-- Schedule preview -->
      <div v-if="(currentGroup.videos || []).length > 0" class="schedule-preview">
        <div class="schedule-preview-title"><i class="pi pi-calendar"></i> Upload Schedule</div>
        <div class="schedule-list">
          <div
            v-for="v in (currentGroup.videos || [])"
            :key="v.id"
            class="schedule-item"
            :class="`status-${v.status}`"
          >
            <div class="schedule-item-title">{{ v.title || v.video_id }}</div>
            <div class="schedule-item-time">
              <Tag :value="v.status" :severity="gvSeverity(v.status)" />
              <span v-if="v.scheduled_at">{{ formatDate(v.scheduled_at) }}</span>
              <span v-else class="muted">Not scheduled</span>
            </div>
            <Button
              icon="pi pi-trash"
              rounded
              text
              severity="danger"
              size="small"
              @click="handleRemoveVideo(v.id)"
            />
          </div>
        </div>
      </div>
      <div v-else class="empty-group">
        <i class="pi pi-inbox"></i>
        <p>No videos yet. Add the first one below.</p>
      </div>

      <!-- Add video form -->
      <div class="add-video-section">
        <h3>Add Video</h3>
        <DragDropZone @file-selected="handleGroupFileSelect" />
        <div v-if="groupUploadFile" class="group-upload-form">
          <div class="form-field">
            <label>Title</label>
            <InputText v-model="groupTitle" placeholder="Video title" class="w-full" />
          </div>
          <div class="form-field">
            <label>Description (optional)</label>
            <Textarea v-model="groupDescription" :rows="3" class="w-full" />
          </div>
          <div class="form-field">
            <label>Context for AI (optional)</label>
            <InputText v-model="groupAiContext" placeholder="Brief description of this video's content" class="w-full" />
          </div>
          <div class="form-actions">
            <Button label="Cancel" severity="secondary" outlined @click="groupUploadFile = null" />
            <Button
              label="Add to Group"
              icon="pi pi-plus"
              :loading="isSaving"
              :disabled="!groupTitle"
              @click="handleAddVideo"
            />
          </div>
          <ProgressBar v-if="groupUploadProgress > 0 && groupUploadProgress < 100" :value="groupUploadProgress" class="mt-2" />
        </div>
      </div>
    </div>

    <!-- ── Groups list view ── -->
    <div v-else class="groups-list-view">
      <div class="groups-header">
        <div>
          <h2>Upload Groups</h2>
          <p class="subtitle">Collect videos and let the scheduler upload them at the best times.</p>
        </div>
        <Button label="New Group" icon="pi pi-plus" @click="showCreateDialog = true" />
      </div>

      <div v-if="isLoading" class="loading-state">
        <i class="pi pi-spin pi-spinner"></i>
        <span>Loading groups…</span>
      </div>

      <div v-else-if="groups.length === 0" class="empty-state">
        <div class="empty-icon"><i class="pi pi-calendar"></i></div>
        <h3>No upload groups yet</h3>
        <p>Create a group to collect videos and auto-schedule uploads at the best times.</p>
        <Button label="Create your first group" icon="pi pi-plus" @click="showCreateDialog = true" />
      </div>

      <div v-else class="cards-grid">
        <UploadGroupCard
          v-for="group in groups"
          :key="group.id"
          :group="group"
          @click="openGroup(group.id)"
        />
      </div>
    </div>

    <!-- Create group dialog -->
    <Dialog v-model:visible="showCreateDialog" header="Create Upload Group" :style="{ width: '440px' }" modal>
      <div class="dialog-form">
        <div class="form-field">
          <label>Group name</label>
          <InputText v-model="newGroupName" placeholder="e.g. Weekly Fitness Tips" class="w-full" />
        </div>
        <div class="form-field">
          <label>Platforms</label>
          <PlatformSelector v-model="newGroupPlatforms" />
        </div>
        <div class="form-field">
          <label>Privacy</label>
          <Dropdown
            v-model="newGroupPrivacy"
            :options="privacyOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>
        <div class="form-field">
          <label>Category</label>
          <Dropdown
            v-model="newGroupCategory"
            :options="categoryOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" outlined @click="showCreateDialog = false" />
        <Button label="Create" icon="pi pi-check" :loading="isSaving" :disabled="!newGroupName || newGroupPlatforms.length === 0" @click="handleCreateGroup" />
      </template>
    </Dialog>

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import ProgressBar from 'primevue/progressbar';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import { DragDropZone, PlatformSelector } from '@/components/upload';
import UploadGroupCard from '@/components/groups/UploadGroupCard.vue';
import { useUploadGroups } from '@/composables/useUploadGroups';
import type { UploadGroup } from '@/types/upload_group.types';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();
const confirm = useConfirm();

const { groups, currentGroup, isLoading, isSaving, fetchGroups, fetchGroup, createGroup, addVideo, removeVideo, updateGroup, removeGroup } = useUploadGroups();

onMounted(async () => {
  if (!authStore.userId) return;
  await fetchGroups(authStore.userId);
  const id = route.params.id as string;
  if (id) openGroup(id);
});

// ── Group list ────────────────────────────────────────────────────────────────

async function openGroup(groupId: string) {
  await fetchGroup(groupId);
  router.replace(`/upload/groups/${groupId}`);
}

function statusSeverity(status: string) {
  return { active: 'success', paused: 'warning', completed: 'secondary' }[status] as any;
}
function gvSeverity(status: string) {
  return { queued: 'info', uploading: 'warning', done: 'success', failed: 'danger' }[status] as any;
}
function platformsLabel(platforms: string[]) {
  return platforms.map((p: string) => ({ youtube: 'YouTube', tiktok: 'TikTok', instagram: 'Instagram' }[p] ?? p)).join(', ');
}
function formatDate(iso: string) {
  try { return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(iso)); }
  catch { return iso; }
}

// ── Create group ──────────────────────────────────────────────────────────────

const showCreateDialog = ref(false);
const newGroupName = ref('');
const newGroupPlatforms = ref<string[]>([]);
const newGroupPrivacy = ref('private');
const newGroupCategory = ref('entertainment');

const privacyOptions = [
  { label: 'Private', value: 'private' },
  { label: 'Public', value: 'public' },
  { label: 'Unlisted', value: 'unlisted' },
];
const categoryOptions = [
  { label: 'Entertainment', value: 'entertainment' },
  { label: 'Education', value: 'education' },
  { label: 'Gaming', value: 'gaming' },
  { label: 'Music', value: 'music' },
  { label: 'Sports', value: 'sports' },
  { label: 'Default', value: 'default' },
];

async function handleCreateGroup() {
  if (!authStore.userId || !newGroupName.value) return;
  try {
    await createGroup(authStore.userId, newGroupName.value, newGroupPlatforms.value, newGroupPrivacy.value, newGroupCategory.value);
    showCreateDialog.value = false;
    newGroupName.value = '';
    newGroupPlatforms.value = [];
    toast.add({ severity: 'success', summary: 'Group created', life: 3000 });
  } catch {
    toast.add({ severity: 'error', summary: 'Failed to create group', life: 3000 });
  }
}

// ── Group detail actions ──────────────────────────────────────────────────────

async function toggleGroupStatus() {
  if (!currentGroup.value || !authStore.userId) return;
  const newStatus = currentGroup.value.status === 'active' ? 'paused' : 'active';
  await updateGroup(currentGroup.value.id, authStore.userId, { status: newStatus });
  toast.add({ severity: 'info', summary: `Group ${newStatus}`, life: 2000 });
}

function confirmDeleteGroup() {
  confirm.require({
    message: `Delete group "${currentGroup.value?.name}"? Videos in the group will not be deleted.`,
    header: 'Delete Group',
    icon: 'pi pi-trash',
    acceptClass: 'p-button-danger',
    accept: async () => {
      if (!currentGroup.value || !authStore.userId) return;
      const id = currentGroup.value.id;
      currentGroup.value = null;
      await removeGroup(id, authStore.userId);
      router.replace('/upload/groups');
      toast.add({ severity: 'info', summary: 'Group deleted', life: 3000 });
    },
  });
}

async function handleRemoveVideo(gvId: string) {
  if (!currentGroup.value || !authStore.userId) return;
  await removeVideo(currentGroup.value.id, gvId, authStore.userId);
  toast.add({ severity: 'info', summary: 'Video removed', life: 2000 });
}

// ── Add video to group ────────────────────────────────────────────────────────

const groupUploadFile = ref<File | null>(null);
const groupTitle = ref('');
const groupDescription = ref('');
const groupAiContext = ref('');
const groupUploadProgress = ref(0);

function handleGroupFileSelect(file: File) {
  groupUploadFile.value = file;
  groupTitle.value = file.name.replace(/\.[^.]+$/, '');
}

async function handleAddVideo() {
  if (!groupUploadFile.value || !currentGroup.value || !authStore.userId) return;
  const formData = new FormData();
  formData.append('video', groupUploadFile.value);
  formData.append('user_id', authStore.userId);
  formData.append('title', groupTitle.value);
  formData.append('description', groupDescription.value);
  formData.append('ai_context', groupAiContext.value);
  formData.append('tags', '');

  try {
    await addVideo(currentGroup.value.id, formData, (pct) => { groupUploadProgress.value = pct; });
    groupUploadFile.value = null;
    groupTitle.value = '';
    groupDescription.value = '';
    groupAiContext.value = '';
    groupUploadProgress.value = 0;
    toast.add({ severity: 'success', summary: 'Video added to group', life: 3000 });
  } catch {
    toast.add({ severity: 'error', summary: 'Failed to add video', life: 3000 });
  }
}
</script>

<style scoped>
.groups-view { max-width: 860px; margin: 0 auto; }

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

/* Groups list */
.groups-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.groups-header h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
}
.subtitle { font-size: 0.875rem; color: var(--text-secondary); margin: 0; }

.loading-state {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-secondary);
}
.empty-icon { font-size: 3rem; color: var(--text-disabled); margin-bottom: 1rem; }
.empty-state h3 { font-size: 1.1rem; color: var(--text-primary); margin: 0 0 0.5rem; }
.empty-state p  { font-size: 0.875rem; margin: 0 0 1.5rem; }

.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }

/* Group detail */
.detail-header {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.detail-title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
.detail-title-row h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
}
.detail-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}
.detail-meta span {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.825rem;
  color: var(--text-secondary);
}
.detail-meta i { color: var(--text-disabled); font-size: 0.8rem; }
.detail-actions { display: flex; gap: 0.625rem; }

/* Schedule */
.schedule-preview {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}
.schedule-preview-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  background: rgba(255,255,255,0.03);
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.schedule-list { display: flex; flex-direction: column; }
.schedule-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.schedule-item:last-child { border-bottom: none; }
.schedule-item-title { flex: 1; font-size: 0.875rem; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.schedule-item-time { display: flex; align-items: center; gap: 0.625rem; font-size: 0.8rem; color: var(--text-secondary); flex-shrink: 0; }
.muted { color: var(--text-disabled); }

.empty-group {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  margin-bottom: 1.5rem;
}
.empty-group i { font-size: 2rem; display: block; margin-bottom: 0.5rem; color: var(--text-disabled); }

/* Add video */
.add-video-section {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 1.5rem;
}
.add-video-section h3 { font-family: 'Poppins', sans-serif; font-size: 0.9375rem; font-weight: 700; color: var(--text-primary); margin: 0 0 1.25rem; }

.group-upload-form { margin-top: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.form-field { display: flex; flex-direction: column; gap: 0.375rem; }
.form-field label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); }
.form-actions { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 0.5rem; }

/* Dialog */
.dialog-form { display: flex; flex-direction: column; gap: 1rem; padding: 0.5rem 0; }

.mt-2 { margin-top: 0.5rem; }

@media (max-width: 640px) {
  .groups-header { flex-direction: column; }
  .cards-grid { grid-template-columns: 1fr; }
  .detail-actions { flex-wrap: wrap; }
}
</style>
