<template>
  <div class="legal-page">
    <div class="legal-container">
      <h1>Privacy Policy</h1>
      
      <section>
        <h2>1. Information We Collect</h2>
        <p>When you use our Service, we collect:</p>
        <ul>
          <li><strong>Account Information:</strong> Email address (for authentication)</li>
          <li><strong>Platform Tokens:</strong> OAuth tokens for YouTube, TikTok, Instagram</li>
          <li><strong>Video Metadata:</strong> Titles, descriptions, tags, privacy settings</li>
          <li><strong>Upload History:</strong> Records of uploaded videos</li>
        </ul>
      </section>

      <section>
        <h2>2. How We Use Your Data</h2>
        <p>Your data is used exclusively for:</p>
        <ul>
          <li>Authenticating with social media platforms</li>
          <li>Uploading videos on your behalf</li>
          <li>Maintaining upload history</li>
          <li>Providing customer support</li>
        </ul>
      </section>

      <section>
        <h2>3. What We DO NOT Do</h2>
        <p><strong>We DO NOT:</strong></p>
        <ul>
          <li>Sell your data to third parties</li>
          <li>Access your existing social media content</li>
          <li>Share your videos with anyone</li>
          <li>Use your content for training or advertising</li>
        </ul>
      </section>

      <section>
        <h2>4. Data Retention</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Data Type</th>
              <th>Retention Period</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>OAuth Tokens</td>
              <td>Until you disconnect the platform</td>
            </tr>
            <tr>
              <td>Uploaded Videos</td>
              <td>Deleted immediately after upload</td>
            </tr>
            <tr>
              <td>Error Logs</td>
              <td>30 days maximum</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section>
        <h2>5. Third-Party Services</h2>
        <p>This Service connects to:</p>
        <ul>
          <li><strong>YouTube API:</strong> Governed by Google Privacy Policy</li>
          <li><strong>TikTok API:</strong> Governed by TikTok Privacy Policy</li>
          <li><strong>Instagram API:</strong> Governed by Meta Privacy Policy</li>
        </ul>
        <p>Your uploads to these platforms are subject to their respective privacy policies.</p>
      </section>

      <section>
        <h2>6. Data Security</h2>
        <p>We implement security measures including:</p>
        <ul>
          <li>Encrypted storage of OAuth tokens</li>
          <li>HTTPS for all data transmission</li>
          <li>Secure OAuth 2.0 authentication flows</li>
          <li>Regular security audits</li>
        </ul>
      </section>

      <section>
        <h2>7. Your Rights (GDPR)</h2>
        <p>For EU users:</p>
        <ul>
          <li><strong>Access:</strong> Request a copy of your data</li>
          <li><strong>Rectification:</strong> Correct inaccurate data</li>
          <li><strong>Erasure:</strong> Delete your account and all data</li>
          <li><strong>Data Portability:</strong> Export your data</li>
          <li><strong>Withdraw Consent:</strong> Disconnect platforms anytime</li>
        </ul>
      </section>

      <section>
        <h2>8. Contact & Data Requests</h2>
        <p>For privacy questions or to exercise your rights:</p>
        <p><strong>Email:</strong> philippnitzsche0811@gmail.com</p>
        <p><strong>Support:</strong> philippnitzsche0811@gmail.com</p>
      </section>

      <div class="last-updated">
        Last updated: February 2026
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Static page
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

strong {
  color: #334155;
  font-weight: 600;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border: 1px solid #e2e8f0;
}

.data-table th {
  background: #f8fafc;
  color: #334155;
  font-weight: 600;
}

.data-table td {
  color: #64748b;
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

  .data-table {
    font-size: 0.875rem;
  }

  .data-table th,
  .data-table td {
    padding: 0.5rem;
  }
}
</style>
