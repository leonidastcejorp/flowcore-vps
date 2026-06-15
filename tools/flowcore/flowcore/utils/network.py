"""
Proxy Manager
=============
Automated proxy pool management with health checks,
rotation, and dynamic sourcing from public lists.
"""
import asyncio
import random
import os

PROXY_DIR = os.path.expanduser("~/.flowcore/proxies")
ALIVE_FILE = os.path.join(PROXY_DIR, "alive.txt")
SOURCES = [
    ("databay-http", "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt"),
    ("databay-socks5", "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt"),
    ("r00tee-https", "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt"),
    ("r00tee-socks5", "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt"),
]


class ProxyPool:
    """
    Rotating proxy pool with automatic health checks.
    Maintains a list of verified proxies for browser/request use.
    """
    
    def __init__(self):
        self.proxies = []
        self._load()
    
    def _load(self):
        """Load alive proxies from cache"""
        if os.path.exists(ALIVE_FILE):
            with open(ALIVE_FILE) as f:
                self.proxies = [l.strip() for l in f if l.strip()]
    
    def get_random(self):
        """Get a random alive proxy"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def get_rotating(self):
        """Generator that cycles through proxies"""
        while True:
            if not self.proxies:
                yield None
            yield random.choice(self.proxies)
    
    async def refresh(self, max_test=200):
        """Download fresh proxy lists and test them"""
        import aiohttp
        
        # Download
        all_proxies = set()
        async with aiohttp.ClientSession() as session:
            for name, url in SOURCES:
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r:
                        text = await r.text()
                        for line in text.strip().split('\n'):
                            p = line.strip()
                            if p and ':' in p:
                                all_proxies.add(p)
                except:
                    pass
        
        # Test alive
        alive = []
        sem = asyncio.Semaphore(50)
        
        async def test(proxy):
            async with sem:
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.get(
                            "https://httpbin.org/ip",
                            proxy=f"http://{proxy}",
                            timeout=aiohttp.ClientTimeout(total=8)
                        ) as r:
                            if r.status == 200:
                                return proxy
                except:
                    pass
                return None
        
        tasks = [test(p) for p in list(all_proxies)[:max_test]]
        results = await asyncio.gather(*tasks)
        self.proxies = [p for p in results if p]
        
        # Save
        os.makedirs(PROXY_DIR, exist_ok=True)
        with open(ALIVE_FILE, 'w') as f:
            f.write('\n'.join(self.proxies))
        
        return self.proxies
