"""
Practical No 01 — Scrape an online E-Commerce site for data

Aim: Extract product data from Amazon (small request set), optionally using a
two-stage pipeline: (1) scrape/normalize, (2) store in a database. Scrape
details such as title, price, rating (extend for color, dimensions, material,
feature ratings as on the live page).

Dependencies: pip install requests beautifulsoup4
(Database: stdlib sqlite3 — matches the practical file sample; use MySQL
connector if your instructor requires MySQL.)
"""

from __future__ import annotations

import sqlite3

import requests
from bs4 import BeautifulSoup

PRACTICAL_NAME = "Practical 01 — E-Commerce (Amazon) data scraping"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_amazon(url: str) -> tuple[str, str, str]:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("span", id="productTitle")
    price = soup.find("span", class_="a-price-whole")
    rating = soup.find("span", class_="a-icon-alt")
    return (
        title.get_text(strip=True) if title else "Not Found",
        price.get_text(strip=True) if price else "Not Found",
        rating.get_text(strip=True) if rating else "Not Found",
    )


def main() -> None:
    print(PRACTICAL_NAME)
    conn = sqlite3.connect("amazon_products.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            title TEXT,
            price TEXT,
            rating TEXT
        )"""
    )
    conn.commit()

    # Replace with any single product URL; keep requests minimal for coursework.
    url = "https://www.amazon.in/dp/B0DZF1485D"
    title, price, rating = scrape_amazon(url)
    cursor.execute(
        "INSERT INTO products (title, price, rating) VALUES (?, ?, ?)",
        (title, price, rating),
    )
    conn.commit()
    print("Data Inserted")
    cursor.execute("SELECT * FROM products")
    for row in cursor.fetchall():
        print(row)
    conn.close()


if __name__ == "__main__":
    main()
