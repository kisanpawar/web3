"""
WDA 4 — Same theme as WDA 1: Amazon-style product extraction + two-stage pipeline + MySQL.

Use a separate script so submission "number 4" is explicit. Keeps requests minimal;
set AMAZON_PRODUCT_URL for one live fetch, or run without env for zero network calls.

Dependencies: pip install requests beautifulsoup4 mysql-connector-python
"""

from __future__ import annotations

import json
import os
import sys

# Reuse implementation from wda_01
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import wda_01 as core  # noqa: E402


def main() -> None:
    print("WDA 4: alternate entry - same pipelines as WDA 1.\n")
    url = os.environ.get("AMAZON_PRODUCT_URL_ALT") or os.environ.get("AMAZON_PRODUCT_URL")
    rec = core.ScrapePipeline().run(url)
    print(json.dumps(rec.to_row(), indent=2))
    core.DatabasePipeline().insert(rec)


if __name__ == "__main__":
    main()
