# CodeAlpha Data Analytics Internship — Task 1: Web Scraping

## Project Overview
This project demonstrates web scraping using Python (BeautifulSoup & Scrapy) to extract
relevant datasets from public web pages, handle HTML structure, and create custom datasets
tailored to specific analysis needs.

## Folder Structure
```
CodeAlpha_ProjectName/
│
├── web_scraping/
│   ├── scrapers/
│   │   ├── bs4_quotes_scraper.py       # BeautifulSoup scraper — quotes dataset
│   │   ├── bs4_books_scraper.py        # BeautifulSoup scraper — books dataset
│   │   └── scrapy_spider.py            # Scrapy spider — news/articles dataset
│   │
│   ├── datasets/
│   │   ├── quotes_dataset.csv          # Scraped quotes with author & tags
│   │   ├── books_dataset.csv           # Scraped books with price & rating
│   │   └── combined_dataset.csv        # Merged/cleaned combined dataset
│   │
│   ├── notebooks/
│   │   └── web_scraping_analysis.ipynb # Jupyter notebook with full walkthrough
│   │
│   ├── utils/
│   │   ├── helpers.py                  # Reusable utilities (headers, retry, cleaning)
│   │   └── html_parser.py              # HTML structure navigator helper
│   │
│   └── output/
│       └── scraping_report.txt         # Summary report of scraped data
│
├── run_all.py                          # Master script — runs all scrapers end-to-end
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run all scrapers at once
```bash
python run_all.py
```

### 3. Run individual scrapers
```bash
# BeautifulSoup — Quotes
python web_scraping/scrapers/bs4_quotes_scraper.py

# BeautifulSoup — Books
python web_scraping/scrapers/bs4_books_scraper.py
```

## Datasets Collected

| Dataset          | Source                          | Records | Fields                          |
|------------------|---------------------------------|---------|----------------------------------|
| quotes_dataset   | quotes.toscrape.com             | 100     | text, author, tags               |
| books_dataset    | books.toscrape.com              | 1000    | title, price, rating, category   |
| combined_dataset | Both sources (cleaned & merged) | varies  | cross-source analysis fields     |

## Tools & Libraries Used
- **BeautifulSoup4** — HTML parsing and navigation
- **Scrapy** — Industrial-strength spider framework
- **Requests** — HTTP requests with headers & retries
- **Pandas** — Data cleaning and CSV export
- **lxml** — Fast HTML/XML parser backend
- **fake-useragent** — Rotating user agents for polite scraping

## Key Concepts Demonstrated
1. Parsing HTML structure (`find`, `find_all`, CSS selectors)
2. Navigating pagination across multiple pages
3. Handling missing/malformed data gracefully
4. Rotating user agents and rate limiting (polite scraping)
5. Exporting clean datasets to CSV and Excel
6. Using Scrapy spiders for scalable scraping

## Notes
- All scraping targets are **public practice sites** designed for scraping (toscrape.com)
- Rate limiting and delays are included to avoid overloading servers
- No authentication or login bypassing is used
