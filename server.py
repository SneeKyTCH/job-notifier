#!/usr/bin/env python3
"""
SERVER pentru Job Notifier
Face scraping pe site-uri și oferă joburile către aplicația mobilă
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import threading
import time
import json
import os

app = Flask(__name__)
CORS(app)  # Permite aplicației să acceseze serverul

# ============== CONFIGURARE ==============
URLs = [
    "https://www.ejobs.ro/locuri-de-munca/bacau",
    "https://www.ejobs.ro/locuri-de-munca/remote",
    "https://www.olx.ro/locuri-de-munca/bacau/",
]

# Cache persistent pentru toate joburile
JOBS_CACHE_FILE = "jobs_cache.json"

# Stocăm joburile în memorie
all_jobs = []  # Toate joburile vreodată găsite
last_update = None

# ============== CACHE ==============

def load_cache():
    """Încarcă toate joburile salvate anterior"""
    if os.path.exists(JOBS_CACHE_FILE):
        try:
            with open(JOBS_CACHE_FILE, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
                # Filtrează joburi cu linkuri neoptimizate (query params OLX)
                cleaned = []
                for j in jobs:
                    link = j.get('link', '')
                    # Rejecta OLX linkuri cu query params
                    if 'olx.ro' in link and '?' in link:
                        continue
                    # Rejecta linkuri care nu sunt valide
                    if link.startswith('http://bilka') or link.startswith('https://bilka'):
                        continue
                    cleaned.append(j)
                return cleaned
        except:
            pass
    return []

def save_cache(jobs):
    """Salvează toate joburile în cache (maxim 500)"""
    jobs_to_save = jobs[-500:]
    with open(JOBS_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(jobs_to_save, f, ensure_ascii=False, indent=2)

# ============== SCRAPING ==============

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def normalize_text(text):
    """Normalizează text pentru comparație (elimină diacritice)"""
    import unicodedata
    if not text:
        return ''
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def get_soup(url, timeout=(5, 8)):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.content, 'html.parser')
    except Exception as e:
        print(f"   [EROARE] {url}: {e}")
        return None

def scrape_ejobs():
    """Extrage anunțurile de pe eJobs"""
    jobs = []
    pages = [
        "https://www.ejobs.ro/locuri-de-munca",
        "https://www.ejobs.ro/locuri-de-munca/remote",
    ]
    for url in pages:
        soup = get_soup(url)
        if not soup:
            continue
        for item in soup.select('article.job-item, div[class*="job-item"], li[class*="job"]'):
            try:
                a = item.find('a', href=True)
                title_el = item.find('h2') or item.find('h3') or (a if a else None)
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if len(title) < 4:
                    continue
                link = a['href'] if a else url
                if not link.startswith('http'):
                    link = 'https://www.ejobs.ro' + link
                company_el = item.find(class_=lambda c: c and 'company' in c.lower())
                company = company_el.get_text(strip=True) if company_el else ''

                # Extrage locația din text-ul job-ului (titlu, companie, descriere)
                location = 'România'
                text_to_search = (title + ' ' + company + ' ' + item.get_text()).lower()

                # Lista completa de județe și orașe
                counties = {
                    'bucuresti': 'București', 'bucureşti': 'București', 'ilfov': 'Ilfov',
                    'prahova': 'Prahova', 'constanta': 'Constanța', 'constanţa': 'Constanța',
                    'cluj': 'Cluj', 'brasov': 'Brașov', 'brașov': 'Brașov', 'brașov': 'Brașov',
                    'galati': 'Galați', 'galați': 'Galați', 'sibiu': 'Sibiu',
                    'vaslui': 'Vaslui', 'botosani': 'Botoșani', 'botoşani': 'Botoșani',
                    'bacau': 'Bacău', 'bacău': 'Bacău', 'bihor': 'Bihor',
                    'maramures': 'Maramureș', 'maramureş': 'Maramureș', 'satu mare': 'Satu Mare',
                    'suceava': 'Suceava', 'iasi': 'Iași', 'iași': 'Iași', 'buzau': 'Buzău',
                    'arges': 'Argeș', 'argeş': 'Argeș', 'dolj': 'Dolj', 'olt': 'Olt',
                    'gorj': 'Gorj', 'mehedinti': 'Mehedinți', 'teleorman': 'Teleorman',
                    'giurgiu': 'Giurgiu', 'calarasi': 'Călărași', 'călărași': 'Călărași',
                    'braila': 'Brăila', 'brăila': 'Brăila', 'tulcea': 'Tulcea',
                    'harghita': 'Harghita', 'covasna': 'Covasna', 'mures': 'Mureș', 'mureş': 'Mureș',
                    'timis': 'Timiș', 'timiş': 'Timiș', 'caras-severin': 'Caraș-Severin'
                }

                for county_slug, county_name in counties.items():
                    if county_slug in text_to_search:
                        location = county_name
                        break

                jobs.append({'id': link, 'title': title, 'company': company,
                             'location': location, 'source': 'eJobs', 'link': link})
            except:
                continue
    return jobs

def scrape_olx():
    """Extrage anunțurile de pe OLX"""
    jobs = []
    urls = [
        "https://www.olx.ro/locuri-de-munca/",
        "https://www.olx.ro/locuri-de-munca/?page=2",
    ]

    # Lista completa de județe și orașe
    counties = {
        'bucuresti': 'București', 'bucureşti': 'București', 'ilfov': 'Ilfov',
        'prahova': 'Prahova', 'constanta': 'Constanța', 'constanţa': 'Constanța',
        'cluj': 'Cluj', 'brasov': 'Brașov', 'brașov': 'Brașov', 'brașov': 'Brașov',
        'galati': 'Galați', 'galați': 'Galați', 'sibiu': 'Sibiu',
        'vaslui': 'Vaslui', 'botosani': 'Botoșani', 'botoşani': 'Botoșani',
        'bacau': 'Bacău', 'bacău': 'Bacău', 'bihor': 'Bihor',
        'maramures': 'Maramureș', 'maramureş': 'Maramureș', 'satu mare': 'Satu Mare',
        'suceava': 'Suceava', 'iasi': 'Iași', 'iași': 'Iași', 'buzau': 'Buzău',
        'arges': 'Argeș', 'argeş': 'Argeș', 'dolj': 'Dolj', 'olt': 'Olt',
        'gorj': 'Gorj', 'mehedinti': 'Mehedinți', 'teleorman': 'Teleorman',
        'giurgiu': 'Giurgiu', 'calarasi': 'Călărași', 'călărași': 'Călărași',
        'braila': 'Brăila', 'brăila': 'Brăila', 'tulcea': 'Tulcea',
        'harghita': 'Harghita', 'covasna': 'Covasna', 'mures': 'Mureș', 'mureş': 'Mureș',
        'timis': 'Timiș', 'timiş': 'Timiș', 'caras-severin': 'Caraș-Severin'
    }

    for url in urls:
        soup = get_soup(url)
        if not soup:
            continue
        for item in soup.select('[data-cy="l-card"], div.offer-wrapper, li.offer-item'):
            try:
                a = item.find('a', href=True)
                if not a:
                    continue
                title_el = item.find('h6') or item.find('h4') or item.find('strong') or a
                title = title_el.get_text(strip=True)
                if len(title) < 4:
                    continue
                link = a['href']
                if not link.startswith('http'):
                    link = 'https://www.olx.ro' + link

                # Skipează linkuri nevalide - doar /oferta/loc-de-munca/ sunt valide
                if '/oferta/loc-de-munca/' not in link.lower():
                    continue

                # Curață link-ul de query parameters ciudate
                if '?' in link:
                    link = link.split('?')[0]

                # Extrage locația din text-ul item-ului
                location = 'România'
                text_to_search = (title + ' ' + item.get_text()).lower()

                for county_slug, county_name in counties.items():
                    if county_slug in text_to_search:
                        location = county_name
                        break

                # Extrage compania din item (e.g. de pe OLX nu e evident, dar încearcă)
                company_el = item.find(class_=lambda c: c and ('seller' in c.lower() or 'company' in c.lower()))
                company = company_el.get_text(strip=True) if company_el else ''

                # Dacă nu găsit company, caută în text job titlu pentru companie
                if not company and ' - ' in title:
                    company = title.split(' - ')[-1].strip()

                # ID unic pe bază de URL (fără query params)
                job_id = link.split('/')[-1].split('.')[0] if '/' in link else link

                jobs.append({'id': job_id, 'title': title, 'company': company,
                             'location': location, 'source': 'OLX', 'link': link})
            except:
                continue
    return jobs

def update_jobs():
    """Actualizează lista de joburi"""
    global all_jobs, last_update
    print(f"[UPDATE] Actualizez joburile... {datetime.now().strftime('%H:%M:%S')}")

    # Încarcă joburile anterioare
    saved_jobs = load_cache()
    existing_ids = {job['id'] for job in saved_jobs}

    # Scrape joburi
    new_jobs_found = []

    print(f"[eJobs]", end=' ', flush=True)
    jobs = scrape_ejobs()
    print(f"{len(jobs)} joburi")
    new_jobs_found.extend(jobs)

    print(f"[OLX]", end=' ', flush=True)
    jobs = scrape_olx()
    print(f"{len(jobs)} joburi")
    new_jobs_found.extend(jobs)

    # Adaugă joburi noi (evita duplicatele)
    for job in new_jobs_found:
        if job['id'] not in existing_ids:
            saved_jobs.append(job)
            existing_ids.add(job['id'])

    # Sortează descrescător după job ID (cel mai recent primul)
    all_jobs = sorted(saved_jobs, key=lambda x: x.get('id', ''), reverse=True)

    # Salva în cache
    save_cache(all_jobs)

    last_update = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    print(f"[DONE] Total: {len(all_jobs)} joburi in cache\n")

def background_updater():
    """Actualizează joburile periodic (la fiecare 30 min)"""
    while True:
        update_jobs()
        time.sleep(1800)  # 30 minute

# ============== API ENDPOINTS ==============

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint - returnează token dummy"""
    return jsonify({
        'token': 'dummy-token-xyz',
        'user': {'id': 1, 'username': 'user', 'email': 'user@example.com'},
        'message': 'Login successful'
    })

@app.route('/register', methods=['POST'])
def register():
    """Register endpoint - returnează token dummy"""
    return jsonify({
        'token': 'dummy-token-xyz',
        'user': {'id': 1, 'username': 'user', 'email': 'user@example.com'},
        'message': 'Registration successful'
    })

@app.route('/me', methods=['GET'])
def get_me():
    """Get current user profile"""
    return jsonify({
        'id': 1,
        'username': 'user',
        'email': 'user@example.com'
    })

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    """User preferences"""
    return jsonify({
        'city': '',
        'keywords': '',
        'email_alerts_enabled': True
    })

@app.route('/profile', methods=['GET'])
def profile():
    """User profile"""
    return jsonify({
        'id': 1,
        'username': 'user',
        'email': 'user@example.com',
        'stats': {'saved': 0, 'applications': 0}
    })

@app.route('/saved-jobs', methods=['GET', 'POST', 'DELETE'])
def saved_jobs():
    """Saved jobs endpoint"""
    return jsonify({'jobs': [], 'total': 0})

@app.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    return jsonify({'message': 'Logged out successfully'})

@app.route('/applications', methods=['GET', 'POST'])
def applications():
    """Applications endpoint"""
    return jsonify({'applications': [], 'total': 0})

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'Job Notifier Server funcționează!',
        'total_jobs': len(all_jobs),
        'last_update': last_update
    })

@app.route('/jobs')
def get_jobs():
    """Returnează joburile cu filtre opționale"""
    city = normalize_text(request.args.get('city', '')).lower()
    keywords = normalize_text(request.args.get('keywords', '')).lower()
    source = request.args.get('source', '').lower()
    search = normalize_text(request.args.get('search', '')).lower()

    filtered = all_jobs

    # Filtrare după oraș (cu normalizare diacritice)
    if city and city != 'all':
        filtered = [j for j in filtered if city in normalize_text(j.get('location', '')).lower()]

    # Filtrare după cuvinte cheie
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(',')]
        filtered = [j for j in filtered if any(k in normalize_text(j.get('title', '')).lower() or
                                                k in normalize_text(j.get('company', '')).lower()
                                                for k in keyword_list)]

    # Filtrare după sursă
    if source and source != 'all':
        filtered = [j for j in filtered if j.get('source', '').lower() == source]

    # Căutare text (titlu + companie + locație)
    if search:
        filtered = [j for j in filtered if search in normalize_text(j.get('title', '')).lower() or
                   search in normalize_text(j.get('company', '')).lower() or
                   search in normalize_text(j.get('location', '')).lower()]

    return jsonify({
        'jobs': filtered,
        'total': len(filtered),
        'last_update': last_update
    })

@app.route('/refresh')
def refresh():
    """Forțează actualizarea joburilor"""
    update_jobs()
    return jsonify({
        'message': 'Joburi actualizate!',
        'total': len(all_jobs)
    })

# ============== STARTUP ==============

# Încarcă cache și pornește background updater la startup
all_jobs = load_cache()
print(f"[CACHE] Incarca: {len(all_jobs)} joburi")

# Prima actualizare
update_jobs()

# Pornește actualizarea în fundal
updater = threading.Thread(target=background_updater, daemon=True)
updater.start()

# ============== START ==============

if __name__ == '__main__':
    print("="*60)
    print("[START] JOB NOTIFIER SERVER (Local Mode)")
    print("="*60)

    # Port dinamic (Render oferă PORT, default 5000 local)
    port = int(os.environ.get("PORT", 5000))

    print("\n[SERVER] Pornit!")
    print(f"[URL] http://0.0.0.0:{port}")
    print("[NOTE] Noteza adresa IP/URL pentru aplicatie\n")

    # Pornește serverul pe toate interfețele (accesibil din rețea)
    app.run(host='0.0.0.0', port=port, debug=False)
