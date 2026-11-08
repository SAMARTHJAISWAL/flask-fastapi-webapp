"""Call a running server's scraper endpoint.

Usage: python trigger.py [BASE_URL]   (default: $SCRAPER_URL or http://127.0.0.1:8888)
"""
import os
import sys

import requests

base_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SCRAPER_URL", "http://127.0.0.1:8888")
endpoint = f"{base_url.rstrip('/')}/box-office-mojo-scraper"

r = requests.post(endpoint, json={}, timeout=120)
r.raise_for_status()
print(r.json())
