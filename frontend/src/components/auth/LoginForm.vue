<template>
  <form @submit.prevent="handleSubmit" class="login-form">
    <div class="field">
      <label for="email">E-Mail-Adresse</label>
      <InputText
        id="email"
        v-model="formData.email"
        type="email"
        placeholder="deine@email.de"
        :class="{ 'p-invalid': errors.email }"
        @blur="validateEmail"
      />
      <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
    </div>

    <div class="field">
      <label for="password">Passwort</label>
      <Password
        id="password"
        v-model="formData.password"
        placeholder="Passwort eingeben"
        :feedback="false"
        toggleMask
        :class="{ 'p-invalid': errors.password }"
        @blur="validatePassword"
      />
      <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
    </div>

    <Button
      type="submit"
      label="Anmelden"
      :loading="loading"
      :disabled="!isFormValid"
      class="submit-btn"
      icon="pi pi-sign-in"
    />

    <div class="form-footer">
      <a href="#" class="forgot-password">Passwort vergessen?</a>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import { isValidEmail } from '@/utils/validators';

const emit = defineEmits<{
  success: [email: string, password: string];
}>();

const toast = useToast();
const loading = ref(false);

const formData = ref({
  email: '',
  password: ''
});

const errors = ref({
  email: '',
  password: ''
});

const validateEmail = () => {
  if (!formData.value.email) {
    errors.value.email = 'E-Mail ist erforderlich';
  } else if (!isValidEmail(formData.value.email)) {
    errors.value.email = 'Ungültige E-Mail-Adresse';
  } else {
    errors.value.email = '';
  }
};

const validatePassword = () => {
  if (!formData.value.password) {
    errors.value.password = 'Passwort ist erforderlich';
  } else if (formData.value.password.length < 6) {
    errors.value.password = 'Passwort muss mindestens 6 Zeichen lang sein';
  } else {
    errors.value.password = '';
  }
};

const isFormValid = computed(() => {
  return formData.value.email && 
         formData.value.password && 
         !errors.value.email && 
         !errors.value.password;
});

const handleSubmit = async () => {
  validateEmail();
  validatePassword();

  if (!isFormValid.value) return;

  loading.value = true;

  try {
    emit('success', formData.value.email, formData.value.password);

    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: 'Login erfolgreich!',
      life: 3000
    });
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Login fehlgeschlagen',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  color: #333;
}

.submit-btn {
  margin-top: 1rem;
  width: 100%;
}

.form-footer {
  text-align: center;
}

.forgot-password {
  color: #2196F3;
  text-decoration: none;
  font-size: 0.9rem;
}

.forgot-password:hover {
  text-decoration: underline;
}
</style>
