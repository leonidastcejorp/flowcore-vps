#!/usr/bin/env python3
"""
🔄 Proxy Auto-Updater — Downloads + Tests free proxies from GitHub
Runs every 6 hours, keeps ~50-100 alive proxies ready
"""
import asyncio
import aiohttp
import os
import json
from datetime import datetime

PROXY_DIR = "/root/bounty_output/proxies"
ALIVE_FILE = f"{PROXY_DIR}/alive.txt"
SOURCES = {
    "databay-http": "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt",
    "databay-socks5": "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt",
    "r00tee-https": "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt",
    "r00tee-socks5": "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt",
}

async def download_proxies():
    """Download proxy lists from all sources"""
    all_proxies = set()
    async with aiohttp.ClientSession() as session:
        for name, url in SOURCES.items():
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                    text = await r.text()
                    count = 0
                    for line in text.strip().split('\n'):
                        p = line.strip()
                        if p and ':' in p:
                            all_proxies.add(p)
                            count += 1
                    print(f"  📥 {name}: {count} proxies")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
    
    print(f"\n  📦 Total unique: {len(all_proxies)}")
    return list(all_proxies)

async def test_proxy(session, proxy, sem):
    async with sem:
        for proto in ['http', 'socks5']:
            try:
                async with session.get(
                    "https://httpbin.org/ip",
                    proxy=f"{proto}://{proxy}",
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        return (proxy, data.get('origin', '?'), True)
            except:
                pass
    return (proxy, None, False)

async def main():
    os.makedirs(PROXY_DIR, exist_ok=True)
    
    print(f"\n{'='*50}")
    print(f"🔄 PROXY UPDATER — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    
    print("\n📥 Downloading proxies...")
    all_proxies = await download_proxies()
    
    print(f"\n🔍 Testing top 500 proxies...")
    sem = asyncio.Semaphore(100)
    
    # Save raw first
    with open(f"{PROXY_DIR}/raw_all.txt", 'w') as f:
        f.write('\n'.join(all_proxies))
    
    alive = []
    async with aiohttp.ClientSession() as session:
        tasks = [test_proxy(session, p, sem) for p in all_proxies[:500]]
        results = await asyncio.gather(*tasks)
        
        for proxy, ip, ok in results:
            if ok:
                alive.append(proxy)
    
    print(f"\n  ✅ Alive: {len(alive)}/{min(len(all_proxies), 500)}")
    
    if alive:
        with open(ALIVE_FILE, 'w') as f:
            f.write('\n'.join(alive))
        print(f"\n  💾 Saved {len(alive)} alive proxies to {ALIVE_FILE}")
        print(f"\n  🌐 Sample:")
        for p in alive[:5]:
            print(f"    • {p}")
    else:
        print("\n  ❌ No alive proxies found")

if __name__ == "__main__":
    asyncio.run(main())
