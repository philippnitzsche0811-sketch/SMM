<template>
  <div class="verify-view">
    <Card class="verify-card">
      <template #content>
        <div v-if="verifying" class="state">
          <i class="pi pi-spin pi-spinner" style="font-size: 3rem; color: #667eea;"></i>
          <h2>Verifiziere Email...</h2>
        </div>

        <div v-else-if="success" class="state success">
          <i class="pi pi-check-circle" style="font-size: 4rem; color: #10b981;"></i>
          <h2>Email verifiziert! 🎉</h2>
          <p>Du kannst dich jetzt anmelden.</p>
          <Button label="Zum Login" icon="pi pi-sign-in" @click="$router.push('/login')" />
        </div>

        <div v-else class="state error">
          <i class="pi pi-times-circle" style="font-size: 4rem; color: #ef4444;"></i>
          <h2>Verification fehlgeschlagen</h2>
          <p>{{ errorMessage }}</p>
          <Button label="Zum Login" outlined @click="$router.push('/login')" />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Card from 'primevue/card';
import Button from 'primevue/button';
import axios from 'axios';

const route = useRoute();
const router = useRouter();

const verifying = ref(true);
const success = ref(false);
const errorMessage = ref('');

onMounted(async () => {
  const token = route.query.token as string;

  if (!token) {
    errorMessage.value = 'Kein Token gefunden';
    verifying.value = false;
    return;
  }

  try {
    await axios.post('/api/auth/verify-email', { token });
    success.value = true;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Verification fehlgeschlagen';
  } finally {
    verifying.value = false;
  }
});
</script>

<style scoped>
.verify-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}
.verify-card { width: 100%; max-width: 500px; }
.state { display: flex; flex-direction: column; align-items: center; gap: 1.5rem; text-align: center; padding: 2rem; }
.state h2 { margin: 0; font-size: 1.75rem; color: #1e293b; }
.state p { margin: 0; color: #64748b; }
</style>

