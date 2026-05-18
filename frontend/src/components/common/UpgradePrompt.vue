<template>
  <div class="upgrade-prompt">
    <div class="upgrade-icon">
      <i class="pi pi-star-fill"></i>
    </div>
    <div class="upgrade-content">
      <p class="upgrade-title">{{ title }}</p>
      <p class="upgrade-text">{{ description }}</p>
    </div>
    <button class="upgrade-btn" @click="$emit('upgrade')">
      Pro freischalten
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  description?: string;
}>();

defineEmits<{ upgrade: [] }>();
</script>

<style scoped>
.upgrade-prompt {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.875rem 1rem;
  background: linear-gradient(135deg, rgba(79,127,255,0.08), rgba(139,92,246,0.08));
  border: 1px solid rgba(79,127,255,0.25);
  border-radius: 10px;
}

.upgrade-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4f7fff, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
  font-size: 0.875rem;
}

.upgrade-content {
  flex: 1;
  min-width: 0;
}

.upgrade-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.125rem;
}

.upgrade-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0;
}

.upgrade-btn {
  flex-shrink: 0;
  padding: 0.4rem 0.875rem;
  background: linear-gradient(135deg, #4f7fff, #8b5cf6);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.upgrade-btn:hover { opacity: 0.85; }
</style>
