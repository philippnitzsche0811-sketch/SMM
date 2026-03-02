<template>
  <div class="settings-view">
    <div class="page-header">
      <h1>Einstellungen</h1>
      <p class="subtitle">Verwalte dein Profil und dein Konto</p>
    </div>

    <div class="settings-grid">
      <!-- Profile Card -->
      <div class="settings-card">
        <h3 class="settings-card-title">
          <i class="pi pi-user"></i> Profil
        </h3>

        <div class="form-field">
          <label>Benutzername</label>
          <InputText v-model="profile.username" placeholder="Benutzername" class="w-full" />
        </div>
        <div class="form-field">
          <label>E-Mail</label>
          <InputText :value="authStore.userEmail || ''" disabled class="w-full" />
          <small class="field-hint">E-Mail kann nicht geändert werden</small>
        </div>

        <div class="card-footer">
          <Button
            label="Speichern"
            icon="pi pi-check"
            :loading="savingProfile"
            @click="saveProfile"
          />
        </div>
      </div>

      <!-- Change Password Card -->
      <div class="settings-card">
        <h3 class="settings-card-title">
          <i class="pi pi-lock"></i> Passwort ändern
        </h3>

        <div class="form-field">
          <label>Aktuelles Passwort</label>
          <Password v-model="passwords.current" :feedback="false" toggleMask class="w-full" inputClass="w-full" />
        </div>
        <div class="form-field">
          <label>Neues Passwort</label>
          <Password v-model="passwords.new" toggleMask class="w-full" inputClass="w-full" />
        </div>
        <div class="form-field">
          <label>Neues Passwort bestätigen</label>
          <Password v-model="passwords.confirm" :feedback="false" toggleMask class="w-full" inputClass="w-full" />
          <small v-if="passwordMismatch" class="field-error">Passwörter stimmen nicht überein</small>
        </div>

        <div class="card-footer">
          <Button
            label="Passwort ändern"
            icon="pi pi-lock"
            :loading="savingPassword"
            :disabled="!canChangePassword"
            @click="changePassword"
          />
        </div>
      </div>

      <!-- Account Info Card -->
      <div class="settings-card info-card">
        <h3 class="settings-card-title">
          <i class="pi pi-info-circle"></i> Konto-Informationen
        </h3>

        <div class="info-row">
          <span class="info-label">Konto-ID</span>
          <span class="info-value mono">{{ authStore.userId }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">E-Mail verifiziert</span>
          <Tag
            :value="authStore.isVerified ? 'Verifiziert' : 'Nicht verifiziert'"
            :severity="authStore.isVerified ? 'success' : 'warn'"
          />
        </div>
        <div class="info-row">
          <span class="info-label">Verbundene Plattformen</span>
          <span class="info-value">{{ authStore.user?.connectedPlatforms?.length || 0 }}</span>
        </div>
      </div>

      <!-- Danger Zone -->
      <div class="settings-card danger-card">
        <h3 class="settings-card-title danger">
          <i class="pi pi-exclamation-triangle"></i> Gefahrenzone
        </h3>
        <p class="danger-text">Diese Aktion kann nicht rückgängig gemacht werden.</p>
        <Button
          label="Konto löschen"
          icon="pi pi-trash"
          class="p-button-danger p-button-outlined"
          @click="confirmDeleteAccount"
        />
      </div>
    </div>

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
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
const toast = useToast();
const confirm = useConfirm();
const router = useRouter();

const savingProfile = ref(false);
const savingPassword = ref(false);

const profile = ref({
  username: authStore.userName || '',
});

const passwords = ref({
  current: '',
  new: '',
  confirm: '',
});

const passwordMismatch = computed(
  () => passwords.value.new && passwords.value.confirm && passwords.value.new !== passwords.value.confirm
);

const canChangePassword = computed(
  () => passwords.value.current && passwords.value.new && passwords.value.confirm && !passwordMismatch.value
);

const saveProfile = async () => {
  savingProfile.value = true;
  try {
    await api.patch(`/api/auth/me`, {
      username: profile.value.username,
    });

    if (authStore.user) {
      authStore.user.username = profile.value.username;
      localStorage.setItem('user', JSON.stringify(authStore.user));
    }

    toast.add({ severity: 'success', summary: 'Gespeichert', detail: 'Profil aktualisiert', life: 3000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || 'Speichern fehlgeschlagen', life: 5000 });
  } finally {
    savingProfile.value = false;
  }
};

const changePassword = async () => {
  savingPassword.value = true;
  try {
    await api.post('/api/auth/change-password', {
      current_password: passwords.value.current,
      new_password: passwords.value.new,
    });

    passwords.value = { current: '', new: '', confirm: '' };
    toast.add({ severity: 'success', summary: 'Geändert', detail: 'Passwort erfolgreich geändert', life: 3000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: err.response?.data?.detail || 'Passwort-Änderung fehlgeschlagen', life: 5000 });
  } finally {
    savingPassword.value = false;
  }
};

const confirmDeleteAccount = () => {
  confirm.require({
    message: 'Dein Konto und alle Daten werden unwiderruflich gelöscht.',
    header: 'Konto wirklich löschen?',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Endgültig löschen',
    rejectLabel: 'Abbrechen',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await api.delete('/api/auth/me');
        authStore.logout();
        router.push('/login');
      } catch (err: any) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Konto konnte nicht gelöscht werden', life: 5000 });
      }
    },
  });
};
</script>

<style scoped>
.settings-view { max-width: 900px; margin: 0 auto; }

.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 1.75rem; font-weight: 700; color: #1e293b; margin: 0 0 0.25rem 0; }
.subtitle { color: #64748b; font-size: 0.9rem; margin: 0; }

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.settings-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.settings-card-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 1rem; font-weight: 600; color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.settings-card-title.danger { color: #ef4444; }

.form-field { display: flex; flex-direction: column; gap: 0.375rem; }
.form-field label { font-size: 0.875rem; font-weight: 500; color: #374151; }
.field-hint { color: #94a3b8; font-size: 0.8rem; }
.field-error { color: #ef4444; font-size: 0.8rem; }

.card-footer { display: flex; justify-content: flex-end; margin-top: 0.5rem; }

/* Info Card */
.info-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.75rem 0; border-bottom: 1px solid #f1f5f9;
}
.info-row:last-child { border-bottom: none; }
.info-label { font-size: 0.875rem; color: #64748b; }
.info-value { font-size: 0.875rem; font-weight: 500; color: #1e293b; }
.mono { font-family: monospace; font-size: 0.8rem; }

/* Danger */
.danger-card { border-color: #fecaca; }
.danger-text { font-size: 0.875rem; color: #64748b; margin: 0; }

@media (max-width: 768px) {
  .settings-grid { grid-template-columns: 1fr; }
}
</style>
