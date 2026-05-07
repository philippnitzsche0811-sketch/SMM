<template>
  <div class="login-page">
    <div class="login-wrap">

      <!-- Card -->
      <div class="login-card">
        <div class="login-header">
          <img :src="logoUrl" alt="Decodu-SMM" class="login-logo" />
          <h1>Decodu-SMM</h1>
          <p>Sign in to your account</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-field">
            <label for="email">Email</label>
            <InputText
              id="email"
              v-model="email"
              type="email"
              placeholder="you@example.com"
              :class="{ 'p-invalid': errors.email }"
              class="w-full"
            />
            <small v-if="errors.email" class="field-error">{{ errors.email }}</small>
          </div>

          <div class="form-field">
            <label for="password">Password</label>
            <Password
              id="password"
              v-model="password"
              placeholder="Your password"
              :feedback="false"
              toggleMask
              hideIcon="pi pi-eye"
              showIcon="pi pi-eye-slash"
              class="w-full"
              inputClass="w-full"
            />
            <div class="forgot-row">
              <router-link to="/forgot-password" class="forgot-link">Forgot password?</router-link>
            </div>
          </div>

          <Button
            type="submit"
            label="Sign in"
            icon="pi pi-sign-in"
            :loading="loading"
            class="w-full submit-btn"
          />

          <Message v-if="errorMessage" severity="error" :closable="false" class="error-msg">
            {{ errorMessage }}
          </Message>
        </form>

        <div class="divider-row">
          <span>Don't have an account?</span>
          <router-link to="/register" class="register-link">Create one</router-link>
        </div>
      </div>

      <!-- Legal links below the card -->
      <LegalFooter dark />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import LegalFooter from '@/components/layout/LegalFooter.vue';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Toast from 'primevue/toast';
import logoUrl from '@/assets/images/logo.png';

const router    = useRouter();
const authStore = useAuthStore();
const toast     = useToast();

const email        = ref('');
const password     = ref('');
const loading      = ref(false);
const errorMessage = ref('');
const errors       = ref<{ email?: string }>({});

const handleLogin = async () => {
  errors.value       = {};
  errorMessage.value = '';

  if (!email.value) {
    errors.value.email = 'Email is required';
    return;
  }

  loading.value = true;
  try {
    await authStore.login(email.value, password.value);
    await new Promise(resolve => setTimeout(resolve, 100));
    await router.push('/dashboard');
  } catch (err: any) {
    const status = err.response?.status;
    const detail = err.response?.data?.detail;

    if (status === 401)      errorMessage.value = 'Invalid email or password';
    else if (status === 403) errorMessage.value = detail || 'Email not verified';
    else                     errorMessage.value = detail || 'Login failed';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #0b0b0f;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.login-wrap {
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0;
}

.login-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 2.25rem 2rem 2rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
  backdrop-filter: blur(8px);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-logo {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  object-fit: contain;
  margin-bottom: 1rem;
}

.login-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.25rem;
  letter-spacing: -0.02em;
}

.login-header p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-field label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #94a3b8;
}

.forgot-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.25rem;
}

.forgot-link {
  font-size: 0.8125rem;
  color: #4f7fff;
  text-decoration: none;
}
.forgot-link:hover { text-decoration: underline; }

.field-error {
  color: #f87171;
  font-size: 0.78rem;
}

.submit-btn {
  background: #4f7fff !important;
  border-color: #4f7fff !important;
  color: #fff !important;
  font-weight: 600 !important;
  height: 2.75rem;
  transition: background 0.2s, box-shadow 0.2s !important;
}
.submit-btn:hover:not(:disabled) {
  background: #3b6ee8 !important;
  border-color: #3b6ee8 !important;
  box-shadow: 0 0 18px rgba(79,127,255,0.35) !important;
}

.error-msg { margin-top: 0.25rem; }

.divider-row {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-size: 0.875rem;
  color: #64748b;
}

.register-link {
  color: #4f7fff;
  font-weight: 500;
  text-decoration: none;
}
.register-link:hover { text-decoration: underline; }

.w-full { width: 100%; }

:deep(.legal-footer) {
  background: transparent;
  border-top: none;
  padding: 1rem 0 0;
}
:deep(.legal-footer a)       { color: #334155; }
:deep(.legal-footer a:hover) { color: #64748b; }
:deep(.legal-footer .dot)    { color: #1e293b; }
</style>
