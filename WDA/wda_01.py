"""
WDA 1 — E-commerce (Amazon) data: scrape → process pipeline → SQLite store.

Assignment coverage
-------------------
a. Extract product data from Amazon (or educational fallback HTML), using two stages:
   - Pipeline 1 (ScrapePipeline): fetch a *small* number of pages and normalize fields.
   - Pipeline 2 (DatabasePipeline): insert normalized rows into SQLite.

b. Parsed fields include color, dimensions, material, feature bullets, overall ratings
   text, star histogram (if present), and customer ratings broken down by feature
   (e.g. “Comfort”, “Value”) when Amazon exposes lighthouse / snapshot rows.

Amazon / ethics note
--------------------
Amazon’s terms and automation defenses limit scraping. This script is intentionally
restricted to a tiny request budget (default: 1 URL). For real coursework, your
instructor may expect either this cap, a provided HTML snapshot, or the built-in
demo HTML (no network). Larger crawls would require proper permission, official
APIs, or proxies — not demonstrated here.

Dependencies: pip install requests beautifulsoup4
(Database: stdlib sqlite3 — no extra package.)

Environment (optional)
----------------------
  SQLITE_PATH            — path to .sqlite/.db file (default: WDA/wda_01_amazon.sqlite)
  AMAZON_PRODUCT_URL     — single product page (one request)
  AMAZON_PRODUCT_URLS    — comma-separated URLs; still capped by MAX_SCRAPE_REQUESTS
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

# Hard cap on outbound HTTP requests (assignment: small set only).
MAX_SCRAPE_REQUESTS = int(os.environ.get("MAX_SCRAPE_REQUESTS", "1"))


# --- Demo HTML when URL omitted or request blocked (zero reliance on Amazon). ---
_FALLBACK_HTML = """
<html><head><title>Demo — Amazon-style product snippet</title></head><body>
<span id="productTitle">Demo Insulated Water Bottle 750 ml</span>
<div id="feature-bullets"><ul class="a-unordered-list a-vertical a-spacing-mini">
<li><span class="a-list-item">Color: Ocean Blue</span></li>
<li><span class="a-list-item">Material: 18/8 stainless steel, BPA-free plastic lid</span></li>
<li><span class="a-list-item">Product Dimensions: 9 x 9 x 26 cm; 350 g</span></li>
</ul></div>
<table id="productDetails_detailBullets_sections1" class="a-keyvalue">
<tr><th>Customer Reviews</th><td>4.2 out of 5 stars — 1,204 global ratings</td></tr>
</table>
<div id="histogramTable">
<table><tr aria-label="5 stars"><td>5 star</td><td>62%</td></tr>
<tr aria-label="4 stars"><td>4 star</td><td>18%</td></tr></table>
</div>
<div id="cr-snapshot-lighthouse-attributes">
<div><span>Comfort</span><span>4.1 out of 5</span></div>
<div><span>Value for money</span><span>4.4 out of 5</span></div>
</div>
<span class="a-price-whole">24</span><span class="a-price-fraction">99</span>
</body></html>
"""


@dataclass
class ProductRecord:
    title: str = ""
    price: str = ""
    color: str = ""
    dimensions: str = ""
    material: str = ""
    ratings_summary: str = ""
    star_histogram: list[dict[str, str]] = field(default_factory=list)
    ratings_by_feature: list[dict[str, str]] = field(default_factory=list)
    feature_bullets: list[str] = field(default_factory=list)
    raw_details: dict[str, Any] = field(default_factory=dict)
    source_url: str = ""

    def to_row(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "price": self.price,
            "color": self.color,
            "dimensions": self.dimensions,
            "material": self.material,
            "ratings_summary": self.ratings_summary,
            "star_histogram_json": json.dumps(self.star_histogram),
            "ratings_by_feature_json": json.dumps(self.ratings_by_feature),
            "feature_bullets_json": json.dumps(self.feature_bullets),
            "raw_details_json": json.dumps(self.raw_details),
            "source_url": self.source_url,
        }


def _urls_from_env() -> list[str]:
    multi = os.environ.get("AMAZON_PRODUCT_URLS", "").strip()
    if multi:
        parts = [u.strip() for u in multi.split(",") if u.strip()]
        return parts[:MAX_SCRAPE_REQUESTS]
    single = os.environ.get("AMAZON_PRODUCT_URL", "").strip()
    if single:
        return [single][:MAX_SCRAPE_REQUESTS]
    return []


class ScrapePipeline:
    """Stage 1: bounded fetch + parse HTML into structured product fields."""

    def __init__(self, timeout: int = 15, delay_sec: float = 2.0):
        self.timeout = timeout
        self.delay_sec = delay_sec
        self._requests_used = 0
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml",
            }
        )

    def fetch(self, url: str | None) -> tuple[str, str]:
        """Return (html, effective_source_label)."""
        if not url:
            return _FALLBACK_HTML, "embedded_demo"
        if self._requests_used >= MAX_SCRAPE_REQUESTS:
            return _FALLBACK_HTML, "embedded_demo_request_cap"
        self._requests_used += 1
        time.sleep(self.delay_sec)
        try:
            r = self.session.get(url, timeout=self.timeout)
            r.raise_for_status()
            text = r.text
            if len(text) < 800 or "automated access" in text.lower():
                return _FALLBACK_HTML, "embedded_demo_blocked_or_short"
            return text, url
        except requests.RequestException:
            return _FALLBACK_HTML, "embedded_demo_network_error"

    def _parse_tech_table(self, soup: BeautifulSoup, rec: ProductRecord) -> None:
        seen_tables: set[int] = set()
        for sel in (
            "#productDetails_techSpec_section_1",
            "#productDetails_detailBullets_sections1",
            "table#productDetails_detailBullets_sections1",
            "table.prodDetTable",
        ):
            table = soup.select_one(sel)
            if not table or id(table) in seen_tables:
                continue
            seen_tables.add(id(table))
            for row in table.select("tr"):
                cells = row.find_all(["th", "td"])
                if len(cells) < 2:
                    continue
                key = cells[0].get_text(" ", strip=True)
                val = cells[1].get_text(" ", strip=True)
                if not key or not val:
                    continue
                lk = key.lower()
                rec.raw_details.setdefault("attribute_rows", []).append(
                    {"name": key, "value": val}
                )
                if "color" in lk and not rec.color:
                    rec.color = val
                elif "dimension" in lk or "size" in lk:
                    if not rec.dimensions:
                        rec.dimensions = val
                elif "material" in lk:
                    if not rec.material:
                        rec.material = val
                elif "customer reviews" in lk or "ratings" in lk:
                    if not rec.ratings_summary:
                        rec.ratings_summary = val[:2000]

    def _parse_star_histogram(self, soup: BeautifulSoup, rec: ProductRecord) -> None:
        root = soup.select_one("#histogramTable, table#histogramTable")
        if not root:
            return
        rows: list[dict[str, str]] = []
        for tr in root.select("tr"):
            label = tr.get("aria-label") or ""
            tds = tr.find_all("td")
            if len(tds) >= 2:
                star = tds[0].get_text(" ", strip=True)
                pct = tds[1].get_text(" ", strip=True)
                if star or pct:
                    rows.append({"stars": star or label, "percent": pct})
            elif label:
                rows.append({"stars": label, "percent": tr.get_text(" ", strip=True)})
        rec.star_histogram = rows
        if rows:
            rec.raw_details["star_histogram_text"] = root.get_text(" ", strip=True)[:2000]

    def _parse_ratings_by_feature(self, soup: BeautifulSoup, rec: ProductRecord) -> None:
        out: list[dict[str, str]] = []
        selectors = (
            "#cr-snapshot-lighthouse-attributes div",
            "[data-hook='cr-lighthouse-row']",
            "tr[data-hook='cr-lighthouse-row']",
        )
        seen: set[str] = set()
        for sel in selectors:
            for node in soup.select(sel):
                text = node.get_text(" ", strip=True)
                if not text or len(text) > 300:
                    continue
                # "Comfort 4.1 out of 5" or two spans
                m = re.match(
                    r"^(.+?)\s+([\d.]+)\s+out\s+of\s+5",
                    text,
                    re.I,
                )
                if m:
                    key = f"{m.group(1).strip()}|{m.group(2)}"
                    if key not in seen:
                        seen.add(key)
                        out.append({"aspect": m.group(1).strip(), "rating": m.group(2)})
                    continue
                spans = node.select("span")
                if len(spans) >= 2:
                    a = spans[0].get_text(strip=True)
                    b = spans[-1].get_text(strip=True)
                    if a and b and re.search(r"\d", b):
                        key = f"{a}|{b}"
                        if key not in seen:
                            seen.add(key)
                            out.append({"aspect": a, "rating": b})
        rec.ratings_by_feature = out

    def parse(self, html: str, source_url: str) -> ProductRecord:
        soup = BeautifulSoup(html, "html.parser")
        rec = ProductRecord(source_url=source_url)

        t = soup.select_one("#productTitle, span#productTitle, h1#title")
        if t:
            rec.title = t.get_text(strip=True)

        whole = soup.select_one("span.a-price-whole")
        frac = soup.select_one("span.a-price-fraction")
        if whole:
            w = whole.get_text(strip=True).replace(",", "").replace(".", "")
            rec.price = w
            if frac:
                rec.price = f"{w}.{frac.get_text(strip=True)}"
        if not rec.price:
            aoff = soup.select_one(".a-price .a-offscreen")
            if aoff:
                rec.price = aoff.get_text(strip=True)

        for li in soup.select("#feature-bullets ul li span.a-list-item, #featurebullets_feature_div li"):
            text = li.get_text(" ", strip=True)
            if text:
                rec.feature_bullets.append(text)

        low_bullets = " ".join(rec.feature_bullets).lower()
        for needle, attr in [
            ("color:", "color"),
            ("dimension", "dimensions"),
            ("material:", "material"),
        ]:
            if needle in low_bullets:
                for b in rec.feature_bullets:
                    bl = b.lower()
                    if needle in bl and ":" in b:
                        val = b.split(":", 1)[-1].strip()
                        if attr == "dimensions" and not rec.dimensions:
                            rec.dimensions = val
                        elif attr == "color" and not rec.color:
                            rec.color = val
                        elif attr == "material" and not rec.material:
                            rec.material = val

        color_twister = soup.select_one("#variation_color_name .selection")
        if color_twister and not rec.color:
            rec.color = color_twister.get_text(strip=True)

        self._parse_tech_table(soup, rec)
        self._parse_star_histogram(soup, rec)
        self._parse_ratings_by_feature(soup, rec)

        # Overall review count / average (common hooks)
        for sel in (
            "[data-hook='rating-out-of-text']",
            "[data-hook='total-review-count']",
            "#acrPopover",
        ):
            el = soup.select_one(sel)
            if el:
                snippet = el.get_text(" ", strip=True)
                if snippet and not rec.ratings_summary:
                    rec.ratings_summary = snippet[:2000]
                break

        if not rec.ratings_summary:
            det = soup.select_one("#productDetails_detailBullets_sections1, table.a-keyvalue")
            if det:
                txt = det.get_text(" ", strip=True)
                rec.raw_details["detail_table_text"] = txt[:4000]
                if "rating" in txt.lower() or "review" in txt.lower():
                    rec.ratings_summary = txt[:2000]

        return rec

    def run(self, urls: list[str]) -> list[ProductRecord]:
        records: list[ProductRecord] = []
        if not urls:
            html, src = self.fetch(None)
            records.append(self.parse(html, src))
            return records
        for u in urls[:MAX_SCRAPE_REQUESTS]:
            html, src = self.fetch(u)
            records.append(self.parse(html, src))
        return records


class DatabasePipeline:
    """Stage 2: create table if needed and insert processed rows into SQLite."""

    def __init__(self, db_path: str | Path | None = None):
        default = Path(__file__).resolve().parent / "wda_01_amazon.sqlite"
        raw = os.environ.get("SQLITE_PATH", "").strip()
        self.db_path = Path(db_path or raw or default)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def ensure_table(self, conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS amazon_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price TEXT,
                color TEXT,
                dimensions TEXT,
                material TEXT,
                ratings_summary TEXT,
                star_histogram_json TEXT,
                ratings_by_feature_json TEXT,
                feature_bullets_json TEXT,
                raw_details_json TEXT,
                source_url TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
        cur.close()

    def insert(self, rec: ProductRecord) -> None:
        self.insert_many([rec])

    def insert_many(self, records: list[ProductRecord]) -> None:
        if not records:
            return
        conn = sqlite3.connect(self.db_path)
        try:
            self.ensure_table(conn)
            cur = conn.cursor()
            for rec in records:
                row = rec.to_row()
                cur.execute(
                    """
                    INSERT INTO amazon_products (
                        title, price, color, dimensions, material, ratings_summary,
                        star_histogram_json, ratings_by_feature_json,
                        feature_bullets_json, raw_details_json, source_url
                    ) VALUES (
                        :title, :price, :color, :dimensions, :material, :ratings_summary,
                        :star_histogram_json, :ratings_by_feature_json,
                        :feature_bullets_json, :raw_details_json, :source_url
                    )
                    """,
                    row,
                )
                print("Inserted product id:", cur.lastrowid)
            conn.commit()
            cur.close()
            print("SQLite database:", self.db_path)
        finally:
            conn.close()


def main() -> None:
    urls = _urls_from_env()
    print(
        f"Pipeline 1: scrape + parse (max {MAX_SCRAPE_REQUESTS} external request(s); "
        f"{len(urls)} URL(s) configured)."
    )
    scrape = ScrapePipeline()
    records = scrape.run(urls)

    for i, record in enumerate(records, 1):
        print(f"\n--- Processed product {i} ---")
        print(json.dumps(record.to_row(), indent=2))

    print("\nPipeline 2: SQLite insert.")
    db = DatabasePipeline()
    db.insert_many(records)


if __name__ == "__main__":
    main()
