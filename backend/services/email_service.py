import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service für Email-Versand"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Sendet eine Email
        
        Args:
            to_email: Empfänger Email
            subject: Betreff
            html_content: HTML Email Body
            text_content: Plain Text Fallback (optional)
        
        Returns:
            bool: True wenn erfolgreich
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text content
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)
            
            # Add HTML content
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"✅ Email gesendet an {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Email-Versand fehlgeschlagen: {str(e)}")
            return False
    
    def send_verification_email(self, to_email: str, verification_token: str) -> bool:
        """
        Sendet Verification Email
        
        Args:
            to_email: User Email
            verification_token: Verification Token
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        subject = "Bestätige deine Email-Adresse"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 Willkommen bei Social Media Manager!</h1>
            </div>
            <div class="content">
                <h2>Bestätige deine Email-Adresse</h2>
                <p>Vielen Dank für deine Registrierung! Bitte bestätige deine Email-Adresse, um deinen Account zu aktivieren.</p>
                
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">Email bestätigen</a>
                </p>
                
                <p>Oder kopiere diesen Link in deinen Browser:</p>
                <p style="background: #fff; padding: 10px; border-radius: 5px; word-break: break-all;">
                    {verification_url}
                </p>
                
                <p><strong>Dieser Link ist 24 Stunden gültig.</strong></p>
                
                <p>Falls du dich nicht registriert hast, ignoriere diese Email einfach.</p>
            </div>
            <div class="footer">
                <p>© 2026 Social Media Manager. Alle Rechte vorbehalten.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Willkommen bei Social Media Manager!
        
        Bestätige deine Email-Adresse:
        {verification_url}
        
        Dieser Link ist 24 Stunden gültig.
        
        Falls du dich nicht registriert hast, ignoriere diese Email.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Sendet Password Reset Email
        
        Args:
            to_email: User Email
            reset_token: Reset Token
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        subject = "Passwort zurücksetzen"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #f5576c;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔑 Passwort zurücksetzen</h1>
            </div>
            <div class="content">
                <h2>Passwort-Anfrage</h2>
                <p>Du hast eine Anfrage zum Zurücksetzen deines Passworts gestellt.</p>
                
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Neues Passwort setzen</a>
                </p>
                
                <p>Oder kopiere diesen Link in deinen Browser:</p>
                <p style="background: #fff; padding: 10px; border-radius: 5px; word-break: break-all;">
                    {reset_url}
                </p>
                
                <div class="warning">
                    <strong>⚠️ Wichtig:</strong>
                    <ul>
                        <li>Dieser Link ist 1 Stunde gültig</li>
                        <li>Der Link kann nur einmal verwendet werden</li>
                        <li>Falls du keine Anfrage gestellt hast, ignoriere diese Email</li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 Social Media Manager. Alle Rechte vorbehalten.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Passwort zurücksetzen
        
        Du hast eine Anfrage zum Zurücksetzen deines Passworts gestellt.
        
        Link zum Zurücksetzen:
        {reset_url}
        
        Dieser Link ist 1 Stunde gültig und kann nur einmal verwendet werden.
        
        Falls du keine Anfrage gestellt hast, ignoriere diese Email.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """
        Sendet Welcome Email nach erfolgreicher Verification
        """
        subject = "Willkommen! Dein Account ist aktiviert"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .feature {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 4px solid #667eea;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 Willkommen, {username}!</h1>
            </div>
            <div class="content">
                <h2>Dein Account ist jetzt aktiviert!</h2>
                <p>Schön, dass du dabei bist. Du kannst jetzt loslegen:</p>
                
                <div class="feature">
                    <strong>📹 Videos hochladen</strong><br>
                    Lade deine Videos auf mehrere Plattformen gleichzeitig hoch
                </div>
                
                <div class="feature">
                    <strong>🔗 Plattformen verbinden</strong><br>
                    Verbinde YouTube, TikTok und Instagram
                </div>
                
                <div class="feature">
                    <strong>📊 Analytics tracken</strong><br>
                    Behalte den Überblick über deine Uploads
                </div>
                
                <p style="text-align: center;">
                    <a href="{settings.FRONTEND_URL}/dashboard" class="button">Zum Dashboard</a>
                </p>
            </div>
            <div class="footer">
                <p>© 2026 Social Media Manager. Alle Rechte vorbehalten.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)
