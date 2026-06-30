"""
utils/html_parser.py
Demonstrates HTML structure navigation techniques using BeautifulSoup.
"""

from bs4 import BeautifulSoup, Tag
from typing import Optional


class HTMLNavigator:
    """
    Helper class to demonstrate navigating HTML structure:
    - Parent / child / sibling traversal
    - CSS selector queries
    - Attribute extraction
    - Nested element access
    """

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "lxml")

    # ── Tag Selectors ────────────────────────────────────────

    def find_by_id(self, element_id: str) -> Optional[Tag]:
        return self.soup.find(id=element_id)

    def find_by_class(self, tag: str, class_name: str) -> list[Tag]:
        return self.soup.find_all(tag, class_=class_name)

    def find_by_css(self, selector: str) -> list[Tag]:
        """Use CSS selectors — most powerful option."""
        return self.soup.select(selector)

    def find_by_attribute(self, tag: str, attr: str, value: str) -> list[Tag]:
        return self.soup.find_all(tag, attrs={attr: value})

    # ── Tree Traversal ───────────────────────────────────────

    def get_children(self, tag: Tag) -> list[Tag]:
        return [c for c in tag.children if isinstance(c, Tag)]

    def get_parent(self, tag: Tag) -> Optional[Tag]:
        return tag.parent

    def get_next_sibling(self, tag: Tag) -> Optional[Tag]:
        sibling = tag.next_sibling
        while sibling and not isinstance(sibling, Tag):
            sibling = sibling.next_sibling
        return sibling

    def get_previous_sibling(self, tag: Tag) -> Optional[Tag]:
        sibling = tag.previous_sibling
        while sibling and not isinstance(sibling, Tag):
            sibling = sibling.previous_sibling
        return sibling

    # ── Content Extractors ───────────────────────────────────

    def get_text(self, tag: Tag, separator: str = " ") -> str:
        return tag.get_text(separator=separator, strip=True)

    def get_attribute(self, tag: Tag, attr: str) -> Optional[str]:
        return tag.get(attr)

    def get_all_links(self) -> list[dict]:
        """Extract all hyperlinks from the page."""
        links = []
        for a in self.soup.find_all("a", href=True):
            links.append({
                "text": a.get_text(strip=True),
                "href": a["href"]
            })
        return links

    def get_all_images(self) -> list[dict]:
        """Extract all image sources and alt texts."""
        return [
            {"src": img.get("src", ""), "alt": img.get("alt", "")}
            for img in self.soup.find_all("img")
        ]

    def get_table_data(self) -> list[list[str]]:
        """Extract all tables as a list of rows."""
        tables = []
        for table in self.soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            tables.append(rows)
        return tables

    # ── Meta Information ─────────────────────────────────────

    def get_meta_tags(self) -> dict:
        meta = {}
        for tag in self.soup.find_all("meta"):
            name = tag.get("name") or tag.get("property", "")
            content = tag.get("content", "")
            if name:
                meta[name] = content
        return meta

    def get_page_title(self) -> str:
        title = self.soup.find("title")
        return title.get_text(strip=True) if title else ""
