"""
run_all.py
Master script — runs all Task 1 scrapers sequentially and produces the combined dataset.
"""

import os
import sys
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Ensure project root is in path ────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

DATASETS_DIR = os.path.join(ROOT, "web_scraping", "datasets")
OUTPUT_DIR   = os.path.join(ROOT, "web_scraping", "output")
COMBINED_CSV = os.path.join(DATASETS_DIR, "combined_dataset.csv")
REPORT_PATH  = os.path.join(OUTPUT_DIR, "scraping_report.txt")


def run_quotes_scraper():
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1 — Running Quotes Scraper (BeautifulSoup)")
    logger.info("=" * 60)
    try:
        from web_scraping.scrapers.bs4_quotes_scraper import main as quotes_main
        df = quotes_main()
        if df is not None and not df.empty:
            logger.info(f"✓ Quotes scraper complete: {len(df)} records")
            return df
        else:
            logger.warning("✗ Quotes scraper returned no data")
            return None
    except Exception as e:
        logger.error(f"✗ Quotes scraper failed: {e}")
        return None


def run_books_scraper():
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2 — Running Books Scraper (BeautifulSoup)")
    logger.info("=" * 60)
    try:
        from web_scraping.scrapers.bs4_books_scraper import main as books_main
        df = books_main()
        if df is not None and not df.empty:
            logger.info(f"✓ Books scraper complete: {len(df)} records")
            return df
        else:
            logger.warning("✗ Books scraper returned no data")
            return None
    except Exception as e:
        logger.error(f"✗ Books scraper failed: {e}")
        return None


def build_combined_dataset(quotes_df, books_df):
    """Build a unified summary dataset with key metrics from each source."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3 — Building Combined Dataset")
    logger.info("=" * 60)

    os.makedirs(DATASETS_DIR, exist_ok=True)

    records = []

    if quotes_df is not None and not quotes_df.empty:
        for _, row in quotes_df.iterrows():
            text = str(row["text"])
            records.append({
                "source": "quotes.toscrape.com",
                "item_type": "quote",
                "title_or_text": text[:120] + ("..." if len(text) > 120 else ""),
                "author": row["author"],
                "extra_1_label": "tags",
                "extra_1_value": row["tags"],
                "extra_2_label": "tag_count",
                "extra_2_value": str(row["tag_count"]),
                "url": row.get("author_url", ""),
            })

    if books_df is not None and not books_df.empty:
        for _, row in books_df.iterrows():
            records.append({
                "source": "books.toscrape.com",
                "item_type": "book",
                "title_or_text": row["title"],
                "author": "N/A",
                "extra_1_label": "price_gbp",
                "extra_1_value": str(row["price_gbp"]),
                "extra_2_label": "rating_stars",
                "extra_2_value": str(row["rating_stars"]),
                "url": row.get("book_url", ""),
            })

    if not records:
        logger.warning("No records to combine — check if scrapers ran successfully.")
        logger.warning("TIP: Run 'pip install requests beautifulsoup4 lxml pandas' first.")
        combined = pd.DataFrame(columns=[
            "source","item_type","title_or_text","author",
            "extra_1_label","extra_1_value","extra_2_label","extra_2_value","url"
        ])
    else:
        combined = pd.DataFrame(records)

    combined.to_csv(COMBINED_CSV, index=False, encoding="utf-8")
    logger.info(f"✓ Combined dataset saved -> {COMBINED_CSV} ({len(combined)} total records)")
    return combined


def write_report(quotes_df, books_df, combined_df):
    """Generate a plain-text summary report."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    lines = [
        "=" * 60,
        "  CODEALPHA DATA ANALYTICS -- TASK 1: WEB SCRAPING REPORT",
        "=" * 60,
        "",
    ]

    if quotes_df is not None and not quotes_df.empty:
        lines += [
            "-- Quotes Dataset (quotes.toscrape.com) --",
            f"  Total quotes   : {len(quotes_df)}",
            f"  Unique authors : {quotes_df['author'].nunique()}",
            f"  Total tags     : {quotes_df['tag_count'].sum()}",
            f"  Avg tags/quote : {quotes_df['tag_count'].mean():.2f}",
            "",
            "  Top 5 Authors:",
        ]
        for author, count in quotes_df["author"].value_counts().head(5).items():
            lines.append(f"    {author:<30} {count} quotes")
        lines.append("")
    else:
        lines += ["-- Quotes Dataset --", "  (No data — scraper could not reach the site)", ""]

    if books_df is not None and not books_df.empty:
        lines += [
            "-- Books Dataset (books.toscrape.com) --",
            f"  Total books    : {len(books_df)}",
            f"  Avg price      : GBP {books_df['price_gbp'].mean():.2f}",
            f"  Cheapest book  : GBP {books_df['price_gbp'].min():.2f}",
            f"  Most expensive : GBP {books_df['price_gbp'].max():.2f}",
            f"  Avg rating     : {books_df['rating_stars'].mean():.2f} / 5",
            f"  5-star books   : {(books_df['rating_stars'] == 5).sum()}",
            "",
            "  Rating Distribution:",
        ]
        for stars, count in books_df["rating_stars"].value_counts().sort_index().items():
            bar = "*" * int(stars) + "-" * (5 - int(stars))
            lines.append(f"    [{bar}]  {count:>4} books")
        lines.append("")
    else:
        lines += ["-- Books Dataset --", "  (No data — scraper could not reach the site)", ""]

    total = len(combined_df) if combined_df is not None else 0
    if total > 0:
        lines += [
            "-- Combined Dataset --",
            f"  Total records  : {total}",
            f"  Sources        : {combined_df['source'].nunique()}",
            f"  Item types     : {', '.join(combined_df['item_type'].unique())}",
            "",
        ]
    else:
        lines += ["-- Combined Dataset --", "  (Empty — see above)", ""]

    lines += [
        "-- Tools Used --",
        "  * BeautifulSoup4 + Requests  (Quotes scraper)",
        "  * BeautifulSoup4 + Requests  (Books scraper)",
        "  * Scrapy                     (Scrapy spider -- quotes)",
        "  * Pandas                     (Data cleaning & export)",
        "",
        "-- Datasets Saved --",
        f"  web_scraping/datasets/quotes_dataset.csv",
        f"  web_scraping/datasets/books_dataset.csv",
        f"  web_scraping/datasets/combined_dataset.csv",
        "",
        "Task 1: Web Scraping -- COMPLETE",
        "=" * 60,
    ]

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"✓ Report saved -> {REPORT_PATH}")
    print("\n" + "\n".join(lines))


def main():
    print("\n CodeAlpha Task 1 -- Web Scraping (run_all.py)\n")

    quotes_df = run_quotes_scraper()
    books_df  = run_books_scraper()
    combined  = build_combined_dataset(quotes_df, books_df)
    write_report(quotes_df, books_df, combined)

    print("\n All scrapers complete. Check web_scraping/datasets/ for output files.")


if __name__ == "__main__":
    main()
