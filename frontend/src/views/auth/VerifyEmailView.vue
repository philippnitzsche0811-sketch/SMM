<template>
  <div class="auth-page">
    <div class="auth-wrap">
      <div class="auth-card">
        <div v-if="verifying" class="state">
          <div class="state-icon spin"><i class="pi pi-spin pi-spinner"></i></div>
          <h2>Verifying your email…</h2>
          <p>Just a moment.</p>
        </div>

        <div v-else-if="success" class="state">
          <div class="state-icon success"><i class="pi pi-check-circle"></i></div>
          <h2>Email verified!</h2>
          <p>Your account is confirmed. You can now sign in.</p>
          <button class="submit-btn" @click="$router.push('/login')">
            <i class="pi pi-sign-in"></i> Go to Sign In
          </button>
        </div>

        <div v-else class="state">
          <div class="state-icon error"><i class="pi pi-times-circle"></i></div>
          <h2>Verification failed</h2>
          <p>{{ errorMessage || 'The link may have expired. Please request a new one.' }}</p>
          <button class="submit-btn outline" @click="$router.push('/login')">
            Back to Sign In
          </button>
        </div>
      </div>

      <LegalFooter dark />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import LegalFooter from '@/components/layout/LegalFooter.vue';

const route        = useRoute();
const verifying    = ref(true);
const success      = ref(false);
const errorMessage = ref('');

onMounted(async () => {
  const token = route.query.token as string;
  if (!token) {
    errorMessage.value = 'No token found in the link.';
    verifying.value = false;
    return;
  }
  try {
    await axios.post('/api/auth/verify-email', { token });
    success.value = true;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Verification failed';
  } finally {
    verifying.value = false;
  }
});
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
  padding: 2.5rem 2rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
  backdrop-filter: blur(8px);
}

.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
}

.state-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  margin-bottom: 0.25rem;
}
.state-icon.spin    { background: rgba(79,127,255,0.12); color: #4f7fff; }
.state-icon.success { background: rgba(16,185,129,0.12); color: #10b981; }
.state-icon.error   { background: rgba(239,68,68,0.12);  color: #ef4444; }

.state h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.375rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
  letter-spacing: -0.02em;
}

.state p {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

.submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 0.5rem;
  padding: 0.75rem 1.75rem;
  background: #4f7fff;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s, box-shadow 0.2s;
}
.submit-btn:hover {
  background: #3b6ee8;
  box-shadow: 0 0 18px rgba(79,127,255,0.35);
}
.submit-btn.outline {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.14);
  color: #cbd5e1;
}
.submit-btn.outline:hover {
  border-color: rgba(255,255,255,0.28);
  background: rgba(255,255,255,0.04);
  box-shadow: none;
}

:deep(.legal-footer) { background: transparent; border-top: none; padding: 1rem 0 0; }
:deep(.legal-footer a)       { color: #334155; }
:deep(.legal-footer a:hover) { color: #64748b; }
:deep(.legal-footer .dot)    { color: #1e293b; }
</style>
