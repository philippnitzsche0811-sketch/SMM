<template>
  <div class="describe-step">
    <div class="field-group">
      <label>What is this video about?</label>
      <Textarea
        :modelValue="context"
        @update:modelValue="$emit('update:context', $event)"
        placeholder="Briefly describe what happens in the video — this gives the AI context to generate better titles, descriptions and tags. E.g. 'A 60-second product demo showing how to use our new coffee grinder.'"
        :rows="4"
        class="w-full"
      />
      <small class="field-hint">Optional — skipping this uses your title as context.</small>
    </div>

    <div class="ai-toggle-row">
      <div class="ai-toggle-info">
        <div class="ai-toggle-label">
          <i class="pi pi-sparkles"></i>
          AI Optimization
        </div>
        <p>Let Claude generate an optimized title, description and hashtags for each platform.</p>
      </div>
      <InputSwitch
        :modelValue="aiEnabled"
        @update:modelValue="$emit('update:aiEnabled', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import Textarea from 'primevue/textarea';
import InputSwitch from 'primevue/inputswitch';

defineProps<{
  context: string;
  aiEnabled: boolean;
}>();
defineEmits<{
  'update:context': [value: string];
  'update:aiEnabled': [value: boolean];
}>();
</script>

<style scoped>
.describe-step { display: flex; flex-direction: column; gap: 1.5rem; }

.field-group { display: flex; flex-direction: column; gap: 0.375rem; }
.field-group label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); }
.field-hint { font-size: 0.78rem; color: var(--text-disabled); }

.ai-toggle-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(79,127,255,0.05);
  border: 1px solid rgba(79,127,255,0.15);
  border-radius: 12px;
}

.ai-toggle-info { flex: 1; }

.ai-toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}
.ai-toggle-label i { color: #7da5ff; font-size: 1rem; }

.ai-toggle-info p { font-size: 0.825rem; color: var(--text-secondary); margin: 0; line-height: 1.4; }
</style>
