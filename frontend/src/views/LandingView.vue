<template>
  <div class="landing">

    <!-- Nav -->
    <nav class="nav">
      <div class="nav-inner">
        <div class="nav-logo">
          <i class="pi pi-video"></i>
          <span>SocialHub</span>
        </div>
        <div class="nav-links">
          <Button label="Sign In" outlined size="small" @click="router.push('/login')" />
          <Button label="Get Started" size="small" @click="router.push('/register')" />
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-badges">
          <span class="badge badge--youtube">YouTube</span>
          <span class="badge badge--tiktok">TikTok</span>
          <span class="badge badge--instagram">Instagram</span>
        </div>
        <h1>Upload once.<br>Post everywhere.</h1>
        <p class="hero-sub">
          SocialHub lets you manage your video uploads to YouTube, TikTok, and Instagram
          from a single dashboard. One login, all your platforms.
        </p>
        <div class="hero-cta">
          <Button label="Create free account" icon="pi pi-user-plus" size="large" @click="router.push('/register')" />
          <Button label="Sign in" icon="pi pi-sign-in" outlined size="large" @click="router.push('/login')" />
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="section section--light">
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
            <i class="pi pi-share-alt feature-icon"></i>
            <h3>Multi-platform publishing</h3>
            <p>Post to YouTube, TikTok, and Instagram Reels simultaneously from one interface.</p>
          </div>
          <div class="feature-card">
            <i class="pi pi-hashtag feature-icon"></i>
            <h3>Metadata management</h3>
            <p>Set titles, descriptions, and hashtags. Optimise each upload for discoverability.</p>
          </div>
          <div class="feature-card">
            <i class="pi pi-eye feature-icon"></i>
            <h3>Privacy control</h3>
            <p>Choose public, unlisted, or private per platform before publishing.</p>
          </div>
          <div class="feature-card">
            <i class="pi pi-shield feature-icon"></i>
            <h3>Secure by design</h3>
            <p>OAuth 2.0 authentication only. Tokens are encrypted at rest. No passwords ever stored.</p>
          </div>
          <div class="feature-card">
            <i class="pi pi-history feature-icon"></i>
            <h3>Upload history</h3>
            <p>Track every upload with status, platform results, and error details all in one place.</p>
          </div>
          <div class="feature-card">
            <i class="pi pi-bolt feature-icon"></i>
            <h3>Background processing</h3>
            <p>Uploads run in the background — close the tab and your video will still be published.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Platforms -->
    <section class="section section--light">
      <div class="section-inner">
        <h2 class="section-title">Supported platforms</h2>
        <div class="platforms-grid">
          <div class="platform-card">
            <div class="platform-logo platform-logo--youtube">▶</div>
            <h3>YouTube</h3>
            <p>Upload videos directly to your YouTube channel. Supports public, unlisted, and private videos. Automatic token refresh keeps your connection alive.</p>
          </div>
          <div class="platform-card">
            <div class="platform-logo platform-logo--tiktok">♪</div>
            <h3>TikTok</h3>
            <p>Post videos to TikTok via the official Content Posting API. Control duet, stitch, and comment settings per upload.</p>
          </div>
          <div class="platform-card">
            <div class="platform-logo platform-logo--instagram">◎</div>
            <h3>Instagram</h3>
            <p>Publish Reels to your Instagram account via the Meta Graph API. Connects to your Instagram Business or Creator account.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="section section--cta">
      <div class="section-inner cta-inner">
        <h2>Ready to save time?</h2>
        <p>Create a free account and connect your first platform in under 2 minutes.</p>
        <Button
          label="Get started for free"
          icon="pi pi-arrow-right"
          iconPos="right"
          size="large"
          class="cta-btn"
          @click="router.push('/register')"
        />
      </div>
    </section>

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
/* ── Base ─────────────────────────────────────────── */
.landing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1e293b;
}

/* ── Nav ──────────────────────────────────────────── */
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #e2e8f0;
}

.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0.9rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #667eea;
}

.nav-logo i {
  font-size: 1.4rem;
}

.nav-links {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

/* ── Hero ─────────────────────────────────────────── */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 5rem 2rem;
  text-align: center;
  color: white;
}

.hero-inner {
  max-width: 720px;
  margin: 0 auto;
}

.hero-badges {
  display: flex;
  justify-content: center;
  gap: 0.6rem;
  margin-bottom: 1.75rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.3rem 0.9rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
}

.badge--youtube   { background: rgba(255,0,0,0.85); }
.badge--tiktok    { background: rgba(0,0,0,0.55); border: 1px solid rgba(255,255,255,0.3); }
.badge--instagram { background: linear-gradient(45deg, #f09433, #dc2743, #bc1888); }

.hero h1 {
  font-size: clamp(2.4rem, 5vw, 3.5rem);
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 1.25rem 0;
  color: white;
}

.hero-sub {
  font-size: 1.15rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.85);
  margin: 0 0 2.25rem 0;
}

.hero-cta {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* ── Generic section ──────────────────────────────── */
.section {
  padding: 5rem 2rem;
}

.section--light  { background: #f8fafc; }
.section--white  { background: white; }

.section-inner {
  max-width: 1100px;
  margin: 0 auto;
}

.section-title {
  font-size: clamp(1.75rem, 3vw, 2.25rem);
  font-weight: 700;
  text-align: center;
  margin: 0 0 0.75rem 0;
}

.section-sub {
  text-align: center;
  color: #64748b;
  font-size: 1.05rem;
  margin: 0 0 3rem 0;
}

/* ── Steps ────────────────────────────────────────── */
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
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.step-icon {
  font-size: 2rem;
  color: #667eea;
  margin-bottom: 0.75rem;
}

.step h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.6rem 0;
}

.step p {
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

.step-arrow {
  color: #cbd5e1;
  font-size: 1.25rem;
  padding-top: 3.5rem;
  flex-shrink: 0;
}

/* ── Features grid ────────────────────────────────── */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 1.75rem;
  border: 1px solid #e2e8f0;
}

.feature-icon {
  font-size: 1.75rem;
  color: #667eea;
  margin-bottom: 1rem;
  display: block;
}

.feature-card h3 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.feature-card p {
  font-size: 0.9rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

/* ── Platforms ────────────────────────────────────── */
.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.platform-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
}

.platform-logo {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  margin: 0 auto 1.25rem;
  font-weight: 700;
}

.platform-logo--youtube   { background: #FF0000; }
.platform-logo--tiktok    { background: #000000; }
.platform-logo--instagram { background: linear-gradient(45deg, #f09433, #dc2743, #bc1888); }

.platform-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.6rem 0;
}

.platform-card p {
  font-size: 0.9rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

/* ── CTA section ──────────────────────────────────── */
.section--cta {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.cta-inner h2 {
  font-size: clamp(1.75rem, 3vw, 2.25rem);
  font-weight: 700;
  margin: 0 0 0.75rem 0;
  color: white;
}

.cta-inner p {
  color: rgba(255, 255, 255, 0.85);
  font-size: 1.05rem;
  margin: 0 0 2rem 0;
}

/* ── Responsive ───────────────────────────────────── */
@media (max-width: 768px) {
  .hero { padding: 3.5rem 1.25rem; }
  .section { padding: 3.5rem 1.25rem; }

  .steps {
    flex-direction: column;
    align-items: center;
  }

  .step { max-width: 100%; }
  .step-arrow { display: none; }

  .nav-inner { padding: 0.75rem 1.25rem; }
}
</style>
