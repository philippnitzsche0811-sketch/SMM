<template>
  <div class="group-card" @click="$emit('click')">
    <div class="group-card-header">
      <div class="group-name">{{ group.name }}</div>
      <Tag
        :value="group.status"
        :severity="statusSeverity"
        class="group-status-tag"
      />
    </div>

    <div class="group-meta">
      <div class="meta-item">
        <i class="pi pi-video"></i>
        {{ group.video_count }} video{{ group.video_count !== 1 ? 's' : '' }}
      </div>
      <div class="meta-item">
        <i class="pi pi-link"></i>
        {{ platformsLabel }}
      </div>
    </div>

    <div v-if="group.next_upload" class="next-upload">
      <i class="pi pi-clock"></i>
      Next: {{ formatDate(group.next_upload) }}
    </div>
    <div v-else-if="group.video_count === 0" class="next-upload muted">
      <i class="pi pi-inbox"></i>
      Empty — add videos to get started
    </div>

    <div class="group-card-footer">
      <Button
        icon="pi pi-arrow-right"
        label="View"
        size="small"
        text
        @click.stop="$emit('click')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import type { UploadGroup } from '@/types/upload_group.types';

const props = defineProps<{ group: UploadGroup }>();
defineEmits<{ click: [] }>();

const statusSeverity = computed(() => ({
  active: 'success',
  paused: 'warning',
  completed: 'secondary',
}[props.group.status] as any));

const platformsLabel = computed(() =>
  (props.group.platforms || [])
    .map((p: string) => ({ youtube: 'YT', tiktok: 'TT', instagram: 'IG' }[p] ?? p))
    .join(' · ')
);

function formatDate(iso: string) {
  try {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    }).format(new Date(iso));
  } catch { return iso; }
}
</script>

<style scoped>
.group-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 1.25rem;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, transform 0.15s;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  position: relative;
  overflow: hidden;
}
.group-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(16,185,129,0.4), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.group-card:hover {
  border-color: rgba(16,185,129,0.3);
  background: rgba(16,185,129,0.03);
  transform: translateY(-2px);
}
.group-card:hover::before { opacity: 1; }

.group-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.group-name {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-primary);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.group-meta {
  display: flex;
  gap: 1rem;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.825rem;
  color: var(--text-secondary);
}
.meta-item i { font-size: 0.8rem; color: var(--text-disabled); }

.next-upload {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: #6ee7b7;
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(16,185,129,0.2);
  border-radius: 8px;
  padding: 0.35rem 0.625rem;
}
.next-upload.muted { color: var(--text-disabled); background: transparent; border-color: rgba(255,255,255,0.06); }
.next-upload i { font-size: 0.75rem; }

.group-card-footer {
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding-top: 0.625rem;
  margin-top: 0.125rem;
}
</style>
