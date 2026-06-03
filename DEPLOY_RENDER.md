# 🚀 Deploy pe Render - Job Notifier Backend

## Status: ✅ GATA PENTRU DEPLOY

Backend-ul a fost actualizat pentru a stoca și furniza **TOATE** joburile din site-uri, nu doar cele noi.

---

## 📋 Pasii pentru Deploy pe Render

### 1. **Push pe GitHub** (Necesar pentru Render)

```bash
# Creează un repository pe GitHub
# https://github.com/new

# Apoi rulează în folder-ul local:
git remote add origin https://github.com/USERNAME/job-notifier.git
git branch -M main
git push -u origin main
```

### 2. **Conectează GitHub la Render**

1. Mergi pe https://render.com
2. Click "New +" → "Web Service"
3. Conectează GitHub account (dacă nu e conectat)
4. Selectează repository-ul `job-notifier`
5. Completează setările:

**Setări Render:**
- **Name**: `job-notifier-api`
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -w 4 server:app` (sau `python server.py`)
- **Environment Variables**: (nu sunt necesare decât dacă modifici config)

### 3. **Așteptă Deploy-ul**

Render va:
1. Clona repository-ul
2. Instala dependințele din `requirements.txt`
3. Rula comanda din `Procfile`
4. Atribuie URL: `https://job-notifier-api-xxxxx.onrender.com`

### 4. **Actualizează URL în App**

După deploy, dacă URL-ul s-a schimbat, actualizează în `app/src/config.js`:

```javascript
export const API_URL = "https://job-notifier-api-xxxxx.onrender.com";
```

---

## 🔧 Configurare Port

Server.py citește `PORT` din variabila de mediu (pe Render: 10000-65000):
- Local: `PORT=5000`
- Render: `PORT` (dinamic)

---

## 📊 Ce se Deploy-ează

- ✅ `server.py` - Flask API cu endpoint `/jobs`
- ✅ `jobs_cache.json` - Cache persistent cu TOATE joburile
- ✅ `requirements.txt` - Dependencies
- ✅ `Procfile` - Instrucțiuni de start

---

## ⚠️ Observații

1. **Cache pe Render**: Joburile se reîncarc din cache la fiecare restart
2. **Actualizare automată**: Background thread-ul face scraping la fiecare 30 min
3. **CORS activat**: App-ul poate accesa API din orice domeniu
4. **Timeout**: Scraping timeout 25s pe request

---

## 🔄 Flux de date

```
Site-uri (eJobs, OLX) 
    ↓
server.py (scraping)
    ↓
jobs_cache.json (STOCHEAZĂ TOATE)
    ↓
/jobs endpoint
    ↓
App mobilă (afișează TOATE joburile)
```

---

## 📱 Endpoint API

```
GET https://job-notifier-api-xxxxx.onrender.com/jobs
```

**Response:**
```json
{
  "jobs": [
    {
      "id": "link-unic",
      "title": "Job Title",
      "company": "Company Name",
      "location": "Bacău",
      "source": "eJobs",
      "link": "https://..."
    },
    ...
  ],
  "total": 150,
  "last_update": "03.06.2026 14:23:45"
}
```

---

## ✅ Verificare Deploy

După deploy, testează în browser:
```
https://job-notifier-api-xxxxx.onrender.com/
https://job-notifier-api-xxxxx.onrender.com/jobs
```

Ar trebui să vadă JSON cu toate joburile!

---

## 🚨 Troubleshooting

**App nu găsește endpoint:**
- Verifică URL în `app/src/config.js`
- Verifica că Render server-ul este "On"

**"Port is already in use":**
- Render alocă port automat, nu necesită configurare manuală

**Cache gol:**
- Prima rulare scanează site-urile (poate lua 1-2 min)
- După aceea, TOATE joburile sunt în cache

---

## 🎯 Rezultat Final

✅ Backend pe cloud (Render)  
✅ App mobilă conectată la API  
✅ TOATE joburile din site-uri stocate persistent  
✅ Email-uri doar pentru joburi NOI  
✅ Actualizare automată la fiecare 30 min  

**Status: GATA PENTRU PRODUCȚIE! 🚀**

---

*Schimbări implementate:*
- `server.py`: Stochează TOATE joburile în `jobs_cache.json`
- `job_notifier.py`: Trimite emailuri doar pentru joburi NOI
- `requirements.txt`: Dependencies pentru deploy
- `Procfile`: Instrucțiuni Render
- `.gitignore`: Exclude fișiere nedorite

