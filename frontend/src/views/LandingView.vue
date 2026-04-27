<template>
  <div class="landing-view">
    <div class="landing-card">
      <div class="hero">
        <div class="logo-icon">
          <i class="pi pi-video"></i>
        </div>
        <h1>SocialHub</h1>
        <p class="tagline">Upload once. Post to YouTube, TikTok &amp; Instagram.</p>
      </div>

      <div class="platforms">
        <div class="platform platform--youtube">YouTube</div>
        <div class="platform platform--tiktok">TikTok</div>
        <div class="platform platform--instagram">Instagram</div>
      </div>

      <ul class="features">
        <li><i class="pi pi-check-circle"></i> Single upload to all platforms</li>
        <li><i class="pi pi-check-circle"></i> Manage titles, descriptions &amp; hashtags</li>
        <li><i class="pi pi-check-circle"></i> Secure OAuth — no passwords stored</li>
      </ul>

      <div class="cta-buttons">
        <Button
          label="Create Account"
          icon="pi pi-user-plus"
          class="p-button-lg"
          @click="router.push('/register')"
        />
        <Button
          label="Sign In"
          icon="pi pi-sign-in"
          outlined
          class="p-button-lg"
          @click="router.push('/login')"
        />
      </div>
    </div>

    <LegalFooter />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import LegalFooter from '@/components/layout/LegalFooter.vue';

const router = useRouter();
</script>

<style scoped>
.landing-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
}

.landing-card {
  width: 100%;
  max-width: 500px;
  background: white;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.hero {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-icon {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 0.75rem;
}

.hero h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
}

.tagline {
  margin: 0;
  color: #64748b;
  font-size: 1rem;
  line-height: 1.5;
}

.platforms {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1.75rem;
}

.platform {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
}

.platform--youtube  { background: #FF0000; }
.platform--tiktok   { background: #000000; }
.platform--instagram { background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); }

.features {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.features li {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #475569;
  font-size: 0.95rem;
}

.features i {
  color: #667eea;
  font-size: 1rem;
}

.cta-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

@media (max-width: 480px) {
  .landing-card {
    padding: 2rem 1.25rem;
  }
}
</style>
