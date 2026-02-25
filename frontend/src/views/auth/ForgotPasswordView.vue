<template>
  <div class="forgot-view">
    <Card class="forgot-card">
      <template #header>
        <div class="card-header">
          <h2>🔑 Passwort vergessen?</h2>
          <p>Email eingeben für Reset Link</p>
        </div>
      </template>

      <template #content>
        <form @submit.prevent="handleSubmit" class="forgot-form">
          <div class="form-field">
            <label for="email">Email</label>
            <InputText
              id="email"
              v-model="email"
              type="email"
              placeholder="email@example.com"
            />
          </div>

          <Button
            type="submit"
            label="Reset Link senden"
            icon="pi pi-send"
            :loading="loading"
            class="p-button-lg w-full"
          />
        </form>

        <div class="form-footer">
          <router-link to="/login" class="back-link">
            <i class="pi pi-arrow-left"></i> Zurück zum Login
          </router-link>
        </div>
      </template>
    </Card>
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Toast from 'primevue/toast';

import { forgotPassword } from '@/services/api';

const router = useRouter();
const toast = useToast();

const email = ref('');
const loading = ref(false);

const handleSubmit = async () => {
  loading.value = true;

  try {
    await forgotPassword(email.value);
    toast.add({
      severity: 'success',
      summary: 'Email gesendet',
      detail: 'Check deine Emails',
      life: 5000,
    });
    setTimeout(() => router.push('/login'), 2000);
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      life: 3000,
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.forgot-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 2rem;
}
.forgot-card { width: 100%; max-width: 450px; }
.card-header { text-align: center; padding: 2rem 2rem 1rem; }
.card-header h2 { margin: 0 0 0.5rem 0; font-size: 1.75rem; color: #1e293b; }
.card-header p { margin: 0; color: #64748b; }
.forgot-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-field { display: flex; flex-direction: column; gap: 0.5rem; }
.form-field label { font-weight: 500; color: #1e293b; }
.w-full { width: 100%; }
.form-footer { text-align: center; margin-top: 1.5rem; }
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #667eea;
  text-decoration: none;
}
.back-link:hover { text-decoration: underline; }
</style>
