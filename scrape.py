"""Scrape Box Office Mojo's worldwide box office tables into CSV files under data/."""
import datetime
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
URL_TEMPLATE = "https://www.boxofficemojo.com/year/world/{year}/"
TABLE_SELECTOR = ".imdb-scroll-table table"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; box-office-scraper/1.0)"}


def url_to_txt(url, timeout=30):
    """Return the page HTML, or None if the request fails."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
    except requests.RequestException:
        return None
    return r.text if r.status_code == 200 else None


def parse_table(html_text):
    """Parse the box office table out of a page. Returns a DataFrame, or None if absent."""
    soup = BeautifulSoup(html_text, "html.parser")
    table = soup.select_one(TABLE_SELECTOR)
    if table is None:
        return None
    rows = table.find_all("tr")
    if not rows:
        return None
    header_names = [th.get_text(strip=True) for th in rows[0].find_all("th")]
    table_data = []
    for row in rows[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) == len(header_names):
            table_data.append(cols)
    return pd.DataFrame(table_data, columns=header_names)


def parse_and_extract(url, name="2020"):
    """Download `url`, parse its table and save it to data/<name>.csv. Returns True on success."""
    html_text = url_to_txt(url)
    if html_text is None:
        return False
    df = parse_table(html_text)
    if df is None:
        return False
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(os.path.join(DATA_DIR, f"{name}.csv"), index=False)
    return True


def run(start_year=None, years_ago=0):
    """Scrape `start_year` (default: current year) and the `years_ago` years before it.

    Returns {"finished": [years...], "failed": [years...]}.
    """
    if start_year is None:
        start_year = datetime.datetime.now().year
    if not isinstance(start_year, int) or len(str(start_year)) != 4:
        raise ValueError("start_year must be a 4-digit integer")
    if not isinstance(years_ago, int) or years_ago < 0:
        raise ValueError("years_ago must be a non-negative integer")

    result = {"finished": [], "failed": []}
    for year in range(start_year, start_year - years_ago - 1, -1):
        if parse_and_extract(URL_TEMPLATE.format(year=year), name=year):
            print(f"Finished {year}")
            result["finished"].append(year)
        else:
            print(f"{year} not finished")
            result["failed"].append(year)
    return result


if __name__ == "__main__":
    import sys

    year = int(sys.argv[1]) if len(sys.argv) > 1 else None
    back = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    print(run(start_year=year, years_ago=back))
