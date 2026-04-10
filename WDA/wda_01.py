"""
WDA 1 — E-commerce (Amazon) scrape → process pipeline → MySQL store (wda_01.py).

Important: Amazon restricts automated access. Use only a tiny number of requests
(no proxies in this demo). For coursework, prefer your own test HTML or obey robots/ToS.

Dependencies: pip install requests beautifulsoup4 mysql-connector-python
Set env: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE (optional MYSQL_PORT)
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

import requests
from bs4 import BeautifulSoup

try:
    import mysql.connector as mysql_connector
except ImportError:
    mysql_connector = None  # type: ignore


# --- Minimal demo HTML if live request fails (educational fallback) ---
_FALLBACK_HTML = """
<html><head><title>Demo Widget — Amazon-style snippet</title></head><body>
<span id="productTitle">Demo Stainless Water Bottle 750ml</span>
<div id="feature-bullets"><ul class="a-unordered-list a-vertical a-spacing-mini">
<li><span class="a-list-item">Color: Ocean Blue</span></li>
<li><span class="a-list-item">Material: 18/8 stainless steel</span></li>
<li><span class="a-list-item">Dimensions: 9 x 9 x 26 cm</span></li>
</ul></div>
<table id="productDetails_detailBullets_sections1" class="a-keyvalue">
<tr><th>Customer Reviews</th><td>4.2 stars — 1,204 ratings</td></tr>
</table>
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
    feature_bullets: list[str] = field(default_factory=list)
    raw_details: dict[str, Any] = field(default_factory=dict)

    def to_row(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "price": self.price,
            "color": self.color,
            "dimensions": self.dimensions,
            "material": self.material,
            "ratings_summary": self.ratings_summary,
            "feature_bullets_json": json.dumps(self.feature_bullets),
            "raw_details_json": json.dumps(self.raw_details),
        }


class ScrapePipeline:
    """Stage 1: fetch (few requests) and parse HTML into structured fields."""

    def __init__(self, timeout: int = 15, delay_sec: float = 2.0):
        self.timeout = timeout
        self.delay_sec = delay_sec
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (education; WDA assignment; minimal requests)",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    def fetch(self, url: str | None) -> str:
        if not url:
            return _FALLBACK_HTML
        time.sleep(self.delay_sec)
        try:
            r = self.session.get(url, timeout=self.timeout)
            r.raise_for_status()
            if len(r.text) < 500 or "api-services-support@amazon" in r.text.lower():
                return _FALLBACK_HTML
            return r.text
        except requests.RequestException:
            return _FALLBACK_HTML

    def parse(self, html: str) -> ProductRecord:
        soup = BeautifulSoup(html, "html.parser")
        rec = ProductRecord()

        t = soup.select_one("#productTitle, span#productTitle")
        if t:
            rec.title = t.get_text(strip=True)

        whole = soup.select_one("span.a-price-whole")
        frac = soup.select_one("span.a-price-fraction")
        if whole:
            rec.price = whole.get_text(strip=True).replace(".", "")
            if frac:
                rec.price = f"{rec.price}.{frac.get_text(strip=True)}"

        bullets = []
        for li in soup.select("#feature-bullets ul li span.a-list-item"):
            text = li.get_text(" ", strip=True)
            if text:
                bullets.append(text)
        rec.feature_bullets = bullets

        low = " ".join(bullets).lower()
        for label, attr in [
            ("color:", "color"),
            ("dimensions:", "dimensions"),
            ("material:", "material"),
        ]:
            if label in low:
                for b in bullets:
                    if label in b.lower():
                        setattr(rec, attr, b.split(":", 1)[-1].strip())
                        break

        det = soup.select_one("#productDetails_detailBullets_sections1, table.a-keyvalue")
        if det:
            rec.raw_details["detail_table_text"] = det.get_text(" ", strip=True)
            if "rating" in det.get_text().lower() or "review" in det.get_text().lower():
                rec.ratings_summary = det.get_text(" ", strip=True)[:500]

        # Ratings by feature (if present)
        for row in soup.select("#cr-snapshot-lighthouse-attributes div, [data-hook='cr-lighthouse-row']"):
            txt = row.get_text(" ", strip=True)
            if txt and len(txt) < 200:
                rec.raw_details.setdefault("rating_features", []).append(txt)

        return rec

    def run(self, url: str | None) -> ProductRecord:
        html = self.fetch(url)
        return self.parse(html)


class DatabasePipeline:
    """Stage 2: persist processed records to MySQL."""

    def __init__(self):
        self.config = {
            "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
            "port": int(os.environ.get("MYSQL_PORT", "3306")),
            "user": os.environ.get("MYSQL_USER", "root"),
            "password": os.environ.get("MYSQL_PASSWORD", ""),
            "database": os.environ.get("MYSQL_DATABASE", "wda_lab"),
        }

    def ensure_table(self, conn) -> None:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS amazon_products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(512),
                price VARCHAR(64),
                color VARCHAR(256),
                dimensions VARCHAR(256),
                material VARCHAR(256),
                ratings_summary TEXT,
                feature_bullets_json TEXT,
                raw_details_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        cur.close()

    def insert(self, rec: ProductRecord) -> None:
        if mysql_connector is None:
            print("mysql-connector-python not installed; skipping DB insert.")
            print("Row that would be inserted:", json.dumps(rec.to_row(), indent=2))
            return
        conn = mysql_connector.connect(**self.config)
        try:
            self.ensure_table(conn)
            row = rec.to_row()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO amazon_products
                (title, price, color, dimensions, material, ratings_summary, feature_bullets_json, raw_details_json)
                VALUES (%(title)s, %(price)s, %(color)s, %(dimensions)s, %(material)s, %(ratings_summary)s, %(feature_bullets_json)s, %(raw_details_json)s)
                """,
                row,
            )
            conn.commit()
            new_id = cur.lastrowid
            cur.close()
            print("Inserted product id:", new_id)
        finally:
            conn.close()


def main() -> None:
    # ONE optional URL — leave None to use embedded demo HTML only (zero external requests).
    product_url = os.environ.get("AMAZON_PRODUCT_URL")  # e.g. one product page for lab

    print("Pipeline 1: scrape + parse (max 1 external request if URL set).")
    scrape = ScrapePipeline()
    record = scrape.run(product_url)

    print("\n--- Processed product ---")
    print(json.dumps(record.to_row(), indent=2))

    print("\nPipeline 2: MySQL insert.")
    db = DatabasePipeline()
    db.insert(record)


if __name__ == "__main__":
    main()
