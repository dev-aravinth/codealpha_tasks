"""
scrapers/bs4_quotes_scraper.py
Scrapes quotes, authors, and tags from https://quotes.toscrape.com
across all paginated pages using BeautifulSoup4.

Dataset fields: text | author | author_url | tags | tag_count
"""

import sys
import os
import pandas as pd

# Allow imports from parent package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from web_scraping.utils.helpers import fetch_page, clean_text, logger

BASE_URL = "https://quotes.toscrape.com"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../datasets/quotes_dataset.csv")


def scrape_quotes_page(soup) -> list[dict]:
    """Parse all quotes from a single page soup."""
    quotes = []
    for quote_div in soup.select("div.quote"):
        # ── Text ──────────────────────────────────────────
        text_tag = quote_div.select_one("span.text")
        text = clean_text(text_tag.get_text()) if text_tag else ""

        # ── Author ────────────────────────────────────────
        author_tag = quote_div.select_one("small.author")
        author = author_tag.get_text(strip=True) if author_tag else "Unknown"

        # ── Author URL ────────────────────────────────────
        author_link = quote_div.select_one("a[href^='/author']")
        author_url = (BASE_URL + author_link["href"]) if author_link else ""

        # ── Tags ──────────────────────────────────────────
        tag_elements = quote_div.select("a.tag")
        tags = [t.get_text(strip=True) for t in tag_elements]

        quotes.append({
            "text": text,
            "author": author,
            "author_url": author_url,
            "tags": ", ".join(tags),
            "tag_count": len(tags),
        })
    return quotes


def get_next_page(soup) -> str | None:
    """Return the URL of the next page, or None if we're at the end."""
    next_btn = soup.select_one("li.next > a")
    return (BASE_URL + next_btn["href"]) if next_btn else None


def scrape_all_quotes() -> pd.DataFrame:
    """Crawl all pages and collect every quote."""
    all_quotes = []
    url = BASE_URL
    page_num = 1

    while url:
        logger.info(f"Scraping quotes page {page_num}: {url}")
        soup = fetch_page(url)
        if not soup:
            logger.error(f"Could not fetch page {page_num}, stopping.")
            break

        page_quotes = scrape_quotes_page(soup)
        all_quotes.extend(page_quotes)
        logger.info(f"  → {len(page_quotes)} quotes found (total so far: {len(all_quotes)})")

        url = get_next_page(soup)
        page_num += 1

    return pd.DataFrame(all_quotes)


def main():
    logger.info("=" * 50)
    logger.info("TASK 1 — BeautifulSoup Quotes Scraper")
    logger.info("=" * 50)

    df = scrape_all_quotes()

    if df.empty:
        logger.warning("No data scraped!")
        return

    # ── Basic stats ───────────────────────────────────────
    logger.info(f"\nTotal quotes  : {len(df)}")
    logger.info(f"Unique authors: {df['author'].nunique()}")
    logger.info(f"Total tags    : {df['tag_count'].sum()}")
    logger.info(f"Top authors   :\n{df['author'].value_counts().head(5).to_string()}")

    # ── Save ──────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    logger.info(f"\nDataset saved → {OUTPUT_PATH}")

    # ── Preview ───────────────────────────────────────────
    print("\n── Sample Records ──")
    print(df.head(5).to_string(index=False))

    return df


if __name__ == "__main__":
    main()
