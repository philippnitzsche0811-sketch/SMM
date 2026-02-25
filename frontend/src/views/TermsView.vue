<template>
  <div class="legal-page">
    <div class="legal-container">
      <h1>Terms of Service</h1>
      
      <section>
        <h2>1. Acceptance of Terms</h2>
        <p>
          By accessing and using this Social Media Upload Tool ("Service"), you accept and agree to be bound by these terms. 
          If you do not agree, please do not use this Service.
        </p>
      </section>

      <section>
        <h2>2. Your Responsibilities</h2>
        <p>
          This Service allows you to upload content to various social media platforms. You are responsible for:
        </p>
        <ul>
          <li>Ensuring you have the rights to upload and distribute your content</li>
          <li>Complying with each platform's terms of service (YouTube, TikTok, Instagram)</li>
          <li>The content you upload - no illegal, harmful, or copyrighted material</li>
          <li>Keeping your account credentials secure</li>
        </ul>
      </section>

      <section>
        <h2>3. Platform Connections</h2>
        <p>
          When you connect your social media accounts:
        </p>
        <ul>
          <li>You grant us permission to upload videos on your behalf</li>
          <li>We securely store OAuth tokens to maintain the connection</li>
          <li>You can disconnect platforms at any time from your settings</li>
          <li>We never access or modify your existing content on these platforms</li>
        </ul>
      </section>

      <section>
        <h2>4. Content Ownership</h2>
        <p>
          You retain all ownership rights to your content. This Service only acts as a technical tool 
          to facilitate uploads to your connected accounts.
        </p>
      </section>

      <section>
        <h2>5. Prohibited Uses</h2>
        <p>You may NOT use this Service to:</p>
        <ul>
          <li>Upload copyrighted material without permission</li>
          <li>Upload illegal, harmful, or offensive content</li>
          <li>Spam or abuse platform upload limits</li>
          <li>Attempt to gain unauthorized access to other users' accounts</li>
          <li>Reverse engineer or compromise the Service</li>
        </ul>
      </section>

      <section>
        <h2>6. Service Availability</h2>
        <p>
          We strive to maintain service availability but do not guarantee uninterrupted access. 
          The Service is provided "as is" without warranties of any kind.
        </p>
      </section>

      <section>
        <h2>7. Limitation of Liability</h2>
        <p>This Service is not liable for:</p>
        <ul>
          <li>Failed uploads due to platform API limitations</li>
          <li>Content moderation decisions by third-party platforms</li>
          <li>Loss of data due to technical issues</li>
          <li>Violations of third-party terms of service</li>
        </ul>
      </section>

      <section>
        <h2>8. Changes to Terms</h2>
        <p>
          We reserve the right to modify these terms at any time. Continued use after changes 
          constitutes acceptance of the new terms.
        </p>
      </section>

      <section>
        <h2>9. Contact</h2>
        <p>For questions about these Terms:</p>
        <p><strong>Email:</strong> philippnitzsche0811@gmail.com</p>
      </section>

      <div class="last-updated">
        Last updated: February 2026
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Static page - no logic needed
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
  margin-bottom: 2.5rem;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 1rem;
}

p {
  font-size: 1rem;
  line-height: 1.8;
  color: #64748b;
  margin-bottom: 1rem;
}

ul {
  margin-left: 1.5rem;
  margin-top: 0.5rem;
}

li {
  font-size: 1rem;
  line-height: 1.8;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.last-updated {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
  color: #94a3b8;
  font-size: 0.875rem;
  text-align: center;
}

@media (max-width: 768px) {
  .legal-container {
    padding: 2rem 1.5rem;
  }

  h1 {
    font-size: 2rem;
  }

  h2 {
    font-size: 1.25rem;
  }
}
</style>
