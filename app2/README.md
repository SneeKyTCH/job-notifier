# 📱 JobBoard - Aplicație Mobilă de Locuri de Muncă

O aplicație React Native modernă și funcțională pentru căutarea joburilor în toată România, construită cu Expo și gata pentru integrare cu backend-ul tău.

## 🚀 Funcționalități Principale

### 📋 Căutare și Filtrare Avansată
- **Search real-time** - Cauta după título, companie, tehnologii
- **Filtre multiple**:
  - Locație (București, Cluj, Timișoara, etc.)
  - Tip job (Full-time, Part-time, Contract, Remote)
  - Nivel experiență (Entry, Junior, Mid, Senior)
  - Tehnologii și skill-uri
  - Interval salarial
- **Sorting** - Sortare după relevanță, salariu, dată

### 💼 Detalii Job Complet
- Descriere detaliată
- Cerințe și beneficii
- Informații despre companie
- Numărul de candidați care au aplicat
- Linkuri directe pentru aplicare
- Distribuire pe social media

### ❤️ Joburi Salvate
- Salvare/Unsave rapid
- Gestionare joburi favorite
- Aplicare la mai multe joburi simultan
- Sincronizare cu backend

### 🔔 Notificări
- Alerte pentru joburi noi
- Notificări personalizate
- Gestionare preferințe

### 👤 Profil Utilizator
- Statistici aplicații
- Setări notificări
- CV și informații personale
- Historia aplicațiilor

### 📊 Joburi Similare
- Recomandări bazate pe job-ul curent
- Descoperire oportunități noi

## 📦 Instalare și Setup

### Prerequisite
- Node.js 16+ instalat
- npm sau yarn
- Expo CLI (`npm install -g expo-cli`)
- Un cont Expo (optional, pentru testing pe telefon)

### Pași de Setup

1. **Clonează/Copiază proiectul**
```bash
# Creează directorul proiectului
mkdir jobboard-app
cd jobboard-app
```

2. **Instalează dependențele**
```bash
npm install
# sau
yarn install
```

3. **Configurează API (Important!)**
   - Deschide `api/jobAPI.js`
   - Înlocuiește `API_BASE_URL` cu URL-ul real al backend-ului tău:
```javascript
const API_BASE_URL = 'https://your-api-domain.com/api';
```

4. **Startează aplicația**
```bash
# Pentru Expo Go (testare pe telefon)
npm start
# sau
expo start

# Pentru Android
npm run android

# Pentru iOS (macOS numai)
npm run ios

# Pentru web
npm run web
```

5. **Accesează din Expo Go**
   - Descarcă app-ul "Expo Go" pe telefon (iOS/Android)
   - Scanează QR code-ul afișat în terminal
   - App-ul se va încărca automat

## 🏗️ Structura Proiectului

```
jobboard-app/
├── App.js                 # Entry point
├── screens/
│   ├── HomeScreen.js      # Pagina principală
│   ├── SearchScreen.js    # Căutare avansată
│   ├── JobDetailScreen.js # Detalii job
│   ├── SavedJobsScreen.js # Joburi salvate
│   └── NotificationsScreen.js # Notificări și profil
├── components/
│   ├── JobCard.js         # Card pentru job
│   └── QuickFilters.js    # Filtre rapide
├── api/
│   └── jobAPI.js          # Service API
├── package.json           # Dependencies
└── README.md
```

## 🔌 Integrare Backend

### API Endpoints necesare

```
GET  /api/jobs                      - Lista joburi (cu filtre)
GET  /api/jobs/:id/similar          - Joburi similare
POST /api/user/saved-jobs           - Salvează job
DELETE /api/user/saved-jobs/:id     - Șterge job salvat
GET  /api/user/saved-jobs           - Joburi salvate
GET  /api/user/notifications        - Notificări
PATCH /api/user/notifications/:id   - Marchează citit
POST /api/user/applications         - Track aplicație
GET  /api/user/profile              - Profil utilizator
GET  /api/companies/:name           - Info companie
POST /api/user/job-alerts           - Creează alarmă
```

### Format Date Returnate

```json
{
  "id": 1,
  "title": "Senior React Developer",
  "company": "TechCorp",
  "location": "București",
  "salary": 7500,
  "jobType": "Full-time",
  "experienceLevel": "Senior",
  "postedDate": "2024-01-15",
  "description": "...",
  "requirements": ["..."],
  "benefits": ["..."],
  "technologies": ["React", "Node.js"],
  "applyUrl": "https://...",
  "recruiterEmail": "careers@techcorp.ro",
  "companyDescription": "...",
  "applicants": 45
}
```

## 🛠️ Configurare Backend

### Exemplu: Node.js + Express

```javascript
const express = require('express');
const app = express();

// Middleware
app.use(express.json());

// Jobs endpoints
app.get('/api/jobs', async (req, res) => {
  const { category, location, limit } = req.query;
  // Query database
  res.json({ jobs: jobsArray });
});

app.get('/api/jobs/:id/similar', async (req, res) => {
  const { id } = req.params;
  // Find similar jobs
  res.json({ jobs: similarJobs });
});

// Saved jobs
app.post('/api/user/saved-jobs', authenticateToken, async (req, res) => {
  const { jobId } = req.body;
  const userId = req.user.id;
  // Save to database
  res.json({ success: true });
});

// ... alte endpoints

app.listen(3000);
```

## 🎨 Customizare Styling

Stilurile sunt definite în `StyleSheet.create()` din fiecare screen. Schimbă colori, fonturi, spacing:

```javascript
const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f9fafb', // Schimbă culoare
    flex: 1,
  },
  // ...
});
```

Culori principale:
- `#2563eb` - Albastru (primary)
- `#059669` - Verde (success)
- `#dc2626` - Roșu (danger)
- `#111827` - Gri închis (text)

## 🚀 Deployment

### Pentru producție:
1. Testează pe dispozitiv real cu `expo build`
2. Creează build-uri:
```bash
expo build:android   # APK/AAB pentru Google Play
expo build:ios       # IPA pentru App Store
```

## 🐛 Troubleshooting

### App crashes la deschidere
- Verifică că API_BASE_URL este corect
- Asigură-te că Node.js version este 16+
- Șterge node_modules și reinstalează: `rm -rf node_modules && npm install`

### Nu se conectează la API
- Verifică că backend-ul rulează și este accesibil
- Testează URL-ul în browser
- Verifica CORS settings pe backend

### Saved jobs nu persist
- AsyncStorage necesită permisii pe iOS
- Verifica că app are acces la storage

## 📱 Testare cu Mock Data

App-ul vine cu mock data integrat. Dacă API nu e disponibil, va afișa:
- 3 job-uri de test
- Funcționalități complete (save, filter, etc.)
- Persistent storage cu AsyncStorage

## 🔒 Securitate

- Token JWT stocat în AsyncStorage
- HTTPS required pentru producție
- Validează input-uri pe backend
- Rate limiting pe API endpoints

## 📝 Notă Importantă

**Această aplicație este gata pentru integrare cu backend real.**

1. Conectează API-ul tău la variabila `API_BASE_URL` din `api/jobAPI.js`
2. Adaptează response format-ul din API la structura job-ului din mock data
3. Implementează autentificare și authorization

## 📞 Support

Contactează pentru asistență cu integrarea backend-ului sau orice probleme.

---

**Made with ❤️ for finding the perfect job**
