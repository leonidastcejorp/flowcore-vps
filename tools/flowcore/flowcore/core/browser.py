"""
FlowCore Browser Engine
=======================
Playwright wrapper with stealth configuration, fingerprint spoofing,
and proxy rotation support for automated web operations.
"""
import asyncio
import random
from playwright.async_api import async_playwright

# Default stealth script — normalizes browser fingerprint
STEALTH_SCRIPT = """
// Remove automation indicators
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// Add plugin array (headless has 0, real browsers have 3-5)
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// Chrome runtime object
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {},
    webstore: undefined
};

// Override permissions query
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
    Promise.resolve({state: 'denied'}) :
    originalQuery(parameters)
);

// Normalize WebGL vendor strings (datacenter GPUs give away headless)
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(param) {
    if (param === 37445) return 'Intel Inc.';
    if (param === 37446) return 'Intel Iris OpenGL Engine';
    return getParameter.call(this, param);
};

// Screen properties
Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
"""

# User-agent pool
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
]

VIEWPORTS = [
    {'width': 1920, 'height': 1080},
    {'width': 1366, 'height': 768},
    {'width': 1536, 'height': 864},
    {'width': 1440, 'height': 900},
    {'width': 1280, 'height': 720},
]

LOCALES = ['en-US', 'en-GB', 'id-ID', 'en', 'ms-MY']
TIMEZONES = ['Asia/Jakarta', 'Asia/Singapore', 'Asia/Makassar', 'America/New_York']


class BrowserSession:
    """
    Managed browser session with stealth and proxy support.
    
    Usage:
        session = BrowserSession()
        browser, context, page = await session.launch()
        # ... do work ...
        await session.close()
    """
    
    def __init__(self, proxy=None, headless=True):
        self.proxy = proxy
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self._playwright = None
    
    async def launch(self):
        """Launch browser with stealth configuration"""
        self._playwright = await async_playwright().start()
        
        # Randomize fingerprint
        ua = random.choice(USER_AGENTS)
        vp = random.choice(VIEWPORTS)
        locale = random.choice(LOCALES)
        tz = random.choice(TIMEZONES)
        chrome_ver = random.choice(['125', '126'])
        platform = random.choice(['Windows', 'macOS', 'Linux'])
        
        # Launch args
        launch_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
        ]
        
        proxy_config = None
        if self.proxy:
            proxy_config = {'server': f'http://{self.proxy}'}
            if '@' in str(self.proxy):
                parts = self.proxy.split('@')
                auth = parts[0]
                server = parts[1]
                if ':' in auth:
                    user, pw = auth.split(':', 1)
                    proxy_config = {
                        'server': f'http://{server}',
                        'username': user,
                        'password': pw
                    }
        
        self.browser = await self._playwright.chromium.launch(
            headless=self.headless,
            executable_path='/root/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome',
            args=launch_args,
            proxy=proxy_config,
        )
        
        self.context = await self.browser.new_context(
            viewport=vp,
            user_agent=ua,
            locale=locale,
            timezone_id=tz,
            extra_http_headers={
                'Accept-Language': f'{locale},en;q=0.9,id;q=0.8',
                'Sec-Ch-Ua': f'"Chromium";v="{chrome_ver}", "Not.A/Brand";v="24"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': f'"{platform}"',
            }
        )
        
        # Inject stealth
        await self.context.add_init_script(STEALTH_SCRIPT)
        self.page = await self.context.new_page()
        
        return self.browser, self.context, self.page
    
    async def close(self):
        """Clean shutdown"""
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
