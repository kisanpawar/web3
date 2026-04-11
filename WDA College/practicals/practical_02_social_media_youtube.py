"""
Practical No 02 — Scrape an online social media site for data

Aim: Use the YouTube Data API to fetch video metadata (title, views, likes)
for given URLs and store results in SQLite. Display with pandas.

Dependencies: pip install google-api-python-client pandas

Security: Set your API key in the environment (never commit keys):
  set YOUTUBE_API_KEY=your_key_here   (Windows cmd)
  $env:YOUTUBE_API_KEY="your_key"    (PowerShell)
"""

from __future__ import annotations

import os
import re
import sqlite3

import pandas as pd
from googleapiclient.discovery import build

PRACTICAL_NAME = "Practical 02 — Social media (YouTube) data"

URLS = [
    "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
]


def main() -> None:
    print(PRACTICAL_NAME)
    api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "Set environment variable YOUTUBE_API_KEY to your YouTube Data API v3 key."
        )

    conn = sqlite3.connect("youtube_data.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS videos (title TEXT, views INT, likes TEXT)")

    youtube = build("youtube", "v3", developerKey=api_key)
    print("Scraping data...")
    for url in URLS:
        try:
            m = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})", url)
            if not m:
                print(f"Could not parse video id from {url}")
                continue
            vid_id = m.group(1)
            resp = youtube.videos().list(part="snippet,statistics", id=vid_id).execute()
            if resp["items"]:
                item = resp["items"][0]
                title = item["snippet"]["title"]
                views = int(item["statistics"].get("viewCount", 0))
                likes = item["statistics"].get("likeCount", "0")
                c.execute("INSERT INTO videos VALUES (?, ?, ?)", (title, views, likes))
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    conn.commit()
    print("\n--- DATABASE CONTENTS ---")
    df = pd.read_sql_query("SELECT * FROM videos", conn)
    print(df.to_string())
    conn.close()


if __name__ == "__main__":
    main()
