"""
scrapers/scrapy_spider.py
Scrapy-based spider that scrapes quotes.toscrape.com
and exports data to JSON using Scrapy's built-in feed exporter.

Run directly via:
    python web_scraping/scrapers/scrapy_spider.py

Or via Scrapy CLI:
    scrapy runspider web_scraping/scrapers/scrapy_spider.py -o output/scrapy_quotes.json
"""

import sys
import os
import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "../datasets/scrapy_quotes.json")


class QuotesSpider(scrapy.Spider):
    """
    Scrapy spider for quotes.toscrape.com.
    Demonstrates:
    - CSS and XPath selectors
    - Automatic pagination follow
    - Structured item extraction
    - Scrapy's request/response pipeline
    """

    name = "quotes_spider"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,              # polite 1-second delay between requests
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "CONCURRENT_REQUESTS": 1,         # sequential to be gentle
        "LOG_LEVEL": "WARNING",           # reduce noise
        "FEEDS": {
            OUTPUT_JSON: {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        },
    }

    def parse(self, response):
        """Parse all quotes on the current page."""
        # ── CSS Selectors ───────────────────────────────────
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(default="").strip(),
                "author": quote.css("small.author::text").get(default="").strip(),
                # XPath for demonstration — same result as CSS
                "author_about": quote.xpath(".//a/@href").get(default=""),
                "tags": quote.css("a.tag::text").getall(),
                "source_url": response.url,
            }

        # ── Pagination ──────────────────────────────────────
        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


def run_scrapy_spider():
    """Launch the Scrapy spider programmatically."""
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

    # Remove old output to avoid appending
    if os.path.exists(OUTPUT_JSON):
        os.remove(OUTPUT_JSON)

    settings = get_project_settings()
    settings.setdict(QuotesSpider.custom_settings)

    process = CrawlerProcess(settings)
    process.crawl(QuotesSpider)
    process.start()

    # ── Verify output ───────────────────────────────────────
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"\n[Scrapy] ✓ Scraped {len(data)} quotes → {OUTPUT_JSON}")
        if data:
            sample = data[0]
            print(f"  Sample: \"{sample['text'][:60]}...\" — {sample['author']}")
    else:
        print("[Scrapy] ✗ No output file found.")


if __name__ == "__main__":
    run_scrapy_spider()
