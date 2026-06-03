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

def scrape_ejobs(url):
    """Extrage anunțurile de pe eJobs"""
    jobs = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        job_containers = soup.find_all('div', class_='job-item') or \
                        soup.find_all('a', class_='absolute-link-overlay') or \
                        soup.find_all('article')

        for i, container in enumerate(job_containers[:20]):
            try:
                title_elem = container.find('h2') or container.find('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if len(title) < 5:
                        continue
                    link = container.find('a')
                    link = link['href'] if link and link.get('href') else url
                    if not link.startswith('http'):
                        link = 'https://www.ejobs.ro' + link

                    jobs.append({
                        'id': f'ejobs_{i}_{int(time.time())}',
                        'title': title,
                        'company': 'eJobs',
                        'location': 'Remote' if 'remote' in url else 'Bacău',
                        'source': 'eJobs',
                        'link': link
                    })
            except:
                continue
    except Exception as e:
        print(f"[EROARE eJobs] {e}")
    return jobs

def scrape_olx(url):
    """Extrage anunțurile de pe OLX"""
    jobs = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        job_containers = soup.find_all('div', class_='itembox') or \
                        soup.find_all('a', class_='item') or \
                        soup.find_all('li', class_='aditem')

        for i, container in enumerate(job_containers[:20]):
            try:
                title_elem = container.find('h2') or container.find('strong') or container.find('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if len(title) < 5:
                        continue
                    link = container.find('a')
                    link = link['href'] if link and link.get('href') else url
                    if not link.startswith('http'):
                        link = 'https://www.olx.ro' + link

                    jobs.append({
                        'id': f'olx_{i}_{int(time.time())}',
                        'title': title,
                        'company': 'OLX',
                        'location': 'Bacău',
                        'source': 'OLX',
                        'link': link
                    })
            except:
                continue
    except Exception as e:
        print(f"[EROARE OLX] {e}")
    return jobs

def update_jobs():
    """Actualizează lista de joburi"""
    global all_jobs, last_update
    print(f"\n🔄 Actualizez joburile... {datetime.now().strftime('%H:%M:%S')}")

    # Încarcă joburile anterioare
    saved_jobs = load_cache()
    existing_ids = {job['id'] for job in saved_jobs}

    new_jobs_found = []
    for url in URLs:
        print(f"   🌐 {url}")
        if 'olx' in url:
            jobs = scrape_olx(url)
        else:
            jobs = scrape_ejobs(url)
        print(f"      └─ {len(jobs)} joburi")
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

# ============== START ==============

if __name__ == '__main__':
    print("="*60)
    print("🚀 JOB NOTIFIER SERVER")
    print("="*60)

    # Încarcă joburile din cache anterior
    global all_jobs
    all_jobs = load_cache()
    print(f"📂 Cache încărcat: {len(all_jobs)} joburi anterioare\n")

    # Prima actualizare
    update_jobs()

    # Pornește actualizarea în fundal
    updater = threading.Thread(target=background_updater, daemon=True)
    updater.start()

    # Port dinamic (Render oferă PORT, default 5000 local)
    port = int(os.environ.get("PORT", 5000))

    print("\n📡 Server pornit!")
    print(f"🌐 http://0.0.0.0:{port}")
    print("📱 Notează adresa IP/URL pentru aplicație\n")

    # Pornește serverul pe toate interfețele (accesibil din rețea)
    app.run(host='0.0.0.0', port=port, debug=False)
