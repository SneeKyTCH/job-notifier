#!/usr/bin/env python3
"""
Script de TEST - Trimite un email de test pentru a vedea formatarea
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ============== CONFIGURARE ==============
EMAIL_TAU = "theangelx1x@gmail.com"      # ← Schimbă cu email-ul tău
EMAIL_SMTP = "theangelx1x@gmail.com"     # ← Același email
PAROLA_EMAIL = "ftxl uryj fugd inxf"    # ← Parola Gmail-ului

# ============== FUNCȚIE TEST ==============

def send_test_email():
    """Trimite un email de test"""
    try:
        # HTML-ul emailului de test
        html_content = """
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #2c3e50; }
                    .job-item { 
                        border-left: 4px solid #3498db;
                        padding: 15px;
                        margin: 10px 0;
                        background: #ecf0f1;
                        border-radius: 4px;
                    }
                    .job-title { 
                        font-size: 16px; 
                        font-weight: bold;
                        color: #2980b9;
                    }
                    .job-link { 
                        color: #e74c3c;
                        text-decoration: none;
                    }
                    .job-source { 
                        color: #7f8c8d;
                        font-size: 12px;
                        margin-top: 5px;
                    }
                    .timestamp { 
                        color: #95a5a6;
                        font-size: 12px;
                    }
                </style>
            </head>
            <body>
                <h1>🔔 Joburi Noi în Bacău! (EMAIL DE TEST)</h1>
                <p class="timestamp">
                    Actualizat: """ + datetime.now().strftime('%d.%m.%Y %H:%M:%S') + """
                </p>
                <p>Acesta este un <strong>EMAIL DE TEST</strong> pentru a vedea formatarea.</p>
                
                <div class="job-item">
                    <div class="job-title">🧪 Agent Vânzări - Bacău (TEST)</div>
                    <a href="https://www.ejobs.ro/locuri-de-munca/bacau" class="job-link" target="_blank">
                        👉 Vezi anunțul complet
                    </a>
                    <div class="job-source">Sursa: eJobs</div>
                </div>
                
                <div class="job-item">
                    <div class="job-title">🧪 Call Center Representative - Bacău (TEST)</div>
                    <a href="https://www.olx.ro/locuri-de-munca/bacau/" class="job-link" target="_blank">
                        👉 Vezi anunțul complet
                    </a>
                    <div class="job-source">Sursa: OLX</div>
                </div>
                
                <div class="job-item">
                    <div class="job-title">🧪 Telefonist - Remote (TEST)</div>
                    <a href="https://www.ejobs.ro/locuri-de-munca/remote" class="job-link" target="_blank">
                        👉 Vezi anunțul complet
                    </a>
                    <div class="job-source">Sursa: eJobs Remote</div>
                </div>
                
                <hr>
                <p style="color: #7f8c8d; font-size: 12px;">
                    Acesta este un email de test. Scriptul funcționează corect! ✅
                </p>
            </body>
        </html>
        """
        
        # Construiește mesajul
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🧪 TEST EMAIL - Job Notifier (02.06.2026)"
        msg['From'] = EMAIL_SMTP
        msg['To'] = EMAIL_TAU
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Conectare și trimitere
        print("📧 Se trimite email de test către " + EMAIL_TAU + "...")
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SMTP, PAROLA_EMAIL)
        server.send_message(msg)
        server.quit()
        
        print("✅ Email de TEST trimis cu succes!")
        print("\n💡 Verifică inbox-ul și folder-ul de spam!")
        
    except Exception as e:
        print(f"❌ Eroare la trimiterea email-ului: {e}")
        print("\n⚠️  Verifică:")
        print("1. Email-ul și parola sunt scrise corect")
        print("2. Ești conectat la internet")
        print("3. Gmail-ul permite aplicații mai puțin sigure")
        print("   https://myaccount.google.com/u/0/security")

if __name__ == "__main__":
    print("="*60)
    print("🧪 TEST EMAIL - Job Notifier")
    print("="*60 + "\n")
    send_test_email()
