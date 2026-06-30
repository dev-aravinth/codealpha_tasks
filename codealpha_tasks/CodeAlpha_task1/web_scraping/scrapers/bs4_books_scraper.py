"""
scrapers/bs4_books_scraper.py
Scrapes all books from https://books.toscrape.com across all 50 catalogue pages.

Dataset fields: title | price_gbp | rating_stars | availability | category | url
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from web_scraping.utils.helpers import fetch_page, clean_price, word_to_stars, clean_text, logger

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../datasets/books_dataset.csv")


def scrape_books_page(soup) -> list[dict]:
    """Extract all book records from one catalogue page."""
    books = []
    for article in soup.select("article.product_pod"):
        # ── Title ──────────────────────────────────────────
        title_tag = article.select_one("h3 > a")
        title = title_tag["title"] if title_tag else "N/A"

        # ── Price ──────────────────────────────────────────
        price_tag = article.select_one("p.price_color")
        price = clean_price(price_tag.get_text()) if price_tag else 0.0

        # ── Star Rating (word → integer) ───────────────────
        # BeautifulSoup: <p class="star-rating Three">
        rating_tag = article.select_one("p.star-rating")
        rating_word = rating_tag["class"][1] if rating_tag else "Zero"
        rating = word_to_stars(rating_word)

        # ── Availability ───────────────────────────────────
        avail_tag = article.select_one("p.availability")
        availability = avail_tag.get_text(strip=True) if avail_tag else "Unknown"

        # ── Book URL ───────────────────────────────────────
        book_href = title_tag["href"].replace("../", "") if title_tag else ""
        book_url = BASE_URL + book_href

        books.append({
            "title": clean_text(title),
            "price_gbp": price,
            "rating_stars": rating,
            "availability": availability,
            "book_url": book_url,
        })
    return books


def get_next_page(soup, current_url: str) -> str | None:
    """Navigate pagination — return next page URL."""
    next_btn = soup.select_one("li.next > a")
    if not next_btn:
        return None
    # href is relative, e.g. "page-2.html"
    return BASE_URL + next_btn["href"]


def scrape_all_books() -> pd.DataFrame:
    all_books = []
    url = START_URL
    page_num = 1

    while url:
        logger.info(f"Scraping books page {page_num}: {url}")
        soup = fetch_page(url)
        if not soup:
            logger.error(f"Could not fetch page {page_num}, stopping.")
            break

        page_books = scrape_books_page(soup)
        all_books.extend(page_books)
        logger.info(f"  → {len(page_books)} books (total: {len(all_books)})")

        url = get_next_page(soup, url)
        page_num += 1

    df = pd.DataFrame(all_books)

    # ── Derive price brackets for analysis ────────────────
    if not df.empty:
        df["price_bracket"] = pd.cut(
            df["price_gbp"],
            bins=[0, 10, 20, 35, 60],
            labels=["Budget (£0-10)", "Mid (£10-20)", "Premium (£20-35)", "Luxury (£35+)"]
        )

    return df


def main():
    logger.info("=" * 50)
    logger.info("TASK 1 — BeautifulSoup Books Scraper")
    logger.info("=" * 50)

    df = scrape_all_books()

    if df.empty:
        logger.warning("No data scraped!")
        return

    # ── Stats ─────────────────────────────────────────────
    logger.info(f"\nTotal books     : {len(df)}")
    logger.info(f"Avg price       : £{df['price_gbp'].mean():.2f}")
    logger.info(f"Avg rating      : {df['rating_stars'].mean():.2f} stars")
    logger.info(f"In stock        : {(df['availability'] == 'In stock').sum()}")
    logger.info(f"\nRating distribution:\n{df['rating_stars'].value_counts().sort_index().to_string()}")
    logger.info(f"\nPrice brackets:\n{df['price_bracket'].value_counts().to_string()}")

    # ── Save ──────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    logger.info(f"\nDataset saved → {OUTPUT_PATH}")

    print("\n── Sample Records ──")
    print(df.head(5).to_string(index=False))

    return df


if __name__ == "__main__":
    main()
