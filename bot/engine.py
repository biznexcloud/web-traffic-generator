import os
import random
import time
import csv
import threading
import concurrent.futures
import re
import json
from datetime import datetime
from typing import Optional, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
from curl_cffi import requests
from curl_cffi.requests import BrowserType

from bot.config import (
    TARGET_URL, KEYWORDS, THREADS, OUTPUT_FOLDER,
    PROXY_ROTATE_INTERVAL, PREMIUM_PROXIES,
    DWELL_MIN, DWELL_MAX, INTERNAL_DWELL_MIN, INTERNAL_DWELL_MAX, GOOGLE_WAIT_MIN, GOOGLE_WAIT_MAX,
    TRAFFIC_SOURCES, SOCIAL_REFERRERS, AI_REFERRERS,
    OTHER_SEARCH_ENGINES, INTERNAL_PATHS,
    PAGES_PER_SESSION_MIN, PAGES_PER_SESSION_MAX, DEVICE_PROFILES,
    RETURNING_USER_RATIO, KEY_EVENT_PROBABILITY, MAX_RETURNING_POOL_SIZE,
    LEAD_PAGES, RETURNING_COHORT_WEIGHTS,
)
from bot.logger import logger


class SEOBoosterBot:
    def __init__(self):
        # Stats Initialization - Individual attributes with type hints
        self.total_visits: int = 0
        self.successful_visits: int = 0
        self.search_clicks: int = 0
        self.analytics_fired_count: int = 0
        self.unique_countries: set = set()
        self.unique_pages: set = set()
        self.start_time: Optional[datetime] = None
        self.stats_lock = threading.Lock()

        self.working_proxies = []
        self.proxy_lock = threading.Lock()

        self.is_running = False
        self.stop_event = threading.Event()
        self.threads = []

        # Cached GA4 measurement ID
        self._ga4_tid: Optional[str] = None
        self._ga4_tid_lock = threading.Lock()

        # Returning user profile pool (for authentic cohort retention)
        self.returning_profiles = []
        self.returning_lock = threading.Lock()
        self.max_returning_pool_size = MAX_RETURNING_POOL_SIZE
        self.returning_profiles_path = os.path.join(OUTPUT_FOLDER, "returning_profiles.json")
        self.load_returning_profiles()

        # Init CSV LOG
        self.log_path = os.path.join(OUTPUT_FOLDER, "traffic_log.csv")
        if not os.path.exists(self.log_path):
            try:
                with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow(["Time", "Type", "Page", "IP", "Country", "Dwell", "Analytics Fired"])
            except Exception as e:
                logger.error(f"Failed to initialize log file: {e}")

    def load_returning_profiles(self):
        """Load returning user profiles from disk."""
        try:
            if os.path.exists(self.returning_profiles_path):
                with open(self.returning_profiles_path, 'r') as f:
                    self.returning_profiles = json.load(f)
                logger.info(f"Loaded {len(self.returning_profiles)} returning user profiles from disk")
        except Exception as e:
            logger.error(f"Failed to load returning profiles: {e}")
            self.returning_profiles = []

    def save_returning_profiles(self):
        """Save returning user profiles to disk (keep last MAX_RETURNING_POOL_SIZE)."""
        try:
            with open(self.returning_profiles_path, 'w') as f:
                json.dump(self.returning_profiles[-self.max_returning_pool_size:], f)
        except Exception as e:
            logger.error(f"Failed to save returning profiles: {e}")

    # ==================== PROXY POOL (UNTOUCHED) ====================

    def get_proxies(self):
        """Scrape free proxies from various sources."""
        sources = [
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&timeout=10000&proxy_format=ipport&format=text",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies/http.txt",
            "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
        ]
        proxies = set()
        s = requests.Session(impersonate="chrome120")
        for url in sources:
            if self.stop_event.is_set():
                break
            try:
                r = s.get(url, timeout=10)
                if r.status_code == 200:
                    for line in r.text.splitlines():
                        line = line.strip()
                        if re.match(r"^\d+\.\d+\.\d+\.\d+:\d+$", line):
                            proxies.add(f"http://{line}")
            except Exception as e:
                logger.debug(f"Failed to fetch proxies from {url}: {e}")
        return list(proxies)

    def get_country_from_ip(self, ip):
        """Estimate country from IP."""
        if ip == "PREMIUM": return "US"
        try:
            r = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode", timeout=5)
            if r.status_code == 200:
                return r.json().get("countryCode", "XX")
        except: pass
        return "XX"

    def test_proxy(self, p_url):
        """Test proxy speed and anonymity."""
        if self.stop_event.is_set():
            return None
        try:
            start = time.time()
            proxies = {"http": p_url, "https": p_url}
            r = requests.get("https://httpbin.org/ip", proxies=proxies,
                             timeout=10, impersonate="chrome120")
            if r.status_code == 200:
                latency = (time.time() - start) * 1000
                ip = r.json()["origin"].split(",")[0]
                country = self.get_country_from_ip(ip)
                score = 100 if latency < 200 else 85 if latency < 500 else 70
                return {"proxy": p_url, "ip": ip, "country": country, "score": score}
        except: pass
        return None

    def build_proxy_pool(self):
        """Refresh the proxy pool with both premium and tested free proxies."""
        logger.info("Initializing Proxy Pool...")

        pool = []
        for p in PREMIUM_PROXIES:
            pool.append({"proxy": p, "ip": "PREMIUM", "country": "US", "score": 100})

        raw_list = self.get_proxies()
        if raw_list:
            logger.info(f"Scraped {len(raw_list)} raw proxies. Testing...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(raw_list) + 1, 100)) as ex:
                results = list(ex.map(self.test_proxy, raw_list))

            good_free = [p for p in results if p and p.get("score", 0) >= 70]
            good_free.sort(key=lambda x: x.get("score", 0), reverse=True)
            pool.extend(good_free[:500])

        with self.proxy_lock:
            self.working_proxies = pool

        logger.info(f"[PROXY] Pool refreshed. Total: {len(self.working_proxies)} (Premium: {len(PREMIUM_PROXIES)})")

    def proxy_refresher(self):
        while not self.stop_event.is_set():
            if self.stop_event.wait(PROXY_ROTATE_INTERVAL):
                break
            self.build_proxy_pool()

    # ==================== GA4 ANALYTICS ====================

    def _resolve_ga4_tid(self, sess, max_retries=3):
        """Fetch and cache GA4 measurement ID from target site with retry."""
        for attempt in range(max_retries):
            with self._ga4_tid_lock:
                if self._ga4_tid:
                    return self._ga4_tid
            try:
                r = sess.get(TARGET_URL, timeout=30)
                if r.status_code == 200:
                    m = re.search(r'G-([A-Z0-9]{8,12})', r.text)
                    if m:
                        tid = m.group(0)
                        with self._ga4_tid_lock:
                            self._ga4_tid = tid
                        return tid
            except Exception as e:
                logger.debug(f"GA4 TID resolve attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                self.stop_event.wait(2)
        return None

    def fire_ga4_event(self, sess, url, title, client_id, session_id, page_id,
                       event_name, hit_seq=1, engagement_time=None,
                       is_first_visit=False, is_session_start=False,
                       is_engaged=False, session_count=1,
                       referrer=None, screen_res="1920x1080",
                       campaign_source=None, campaign_medium=None,
                       campaign_term=None, campaign_name=None,
                       percent_scrolled=None, link_url=None,
                       custom_params=None):
        """Fire a single authentic GA4 collect event with proper origin headers and params."""
        try:
            tid = self._resolve_ga4_tid(sess)
            if not tid:
                return False

            parsed_url = urlparse(url)
            origin = f"{parsed_url.scheme}://{parsed_url.netloc}"

            params = {
                "v": "2",
                "tid": tid,
                "gtm": "45je4b10v878893931za200",
                "_p": page_id,
                "cid": client_id,
                "ul": "en-us",
                "sr": screen_res,
                "dl": url,
                "dt": title,
                "en": event_name,
                "sid": session_id,
                "_s": str(hit_seq),
                "_sct": str(session_count),
                "gcs": "G111",
                "gcd": "13p3p3p2p5",
                "npa": "0",
                "dma": "0",
            }

            # Session engaged flag (engaged once dwell completes or after first hit)
            if is_engaged or hit_seq > 1:
                params["_seg"] = "1"

            # Document referrer (where user came from)
            if referrer:
                params["dr"] = referrer

            # Session / visit flags (only on initial hit)
            if is_session_start:
                params["_ss"] = "1"
            if is_first_visit:
                params["_fv"] = "1"

            # Engagement time in milliseconds
            if engagement_time:
                params["_et"] = str(engagement_time)

            # Campaign source / medium / keyword attribution (guarantees non-direct in GA4)
            if campaign_source:
                params["cs"] = campaign_source
            if campaign_medium:
                params["cm"] = campaign_medium
            if campaign_term:
                params["ck"] = campaign_term
            if campaign_name:
                params["cn"] = campaign_name

            # Search Console simulation for organic traffic
            if campaign_source == "google" and campaign_medium == "organic" and campaign_term:
                params["cq"] = quote(campaign_term)  # Search query
                # Search position simulation
                if "restromandu" in campaign_term.lower():
                    params["cps"] = str(random.randint(1, 5))  # Branded: position 1-5
                else:
                    params["cps"] = str(random.randint(10, 50))  # Generic: position 10-50

            # Event-specific parameters
            if percent_scrolled:
                params["epn.percent_scrolled"] = str(percent_scrolled)
            if link_url:
                params["ep.link_url"] = link_url

            # Custom conversion parameters (form_start, generate_lead)
            if custom_params:
                for k, v in custom_params.items():
                    params[k] = str(v)

            # Authentic browser collect headers (clean fetch without HTML document headers)
            collect_headers = {
                "Accept": "*/*",
                "Referer": url,
                "Origin": origin,
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Dest": "empty",
            }

            query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
            r = sess.get(f"https://www.google-analytics.com/g/collect?{query}",
                         headers=collect_headers, timeout=10)
            return r.status_code in (200, 204)
        except Exception as e:
            logger.debug(f"GA4 event '{event_name}' failed: {e}")
            return False

    # ==================== PAGE HELPERS ====================

    def get_page_title(self, sess, url):
        """Fetch page, return (title, status_code). Returns (None, code) on error."""
        try:
            r = sess.get(url, timeout=30)
            if r.status_code != 200:
                return None, r.status_code
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.title.string.strip() if soup.title and soup.title.string else "RestroMandu"
            return title, 200
        except Exception:
            return None, 0

    def discover_internal_links(self, sess, page_url):
        """Parse page HTML, return list of same-domain internal links."""
        try:
            r = sess.get(page_url, timeout=30)
            if r.status_code != 200:
                return []
            soup = BeautifulSoup(r.text, 'html.parser')
            base = urlparse(page_url)
            links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                full = urljoin(page_url, href)
                parsed = urlparse(full)
                if (parsed.netloc == base.netloc and
                    parsed.scheme in ('http', 'https') and
                    not parsed.path.endswith(('.pdf', '.jpg', '.png', '.css', '.js', '.xml', '.gz')) and
                    parsed.path != urlparse(page_url).path and
                    '#' not in href):
                    clean = parsed.scheme + "://" + parsed.netloc + parsed.path
                    links.add(clean)
            return list(links)
        except Exception:
            return []

    # ==================== SESSION / DEVICE ====================

    def _pick_device_profile(self):
        """Weighted random device profile selection."""
        weights = [p["weight"] for p in DEVICE_PROFILES]
        return random.choices(DEVICE_PROFILES, weights=weights, k=1)[0]

    def get_session(self, proxy_data):
        """Create session with diverse browser fingerprint. Returns (session, profile)."""
        profile = self._pick_device_profile()

        # Choose impersonation based on browser
        browser = profile["browser"]
        if browser in ("Chrome", "Edge"):
            impersonate = BrowserType.chrome120
        elif browser == "Safari":
            impersonate = BrowserType.safari15_5
        elif browser == "Firefox":
            impersonate = BrowserType.firefox120
        elif browser == "SamsungBrowser":
            impersonate = BrowserType.chrome120  # Samsung Browser is Chrome-based
        else:
            impersonate = BrowserType.chrome120

        s = requests.Session(impersonate=impersonate, timeout=60)

        chrome_ver = random.randint(120, 131)
        version = f"{chrome_ver}.0.{random.randint(6000, 7000)}.{random.randint(10, 200)}"
        minor = random.randint(1, 6)

        ua = profile["ua_tpl"].format(ver=version, minor=minor)
        res = random.choice(profile["resolutions"])
        is_mobile = profile["platform"] == "mobile"

        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

        # Chrome/Edge send Sec-Ch-Ua headers
        if browser in ("Chrome", "Edge"):
            headers["Sec-Ch-Ua"] = f'"Not_A Brand";v="8", "Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}"'
            headers["Sec-Ch-Ua-Mobile"] = "?1" if is_mobile else "?0"
            headers["Sec-Ch-Ua-Platform"] = f'"{profile["os"]}"'

        s.headers.update(headers)

        if proxy_data and proxy_data.get("proxy"):
            p = proxy_data["proxy"]
            s.proxies = {"http": p, "https": p}

        profile["_res"] = res
        return s, profile

    # ==================== TRAFFIC SOURCE SELECTION ====================

    def _pick_traffic_source(self):
        """Weighted random traffic source. Returns (source_type, referer_url, landing_url, keyword, cs, cm)."""
        roll = random.random()
        cumulative = 0.0
        source_type = "google_organic"

        for src_type, weight in TRAFFIC_SOURCES.items():
            cumulative += weight
            if roll < cumulative:
                source_type = src_type
                break

        base_target = TARGET_URL.rstrip('/') + '/'

        if source_type == "google_organic":
            kw = random.choice(KEYWORDS)
            return source_type, "https://www.google.com/", base_target, kw, "google", "organic"

        elif source_type == "social_referral":
            # Weighted selection for social referrers
            weights = [s.get("weight", 1) for s in SOCIAL_REFERRERS]
            src = random.choices(SOCIAL_REFERRERS, weights=weights, k=1)[0]
            landing = f"{base_target}?utm_source={src['utm_source']}&utm_medium={src['utm_medium']}"
            return source_type, src["referer"], landing, None, src["utm_source"], src["utm_medium"]

        elif source_type == "ai_assistant":
            # Weighted selection for AI referrers
            weights = [s.get("weight", 1) for s in AI_REFERRERS]
            src = random.choices(AI_REFERRERS, weights=weights, k=1)[0]
            landing = f"{base_target}?utm_source={src['utm_source']}&utm_medium={src['utm_medium']}"
            return source_type, src["referer"], landing, None, src["utm_source"], src["utm_medium"]

        else:  # other_organic
            kw = random.choice(KEYWORDS)
            weights = [s.get("weight", 1) for s in OTHER_SEARCH_ENGINES]
            src = random.choices(OTHER_SEARCH_ENGINES, weights=weights, k=1)[0]
            return source_type, src["referer"], base_target, kw, src["engine"], "organic"

    # ==================== MAIN SIMULATION LOOP ====================

    def simulate_human(self):
        """Main bot loop — realistic multi-page sessions with proper GA4 events."""
        while not self.stop_event.is_set():
            with self.proxy_lock:
                if not self.working_proxies:
                    self.stop_event.wait(5)
                    continue
                proxy = random.choice(self.working_proxies)

            sess, device = self.get_session(proxy)

            # Returning user simulation or authentic new client ID
            is_returning = False
            session_count = 1

            with self.returning_lock:
                if self.returning_profiles and random.random() < RETURNING_USER_RATIO:
                    # Cohort-weighted selection: prefer recent profiles
                    now = time.time()
                    weights = []
                    for p in self.returning_profiles:
                        age_days = (now - p.get("last_seen", now)) / 86400
                        if age_days <= 1:
                            weights.append(RETURNING_COHORT_WEIGHTS["day_1"])
                        elif age_days <= 7:
                            weights.append(RETURNING_COHORT_WEIGHTS["day_7"])
                        else:
                            weights.append(RETURNING_COHORT_WEIGHTS["day_30"])
                    profile = random.choices(self.returning_profiles, weights=weights, k=1)[0]
                    profile["sct"] += 1
                    profile["last_seen"] = now
                    session_count = profile["sct"]
                    client_id = profile["cid"]
                    is_returning = True

            if not is_returning:
                now_epoch = int(time.time())
                past_epoch = now_epoch - random.randint(3600, 86400 * 30)
                client_id = f"{random.randint(1000000000, 2147483647)}.{past_epoch}"
                session_count = 1

            session_id = str(int(time.time()))
            screen_res = device["_res"]
            events_fired = 0
            pages_visited = []

            try:
                # 1. Pick traffic source with explicit campaign attribution (100% non-direct)
                source_type, referer_url, landing_url, keyword, cs, cm = self._pick_traffic_source()
                sess.headers["Referer"] = referer_url

                # For search engines, simulate the search engine query visit first
                if source_type in ("google_organic", "other_organic") and keyword:
                    logger.info(f"[SEARCH] {source_type}: '{keyword}'")
                    try:
                        search_base = referer_url.rstrip("/")
                        actual_search_url = f"{search_base}/search?q={quote(keyword)}&sourceid=chrome&ie=UTF-8"
                        sess.get(actual_search_url, timeout=40)
                        referer_url = actual_search_url  # Use actual search URL as referrer for GA4 dr param
                    except Exception:
                        pass
                    self.stop_event.wait(random.uniform(GOOGLE_WAIT_MIN, GOOGLE_WAIT_MAX))
                    if self.stop_event.is_set():
                        continue
                else:
                    logger.info(f"[{source_type.upper()}] Visiting via {referer_url}")

                # 2. Land on target — check for errors (skips 500s)
                title, status = self.get_page_title(sess, landing_url)
                if title is None:
                    logger.debug(f"Landing page returned status {status}, skipping")
                    self.stop_event.wait(random.uniform(3, 8))
                    continue

                pages_visited.append(landing_url)
                page_id = str(random.randint(100000000, 999999999))
                hit_seq = 1

                # 3. Fire initial page_view with session_start + (first_visit if new) + source/medium attribution
                # RETRY LOGIC: Up to 3 attempts with proxy rotation to prevent "(not set)" landing pages
                max_hit1_retries = 3
                hit_1_ok = False

                for attempt in range(max_hit1_retries):
                    hit_1_ok = self.fire_ga4_event(
                        sess=sess, url=landing_url, title=title,
                        client_id=client_id, session_id=session_id, page_id=page_id,
                        event_name="page_view", hit_seq=hit_seq,
                        session_count=session_count,
                        is_session_start=True,
                        is_first_visit=(not is_returning),
                        referrer=referer_url, screen_res=screen_res,
                        campaign_source=cs, campaign_medium=cm, campaign_term=keyword
                    )

                    if hit_1_ok:
                        break

                    logger.warning(f"[GA4] Hit 1 attempt {attempt+1}/{max_hit1_retries} failed. Rotating proxy...")

                    with self.proxy_lock:
                        if self.working_proxies:
                            proxy = random.choice(self.working_proxies)
                    sess, device = self.get_session(proxy)
                    screen_res = device["_res"]
                    source_type, referer_url, landing_url, keyword, cs, cm = self._pick_traffic_source()
                    sess.headers["Referer"] = referer_url
                    title, status = self.get_page_title(sess, landing_url)
                    if title is None:
                        continue

                # Fail-fast: If Hit 1 fails after all retries, abort to prevent Direct/Unassigned leakage
                if not hit_1_ok:
                    logger.debug(f"[GA4] Hit 1 failed after {max_hit1_retries} retries. Aborting session to prevent Direct/Unassigned leakage.")
                    self.stop_event.wait(random.uniform(2, 5))
                    continue

                events_fired += 1

                # If new user succeeded, store in returning pool
                if not is_returning:
                    with self.returning_lock:
                        if len(self.returning_profiles) >= self.max_returning_pool_size:
                            self.returning_profiles.pop(0)
                        self.returning_profiles.append({
                            "cid": client_id,
                            "sct": 1,
                            "source": source_type,
                            "last_seen": time.time()
                        })
                    self.save_returning_profiles()

                # 4. Dwell on landing page
                dwell = random.uniform(DWELL_MIN, DWELL_MAX)
                self.stop_event.wait(dwell)
                if self.stop_event.is_set():
                    break

                # 5. Engagement event (shares same page_id, incrementing hit_seq, marked as engaged)
                hit_seq += 1
                engagement_ms = int(dwell * 1000) + random.randint(0, 5000)
                if self.fire_ga4_event(
                    sess=sess, url=landing_url, title=title,
                    client_id=client_id, session_id=session_id, page_id=page_id,
                    event_name="user_engagement", hit_seq=hit_seq,
                    session_count=session_count, is_engaged=True,
                    engagement_time=engagement_ms, screen_res=screen_res
                ):
                    events_fired += 1

                # Multi-point scroll on landing page (25/50/75/90)
                scroll_points = [25, 50, 75, 90]
                for sp in scroll_points:
                    if random.random() < 0.4:  # 40% chance per scroll point
                        hit_seq += 1
                        if self.fire_ga4_event(
                            sess=sess, url=landing_url, title=title,
                            client_id=client_id, session_id=session_id, page_id=page_id,
                            event_name="scroll", hit_seq=hit_seq,
                            session_count=session_count, is_engaged=True,
                            screen_res=screen_res, percent_scrolled=sp
                        ):
                            events_fired += 1
                        self.stop_event.wait(random.uniform(1, 3))
                        if self.stop_event.is_set():
                            break

                # Key Event / Conversion Simulation if landing page is a lead-generating page
                if any(p in landing_url for p in LEAD_PAGES) and random.random() < KEY_EVENT_PROBABILITY:
                    hit_seq += 1
                    if self.fire_ga4_event(
                        sess=sess, url=landing_url, title=title,
                        client_id=client_id, session_id=session_id, page_id=page_id,
                        event_name="form_start", hit_seq=hit_seq,
                        session_count=session_count, is_engaged=True,
                        screen_res=screen_res,
                        custom_params={"ep.form_id": "contact_lead_form", "ep.form_name": "Inquiry Form"}
                    ):
                        events_fired += 1

                    self.stop_event.wait(random.uniform(2, 5))
                    hit_seq += 1
                    if self.fire_ga4_event(
                        sess=sess, url=landing_url, title=title,
                        client_id=client_id, session_id=session_id, page_id=page_id,
                        event_name="generate_lead", hit_seq=hit_seq,
                        session_count=session_count, is_engaged=True,
                        screen_res=screen_res,
                        custom_params={"ep.currency": "NPR", "epn.value": "5000", "ep.lead_type": "restaurant_erp_inquiry"}
                    ):
                        events_fired += 1
                        logger.info(f"[CONVERSION] Successfully fired lead conversion event on {landing_url}")

                # 6. Multi-page navigation loop
                num_extra_pages = random.randint(PAGES_PER_SESSION_MIN - 1, PAGES_PER_SESSION_MAX - 1)
                current_url = landing_url
                session_dwell = dwell

                for _ in range(num_extra_pages):
                    if self.stop_event.is_set():
                        break

                    links = self.discover_internal_links(sess, current_url)
                    if not links:
                        base = TARGET_URL.rstrip('/')
                        links = [f"{base}{p}" for p in INTERNAL_PATHS]

                    unvisited = [l for l in links if l not in pages_visited]
                    if not unvisited:
                        unvisited = links

                    next_url = random.choice(unvisited)

                    # Fire click event on current page before following link
                    hit_seq += 1
                    if self.fire_ga4_event(
                        sess=sess, url=current_url, title=title,
                        client_id=client_id, session_id=session_id, page_id=page_id,
                        event_name="click", hit_seq=hit_seq,
                        session_count=session_count, is_engaged=True,
                        screen_res=screen_res, link_url=next_url
                    ):
                        events_fired += 1

                    self.stop_event.wait(random.uniform(0.5, 2.0))

                    # Update HTTP Referer header for the internal page GET
                    sess.headers["Referer"] = current_url

                    # Navigate to next page — skip if error
                    next_title, next_status = self.get_page_title(sess, next_url)
                    if next_title is None:
                        logger.debug(f"Internal page {next_url} returned {next_status}, skipping")
                        continue

                    pages_visited.append(next_url)
                    previous_url = current_url
                    current_url = next_url
                    title = next_title
                    page_id = str(random.randint(100000000, 999999999))  # New page_id for new page

                    # Fire page_view on new page (internal referrer, marked engaged)
                    hit_seq += 1
                    if self.fire_ga4_event(
                        sess=sess, url=next_url, title=next_title,
                        client_id=client_id, session_id=session_id, page_id=page_id,
                        event_name="page_view", hit_seq=hit_seq,
                        session_count=session_count, is_engaged=True,
                        referrer=previous_url, screen_res=screen_res
                    ):
                        events_fired += 1

                    # Dwell on internal page
                    page_dwell = random.uniform(INTERNAL_DWELL_MIN, INTERNAL_DWELL_MAX)
                    self.stop_event.wait(page_dwell)
                    session_dwell += page_dwell
                    if self.stop_event.is_set():
                        break

                    # Engagement event on internal page
                    hit_seq += 1
                    page_engagement_ms = int(page_dwell * 1000) + random.randint(0, 3000)
                    if self.fire_ga4_event(
                        sess=sess, url=next_url, title=next_title,
                        client_id=client_id, session_id=session_id, page_id=page_id,
                        event_name="user_engagement", hit_seq=hit_seq,
                        session_count=session_count, is_engaged=True,
                        engagement_time=page_engagement_ms, screen_res=screen_res
                    ):
                        events_fired += 1

                    # Multi-point scroll on internal page (25/50/75/90)
                    if random.random() < 0.3:
                        scroll_points = [25, 50, 75, 90]
                        for sp in scroll_points:
                            if random.random() < 0.4:
                                hit_seq += 1
                                if self.fire_ga4_event(
                                    sess=sess, url=next_url, title=next_title,
                                    client_id=client_id, session_id=session_id, page_id=page_id,
                                    event_name="scroll", hit_seq=hit_seq,
                                    session_count=session_count, is_engaged=True,
                                    screen_res=screen_res, percent_scrolled=sp
                                ):
                                    events_fired += 1
                                self.stop_event.wait(random.uniform(1, 3))
                                if self.stop_event.is_set():
                                    break

                    # Key Event / Conversion Simulation on internal lead pages
                    if any(p in next_url for p in LEAD_PAGES) and random.random() < KEY_EVENT_PROBABILITY:
                        hit_seq += 1
                        if self.fire_ga4_event(
                            sess=sess, url=next_url, title=title,
                            client_id=client_id, session_id=session_id, page_id=page_id,
                            event_name="form_start", hit_seq=hit_seq,
                            session_count=session_count, is_engaged=True,
                            screen_res=screen_res,
                            custom_params={"ep.form_id": "contact_lead_form", "ep.form_name": "Inquiry Form"}
                        ):
                            events_fired += 1

                        self.stop_event.wait(random.uniform(2, 5))
                        hit_seq += 1
                        if self.fire_ga4_event(
                            sess=sess, url=next_url, title=title,
                            client_id=client_id, session_id=session_id, page_id=page_id,
                            event_name="generate_lead", hit_seq=hit_seq,
                            session_count=session_count, is_engaged=True,
                            screen_res=screen_res,
                            custom_params={"ep.currency": "NPR", "epn.value": "5000", "ep.lead_type": "restaurant_erp_inquiry"}
                        ):
                            events_fired += 1
                            logger.info(f"[CONVERSION] Successfully fired lead conversion event on {next_url}")

                # Logging now includes country for geo analysis
                self.log_visit(
                    source_type.upper(),
                    ",".join(urlparse(p).path or "/" for p in pages_visited),
                    proxy.get("ip", "0.0.0.0"),
                    proxy.get("country", "XX"),
                    session_dwell,
                    events_fired
                )

                with self.stats_lock:
                    if source_type in ("google_organic", "other_organic"):
                        self.search_clicks += 1
                    self.analytics_fired_count += events_fired

                # Pause between sessions
                self.stop_event.wait(random.uniform(5, 15))

            except Exception as e:
                logger.debug(f"Worker iteration failed: {e}")
                self.stop_event.wait(5)

    # ==================== LOGGING & STATS ====================

    def log_visit(self, type_, page, ip, country, dwell, fired):
        with self.stats_lock:
            self.total_visits += 1
            self.successful_visits += 1
            if country != "XX":
                self.unique_countries.add(country)
            self.unique_pages.add(page)

            try:
                with open(self.log_path, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), type_, page, ip, country,
                        f"{dwell:.1f}s", fired
                    ])
            except Exception as e:
                logger.error(f"Failed to log visit: {e}")

    def get_stats(self):
        with self.stats_lock:
            uptime = 0
            if self.start_time:
                uptime = (datetime.now() - self.start_time).total_seconds()

            countries = list(self.unique_countries)
            top_countries = countries[:5]
            country_str = ", ".join(top_countries) if top_countries else "N/A"

            return {
                "visits": self.successful_visits,
                "unique_countries": len(countries),
                "countries_str": country_str,
                "search_clicks": self.search_clicks,
                "analytics_fired": int(self.analytics_fired_count),
                "uptime": uptime,
                "is_running": self.is_running,
                "active_proxies": len(self.working_proxies),
                "threads": THREADS,
                "target_url": TARGET_URL
            }

    # ==================== START / STOP ====================

    def start(self):
        if self.is_running: return False
        logger.info("Starting SEO Booster Engine...")
        self.is_running = True
        self.stop_event.clear()
        with self.stats_lock:
            if not self.start_time:
                self.start_time = datetime.now()
        t_init = threading.Thread(target=self._start_internal, daemon=True)
        t_init.start()
        return True

    def _start_internal(self):
        self.build_proxy_pool()
        if self.stop_event.is_set(): return
        t_rot = threading.Thread(target=self.proxy_refresher, daemon=True)
        t_rot.start()
        self.threads.append(t_rot)
        for _ in range(THREADS):
            t = threading.Thread(target=self.simulate_human, daemon=True)
            t.start()
            self.threads.append(t)

    def stop(self):
        if not self.is_running: return False
        logger.info("Stopping Engine... Finishing active sessions.")
        self.stop_event.set()
        self.is_running = False
        self.threads = []
        return True


bot = SEOBoosterBot()