#!/usr/bin/env python3
"""
SERVER pentru Job Notifier
Face scraping pe site-uri și oferă joburile către aplicația mobilă
"""

from flask import Flask, jsonify
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
                return json.load(f)
        except:
            pass
    return []

def save_cache(jobs):
    """Salvează toate joburile în cache (maxim 10000)"""
    jobs_to_save = jobs[-10000:]
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
    pages = ["https://www.ejobs.ro/locuri-de-munca",
             "https://www.ejobs.ro/locuri-de-munca/remote"]
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
                location_el = item.find(class_=lambda c: c and ('location' in c.lower() or 'city' in c.lower()))
                location = location_el.get_text(strip=True) if location_el else 'România'
                jobs.append({'id': link, 'title': title, 'company': company,
                             'location': location, 'source': 'eJobs', 'link': link})
            except:
                continue
    return jobs

def scrape_olx():
    """Extrage anunțurile de pe OLX"""
    jobs = []
    url = "https://www.olx.ro/locuri-de-munca/"
    soup = get_soup(url)
    if not soup:
        return jobs
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
            location_el = item.find('p', attrs={'data-testid': 'location-date'}) or \
                          item.find(class_=lambda c: c and 'location' in c.lower())
            location = location_el.get_text(strip=True).split('-')[0].strip() if location_el else 'România'
            jobs.append({'id': link, 'title': title, 'company': '',
                         'location': location, 'source': 'OLX', 'link': link})
        except:
            continue
    return jobs

def update_jobs():
    """Actualizează lista de joburi"""
    global all_jobs, last_update
    print(f"\n🔄 Actualizez joburile... {datetime.now().strftime('%H:%M:%S')}")

    # Încarcă joburile anterioare
    saved_jobs = load_cache()
    existing_ids = {job['id'] for job in saved_jobs}

    # Scrape joburi
    new_jobs_found = []

    print(f"   🌐 eJobs...", end=' ', flush=True)
    jobs = scrape_ejobs()
    print(f"{len(jobs)} joburi")
    new_jobs_found.extend(jobs)

    print(f"   🌐 OLX...", end=' ', flush=True)
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
    print(f"✅ Total: {len(all_jobs)} joburi în cache\n")

def background_updater():
    """Actualizează joburile periodic (la fiecare 30 min)"""
    while True:
        update_jobs()
        time.sleep(1800)  # 30 minute

# ============== API ENDPOINTS ==============

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
    """Returnează TOATE joburile vreodată găsite"""
    return jsonify({
        'jobs': all_jobs,
        'total': len(all_jobs),
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
print(f"📂 Cache încărcat: {len(all_jobs)} joburi")

# Prima actualizare
update_jobs()

# Pornește actualizarea în fundal
updater = threading.Thread(target=background_updater, daemon=True)
updater.start()

# ============== START ==============

if __name__ == '__main__':
    print("="*60)
    print("🚀 JOB NOTIFIER SERVER (Local Mode)")
    print("="*60)

    # Port dinamic (Render oferă PORT, default 5000 local)
    port = int(os.environ.get("PORT", 5000))

    print("\n📡 Server pornit!")
    print(f"🌐 http://0.0.0.0:{port}")
    print("📱 Notează adresa IP/URL pentru aplicație\n")

    # Pornește serverul pe toate interfețele (accesibil din rețea)
    app.run(host='0.0.0.0', port=port, debug=False)
