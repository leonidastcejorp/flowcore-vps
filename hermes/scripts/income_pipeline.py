#!/usr/bin/env python3
"""
💰 BREACH INCOME PIPELINE v1.0
Automated money opportunity scraper & analyzer
Runs every 6 hours, delivers fresh leads
"""
import json
import urllib.request
import urllib.error
import urllib.parse
import re
import os
from datetime import datetime
from html.parser import HTMLParser

CACHE_DIR = "/root/bounty_output"
os.makedirs(CACHE_DIR, exist_ok=True)
RESULTS = []

def log(cat, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    RESULTS.append(f"[{ts}] [{cat}] {msg}")

def fetch(url, headers=None):
    if headers is None:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None

def scrape_reddit(subreddit, query="paypal crypto usd bitcoin"):
    """Scrape Reddit for gig posts"""
    url = f"https://www.reddit.com/r/{subreddit}/search.json?q={urllib.parse.quote(query)}&restrict_sr=on&sort=new&limit=15"
    data = fetch(url, {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Python/3.11"})
    if not data:
        log(subreddit, "Failed to fetch")
        return
    
    try:
        j = json.loads(data)
        posts = j.get("data", {}).get("children", [])
        if not posts:
            log(subreddit, "No posts found")
            return
        
        log(subreddit, f"Found {len(posts)} posts")
        count = 0
        for p in posts[:8]:
            d = p.get("data", {})
            title = d.get("title", "")
            score = d.get("score", 0)
            url_post = d.get("url", "")
            # Filter for money-related
            money_kw = ['$', 'usd', 'pay', 'paypal', 'btc', 'eth', 'crypto', 'bitcoin', 'task', 'job', 'work', 'hire']
            if any(kw in title.lower() for kw in money_kw):
                log(subreddit, f"[{score}pts] {title[:120]}")
                log(subreddit, f"       {url_post}")
                count += 1
        
        if count == 0:
            log(subreddit, "No money-related posts in results")
    except Exception as e:
        log(subreddit, f"Parse error: {e}")

def scrape_layer3_quests():
    """Try multiple known Layer3 API endpoints"""
    endpoints = [
        "https://api.layer3.xyz/api/trpc/quest.listActiveQuests?limit=5",
        "https://layer3.xyz/api/trpc/quest.listActiveQuests?limit=5",
        "https://api.layer3.io/api/trpc/quest.listActiveQuests?limit=5",
    ]
    for ep in endpoints:
        data = fetch(ep)
        if data:
            log("Layer3", f"API endpoint works: {ep.split('/api')[0]}")
            try:
                j = json.loads(data)
                quests = j.get("result", {}).get("data", {}).get("json", [])
                if quests:
                    log("Layer3", f"{len(quests)} active quests!")
                    for q in quests[:5]:
                        title = q.get("title", q.get("name", "Unnamed"))
                        log("Layer3", f"  • {title}")
                    return
            except:
                log("Layer3", f"Response received but couldn't parse")
                return
    log("Layer3", "No API endpoints responded")

def scrape_galxe():
    """Try Galxe API"""
    # Galxe uses GraphQL
    data = fetch("https://api.galxe.com/", {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    })
    if data:
        log("Galxe", "API accessible")
    else:
        log("Galxe", "API not accessible directly")
    
    # Check main page for campaigns
    html = fetch("https://galxe.com/campaigns", {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    })
    if html and len(html) > 1000:
        log("Galxe", "Campaigns page accessible ✓")
        # Try to extract campaign names
        titles = re.findall(r'<h[23][^>]*>([^<]{10,80})</h[23]>', html)
        for t in titles[:5]:
            log("Galxe", f"  • {t.strip()}")
    else:
        log("Galxe", "Campaigns page not accessible")

def scrape_free_pm():
    """Scrape Freelance job boards for quick gigs"""
    # Check Upwork RSS
    data = fetch("https://www.upwork.com/ab/feed/topics/rss?cat=web-mobile-software-dev")
    if data and "xml" in data[:100].lower():
        # Extract job titles
        titles = re.findall(r'<title><!\[CDATA\[([^\]]+)\]\]></title>', data)
        titles = titles[:5] if len(titles) > 5 else titles
        if titles:
            log("Upwork", f"{len(titles)} recent dev jobs")
            for t in titles[:3]:
                log("Upwork", f"  • {t[:100]}")
    else:
        log("Upwork", "RSS feed not accessible")
    
    # Check peopleperhour
    html = fetch("https://www.peopleperhour.com/freelance-jobs")
    if html:
        log("PeoplePerHour", "Jobs page accessible")
        titles = re.findall(r'<h3[^>]*>([^<]{15,100})</h3>', html)
        for t in titles[:3]:
            log("PeoplePerHour", f"  • {t.strip()}")
    else:
        log("PeoplePerHour", "Not accessible")

def suggest_actions():
    """Generate actionable next steps based on findings"""
    print("\n" + "=" * 60)
    print("🎯 ACTIONABLE NEXT STEPS")
    print("=" * 60)
    print("""
1️⃣  REDDIT GIGS — Reply to posts above with your offer
    • Data entry: $5-10/hr
    • Translation EN→ID: $10-20/1000words
    • Virtual assistant: $5-15/hr

2️⃣  TESTNET FARMING (free money)
    • Go to https://www.alchemy.com/faucets → claim Sepolia ETH
    • Bridge to zkSync/Base/Scroll testnet
    • Do swaps on testnet DEX → farm points → redeem later

3️⃣  FREELANCE REGISTRATION
    • Upwork.com — Create profile, bid on EN→ID translation
    • Fiverr.com — Gig: "I will translate 1000 words ENG to ID for $5"
    • PeoplePerHour — Similar

4️⃣  QUICK MICRO TASKS
    • r/slavelabour — Sort by new, be first to reply
    • Appen/OneForma — AI training tasks ($5-12/hr)
    • Clickworker — Micro tasks ($1-5/task)
""")

if __name__ == "__main__":
    print("=" * 60)
    print("💰 BREACH INCOME PIPELINE v1.0")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\n📡 Scraping Reddit...")
    scrape_reddit("slavelabour", "paypal crypto usd bitcoin")
    scrape_reddit("beermoney", "paypal free crypto")
    scrape_reddit("forhire", "paypal usd")
    
    print("\n🌐 Checking Crypto Platforms...")
    scrape_layer3_quests()
    scrape_galxe()
    
    print("\n💼 Checking Freelance Boards...")
    scrape_free_pm()
    
    print("\n" + "=" * 60)
    for r in RESULTS:
        print(r)
    
    suggest_actions()
    
    # Save report
    report_path = f"{CACHE_DIR}/pipeline_report.txt"
    with open(report_path, "w") as f:
        f.write(f"BREACH Income Pipeline Report — {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n")
        f.write("\n".join(RESULTS))
        f.write("\n")
    print(f"\n📄 Report saved: {report_path}")
