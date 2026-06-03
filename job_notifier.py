#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Notifier - Monitorizare joburi din toata Romania
Ruleaza continuu si trimite email cand apar joburi noi.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import time
import os
from datetime import datetime

# ============== CONFIGURARE ==============
# In cloud (GitHub Actions) ia datele din "secrets" (variabile de mediu).
# Local foloseste valorile de mai jos.
EMAIL_TAU = os.environ.get("EMAIL_TAU", "theangelx1x@gmail.com")
EMAIL_SMTP = os.environ.get("EMAIL_SMTP", "theangelx1x@gmail.com")
PAROLA_EMAIL = os.environ.get("PAROLA_EMAIL", "ftxl uryj fugd inxf")

# Daca RUN_ONCE=1 (in cloud) ruleaza o singura data si iese.
RUN_ONCE = os.environ.get("RUN_ONCE", "0") == "1"

INTERVAL_MINUTE = 30          # Cât de des verifică (minute)
MAX_JOBURI_PER_EMAIL = 50     # Maxim joburi într-un singur email
CACHE_FILE = "job_cache.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# ============== CACHE ==============

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            pass
    return set()

def save_cache(seen_ids):
    # Păstrăm maxim 10000 ID-uri ca să nu crească infinit
    ids_list = list(seen_ids)[-10000:]
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(ids_list, f)

# ============== SCRAPING ==============

def get_soup(url, timeout=(5, 8)):
    # timeout = (connect_timeout, read_timeout) - garanteaza ca nu blocheaza
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.content, 'html.parser')
    except Exception as e:
        print(f"   [EROARE] {url}: {e}")
        return None

def scrape_ejobs():
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

def scrape_bestjobs():
    jobs = []
    url = "https://www.bestjobs.eu/ro/locuri-de-munca"
    soup = get_soup(url)
    if not soup:
        return jobs
    try:
        import json as _json
        script = soup.find('script', id='__NEXT_DATA__')
        if not script:
            return jobs
        data = _json.loads(script.string)
        items = data['props']['pageProps']['jobListCardsFromServer']['items']
        for j in items:
            slug = j.get('slug', '')
            link = f"https://www.bestjobs.eu/ro/locuri-de-munca/{slug}"
            title = j.get('title', '')
            company = j.get('companyName', '')
            locs = j.get('locations', [])
            location = locs[0].get('name', 'Romania') if locs else 'Romania'
            if title and slug:
                jobs.append({'id': link, 'title': title, 'company': company,
                             'location': location, 'source': 'BestJobs', 'link': link})
    except Exception as e:
        print(f"   [BestJobs parse err] {e}")
    return jobs

def scrape_cariere():
    jobs = []
    url = "https://www.cariere.ro/locuri-de-munca"
    soup = get_soup(url)
    if not soup:
        return jobs
    for item in soup.select('[class*=job-item]'):
        try:
            a = item.find('a', href=True)
            title_el = item.find('h2') or item.find('h3') or item.find('h4')
            if not title_el or not a:
                continue
            title = title_el.get_text(strip=True)
            if len(title) < 4:
                continue
            link = a['href']
            if not link.startswith('http'):
                link = 'https://www.cariere.ro' + link
            jobs.append({'id': link, 'title': title, 'company': '',
                         'location': 'Romania', 'source': 'Cariere.ro', 'link': link})
        except:
            continue
    return jobs

SCRAPERS = [
    ('eJobs',       scrape_ejobs),
    ('OLX',         scrape_olx),
    ('BestJobs',    scrape_bestjobs),
]

def scrape_all():
    import threading
    all_jobs = []
    for name, fn in SCRAPERS:
        print(f"   🌐 {name}...", end=' ', flush=True)
        result = {'jobs': None, 'err': None}

        def worker():
            try:
                result['jobs'] = fn()
            except Exception as e:
                result['err'] = e

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        t.join(timeout=25)  # asteapta max 25s; daca nu termina, abandonam thread-ul

        if t.is_alive():
            print("TIMEOUT (sarit)")
        elif result['err'] is not None:
            print(f"EROARE: {result['err']}")
        else:
            jobs = result['jobs'] or []
            print(f"{len(jobs)} joburi")
            all_jobs.extend(jobs)
    return all_jobs

# ============== EMAIL ==============

def send_email(new_jobs):
    if not new_jobs:
        return

    # Dacă sunt prea multe, trimitem în batch-uri
    batches = [new_jobs[i:i+MAX_JOBURI_PER_EMAIL]
               for i in range(0, len(new_jobs), MAX_JOBURI_PER_EMAIL)]

    for idx, batch in enumerate(batches):
        subject = f"🔔 {len(new_jobs)} Joburi Noi în România - {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        if len(batches) > 1:
            subject += f" (partea {idx+1}/{len(batches)})"

        rows = ""
        for j in batch:
            company_str = f"<span style='color:#555'> | {j['company']}</span>" if j['company'] else ""
            rows += f"""
            <div style="border-left:4px solid #3498db;padding:12px 15px;margin:8px 0;
                        background:#f8f9fa;border-radius:4px;">
                <div style="font-size:15px;font-weight:bold;color:#2980b9;">
                    <a href="{j['link']}" style="color:#2980b9;text-decoration:none;">{j['title']}</a>
                </div>
                <div style="font-size:12px;color:#7f8c8d;margin-top:4px;">
                    📍 {j['location']}{company_str}
                    &nbsp;·&nbsp;
                    <span style="background:#e8f4fd;color:#2980b9;padding:2px 6px;
                                 border-radius:3px;font-size:11px;">{j['source']}</span>
                </div>
            </div>"""

        html = f"""
        <html><head><meta charset="UTF-8"></head>
        <body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:20px;">
            <h2 style="color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:10px;">
                🔔 {len(new_jobs)} Joburi Noi în România
            </h2>
            <p style="color:#7f8c8d;font-size:12px;">
                Actualizat: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
                {"&nbsp;·&nbsp; Afișate " + str(len(batch)) + "/" + str(len(new_jobs)) if len(batches) > 1 else ""}
            </p>
            {rows}
            <hr style="margin-top:20px;border:none;border-top:1px solid #eee;">
            <p style="color:#bdc3c7;font-size:11px;">
                Job Notifier • Verificare la fiecare {INTERVAL_MINUTE} minute
            </p>
        </body></html>"""

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_SMTP
        msg['To'] = EMAIL_TAU
        msg.attach(MIMEText(html, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_SMTP, PAROLA_EMAIL)
            server.send_message(msg)
            server.quit()
            print(f"   📧 Email trimis: {len(batch)} joburi (batch {idx+1}/{len(batches)})")
        except Exception as e:
            print(f"   ❌ Eroare email: {e}")

# ============== LOOP PRINCIPAL ==============

def run():
    print("=" * 60)
    print("🚀 JOB NOTIFIER - Toată românia - STOCHEAZĂ TOATE JOBURILE")
    print("=" * 60)
    print(f"📧 Email: {EMAIL_TAU}")
    print(f"⏱  Interval: la fiecare {INTERVAL_MINUTE} minute")
    print(f"Site-uri: {', '.join(name for name, _ in SCRAPERS)}")
    print("=" * 60)

    seen_ids = load_cache()
    first_run = len(seen_ids) == 0

    if first_run:
        print("\n⚠️  Prima rulare: înregistrez TOATE joburile existente.")
        print("   Acum stocheaza si furnizeaza TOATE joburile, nu doar pe cele noi.\n")

    while True:
        now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        print(f"\n🔄 Verificare la {now}")

        all_jobs = scrape_all()
        print(f"   📊 Total găsite în scraping: {len(all_jobs)}")

        new_jobs = [j for j in all_jobs if j['id'] not in seen_ids]
        print(f"   ✨ Joburi NOI: {len(new_jobs)}")

        # Adăugăm toate în cache (stochează TOATE joburile)
        for j in all_jobs:
            seen_ids.add(j['id'])
        save_cache(seen_ids)
        print(f"   💾 Cache total: {len(seen_ids)} joburi stocate")

        if new_jobs and not first_run:
            print(f"   📧 Trimit email cu {len(new_jobs)} joburi NOI...")
            send_email(new_jobs)
        elif first_run:
            print(f"   ✅ {len(seen_ids)} joburi înregistrate în cache. Gata pentru app!")
            first_run = False
        else:
            print(f"   ℹ️  Niciun job nou (continuez să furnizez {len(seen_ids)} joburi la app)")

        if RUN_ONCE:
            print("   ✅ Rulare unică terminată (mod cloud).")
            break

        print(f"   ⏳ Următoarea verificare în {INTERVAL_MINUTE} minute...")
        time.sleep(INTERVAL_MINUTE * 60)

if __name__ == '__main__':
    run()
