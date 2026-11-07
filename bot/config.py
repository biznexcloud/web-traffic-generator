import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# ==================== CONFIG ====================

# Target Website (normalized with trailing slash for canonical GA4 paths)
_raw_target = os.getenv("TARGET_URL", "https://restromandu.com").strip()
TARGET_URL = _raw_target if _raw_target.endswith("/") else f"{_raw_target}/"

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
THREADS = int(os.getenv("THREADS", 31))
PROXY_ROTATE_INTERVAL = int(os.getenv("PROXY_ROTATE_INTERVAL", 1800))  # seconds
PORT = int(os.getenv("PORT", 5000))

# Behavior Timing (seconds)
DWELL_MIN = int(os.getenv("DWELL_MIN", 90))
DWELL_MAX = int(os.getenv("DWELL_MAX", 300))
INTERNAL_DWELL_MIN = int(os.getenv("INTERNAL_DWELL_MIN", 45))
INTERNAL_DWELL_MAX = int(os.getenv("INTERNAL_DWELL_MAX", 120))
GOOGLE_WAIT_MIN = int(os.getenv("GOOGLE_WAIT_MIN", 10))
GOOGLE_WAIT_MAX = int(os.getenv("GOOGLE_WAIT_MAX", 30))

OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "SEO_BOOSTER_2025")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Admin Credentials
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "Ramesh@5611")

# --------------- Traffic Source Distribution (100% Non-Direct) ---------------
TRAFFIC_SOURCES = {
    "google_organic": 0.50,
    "social_referral": 0.15,
    "ai_assistant": 0.20,
    "other_organic": 0.15,
}

# AI Assistant Referrers (Expanded - 12 sources with weights)
AI_REFERRERS = [
    # Tier 1: Major AI assistants (higher weight)
    {"referer": "https://chatgpt.com/", "utm_source": "chatgpt.com", "utm_medium": "ai-assistant", "weight": 25},
    {"referer": "https://claude.ai/", "utm_source": "claude.ai", "utm_medium": "ai-assistant", "weight": 20},
    {"referer": "https://gemini.google.com/", "utm_source": "gemini.google.com", "utm_medium": "ai-assistant", "weight": 15},
    {"referer": "https://copilot.microsoft.com/", "utm_source": "copilot.microsoft.com", "utm_medium": "ai-assistant", "weight": 10},
    {"referer": "https://www.perplexity.ai/", "utm_source": "perplexity.ai", "utm_medium": "ai-assistant", "weight": 10},
    # Tier 2: Emerging AI assistants
    {"referer": "https://meta.ai/", "utm_source": "meta.ai", "utm_medium": "ai-assistant", "weight": 5},
    {"referer": "https://you.com/", "utm_source": "you.com", "utm_medium": "ai-assistant", "weight": 4},
    {"referer": "https://www.phind.com/", "utm_source": "phind.com", "utm_medium": "ai-assistant", "weight": 3},
    {"referer": "https://poe.com/", "utm_source": "poe.com", "utm_medium": "ai-assistant", "weight": 3},
    {"referer": "https://character.ai/", "utm_source": "character.ai", "utm_medium": "ai-assistant", "weight": 2},
    {"referer": "https://groq.com/", "utm_source": "groq.com", "utm_medium": "ai-assistant", "weight": 2},
    {"referer": "https://huggingface.co/chat/", "utm_source": "huggingface.co", "utm_medium": "ai-assistant", "weight": 1},
]

# Social Referrers (Expanded - 18 sources with weights)
SOCIAL_REFERRERS = [
    # Facebook/Meta
    {"referer": "https://www.facebook.com/", "utm_source": "facebook", "utm_medium": "social", "weight": 20},
    {"referer": "https://m.facebook.com/", "utm_source": "facebook", "utm_medium": "social", "weight": 5},
    {"referer": "https://l.facebook.com/", "utm_source": "facebook", "utm_medium": "social", "weight": 5},
    # Instagram
    {"referer": "https://www.instagram.com/", "utm_source": "instagram", "utm_medium": "social", "weight": 15},
    {"referer": "https://instagram.com/", "utm_source": "instagram", "utm_medium": "social", "weight": 5},
    # X/Twitter
    {"referer": "https://x.com/", "utm_source": "x.com", "utm_medium": "social", "weight": 15},
    {"referer": "https://t.co/", "utm_source": "t.co", "utm_medium": "social", "weight": 5},
    # LinkedIn
    {"referer": "https://www.linkedin.com/feed/", "utm_source": "linkedin", "utm_medium": "social", "weight": 10},
    {"referer": "https://www.linkedin.com/posts/", "utm_source": "linkedin", "utm_medium": "social", "weight": 5},
    {"referer": "https://lnkd.in/", "utm_source": "linkedin", "utm_medium": "social", "weight": 3},
    # Reddit
    {"referer": "https://www.reddit.com/r/restaurant/", "utm_source": "reddit", "utm_medium": "social", "weight": 5},
    {"referer": "https://www.reddit.com/r/Nepal/", "utm_source": "reddit", "utm_medium": "social", "weight": 3},
    {"referer": "https://www.reddit.com/r/smallbusiness/", "utm_source": "reddit", "utm_medium": "social", "weight": 2},
    # YouTube
    {"referer": "https://www.youtube.com/", "utm_source": "youtube", "utm_medium": "social", "weight": 5},
    # Pinterest
    {"referer": "https://www.pinterest.com/", "utm_source": "pinterest", "utm_medium": "social", "weight": 3},
    # Quora
    {"referer": "https://www.quora.com/", "utm_source": "quora", "utm_medium": "social", "weight": 2},
    # Medium
    {"referer": "https://medium.com/", "utm_source": "medium", "utm_medium": "social", "weight": 2},
    # GitHub (developer traffic)
    {"referer": "https://github.com/", "utm_source": "github", "utm_medium": "referral", "weight": 1},
]

# Other Search Engines (Expanded - 10 sources with weights)
OTHER_SEARCH_ENGINES = [
    {"referer": "https://www.bing.com/", "engine": "bing", "weight": 30},
    {"referer": "https://duckduckgo.com/", "engine": "duckduckgo", "weight": 25},
    {"referer": "https://search.yahoo.com/", "engine": "yahoo", "weight": 15},
    {"referer": "https://www.ecosia.org/", "engine": "ecosia", "weight": 8},
    {"referer": "https://search.brave.com/", "engine": "brave", "weight": 8},
    {"referer": "https://www.startpage.com/", "engine": "startpage", "weight": 5},
    {"referer": "https://swisscows.com/", "engine": "swisscows", "weight": 3},
    {"referer": "https://www.qwant.com/", "engine": "qwant", "weight": 3},
    {"referer": "https://search.naver.com/", "engine": "naver", "weight": 2},
    {"referer": "https://www.seznam.cz/", "engine": "seznam", "weight": 1},
]

# Returning User Simulation (Authentic Cohort Retention)
RETURNING_USER_RATIO = float(os.getenv("RETURNING_USER_RATIO", 0.25))
MAX_RETURNING_POOL_SIZE = int(os.getenv("MAX_RETURNING_POOL_SIZE", 2000))

# Cohort retention weights (Day 1, Day 7, Day 30)
RETURNING_COHORT_WEIGHTS = {
    "day_1": 0.40,    # 40% return within 24h
    "day_7": 0.35,    # 35% return within 7 days
    "day_30": 0.25,   # 25% return within 30 days
}

# Key Events / Conversion Simulation for Lead Generation
KEY_EVENT_PROBABILITY = float(os.getenv("KEY_EVENT_PROBABILITY", 0.15))

LEAD_PAGES = [
    "/contact/",
    "/start-free-trial/",
    "/demo/",
    "/pricing/",
    "/book-demo/",
    "/get-started/",
    "/free-trial/",
]

# --------------- Multi-Page Navigation ---------------
INTERNAL_PATHS = ["/news/", "/about/", "/contact/", "/pricing/", "/demo/", "/features/"]
PAGES_PER_SESSION_MIN = int(os.getenv("PAGES_PER_SESSION_MIN", 3))
PAGES_PER_SESSION_MAX = int(os.getenv("PAGES_PER_SESSION_MAX", 6))

# Target Countries for Geo-Targeting (RestroMandu markets)
TARGET_COUNTRIES = {
    "NP": 0.35,   # Nepal - primary
    "IN": 0.25,   # India - major market
    "BD": 0.10,   # Bangladesh
    "AE": 0.05,   # UAE
    "QA": 0.03,   # Qatar
    "SA": 0.03,   # Saudi Arabia
    "MY": 0.03,   # Malaysia
    "SG": 0.03,   # Singapore
    "TH": 0.03,   # Thailand
    "PH": 0.03,   # Philippines
    "LK": 0.02,   # Sri Lanka
    "US": 0.02,   # US (some legitimate traffic)
    "GB": 0.01,   # UK
    "AU": 0.01,   # Australia
}

# Language by Country for GA4 'ul' parameter
COUNTRY_LANGUAGES = {
    "NP": ["ne-NP", "en-US"],
    "IN": ["en-IN", "hi-IN", "en-US"],
    "BD": ["bn-BD", "en-US"],
    "AE": ["ar-AE", "en-US"],
    "QA": ["ar-QA", "en-US"],
    "SA": ["ar-SA", "en-US"],
    "MY": ["ms-MY", "en-US"],
    "SG": ["en-SG", "zh-CN", "ms-MY"],
    "TH": ["th-TH", "en-US"],
    "PH": ["en-PH", "tl-PH"],
    "LK": ["si-LK", "ta-LK", "en-US"],
    "US": ["en-US"],
    "GB": ["en-GB"],
    "AU": ["en-AU"],
}

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
    {"weight": 8, "platform": "desktop", "os": "Windows", "browser": "Edge",
     "ua_tpl": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36 Edg/{ver}",
     "resolutions": ["1920x1080", "1366x768", "1536x864"]},
    {"weight": 5, "platform": "desktop", "os": "Windows", "browser": "Firefox",
     "ua_tpl": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{ver}.0) Gecko/20100101 Firefox/{ver}.0",
     "resolutions": ["1920x1080", "1366x768"]},
    {"weight": 3, "platform": "desktop", "os": "Macintosh", "browser": "Firefox",
     "ua_tpl": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{ver}.0) Gecko/20100101 Firefox/{ver}.0",
     "resolutions": ["1440x900", "1920x1080"]},
    {"weight": 15, "platform": "mobile", "os": "Android", "browser": "Chrome",
     "ua_tpl": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Mobile Safari/537.36",
     "resolutions": ["412x915", "393x873", "360x800"]},
    {"weight": 5, "platform": "mobile", "os": "Android", "browser": "SamsungBrowser",
     "ua_tpl": "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/{ver}.0 Chrome/{ver} Mobile Safari/537.36",
     "resolutions": ["412x915", "393x873"]},
    {"weight": 12, "platform": "mobile", "os": "iOS", "browser": "Safari",
     "ua_tpl": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.{minor} Mobile/15E148 Safari/604.1",
     "resolutions": ["393x852", "390x844", "414x896"]},
]