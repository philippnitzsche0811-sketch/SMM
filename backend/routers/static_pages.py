"""
Static Pages Router
Stellt Terms of Service und Privacy Policy bereit
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Static Pages"])


@router.get("/terms", response_class=HTMLResponse)
async def terms_of_service():
    """Terms of Service - Für TikTok App Registration"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Terms of Service</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                background: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: white;
                min-height: 100vh;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
                margin-bottom: 15px;
            }
            .meta {
                color: #7f8c8d;
                font-style: italic;
                margin-bottom: 30px;
            }
            ul {
                margin-left: 20px;
                margin-bottom: 15px;
            }
            li {
                margin-bottom: 8px;
            }
            footer {
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #ecf0f1;
                text-align: center;
                color: #95a5a6;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Terms of Service</h1>
            <p class="meta">Last updated: December 28, 2024</p>
            
            <h2>1. Acceptance of Terms</h2>
            <p>
                By accessing and using this Social Media Upload Tool ("Service"), you accept and agree 
                to be bound by these terms. If you do not agree, please do not use this Service.
            </p>
            
            <h2>2. Use of Service</h2>
            <p>This Service allows you to upload content to various social media platforms. You are responsible for:</p>
            <ul>
                <li>All content you upload through this Service</li>
                <li>Complying with each platform's terms of service</li>
                <li>Ensuring you have the rights to upload and distribute the content</li>
                <li>Not uploading illegal, harmful, or copyright-infringing content</li>
            </ul>
            
            <h2>3. Authentication & Data</h2>
            <p>When you connect your social media accounts:</p>
            <ul>
                <li>You grant this Service permission to upload content on your behalf</li>
                <li>Your authentication tokens are stored securely</li>
                <li>You can revoke access at any time through your account settings</li>
                <li>We do not store your passwords - only OAuth tokens</li>
            </ul>
            
            <h2>4. Content Ownership</h2>
            <p>
                You retain all ownership rights to your content. This Service only acts as a 
                technical tool to facilitate uploads to your connected accounts.
            </p>
            
            <h2>5. Prohibited Uses</h2>
            <p>You may NOT use this Service to:</p>
            <ul>
                <li>Upload spam, malicious, or harmful content</li>
                <li>Violate any applicable laws or regulations</li>
                <li>Infringe on intellectual property rights</li>
                <li>Distribute viruses, malware, or harmful code</li>
                <li>Impersonate others or misrepresent your identity</li>
            </ul>
            
            <h2>6. Service Availability</h2>
            <p>
                We strive to maintain service availability but do not guarantee uninterrupted access. 
                The Service is provided "as is" without warranties of any kind.
            </p>
            
            <h2>7. Limitation of Liability</h2>
            <p>This Service is not liable for:</p>
            <ul>
                <li>Failed uploads or data loss</li>
                <li>Account suspensions on connected platforms</li>
                <li>Third-party platform changes or outages</li>
                <li>Any damages arising from use of the Service</li>
            </ul>
            
            <h2>8. Changes to Terms</h2>
            <p>
                We reserve the right to modify these terms at any time. Continued use after 
                changes constitutes acceptance of the new terms.
            </p>
            
            <h2>9. Contact</h2>
            <p>
                For questions about these Terms:<br>
                <strong>Email:</strong> philippnitzsche0811@gmail.com
            </p>
            
            <footer>
                <a href="/privacy">Privacy Policy</a> | 
                <a href="/">Back to Home</a>
            </footer>
        </div>
    </body>
    </html>
    """


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    """Privacy Policy - Für TikTok App Registration"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Privacy Policy</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                background: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: white;
                min-height: 100vh;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
                margin-bottom: 15px;
            }
            h3 {
                color: #556677;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            .meta {
                color: #7f8c8d;
                font-style: italic;
                margin-bottom: 30px;
            }
            .highlight {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }
            ul {
                margin-left: 20px;
                margin-bottom: 15px;
            }
            li {
                margin-bottom: 8px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
            }
            th {
                background: #f8f9fa;
                font-weight: 600;
            }
            footer {
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #ecf0f1;
                text-align: center;
                color: #95a5a6;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Privacy Policy</h1>
            <p class="meta">Last updated: December 28, 2024</p>
            
            <div class="highlight">
                <strong>TL;DR:</strong> We only store what's necessary to operate the service. 
                No passwords, only OAuth tokens. Videos are deleted after upload.
            </div>
            
            <h2>1. Information We Collect</h2>
            
            <h3>1.1 Authentication Data</h3>
            <ul>
                <li><strong>OAuth Tokens:</strong> Access tokens to upload content on your behalf</li>
                <li><strong>Platform IDs:</strong> YouTube channel ID, TikTok open_id, Instagram user_id</li>
                <li><strong>NOT Collected:</strong> Passwords, email addresses, personal profile information</li>
            </ul>
            
            <h3>1.2 Content Data</h3>
            <ul>
                <li><strong>Videos:</strong> Temporarily stored during upload process only</li>
                <li><strong>Metadata:</strong> Titles, descriptions, tags you provide</li>
                <li><strong>Retention:</strong> Videos automatically deleted after successful upload</li>
            </ul>
            
            <h3>1.3 Technical Data</h3>
            <ul>
                <li>API request logs (for debugging and security)</li>
                <li>Error logs (to improve service reliability)</li>
                <li>No IP addresses or tracking cookies</li>
            </ul>
            
            <h2>2. How We Use Your Information</h2>
            <p>Your data is used exclusively for:</p>
            <ul>
                <li>Uploading content to your connected social media accounts</li>
                <li>Maintaining authentication with platforms</li>
                <li>Debugging and error handling</li>
            </ul>
            
            <p><strong>We DO NOT:</strong></p>
            <ul>
                <li>Sell or share your data with third parties</li>
                <li>Use your data for advertising or marketing</li>
                <li>Access your content beyond the upload process</li>
                <li>Track your activity across other websites</li>
            </ul>
            
            <h2>3. Data Storage & Security</h2>
            
            <h3>3.1 Storage</h3>
            <ul>
                <li><strong>OAuth Tokens:</strong> Stored in encrypted JSON files on server</li>
                <li><strong>Videos:</strong> Stored temporarily in isolated containers</li>
                <li><strong>Duration:</strong> Tokens until disconnected, videos deleted immediately after upload</li>
            </ul>
            
            <h3>3.2 Security Measures</h3>
            <ul>
                <li>HTTPS/TLS encryption for all connections</li>
                <li>OAuth 2.0 industry-standard authentication</li>
                <li>Automatic token refresh when expired</li>
                <li>Isolated Docker containers</li>
            </ul>
            
            <h2>4. Data Retention</h2>
            <table>
                <tr>
                    <th>Data Type</th>
                    <th>Retention Period</th>
                </tr>
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
            </table>
            
            <h2>5. Your Rights</h2>
            <ul>
                <li><strong>Access:</strong> Request information about stored data</li>
                <li><strong>Deletion:</strong> Disconnect platforms to delete tokens</li>
                <li><strong>Revocation:</strong> Revoke access via platform settings anytime</li>
                <li><strong>Portability:</strong> Request copy of your data</li>
            </ul>
            
            <h2>6. Third-Party Services</h2>
            <p>This Service connects to:</p>
            <ul>
                <li><strong>YouTube (Google):</strong> <a href="https://policies.google.com/privacy" target="_blank">Privacy Policy</a></li>
                <li><strong>TikTok:</strong> <a href="https://www.tiktok.com/legal/privacy-policy" target="_blank">Privacy Policy</a></li>
                <li><strong>Instagram (Meta):</strong> <a href="https://www.facebook.com/privacy/policy" target="_blank">Privacy Policy</a></li>
            </ul>
            
            <h2>7. GDPR Compliance</h2>
            <p>For EU users:</p>
            <ul>
                <li><strong>Legal Basis:</strong> Consent (you explicitly connect accounts)</li>
                <li><strong>Right to Erasure:</strong> Disconnect platforms to delete data</li>
                <li><strong>Data Portability:</strong> Contact us to export your data</li>
            </ul>
            
            <h2>8. Contact</h2>
            <p>
                For privacy questions or to exercise your rights:<br>
                <strong>Email:</strong> philippnitzsche0811@gmail.com<br>
                <strong>Support:</strong> philippnitzsche0811@gmail.com
            </p>
            
            <footer>
                <a href="/terms">Terms of Service</a> | 
                <a href="/">Back to Home</a>
            </footer>
        </div>
    </body>
    </html>
    """