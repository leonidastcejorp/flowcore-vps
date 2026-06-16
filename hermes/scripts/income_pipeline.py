#!/usr/bin/env python3
"""💰 Income Pipeline — nyari gigs & peluang cuan dari Reddit, Freelancer, DeFi."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

CACHE_DIR = "/root/projects/bounty-output"
os.makedirs(CACHE_DIR, exist_ok=True)

log = ErrorLog("💰 Cuan Feed")
RESULTS = []
TS = datetime.now().strftime("%H:%M")


def tulis(cat, msg):
    RESULTS.append(f"[{TS}] [{cat}] {msg}")


def fetch(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        log.warning(f"Gagal buka {url[:40]}...", f"Server ngasih kode {e.code}", "Cek apakah situsnya lagi down")
        return None
    except urllib.error.URLError as e:
        log.warning(f"Gagal konek {url[:40]}...", f"Error jaringan: {e.reason}", "Cek koneksi internet")
        return None
    except TimeoutError:
        log.warning(f"Koneksi timeout {url[:40]}...", f"Lebih dari {timeout} detik gak ada respon", "Cek latency koneksi")
        return None
    except Exception as e:
        log.error(f"Error buka {url[:40]}...", f"{type(e).__name__}: {e}", "Coba buka manual di browser")
        return None


# ─── REDDIT ───────────────────────────────────────────────────────────────────

def cek_reddit(subreddit, query="paypal crypto usd bitcoin"):
    url = (f"https://old.reddit.com/r/{subreddit}/search.rss?"
           f"q={urllib.parse.quote(query)}&sort=new&restrict_sr=on&limit=15")
    html = fetch(url)
    if not html:
        tulis(subreddit, "Gagal ambil data")
        return

    entries = re.findall(r'<entry>(.*?)</entry>', html, re.DOTALL)
    if not entries:
        tulis(subreddit, "Gak ada postingan")
        log.warning(f"Reddit r/{subreddit} kosong", "Feed RSS gak ngembaliin data", "Cek manual di old.reddit.com")
        return

    tulis(subreddit, f"Dapet {len(entries)} postingan")
    keywords = ['$', 'usd', 'pay', 'paypal', 'btc', 'eth', 'crypto', 'task', 'job', 'hire']
    count = 0
    for e in entries[:8]:
        title_m = re.search(r'<title>(.*?)</title>', e, re.DOTALL)
        link_m = re.search(r'<link[^>]*href="([^"]+)"', e) or re.search(r'<link>(.*?)</link>', e)
        title = title_m.group(1).strip() if title_m else "?"
        title = title.replace('&amp;', '&').replace('&#x27;', "'").replace('&quot;', '"')
        link = link_m.group(1).strip() if link_m else "?"
        if any(kw in title.lower() for kw in keywords):
            tulis(subreddit, f"[?pts] {title[:120]}")
            tulis(subreddit, f"       {link}")
            count += 1
    if count == 0:
        tulis(subreddit, "Gak ada postingan relevan")


# ─── DEFI ─────────────────────────────────────────────────────────────────────

def cek_defillama():
    data = fetch("https://api.llama.fi/protocols", timeout=15)
    if not data:
        tulis("DeFiLlama", "Gagal ambil data")
        return
    try:
        j = json.loads(data)
    except json.JSONDecodeError:
        tulis("DeFiLlama", "Data bukan JSON")
        log.error("Data DeFiLlama error", "API ngasih balasan yang bukan JSON", "Cek https://api.llama.fi/protocols")
        return
    if not isinstance(j, list):
        tulis("DeFiLlama", "Format data aneh")
        return
    valid = [p for p in j if p.get("change_1d") is not None]
    if not valid:
        log.warning("Data DeFiLlama kosong", "Semua protocol gak punya data perubahan 1 hari", "Mungkin API lagi error")
        tulis("DeFiLlama", "Gak ada data perubahan")
        return
    valid.sort(key=lambda p: abs(p["change_1d"]), reverse=True)
    tulis("DeFiLlama", f"Tracking {len(valid)}/{len(j)} protocol")
    for p in valid[:5]:
        n, tvl, chg, sym = p.get("name", "?"), p.get("tvl", 0) or 0, p.get("change_1d", 0) or 0, p.get("symbol", "") or ""
        tulis("DeFiLlama", f"  {sym:6s} {n:20s} TVL ${tvl:,.0f}  ({chg:+.2f}%)")


def cek_gas():
    html = fetch("https://etherscan.io/gastracker", timeout=15)
    if not html:
        tulis("Gas", "Gagal ambil data")
        return
    low = re.search(r'Low\s*:\s*([0-9.]+)', html, re.IGNORECASE)
    high = re.search(r'(?:High|Fast)\s*:\s*([0-9.]+)', html, re.IGNORECASE)
    base = re.search(r'Base Fee\s*:\s*([0-9.]+)', html, re.IGNORECASE)
    parts = []
    if low: parts.append(f"Low={low.group(1)}")
    if base: parts.append(f"Base={base.group(1)}")
    if high: parts.append(f"High={high.group(1)}")
    if parts:
        tulis("Gas", f"Ethereum gas: {' | '.join(parts)} Gwei")
    else:
        log.warning("Gagal baca gas Ethereum", "Halaman etherscan kebuka tapi angka gas gak terbaca", "Mungkin struktur halaman berubah")


# ─── FREELANCER ───────────────────────────────────────────────────────────────

def cek_freelancer():
    data = fetch("https://www.freelancer.com/api/projects/0.1/projects/active/?limit=5", timeout=15)
    if not data:
        tulis("Freelancer", "Gagal ambil data")
        return
    try:
        j = json.loads(data)
    except json.JSONDecodeError:
        log.error("Data Freelancer error", "API ngasih balasan bukan JSON", "Cek API Freelancer")
        tulis("Freelancer", "Data error")
        return
    if j.get("status") != "success":
        log.warning("API Freelancer error", f"Status: {j.get('message', '?')}", "Mungkin kena rate limit")
        tulis("Freelancer", f"API error: {j.get('message', '?')}")
        return
    projects = j.get("result", {}).get("projects", [])
    if not projects:
        tulis("Freelancer", "Gak ada project baru")
        return
    tulis("Freelancer", f"{len(projects)} project baru")
    for p in projects[:5]:
        title = p.get("title", "Untitled")[:70]
        budget = p.get("budget", {})
        amount = budget.get("minimum", "?")
        currency = budget.get("currency", {}).get("code", "$")
        tulis("Freelancer", f"  • {title} — {currency}{amount}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        cek_reddit("slavelabour", "paypal crypto usd bitcoin")
        cek_reddit("beermoney", "paypal free crypto")
        cek_reddit("forhire", "paypal usd")
        cek_defillama()
        cek_gas()
        cek_freelancer()
    except Exception:
        log.exception("Pipeline error total", "Cek koneksi internet & API")

    # ── Simpan ke cache ──
    try:
        with open(f"{CACHE_DIR}/pipeline_report.txt", "w") as f:
            f.write(f"💰 Income Pipeline — {datetime.now().isoformat()}\n")
            f.write("=" * 52 + "\n")
            for r in RESULTS:
                f.write(r + "\n")
    except OSError:
        log.error("Gagal simpan cache", "File report gak bisa ditulis", "Cek disk")

    # ── STDOUT: cuma kalo ada gigs $50+ ──
    high_val = [r for r in RESULTS if re.search(r'\$[5-9]\d{2,}|\$\d{4,}', r)]

    output = []
    if high_val:
        output.append("💰 **HIGH-VALUE GIG!**\n")
        for h in high_val:
            output.append(h)
        output.append("")

    # Append error report kalo ada critical/error
    err_report = log.format_report()
    if err_report and (high_val or log.ada_masalah()):
        output.append(err_report)

    if output:
        print("\n".join(output))

    log.persist()
