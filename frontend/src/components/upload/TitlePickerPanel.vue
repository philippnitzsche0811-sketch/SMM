<template>
  <div class="title-picker">
    <div class="picker-header">
      <i class="pi pi-sparkles"></i>
      <span>Choose a title — or write your own below</span>
    </div>

    <div class="option-cards">
      <button
        v-for="(opt, idx) in displayOptions"
        :key="idx"
        class="title-card"
        :class="{ selected: selectedIdx === idx }"
        @click="selectOption(idx)"
      >
        <span class="title-badge" :class="badgeClass(idx)">{{ badgeLabel(idx) }}</span>
        <span class="title-text">{{ opt }}</span>
      </button>

      <!-- Write your own card -->
      <button
        class="title-card own-card"
        :class="{ selected: selectedIdx === -1 }"
        @click="selectOwn"
      >
        <span class="title-badge badge-own">Own</span>
        <span class="title-text muted">Write your own title below</span>
      </button>
    </div>

    <!-- Always-visible editable input -->
    <div class="title-input-wrap">
      <InputText
        ref="inputRef"
        :modelValue="modelValue"
        @update:modelValue="onInput"
        placeholder="Your video title…"
        class="w-full title-input"
        :maxlength="200"
      />
      <span class="char-count">{{ modelValue.length }}/200</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import InputText from 'primevue/inputtext';

const props = defineProps<{
  options: string[];
  modelValue: string;
}>();

const emit = defineEmits<{ 'update:modelValue': [value: string] }>();

const selectedIdx = ref<number | null>(null);
const inputRef = ref<any>(null);

const displayOptions = computed(() => props.options.slice(0, 3));

watch(() => props.options, () => {
  selectedIdx.value = null;
}, { deep: true });

function selectOption(idx: number) {
  selectedIdx.value = idx;
  emit('update:modelValue', props.options[idx] ?? '');
}

function selectOwn() {
  selectedIdx.value = -1;
  inputRef.value?.$el?.focus();
}

function onInput(val: string) {
  selectedIdx.value = -1;
  emit('update:modelValue', val);
}

const badgeLabels = ['Hook', 'SEO', 'Curiosity'];
const badgeClasses = ['badge-hook', 'badge-seo', 'badge-curiosity'];

const badgeLabel = (idx: number) => badgeLabels[idx] ?? `Option ${idx + 1}`;
const badgeClass = (idx: number) => badgeClasses[idx] ?? 'badge-hook';
</script>

<style scoped>
.title-picker { display: flex; flex-direction: column; gap: 0.875rem; }

.picker-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}
.picker-header i { color: #7da5ff; }

.option-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.625rem;
}

.title-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  transition: border-color 0.18s, background 0.18s, box-shadow 0.18s;
}
.title-card:hover {
  border-color: rgba(79,127,255,0.3);
  background: rgba(79,127,255,0.04);
}
.title-card.selected {
  border-color: rgba(79,127,255,0.55);
  background: rgba(79,127,255,0.08);
  box-shadow: 0 0 0 1px rgba(79,127,255,0.25);
}
.own-card { opacity: 0.7; }
.own-card:hover, .own-card.selected { opacity: 1; border-color: rgba(255,255,255,0.2); background: rgba(255,255,255,0.04); box-shadow: none; }

.title-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 99px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
.badge-hook      { background: rgba(239,68,68,0.15);  color: #f87171; }
.badge-seo       { background: rgba(16,185,129,0.15); color: #34d399; }
.badge-curiosity { background: rgba(139,92,246,0.15); color: #a78bfa; }
.badge-own       { background: rgba(255,255,255,0.08); color: var(--text-disabled); }

.title-text {
  font-size: 0.875rem;
  color: var(--text-primary);
  line-height: 1.45;
  word-break: break-word;
}
.title-text.muted { color: var(--text-disabled); font-style: italic; }

.title-input-wrap {
  position: relative;
}
.title-input { padding-right: 3.5rem !important; }
.char-count {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.72rem;
  color: var(--text-disabled);
  pointer-events: none;
}

@media (max-width: 640px) {
  .option-cards { grid-template-columns: 1fr; }
}
</style>
