<template>
  <div class="landing">

    <!-- Nav -->
    <nav class="nav">
      <div class="nav-inner">
        <div class="nav-logo">
          <img :src="logoUrl" alt="SocialHub" class="nav-logo-img" />
          <span>SocialHub</span>
        </div>
        <div class="nav-links">
          <Button label="Sign In" text class="p-button-sm" @click="router.push('/login')" />
          <Button label="Get Started" class="p-button-sm" @click="router.push('/register')" />
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-badges">
          <span class="badge badge--youtube"><i class="pi pi-youtube"></i> YouTube</span>
          <span class="badge badge--tiktok"><i class="pi pi-video"></i> TikTok</span>
          <span class="badge badge--instagram"><i class="pi pi-instagram"></i> Instagram</span>
        </div>
        <h1>Upload once.<br>Post everywhere.</h1>
        <p class="hero-sub">
          SocialHub lets you manage your video uploads to YouTube, TikTok, and Instagram
          from a single dashboard. One login, all your platforms.
        </p>
        <div class="hero-cta">
          <Button label="Create free account" icon="pi pi-user-plus" class="p-button-lg cta-primary" @click="router.push('/register')" />
          <Button label="Sign in" icon="pi pi-sign-in" outlined class="p-button-lg cta-secondary" @click="router.push('/login')" />
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="section section--gray">
      <div class="section-inner">
        <h2 class="section-title">How it works</h2>
        <p class="section-sub">Three steps to publish your video on all platforms at once.</p>
        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-icon"><i class="pi pi-link"></i></div>
            <h3>Connect your accounts</h3>
            <p>Link your YouTube, TikTok, and Instagram accounts once via secure OAuth. No passwords stored — you can revoke access anytime.</p>
          </div>
          <div class="step-arrow"><i class="pi pi-chevron-right"></i></div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-icon"><i class="pi pi-cloud-upload"></i></div>
            <h3>Upload your video</h3>
            <p>Drag and drop your video file. Add a title, description, and hashtags. Choose the privacy setting for each platform.</p>
          </div>
          <div class="step-arrow"><i class="pi pi-chevron-right"></i></div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-icon"><i class="pi pi-send"></i></div>
            <h3>Publish everywhere</h3>
            <p>Select which platforms to post to and hit upload. SocialHub handles the rest — simultaneously publishing to all selected platforms.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="section section--white">
      <div class="section-inner">
        <h2 class="section-title">Everything you need</h2>
        <p class="section-sub">Built for creators who publish regularly across multiple platforms.</p>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon-wrap"><i class="pi pi-share-alt"></i></div>
            <h3>Multi-platform publishing</h3>
            <p>Post to YouTube, TikTok, and Instagram Reels simultaneously from one interface.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon-wrap"><i class="pi pi-hashtag"></i></div>
            <h3>Metadata management</h3>
            <p>Set titles, descriptions, and hashtags. Optimise each upload for discoverability.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon-wrap"><i class="pi pi-eye"></i></div>
            <h3>Privacy control</h3>
            <p>Choose public, unlisted, or private per platform before publishing.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon-wrap"><i class="pi pi-shield"></i></div>
            <h3>Secure by design</h3>
            <p>OAuth 2.0 authentication only. Tokens are encrypted at rest. No passwords ever stored.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon-wrap"><i class="pi pi-history"></i></div>
            <h3>Upload history</h3>
            <p>Track every upload with status, platform results, and error details all in one place.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon-wrap"><i class="pi pi-bolt"></i></div>
            <h3>Background processing</h3>
            <p>Uploads run in the background — close the tab and your video will still be published.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Platforms -->
    <section class="section section--gray">
      <div class="section-inner">
        <h2 class="section-title">Supported platforms</h2>
        <div class="platforms-grid">
          <div class="platform-card">
            <div class="platform-logo platform-logo--youtube"><i class="pi pi-youtube"></i></div>
            <h3>YouTube</h3>
            <p>Upload videos directly to your YouTube channel. Supports public, unlisted, and private videos. Automatic token refresh keeps your connection alive.</p>
          </div>
          <div class="platform-card">
            <div class="platform-logo platform-logo--tiktok"><i class="pi pi-video"></i></div>
            <h3>TikTok</h3>
            <p>Post videos to TikTok via the official Content Posting API. Control duet, stitch, and comment settings per upload.</p>
          </div>
          <div class="platform-card">
            <div class="platform-logo platform-logo--instagram"><i class="pi pi-instagram"></i></div>
            <h3>Instagram</h3>
            <p>Publish Reels to your Instagram account via the Meta Graph API. Connects to your Instagram Business or Creator account.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="section section--dark">
      <div class="section-inner cta-inner">
        <h2>Ready to save time?</h2>
        <p>Create a free account and connect your first platform in under 2 minutes.</p>
        <Button
          label="Get started for free"
          icon="pi pi-arrow-right"
          iconPos="right"
          class="p-button-lg cta-dark-btn"
          @click="router.push('/register')"
        />
      </div>
    </section>

    <LegalFooter dark />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import LegalFooter from '@/components/layout/LegalFooter.vue';
import logoUrl from '@/assets/images/logo.png';

const router = useRouter();
</script>

<style scoped>
.landing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1e293b;
}

/* ── Nav ── */
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #e2e8f0;
}

.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0.875rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
  text-decoration: none;
}

.nav-logo-img {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  object-fit: contain;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* ── Hero ── */
.hero {
  background: #fff;
  padding: 6rem 2rem 5rem;
  text-align: center;
  border-bottom: 1px solid #f1f5f9;
}

.hero-inner {
  max-width: 720px;
  margin: 0 auto;
}

.hero-badges {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid transparent;
}

.badge--youtube   { background: #fff5f5; color: #dc2626; border-color: #fecaca; }
.badge--tiktok    { background: #f8fafc; color: #1e293b; border-color: #e2e8f0; }
.badge--instagram { background: #fdf4ff; color: #9333ea; border-color: #e9d5ff; }

.hero h1 {
  font-size: clamp(2.4rem, 5vw, 3.75rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin: 0 0 1.25rem 0;
  color: #0f172a;
}

.hero-sub {
  font-size: 1.125rem;
  line-height: 1.75;
  color: #64748b;
  margin: 0 0 2.5rem 0;
}

.hero-cta {
  display: flex;
  justify-content: center;
  gap: 0.875rem;
  flex-wrap: wrap;
}

.cta-primary {
  background: #0f172a !important;
  border-color: #0f172a !important;
  color: #fff !important;
}
.cta-primary:hover { background: #1e293b !important; border-color: #1e293b !important; }

.cta-secondary {
  border-color: #e2e8f0 !important;
  color: #1e293b !important;
}
.cta-secondary:hover { background: #f8fafc !important; }

/* ── Sections ── */
.section { padding: 5rem 2rem; }
.section--gray  { background: #f8fafc; }
.section--white { background: #fff; }
.section--dark  { background: #0f172a; color: #fff; text-align: center; }

.section-inner {
  max-width: 1100px;
  margin: 0 auto;
}

.section-title {
  font-size: clamp(1.75rem, 3vw, 2.25rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  text-align: center;
  margin: 0 0 0.75rem 0;
}

.section-sub {
  text-align: center;
  color: #64748b;
  font-size: 1rem;
  margin: 0 0 3rem 0;
}

/* ── Steps ── */
.steps {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  justify-content: center;
}

.step {
  flex: 1;
  max-width: 280px;
  text-align: center;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #0f172a;
  color: white;
  font-size: 0.8rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.step-icon {
  font-size: 1.75rem;
  color: #6366f1;
  margin-bottom: 0.75rem;
}

.step h3 { font-size: 1rem; font-weight: 600; margin: 0 0 0.5rem 0; }
.step p  { font-size: 0.9rem; color: #64748b; line-height: 1.6; margin: 0; }

.step-arrow {
  color: #cbd5e1;
  font-size: 1.1rem;
  padding-top: 3.5rem;
  flex-shrink: 0;
}

/* ── Features ── */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
}

.feature-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
}

.feature-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: #6366f1;
}

.feature-card h3 { font-size: 0.9375rem; font-weight: 600; margin: 0 0 0.4rem 0; }
.feature-card p  { font-size: 0.875rem; color: #64748b; line-height: 1.6; margin: 0; }

/* ── Platforms ── */
.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
}

.platform-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
}

.platform-logo {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.375rem;
  color: white;
  margin: 0 auto 1.25rem;
}

.platform-logo--youtube   { background: #ef4444; }
.platform-logo--tiktok    { background: #1e293b; }
.platform-logo--instagram { background: #9333ea; }

.platform-card h3 { font-size: 1rem; font-weight: 600; margin: 0 0 0.5rem 0; }
.platform-card p  { font-size: 0.875rem; color: #64748b; line-height: 1.6; margin: 0; }

/* ── Dark CTA ── */
.cta-inner h2 {
  font-size: clamp(1.75rem, 3vw, 2.25rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 0.75rem 0;
  color: #fff;
}

.cta-inner p {
  color: #94a3b8;
  font-size: 1rem;
  margin: 0 0 2rem 0;
}

.cta-dark-btn {
  background: #fff !important;
  border-color: #fff !important;
  color: #0f172a !important;
  font-weight: 600 !important;
}
.cta-dark-btn:hover { background: #f1f5f9 !important; }

/* ── Legal footer ── */
:deep(.legal-footer) {
  background: #0f172a;
  border-top: 1px solid #1e293b;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .hero    { padding: 4rem 1.25rem 3rem; }
  .section { padding: 3.5rem 1.25rem; }

  .steps {
    flex-direction: column;
    align-items: center;
  }

  .step      { max-width: 100%; }
  .step-arrow { display: none; }
  .nav-inner { padding: 0.75rem 1.25rem; }
}
</style>
