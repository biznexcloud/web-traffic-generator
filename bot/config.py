import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# ==================== CONFIG ====================

# Target Website
TARGET_URL = os.getenv("TARGET_URL", "https://restromandu.com")

# Proxy Settings
# Support for authenticated proxies: "http://user:pass@host:port" or "socks5://user:pass@host:port"
# Leave empty to only use free scraped proxies
PREMIUM_PROXIES = [] 

# 31 Core SEO Keywords — RestroMandu (2026)
KEYWORDS = [
    "restromandu",
    "restromandu.com",
    "restro mandu",
    "restromandu restaurant software",
    "restromandu restaurant management system",
    "restromandu restaurant ERP",
    "restromandu POS",
    "restromandu restaurant POS",
    "restromandu billing",
    "restromandu Nepal",

    "restaurant management system Nepal",
    "restaurant management software Nepal",
    "restaurant ERP Nepal",
    "restaurant ERP software Nepal",
    "restaurant software Nepal",
    "restaurant software in Nepal",

    "best restaurant management system Nepal",
    "best restaurant management software Nepal",
    "best restaurant ERP Nepal",
    "best restaurant POS Nepal",
    "restaurant POS software Nepal",
    "restaurant billing software Nepal",

    "restaurant inventory management software Nepal",
    "restaurant procurement software Nepal",
    "restaurant recipe costing software Nepal",
    "restaurant food costing software Nepal",
    "restaurant KOT software Nepal",
    "restaurant KDS software Nepal",
    "restaurant table management software Nepal",
    "restaurant online ordering software Nepal",
    "restaurant accounting software Nepal",
]

# ponytail: basic casts only; add schema validator if complex types needed
_env_keywords = os.getenv("KEYWORDS")
if _env_keywords and _env_keywords.strip():
    KEYWORDS = [k.strip() for k in _env_keywords.split(",") if k.strip()]

# Threading & Performance
THREADS = int(os.getenv("THREADS", 21))
PROXY_ROTATE_INTERVAL = int(os.getenv("PROXY_ROTATE_INTERVAL", 1800))  # seconds
PORT = int(os.getenv("PORT", 5000))

# Behavior Timing (seconds)
DWELL_MIN = int(os.getenv("DWELL_MIN", 60))
DWELL_MAX = int(os.getenv("DWELL_MAX", 180))
GOOGLE_WAIT_MIN = int(os.getenv("GOOGLE_WAIT_MIN", 10))
GOOGLE_WAIT_MAX = int(os.getenv("GOOGLE_WAIT_MAX", 30))

OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "SEO_BOOSTER_2025")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Admin Credentials
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "Ramesh@5611")

# --------------- Traffic Source Distribution ---------------
TRAFFIC_SOURCES = {
    "google_organic": 0.60,
    "social_referral": 0.20,
    "ai_assistant": 0.10,
    "other_organic": 0.10,
}

SOCIAL_REFERRERS = [
    {"referer": "https://www.facebook.com/", "utm_source": "facebook", "utm_medium": "social"},
    {"referer": "https://www.linkedin.com/feed/", "utm_source": "linkedin.com", "utm_medium": "referral"},
    {"referer": "https://t.co/abc123", "utm_source": "twitter", "utm_medium": "social"},
    {"referer": "https://www.linkedin.com/posts/", "utm_source": "linkedin", "utm_medium": "social"},
]

AI_REFERRERS = [
    {"referer": "https://chatgpt.com/", "utm_source": "chatgpt.com", "utm_medium": "ai-assistant"},
]

OTHER_SEARCH_ENGINES = [
    {"referer": "https://www.bing.com/", "engine": "bing"},
    {"referer": "https://duckduckgo.com/", "engine": "duckduckgo"},
]

# --------------- Multi-Page Navigation ---------------
INTERNAL_PATHS = ["/news/", "/about/", "/contact/"]
PAGES_PER_SESSION_MIN = int(os.getenv("PAGES_PER_SESSION_MIN", 2))
PAGES_PER_SESSION_MAX = int(os.getenv("PAGES_PER_SESSION_MAX", 5))

# --------------- Device / Browser Diversity ---------------
DEVICE_PROFILES = [
    {"weight": 50, "platform": "desktop", "os": "Windows", "browser": "Chrome",
     "ua_tpl": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36",
     "resolutions": ["1920x1080", "1366x768", "1536x864", "1440x900", "1280x720"]},
    {"weight": 10, "platform": "desktop", "os": "Macintosh", "browser": "Chrome",
     "ua_tpl": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36",
     "resolutions": ["1440x900", "1920x1080", "2560x1440"]},
    {"weight": 8, "platform": "desktop", "os": "Macintosh", "browser": "Safari",
     "ua_tpl": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.{minor} Safari/605.1.15",
     "resolutions": ["1440x900", "1920x1080"]},
    {"weight": 5, "platform": "desktop", "os": "Linux", "browser": "Chrome",
     "ua_tpl": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36",
     "resolutions": ["1920x1080", "1366x768"]},
    {"weight": 15, "platform": "mobile", "os": "Android", "browser": "Chrome",
     "ua_tpl": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Mobile Safari/537.36",
     "resolutions": ["412x915", "393x873", "360x800"]},
    {"weight": 12, "platform": "mobile", "os": "iOS", "browser": "Safari",
     "ua_tpl": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.{minor} Mobile/15E148 Safari/604.1",
     "resolutions": ["393x852", "390x844", "414x896"]},
]