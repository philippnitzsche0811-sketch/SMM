<template>
  <Card class="dashboard-card">
    <template #content>
      <div class="card-content">
        <div class="card-icon" :style="{ background: iconBackground }">
          <i :class="icon" :style="{ color: color }"></i>
        </div>
        <div class="card-info">
          <span class="card-value">{{ formattedValue }}</span>
          <span class="card-title">{{ title }}</span>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Card from 'primevue/card';

interface Props {
  title: string;
  value: number | string;
  icon: string;
  color: string;
}

const props = defineProps<Props>();

const iconBackground = computed(() => {
  // Lighter version of the color for background
  return `${props.color}15`;
});

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    // Format large numbers
    if (props.value >= 1000000) {
      return (props.value / 1000000).toFixed(1) + 'M';
    }
    if (props.value >= 1000) {
      return (props.value / 1000).toFixed(1) + 'K';
    }
    return props.value.toString();
  }
  return props.value;
});
</script>

<style scoped>
.dashboard-card {
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.5rem;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  flex-shrink: 0;
}

.card-icon i {
  font-size: 2rem;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.card-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.card-title {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Responsive */
@media (max-width: 768px) {
  .card-content {
    flex-direction: column;
    text-align: center;
  }

  .card-value {
    font-size: 1.75rem;
  }
}
</style>
