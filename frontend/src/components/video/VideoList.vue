<template>
  <div class="video-list-container">
    <!-- Empty State -->
    <div v-if="displayVideos.length === 0" class="empty-state">
      <i class="pi pi-video empty-icon"></i>
      <h3>Keine Videos vorhanden</h3>
      <p>Lade dein erstes Video hoch, um loszulegen!</p>
    </div>

    <!-- Video Table -->
    <DataTable 
      v-else
      :value="displayVideos" 
      :paginator="!limit" 
      :rows="10"
      responsiveLayout="scroll"
    >
      <!-- Title Column -->
      <Column field="title" header="Titel" :sortable="true">
        <template #body="{ data }">
          <div class="title-cell">
            <i class="pi pi-video" style="color: #3b82f6; margin-right: 0.5rem;"></i>
            <span class="video-title">{{ data.title }}</span>
          </div>
        </template>
      </Column>

      <!-- Platforms Column -->
      <Column field="platforms" header="Plattformen">
        <template #body="{ data }">
          <div class="platform-tags">
            <Tag 
              v-for="platform in data.platforms" 
              :key="platform" 
              :value="getPlatformLabel(platform)"
              :style="{ 
                background: getPlatformColor(platform),
                color: 'white'
              }"
              class="platform-tag"
            >
              <i :class="getPlatformIcon(platform)" style="margin-right: 0.25rem;"></i>
              {{ getPlatformLabel(platform) }}
            </Tag>
          </div>
        </template>
      </Column>

      <!-- Status Column -->
      <Column field="status" header="Status" :sortable="true">
        <template #body="{ data }">
          <Tag 
            :value="getStatusLabel(data.status)" 
            :severity="getStatusSeverity(data.status)"
            :icon="getStatusIcon(data.status)"
          />
        </template>
      </Column>

      <!-- Date Column -->
      <Column field="createdAt" header="Erstellt" :sortable="true">
        <template #body="{ data }">
          <span class="date-text">{{ formatDate(data.createdAt) }}</span>
        </template>
      </Column>

      <!-- Views Column (optional) -->
      <Column field="views" header="Aufrufe" :sortable="true">
        <template #body="{ data }">
          <span class="views-text">{{ formatViews(data.views || 0) }}</span>
        </template>
      </Column>

      <!-- Actions Column -->
      <Column header="Aktionen" :exportable="false" style="width: 150px;">
        <template #body="{ data }">
          <div class="action-buttons">
            <Button 
              icon="pi pi-pencil" 
              class="p-button-text p-button-rounded p-button-info"
              v-tooltip.top="'Bearbeiten'"
              @click="handleEdit(data)"
            />
            <Button 
              icon="pi pi-trash" 
              class="p-button-text p-button-rounded p-button-danger"
              v-tooltip.top="'Löschen'"
              @click="confirmDelete(data)"
            />
            <Button 
              icon="pi pi-eye" 
              class="p-button-text p-button-rounded"
              v-tooltip.top="'Details'"
              @click="viewDetails(data)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Confirm Delete Dialog -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { useAuthStore } from '@/stores/authStore';
import { deleteVideo } from '@/services/api'; // ✅ Import hinzugefügt
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Button from 'primevue/button';
import ConfirmDialog from 'primevue/confirmdialog';

interface Video {
  id: string;
  title: string;
  platforms: string[];
  status: string;
  createdAt: string;
  views?: number;
}

const props = defineProps<{
  videos: Video[];
  limit?: number;
}>();

const emit = defineEmits<{
  edit: [video: Video];
  delete: [video: Video];
  view: [video: Video];
}>();

const confirm = useConfirm();
const toast = useToast();
const authStore = useAuthStore(); // ✅ Store initialisieren

const displayVideos = computed(() => 
  props.limit ? props.videos.slice(0, props.limit) : props.videos
);

// Platform Helpers
const getPlatformLabel = (platform: string): string => {
  const labels: Record<string, string> = {
    'youtube': 'YouTube',
    'tiktok': 'TikTok',
    'instagram': 'Instagram'
  };
  return labels[platform] || platform;
};

const getPlatformIcon = (platform: string): string => {
  const icons: Record<string, string> = {
    'youtube': 'pi pi-youtube',
    'tiktok': 'pi pi-video',
    'instagram': 'pi pi-instagram'
  };
  return icons[platform] || 'pi pi-globe';
};

const getPlatformColor = (platform: string): string => {
  const colors: Record<string, string> = {
    'youtube': '#FF0000',
    'tiktok': '#000000',
    'instagram': '#E4405F'
  };
  return colors[platform] || '#3b82f6';
};

// Status Helpers
const getStatusSeverity = (status: string): string => {
  const map: Record<string, string> = {
    'uploaded': 'success',
    'processing': 'info',
    'pending': 'warning',
    'partial': 'warning',
    'failed': 'danger'
  };
  return map[status] || 'info';
};

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    'uploaded': 'Hochgeladen',
    'processing': 'Wird verarbeitet',
    'pending': 'Ausstehend',
    'partial': 'Teilweise',
    'failed': 'Fehlgeschlagen'
  };
  return labels[status] || status;
};

const getStatusIcon = (status: string): string => {
  const icons: Record<string, string> = {
    'uploaded': 'pi pi-check-circle',
    'processing': 'pi pi-spin pi-spinner',
    'pending': 'pi pi-clock',
    'partial': 'pi pi-exclamation-triangle',
    'failed': 'pi pi-times-circle'
  };
  return icons[status] || 'pi pi-info-circle';
};

// Format Helpers
const formatDate = (date: string): string => {
  const d = new Date(date);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - d.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Heute';
  if (diffDays === 1) return 'Gestern';
  if (diffDays < 7) return `Vor ${diffDays} Tagen`;
  
  return d.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  });
};

const formatViews = (views: number): string => {
  if (views >= 1000000) {
    return (views / 1000000).toFixed(1) + 'M';
  }
  if (views >= 1000) {
    return (views / 1000).toFixed(1) + 'K';
  }
  return views.toString();
};

// Actions
const handleEdit = (video: Video) => {
  emit('edit', video);
};

const confirmDelete = (video: any) => {
  confirm.require({
    message: `Möchtest du das Video "${video.title}" wirklich löschen?`,
    header: 'Video löschen',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Ja, löschen',
    rejectLabel: 'Abbrechen',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        const userId = authStore.user?.id;
        if (!userId) {
          throw new Error('User nicht eingeloggt');
        }

        // ✅ Backend-Aufruf über gemeinsamen API-Client
        const result = await deleteVideo(video.id, userId);

        // Lokale Liste im Parent aktualisieren
        emit('delete', video);

        toast.add({
          severity: 'success',
          summary: 'Gelöscht',
          detail: result?.message || `Video "${video.title}" wurde gelöscht`,
          life: 3000,
        });
      } catch (err: any) {
        console.error('Delete error:', err);
        toast.add({
          severity: 'error',
          summary: 'Fehler',
          detail: err.message || 'Video konnte nicht gelöscht werden',
          life: 3000,
        });
      }
    },
  });
};


const viewDetails = (video: Video) => {
  emit('view', video);
};
</script>

<style scoped>
.video-list-container {
  width: 100%;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #64748b;
  margin: 0;
}

/* Title Cell */
.title-cell {
  display: flex;
  align-items: center;
}

.video-title {
  font-weight: 500;
  color: #1e293b;
}

/* Platform Tags */
.platform-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.platform-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

/* Date & Views */
.date-text,
.views-text {
  color: #64748b;
  font-size: 0.875rem;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 0.25rem;
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
}
</style>


