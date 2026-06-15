"""
Watcher Module
==============
Scheduled pipeline monitoring — automated data collection,
web scraping, and opportunity tracking workflows.
"""
import asyncio
import json
import os
import re
import urllib.request
import urllib.parse
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/.flowcore/reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch(url, headers=None):
    """Simple HTTP GET with timeout"""
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'
        }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8', errors='replace')
    except:
        return None


def scrape_opportunities():
    """
    Scrape various sources for work/freelance opportunities.
    Returns structured report data.
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'sources': {},
    }
    
    # Reddit r/slavelabour
    try:
        url = 'https://www.reddit.com/r/slavelabour/search.json?q=paypal+usd+task&restrict_sr=on&sort=new&limit=10'
        data = fetch(url, {'User-Agent': 'Mozilla/5.0 Python/3.11'})
        if data:
            j = json.loads(data)
            posts = j.get('data', {}).get('children', [])
            report['sources']['slavelabour'] = [
                {
                    'title': p.get('data', {}).get('title', ''),
                    'score': p.get('data', {}).get('score', 0),
                    'url': p.get('data', {}).get('url', ''),
                }
                for p in posts[:5]
            ]
    except:
        report['sources']['slavelabour'] = []
    
    # Reddit r/beermoney
    try:
        url = 'https://www.reddit.com/r/beermoney/search.json?q=free+crypto+paypal&restrict_sr=on&sort=new&limit=5'
        data = fetch(url, {'User-Agent': 'Mozilla/5.0 Python/3.11'})
        if data:
            j = json.loads(data)
            posts = j.get('data', {}).get('children', [])
            report['sources']['beermoney'] = [
                {
                    'title': p.get('data', {}).get('title', ''),
                    'score': p.get('data', {}).get('score', 0),
                    'url': p.get('data', {}).get('url', ''),
                }
                for p in posts[:5]
            ]
    except:
        report['sources']['beermoney'] = []
    
    return report


def generate_report(report):
    """Generate a formatted report from pipeline data"""
    lines = []
    lines.append("=" * 55)
    lines.append("📊 FLOWCORE PIPELINE REPORT")
    lines.append(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 55)
    
    for source, items in report.get('sources', {}).items():
        if items:
            lines.append(f"\n📌 r/{source}:")
            for item in items[:3]:
                lines.append(f"   • [{item.get('score', 0)}] {item.get('title', '')[:100]}")
        else:
            lines.append(f"\n📌 r/{source}: No results")
    
    lines.append("\n" + "=" * 55)
    lines.append("📋 Tips:")
    lines.append("  1. Check testnet faucets for free crypto")
    lines.append("  2. Try freelancer platforms (Fiverr, Upwork)")
    lines.append("  3. Complete Galxe/Layer3 quests")
    lines.append("=" * 55)
    
    return '\n'.join(lines)


def run():
    """Execute the watcher pipeline and return a report string"""
    report = scrape_opportunities()
    output = generate_report(report)
    
    # Save report
    filepath = os.path.join(OUTPUT_DIR, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(filepath, 'w') as f:
        f.write(output)
    
    return output


if __name__ == "__main__":
    print(run())
