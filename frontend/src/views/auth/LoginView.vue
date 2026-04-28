<template>
  <div class="login-page">
    <div class="login-wrap">

      <!-- Card -->
      <div class="login-card">
        <div class="login-header">
          <img :src="logoUrl" alt="SocialHub" class="login-logo" />
          <h1>SocialHub</h1>
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
              maskIcon="pi pi-eye-slash"
              unmaskIcon="pi pi-eye"
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
  background: #f8fafc;
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
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 2.25rem 2rem 2rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
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
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
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
  color: #374151;
}

.forgot-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.25rem;
}

.forgot-link {
  font-size: 0.8125rem;
  color: #6366f1;
  text-decoration: none;
}
.forgot-link:hover { text-decoration: underline; }

.field-error {
  color: #dc2626;
  font-size: 0.78rem;
}

.submit-btn {
  background: #0f172a !important;
  border-color: #0f172a !important;
  color: #fff !important;
  font-weight: 600 !important;
  height: 2.75rem;
}
.submit-btn:hover:not(:disabled) {
  background: #1e293b !important;
  border-color: #1e293b !important;
}

.error-msg { margin-top: 0.25rem; }

.divider-row {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-size: 0.875rem;
  color: #64748b;
}

.register-link {
  color: #6366f1;
  font-weight: 500;
  text-decoration: none;
}
.register-link:hover { text-decoration: underline; }

.w-full { width: 100%; }

/* Legal footer sits flush below the card with no gap */
:deep(.legal-footer) {
  background: transparent;
  border-top: none;
  padding: 1rem 0 0;
}

:deep(.legal-footer a)       { color: #94a3b8; }
:deep(.legal-footer a:hover) { color: #475569; }
:deep(.legal-footer .dot)    { color: #cbd5e1; }

:deep(.p-password) { width: 100%; position: relative; }
:deep(.p-password input) { width: 100%; padding-right: 2.5rem; }
:deep(.p-password-toggle-mask-icon) {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #94a3b8;
}
</style>
