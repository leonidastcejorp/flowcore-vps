"""
Registrar Module
================
Web form automation engine — configurable field mapping,
validation, and submission for multi-platform account workflows.

Designed for enterprise identity lifecycle management,
testing, and staging environment provisioning.

Supported targets:
  - discord.com/register
  - fiverr.com/join  
  - reddit.com/register
"""
import asyncio
import json
import os
import random
import sys
from datetime import datetime

from flowcore.core.browser import BrowserSession
from flowcore.utils.names import random_name, random_username, random_email, random_password

OUTPUT_DIR = os.path.expanduser("~/.flowcore/accounts")
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def register_discord(page, idx, verbose=True):
    """Register on Discord"""
    name = random_name()
    username = random_username(name)
    email = random_email()
    pw = random_password()
    
    if verbose:
        print(f"  [{idx}] → discord.com/register")
    
    await page.goto('https://discord.com/register', wait_until='networkidle', timeout=20000)
    await asyncio.sleep(random.uniform(1, 3))
    
    try:
        inputs = await page.query_selector_all('input')
        if len(inputs) >= 3:
            await inputs[0].fill(email)
            await asyncio.sleep(random.uniform(0.3, 0.8))
            await inputs[1].fill(username)
            await asyncio.sleep(random.uniform(0.3, 0.8))
            await inputs[2].fill(pw)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Birthday selectors
            selects = await page.query_selector_all('select')
            if len(selects) >= 3:
                await selects[0].select_option(str(random.randint(1, 12)))
                await selects[1].select_option(str(random.randint(1, 28)))
                await selects[2].select_option(str(random.randint(1990, 2005)))
            
            await asyncio.sleep(1)
            
            return {
                'site': 'discord',
                'email': email,
                'username': username,
                'password': pw,
                'name': name,
                'status': 'submitted',
                'timestamp': datetime.now().isoformat(),
            }
        return {'site': 'discord', 'status': 'form_not_found'}
    except Exception as e:
        return {'site': 'discord', 'status': 'error', 'detail': str(e)[:80]}


async def register_fiverr(page, idx, verbose=True):
    """Register on Fiverr (Turnstile protected)"""
    name = random_name()
    username = random_username(name)
    email = random_email()
    pw = random_password()
    
    if verbose:
        print(f"  [{idx}] → fiverr.com/join")
    
    # Check if blocked first
    await page.goto('https://www.fiverr.com/join', wait_until='domcontentloaded', timeout=20000)
    await asyncio.sleep(2)
    
    body_text = await page.evaluate('() => document.body.innerText.substring(0, 200)')
    if 'human touch' in body_text.lower() or 'blocked' in body_text.lower():
        return {'site': 'fiverr', 'status': 'blocked', 'detail': 'IP/proxy blocked'}
    
    try:
        await page.fill('input[name="email"]', email)
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', pw)
        await asyncio.sleep(random.uniform(1, 2))
        await page.click('button[type="submit"]')
        await asyncio.sleep(3)
        
        return {
            'site': 'fiverr',
            'email': email,
            'username': username,
            'password': pw,
            'name': name,
            'status': 'submitted',
            'timestamp': datetime.now().isoformat(),
        }
    except Exception as e:
        return {'site': 'fiverr', 'status': 'error', 'detail': str(e)[:80]}


async def register_reddit(page, idx, verbose=True):
    """Register on Reddit"""
    name = random_name()
    username = random_username(name)
    email = random_email()
    pw = random_password()
    
    if verbose:
        print(f"  [{idx}] → reddit.com/register")
    
    await page.goto('https://www.reddit.com/register/', wait_until='networkidle', timeout=20000)
    await asyncio.sleep(2)
    
    # Check block
    text = await page.evaluate('() => document.body.innerText.substring(0, 200)')
    if 'blocked' in text.lower() or 'security' in text.lower():
        return {'site': 'reddit', 'status': 'blocked', 'detail': 'IP blocked'}
    
    try:
        await page.fill('input[name="email"]', email)
        await asyncio.sleep(0.3)
        await page.fill('input[name="username"]', username)
        await asyncio.sleep(0.3)
        await page.fill('input[name="password"]', pw)
        await asyncio.sleep(1)
        await page.click('button[type="submit"]')
        await asyncio.sleep(3)
        
        return {
            'site': 'reddit',
            'email': email,
            'username': username,
            'password': pw,
            'name': name,
            'status': 'submitted',
            'timestamp': datetime.now().isoformat(),
        }
    except Exception as e:
        return {'site': 'reddit', 'status': 'error', 'detail': str(e)[:80]}


# Registry of supported platforms
REGISTRY = {
    'discord': register_discord,
    'fiverr': register_fiverr,
    'reddit': register_reddit,
}


async def run(targets=None, count=1, proxy=None, verbose=True):
    """
    Run account registration workflow.
    
    Args:
        targets: List of site keys (None = all)
        count: Number of accounts per target
        proxy: Optional proxy string
        verbose: Print progress
    
    Returns:
        List of registration results
    """
    if targets is None:
        targets = list(REGISTRY.keys())
    elif isinstance(targets, str):
        targets = [targets]
    
    results = []
    session = BrowserSession(proxy=proxy)
    
    try:
        _, _, page = await session.launch()
        
        for idx in range(1, count + 1):
            for target in targets:
                if target in REGISTRY:
                    result = await REGISTRY[target](page, idx, verbose)
                    results.append(result)
                    await asyncio.sleep(random.uniform(2, 4))
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(OUTPUT_DIR, f"accounts_{timestamp}.json")
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        if verbose:
            print(f"\n📄 Saved: {filepath}")
        
    finally:
        await session.close()
    
    return results


if __name__ == "__main__":
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FlowCore Registrar — Form automation engine")
    parser.add_argument('--site', default='all', help='Target site (discord, fiverr, reddit, or all)')
    parser.add_argument('--count', type=int, default=1, help='Number of accounts to create')
    parser.add_argument('--proxy', help='Proxy server (host:port)')
    
    args = parser.parse_args()
    
    targets = list(REGISTRY.keys()) if args.site == 'all' else [args.site]
    print(f"🎯 Target(s): {', '.join(targets)}")
    print(f"📦 Count: {args.count}")
    print(f"🌐 Proxy: {args.proxy or 'direct'}")
    
    asyncio.run(run(targets=targets, count=args.count, proxy=args.proxy))
