<template>
  <div class="admin-view">
    <div class="page-header">
      <h1><i class="pi pi-shield"></i> Admin — Trend-Daten</h1>
      <p class="subtitle">Manuell recherchierte Plattform-Daten für den KI-Optimizer</p>
    </div>

    <!-- Research guide -->
    <div class="admin-card guide-card">
      <h3 class="card-title"><i class="pi pi-info-circle"></i> Woher kommen die Daten?</h3>
      <div class="guide-grid">
        <div class="guide-item">
          <strong>TikTok</strong>
          <span>creative.tiktok.com → Trending → Hashtags (Filter: Deutschland, Kategorie)</span>
        </div>
        <div class="guide-item">
          <strong>YouTube</strong>
          <span>youtube.com/feed/trending + studio.youtube.com → Analytics → Research</span>
        </div>
        <div class="guide-item">
          <strong>Instagram</strong>
          <span>instagram.com/explore → Hashtag-Seiten der Top-Reels</span>
        </div>
      </div>
    </div>

    <!-- Raw paste + extract -->
    <div class="admin-card extract-card">
      <h3 class="card-title"><i class="pi pi-bolt"></i> Rohdaten einfügen &amp; extrahieren</h3>
      <p class="extract-hint">
        Kopiere einfach alles rein — TikTok Creative Center Liste, Instagram Captions, YouTube Titel — und klick auf Extrahieren.
        Die Felder unten werden automatisch befüllt.
      </p>

      <div class="form-field">
        <textarea
          v-model="rawText"
          rows="6"
          class="form-textarea"
          placeholder="#gaming #tutorial #howto&#10;Wie ich in 5 Tagen...&#10;Das beste Setup für...&#10;5 Tricks die jeder kennen sollte&#10;..."
        />
      </div>

      <div class="form-actions">
        <span v-if="extractError" class="error-msg">{{ extractError }}</span>
        <button class="btn-extract" :disabled="extracting || !rawText.trim()" @click="extractRaw">
          <i class="pi" :class="extracting ? 'pi-spin pi-spinner' : 'pi-sparkles'"></i>
          {{ extracting ? 'Analysiere...' : 'Extrahieren' }}
        </button>
      </div>
    </div>

    <!-- Entry form -->
    <div class="admin-card">
      <h3 class="card-title">Eintrag erstellen / aktualisieren</h3>

      <div class="form-row">
        <div class="form-field">
          <label>Platform</label>
          <select v-model="form.platform" class="form-select">
            <option value="youtube">YouTube</option>
            <option value="tiktok">TikTok</option>
            <option value="instagram">Instagram</option>
          </select>
        </div>
        <div class="form-field">
          <label>Kategorie</label>
          <select v-model="form.category" class="form-select">
            <option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <div class="form-field">
        <label>
          Top Hashtags
          <small class="field-hint">kommagetrennt, ohne #</small>
        </label>
        <textarea
          v-model="tagsInput"
          rows="3"
          class="form-textarea"
          placeholder="gaming, tutorial, howto, viral2026, ..."
        />
      </div>

      <div class="form-field">
        <label>
          Häufige Titelwörter
          <small class="field-hint">kommagetrennt — Wörter die in viralen Titeln oft auftauchen</small>
        </label>
        <textarea
          v-model="titleWordsInput"
          rows="2"
          class="form-textarea"
          placeholder="einfach, schnell, kostenlos, Schritt, Anleitung, ..."
        />
      </div>

      <div class="form-field">
        <label>
          Titel-Starter
          <small class="field-hint">ein Starter pro Zeile — typische Einstiegsphrasen</small>
        </label>
        <textarea
          v-model="titleStartersInput"
          rows="3"
          class="form-textarea"
          placeholder="Wie ich ...&#10;5 Wege ...&#10;So geht ...&#10;Das beste ..."
        />
      </div>

      <div class="form-field">
        <label>
          Notizen / Beobachtungen
          <small class="field-hint">Freitext — Tonalität, aktuelle Trends, Auffälligkeiten</small>
        </label>
        <textarea
          v-model="form.notes"
          rows="3"
          class="form-textarea"
          placeholder="z.B.: Titel werden kürzer (unter 50 Zeichen), Emojis am Anfang presenten gut, Thema 'KI-Tools' explodiert gerade..."
        />
      </div>

      <div class="form-actions">
        <span v-if="saveSuccess" class="success-msg"><i class="pi pi-check"></i> Gespeichert</span>
        <span v-if="saveError" class="error-msg">{{ saveError }}</span>
        <button class="btn-primary" :disabled="saving" @click="save">
          <i class="pi pi-save"></i>
          {{ saving ? 'Speichern...' : 'Speichern / Aktualisieren' }}
        </button>
      </div>
    </div>

    <!-- Entries table -->
    <div class="admin-card">
      <h3 class="card-title">Vorhandene Einträge</h3>
      <div v-if="loading" class="status-msg">Lade...</div>
      <div v-else-if="entries.length === 0" class="status-msg muted">Noch keine Einträge. Fang oben an!</div>
      <div v-else class="table-wrap">
        <table class="entries-table">
          <thead>
            <tr>
              <th>Platform</th>
              <th>Kategorie</th>
              <th>Tags (Auszug)</th>
              <th>Titelwörter</th>
              <th>Starter</th>
              <th>Notizen</th>
              <th>Aktualisiert</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in entries" :key="e.id">
              <td>
                <span class="platform-badge" :class="e.platform">{{ e.platform }}</span>
              </td>
              <td>{{ e.category }}</td>
              <td class="tags-cell">
                {{ (e.top_tags || []).slice(0, 5).join(', ') }}
                <span v-if="(e.top_tags || []).length > 5" class="more-hint">+{{ (e.top_tags || []).length - 5 }}</span>
              </td>
              <td class="tags-cell">{{ (e.title_words || []).slice(0, 4).join(', ') }}</td>
              <td class="tags-cell">{{ (e.title_starters || []).slice(0, 2).join(' / ') }}</td>
              <td class="notes-cell">{{ truncate(e.notes, 55) }}</td>
              <td class="date-cell">{{ formatDate(e.updated_at) }}</td>
              <td class="actions-cell">
                <button class="btn-icon" title="In Formular laden" @click="loadEntry(e)">
                  <i class="pi pi-pencil"></i>
                </button>
                <button class="btn-icon btn-delete" title="Löschen" @click="deleteEntry(e.id)">
                  <i class="pi pi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import {
  listAdminTrendData,
  upsertAdminTrendData,
  deleteAdminTrendData,
  parseAdminRawText,
  type AdminTrendDataOut,
} from '@/services/api';

const CATEGORIES = [
  'default', 'gaming', 'education', 'music', 'entertainment',
  'lifestyle', 'tech', 'food', 'sports',
];

const entries       = ref<AdminTrendDataOut[]>([]);
const loading       = ref(false);
const saving        = ref(false);
const saveError     = ref('');
const saveSuccess   = ref(false);

const rawText       = ref('');
const extracting    = ref(false);
const extractError  = ref('');

const form = reactive({ platform: 'youtube', category: 'default', notes: '' });
const tagsInput          = ref('');
const titleWordsInput    = ref('');
const titleStartersInput = ref('');

const parseComma = (s: string) => s.split(',').map(t => t.replace(/^#/, '').trim()).filter(Boolean);
const parseLines = (s: string) => s.split('\n').map(t => t.trim()).filter(Boolean);

async function extractRaw() {
  extractError.value = '';
  extracting.value = true;
  try {
    const result = await parseAdminRawText(rawText.value, form.platform, form.category);
    if (result.top_tags.length)       tagsInput.value          = result.top_tags.join(', ');
    if (result.title_words.length)    titleWordsInput.value    = result.title_words.join(', ');
    if (result.title_starters.length) titleStartersInput.value = result.title_starters.join('\n');
    rawText.value = '';
  } catch (e: any) {
    extractError.value = e?.response?.data?.detail || 'Fehler beim Extrahieren';
  } finally {
    extracting.value = false;
  }
}

async function fetchEntries() {
  loading.value = true;
  try { entries.value = await listAdminTrendData(); }
  finally { loading.value = false; }
}

async function save() {
  saveError.value = '';
  saveSuccess.value = false;
  saving.value = true;
  try {
    await upsertAdminTrendData({
      platform:       form.platform,
      category:       form.category,
      top_tags:       parseComma(tagsInput.value),
      title_words:    parseComma(titleWordsInput.value),
      title_starters: parseLines(titleStartersInput.value),
      notes:          form.notes || undefined,
    });
    saveSuccess.value = true;
    setTimeout(() => { saveSuccess.value = false; }, 3000);
    await fetchEntries();
  } catch (e: any) {
    saveError.value = e?.response?.data?.detail || 'Fehler beim Speichern';
  } finally {
    saving.value = false;
  }
}

function loadEntry(e: AdminTrendDataOut) {
  form.platform          = e.platform;
  form.category          = e.category;
  form.notes             = e.notes || '';
  tagsInput.value          = (e.top_tags || []).join(', ');
  titleWordsInput.value    = (e.title_words || []).join(', ');
  titleStartersInput.value = (e.title_starters || []).join('\n');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function deleteEntry(id: string) {
  if (!confirm('Eintrag wirklich löschen?')) return;
  await deleteAdminTrendData(id);
  await fetchEntries();
}

function formatDate(iso?: string) {
  if (!iso) return '–';
  return new Date(iso).toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' });
}

function truncate(s?: string | null, n = 55) {
  if (!s) return '–';
  return s.length > n ? s.slice(0, n) + '…' : s;
}

onMounted(fetchEntries);
</script>

<style scoped>
.admin-view {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.page-header h1 i { color: #a78bfa; }
.subtitle { font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem; }

.admin-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.card-title i { color: var(--text-secondary); }

/* Guide */
.guide-card { background: rgba(167,139,250,0.04); border-color: rgba(167,139,250,0.2); }

/* Extract */
.extract-card { background: rgba(79,127,255,0.04); border-color: rgba(79,127,255,0.2); }
.extract-hint { font-size: 0.85rem; color: var(--text-secondary); margin: -0.5rem 0 1rem; line-height: 1.5; }

.btn-extract {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(79,127,255,0.15);
  color: #7da5ff;
  border: 1px solid rgba(79,127,255,0.3);
  border-radius: 8px;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-extract:hover:not(:disabled) { background: rgba(79,127,255,0.25); border-color: rgba(79,127,255,0.5); }
.btn-extract:disabled { opacity: 0.4; cursor: not-allowed; }
.guide-grid { display: flex; flex-direction: column; gap: 0.6rem; }
.guide-item { display: flex; gap: 0.75rem; font-size: 0.875rem; }
.guide-item strong { color: var(--text-primary); min-width: 80px; }
.guide-item span { color: var(--text-secondary); }

/* Form */
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-field { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1rem; }
.form-field label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); }
.field-hint { font-weight: 400; color: var(--text-disabled); margin-left: 0.4rem; }

.form-select,
.form-textarea {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
  width: 100%;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}
.form-select:focus,
.form-textarea:focus { border-color: #4f7fff; }
.form-textarea { resize: vertical; }

.form-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 0.75rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #4f7fff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) { background: #3d6ef0; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.success-msg { font-size: 0.8rem; color: #10b981; display: flex; align-items: center; gap: 0.3rem; }
.error-msg   { font-size: 0.8rem; color: #f87171; }

/* Table */
.table-wrap { overflow-x: auto; }
.entries-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.825rem;
}
.entries-table th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap;
}
.entries-table td {
  padding: 0.6rem 0.75rem;
  color: var(--text-primary);
  border-bottom: 1px solid rgba(255,255,255,0.04);
  vertical-align: top;
}
.entries-table tr:last-child td { border-bottom: none; }
.entries-table tr:hover td { background: rgba(255,255,255,0.02); }

.tags-cell   { color: var(--text-secondary); max-width: 160px; }
.notes-cell  { color: var(--text-secondary); max-width: 180px; }
.date-cell   { color: var(--text-disabled);  white-space: nowrap; }
.actions-cell { white-space: nowrap; }
.more-hint   { color: var(--text-disabled); font-size: 0.75rem; }

.platform-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}
.platform-badge.youtube   { background: rgba(255,0,0,0.1);   color: #f87171; }
.platform-badge.tiktok    { background: rgba(0,255,255,0.07); color: #67e8f9; }
.platform-badge.instagram { background: rgba(217,70,239,0.1); color: #e879f9; }

.btn-icon {
  background: none;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem 0.4rem;
  font-size: 0.8rem;
  transition: all 0.2s;
}
.btn-icon:hover { border-color: var(--border-color); color: var(--text-primary); background: rgba(255,255,255,0.04); }
.btn-icon.btn-delete:hover { border-color: rgba(248,113,113,0.3); color: #f87171; }

.status-msg { color: var(--text-secondary); font-size: 0.875rem; padding: 0.5rem 0; }
.status-msg.muted { color: var(--text-disabled); }

@media (max-width: 640px) {
  .form-row { grid-template-columns: 1fr; }
  .admin-card { padding: 1rem; }
}
</style>
