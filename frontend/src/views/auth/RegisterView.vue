<template>
  <div class="login-page">
    <div class="login-wrap">

      <div class="login-card">
        <div class="login-header">
          <img :src="logoUrl" alt="Decodu-SMM" class="login-logo" />
          <h1>Decodu-SMM</h1>
          <p>Create your free account</p>
        </div>

        <form @submit.prevent="handleRegister" class="login-form">
          <div class="form-field">
            <label for="email">Email</label>
            <InputText
              id="email"
              v-model="email"
              type="email"
              placeholder="you@example.com"
              class="w-full"
            />
          </div>

          <div class="form-field">
            <label for="password">Password</label>
            <Password
              id="password"
              v-model="password"
              placeholder="Min. 8 characters"
              toggleMask
              hideIcon="pi pi-eye"
              showIcon="pi pi-eye-slash"
              class="w-full"
              inputClass="w-full"
            />
          </div>

          <div class="form-field">
            <label for="confirmPassword">Confirm password</label>
            <Password
              id="confirmPassword"
              v-model="confirmPassword"
              placeholder="Repeat password"
              :feedback="false"
              toggleMask
              hideIcon="pi pi-eye"
              showIcon="pi pi-eye-slash"
              class="w-full"
              inputClass="w-full"
            />
          </div>

          <Button
            type="submit"
            label="Create account"
            icon="pi pi-user-plus"
            :loading="loading"
            class="w-full submit-btn"
          />

          <Message v-if="successMessage" severity="success" :closable="false">
            {{ successMessage }}
          </Message>
          <Message v-if="errorMessage" severity="error" :closable="false">
            {{ errorMessage }}
          </Message>
        </form>

        <div class="divider-row">
          <span>Already have an account?</span>
          <router-link to="/login" class="register-link">Sign in</router-link>
        </div>
      </div>

      <LegalFooter dark />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import LegalFooter from '@/components/layout/LegalFooter.vue';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Toast from 'primevue/toast';
import logoUrl from '@/assets/images/logo.png';

const router    = useRouter();
const authStore = useAuthStore();
const toast     = useToast();

const email           = ref('');
const password        = ref('');
const confirmPassword = ref('');
const loading         = ref(false);
const successMessage  = ref('');
const errorMessage    = ref('');

const handleRegister = async () => {
  successMessage.value = '';
  errorMessage.value   = '';

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match';
    return;
  }

  if (password.value.length < 8) {
    errorMessage.value = 'Password must be at least 8 characters';
    return;
  }

  loading.value = true;
  try {
    await authStore.register(email.value, password.value);
    successMessage.value = 'Check your email for the verification link!';
    toast.add({ severity: 'success', summary: 'Registration successful', life: 5000 });
    setTimeout(() => router.push('/login'), 3000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Registration failed';
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
