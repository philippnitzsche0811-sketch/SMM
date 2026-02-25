<template>
  <div class="login-view">
    <Card class="login-card">
      <template #header>
        <div class="card-header">
          <div class="logo">
            <i class="pi pi-video" style="font-size: 3rem; color: #667eea;"></i>
          </div>
          <h1>Social Media Manager</h1>
          <p>Melde dich an</p>
        </div>
      </template>

      <template #content>
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-field">
            <label for="email">Email</label>
            <InputText
              id="email"
              v-model="email"
              type="email"
              placeholder="email@example.com"
              :class="{ 'p-invalid': errors.email }"
            />
            <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
          </div>

          <div class="form-field">
            <label for="password">Passwort</label>
            <Password
              id="password"
              v-model="password"
              placeholder="Passwort"
              :feedback="false"
              toggleMask
            />
          </div>

          <div class="form-footer-links">
            <router-link to="/forgot-password" class="forgot-link">
              Passwort vergessen?
            </router-link>
          </div>

          <Button
            type="submit"
            label="Anmelden"
            icon="pi pi-sign-in"
            :loading="loading"
            class="p-button-lg w-full"
          />

          <Message v-if="errorMessage" severity="error" :closable="false">
            {{ errorMessage }}
          </Message>
        </form>

        <div class="register-section">
          <Divider />
          <p>Noch kein Account?</p>
          <Button
            label="Registrieren"
            icon="pi pi-user-plus"
            outlined
            class="w-full"
            @click="$router.push('/register')"
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
const loading = ref(false);
const errorMessage = ref('');
const errors = ref<{ email?: string }>({});

const handleLogin = async () => {
  errors.value = {};
  errorMessage.value = '';
  
  if (!email.value) {
    errors.value.email = 'Email erforderlich';
    return;
  }

  loading.value = true;

  try {
    console.log('🔐 Attempting login...', email.value)
    
    await authStore.login(email.value, password.value);
    
    console.log('✅ Login successful')
    console.log('Token:', authStore.token?.substring(0, 20) + '...')
    console.log('User:', authStore.user)
    console.log('isAuthenticated:', authStore.isAuthenticated)
    
    toast.add({ 
      severity: 'success', 
      summary: 'Login erfolgreich', 
      life: 3000 
    });
    
    console.log('🚀 Redirecting to /dashboard...')
    
    // ✅ Small delay to ensure state is updated
    await new Promise(resolve => setTimeout(resolve, 100))
    
    await router.push('/dashboard');
    
    console.log('✅ Redirect complete')
    
  } catch (err: any) {
    console.error('❌ Login failed:', err)
    const status = err.response?.status;
    const detail = err.response?.data?.detail;

    if (status === 401) {
      errorMessage.value = 'Ungültige Email oder Passwort';
    } else if (status === 403) {
      errorMessage.value = detail || 'Email nicht verifiziert';
    } else {
      errorMessage.value = detail || 'Login fehlgeschlagen';
    }
  } finally {
    loading.value = false;
  }
};

</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}
.login-card { width: 100%; max-width: 450px; }
.card-header { text-align: center; padding: 2rem 2rem 1rem; }
.logo { margin-bottom: 1rem; }
.card-header h1 { margin: 0 0 0.5rem 0; font-size: 2rem; color: #1e293b; }
.card-header p { margin: 0; color: #64748b; }
.login-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-field { display: flex; flex-direction: column; gap: 0.5rem; }
.form-field label { font-weight: 500; color: #1e293b; }
.form-footer-links { display: flex; justify-content: flex-end; margin-top: -0.5rem; }
.forgot-link { color: #667eea; text-decoration: none; font-size: 0.875rem; }
.forgot-link:hover { text-decoration: underline; }
.w-full { width: 100%; }
.register-section { margin-top: 1.5rem; text-align: center; }
.register-section p { margin: 1rem 0; color: #64748b; font-size: 0.875rem; }
</style>



