<template>
  <div class="reset-view">
    <Card class="reset-card">
      <template #header>
        <div class="card-header">
          <h2>🔒 Neues Passwort</h2>
        </div>
      </template>

      <template #content>
        <form @submit.prevent="handleSubmit" class="reset-form">
          <div class="form-field">
            <label for="password">Neues Passwort</label>
            <Password
              id="password"
              v-model="password"
              placeholder="Min. 8 Zeichen"
              toggleMask
            />
          </div>

          <div class="form-field">
            <label for="confirmPassword">Bestätigen</label>
            <Password
              id="confirmPassword"
              v-model="confirmPassword"
              placeholder="Passwort wiederholen"
              :feedback="false"
              toggleMask
            />
          </div>

          <Button
            type="submit"
            label="Passwort zurücksetzen"
            icon="pi pi-check"
            :loading="loading"
            class="p-button-lg w-full"
          />
        </form>
      </template>
    </Card>
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Toast from 'primevue/toast';

import { resetPassword } from '@/services/api';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const token = ref('');

onMounted(() => {
  token.value = route.query.token as string;
  if (!token.value) {
    toast.add({ severity: 'error', summary: 'Ungültiger Link', life: 3000 });
    router.push('/login');
  }
});

const handleSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    toast.add({
      severity: 'error',
      summary: 'Passwörter stimmen nicht überein',
      life: 3000,
    });
    return;
  }

  if (password.value.length < 8) {
    toast.add({
      severity: 'error',
      summary: 'Min. 8 Zeichen',
      life: 3000,
    });
    return;
  }

  loading.value = true;

  try {
    await resetPassword(token.value, password.value);

    toast.add({
      severity: 'success',
      summary: 'Passwort zurückgesetzt',
      life: 5000,
    });
    setTimeout(() => router.push('/login'), 2000);
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Reset fehlgeschlagen',
      life: 3000,
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.reset-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 2rem;
}
.reset-card { width: 100%; max-width: 450px; }
.card-header { text-align: center; padding: 2rem 2rem 1rem; }
.card-header h2 { margin: 0; font-size: 1.75rem; color: #1e293b; }
.reset-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-field { display: flex; flex-direction: column; gap: 0.5rem; }
.form-field label { font-weight: 500; color: #1e293b; }
.w-full { width: 100%; }
</style>


