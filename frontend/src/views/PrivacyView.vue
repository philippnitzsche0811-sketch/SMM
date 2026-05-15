<template>
  <div class="legal-page">
    <div class="legal-container">
      <div class="app-brand">
        <img :src="logoUrl" alt="Decodu-SMM" class="brand-logo" />
        <span class="brand-name">Decodu-SMM</span>
      </div>

      <h1>Privacy Policy</h1>

      <section>
        <h2>1. Information We Collect</h2>
        <p>When you use Decodu-SMM, we collect:</p>
        <ul>
          <li><strong>Account Information:</strong> Email address (for authentication and account management)</li>
          <li><strong>Platform Tokens:</strong> OAuth access tokens for YouTube, TikTok, and Instagram — stored encrypted at rest</li>
          <li><strong>Video Metadata:</strong> Titles, descriptions, hashtags, and privacy settings you enter</li>
          <li><strong>Upload History:</strong> Records of uploaded videos and their platform status</li>
          <li><strong>Performance Data:</strong> View counts, like counts, comment counts, and shares fetched from connected platforms on your request</li>
          <li><strong>Comments:</strong> Comments on your Instagram posts, fetched on your request for analysis within the app</li>
        </ul>
      </section>

      <section>
        <h2>2. How We Use Your Data</h2>
        <p>Your data is used exclusively to provide the Decodu-SMM service:</p>
        <ul>
          <li>Authenticating with social media platforms on your behalf</li>
          <li>Publishing video content to platforms you select</li>
          <li>Displaying performance analytics (views, likes, comments) for your own posts</li>
          <li>Showing comments from your own Instagram posts so you can filter questions and ideas</li>
          <li>Maintaining your upload history</li>
          <li>Providing customer support</li>
        </ul>
        <p>We only access data from your connected accounts that is necessary for the features above. We do not read or store data about accounts you do not own.</p>
      </section>

      <section>
        <h2>3. What We DO NOT Do</h2>
        <p><strong>We NEVER:</strong></p>
        <ul>
          <li>Sell your data or Platform Data to third parties</li>
          <li>Use Platform Data for advertising, profiling, or data brokering</li>
          <li>Share your OAuth tokens or credentials with any third party</li>
          <li>Access social media content beyond what is required for the features described above</li>
          <li>Use your content or data to train AI models</li>
          <li>Transfer Platform Data to data brokers or ad networks</li>
        </ul>
      </section>

      <section>
        <h2>4. Meta / Instagram Platform Data</h2>
        <p>Decodu-SMM uses the Instagram Graph API and requests the following permissions:</p>
        <ul>
          <li><strong>instagram_business_basic:</strong> Read your Instagram account ID and basic profile information to link your account.</li>
          <li><strong>instagram_business_content_publish:</strong> Publish Reels and videos to your Instagram account on your behalf.</li>
          <li><strong>instagram_manage_comments:</strong> Read comments on your own posts so you can view and filter them within the app.</li>
          <li><strong>instagram_business_manage_insights:</strong> Read reach, impressions, plays, and engagement metrics for your own posts.</li>
        </ul>
        <p>All data received via these permissions is used solely to display information to you within the app and is never shared or sold. Comments and insights data is fetched on demand and not permanently stored.</p>
        <p>You can revoke these permissions at any time via your Instagram account settings. When you revoke access or delete your Decodu-SMM account, all associated tokens and data are immediately deleted from our servers.</p>

        <h3 style="margin-top:1rem;font-size:1.1rem;color:#334155;">Data Deletion Request</h3>
        <p>If you remove Decodu-SMM from your connected Instagram apps, Meta will automatically send us a deletion request and all data linked to your Instagram account will be deleted. You can also submit a manual deletion request by emailing <a href="mailto:privacy@decodu-smm.com" style="color:#667eea">privacy@decodu-smm.com</a>.</p>
      </section>

      <section>
        <h2>5. Data Retention</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Data Type</th>
              <th>Retention Period</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>OAuth Tokens (all platforms)</td>
              <td>Until you disconnect the platform or delete your account</td>
            </tr>
            <tr>
              <td>Video files</td>
              <td>Deleted immediately after successful upload to the platform</td>
            </tr>
            <tr>
              <td>Upload history &amp; metadata</td>
              <td>Until you delete the video record or your account</td>
            </tr>
            <tr>
              <td>Performance stats (views, likes)</td>
              <td>Cached for up to 24 hours; deleted when account is deleted</td>
            </tr>
            <tr>
              <td>Comments data (Instagram)</td>
              <td>Fetched on demand, not permanently stored</td>
            </tr>
            <tr>
              <td>Error logs</td>
              <td>Maximum 30 days</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section>
        <h2>6. Third-Party Services</h2>
        <p>This service integrates with the following platforms. Your use of those platforms is governed by their own privacy policies:</p>
        <ul>
          <li><strong>YouTube (Google):</strong> <a href="https://policies.google.com/privacy" target="_blank" rel="noopener" style="color:#667eea">Google Privacy Policy</a></li>
          <li><strong>TikTok:</strong> <a href="https://www.tiktok.com/legal/page/us/privacy-policy" target="_blank" rel="noopener" style="color:#667eea">TikTok Privacy Policy</a></li>
          <li><strong>Instagram / Meta:</strong> <a href="https://privacycenter.instagram.com/policy" target="_blank" rel="noopener" style="color:#667eea">Meta Privacy Policy</a></li>
        </ul>
        <p>Decodu-SMM's use of data received from Meta APIs complies with <a href="https://developers.facebook.com/terms/" target="_blank" rel="noopener" style="color:#667eea">Meta's Platform Terms</a> and <a href="https://developers.facebook.com/devpolicy/" target="_blank" rel="noopener" style="color:#667eea">Developer Policies</a>.</p>
      </section>

      <section>
        <h2>7. Data Security</h2>
        <p>We implement the following security measures:</p>
        <ul>
          <li>Encrypted storage of all OAuth tokens (AES encryption at rest)</li>
          <li>HTTPS (TLS) for all data transmission</li>
          <li>Secure OAuth 2.0 authentication flows</li>
          <li>Access control: users can only access their own data</li>
          <li>No plaintext passwords stored (bcrypt hashing)</li>
          <li>Rate limiting on all authentication endpoints</li>
        </ul>
      </section>

      <section>
        <h2>8. Your Rights (GDPR)</h2>
        <p>As a user in the EU / EEA, you have the following rights:</p>
        <ul>
          <li><strong>Right of Access:</strong> Request a copy of all data we hold about you</li>
          <li><strong>Right to Rectification:</strong> Correct inaccurate personal data</li>
          <li><strong>Right to Erasure:</strong> Delete your account and all associated data at any time via Settings → Delete Account, or by emailing privacy@decodu-smm.com</li>
          <li><strong>Right to Data Portability:</strong> Request an export of your data</li>
          <li><strong>Right to Withdraw Consent:</strong> Disconnect any platform at any time — tokens are immediately deleted</li>
          <li><strong>Right to Object:</strong> Object to any processing of your personal data</li>
        </ul>
        <p>To exercise any right, contact us at <a href="mailto:privacy@decodu-smm.com" style="color:#667eea">privacy@decodu-smm.com</a>. We respond within 30 days.</p>
      </section>

      <section>
        <h2>9. Contact &amp; Data Requests</h2>
        <p>Data Controller: Decodu-SMM</p>
        <p><strong>Privacy email:</strong> <a href="mailto:privacy@decodu-smm.com" style="color:#667eea">privacy@decodu-smm.com</a></p>
        <p><strong>Support:</strong> <a href="mailto:support@decodu-smm.com" style="color:#667eea">support@decodu-smm.com</a></p>
      </section>

      <div class="last-updated">
        Last updated: May 2026
      </div>

      <LegalFooter class="footer-in-page" />
    </div>
  </div>
</template>

<script setup lang="ts">
import LegalFooter from '@/components/layout/LegalFooter.vue';
import logoUrl from '@/assets/images/logo.png';
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

.app-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.5rem;
}

.brand-logo {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: contain;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #667eea;
}

.last-updated {
  margin-top: 3rem;
  padding-top: 2rem;
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
