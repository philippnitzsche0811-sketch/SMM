<template>
  <div class="legal-page">
    <div class="legal-container">
      <h1>Impressum</h1>

      <section>
        <h2>Angaben gemäß § 5 TMG</h2>
        <p>
          Philipp Nitzsche<br>
          Graugansstraße 10<br>
          70378 Stuttgart<br>
          Deutschland
        </p>
      </section>

      <section>
        <h2>Kontakt</h2>
        <p>
          E-Mail: support@decodu-smm.com
        </p>
      </section>

      <section>
        <h2>Hinweise zur Website</h2>
        <p>
          SocialHub ist ein privat betriebenes Tool zur Verwaltung von Social-Media-Uploads.
          Diese Website steht in keiner offiziellen Verbindung mit YouTube (Google LLC),
          TikTok (ByteDance Ltd.) oder Instagram (Meta Platforms, Inc.).
        </p>
      </section>

      <section>
        <h2>Haftungsausschluss</h2>
        <p>
          Trotz sorgfältiger inhaltlicher Kontrolle übernehmen wir keine Haftung für
          die Inhalte externer Links. Für den Inhalt der verlinkten Seiten sind
          ausschließlich deren Betreiber verantwortlich.
        </p>
      </section>

      <div class="last-updated">
        Stand: April 2026
      </div>

      <LegalFooter class="footer-in-page" />
    </div>
  </div>
</template>

<script setup lang="ts">
import LegalFooter from '@/components/layout/LegalFooter.vue';
</script>

<style scoped>
.legal-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
}

.legal-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 2rem;
  border-bottom: 3px solid #667eea;
  padding-bottom: 1rem;
}

section {
  margin-bottom: 2rem;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.75rem;
}

p {
  font-size: 1rem;
  line-height: 1.8;
  color: #64748b;
}

.last-updated {
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
  color: #94a3b8;
  font-size: 0.875rem;
  text-align: center;
}

.footer-in-page {
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .legal-container {
    padding: 2rem 1.5rem;
  }

  h1 {
    font-size: 2rem;
  }
}
</style>
