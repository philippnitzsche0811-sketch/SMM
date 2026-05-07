<template>
  <div class="describe-step">
    <div class="field-group">
      <label>What is this video about?</label>
      <Textarea
        :modelValue="context"
        @update:modelValue="$emit('update:context', $event)"
        placeholder="Briefly describe what happens in the video — gives the AI context to generate better titles, descriptions and tags. E.g. 'A 60-second product demo showing how to use our new coffee grinder.'"
        :rows="4"
        class="w-full"
      />
      <small class="field-hint">Optional — skipping this uses your title as context.</small>
    </div>
  </div>
</template>

<script setup lang="ts">
import Textarea from 'primevue/textarea';

defineProps<{ context: string }>();
defineEmits<{ 'update:context': [value: string] }>();
</script>

<style scoped>
.describe-step { display: flex; flex-direction: column; gap: 1rem; }
.field-group { display: flex; flex-direction: column; gap: 0.375rem; }
.field-group label { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); }
.field-hint { font-size: 0.78rem; color: var(--text-disabled); }
</style>
