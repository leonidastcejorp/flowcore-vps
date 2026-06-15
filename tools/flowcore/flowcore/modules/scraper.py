"""
Scraper Module
==============
Intelligent data collection engine with anti-detection,
rate limiting, and structured output formatting.
"""
import asyncio
import json
import os
import time
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/.flowcore/scrapes")
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def scrape_page(page, url, selectors=None):
    """
    Scrape a page with anti-detection delays.
    
    Args:
        page: Playwright page object
        url: Target URL
        selectors: CSS selectors to extract (default: body text)
    
    Returns:
        Dict with scraped content
    """
    await page.goto(url, wait_until='networkidle', timeout=30000)
    await asyncio.sleep(2)
    
    result = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'title': await page.title(),
    }
    
    if selectors:
        for name, selector in selectors.items():
            try:
                elements = await page.query_selector_all(selector)
                result[name] = [await el.inner_text() for el in elements[:10]]
            except:
                result[name] = []
    else:
        result['text'] = await page.evaluate('() => document.body.innerText.substring(0, 5000)')
    
    return result


def save_results(data, name="scrape"):
    """Save scraped data to file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(OUTPUT_DIR, f"{name}_{timestamp}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    return filepath
