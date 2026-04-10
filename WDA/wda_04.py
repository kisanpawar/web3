"""
WDA 4 — E-commerce (Amazon): scrape → process pipeline → MySQL store.

Assignment coverage
-------------------
a. Extract product data from Amazon using two pipelines:
   - Pipeline 1 (ScrapePipeline): bounded HTTP (default 1 URL) and field normalization.
   - Pipeline 2 (DatabasePipeline): insert rows into MySQL.

b. Fields include color, dimensions, material, feature bullets, ratings summary,
   star histogram, and customer ratings by feature when the page exposes them.

Amazon note: keep requests minimal (MAX_SCRAPE_REQUESTS, default 1). Heavy scraping
needs permission, official APIs, or proxies — not used here.

Environment
-----------
  AMAZON_PRODUCT_URL, AMAZON_PRODUCT_URLS, MAX_SCRAPE_REQUESTS  — same as wda_01
  MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE — for inserts

Dependencies: pip install requests beautifulsoup4 mysql-connector-python
"""

from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import wda_01_amazon_mysql_pipeline as core  # noqa: E402


def _product_urls() -> list[str]:
    alt = os.environ.get("AMAZON_PRODUCT_URL_ALT", "").strip()
    if alt:
        return [alt][: core.MAX_SCRAPE_REQUESTS]
    return core._urls_from_env()


def main() -> None:
    print("WDA 4: Amazon scrape (pipeline 1) -> MySQL (pipeline 2).\n")
    urls = _product_urls()
    records = core.ScrapePipeline().run(urls)
    for i, rec in enumerate(records, 1):
        print(f"\n--- Product {i} ---")
        print(json.dumps(rec.to_row(), indent=2))
    core.DatabasePipeline().insert_many(records)


if __name__ == "__main__":
    main()
