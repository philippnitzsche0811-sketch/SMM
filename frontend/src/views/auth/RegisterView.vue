<template>
  <div class="register-view">
    <Card class="register-card">
      <template #header>
        <div class="card-header">
          <h1>Account erstellen</h1>
          <p>Registriere dich</p>
        </div>
      </template>

      <template #content>
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-field">
            <label for="email">Email</label>
            <InputText
              id="email"
              v-model="email"
              type="email"
              placeholder="email@example.com"
            />
          </div>

          <div class="form-field">
            <label for="password">Passwort</label>
            <Password
              id="password"
              v-model="password"
              placeholder="Min. 8 Zeichen"
              toggleMask
            />
          </div>

          <div class="form-field">
            <label for="confirmPassword">Passwort bestätigen</label>
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
            label="Registrieren"
            icon="pi pi-user-plus"
            :loading="loading"
            class="p-button-lg w-full"
          />

          <Message v-if="successMessage" severity="success" :closable="false">
            {{ successMessage }}
          </Message>

          <Message v-if="errorMessage" severity="error" :closable="false">
            {{ errorMessage }}
          </Message>
        </form>

        <div class="login-section">
          <Divider />
          <p>Bereits registriert?</p>
          <Button
            label="Zum Login"
            icon="pi pi-sign-in"
            outlined
            class="w-full"
            @click="$router.push('/login')"
          />
        </div>
      </template>
    </Card>
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Divider from 'primevue/divider';
import Toast from 'primevue/toast';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

const handleRegister = async () => {
  successMessage.value = '';
  errorMessage.value = '';

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwörter stimmen nicht überein';
    return;
  }

  if (password.value.length < 8) {
    errorMessage.value = 'Passwort muss min. 8 Zeichen haben';
    return;
  }

  loading.value = true;

  try {
    await authStore.register(email.value, password.value);
    successMessage.value = 'Check deine Emails für den Verification Link!';
    toast.add({ severity: 'success', summary: 'Registrierung erfolgreich', life: 5000 });
    
    setTimeout(() => router.push('/login'), 3000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Registrierung fehlgeschlagen';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}
.register-card { width: 100%; max-width: 500px; }
.card-header { text-align: center; padding: 2rem 2rem 1rem; }
.card-header h1 { margin: 0 0 0.5rem 0; font-size: 2rem; color: #1e293b; }
.card-header p { margin: 0; color: #64748b; }
.register-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-field { display: flex; flex-direction: column; gap: 0.5rem; }
.form-field label { font-weight: 500; color: #1e293b; }
.w-full { width: 100%; }
.login-section { margin-top: 1.5rem; text-align: center; }
.login-section p { margin: 1rem 0; color: #64748b; font-size: 0.875rem; }
</style>

