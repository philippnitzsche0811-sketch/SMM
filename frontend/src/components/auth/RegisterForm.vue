<template>
  <form @submit.prevent="handleSubmit" class="register-form">
    <div class="field">
      <label for="reg-email">E-Mail-Adresse</label>
      <InputText
        id="reg-email"
        v-model="formData.email"
        type="email"
        placeholder="deine@email.de"
        :class="{ 'p-invalid': errors.email }"
        @blur="validateEmail"
      />
      <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
    </div>

    <div class="field">
      <label for="reg-password">Passwort</label>
      <Password
        id="reg-password"
        v-model="formData.password"
        placeholder="Sicheres Passwort wählen"
        :feedback="true"
        toggleMask
        :class="{ 'p-invalid': errors.password }"
        @blur="validatePassword"
      >
        <template #header>
          <h6>Wähle ein Passwort</h6>
        </template>
        <template #footer>
          <Divider />
          <p class="password-hints">Empfehlungen</p>
          <ul class="password-requirements">
            <li>Mindestens ein Kleinbuchstabe</li>
            <li>Mindestens ein Großbuchstabe</li>
            <li>Mindestens eine Zahl</li>
            <li>Mindestens 8 Zeichen</li>
          </ul>
        </template>
      </Password>
      <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
    </div>

    <div class="field">
      <label for="reg-confirm">Passwort bestätigen</label>
      <Password
        id="reg-confirm"
        v-model="formData.confirmPassword"
        placeholder="Passwort wiederholen"
        :feedback="false"
        toggleMask
        :class="{ 'p-invalid': errors.confirmPassword }"
        @blur="validateConfirmPassword"
      />
      <small v-if="errors.confirmPassword" class="p-error">{{ errors.confirmPassword }}</small>
    </div>

    <div class="field-checkbox">
      <Checkbox
        id="terms"
        v-model="formData.acceptTerms"
        :binary="true"
      />
      <label for="terms">
        Ich akzeptiere die <a href="#">AGB</a> und <a href="#">Datenschutzerklärung</a>
      </label>
    </div>

    <Button
      type="submit"
      label="Registrieren"
      :loading="loading"
      :disabled="!isFormValid"
      class="submit-btn"
      icon="pi pi-user-plus"
    />
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Divider from 'primevue/divider';
import { isValidEmail, isStrongPassword } from '@/utils/validators';

// ✅ Emit sendet ein Objekt
const emit = defineEmits<{
  success: [data: { email: string; password: string }];
}>();

const toast = useToast();
const loading = ref(false);

const formData = ref({
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
});

const errors = ref({
  email: '',
  password: '',
  confirmPassword: ''
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
  } else if (!isStrongPassword(formData.value.password)) {
    errors.value.password = 'Passwort erfüllt nicht die Anforderungen';
  } else {
    errors.value.password = '';
  }
};

const validateConfirmPassword = () => {
  if (!formData.value.confirmPassword) {
    errors.value.confirmPassword = 'Bitte bestätige dein Passwort';
  } else if (formData.value.password !== formData.value.confirmPassword) {
    errors.value.confirmPassword = 'Passwörter stimmen nicht überein';
  } else {
    errors.value.confirmPassword = '';
  }
};

const isFormValid = computed(() => {
  return formData.value.email && 
         formData.value.password && 
         formData.value.confirmPassword &&
         formData.value.acceptTerms &&
         !errors.value.email && 
         !errors.value.password &&
         !errors.value.confirmPassword;
});

const handleSubmit = async () => {
  validateEmail();
  validatePassword();
  validateConfirmPassword();

  if (!isFormValid.value) return;

  loading.value = true;

  try {
    // ✅ Emit als Objekt
    emit('success', {
      email: formData.value.email,
      password: formData.value.password
    });

    // Toast wird vom Parent Component gehandelt
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Registrierung fehlgeschlagen',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.field-checkbox label {
  font-size: 0.9rem;
}

.field-checkbox a {
  color: #2196F3;
  text-decoration: none;
}

.field-checkbox a:hover {
  text-decoration: underline;
}

label {
  font-weight: 600;
  color: #333;
}

.submit-btn {
  margin-top: 1rem;
  width: 100%;
}

.password-hints {
  margin: 0.5rem 0;
  font-weight: 600;
}

.password-requirements {
  padding-left: 1.2rem;
  margin: 0;
  font-size: 0.85rem;
}

.password-requirements li {
  margin: 0.25rem 0;
}
</style>
