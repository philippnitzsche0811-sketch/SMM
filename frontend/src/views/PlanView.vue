<template>
  <div class="plan-view">
    <!-- Tab-Navigation -->
    <div class="plan-tabs">
      <button
        class="plan-tab"
        :class="{ active: activeTab === 'ideas' }"
        @click="activeTab = 'ideas'"
      >
        <i class="pi pi-lightbulb"></i>
        Ideen Board
      </button>
      <button
        class="plan-tab"
        :class="{ active: activeTab === 'calendar' }"
        @click="activeTab = 'calendar'"
      >
        <i class="pi pi-calendar"></i>
        Kalender
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <IdeasView v-if="activeTab === 'ideas'" />
      <CalendarView v-if="activeTab === 'calendar'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import IdeasView from './IdeasView.vue';
import CalendarView from './CalendarView.vue';

const route = useRoute();
const activeTab = ref<'ideas' | 'calendar'>(
  route.query.tab === 'calendar' ? 'calendar' : 'ideas'
);
</script>

<style scoped>
.plan-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.plan-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 1rem 2rem 0;
  border-bottom: 1px solid var(--border-color, #3f3f46);
  background: var(--surface-ground, #18181b);
  flex-shrink: 0;
}

.plan-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.625rem 1rem;
  border: none;
  background: none;
  color: var(--text-secondary, #a1a1aa);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  border-radius: 0;
  transition: color 0.15s, border-color 0.15s;
}

.plan-tab:hover {
  color: var(--text-primary, #f4f4f5);
}

.plan-tab.active {
  color: var(--primary-400, #a78bfa);
  border-bottom-color: var(--primary-400, #a78bfa);
}

.tab-content {
  flex: 1;
  overflow-y: auto;
}
</style>
