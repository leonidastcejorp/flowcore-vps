"""
Fingerprint Engine
==================
Browser fingerprint spoofing and randomization.
Provides identity profiles that mimic real user configurations.
"""
import random

PROFILES = {
    "windows_chrome": {
        "platform": "Windows",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": (1920, 1080),
    },
    "mac_chrome": {
        "platform": "macOS",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": (1440, 900),
    },
    "linux_chrome": {
        "platform": "Linux",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": (1366, 768),
    },
}


class IdentityProfile:
    """Represents a browser identity with randomized fingerprint attributes."""
    
    def __init__(self, profile_type=None):
        if profile_type and profile_type in PROFILES:
            base = PROFILES[profile_type].copy()
        else:
            base = random.choice(list(PROFILES.values()))
        
        self.platform = base["platform"]
        self.user_agent = base["user_agent"]
        self.viewport = base["viewport"]
        self.locale = random.choice(['en-US', 'en-GB', 'id-ID', 'ms-MY'])
        self.timezone = random.choice(['Asia/Jakarta', 'Asia/Singapore', 'Asia/Makassar'])
        self.chrome_version = random.choice(['125', '126'])
        self.language = self.locale.split('-')[0]
    
    def to_dict(self):
        return {
            'platform': self.platform,
            'user_agent': self.user_agent,
            'viewport': self.viewport,
            'locale': self.locale,
            'timezone': self.timezone,
        }
