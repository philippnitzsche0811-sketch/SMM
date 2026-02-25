<template>
  <div class="settings-view">
    <!-- Header -->
    <div class="settings-header">
      <h1>
        <i class="pi pi-cog"></i>
        Einstellungen
      </h1>
    </div>

    <div class="settings-content">
      <!-- Account Settings Card -->
      <Card>
        <template #title>
          <i class="pi pi-user"></i>
          Account
        </template>
        
        <template #content>
          <div class="setting-item">
            <label>Email</label>
            <InputText 
              :value="authStore.userEmail" 
              disabled 
              class="w-full"
            />
          </div>

          <div class="setting-item">
            <label>User ID</label>
            <InputText 
              :value="authStore.userId" 
              disabled 
              class="w-full"
            />
          </div>

          <Divider />

          <div class="setting-item">
            <Button 
              label="Passwort ändern"
              icon="pi pi-lock"
              @click="showPasswordDialog = true"
              outlined
            />
          </div>
        </template>
      </Card>

      <!-- Security Settings Card -->
      <Card>
        <template #title>
          <i class="pi pi-shield"></i>
          Sicherheit
        </template>
        
        <template #content>
          <div class="setting-item">
            <label>Email verifiziert</label>
            <Tag 
              :value="authStore.isVerified ? 'Verifiziert' : 'Nicht verifiziert'"
              :severity="authStore.isVerified ? 'success' : 'warning'"
            />
          </div>
        </template>
      </Card>

      <!-- Danger Zone Card -->
      <Card class="danger-zone">
        <template #title>
          <i class="pi pi-exclamation-triangle"></i>
          Danger Zone
        </template>
        
        <template #content>
          <div class="setting-item">
            <Button 
              label="Account löschen"
              icon="pi pi-trash"
              severity="danger"
              outlined
              @click="confirmDeleteAccount"
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- ✅ Password Change Dialog -->
    <Dialog 
      v-model:visible="showPasswordDialog"
      header="Passwort ändern"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="password-form">
        <div class="form-field">
          <label for="currentPassword">Aktuelles Passwort</label>
          <Password 
            id="currentPassword"
            v-model="passwordForm.currentPassword"
            :feedback="false"
            toggleMask
            class="w-full"
            :class="{ 'p-invalid': passwordErrors.currentPassword }"
          />
          <small v-if="passwordErrors.currentPassword" class="p-error">
            {{ passwordErrors.currentPassword }}
          </small>
        </div>

        <div class="form-field">
          <label for="newPassword">Neues Passwort</label>
          <Password 
            id="newPassword"
            v-model="passwordForm.newPassword"
            toggleMask
            class="w-full"
            :class="{ 'p-invalid': passwordErrors.newPassword }"
          />
          <small v-if="passwordForm.newPassword && passwordForm.newPassword.length < 8" class="p-error">
            Passwort muss mindestens 8 Zeichen lang sein
          </small>
        </div>

        <div class="form-field">
          <label for="confirmPassword">Neues Passwort bestätigen</label>
          <Password 
            id="confirmPassword"
            v-model="passwordForm.confirmPassword"
            :feedback="false"
            toggleMask
            class="w-full"
            :class="{ 'p-invalid': passwordErrors.confirmPassword }"
          />
          <small v-if="passwordForm.confirmPassword && passwordForm.newPassword !== passwordForm.confirmPassword" class="p-error">
            Passwörter stimmen nicht überein
          </small>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Abbrechen" 
          severity="secondary"
          @click="closePasswordDialog"
        />
        <Button 
          label="Passwort ändern"
          icon="pi pi-check"
          :loading="isChangingPassword"
          :disabled="!isPasswordFormValid"
          @click="handleChangePassword"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Tag from 'primevue/tag';
import Divider from 'primevue/divider';
import Dialog from 'primevue/dialog';
import axios from 'axios';

const authStore = useAuthStore();
const toast = useToast();

// Password Dialog
const showPasswordDialog = ref(false);
const isChangingPassword = ref(false);

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const passwordErrors = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const isPasswordFormValid = computed(() => {
  return (
    passwordForm.value.currentPassword &&
    passwordForm.value.newPassword &&
    passwordForm.value.newPassword.length >= 8 &&
    passwordForm.value.newPassword === passwordForm.value.confirmPassword
  );
});

const handleChangePassword = async () => {
  if (!isPasswordFormValid.value) return;

  // Reset errors
  passwordErrors.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  };

  isChangingPassword.value = true;

  try {
    await axios.post('/api/auth/change-password', {
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword
    });

    toast.add({
      severity: 'success',
      summary: 'Passwort geändert',
      detail: 'Dein Passwort wurde erfolgreich geändert',
      life: 3000
    });

    closePasswordDialog();
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 'Passwort konnte nicht geändert werden';
    
    // Check if it's a wrong password error
    if (errorMessage.includes('Aktuelles Passwort ist falsch')) {
      passwordErrors.value.currentPassword = errorMessage;
    }
    
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    isChangingPassword.value = false;
  }
};

const closePasswordDialog = () => {
  showPasswordDialog.value = false;
  passwordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
  passwordErrors.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
};

const confirmDeleteAccount = () => {
  toast.add({
    severity: 'warn',
    summary: 'Noch nicht implementiert',
    detail: 'Account-Löschung ist noch nicht verfügbar',
    life: 3000
  });
};
</script>

<style scoped>
.settings-view {
  min-height: 100vh;
  background: var(--surface-ground);
  padding: 2rem;
}

.settings-header {
  max-width: 1200px;
  margin: 0 auto 2rem;
}

.settings-header h1 {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 2rem;
  margin: 0;
}

.settings-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.setting-item {
  margin-bottom: 1.5rem;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-item label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.danger-zone {
  border: 2px solid var(--red-500);
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem 0;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-weight: 600;
  color: var(--text-color);
}

.p-error {
  color: var(--red-500);
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.p-invalid {
  border-color: var(--red-500);
}

@media (max-width: 768px) {
  .settings-view {
    padding: 1rem;
  }

  .settings-header h1 {
    font-size: 1.5rem;
  }
}
</style>

