#!/usr/bin/env python3
"""
Proxy Pool Updater
==================
Downloads fresh proxy lists from public sources and tests them.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from flowcore.utils.network import ProxyPool

async def main():
    print("🔄 Refreshing proxy pool...")
    pool = ProxyPool()
    alive = await pool.refresh(max_test=300)
    print(f"✅ Found {len(alive)} alive proxies")
    if alive:
        print(f"   Sample: {', '.join(alive[:5])}")

if __name__ == "__main__":
    asyncio.run(main())
