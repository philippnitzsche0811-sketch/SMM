<template>
  <div class="auth-page">
    <div class="auth-wrap">
      <div class="auth-card">
        <div class="auth-header">
          <div class="auth-icon-wrap">
            <i class="pi pi-lock"></i>
          </div>
          <h1>Set new password</h1>
          <p>Choose a strong password for your account.</p>
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-field">
            <label for="password">New password</label>
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
            label="Reset password"
            icon="pi pi-check"
            :loading="loading"
            class="w-full submit-btn"
          />
        </form>

        <div class="divider-row">
          <router-link to="/login" class="back-link">
            <i class="pi pi-arrow-left"></i> Back to Sign In
          </router-link>
        </div>
      </div>

      <LegalFooter dark />
    </div>
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Toast from 'primevue/toast';
import LegalFooter from '@/components/layout/LegalFooter.vue';
import { resetPassword } from '@/services/api';

const route  = useRoute();
const router = useRouter();
const toast  = useToast();

const password        = ref('');
const confirmPassword = ref('');
const loading         = ref(false);
const token           = ref('');

onMounted(() => {
  token.value = route.query.token as string;
  if (!token.value) {
    toast.add({ severity: 'error', summary: 'Invalid link', life: 3000 });
    router.push('/login');
  }
});

const handleSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    toast.add({ severity: 'error', summary: 'Passwords do not match', life: 3000 });
    return;
  }
  if (password.value.length < 8) {
    toast.add({ severity: 'error', summary: 'Minimum 8 characters', life: 3000 });
    return;
  }
  loading.value = true;
  try {
    await resetPassword(token.value, password.value);
    toast.add({ severity: 'success', summary: 'Password reset', detail: 'You can now sign in', life: 5000 });
    setTimeout(() => router.push('/login'), 2000);
  } catch {
    toast.add({ severity: 'error', summary: 'Reset failed', detail: 'The link may have expired', life: 3000 });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: #0b0b0f;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.auth-wrap {
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.auth-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 2.25rem 2rem 2rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
  backdrop-filter: blur(8px);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(79,127,255,0.12);
  border: 1px solid rgba(79,127,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  font-size: 1.375rem;
  color: #4f7fff;
}

.auth-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.375rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.25rem;
  letter-spacing: -0.02em;
}

.auth-header p { color: #64748b; font-size: 0.875rem; margin: 0; }

.auth-form { display: flex; flex-direction: column; gap: 1.25rem; }

.form-field { display: flex; flex-direction: column; gap: 0.375rem; }
.form-field label { font-size: 0.875rem; font-weight: 500; color: #94a3b8; }

.submit-btn {
  background: #4f7fff !important;
  border-color: #4f7fff !important;
  color: #fff !important;
  font-weight: 600 !important;
  height: 2.75rem;
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
  justify-content: center;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.875rem;
  color: #64748b;
  text-decoration: none;
  transition: color 0.2s;
}
.back-link:hover { color: #4f7fff; }

.w-full { width: 100%; }

:deep(.legal-footer) { background: transparent; border-top: none; padding: 1rem 0 0; }
:deep(.legal-footer a)       { color: #334155; }
:deep(.legal-footer a:hover) { color: #64748b; }
:deep(.legal-footer .dot)    { color: #1e293b; }
</style>
