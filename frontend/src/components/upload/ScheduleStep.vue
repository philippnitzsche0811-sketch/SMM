<template>
  <div class="schedule-step">
    <div class="schedule-options">
      <label
        v-for="opt in options"
        :key="opt.value"
        class="schedule-option"
        :class="{ selected: scheduleType === opt.value }"
        @click="$emit('update:scheduleType', opt.value)"
      >
        <div class="option-radio">
          <div class="radio-dot" :class="{ active: scheduleType === opt.value }"></div>
        </div>
        <div class="option-body">
          <div class="option-label">
            <i :class="opt.icon"></i>
            {{ opt.label }}
            <span v-if="opt.value === 'recommended' && recommendedLabel" class="rec-badge">
              {{ recommendedLabel }}
            </span>
          </div>
          <p>{{ opt.description }}</p>
        </div>
      </label>
    </div>

    <!-- Datetime picker -->
    <div v-if="scheduleType === 'datetime'" class="schedule-detail">
      <label>Date and time (your local timezone)</label>
      <Calendar
        :modelValue="scheduledAt ? new Date(scheduledAt) : null"
        @update:modelValue="onDateSelect"
        showTime
        hourFormat="24"
        :minDate="minDate"
        class="w-full"
        dateFormat="dd.mm.yy"
        placeholder="Select date and time"
      />
    </div>

    <!-- Group picker -->
    <div v-if="scheduleType === 'group'" class="schedule-detail">
      <label>Select upload group</label>
      <div v-if="groups.length === 0" class="no-groups">
        <i class="pi pi-info-circle"></i>
        No groups yet.
        <button class="create-group-link" @click="$emit('create-group')">Create one</button>
      </div>
      <Dropdown
        v-else
        :modelValue="selectedGroupId"
        @update:modelValue="$emit('update:selectedGroupId', $event)"
        :options="groups"
        optionLabel="name"
        optionValue="id"
        placeholder="Choose a group"
        class="w-full"
      >
        <template #option="{ option }">
          <div class="group-option">
            <span>{{ option.name }}</span>
            <span class="group-count">{{ option.video_count }} video{{ option.video_count !== 1 ? 's' : '' }}</span>
          </div>
        </template>
      </Dropdown>
      <small v-if="selectedGroupId" class="field-hint">
        The scheduler auto-assigns the best upload time based on the group's video count.
      </small>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';
import type { UploadGroup } from '@/types/upload_group.types';

const props = defineProps<{
  scheduleType: string;
  scheduledAt: string | null;
  selectedGroupId: string | null;
  groups: UploadGroup[];
  recommendedAt?: string | null;
}>();

const emit = defineEmits<{
  'update:scheduleType': [value: string];
  'update:scheduledAt': [value: string | null];
  'update:selectedGroupId': [value: string | null];
  'create-group': [];
}>();

const minDate = new Date();

const options = [
  {
    value: 'now',
    label: 'Publish Now',
    icon: 'pi pi-send',
    description: 'Upload to all selected platforms immediately.',
  },
  {
    value: 'recommended',
    label: 'Recommended Time',
    icon: 'pi pi-star',
    description: 'Upload at the optimal time for your platforms — based on when your audience is most active.',
  },
  {
    value: 'datetime',
    label: 'Schedule for Later',
    icon: 'pi pi-clock',
    description: 'Choose a specific date and time for the upload.',
  },
  {
    value: 'group',
    label: 'Add to Upload Group',
    icon: 'pi pi-calendar',
    description: 'Queue this video in a group — the scheduler picks the best time automatically.',
  },
];

const recommendedLabel = computed(() => {
  if (!props.recommendedAt) return null;
  const d = new Date(props.recommendedAt);
  return d.toLocaleDateString('en-GB', { weekday: 'short', month: 'short', day: 'numeric' })
    + ' · '
    + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
});

function onDateSelect(date: Date | null) {
  emit('update:scheduledAt', date ? date.toISOString() : null);
}
</script>

<style scoped>
.schedule-step { display: flex; flex-direction: column; gap: 1.25rem; }

.schedule-options { display: flex; flex-direction: column; gap: 0.625rem; }

.schedule-option {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.125rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.schedule-option.selected {
  border-color: rgba(79,127,255,0.4);
  background: rgba(79,127,255,0.06);
}
.schedule-option:hover:not(.selected) {
  border-color: rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.03);
}

.option-radio { padding-top: 2px; flex-shrink: 0; }

.radio-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.2);
  transition: border-color 0.2s;
  position: relative;
}
.radio-dot.active { border-color: #4f7fff; }
.radio-dot.active::after {
  content: '';
  position: absolute;
  inset: 3px;
  border-radius: 50%;
  background: #4f7fff;
}

.option-body { flex: 1; }
.option-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.2rem;
  flex-wrap: wrap;
}
.option-label i { color: #7da5ff; font-size: 0.875rem; }

.rec-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  background: rgba(79,127,255,0.15);
  border: 1px solid rgba(79,127,255,0.3);
  border-radius: 10px;
  color: #93c5fd;
  white-space: nowrap;
}

.option-body p { font-size: 0.825rem; color: var(--text-secondary); margin: 0; }

.schedule-detail {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem 1.125rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
}
.schedule-detail label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); }

.no-groups {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  padding: 0.75rem 0;
}
.create-group-link {
  background: none;
  border: none;
  color: #4f7fff;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
  text-decoration: underline;
}
.no-groups i { color: var(--text-disabled); }

.group-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.group-count { font-size: 0.78rem; color: var(--text-disabled); }

.field-hint { font-size: 0.78rem; color: var(--text-disabled); }
</style>
