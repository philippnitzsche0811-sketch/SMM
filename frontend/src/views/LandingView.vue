<template>
  <div class="landing">

    <!-- Nav -->
    <nav class="nav" :class="{ scrolled: isScrolled }">
      <div class="nav-inner">
        <div class="nav-logo">
          <img :src="logoUrl" alt="Decodu-SMM" class="nav-logo-img" />
          <span>Decodu-SMM</span>
        </div>
        <div class="nav-links">
          <button class="btn-ghost" @click="router.push('/login')">Sign In</button>
          <button class="btn-primary" @click="router.push('/register')">Get Started</button>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-glow hero-glow--left"></div>
      <div class="hero-glow hero-glow--right"></div>
      <div class="hero-inner">
        <div class="hero-pill anim-fadeup" style="--delay:0s">
          <span class="pill-dot"></span>
          Smart publishing. Maximum reach.
        </div>
        <h1 class="anim-fadeup" style="--delay:0.1s">
          Publish smarter.<br><span class="accent">Grow faster.</span>
        </h1>
        <p class="hero-sub anim-fadeup" style="--delay:0.2s">
          Decodu-SMM publishes your videos to YouTube, TikTok, and Instagram simultaneously —
          and helps you maximize reach with AI-optimized content, smart upload timing, and
          cross-platform analytics. All from one dashboard.
        </p>
        <div class="hero-cta anim-fadeup" style="--delay:0.3s">
          <button class="btn-primary btn-lg" @click="router.push('/register')">
            <i class="pi pi-user-plus"></i> Create free account
          </button>
          <button class="btn-outline btn-lg" @click="router.push('/login')">
            <i class="pi pi-sign-in"></i> Sign in
          </button>
        </div>
        <div class="hero-platforms anim-fadeup" style="--delay:0.4s">
          <span class="platform-pill platform-pill--youtube"><i class="pi pi-youtube"></i> YouTube</span>
          <span class="platform-pill platform-pill--tiktok"><i class="pi pi-video"></i> TikTok</span>
          <span class="platform-pill platform-pill--instagram"><i class="pi pi-instagram"></i> Instagram</span>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="section section--glow-right">
      <div class="section-glow section-glow--right"></div>
      <div class="section-inner">
        <div class="section-label">How it works</div>
        <h2 class="section-title">From upload to growth — in three steps</h2>
        <p class="section-sub">Connect your accounts once, then let Decodu-SMM handle publishing, optimization, and reach.</p>
        <div class="steps-grid">
          <div v-for="step in steps" :key="step.num" class="step-card">
            <div class="step-num">{{ step.num }}</div>
            <div class="step-icon-wrap"><i :class="step.icon"></i></div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="section section--alt">
      <div class="section-inner">
        <div class="section-label">Features</div>
        <h2 class="section-title">Built to grow your reach</h2>
        <p class="section-sub">Every feature is designed to save time and maximize the impact of every upload.</p>
        <div class="features-grid">
          <div v-for="feat in features" :key="feat.title" class="feature-card">
            <div class="feature-icon-wrap"><i :class="feat.icon"></i></div>
            <h3>{{ feat.title }}</h3>
            <p>{{ feat.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Platforms -->
    <section class="section section--glow-left">
      <div class="section-glow section-glow--left"></div>
      <div class="section-inner">
        <div class="section-label">Platforms</div>
        <h2 class="section-title">Supported platforms</h2>
        <p class="section-sub">Native API integrations — no third-party bridges, no data sharing. Your content goes directly to each platform.</p>
        <div class="platforms-grid">
          <div
            v-for="p in platforms"
            :key="p.name"
            class="platform-card"
            :class="p.cls"
          >
            <div class="platform-icon-wrap">
              <i :class="p.icon"></i>
            </div>
            <h3>{{ p.name }}</h3>
            <p>{{ p.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="cta-glow"></div>
      <div class="section-inner cta-inner">
        <h2>Ready to grow your audience?</h2>
        <p>Create a free account, connect your first platform, and start publishing smarter — in under 2 minutes.</p>
        <button class="btn-primary btn-lg" @click="router.push('/register')">
          Get started for free <i class="pi pi-arrow-right"></i>
        </button>
      </div>
    </section>

    <LegalFooter dark />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import LegalFooter from '@/components/layout/LegalFooter.vue';
import logoUrl from '@/assets/images/logo.png';

const router = useRouter();
const isScrolled = ref(false);

const onScroll = () => { isScrolled.value = window.scrollY > 40; };
onMounted(()   => window.addEventListener('scroll', onScroll, { passive: true }));
onUnmounted(() => window.removeEventListener('scroll', onScroll));

const steps = [
  {
    num: '01',
    icon: 'pi pi-link',
    title: 'Connect your accounts',
    desc:  'Link YouTube, TikTok, and Instagram once via secure OAuth. No passwords stored — revoke access anytime.',
  },
  {
    num: '02',
    icon: 'pi pi-sparkles',
    title: 'Optimize with AI',
    desc:  'Let AI suggest platform-optimized titles, descriptions, and hashtags. Find the best posting time based on platform data and your audience.',
  },
  {
    num: '03',
    icon: 'pi pi-chart-line',
    title: 'Publish & grow',
    desc:  'Hit upload once — all selected platforms publish simultaneously. Track views, reach, and performance across every channel in one dashboard.',
  },
];

const features = [
  { icon: 'pi pi-share-alt',  title: 'Multi-platform publishing', desc: 'Post to YouTube, TikTok, and Instagram Reels simultaneously — one upload, full coverage.' },
  { icon: 'pi pi-sparkles',   title: 'AI content optimizer',      desc: 'AI-generated titles, descriptions, and hashtags tailored to each platform\'s algorithm.' },
  { icon: 'pi pi-clock',      title: 'Smart upload timing',       desc: 'Publish when your audience is most active. Platform data and upload history determine the optimal time.' },
  { icon: 'pi pi-chart-bar',  title: 'Performance analytics',     desc: 'Track views, reach, and engagement across all platforms in one unified dashboard.' },
  { icon: 'pi pi-eye',        title: 'Privacy control',           desc: 'Choose public, unlisted, or private independently for each platform before every upload.' },
  { icon: 'pi pi-shield',     title: 'Secure by design',          desc: 'OAuth 2.0 only. Tokens are encrypted at rest. No passwords ever stored.' },
];

const platforms = [
  {
    name: 'YouTube',
    icon: 'pi pi-youtube',
    cls:  'platform-card--youtube',
    desc: 'Upload to your channel with AI-optimized titles and descriptions. Supports public, unlisted, and private — automatic token refresh keeps your connection alive.',
  },
  {
    name: 'TikTok',
    icon: 'pi pi-video',
    cls:  'platform-card--tiktok',
    desc: 'Post via the official Content Posting API with trending hashtag suggestions and optimal timing. Control duet, stitch, and comment settings per upload.',
  },
  {
    name: 'Instagram',
    icon: 'pi pi-instagram',
    cls:  'platform-card--instagram',
    desc: 'Publish Reels via the Meta Graph API. AI-generated captions, hashtag recommendations, and best-time publishing for maximum Reels reach.',
  },
];
</script>

<style scoped>
/* ── Base ── */
.landing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0b0b0f;
  color: #e2e8f0;
  font-family: 'Inter', -apple-system, sans-serif;
}

/* ── Fade-up animation ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(22px); }
  to   { opacity: 1; transform: translateY(0); }
}
.anim-fadeup {
  animation: fadeUp 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: var(--delay, 0s);
}

/* ── Nav ── */
.nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: transparent;
  border-bottom: 1px solid transparent;
  transition: background 0.3s ease, backdrop-filter 0.3s ease, border-color 0.3s ease;
}
.nav.scrolled {
  background: rgba(11, 11, 15, 0.88);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-bottom-color: rgba(255, 255, 255, 0.06);
}

.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-family: 'Poppins', sans-serif;
  font-size: 1.075rem;
  font-weight: 700;
  color: #f1f5f9;
}

.nav-logo-img {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  object-fit: contain;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* ── Buttons ── */
.btn-ghost {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: color 0.2s, background 0.2s;
  font-family: inherit;
}
.btn-ghost:hover { color: #f1f5f9; background: rgba(255,255,255,0.06); }

.btn-primary {
  background: #4f7fff;
  color: #fff;
  border: none;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.5625rem 1.25rem;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  transition: background 0.2s, box-shadow 0.2s, transform 0.15s;
  font-family: inherit;
}
.btn-primary:hover {
  background: #3b6ee8;
  box-shadow: 0 0 22px rgba(79, 127, 255, 0.38);
  transform: translateY(-1px);
}

.btn-outline {
  background: transparent;
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.14);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.5625rem 1.25rem;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
  font-family: inherit;
}
.btn-outline:hover {
  border-color: rgba(255,255,255,0.28);
  color: #f1f5f9;
  background: rgba(255,255,255,0.04);
}

.btn-lg {
  padding: 0.8125rem 1.875rem;
  font-size: 1rem;
  border-radius: 10px;
}

/* ── Hero ── */
.hero {
  position: relative;
  padding: 10rem 2rem 7rem;
  text-align: center;
  overflow: hidden;
}

.hero-glow {
  position: absolute;
  width: 640px;
  height: 640px;
  border-radius: 50%;
  filter: blur(130px);
  pointer-events: none;
}
.hero-glow--left  { background: rgba(79, 127, 255, 0.17); top: -80px; left: -220px; }
.hero-glow--right { background: rgba(139, 92, 246, 0.12); top: -40px; right: -220px; }

.hero-inner {
  max-width: 780px;
  margin: 0 auto;
  position: relative;
}

.hero-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 1rem 0.35rem 0.5rem;
  border: 1px solid rgba(79, 127, 255, 0.3);
  border-radius: 99px;
  font-size: 0.8rem;
  font-weight: 500;
  color: #93c5fd;
  background: rgba(79, 127, 255, 0.08);
  margin-bottom: 1.875rem;
}
.pill-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4f7fff;
  box-shadow: 0 0 6px #4f7fff;
  flex-shrink: 0;
}

.hero h1 {
  font-family: 'Poppins', sans-serif;
  font-size: clamp(2.5rem, 6vw, 4.25rem);
  font-weight: 800;
  line-height: 1.08;
  letter-spacing: -0.035em;
  color: #f8fafc;
  margin: 0 0 1.375rem;
}
.accent { color: #4f7fff; }

.hero-sub {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #64748b;
  margin: 0 0 2.625rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-cta {
  display: flex;
  justify-content: center;
  gap: 0.875rem;
  flex-wrap: wrap;
  margin-bottom: 2.75rem;
}

.hero-platforms {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.platform-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.75rem;
  border-radius: 99px;
  font-size: 0.78rem;
  font-weight: 500;
  border: 1px solid transparent;
}
.platform-pill--youtube   { background: rgba(239,68,68,0.1);  color: #fca5a5; border-color: rgba(239,68,68,0.22); }
.platform-pill--tiktok    { background: rgba(255,255,255,0.05); color: #cbd5e1; border-color: rgba(255,255,255,0.1); }
.platform-pill--instagram { background: rgba(225,48,108,0.1); color: #f9a8d4; border-color: rgba(225,48,108,0.22); }

/* ── Sections ── */
.section { padding: 6rem 2rem; position: relative; overflow: hidden; }
.section--alt { background: rgba(255,255,255,0.018); }

/* Section gradient orbs */
.section-glow {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  filter: blur(130px);
  pointer-events: none;
}
.section-glow--right {
  background: rgba(79,127,255,0.09);
  top: -100px;
  right: -180px;
}
.section-glow--left {
  background: rgba(139,92,246,0.08);
  bottom: -100px;
  left: -180px;
}

.section-inner {
  max-width: 1100px;
  margin: 0 auto;
}

.section-label {
  display: block;
  text-align: center;
  font-size: 0.72rem;
  font-weight: 700;
  color: #4f7fff;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.section-title {
  font-family: 'Poppins', sans-serif;
  font-size: clamp(1.75rem, 3vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #f1f5f9;
  text-align: center;
  margin: 0 0 0.75rem;
}

.section-sub {
  text-align: center;
  color: #64748b;
  font-size: 1rem;
  margin: 0 0 3.5rem;
}

/* ── Steps ── */
.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.step-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px;
  padding: 2rem 1.75rem;
  text-align: center;
  transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
}
.step-card:hover {
  border-color: rgba(79,127,255,0.35);
  box-shadow: 0 0 32px rgba(79,127,255,0.1);
  transform: translateY(-5px);
}

.step-num {
  font-family: 'Poppins', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  color: #4f7fff;
  letter-spacing: 0.06em;
  margin-bottom: 1.25rem;
}

.step-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(79,127,255,0.1);
  border: 1px solid rgba(79,127,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.25rem;
  font-size: 1.25rem;
  color: #4f7fff;
}

.step-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 0.625rem;
}
.step-card p {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.65;
  margin: 0;
}

/* ── Features ── */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.feature-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 1.625rem 1.5rem;
  transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
}
.feature-card:hover {
  border-color: rgba(79,127,255,0.25);
  box-shadow: 0 0 22px rgba(79,127,255,0.08);
  transform: translateY(-3px);
}

.feature-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(79,127,255,0.1);
  border: 1px solid rgba(79,127,255,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  font-size: 1.05rem;
  color: #4f7fff;
}

.feature-card h3 {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 0.375rem;
}
.feature-card p {
  font-size: 0.85rem;
  color: #64748b;
  line-height: 1.65;
  margin: 0;
}

/* ── Platforms ── */
.platforms-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.platform-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
}

.platform-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.375rem;
  font-size: 1.4rem;
}

/* Platform-specific colors */
.platform-card--youtube .platform-icon-wrap {
  background: rgba(239,68,68,0.12);
  border: 1px solid rgba(239,68,68,0.25);
  color: #f87171;
}
.platform-card--youtube:hover {
  border-color: rgba(239,68,68,0.3);
  box-shadow: 0 0 28px rgba(239,68,68,0.1);
  transform: translateY(-5px);
}

.platform-card--tiktok .platform-icon-wrap {
  background: rgba(200,200,200,0.08);
  border: 1px solid rgba(200,200,200,0.15);
  color: #e2e8f0;
}
.platform-card--tiktok:hover {
  border-color: rgba(255,255,255,0.2);
  box-shadow: 0 0 28px rgba(255,255,255,0.05);
  transform: translateY(-5px);
}

.platform-card--instagram .platform-icon-wrap {
  background: rgba(225,48,108,0.12);
  border: 1px solid rgba(225,48,108,0.25);
  color: #f9a8d4;
}
.platform-card--instagram:hover {
  border-color: rgba(225,48,108,0.3);
  box-shadow: 0 0 28px rgba(225,48,108,0.1);
  transform: translateY(-5px);
}

.platform-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 0.5rem;
}
.platform-card p {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.65;
  margin: 0;
}

/* ── CTA section ── */
.cta-section {
  position: relative;
  padding: 7rem 2rem;
  text-align: center;
  overflow: hidden;
}
.cta-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 80% at 50% 50%, rgba(79,127,255,0.12) 0%, transparent 70%);
  pointer-events: none;
}
.cta-inner { position: relative; }
.cta-inner h2 {
  font-family: 'Poppins', sans-serif;
  font-size: clamp(1.75rem, 3.5vw, 2.75rem);
  font-weight: 700;
  letter-spacing: -0.028em;
  color: #f1f5f9;
  margin: 0 0 0.875rem;
}
.cta-inner p {
  color: #64748b;
  font-size: 1rem;
  margin: 0 0 2.25rem;
}

/* ── Legal footer ── */
:deep(.legal-footer) {
  background: #0b0b0f;
  border-top: 1px solid rgba(255,255,255,0.06);
}
:deep(.legal-footer a)       { color: #334155; }
:deep(.legal-footer a:hover) { color: #64748b; }
:deep(.legal-footer .dot)    { color: #1e293b; }

/* ── Responsive ── */
@media (max-width: 900px) {
  .steps-grid, .features-grid, .platforms-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .hero    { padding: 7.5rem 1.25rem 4.5rem; }
  .section { padding: 4rem 1.25rem; }
  .cta-section { padding: 5rem 1.25rem; }

  .steps-grid, .features-grid, .platforms-grid {
    grid-template-columns: 1fr;
  }

  .nav-inner { padding: 0.875rem 1.25rem; }
  .hero h1   { font-size: 2.25rem; }
  .hero-sub  { font-size: 1rem; }
}
</style>
