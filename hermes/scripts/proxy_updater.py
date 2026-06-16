#!/usr/bin/env python3
"""
🔄 Proxy Auto-Updater — Downloads + Tests free proxies from multiple proven sources
Runs every 6 hours, keeps ~50-100 alive proxies ready
"""
import asyncio
import aiohttp
import os
import re
from datetime import datetime
from collections import defaultdict

PROXY_DIR = "/root/projects/bounty-output/proxies"
ALIVE_FILE = f"{PROXY_DIR}/alive.txt"
BATCH_SIZE = 200
PROXY_TIMEOUT = 5
MIN_ALIVE_THRESHOLD = 5
CONCURRENCY = 100

# Proven free proxy sources
SOURCES = {
    "shiftytr-http": "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "hookzof-socks5": "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "anonymous-http": "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
    "roosterkid-https": "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "proxyscrape-api": "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "jetkai-http": "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "prxchk-http": "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
}

# Regex to validate ip:port format
IP_PORT_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$")


def is_valid_proxy(proxy: str) -> bool:
    """Filter out obviously bad proxy formats (non-ip:port, empty, garbage)."""
    if not proxy or ":" not in proxy:
        return False
    proxy = proxy.strip()
    if not IP_PORT_RE.match(proxy):
        return False
    # Validate IP octets are in range 0-255
    parts = proxy.split(":")
    octets = parts[0].split(".")
    try:
        for octet in octets:
            val = int(octet)
            if val < 0 or val > 255:
                return False
        port = int(parts[1])
        if port < 1 or port > 65535:
            return False
    except ValueError:
        return False
    return True


async def download_proxies(session):
    """Download proxy lists from all sources. Returns dict: source_name -> [proxies]."""
    source_proxies = defaultdict(set)

    async def fetch_source(name, url):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                text = await r.text()
                count_before = len(source_proxies[name])
                # Plain text, one proxy per line
                for line in text.strip().split("\n"):
                    p = line.strip()
                    if is_valid_proxy(p):
                        source_proxies[name].add(p)
                count = len(source_proxies[name]) - count_before
                print(f"  📥 {name}: {count} proxy")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    tasks = [fetch_source(name, url) for name, url in SOURCES.items()]
    await asyncio.gather(*tasks)

    # Deduplicate across sources — build source->proxies mapping
    all_unique = set()
    for proxies in source_proxies.values():
        all_unique.update(proxies)

    print(f"\n  📦 Total proxy unik: {len(all_unique)}")
    return source_proxies, list(all_unique)


async def test_proxy(session, proxy, sem):
    """Test a single proxy against httpbin. Returns (proxy, source, True/False)."""
    async with sem:
        for proto in ["http", "https"]:
            try:
                async with session.get(
                    "https://httpbin.org/ip",
                    proxy=f"{proto}://{proxy}",
                    timeout=aiohttp.ClientTimeout(total=PROXY_TIMEOUT),
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        return (proxy, data.get("origin", "?"), True)
            except Exception:
                pass
    return (proxy, None, False)


async def main():
    os.makedirs(PROXY_DIR, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"🔄 PROXY UPDATER — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")

    print("\n📥 Download proxy dari sumber terkenal...")
    async with aiohttp.ClientSession() as session:
        source_proxies, all_proxies = await download_proxies(session)

        if not all_proxies:
            print("\n  ❌ Gagal download proxy dari semua sumber. Keluar.")
            return

        print(f"\n🔍 Test {BATCH_SIZE} proxy teratas (timeout: {PROXY_TIMEOUT}s per proxy)...")
        sem = asyncio.Semaphore(CONCURRENCY)

        # Save raw list
        with open(f"{PROXY_DIR}/raw_all.txt", "w") as f:
            f.write("\n".join(all_proxies))

        # Test batch
        to_test = all_proxies[:BATCH_SIZE]
        tasks = [test_proxy(session, p, sem) for p in to_test]
        results = await asyncio.gather(*tasks)

    # Process results
    alive = []
    source_alive = defaultdict(int)
    # Build reverse lookup: proxy -> source(s)
    proxy_to_sources = {}
    for src, proxies in source_proxies.items():
        for p in proxies:
            proxy_to_sources.setdefault(p, []).append(src)

    for proxy, ip, ok in results:
        if ok:
            alive.append(proxy)
            srcs = proxy_to_sources.get(proxy, ["unknown"])
            for s in srcs:
                source_alive[s] += 1

    print(f"\n  ✅ Hidup: {len(alive)}/{len(to_test)}")
    print(f"\n  📊 Ringkasan:")
    print(f"     Total dites:  {len(to_test)}")
    print(f"     Hidup:         {len(alive)}")
    print(f"     Mati:          {len(to_test) - len(alive)}")
    print(f"     Persentase:    {len(alive)/len(to_test)*100:.1f}%")

    if source_alive:
        print(f"\n  📂 Hidup per sumber:")
        for src in sorted(source_alive, key=source_alive.get, reverse=True):
            print(f"     • {src}: {source_alive[src]} hidup")

    if len(alive) >= MIN_ALIVE_THRESHOLD:
        with open(ALIVE_FILE, "w") as f:
            f.write("\n".join(alive))
        print(f"\n  💾 Disimpan {len(alive)} proxy hidup ke {ALIVE_FILE}")
        print(f"\n  🌐 Contoh:")
        for p in alive[:5]:
            print(f"    • {p}")
    else:
        print(f"\n  ⚠️  Cuma {len(alive)} proxy hidup (minimal {MIN_ALIVE_THRESHOLD}). Gak disimpan.")
        print("     Pakai proxy lama kalo ada.")


if __name__ == "__main__":
    asyncio.run(main())
