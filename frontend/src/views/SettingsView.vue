<template>
  <div class="settings-view">
    <div class="page-header">
      <h1>Einstellungen</h1>
      <p class="subtitle">Profil, Plattformen und Konto verwalten</p>
    </div>

    <!-- Tab-Navigation -->
    <div class="settings-tabs">
      <button class="settings-tab" :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">
        <i class="pi pi-user"></i> Profil
      </button>
      <button class="settings-tab" :class="{ active: activeTab === 'platforms' }" @click="activeTab = 'platforms'">
        <i class="pi pi-link"></i> Plattformen
      </button>
      <button class="settings-tab" :class="{ active: activeTab === 'account' }" @click="activeTab = 'account'">
        <i class="pi pi-cog"></i> Konto
      </button>
    </div>

    <!-- Tab: Plattformen -->
    <div v-if="activeTab === 'platforms'" class="platforms-tab">
      <p class="platforms-hint">Verbinde deine Social-Media-Konten, um Videos von hier hochzuladen.</p>
      <div class="platforms-list">

        <!-- YouTube -->
        <div class="platform-row">
          <div class="platform-row-left">
            <div class="platform-icon-wrap youtube"><i class="pi pi-youtube"></i></div>
            <div class="platform-row-info">
              <span class="platform-row-name">YouTube</span>
              <span class="platform-row-sub" v-if="platformStore.isConnected('youtube')">
                {{ platformStore.getConnectionStatus('youtube')?.username || 'Verbunden' }}
              </span>
              <span class="platform-row-sub" v-else>Client Secret (JSON) hochladen</span>
            </div>
          </div>
          <div class="platform-row-right">
            <span class="platform-status-dot" :class="platformStore.isConnected('youtube') ? 'connected' : 'disconnected'">
              {{ platformStore.isConnected('youtube') ? 'Verbunden' : 'Nicht verbunden' }}
            </span>
            <FileUpload
              v-if="!platformStore.isConnected('youtube')"
              mode="basic"
              accept="application/json"
              :maxFileSize="1000000"
              chooseLabel="Verbinden"
              customUpload
              @uploader="handleYouTubeUpload"
              :auto="false"
              :disabled="ytUploading"
              class="platform-upload-btn"
            />
            <Button
              v-else
              label="Trennen"
              severity="danger"
              outlined
              size="small"
              @click="handleDisconnect('youtube')"
              :loading="disconnecting === 'youtube'"
            />
          </div>
        </div>

        <!-- TikTok -->
        <div class="platform-row">
          <div class="platform-row-left">
            <div class="platform-icon-wrap tiktok"><i class="pi pi-mobile"></i></div>
            <div class="platform-row-info">
              <span class="platform-row-name">TikTok</span>
              <span class="platform-row-sub" v-if="platformStore.isConnected('tiktok')">
                @{{ platformStore.getConnectionStatus('tiktok')?.username || 'Verbunden' }}
              </span>
              <span class="platform-row-sub" v-else>OAuth — du wirst weitergeleitet</span>
            </div>
          </div>
          <div class="platform-row-right">
            <span class="platform-status-dot" :class="platformStore.isConnected('tiktok') ? 'connected' : 'disconnected'">
              {{ platformStore.isConnected('tiktok') ? 'Verbunden' : 'Nicht verbunden' }}
            </span>
            <Button
              v-if="!platformStore.isConnected('tiktok')"
              label="Verbinden"
              icon="pi pi-sign-in"
              outlined
              size="small"
              @click="handleTikTokConnect"
              :loading="connecting === 'tiktok'"
            />
            <Button
              v-else
              label="Trennen"
              severity="danger"
              outlined
              size="small"
              @click="handleDisconnect('tiktok')"
              :loading="disconnecting === 'tiktok'"
            />
          </div>
        </div>

        <!-- Instagram -->
        <div class="platform-row">
          <div class="platform-row-left">
            <div class="platform-icon-wrap instagram"><i class="pi pi-instagram"></i></div>
            <div class="platform-row-info">
              <span class="platform-row-name">Instagram</span>
              <span class="platform-row-sub" v-if="platformStore.isConnected('instagram')">
                @{{ platformStore.getConnectionStatus('instagram')?.username || 'Verbunden' }}
              </span>
              <span class="platform-row-sub" v-else>Business / Creator Konto erforderlich</span>
            </div>
          </div>
          <div class="platform-row-right">
            <span class="platform-status-dot" :class="platformStore.isConnected('instagram') ? 'connected' : 'disconnected'">
              {{ platformStore.isConnected('instagram') ? 'Verbunden' : 'Nicht verbunden' }}
            </span>
            <Button
              v-if="!platformStore.isConnected('instagram')"
              label="Verbinden"
              icon="pi pi-sign-in"
              outlined
              size="small"
              @click="handleInstagramConnect"
              :loading="connecting === 'instagram'"
            />
            <Button
              v-else
              label="Trennen"
              severity="danger"
              outlined
              size="small"
              @click="handleDisconnect('instagram')"
              :loading="disconnecting === 'instagram'"
            />
          </div>
        </div>

      </div>
    </div>

    <div v-if="activeTab === 'profile' || activeTab === 'account'" class="settings-grid">
      <!-- Profile (nur in Profil-Tab) -->
      <div v-if="activeTab === 'profile'" class="settings-card">
        <h3 class="settings-card-title"><i class="pi pi-user"></i> Profil</h3>
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

      <!-- Creator Profile (nur in Profil-Tab) -->
      <div v-if="activeTab === 'profile'" class="settings-card">
        <h3 class="settings-card-title"><i class="pi pi-sparkles"></i> Creator Profile</h3>
        <p class="field-hint" style="margin:0">These settings personalize the AI — it generates niche-specific titles, descriptions and hashtags that match your content style.</p>
        <div class="form-field">
          <span class="form-label">Your niche</span>
          <Dropdown
            v-model="creatorProfile.niche"
            :options="nicheOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Select your niche…"
            class="w-full"
          />
        </div>
        <div class="form-field">
          <span class="form-label">Creator tone</span>
          <Dropdown
            v-model="creatorProfile.creatorTone"
            :options="toneOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Select your tone…"
            class="w-full"
          />
          <small class="field-hint">How you communicate with your audience</small>
        </div>
        <div class="card-footer">
          <Button label="Save creator profile" icon="pi pi-check" :loading="savingCreator" @click="saveCreatorProfile" />
        </div>
      </div>

      <!-- Change Password (nur in Konto-Tab) -->
      <div v-if="activeTab === 'account'" class="settings-card">
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

      <!-- Plan Status (nur in Konto-Tab) -->
      <div v-if="activeTab === 'account'" class="settings-card plan-card">
        <h3 class="settings-card-title"><i class="pi pi-star"></i> Dein Plan</h3>
        <div class="plan-status-row">
          <div class="plan-badge" :class="isProUser ? 'pro' : 'free'">
            <i class="pi pi-star-fill" v-if="isProUser"></i>
            <i class="pi pi-user" v-else></i>
            {{ isProUser ? 'Pro' : 'Free' }}
          </div>
          <div>
            <p class="plan-desc" v-if="!isProUser">
              Free-Plan: Alle Uploads, Scheduling, Kalender, Analytics — ohne KI.
            </p>
            <p class="plan-desc" v-else>
              Pro-Plan: KI-Optimierung für Titel, Beschreibung, Hashtags und Video-Analyse aktiv.
            </p>
          </div>
        </div>
        <div v-if="!isProUser" class="plan-features">
          <div class="plan-feature-item"><i class="pi pi-check-circle"></i> Alle 3 Plattformen</div>
          <div class="plan-feature-item"><i class="pi pi-check-circle"></i> Unbegrenzte Uploads &amp; Scheduling</div>
          <div class="plan-feature-item"><i class="pi pi-check-circle"></i> Upload-Gruppen &amp; Kalender</div>
          <div class="plan-feature-item pro-locked"><i class="pi pi-lock"></i> KI: Titel, Beschreibung, Hashtags</div>
          <div class="plan-feature-item pro-locked"><i class="pi pi-lock"></i> KI: Hook-Score &amp; Video-Analyse</div>
        </div>
        <div class="card-footer" v-if="!isProUser">
          <Button label="Upgrade auf Pro — €12/Monat" icon="pi pi-star" @click="showUpgradeDialog = true" />
        </div>
      </div>

      <!-- Account Info (nur in Konto-Tab) -->
      <div v-if="activeTab === 'account'" class="settings-card info-card">
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

      <!-- Legal Links (nur in Konto-Tab) -->
      <div v-if="activeTab === 'account'" class="settings-card">
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

      <!-- Data Deletion (nur in Konto-Tab) -->
      <div v-if="activeTab === 'account'" class="settings-card data-card">
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

      <!-- Danger Zone (nur in Konto-Tab) -->
      <div v-if="activeTab === 'account'" class="settings-card danger-card">
        <h3 class="settings-card-title danger"><i class="pi pi-exclamation-triangle"></i> Danger Zone</h3>
        <p class="danger-text">This action is permanent and cannot be undone.</p>
        <Button label="Delete Account" icon="pi pi-trash" class="p-button-danger p-button-outlined" @click="confirmDeleteAccount" />
      </div>
    </div><!-- end settings-grid -->

    <!-- Upgrade Dialog -->
    <Dialog v-model:visible="showUpgradeDialog" header="Pro freischalten" :modal="true" :style="{ width: '420px' }">
      <div class="upgrade-dialog-body">
        <p class="upgrade-price">€12 / Monat</p>
        <div class="upgrade-features">
          <div class="upgrade-feature"><i class="pi pi-check-circle"></i> KI-Titel, Beschreibung &amp; Hashtags</div>
          <div class="upgrade-feature"><i class="pi pi-check-circle"></i> Hook-Score &amp; Video-Analyse</div>
          <div class="upgrade-feature"><i class="pi pi-check-circle"></i> Hook-Vorschläge im Planen-Tab</div>
          <div class="upgrade-feature"><i class="pi pi-check-circle"></i> Kommentar-Hub (demnächst)</div>
        </div>
        <p class="upgrade-contact">Sende eine E-Mail an <a href="mailto:support@decodu-smm.com">support@decodu-smm.com</a>, um deinen Plan zu aktivieren.</p>
      </div>
      <template #footer>
        <Button label="Schließen" class="p-button-text" @click="showUpgradeDialog = false" />
      </template>
    </Dialog>

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
import { usePlan } from '@/composables/usePlan';
import { usePlatformStore } from '@/stores/platformStore';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Dropdown from 'primevue/dropdown';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import FileUpload from 'primevue/fileupload';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import api, { connectYouTube, connectInstagram } from '@/services/api';

const activeTab = ref<'profile' | 'platforms' | 'account'>('profile');

const authStore      = useAuthStore();
const toast          = useToast();
const confirm        = useConfirm();
const router         = useRouter();
const platformStore  = usePlatformStore();
const { isProUser }  = usePlan();

const showUpgradeDialog = ref(false);
const ytUploading       = ref(false);
const connecting        = ref<string | null>(null);
const disconnecting     = ref<string | null>(null);

const savingProfile  = ref(false);
const savingPassword = ref(false);
const savingCreator  = ref(false);

const profile   = ref({ username: authStore.userName || '' });
const passwords = ref({ current: '', new: '', confirm: '' });
const creatorProfile = ref({
  niche:       authStore.user?.niche || null,
  creatorTone: authStore.user?.creatorTone || null,
});

const nicheOptions = [
  { label: 'General (default)',     value: 'default'   },
  { label: 'Fitness & Sport',       value: 'fitness'   },
  { label: 'Food & Recipes',        value: 'food'      },
  { label: 'Finance & Money',       value: 'finance'   },
  { label: 'Gaming',                value: 'gaming'    },
  { label: 'Tech & Gadgets',        value: 'tech'      },
  { label: 'Lifestyle',             value: 'lifestyle' },
  { label: 'Education & Learning',  value: 'education' },
  { label: 'Comedy & Entertainment',value: 'comedy'    },
  { label: 'Beauty & Make-up',      value: 'beauty'    },
  { label: 'Travel',                value: 'travel'    },
];

const toneOptions = [
  { label: 'Informative (factual, direct)',        value: 'informative'   },
  { label: 'Educational (teach & explain)',        value: 'educational'   },
  { label: 'Entertainer (fun & personality)',      value: 'entertainer'   },
  { label: 'Inspirational (motivate & empower)',   value: 'inspirational' },
];

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

const saveCreatorProfile = async () => {
  savingCreator.value = true;
  try {
    await api.patch('/api/auth/me', {
      niche:        creatorProfile.value.niche,
      creator_tone: creatorProfile.value.creatorTone,
    });
    if (authStore.user) {
      authStore.user.niche = creatorProfile.value.niche;
      authStore.user.creatorTone = creatorProfile.value.creatorTone;
      localStorage.setItem('user', JSON.stringify(authStore.user));
    }
    toast.add({ severity: 'success', summary: 'Saved', detail: 'Creator profile updated — AI will use this for all future uploads', life: 4000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Save failed', life: 5000 });
  } finally { savingCreator.value = false; }
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

const handleYouTubeUpload = async (event: any) => {
  const file = event.files[0];
  if (!file || !authStore.userId) return;
  ytUploading.value = true;
  try {
    const response = await connectYouTube(authStore.userId, file);
    if (response.auth_url) {
      toast.add({ severity: 'info', summary: 'YouTube', detail: 'Weiterleitung zur Google-Anmeldung…', life: 2000 });
      setTimeout(() => { window.location.href = response.auth_url; }, 1200);
    }
  } catch {
    toast.add({ severity: 'error', summary: 'Fehler', detail: 'YouTube-Verbindung fehlgeschlagen', life: 5000 });
  } finally { ytUploading.value = false; }
};

const handleTikTokConnect = async () => {
  connecting.value = 'tiktok';
  try {
    const response = await api.post('/api/tiktok/connect', { user_id: authStore.userId });
    if (response.data.auth_url) {
      toast.add({ severity: 'info', summary: 'TikTok', detail: 'Weiterleitung zur TikTok-Anmeldung…', life: 2000 });
      setTimeout(() => { window.location.href = response.data.auth_url; }, 1200);
    }
  } catch {
    toast.add({ severity: 'error', summary: 'Fehler', detail: 'TikTok-Verbindung fehlgeschlagen', life: 5000 });
  } finally { connecting.value = null; }
};

const handleInstagramConnect = async () => {
  connecting.value = 'instagram';
  try {
    const response = await connectInstagram(authStore.userId!);
    if (response.auth_url) {
      toast.add({ severity: 'info', summary: 'Instagram', detail: 'Weiterleitung zur Instagram-Anmeldung…', life: 2000 });
      setTimeout(() => { window.location.href = response.auth_url; }, 1200);
    }
  } catch {
    toast.add({ severity: 'error', summary: 'Fehler', detail: 'Instagram-Verbindung fehlgeschlagen', life: 5000 });
  } finally { connecting.value = null; }
};

const handleDisconnect = async (platform: string) => {
  disconnecting.value = platform;
  try {
    await platformStore.disconnectPlatform(platform);
    toast.add({ severity: 'success', summary: 'Getrennt', detail: `${platform} wurde erfolgreich getrennt`, life: 3000 });
  } catch {
    toast.add({ severity: 'error', summary: 'Fehler', detail: 'Trennen fehlgeschlagen', life: 5000 });
  } finally { disconnecting.value = null; }
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
.settings-view { max-width: 900px; margin: 0 auto; padding: 1.5rem 1rem; }

/* Tabs */
.settings-tabs {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color, #3f3f46);
}
.settings-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.625rem 1rem;
  border: none;
  background: none;
  color: var(--text-secondary, #a1a1aa);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 0.15s, border-color 0.15s;
}
.settings-tab:hover { color: var(--text-primary, #f4f4f5); }
.settings-tab.active { color: var(--primary-400, #a78bfa); border-bottom-color: var(--primary-400, #a78bfa); }

/* Plattformen-Tab */
.platforms-hint {
  font-size: 0.875rem;
  color: var(--text-secondary, #a1a1aa);
  margin: 0 0 1.25rem;
}

.platforms-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.platform-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: rgba(255,255,255,0.02);
  gap: 1rem;
  border-bottom: 1px solid var(--border-color);
}
.platform-row:last-child { border-bottom: none; }
.platform-row:hover { background: rgba(255,255,255,0.04); }

.platform-row-left {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  flex: 1;
  min-width: 0;
}

.platform-icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.platform-icon-wrap.youtube   { background: rgba(239,68,68,0.12);  color: #f87171; }
.platform-icon-wrap.tiktok    { background: rgba(255,255,255,0.06); color: #cbd5e1; }
.platform-icon-wrap.instagram { background: rgba(236,72,153,0.12); color: #f9a8d4; }

.platform-row-info { display: flex; flex-direction: column; gap: 1px; }
.platform-row-name { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); }
.platform-row-sub  { font-size: 0.78rem; color: var(--text-secondary); }

.platform-row-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.platform-status-dot {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
}
.platform-status-dot.connected    { background: rgba(16,185,129,0.12); color: #10b981; }
.platform-status-dot.disconnected { background: rgba(161,161,170,0.1); color: var(--text-secondary); }

:deep(.platform-upload-btn .p-button) {
  padding: 0.375rem 0.875rem;
  font-size: 0.8125rem;
}

/* Plan card */
.plan-card { border-color: rgba(139,92,246,0.25); }

.plan-status-row {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.plan-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.375rem 0.875rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
}
.plan-badge.pro  { background: rgba(139,92,246,0.15); color: #a78bfa; border: 1px solid rgba(139,92,246,0.4); }
.plan-badge.free { background: rgba(161,161,170,0.1); color: var(--text-secondary); border: 1px solid var(--border-color); }

.plan-desc { font-size: 0.875rem; color: var(--text-secondary); margin: 0.25rem 0 0; line-height: 1.5; }

.plan-features {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.plan-feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-primary);
}
.plan-feature-item .pi-check-circle { color: #22c55e; }
.plan-feature-item.pro-locked { color: var(--text-secondary); }
.plan-feature-item.pro-locked .pi-lock { color: #71717a; }

/* Upgrade Dialog */
.upgrade-dialog-body { display: flex; flex-direction: column; gap: 1rem; }
.upgrade-price { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; text-align: center; }
.upgrade-features { display: flex; flex-direction: column; gap: 0.5rem; }
.upgrade-feature { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--text-primary); }
.upgrade-feature .pi-check-circle { color: #22c55e; }
.upgrade-contact { font-size: 0.8125rem; color: var(--text-secondary); margin: 0; text-align: center; }
.upgrade-contact a { color: var(--primary-color); }

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
