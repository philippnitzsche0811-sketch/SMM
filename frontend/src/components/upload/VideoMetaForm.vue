<template>
  <div class="video-meta-form">
    <h3>Video-Details</h3>
    
    <div class="field">
      <label for="title">Titel *</label>
      <InputText 
        id="title" 
        v-model="localTitle" 
        placeholder="Gib einen Titel ein..."
        :class="{ 'p-invalid': !localTitle }"
      />
    </div>
    
    <div class="field">
      <label for="description">Beschreibung</label>
      <Textarea 
        id="description"
        v-model="localDescription"
        rows="5"
        placeholder="Beschreibe dein Video..."
      />
    </div>
    
    <div class="field">
      <label for="tags">Tags (komma-getrennt)</label>
      <Chips v-model="localTags" separator="," />
    </div>
    
    <div class="field">
      <label for="privacy">Sichtbarkeit</label>
      <Dropdown 
        id="privacy"
        v-model="localPrivacyStatus"
        :options="privacyOptions"
        optionLabel="label"
        optionValue="value"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Chips from 'primevue/chips';
import Dropdown from 'primevue/dropdown';

const props = defineProps<{
  title: string;
  description: string;
  tags: string[];
  privacyStatus: string;
}>();

const emit = defineEmits<{
  'update:title': [value: string];
  'update:description': [value: string];
  'update:tags': [value: string[]];
  'update:privacyStatus': [value: string];
}>();

const localTitle = ref(props.title);
const localDescription = ref(props.description);
const localTags = ref(props.tags);
const localPrivacyStatus = ref(props.privacyStatus);

const privacyOptions = [
  { label: 'Privat', value: 'private' },
  { label: 'Öffentlich', value: 'public' },
  { label: 'Nicht gelistet', value: 'unlisted' }
];

watch(localTitle, (val) => emit('update:title', val));
watch(localDescription, (val) => emit('update:description', val));
watch(localTags, (val) => emit('update:tags', val));
watch(localPrivacyStatus, (val) => emit('update:privacyStatus', val));
</script>

<style scoped>
.field {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}
</style>
