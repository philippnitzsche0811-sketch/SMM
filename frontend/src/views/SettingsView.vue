<template>
  <div class="settings-view">
    <div class="page-header">
      <h1>Settings</h1>
      <p class="subtitle">Manage your profile and account preferences</p>
    </div>

    <div class="settings-grid">
      <!-- Profile -->
      <div class="settings-card">
        <h3 class="settings-card-title"><i class="pi pi-user"></i> Profile</h3>
        <div class="form-field">
          <span class="form-label">Username</span>
          <InputText v-model="profile.username" placeholder="Username" class="w-full" />
        </div>
        <div class="form-field">
          <span class="form-label">Email</span>
          <InputText :value="authStore.userEmail || ''" disabled class="w-full" />
          <small class="field-hint">Email address cannot be changed</small>
        </div>
        <div class="card-footer">
          <Button label="Save changes" icon="pi pi-check" :loading="savingProfile" @click="saveProfile" />
        </div>
      </div>

      <!-- Change Password -->
      <div class="settings-card">
        <h3 class="settings-card-title"><i class="pi pi-lock"></i> Change Password</h3>
        <div class="form-field">
          <span class="form-label">Current Password</span>
          <Password v-model="passwords.current" :feedback="false" toggleMask hideIcon="pi pi-eye" showIcon="pi pi-eye-slash" class="w-full" inputClass="w-full" />
        </div>
        <div class="form-field">
          <span class="form-label">New Password</span>
          <Password v-model="passwords.new" toggleMask hideIcon="pi pi-eye" showIcon="pi pi-eye-slash" class="w-full" inputClass="w-full" />
        </div>
        <div class="form-field">
          <span class="form-label">Confirm New Password</span>
          <Password v-model="passwords.confirm" :feedback="false" toggleMask hideIcon="pi pi-eye" showIcon="pi pi-eye-slash" class="w-full" inputClass="w-full" />
          <small v-if="passwordMismatch" class="field-error">Passwords do not match</small>
        </div>
        <div class="card-footer">
          <Button label="Update Password" icon="pi pi-lock" :loading="savingPassword" :disabled="!canChangePassword" @click="changePassword" />
        </div>
      </div>

      <!-- Account Info -->
      <div class="settings-card info-card">
        <h3 class="settings-card-title"><i class="pi pi-info-circle"></i> Account Info</h3>
        <div class="info-row">
          <span class="info-label">Account ID</span>
          <span class="info-value mono">{{ authStore.userId }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Email verified</span>
          <Tag
            :value="authStore.isVerified ? 'Verified' : 'Not verified'"
            :severity="authStore.isVerified ? 'success' : 'warn'"
          />
        </div>
        <div class="info-row">
          <span class="info-label">Connected platforms</span>
          <span class="info-value">{{ authStore.user?.connectedPlatforms?.length || 0 }}</span>
        </div>
      </div>

      <!-- Legal Links -->
      <div class="settings-card">
        <h3 class="settings-card-title"><i class="pi pi-file"></i> Legal</h3>
        <div class="legal-links">
          <a href="/terms" target="_blank" class="legal-link">
            <i class="pi pi-file-edit"></i>
            <span>Terms of Service</span>
            <i class="pi pi-external-link ml-auto"></i>
          </a>
          <a href="/privacy" target="_blank" class="legal-link">
            <i class="pi pi-shield"></i>
            <span>Privacy Policy</span>
            <i class="pi pi-external-link ml-auto"></i>
          </a>
        </div>
      </div>

      <!-- Data Deletion -->
      <div class="settings-card data-card">
        <h3 class="settings-card-title"><i class="pi pi-database"></i> Your Data</h3>
        <p class="data-text">You have the right to delete all your stored data, including:</p>
        <div class="data-list">
          <div class="data-list-item"><i class="pi pi-check-circle"></i> Your profile and email address</div>
          <div class="data-list-item"><i class="pi pi-check-circle"></i> All connected social media platforms</div>
          <div class="data-list-item"><i class="pi pi-check-circle"></i> Your uploaded videos and metadata</div>
          <div class="data-list-item"><i class="pi pi-check-circle"></i> All stored access tokens</div>
        </div>
        <p class="data-text">
          To request data deletion, click <strong>"Delete Account"</strong> below, or contact us at
          <a href="mailto:support@decodu-smm.com" class="data-email">support@decodu-smm.com</a>
        </p>
      </div>

      <!-- Danger Zone -->
      <div class="settings-card danger-card">
        <h3 class="settings-card-title danger"><i class="pi pi-exclamation-triangle"></i> Danger Zone</h3>
        <p class="danger-text">This action is permanent and cannot be undone.</p>
        <Button label="Delete Account" icon="pi pi-trash" class="p-button-danger p-button-outlined" @click="confirmDeleteAccount" />
      </div>
    </div>

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Tag from 'primevue/tag';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import api from '@/services/api';

const authStore = useAuthStore();
const toast     = useToast();
const confirm   = useConfirm();
const router    = useRouter();

const savingProfile  = ref(false);
const savingPassword = ref(false);

const profile   = ref({ username: authStore.userName || '' });
const passwords = ref({ current: '', new: '', confirm: '' });

const passwordMismatch = computed(() =>
  passwords.value.new && passwords.value.confirm && passwords.value.new !== passwords.value.confirm
);

const canChangePassword = computed(() =>
  passwords.value.current && passwords.value.new && passwords.value.confirm && !passwordMismatch.value
);

const saveProfile = async () => {
  savingProfile.value = true;
  try {
    await api.patch('/api/auth/me', { username: profile.value.username });
    if (authStore.user) {
      authStore.user.username = profile.value.username;
      localStorage.setItem('user', JSON.stringify(authStore.user));
    }
    toast.add({ severity: 'success', summary: 'Saved', detail: 'Profile updated', life: 3000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Save failed', life: 5000 });
  } finally { savingProfile.value = false; }
};

const changePassword = async () => {
  savingPassword.value = true;
  try {
    await api.post('/api/auth/change-password', {
      current_password: passwords.value.current,
      new_password:     passwords.value.new,
    });
    passwords.value = { current: '', new: '', confirm: '' };
    toast.add({ severity: 'success', summary: 'Updated', detail: 'Password changed successfully', life: 3000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Password change failed', life: 5000 });
  } finally { savingPassword.value = false; }
};

const confirmDeleteAccount = () => {
  confirm.require({
    message:     'Your account and all associated data will be permanently deleted.',
    header:      'Delete Account?',
    icon:        'pi pi-exclamation-triangle',
    acceptLabel: 'Delete permanently',
    rejectLabel: 'Cancel',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await api.delete('/api/auth/me');
        authStore.logout();
        router.push('/login');
      } catch (err: any) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Could not delete account', life: 5000 });
      }
    },
  });
};
</script>

<style scoped>
.settings-view { max-width: 900px; margin: 0 auto; }

.page-header { margin-bottom: 1.75rem; }
.page-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.2rem;
  letter-spacing: -0.025em;
}
.subtitle { color: var(--text-secondary); font-size: 0.875rem; margin: 0; }

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.settings-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

.settings-card-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem; font-weight: 600; color: var(--text-primary); margin: 0;
  letter-spacing: -0.01em;
}
.settings-card-title.danger { color: var(--danger-color); }

.form-field  { display: flex; flex-direction: column; gap: 0.35rem; }
.form-label  { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); }
.field-hint  { color: var(--text-disabled); font-size: 0.78rem; }
.field-error { color: var(--danger-color); font-size: 0.78rem; }
.card-footer { display: flex; justify-content: flex-end; margin-top: 0.25rem; }

.info-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.625rem 0; border-bottom: 1px solid var(--bg-tertiary);
}
.info-row:last-child { border-bottom: none; }
.info-label { font-size: 0.875rem; color: var(--text-secondary); }
.info-value { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); }
.mono       { font-family: monospace; font-size: 0.78rem; }

.legal-links { display: flex; flex-direction: column; gap: 0.625rem; }
.legal-link {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.7rem 0.875rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 0.875rem;
  transition: background 0.15s;
}
.legal-link:hover { background: var(--bg-secondary); color: var(--text-primary); }
.ml-auto { margin-left: auto; }

.data-card { border-color: rgba(59,130,246,0.25); }
.data-text { font-size: 0.875rem; color: var(--text-secondary); margin: 0; line-height: 1.6; }
.data-list { display: flex; flex-direction: column; gap: 0.4rem; }
.data-list-item {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.875rem; color: var(--text-primary);
}
.data-list .pi-check-circle { color: #22c55e; }
.data-email { color: var(--primary-color); }
.data-email:hover { text-decoration: underline; }

.danger-card { border-color: rgba(239,68,68,0.25); }
.danger-text { font-size: 0.875rem; color: var(--text-secondary); margin: 0; }

@media (max-width: 768px) {
  .settings-grid { grid-template-columns: 1fr; }
}

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
