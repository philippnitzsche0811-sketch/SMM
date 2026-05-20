<template>
  <div class="ideas-view-wrap" :class="{ 'panel-open': !!selectedIdea }">
  <div class="ideas-view">
    <div class="ideas-header">
      <div>
        <h1 class="page-title">Ideas</h1>
        <p class="page-subtitle">Plan your content before you pick up the camera</p>
      </div>
      <button class="btn-primary" @click="openCreateModal">
        <i class="pi pi-plus"></i> New Idea
      </button>
    </div>

    <!-- Kanban Board -->
    <div class="kanban-board" v-if="!loading">
      <div
        v-for="col in columns"
        :key="col.status"
        class="kanban-col"
      >
        <div class="col-header">
          <span class="col-dot" :class="col.status"></span>
          <span class="col-title">{{ col.label }}</span>
          <span class="col-count">{{ ideasByStatus(col.status).length }}</span>
        </div>

        <div class="col-cards">
          <div
            v-for="idea in ideasByStatus(col.status)"
            :key="idea.id"
            class="idea-card"
            :class="{ selected: selectedIdea?.id === idea.id }"
            @click="selectedIdea = idea"
          >
            <div class="card-title">{{ idea.title }}</div>
            <div class="card-concept" v-if="idea.concept">{{ idea.concept }}</div>
            <div class="card-footer">
              <div class="card-platforms">
                <i
                  v-for="p in (idea.target_platforms || []).slice(0, 3)"
                  :key="p"
                  :class="platformIcon(p)"
                  :title="p"
                ></i>
              </div>
              <div class="card-date" v-if="idea.target_date">
                <i class="pi pi-calendar"></i>
                {{ formatDate(idea.target_date) }}
              </div>
            </div>
            <div class="card-actions">
              <button
                class="btn-optimize"
                @click.stop="selectedIdea = idea"
                title="Optimize"
              >
                <i class="pi pi-sparkles"></i>
              </button>
              <button
                v-if="idea.status === 'ready'"
                class="btn-upload-card"
                @click.stop="goToUpload(idea)"
                title="Upload now"
              >
                <i class="pi pi-cloud-upload"></i>
              </button>
              <button class="btn-edit" @click.stop="openEditModal(idea)" title="Edit">
                <i class="pi pi-pencil"></i>
              </button>
              <button class="btn-delete" @click.stop="confirmDelete(idea)" title="Delete">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </div>

          <div class="empty-col" v-if="ideasByStatus(col.status).length === 0">
            No ideas here
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <i class="pi pi-spin pi-spinner"></i> Loading ideas...
    </div>

  </div><!-- end ideas-view -->

  <!-- Optimize Panel -->
  <transition name="panel-slide">
    <div v-if="selectedIdea" class="optimize-panel-wrap">
      <IdeaOptimizePanel :idea="selectedIdea" @close="selectedIdea = null" />
    </div>
  </transition>

  <!-- Create / Edit Modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="idea-modal">
        <div class="modal-header">
          <h3>{{ editingIdea ? 'Edit Idea' : 'New Idea' }}</h3>
          <button class="modal-close" @click="closeModal"><i class="pi pi-times"></i></button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label>Title *</label>
            <input
              v-model="form.title"
              class="form-input"
              placeholder="What's the video about?"
              maxlength="120"
            />
          </div>

          <div class="form-group">
            <label>Concept</label>
            <textarea
              v-model="form.concept"
              class="form-textarea"
              placeholder="Hook idea, angle, key message…"
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <label>Platforms</label>
            <div class="platform-checks">
              <label v-for="p in platformOptions" :key="p.value" class="check-label">
                <input type="checkbox" :value="p.value" v-model="form.target_platforms" />
                <i :class="p.icon"></i> {{ p.label }}
              </label>
            </div>
          </div>

          <div class="form-group">
            <label>Target Date</label>
            <input type="date" v-model="form.target_date" class="form-input" />
          </div>

          <div class="form-group">
            <label>Status</label>
            <select v-model="form.status" class="form-select">
              <option value="idea">Idea</option>
              <option value="planning">Planning</option>
              <option value="ready">Ready</option>
            </select>
          </div>

          <div class="form-group">
            <label>Tags</label>
            <input
              v-model="form.tags"
              class="form-input"
              placeholder="tag1, tag2, tag3"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModal">Cancel</button>
          <button
            class="btn-save"
            :disabled="!form.title.trim() || saving"
            @click="saveIdea"
          >
            <i v-if="saving" class="pi pi-spin pi-spinner"></i>
            {{ editingIdea ? 'Save' : 'Create' }}
          </button>
        </div>
      </div>
    </div>

  <!-- Delete Confirm -->
  <div v-if="deleteTarget" class="modal-backdrop" @click.self="deleteTarget = null">
    <div class="confirm-modal">
      <h3>Delete idea?</h3>
      <p>"{{ deleteTarget.title }}" will be permanently removed.</p>
      <div class="confirm-actions">
        <button class="btn-cancel" @click="deleteTarget = null">Cancel</button>
        <button class="btn-danger" :disabled="saving" @click="doDelete">Delete</button>
      </div>
    </div>
  </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { listIdeas, createIdea, updateIdea, deleteIdea } from '@/services/api';
import IdeaOptimizePanel from '@/components/plan/IdeaOptimizePanel.vue';
import { useToast } from 'primevue/usetoast';

interface Idea {
  id: string;
  title: string;
  concept?: string;
  target_platforms: string[];
  target_date?: string;
  status: string;
  tags?: string[];
}

const authStore = useAuthStore();
const router    = useRouter();
const toast     = useToast();

const ideas        = ref<Idea[]>([]);
const loading      = ref(true);
const selectedIdea = ref<Idea | null>(null);
const showModal    = ref(false);
const editingIdea  = ref<Idea | null>(null);
const deleteTarget = ref<Idea | null>(null);
const saving       = ref(false);

const columns = [
  { status: 'idea',     label: 'Idea' },
  { status: 'planning', label: 'Planning' },
  { status: 'ready',    label: 'Ready' },
];

const platformOptions = [
  { value: 'tiktok',    label: 'TikTok',    icon: 'pi pi-mobile' },
  { value: 'instagram', label: 'Instagram', icon: 'pi pi-instagram' },
  { value: 'youtube',   label: 'YouTube',   icon: 'pi pi-youtube' },
];

const form = ref({
  title: '',
  concept: '',
  target_platforms: [] as string[],
  target_date: '',
  status: 'idea',
  tags: '',
});

function ideasByStatus(status: string) {
  return ideas.value.filter(i => i.status === status);
}

function platformIcon(p: string) {
  return { youtube: 'pi pi-youtube', tiktok: 'pi pi-mobile', instagram: 'pi pi-instagram' }[p] ?? 'pi pi-video';
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
}

async function load() {
  if (!authStore.userId) return;
  loading.value = true;
  try {
    ideas.value = await listIdeas(authStore.userId);
  } finally {
    loading.value = false;
  }
}

onMounted(load);

function openCreateModal() {
  editingIdea.value = null;
  form.value = { title: '', concept: '', target_platforms: [], target_date: '', status: 'idea', tags: '' };
  showModal.value = true;
}

function openEditModal(idea: Idea) {
  editingIdea.value = idea;
  form.value = {
    title: idea.title,
    concept: idea.concept || '',
    target_platforms: [...(idea.target_platforms || [])],
    target_date: idea.target_date ? idea.target_date.split('T')[0] : '',
    status: idea.status,
    tags: (idea.tags || []).join(', '),
  };
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingIdea.value = null;
}

async function saveIdea() {
  if (!authStore.userId || !form.value.title.trim()) return;
  saving.value = true;
  try {
    const tags = form.value.tags
      .split(',')
      .map(t => t.trim())
      .filter(Boolean);
    if (editingIdea.value) {
      await updateIdea(editingIdea.value.id, {
        user_id: authStore.userId,
        title: form.value.title,
        concept: form.value.concept || null,
        target_platforms: form.value.target_platforms,
        target_date: form.value.target_date || null,
        status: form.value.status,
        tags,
      });
      toast.add({ severity: 'success', summary: 'Saved', life: 2000 });
    } else {
      await createIdea({
        user_id: authStore.userId,
        title: form.value.title,
        concept: form.value.concept || undefined,
        target_platforms: form.value.target_platforms,
        target_date: form.value.target_date || undefined,
        status: form.value.status,
        tags,
      });
      toast.add({ severity: 'success', summary: 'Idea created', life: 2000 });
    }
    closeModal();
    await load();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Could not save idea', life: 3000 });
  } finally {
    saving.value = false;
  }
}

function confirmDelete(idea: Idea) {
  deleteTarget.value = idea;
}

async function doDelete() {
  if (!deleteTarget.value || !authStore.userId) return;
  saving.value = true;
  try {
    await deleteIdea(deleteTarget.value.id, authStore.userId);
    if (selectedIdea.value?.id === deleteTarget.value.id) selectedIdea.value = null;
    deleteTarget.value = null;
    await load();
    toast.add({ severity: 'success', summary: 'Deleted', life: 2000 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Could not delete idea', life: 3000 });
  } finally {
    saving.value = false;
  }
}

function goToUpload(idea: Idea) {
  router.push({
    path: '/upload',
    query: {
      title: idea.title,
      description: idea.concept || '',
      platforms: (idea.target_platforms || []).join(','),
      tags: (idea.tags || []).join(','),
    },
  });
}
</script>

<style scoped>
.ideas-view-wrap {
  display: flex;
  height: 100%;
  gap: 0;
  overflow: hidden;
}

.ideas-view {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  padding: 0 1rem 2rem;
  transition: flex 0.3s ease;
}

.panel-open .ideas-view { flex: 1; }

.ideas-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.page-title   { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.2rem; }
.page-subtitle{ font-size: 0.875rem; color: var(--text-secondary); margin: 0; }

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #4f7fff, #7c3aed);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.15s;
}
.btn-primary:hover { opacity: 0.85; }

/* Kanban */
.kanban-board {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  align-items: start;
}

.kanban-col {
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-color, #3f3f46);
  border-radius: 12px;
  padding: 0.875rem;
  min-height: 200px;
}

.col-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.col-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.col-dot.idea     { background: #60a5fa; }
.col-dot.planning { background: #fb923c; }
.col-dot.ready    { background: #4ade80; }

.col-title { font-size: 0.8125rem; font-weight: 700; color: var(--text-primary); flex: 1; }
.col-count {
  font-size: 0.72rem;
  font-weight: 700;
  background: rgba(255,255,255,0.08);
  padding: 1px 6px;
  border-radius: 10px;
  color: var(--text-muted, #71717a);
}

.col-cards { display: flex; flex-direction: column; gap: 0.5rem; }

.idea-card {
  background: var(--surface-card, #27272a);
  border: 1px solid var(--border-color, #3f3f46);
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: border-color 0.15s, transform 0.1s;
}
.idea-card:hover { border-color: rgba(124,58,237,0.35); transform: translateY(-1px); }
.idea-card.selected { border-color: rgba(124,58,237,0.6); background: rgba(124,58,237,0.05); }

.card-title {
  font-size: 0.8375rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-concept {
  font-size: 0.775rem;
  color: var(--text-muted, #71717a);
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.card-platforms { display: flex; gap: 0.35rem; }
.card-platforms i { font-size: 0.8rem; color: var(--text-muted, #71717a); }

.card-date {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.72rem;
  color: var(--text-muted, #71717a);
}
.card-date i { font-size: 0.65rem; }

.card-actions {
  display: flex;
  gap: 0.25rem;
  justify-content: flex-end;
}

.btn-optimize, .btn-edit, .btn-delete, .btn-upload-card {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: rgba(255,255,255,0.04);
  color: var(--text-muted, #71717a);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  transition: background 0.15s, color 0.15s;
}
.btn-optimize:hover { background: rgba(124,58,237,0.15); color: #a78bfa; }
.btn-edit:hover     { background: rgba(59,130,246,0.15); color: #60a5fa; }
.btn-delete:hover   { background: rgba(239,68,68,0.15);  color: #f87171; }
.btn-upload-card    { background: rgba(16,185,129,0.1); color: #34d399; border-color: rgba(16,185,129,0.25); }
.btn-upload-card:hover { background: rgba(16,185,129,0.2); color: #4ade80; }

.empty-col {
  padding: 1rem 0;
  text-align: center;
  font-size: 0.8rem;
  color: var(--text-muted, #71717a);
  font-style: italic;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-secondary);
  padding: 2rem;
}

/* Optimize panel slide-in */
.optimize-panel-wrap {
  width: 340px;
  flex-shrink: 0;
  border-left: 1px solid var(--border-color, #3f3f46);
  background: var(--surface-card, #27272a);
  overflow-y: auto;
  height: 100%;
}

.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: all 0.25s ease;
}
.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.idea-modal, .confirm-modal {
  background: var(--bg-card, #1e293b);
  border: 1px solid var(--border-color, #334155);
  border-radius: 14px;
  width: 100%;
  max-width: 480px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid var(--border-color);
}
.modal-header h3 { margin: 0; font-size: 1rem; font-weight: 700; color: var(--text-primary); }
.modal-close { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.9rem; padding: 2px; }

.modal-body { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 1rem; max-height: 65vh; overflow-y: auto; }

.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-group label { font-size: 0.8125rem; font-weight: 600; color: var(--text-secondary); }

.form-input, .form-textarea, .form-select {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-color, #334155);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
  transition: border-color 0.15s;
}
.form-input:focus, .form-textarea:focus, .form-select:focus { border-color: rgba(124,58,237,0.5); }
.form-textarea { resize: vertical; }
.form-select { cursor: pointer; }

.platform-checks { display: flex; gap: 1rem; flex-wrap: wrap; }
.check-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  cursor: pointer;
}
.check-label input { cursor: pointer; }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
}

.btn-cancel {
  padding: 0.45rem 1rem;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.15s;
}
.btn-cancel:hover { background: rgba(255,255,255,0.04); }

.btn-save {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 1.25rem;
  background: linear-gradient(135deg, #4f7fff, #7c3aed);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-save:not(:disabled):hover { opacity: 0.85; }

/* Confirm modal */
.confirm-modal { max-width: 380px; padding: 1.5rem; }
.confirm-modal h3 { margin: 0 0 0.5rem; font-size: 1rem; color: var(--text-primary); }
.confirm-modal p  { margin: 0 0 1.25rem; font-size: 0.875rem; color: var(--text-secondary); }
.confirm-actions  { display: flex; gap: 0.75rem; justify-content: flex-end; }
.btn-danger {
  padding: 0.45rem 1rem;
  background: #ef4444;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn-danger:hover { opacity: 0.85; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 768px) {
  .kanban-board { grid-template-columns: 1fr; }
  .ideas-view-wrap.panel-open { flex-direction: column; }
  .optimize-panel-wrap { width: 100%; height: auto; border-left: none; border-top: 1px solid var(--border-color); }
}
</style>
