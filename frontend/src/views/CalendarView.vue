<template>
  <div class="calendar-view">
    <div class="calendar-header">
      <div class="header-left">
        <h1 class="page-title">Kalender</h1>
        <p class="page-subtitle">Deine geplanten Uploads im Überblick</p>
      </div>
      <div class="header-right">
        <button class="btn-nav" @click="prevMonth">
          <i class="pi pi-chevron-left"></i>
        </button>
        <span class="month-label">{{ monthLabel }}</span>
        <button class="btn-nav" @click="nextMonth">
          <i class="pi pi-chevron-right"></i>
        </button>
        <button class="btn-today" @click="goToday">Heute</button>
      </div>
    </div>

    <div class="calendar-grid-wrap">
      <!-- Wochentags-Header -->
      <div class="weekday-row">
        <div v-for="day in weekdays" :key="day" class="weekday-cell">{{ day }}</div>
      </div>

      <!-- Tage -->
      <div class="days-grid">
        <div
          v-for="cell in calendarCells"
          :key="cell.key"
          class="day-cell"
          :class="{
            'other-month': !cell.currentMonth,
            'today': cell.isToday,
          }"
        >
          <div class="day-number">{{ cell.day }}</div>
          <div class="day-events">
            <div
              v-for="event in cell.events"
              :key="event.id"
              class="event-chip"
              :class="event.source"
              @click="openEvent(event)"
              :title="event.title"
            >
              <span class="event-platform-icons">
                <i
                  v-for="p in event.platforms.slice(0, 2)"
                  :key="p"
                  :class="platformIcon(p)"
                ></i>
              </span>
              <span class="event-title-text">{{ event.title }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Detail Modal -->
    <div v-if="selectedEvent" class="modal-backdrop" @click.self="selectedEvent = null">
      <div class="event-modal">
        <button class="modal-close" @click="selectedEvent = null">
          <i class="pi pi-times"></i>
        </button>
        <h3>{{ selectedEvent.title }}</h3>
        <div class="modal-row">
          <i class="pi pi-calendar"></i>
          <span>{{ formatDateTime(selectedEvent.scheduled_at) }}</span>
        </div>
        <div class="modal-row">
          <i class="pi pi-send"></i>
          <span>{{ selectedEvent.platforms.join(', ') }}</span>
        </div>
        <div class="modal-row">
          <i class="pi pi-info-circle"></i>
          <span class="status-badge" :class="selectedEvent.status">{{ selectedEvent.status }}</span>
        </div>
        <div v-if="selectedEvent.group_name" class="modal-row">
          <i class="pi pi-folder"></i>
          <span>Gruppe: {{ selectedEvent.group_name }}</span>
        </div>
      </div>
    </div>

    <!-- Loading / Empty -->
    <div v-if="loading" class="state-overlay">
      <i class="pi pi-spin pi-spinner"></i>
      <span>Lade Kalender...</span>
    </div>
    <div v-else-if="!loading && totalEvents === 0" class="empty-state">
      <i class="pi pi-calendar-plus empty-icon"></i>
      <p>Keine geplanten Uploads in diesem Monat.</p>
      <router-link to="/upload" class="btn-primary">Video planen</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { getCalendarEvents } from '@/services/api';

interface CalendarEvent {
  id: string;
  title: string;
  platforms: string[];
  scheduled_at: string;
  status: string;
  source: 'direct' | 'group';
  group_name?: string;
  group_id?: string;
}

const authStore = useAuthStore();
const loading = ref(false);
const events = ref<CalendarEvent[]>([]);
const selectedEvent = ref<CalendarEvent | null>(null);

const today = new Date();
const currentYear = ref(today.getFullYear());
const currentMonth = ref(today.getMonth()); // 0-based

const weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];

const monthLabel = computed(() => {
  const d = new Date(currentYear.value, currentMonth.value, 1);
  return d.toLocaleDateString('de-DE', { month: 'long', year: 'numeric' });
});

const totalEvents = computed(() => events.value.length);

// Build the calendar grid (6 rows × 7 cols)
const calendarCells = computed(() => {
  const year = currentYear.value;
  const month = currentMonth.value;

  const firstDay = new Date(year, month, 1);
  // Monday = 0, Sunday = 6
  let startDow = firstDay.getDay() - 1;
  if (startDow < 0) startDow = 6;

  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const prevMonthDays = new Date(year, month, 0).getDate();

  const cells: {
    key: string;
    day: number;
    date: Date;
    currentMonth: boolean;
    isToday: boolean;
    events: CalendarEvent[];
  }[] = [];

  // Prev month fill
  for (let i = startDow - 1; i >= 0; i--) {
    const d = prevMonthDays - i;
    const date = new Date(year, month - 1, d);
    cells.push({ key: `prev-${d}`, day: d, date, currentMonth: false, isToday: false, events: [] });
  }

  const todayStr = toDateStr(new Date());

  // Current month
  for (let d = 1; d <= daysInMonth; d++) {
    const date = new Date(year, month, d);
    const dateStr = toDateStr(date);
    const dayEvents = events.value.filter(e => e.scheduled_at.startsWith(dateStr));
    cells.push({
      key: `cur-${d}`,
      day: d,
      date,
      currentMonth: true,
      isToday: dateStr === todayStr,
      events: dayEvents,
    });
  }

  // Next month fill (complete to 6 rows = 42 cells)
  const remaining = 42 - cells.length;
  for (let d = 1; d <= remaining; d++) {
    const date = new Date(year, month + 1, d);
    cells.push({ key: `next-${d}`, day: d, date, currentMonth: false, isToday: false, events: [] });
  }

  return cells;
});

function toDateStr(d: Date) {
  return d.toISOString().slice(0, 10);
}

async function loadEvents() {
  const userId = authStore.userId;
  if (!userId) return;
  loading.value = true;
  try {
    const firstDay = new Date(currentYear.value, currentMonth.value, 1);
    const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0);
    const data = await getCalendarEvents(userId, toDateStr(firstDay), toDateStr(lastDay) + 'T23:59:59');
    events.value = data.events || [];
  } catch (e) {
    console.error('Kalender laden fehlgeschlagen', e);
  } finally {
    loading.value = false;
  }
}

function prevMonth() {
  if (currentMonth.value === 0) { currentMonth.value = 11; currentYear.value--; }
  else currentMonth.value--;
}

function nextMonth() {
  if (currentMonth.value === 11) { currentMonth.value = 0; currentYear.value++; }
  else currentMonth.value++;
}

function goToday() {
  currentMonth.value = today.getMonth();
  currentYear.value = today.getFullYear();
}

function openEvent(event: CalendarEvent) {
  selectedEvent.value = event;
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString('de-DE', {
    weekday: 'short', day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function platformIcon(platform: string) {
  const map: Record<string, string> = {
    tiktok: 'pi pi-tiktok',
    youtube: 'pi pi-youtube',
    instagram: 'pi pi-instagram',
  };
  return map[platform] || 'pi pi-send';
}

watch([currentMonth, currentYear], loadEvents);
onMounted(loadEvents);
</script>

<style scoped>
.calendar-view {
  padding: 1.5rem 2rem;
  max-width: 1200px;
  position: relative;
}

.calendar-header {
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

.header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-nav {
  background: var(--surface-card, #27272a);
  border: 1px solid var(--border-color, #3f3f46);
  color: var(--text-primary, #f4f4f5);
  border-radius: 8px;
  width: 34px;
  height: 34px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.btn-nav:hover { background: var(--surface-hover, #3f3f46); }

.month-label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary, #f4f4f5);
  min-width: 160px;
  text-align: center;
}

.btn-today {
  background: var(--primary-600, #7c3aed);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.4rem 0.9rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-today:hover { background: var(--primary-700, #6d28d9); }

.calendar-grid-wrap {
  background: var(--surface-card, #27272a);
  border: 1px solid var(--border-color, #3f3f46);
  border-radius: 12px;
  overflow: hidden;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 1px solid var(--border-color, #3f3f46);
}

.weekday-cell {
  padding: 0.6rem;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted, #71717a);
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.day-cell {
  min-height: 100px;
  border-right: 1px solid var(--border-color, #3f3f46);
  border-bottom: 1px solid var(--border-color, #3f3f46);
  padding: 0.4rem;
  position: relative;
}
.day-cell:nth-child(7n) { border-right: none; }

.day-number {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary, #a1a1aa);
  margin-bottom: 0.25rem;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.day-cell.today .day-number {
  background: var(--primary-600, #7c3aed);
  color: white;
}

.day-cell.other-month .day-number {
  opacity: 0.3;
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  background: var(--primary-900, #2e1065);
  color: var(--primary-300, #c4b5fd);
  border: 1px solid var(--primary-700, #6d28d9);
  transition: background 0.15s;
}
.event-chip.group {
  background: #1c1917;
  color: #d6d3d1;
  border-color: #57534e;
}
.event-chip:hover { filter: brightness(1.15); }

.event-platform-icons { display: flex; gap: 2px; font-size: 0.65rem; }
.event-title-text { overflow: hidden; text-overflow: ellipsis; flex: 1; }

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.event-modal {
  background: var(--surface-card, #27272a);
  border: 1px solid var(--border-color, #3f3f46);
  border-radius: 12px;
  padding: 1.5rem;
  min-width: 320px;
  max-width: 480px;
  position: relative;
}

.event-modal h3 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary, #f4f4f5);
  padding-right: 2rem;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: var(--text-muted, #71717a);
  cursor: pointer;
  font-size: 1rem;
}

.modal-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary, #a1a1aa);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--surface-hover, #3f3f46);
}
.status-badge.uploaded, .status-badge.done { background: #14532d; color: #86efac; }
.status-badge.pending, .status-badge.queued { background: #1e3a5f; color: #93c5fd; }
.status-badge.failed { background: #450a0a; color: #fca5a5; }
.status-badge.processing, .status-badge.uploading { background: #713f12; color: #fde68a; }

/* States */
.state-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-muted, #71717a);
  background: rgba(0,0,0,0.3);
  border-radius: 12px;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted, #71717a);
}

.empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
  opacity: 0.4;
}

.btn-primary {
  display: inline-block;
  margin-top: 1rem;
  background: var(--primary-600, #7c3aed);
  color: white;
  text-decoration: none;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  transition: background 0.15s;
}
.btn-primary:hover { background: var(--primary-700, #6d28d9); }
</style>
