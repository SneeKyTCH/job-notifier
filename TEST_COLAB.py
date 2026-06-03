# ============================================================
# TEST: Merge scraping-ul dintr-un IP de cloud/datacenter?
# Copiaza TOT acest cod intr-o celula Google Colab si ruleaza (Shift+Enter).
# ============================================================
import requests, json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
}

print("Verific de pe ce IP rulez...")
try:
    ip = requests.get("https://api.ipify.org", timeout=10).text
    print("IP cloud:", ip, "\n")
except Exception as e:
    print("Nu pot afla IP-ul:", e, "\n")

from bs4 import BeautifulSoup

def test(name, url, check):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        status = r.status_code
        n = check(r)
        verdict = "OK" if (status == 200 and n > 0) else "BLOCAT/GOL"
        print(f"[{name}] status={status}  joburi_gasite={n}  --> {verdict}")
    except Exception as e:
        print(f"[{name}] EROARE: {e}")

def ck_ejobs(r):
    s = BeautifulSoup(r.content, 'html.parser')
    return len(s.select('article.job-item, div[class*="job-item"], li[class*="job"]'))

def ck_olx(r):
    s = BeautifulSoup(r.content, 'html.parser')
    return len(s.select('[data-cy="l-card"], div.offer-wrapper, li.offer-item'))

def ck_bestjobs(r):
    s = BeautifulSoup(r.content, 'html.parser')
    sc = s.find('script', id='__NEXT_DATA__')
    if not sc:
        return 0
    try:
        d = json.loads(sc.string)
        return len(d['props']['pageProps']['jobListCardsFromServer']['items'])
    except Exception:
        return 0

print("=== TEST SCRAPING DIN CLOUD ===\n")
test("eJobs",    "https://www.ejobs.ro/locuri-de-munca", ck_ejobs)
test("OLX",      "https://www.olx.ro/locuri-de-munca/", ck_olx)
test("BestJobs", "https://www.bestjobs.eu/ro/locuri-de-munca", ck_bestjobs)
print("\nGata. Trimite-mi rezultatul de mai sus.")
