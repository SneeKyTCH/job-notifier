# 📋 GHID JOB NOTIFIER - Configurare Completă

## Ce face scriptul?
- Monitorizează 3 URL-uri (eJobs, OLX, remote jobs)
- Caută anunțuri noi în domenii de vânzări și call center
- Trimite email cu noile anunțuri
- Se poate rula automat (zilnic, orar, etc.)

---

## ⚙️ PASUL 1: Instalare Dependințe

### Pe Windows:
```bash
pip install requests beautifulsoup4
```

### Pe Mac/Linux:
```bash
pip3 install requests beautifulsoup4
```

---

## 🔐 PASUL 2: Setup Gmail (Foarte Important!)

### Dacă folosești Gmail:

1. **Mergi pe**: https://myaccount.google.com/apppasswords
2. **Selectează**:
   - Select app: **Mail**
   - Select device: **Windows Computer** (sau al tău)
3. **Copiază** parola generată (o vei folosi în script)
4. **Dacă nu găsești "App Passwords"**:
   - Activează Two-Factor Authentication mai întâi
   - Merge pe: https://myaccount.google.com/security

### Dacă folosești alt email (Outlook, Yahoo, etc.):
```
Outlook/Hotmail: smtp-mail.outlook.com:587 (TLS)
Yahoo: smtp.mail.yahoo.com:465 (SSL)
```

---

## 📝 PASUL 3: Configurare Script

Deschide fișierul `job_notifier.py` și modifică doar aceste 3 linii:

```python
EMAIL_TAU = "emailul.tau@gmail.com"      # ← Schimbă cu email-ul tău
EMAIL_SMTP = "emailul.tau@gmail.com"      # ← La fel ca sus (dacă Gmail)
PAROLA_EMAIL = "parola_aplicatie"         # ← Parola generată de Google
```

### Exemplu:
```python
EMAIL_TAU = "ion.popescu@gmail.com"
EMAIL_SMTP = "ion.popescu@gmail.com"
PAROLA_EMAIL = "xyzabc defghijk lmnop"  # Parola generată de Google
```

---

## 🧪 PASUL 4: Test Script

Rulează scriptul pentru a testa:

### Windows (Command Prompt):
```bash
python job_notifier.py
```

### Mac/Linux (Terminal):
```bash
python3 job_notifier.py
```

**Ar trebui să vezi**:
```
============================================================
🔍 JOB NOTIFIER - Monitorizarea anunțurilor de job-uri
============================================================
⏰ Start: 02.06.2026 14:23:45

🌐 Procesez: https://www.ejobs.ro/locuri-de-munca/bacau
   └─ Găsite 5 anunțuri relevante

🌐 Procesez: https://www.olx.ro/locuri-de-munca/bacau/
   └─ Găsite 3 anunțuri relevante

...

📨 Au fost găsite 8 anunțuri noi!
📧 Se trimite email către emailul.tau@gmail.com...
✅ Email trimis cu succes! (8 joburi noi)
```

---

## ⏰ PASUL 5: Automatizare (Rulează Zilnic/Orar)

### OPȚIUNEA 1: WINDOWS (Task Scheduler) - CEL MAI UȘOR ✅

1. **Apasă**: `Windows + R`
2. **Tastează**: `taskschd.msc` și Enter
3. **Din meniu**: Action → Create Basic Task
4. **Nume**: "Job Notifier"
5. **Trigger**: "Daily" la ora pe care o vrei (ex: 08:00, 12:00, 16:00)
6. **Action**: 
   - Program: `python` (sau `python.exe`)
   - Arguments: `C:\cale\catre\job_notifier.py`
   - Start in: `C:\cale\catre\` (directorul unde e fișierul)

**Exemplu real**:
- Program: `C:\Users\Ion\AppData\Local\Programs\Python\Python311\python.exe`
- Arguments: `job_notifier.py`
- Start in: `C:\Users\Ion\Desktop\job_notifier`

### OPȚIUNEA 2: Mac/Linux (Cron)

1. **Deschide Terminal**
2. **Tastează**: `crontab -e`
3. **Adaugă o linie** (exemplu: ruleaza zilnic la 8:00):
```
0 8 * * * /usr/bin/python3 /home/utilizator/job_notifier.py
```

4. **Pentru mai des (la fiecare 2 ore)**:
```
0 */2 * * * /usr/bin/python3 /home/utilizator/job_notifier.py
```

---

## 📝 Personalizare Cuvinte Cheie

Deschide scriptul și modifică lista `KEYWORDS` dacă vrei alte domenii:

```python
KEYWORDS = [
    "vânzări", 
    "vânzare", 
    "call center", 
    "telefonist", 
    "agent vânzări",
    # Adaugă aici alte cuvinte dacă vrei
    "reprezentant comercial",
    "supervisor",
    "manager"
]
```

---

## 🔧 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'requests'"
**Soluție**: Rulează din nou instalarea
```bash
pip install requests beautifulsoup4
```

### ❌ "SMTP: Authentication failed"
**Soluție**: 
- Verifică că ai generat "App Password" corect
- Copiază din nou parola (nu scrie manual!)
- Asigură-te că ai Two-Factor Authentication activat

### ❌ "Connection timeout"
**Soluție**: Site-urile pot fi temporar inaccesibile. Scriptul va reîncerca data viitoare.

### ❌ "Nu primesc emailuri"
**Verifică**:
1. Spam/Junk folder
2. Ca EMAIL_TAU și EMAIL_SMTP sunt identice
3. Ca PAROLA_EMAIL e corect copiată

---

## 📊 Fișierul Cache

Scriptul creează `job_cache.json` - salvează anunțurile pe care le-a văzut.
- Nu-l șterge decât dacă vrei să primești notificări pentru TOATE anunțurile din nou
- Este actualizat automat după fiecare rulare

---

## 💡 Sfaturi

✅ **Test complet**: Rulează scriptul manual prima data  
✅ **Frecvență**: Recomand zilnic la 08:00, 12:00, 16:00  
✅ **Email**: Păstrează parola App Password secretă!  
✅ **Monitorizare**: Verifică logs-ul pentru erori  

---

## 🎯 Rezultatul Final

După configurare, vei primi emailuri automate cu joburi noi:

```
To: emailul.tau@gmail.com
Subject: 🔔 5 Joburi Noi - Bacău (02.06.2026)

🔔 Joburi Noi în Bacău!

Au fost găsite 5 anunțuri noi:

- Agent Vânzări - Bacău (eJobs) [Link]
- Call Center Representative - Bacău (OLX) [Link]
...
```

---

**Ai nevoie de ajutor? Rulează scriptul și observă mesajele de eroare!** 🚀
