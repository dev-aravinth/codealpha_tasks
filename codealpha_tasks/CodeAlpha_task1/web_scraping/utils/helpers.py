"""
utils/helpers.py
Reusable utilities for web scraping: headers, retry logic, rate limiting, cleaning.
"""

import time
import random
import requests
import logging
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# HTTP Headers
# ──────────────────────────────────────────────

HEADERS_LIST = [
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.4 Safari/605.1.15"
        ),
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) "
            "Gecko/20100101 Firefox/125.0"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
]


def get_random_headers() -> dict:
    """Return a random browser-like header dict."""
    return random.choice(HEADERS_LIST)


# ──────────────────────────────────────────────
# HTTP Fetch with Retry
# ──────────────────────────────────────────────

def fetch_page(url: str, retries: int = 3, delay: float = 1.5) -> BeautifulSoup | None:
    """
    Fetch a URL with retries and return a BeautifulSoup object.

    Args:
        url:     Target URL.
        retries: Number of attempts before giving up.
        delay:   Seconds to wait between retries.

    Returns:
        BeautifulSoup object or None on failure.
    """
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Fetching (attempt {attempt}): {url}")
            response = requests.get(url, headers=get_random_headers(), timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"   # fix Â£ encoding issue on Windows
            polite_delay()
            return BeautifulSoup(response.text, "lxml")
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error {e} on attempt {attempt}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {attempt}")
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt}")
        if attempt < retries:
            time.sleep(delay * attempt)   # exponential-ish back-off
    logger.error(f"Failed to fetch: {url}")
    return None


# ──────────────────────────────────────────────
# Polite delay between requests
# ──────────────────────────────────────────────

def polite_delay(min_sec: float = 0.5, max_sec: float = 1.5) -> None:
    """Sleep a random amount to avoid hammering the server."""
    time.sleep(random.uniform(min_sec, max_sec))


# ──────────────────────────────────────────────
# Data Cleaning Utilities
# ──────────────────────────────────────────────

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}


def clean_price(raw: str) -> float:
    """Strip currency symbols and convert price to float."""
    return float(raw.replace("£", "").replace("$", "").replace(",", "").strip())


def word_to_stars(word: str) -> int:
    """Convert word rating (e.g. 'Three') to integer stars."""
    return RATING_MAP.get(word.strip().title(), 0)


def clean_text(raw: str) -> str:
    """Strip whitespace and normalise quotes."""
    return raw.strip().replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'")


def truncate(text: str, max_len: int = 200) -> str:
    """Truncate long strings."""
    return text if len(text) <= max_len else text[:max_len].rstrip() + "…"
