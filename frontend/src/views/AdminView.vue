<template>
  <div class="admin-view">
    <div class="page-header">
      <h1><i class="pi pi-shield"></i> Admin — Trend-Daten</h1>
      <p class="subtitle">Manuell recherchierte Plattform-Daten für den KI-Optimizer</p>
    </div>

    <!-- KI-Token Nutzung -->
    <div class="admin-card token-card">
      <div class="token-card-header">
        <h3 class="card-title" style="margin:0"><i class="pi pi-chart-bar"></i> KI-Token Nutzung</h3>
        <a href="https://console.anthropic.com/usage" target="_blank" rel="noopener" class="console-link">
          <i class="pi pi-external-link"></i> Anthropic Console
        </a>
      </div>

      <div v-if="tokenLoading" class="status-msg">Lade...</div>
      <div v-else-if="tokenError" class="status-msg" style="color:#f87171">{{ tokenError }}</div>
      <div v-else-if="tokenUsage">
        <div class="token-month-header">
          <span class="token-period-label">Diesen Monat ({{ tokenUsage.month_label }})</span>
          <span class="token-calls-badge">{{ tokenUsage.this_month.calls }} API-Aufrufe</span>
        </div>

        <div class="token-stats-grid">
          <div class="token-stat">
            <span class="stat-num">{{ formatTokens(tokenUsage.this_month.total_tokens) }}</span>
            <span class="stat-label">Tokens gesamt</span>
          </div>
          <div class="token-stat">
            <span class="stat-num">{{ formatTokens(tokenUsage.this_month.input_tokens) }}</span>
            <span class="stat-label">Input</span>
          </div>
          <div class="token-stat">
            <span class="stat-num">{{ formatTokens(tokenUsage.this_month.output_tokens) }}</span>
            <span class="stat-label">Output</span>
          </div>
          <div class="token-stat token-stat-cost">
            <span class="stat-num">${{ tokenUsage.this_month.estimated_cost_usd.toFixed(4) }}</span>
            <span class="stat-label">~Kosten (USD)</span>
          </div>
        </div>

        <!-- Budget progress (only if budget set) -->
        <div v-if="tokenUsage.monthly_budget_tokens" class="budget-bar-wrap">
          <div class="budget-bar-labels">
            <span>{{ formatTokens(tokenUsage.this_month.total_tokens) }} / {{ formatTokens(tokenUsage.monthly_budget_tokens) }}</span>
            <span :class="budgetPercent >= 100 ? 'text-danger' : ''">{{ budgetPercent }}%</span>
          </div>
          <div class="budget-bar">
            <div class="budget-fill" :style="{ width: Math.min(budgetPercent, 100) + '%' }" :class="budgetBarClass" />
          </div>
          <div v-if="budgetPercent < 100" class="budget-remaining">
            Noch ~{{ formatTokens(tokenUsage.monthly_budget_tokens - tokenUsage.this_month.total_tokens) }} Tokens übrig
          </div>
          <div v-else class="text-danger" style="font-size:0.8rem;margin-top:0.25rem">Budget überschritten</div>
        </div>

        <div class="token-alltime">
          <i class="pi pi-history" style="color:var(--text-disabled)"></i>
          Gesamt:&nbsp;
          <strong>{{ formatTokens(tokenUsage.all_time.total_tokens) }}</strong> Tokens &nbsp;·&nbsp;
          <strong>{{ tokenUsage.all_time.calls }}</strong> Aufrufe &nbsp;·&nbsp;
          ~<strong>${{ tokenUsage.all_time.estimated_cost_usd.toFixed(4) }}</strong>
        </div>

        <div class="budget-setting-row">
          <label class="budget-setting-label">
            Monatliches Token-Budget
            <small class="field-hint">0 = kein Limit</small>
          </label>
          <div class="budget-input-group">
            <input
              v-model.number="budgetInput"
              type="number"
              min="0"
              step="10000"
              class="form-select budget-input"
              placeholder="z.B. 500000"
            />
            <button class="btn-primary" :disabled="savingBudget" @click="saveBudget">
              {{ savingBudget ? '...' : 'Speichern' }}
            </button>
          </div>
        </div>
      </div>
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

    <!-- Hook Examples -->
    <div class="admin-card hook-card">
      <h3 class="card-title"><i class="pi pi-video"></i> Hook-Beispiele</h3>
      <p class="extract-hint">
        Erfolgreiche Hooks pro Nische &amp; Plattform — werden beim Analyse-Prompt als Referenz mitgegeben.
      </p>

      <!-- Add form -->
      <div class="hook-form-grid">
        <div class="form-field">
          <label>Platform</label>
          <select v-model="hookForm.platform" class="form-select">
            <option value="youtube">YouTube</option>
            <option value="tiktok">TikTok</option>
            <option value="instagram">Instagram</option>
          </select>
        </div>
        <div class="form-field">
          <label>Nische</label>
          <select v-model="hookForm.niche" class="form-select">
            <option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div class="form-field">
          <label>Hook-Typ</label>
          <select v-model="hookForm.hook_type" class="form-select">
            <option value="">– keiner –</option>
            <option value="verbal">Verbal</option>
            <option value="visual">Visual</option>
            <option value="text_overlay">Text Overlay</option>
            <option value="music">Music</option>
            <option value="combo">Combo</option>
          </select>
        </div>
        <div class="form-field">
          <label>Score (1–10)</label>
          <input v-model.number="hookForm.score" type="number" min="1" max="10" class="form-select" placeholder="8" />
        </div>
        <div class="form-field hook-form-full">
          <label>Beschreibung <small class="field-hint">was passiert in den ersten 3–5s?</small></label>
          <textarea v-model="hookForm.description" rows="2" class="form-textarea" placeholder="z.B. Creator schaut direkt in Kamera, stellt provokante Frage ohne Kontext..." />
        </div>
        <div class="form-field hook-form-full">
          <label>Was hat funktioniert?</label>
          <textarea v-model="hookForm.what_worked" rows="2" class="form-textarea" placeholder="z.B. Instant-Pattern-Interrupt + Gesicht sofort sichtbar + 1 Satz Hook" />
        </div>
        <div class="form-field hook-form-full">
          <label>Source URL <small class="field-hint">optional</small></label>
          <input v-model="hookForm.source_url" type="text" class="form-select" placeholder="https://..." />
        </div>
      </div>

      <div class="form-actions">
        <span v-if="hookSaveError" class="error-msg">{{ hookSaveError }}</span>
        <span v-if="hookSaveSuccess" class="success-msg"><i class="pi pi-check"></i> Gespeichert</span>
        <button class="btn-primary" :disabled="hookSaving || !hookForm.niche" @click="saveHookExample">
          <i class="pi pi-plus"></i>
          {{ hookSaving ? 'Speichern...' : 'Hook-Beispiel hinzufügen' }}
        </button>
      </div>

      <!-- Table -->
      <div v-if="hookExamples.length" class="table-wrap" style="margin-top:1.25rem">
        <table class="entries-table">
          <thead>
            <tr>
              <th>Platform</th>
              <th>Nische</th>
              <th>Typ</th>
              <th>Score</th>
              <th>Beschreibung</th>
              <th>Was hat gewirkt?</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ex in hookExamples" :key="ex.id">
              <td><span class="platform-badge" :class="ex.platform">{{ ex.platform }}</span></td>
              <td>{{ ex.niche }}</td>
              <td>{{ ex.hook_type || '–' }}</td>
              <td>
                <span v-if="ex.score" class="score-chip" :class="scoreClass(ex.score)">{{ ex.score }}/10</span>
                <span v-else>–</span>
              </td>
              <td class="notes-cell">{{ truncate(ex.description, 60) }}</td>
              <td class="notes-cell">{{ truncate(ex.what_worked, 60) }}</td>
              <td class="actions-cell">
                <button class="btn-icon btn-delete" title="Löschen" @click="deleteHook(ex.id)">
                  <i class="pi pi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="status-msg muted">Noch keine Hook-Beispiele. Füge oben dein erstes hinzu!</div>
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
import { ref, reactive, computed, onMounted } from 'vue';
import {
  listAdminTrendData,
  upsertAdminTrendData,
  deleteAdminTrendData,
  parseAdminRawText,
  listHookExamples,
  createHookExample,
  deleteHookExample,
  getAdminTokenUsage,
  setAdminTokenBudget,
  type AdminTrendDataOut,
  type HookExampleOut,
  type TokenUsageResponse,
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

// ── Hook Examples ─────────────────────────────────────────────────────────────

const hookExamples   = ref<HookExampleOut[]>([]);
const hookSaving     = ref(false);
const hookSaveError  = ref('');
const hookSaveSuccess = ref(false);

const hookForm = reactive({
  platform: 'youtube',
  niche: 'default',
  hook_type: '',
  description: '',
  what_worked: '',
  score: undefined as number | undefined,
  source_url: '',
});

async function fetchHookExamples() {
  try { hookExamples.value = await listHookExamples(); }
  catch { /* silent */ }
}

async function saveHookExample() {
  hookSaveError.value = '';
  hookSaveSuccess.value = false;
  hookSaving.value = true;
  try {
    await createHookExample({
      platform:    hookForm.platform,
      niche:       hookForm.niche,
      hook_type:   hookForm.hook_type || undefined,
      description: hookForm.description || undefined,
      what_worked: hookForm.what_worked || undefined,
      score:       hookForm.score || undefined,
      source_url:  hookForm.source_url || undefined,
    });
    hookSaveSuccess.value = true;
    setTimeout(() => { hookSaveSuccess.value = false; }, 3000);
    hookForm.description = '';
    hookForm.what_worked = '';
    hookForm.score = undefined;
    hookForm.source_url = '';
    hookForm.hook_type = '';
    await fetchHookExamples();
  } catch (e: any) {
    hookSaveError.value = e?.response?.data?.detail || 'Fehler beim Speichern';
  } finally {
    hookSaving.value = false;
  }
}

async function deleteHook(id: string) {
  if (!confirm('Hook-Beispiel wirklich löschen?')) return;
  await deleteHookExample(id);
  await fetchHookExamples();
}

function scoreClass(score: number) {
  if (score >= 8) return 'score-high';
  if (score >= 5) return 'score-mid';
  return 'score-low';
}

// ── Token Usage ───────────────────────────────────────────────────────────────

const tokenUsage   = ref<TokenUsageResponse | null>(null);
const tokenLoading = ref(false);
const tokenError   = ref('');
const budgetInput  = ref<number | undefined>(undefined);
const savingBudget = ref(false);

const budgetPercent = computed(() => {
  if (!tokenUsage.value?.monthly_budget_tokens) return 0;
  return Math.round((tokenUsage.value.this_month.total_tokens / tokenUsage.value.monthly_budget_tokens) * 100);
});

const budgetBarClass = computed(() => {
  if (budgetPercent.value >= 90) return 'fill-danger';
  if (budgetPercent.value >= 70) return 'fill-warn';
  return 'fill-ok';
});

function formatTokens(n: number) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M';
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K';
  return String(n);
}

async function fetchTokenUsage() {
  tokenLoading.value = true;
  tokenError.value = '';
  try {
    tokenUsage.value = await getAdminTokenUsage();
    budgetInput.value = tokenUsage.value.monthly_budget_tokens ?? undefined;
  } catch (e: any) {
    tokenError.value = e?.response?.data?.detail || 'Fehler beim Laden der Token-Daten';
  } finally {
    tokenLoading.value = false;
  }
}

async function saveBudget() {
  savingBudget.value = true;
  try {
    await setAdminTokenBudget(budgetInput.value || null);
    await fetchTokenUsage();
  } catch {
    /* silent */
  } finally {
    savingBudget.value = false;
  }
}

onMounted(() => { fetchEntries(); fetchHookExamples(); fetchTokenUsage(); });
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

.hook-card { background: rgba(99,102,241,0.04); border-color: rgba(99,102,241,0.18); }

.hook-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 1rem;
}
.hook-form-full { grid-column: 1 / -1; }

.score-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.1rem 0.45rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
}
.score-high { background: rgba(34,197,94,0.12);  color: #22c55e; border-color: rgba(34,197,94,0.25); }
.score-mid  { background: rgba(234,179,8,0.12);   color: #eab308; border-color: rgba(234,179,8,0.25); }
.score-low  { background: rgba(239,68,68,0.12);   color: #ef4444; border-color: rgba(239,68,68,0.25); }

/* Token usage card */
.token-card { background: rgba(16,185,129,0.03); border-color: rgba(16,185,129,0.2); }

.token-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.console-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-decoration: none;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 0.25rem 0.6rem;
  transition: all 0.2s;
}
.console-link:hover { color: var(--text-primary); border-color: rgba(16,185,129,0.4); }

.token-month-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.875rem;
}
.token-period-label { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); }
.token-calls-badge {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 0.1rem 0.5rem;
}

.token-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.token-stat {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.6rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.token-stat-cost { border-color: rgba(16,185,129,0.25); background: rgba(16,185,129,0.05); }

.stat-num   { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.stat-label { font-size: 0.72rem; color: var(--text-disabled); }

.budget-bar-wrap { margin-bottom: 0.75rem; }
.budget-bar-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin-bottom: 0.35rem;
}
.budget-bar {
  height: 8px;
  background: rgba(255,255,255,0.08);
  border-radius: 99px;
  overflow: hidden;
}
.budget-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.4s ease;
}
.fill-ok     { background: linear-gradient(90deg, #10b981, #34d399); }
.fill-warn   { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.fill-danger { background: linear-gradient(90deg, #ef4444, #f87171); }

.budget-remaining {
  font-size: 0.78rem;
  color: #10b981;
  margin-top: 0.3rem;
}
.text-danger { color: #f87171; }

.token-alltime {
  font-size: 0.82rem;
  color: var(--text-secondary);
  padding: 0.625rem 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.token-alltime strong { color: var(--text-primary); }

.budget-setting-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.budget-setting-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
}
.budget-input-group { display: flex; gap: 0.5rem; align-items: center; flex: 1; min-width: 220px; }
.budget-input { max-width: 180px; }

@media (max-width: 640px) {
  .token-stats-grid { grid-template-columns: repeat(2, 1fr); }
  .token-card-header { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
  .budget-setting-row { flex-direction: column; align-items: flex-start; }
}

@media (max-width: 640px) {
  .form-row { grid-template-columns: 1fr; }
  .hook-form-grid { grid-template-columns: 1fr; }
  .hook-form-full { grid-column: 1; }
  .admin-card { padding: 1rem; }
}
</style>
