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