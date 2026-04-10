"""
Shared Amazon scrape + MySQL persistence for WDA 4.

Pipeline 1 — ScrapePipeline: same bounded fetch/parse as wda_01 (small request budget).
Pipeline 2 — DatabasePipeline: inserts normalized rows into MySQL.

Environment (MySQL)
-------------------
  MYSQL_HOST      — default localhost
  MYSQL_PORT      — default 3306
  MYSQL_USER      — required for live insert
  MYSQL_PASSWORD  — required for live insert
  MYSQL_DATABASE  — required for live insert

If MySQL env is incomplete, inserts are skipped with a clear message (demo HTML path still works).

Dependencies: pip install requests beautifulsoup4 mysql-connector-python
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Reuse scrape types and logic from wda_01
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import wda_01 as _amazon  # noqa: E402

MAX_SCRAPE_REQUESTS = _amazon.MAX_SCRAPE_REQUESTS
ProductRecord = _amazon.ProductRecord
ScrapePipeline = _amazon.ScrapePipeline
_urls_from_env = _amazon._urls_from_env


class DatabasePipeline:
    """Stage 2: create table if needed and insert processed rows into MySQL."""

    def __init__(self) -> None:
        self.host = os.environ.get("MYSQL_HOST", "localhost").strip()
        self.port = int(os.environ.get("MYSQL_PORT", "3306") or "3306")
        self.user = os.environ.get("MYSQL_USER", "").strip()
        self.password = os.environ.get("MYSQL_PASSWORD", "")
        self.database = os.environ.get("MYSQL_DATABASE", "").strip()

    def _config_ok(self) -> bool:
        return bool(self.user and self.database)

    def _connect(self) -> Any:
        import mysql.connector  # type: ignore

        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
        )

    def ensure_table(self, cur: Any) -> None:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS amazon_products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT,
                price VARCHAR(64),
                color TEXT,
                dimensions TEXT,
                material TEXT,
                ratings_summary TEXT,
                star_histogram_json LONGTEXT,
                ratings_by_feature_json LONGTEXT,
                feature_bullets_json LONGTEXT,
                raw_details_json LONGTEXT,
                source_url VARCHAR(2048),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )

    def insert(self, rec: ProductRecord) -> None:
        self.insert_many([rec])

    def insert_many(self, records: list[ProductRecord]) -> None:
        if not records:
            return
        if not self._config_ok():
            print(
                "MySQL: skipping insert (set MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE; "
                "optional MYSQL_HOST, MYSQL_PORT)."
            )
            return
        try:
            import mysql.connector  # type: ignore
        except ImportError:
            print("MySQL: install mysql-connector-python to enable inserts.")
            return

        conn = None
        try:
            conn = self._connect()
            cur = conn.cursor()
            self.ensure_table(cur)
            for rec in records:
                row = rec.to_row()
                cur.execute(
                    """
                    INSERT INTO amazon_products (
                        title, price, color, dimensions, material, ratings_summary,
                        star_histogram_json, ratings_by_feature_json,
                        feature_bullets_json, raw_details_json, source_url
                    ) VALUES (
                        %(title)s, %(price)s, %(color)s, %(dimensions)s, %(material)s,
                        %(ratings_summary)s, %(star_histogram_json)s,
                        %(ratings_by_feature_json)s, %(feature_bullets_json)s,
                        %(raw_details_json)s, %(source_url)s
                    )
                    """,
                    row,
                )
                print("Inserted product id:", cur.lastrowid)
            conn.commit()
            cur.close()
            print(f"MySQL database: {self.database} @ {self.host}:{self.port}")
        except mysql.connector.Error as e:  # type: ignore
            print("MySQL error:", e)
            if conn is not None:
                conn.rollback()
        finally:
            if conn is not None:
                conn.close()


def main() -> None:
    import json

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

    print("\nPipeline 2: MySQL insert.")
    DatabasePipeline().insert_many(records)


if __name__ == "__main__":
    main()
