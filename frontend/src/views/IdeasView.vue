<template>
  <div class="ideas-view">
    <div class="ideas-header">
      <div>
        <h1 class="page-title">Ideen</h1>
        <p class="page-subtitle">Plane deinen Content bevor du die Kamera anmachst</p>
      </div>
      <button class="btn-primary" @click="openCreateModal">
        <i class="pi pi-plus"></i> Neue Idee
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
            @click="openEditModal(idea)"
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
                v-if="idea.status === 'ready'"
                class="btn-to-upload"
                @click.stop="goToUpload(idea)"
                title="Zu Upload weiterleiten"
              >
                <i class="pi pi-cloud-upload"></i> Hochladen
              </button>
              <button class="btn-delete" @click.stop="confirmDelete(idea)" title="Löschen">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </div>

          <div class="empty-col" v-if="ideasByStatus(col.status).length === 0">
            Keine Ideen hier
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <i class="pi pi-spin pi-spinner"></i> Lade Ideen...
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="idea-modal">
        <div class="modal-header">
          <h3>{{ editingIdea ? 'Idee bearbeiten' : 'Neue Idee' }}</h3>
          <button class="modal-close" @click="closeModal"><i class="pi pi-times"></i></button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label>Titel *</label>
            <input
              v-model="form.title"
              type="text"
              placeholder="Was ist das Video-Thema?"
              class="form-input"
              maxlength="120"
            />
          </div>

          <div class="form-group">
            <label>Konzept / Beschreibung</label>
            <textarea
              v-model="form.concept"
              placeholder="Worum geht es? Welcher Hook? Was ist der Call to Action?"
              class="form-textarea"
              rows="3"
            />
          </div>

          <div class="form-group">
            <label>Zielplattformen</label>
            <div class="platform-checkboxes">
              <label v-for="p in ['tiktok', 'instagram', 'youtube']" :key="p" class="platform-check">
                <input
                  type="checkbox"
                  :value="p"
                  v-model="form.target_platforms"
                />
                <i :class="platformIcon(p)"></i> {{ p }}
              </label>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Zieldatum</label>
              <input v-model="form.target_date" type="date" class="form-input" />
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="form.status" class="form-input">
                <option value="idea">Idee</option>
                <option value="filming">Dreht</option>
                <option value="editing">Schneidet</option>
                <option value="ready">Fertig</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Tags (kommagetrennt)</label>
            <input
              v-model="tagsInput"
              type="text"
              placeholder="gaming, tutorial, deutsch"
              class="form-input"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModal">Abbrechen</button>
          <button class="btn-primary" @click="saveIdea" :disabled="!form.title.trim() || saving">
            <i v-if="saving" class="pi pi-spin pi-spinner"></i>
            {{ editingIdea ? 'Speichern' : 'Erstellen' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { listIdeas, createIdea, updateIdea, deleteIdea } from '@/services/api';

interface Idea {
  id: string;
  user_id: string;
  title: string;
  concept?: string;
  target_platforms: string[];
  target_date?: string;
  status: string;
  tags: string[];
  ai_suggestions: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

const authStore = useAuthStore();
const router = useRouter();

const loading = ref(false);
const saving = ref(false);
const ideas = ref<Idea[]>([]);
const showModal = ref(false);
const editingIdea = ref<Idea | null>(null);

const form = ref({
  title: '',
  concept: '',
  target_platforms: [] as string[],
  target_date: '',
  status: 'idea',
});
const tagsInput = ref('');

const columns = [
  { status: 'idea',    label: 'Idee' },
  { status: 'filming', label: 'Drehen' },
  { status: 'editing', label: 'Schneiden' },
  { status: 'ready',   label: 'Bereit' },
];

function ideasByStatus(status: string) {
  return ideas.value.filter(i => i.status === status);
}

function platformIcon(p: string) {
  const map: Record<string, string> = {
    tiktok: 'pi pi-tiktok',
    youtube: 'pi pi-youtube',
    instagram: 'pi pi-instagram',
  };
  return map[p] || 'pi pi-send';
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('de-DE', { day: '2-digit', month: 'short' });
}

async function loadIdeas() {
  const userId = authStore.userId;
  if (!userId) return;
  loading.value = true;
  try {
    ideas.value = await listIdeas(userId);
  } catch (e) {
    console.error('Ideen laden fehlgeschlagen', e);
  } finally {
    loading.value = false;
  }
}

function openCreateModal() {
  editingIdea.value = null;
  form.value = { title: '', concept: '', target_platforms: [], target_date: '', status: 'idea' };
  tagsInput.value = '';
  showModal.value = true;
}

function openEditModal(idea: Idea) {
  editingIdea.value = idea;
  form.value = {
    title: idea.title,
    concept: idea.concept || '',
    target_platforms: [...idea.target_platforms],
    target_date: idea.target_date ? idea.target_date.slice(0, 10) : '',
    status: idea.status,
  };
  tagsInput.value = (idea.tags || []).join(', ');
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingIdea.value = null;
}

async function saveIdea() {
  const userId = authStore.userId;
  if (!userId || !form.value.title.trim()) return;
  saving.value = true;
  try {
    const tags = tagsInput.value.split(',').map(t => t.trim()).filter(Boolean);
    const payload = {
      user_id: userId,
      title: form.value.title.trim(),
      concept: form.value.concept || undefined,
      target_platforms: form.value.target_platforms,
      target_date: form.value.target_date || undefined,
      status: form.value.status,
      tags,
    };

    if (editingIdea.value) {
      const updated = await updateIdea(editingIdea.value.id, payload);
      const idx = ideas.value.findIndex(i => i.id === editingIdea.value!.id);
      if (idx !== -1) ideas.value[idx] = updated;
    } else {
      const created = await createIdea(payload);
      ideas.value.unshift(created);
    }
    closeModal();
  } catch (e) {
    console.error('Idee speichern fehlgeschlagen', e);
  } finally {
    saving.value = false;
  }
}

async function confirmDelete(idea: Idea) {
  const userId = authStore.userId;
  if (!userId) return;
  if (!confirm(`Idee "${idea.title}" wirklich löschen?`)) return;
  try {
    await deleteIdea(idea.id, userId);
    ideas.value = ideas.value.filter(i => i.id !== idea.id);
  } catch (e) {
    console.error('Idee löschen fehlgeschlagen', e);
  }
}

function goToUpload(idea: Idea) {
  router.push({
    path: '/upload',
    query: {
      title: idea.title,
      description: idea.concept || '',
      platforms: (idea.target_platforms || []).join(','),
    },
  });
}

onMounted(loadIdeas);
</script>

<style scoped>
.ideas-view {
  padding: 1.5rem 2rem;
  max-width: 1400px;
}

.ideas-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #f4f4f5);
  margin: 0;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted, #71717a);
  margin: 0.25rem 0 0;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--primary-600, #7c3aed);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.1rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  text-decoration: none;
}
.btn-primary:hover { background: var(--primary-700, #6d28d9); }
.btn-primary:disabled { opacity: 0.5; cursor: default; }

.btn-secondary {
  background: var(--surface-card, #27272a);
  color: var(--text-secondary, #a1a1aa);
  border: 1px solid var(--border-color, #3f3f46);
  border-radius: 8px;
  padding: 0.5rem 1.1rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-secondary:hover { background: var(--surface-hover, #3f3f46); }

/* Kanban */
.kanban-board {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  align-items: start;
}

@media (max-width: 900px) {
  .kanban-board { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .kanban-board { grid-template-columns: 1fr; }
}

.kanban-col {
  background: var(--surface-card, #27272a);
  border: 1px solid var(--border-color, #3f3f46);
  border-radius: 12px;
  overflow: hidden;
}

.col-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color, #3f3f46);
}

.col-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.col-dot.idea    { background: #6366f1; }
.col-dot.filming { background: #f59e0b; }
.col-dot.editing { background: #3b82f6; }
.col-dot.ready   { background: #22c55e; }

.col-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary, #f4f4f5);
  flex: 1;
}

.col-count {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted, #71717a);
  background: var(--surface-hover, #3f3f46);
  border-radius: 10px;
  padding: 1px 7px;
}

.col-cards {
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 80px;
}

.idea-card {
  background: var(--surface-ground, #18181b);
  border: 1px solid var(--border-color, #3f3f46);
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.idea-card:hover {
  border-color: var(--primary-500, #8b5cf6);
  background: #1f1f23;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary, #f4f4f5);
  margin-bottom: 0.25rem;
  line-height: 1.3;
}

.card-concept {
  font-size: 0.775rem;
  color: var(--text-muted, #71717a);
  line-height: 1.4;
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
  margin-top: 0.5rem;
}

.card-platforms { display: flex; gap: 4px; font-size: 0.85rem; color: var(--text-muted, #71717a); }

.card-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  color: var(--text-muted, #71717a);
}

.card-actions {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.5rem;
}

.btn-to-upload {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--primary-900, #2e1065);
  color: var(--primary-300, #c4b5fd);
  border: 1px solid var(--primary-700, #6d28d9);
  border-radius: 6px;
  padding: 3px 8px;
  cursor: pointer;
  transition: background 0.15s;
  flex: 1;
}
.btn-to-upload:hover { background: var(--primary-800, #4c1d95); }

.btn-delete {
  background: none;
  border: none;
  color: var(--text-muted, #71717a);
  cursor: pointer;
  font-size: 0.8rem;
  padding: 3px 5px;
  border-radius: 6px;
  transition: color 0.15s, background 0.15s;
}
.btn-delete:hover { color: #f87171; background: rgba(239,68,68,0.08); }

.empty-col {
  font-size: 0.78rem;
  color: var(--text-muted, #71717a);
  text-align: center;
  padding: 1.5rem 0.5rem;
  opacity: 0.6;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted, #71717a);
  padding: 2rem;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.idea-modal {
  background: var(--surface-card, #27272a);
  border: 1px solid var(--border-color, #3f3f46);
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color, #3f3f46);
}

.modal-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary, #f4f4f5);
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-muted, #71717a);
  cursor: pointer;
  font-size: 1rem;
}

.modal-body {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color, #3f3f46);
}

.form-group { display: flex; flex-direction: column; gap: 0.35rem; }

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary, #a1a1aa);
}

.form-input, .form-textarea {
  background: var(--surface-ground, #18181b);
  border: 1px solid var(--border-color, #3f3f46);
  border-radius: 8px;
  color: var(--text-primary, #f4f4f5);
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s;
}
.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--primary-500, #8b5cf6);
}

.form-textarea { resize: vertical; font-family: inherit; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

.platform-checkboxes {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.platform-check {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: var(--text-secondary, #a1a1aa);
  cursor: pointer;
  user-select: none;
}
.platform-check input { cursor: pointer; }
</style>
