# 📖 FlowCore Tutorial Guide

> Complete walkthrough for all FlowCore features

---

## 📑 Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Module: Registrar (Account Creator)](#module-registrar-account-creator)
4. [Module: Scraper (Data Collection)](#module-scraper-data-collection)
5. [Module: Watcher (Pipeline Monitoring)](#module-watcher-pipeline-monitoring)
6. [Proxy Configuration](#proxy-configuration)
7. [Browser Fingerprinting](#browser-fingerprinting)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites
- Python 3.11+
- Git

### Setup
```bash
# Clone repository
git clone https://github.com/leonidastcejorp/flowcore1.git
cd flowcore1

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser engine
playwright install chromium

# Verify installation
python tests/test_browser.py
```

Expected output:
```
🧪 FlowCore Test Suite
========================================
📋 Name Generator:
   ...
🔐 Sample password: ...
🖐️  Fingerprint Profiles:
   ...
✅ All system tests passed!
```

---

## Quick Start

The fastest way to get started:

```bash
# Create 3 Discord accounts
python -m flowcore.modules.registrar --site discord --count 3

# View saved accounts
cat ~/.flowcore/accounts/accounts_*.json
```

---

## Module: Registrar (Account Creator)

### Overview
The Registrar module automates web form submissions with anti-detection. It supports multiple platforms and uses randomized browser fingerprints per session.

### Supported Platforms

| Platform   | Status      | Notes                                |
|------------|-------------|--------------------------------------|
| Discord    | ✅ Working  | No email verification required       |
| Fiverr     | ⚠️ Needs proxy | Turnstile protected, IP dependent |
| Reddit     | ⚠️ Needs proxy | IP blocking aggressive             |

### Usage

**Basic usage — single site:**
```bash
python -m flowcore.modules.registrar --site discord
```

**Multiple accounts:**
```bash
python -m flowcore.modules.registrar --site discord --count 10
```

**All supported sites:**
```bash
python -m flowcore.modules.registrar --site all --count 1
```

**With proxy:**
```bash
python -m flowcore.modules.registrar --site fiverr --count 3 --proxy 192.168.1.1:8080
```

### Output

Accounts are saved to `~/.flowcore/accounts/accounts_TIMESTAMP.json`:
```json
[
  {
    "site": "discord",
    "email": "citra.hutapea123@gmail.com",
    "username": "citrahutapea742",
    "password": "aB3$k9!mN2@pQ7*",
    "name": "Citra Hutapea",
    "status": "submitted",
    "timestamp": "2026-06-15T19:42:08"
  }
]
```

### Tips for Success

1. **Use a clean IP** — Run from your home network (Telkomsel, IndiHome) instead of a VPS
2. **Add delays** — The script already adds random delays; don't rush
3. **Proxy rotation** — For mass creation, use rotating residential proxies
4. **One IP = 3-5 accounts max** — Beyond that, platforms get suspicious
5. **Email verification** — Some platforms require email confirmation; use temp mail services

---

## Module: Scraper (Data Collection)

### Overview
The Scraper module provides anti-detection web scraping capabilities.

### Usage as a library

```python
import asyncio
from flowcore.core.browser import BrowserSession
from flowcore.modules.scraper import scrape_page, save_results

async def main():
    session = BrowserSession()
    _, _, page = await session.launch()
    
    # Scrape a page
    data = await scrape_page(
        page,
        "https://example.com",
        selectors={
            'headlines': 'h1, h2',
            'links': 'a[href]',
        }
    )
    
    # Save results
    path = save_results(data, name="example_scrape")
    print(f"Saved to: {path}")
    
    await session.close()

asyncio.run(main())
```

### Output Format
Results are saved as JSON to `~/.flowcore/scrapes/`:
```json
{
  "url": "https://example.com",
  "timestamp": "2026-06-15T20:00:00",
  "title": "Example Page",
  "headlines": ["Welcome", "About Us"],
  "links": ["/about", "/contact"]
}
```

---

## Module: Watcher (Pipeline Monitoring)

### Overview
The Watcher module runs scheduled checks for online opportunities, freelance gigs, and crypto airdrops.

### Run manually
```bash
python -m flowcore.modules.watcher
```

### As a cron job
The watcher runs automatically every 6 hours via Hermes cron. Reports are delivered to your configured channel.

### What it monitors
- **Reddit r/slavelabour** — Freelance gigs paying in USD/PayPal
- **Reddit r/beermoney** — Quick money opportunities
- **Testnet faucets** — Free crypto for testing
- **Airdrop platforms** — Galxe, Layer3 quests

---

## Proxy Configuration

### Free Proxy Lists
The Proxy Manager automatically downloads free proxy lists from GitHub.

**Refresh proxies:**
```bash
python scripts/refresh_proxies.py
```

**Auto-refresh schedule:** Every 6 hours (via Hermes cron)

### Using Proxies with Registrar
```bash
# Single proxy
python -m flowcore.modules.registrar --site fiverr --proxy 1.2.3.4:8080

# Proxy pool (from file)
echo "1.2.3.4:8080
5.6.7.8:3128" > proxies.txt
# Then modify registrar.py to randomize from pool
```

### Proxy Recommendations

| Type            | Speed    | Cost       | Best For               |
|-----------------|----------|------------|------------------------|
| Residential     | Fast     | $2-5/mo    | Account creation       |
| Datacenter      | Fastest  | Free-$1/mo | General scraping       |
| Mobile          | Medium   | $5-15/mo   | High-security targets  |
| Free (GitHub)   | Slow     | Free       | Testing, light use     |

---

## Browser Fingerprinting

FlowCore uses advanced browser fingerprint spoofing to avoid detection:

### What's Spoofed
- ✅ `navigator.webdriver` — Removed (undetected)
- ✅ `navigator.plugins` — Set to 5 plugins
- ✅ `window.chrome` — Chrome runtime object
- ✅ WebGL vendor — Spoofed as Intel
- ✅ Screen properties — Color depth, pixel depth
- ✅ User agent — Rotated per session
- ✅ Viewport — Random resolution
- ✅ Locale & Timezone — Realistic values
- ✅ Sec-Ch-Ua headers — Matching browser version

### Verification
```python
from flowcore.core.browser import BrowserSession
import asyncio

async def check():
    session = BrowserSession()
    _, context, page = await session.launch()
    
    fingerprint = await page.evaluate("""() => ({
        webdriver: navigator.webdriver,
        plugins: navigator.plugins.length,
        chrome: typeof window.chrome !== 'undefined',
        userAgent: navigator.userAgent,
    })""")
    
    print(fingerprint)
    await session.close()

asyncio.run(check())
```

Expected result:
```python
{
    'webdriver': None,      # ✅ undetected
    'plugins': 5,           # ✅ looks real
    'chrome': True,         # ✅ has Chrome runtime
    'userAgent': 'Mozilla/5.0 ... Chrome/125.0.0.0'
}
```

---

## Troubleshooting

### "IP blocked" on Reddit/Fiverr
Your IP is flagged as datacenter. Solutions:
- Run from home network (recommended)
- Use residential proxy
- Use mobile hotspot

### Turnstile challenge appears
Cloudflare Turnstile is hard to bypass from VPS:
- Needs residential IP to pass
- Free proxies are too slow
- Best approach: run from home network

### "Page.goto timeout"
The proxy is too slow:
```bash
# Increase timeout in browser.py
await page.goto(url, timeout=60000)  # 60 seconds
```

### Account creation succeeds but no email
Some platforms send email verification:
```python
# Use temp mail API (add to registrar.py)
# https://www.1secmail.com/api/v1/
```

### Playwright not found
```bash
playwright install chromium
# Or with dependencies
playwright install --with-deps chromium
```

### Still stuck?
Open an issue on GitHub or check the [discussions](https://github.com/leonidastcejorp/flowcore1/discussions).

---

## 🚀 Quick Reference

```bash
# Install
pip install -r requirements.txt && playwright install chromium

# Create accounts
python -m flowcore.modules.registrar --site discord --count 5

# Run pipeline
python -m flowcore.modules.watcher

# Refresh proxies
python scripts/refresh_proxies.py

# Run tests
python tests/test_browser.py
```

---

*FlowCore v1.0.0 — Enterprise Workflow Automation Toolkit*
