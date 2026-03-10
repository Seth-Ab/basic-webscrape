# Scrape big tech ratios from StockAnalysis into data/stats.csv.

import csv
import os
import time
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

from config import TICKERS, BASE_URL_TEMPLATE, METRIC_FIELDS

# Absolute path to data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Absolute path to the stats.csv file where scraped stats will be saved.
STATS_CSV = os.path.join(DATA_DIR, "stats.csv")

# Be polite to the host.
REQUEST_DELAY_SECONDS = 1.5
# Read user agent from environment so personal info isn't committed.
USER_AGENT = os.getenv(
    # Try user-provided agent, otherwise use a generic one.
    "SCRAPER_USER_AGENT",
    "webscrape-data/1.0 (contact: you@example.com)",
)

# StockAnalysis labels -> our CSV fields.
LABEL_TO_FIELD = {
    "Last Close Price": "price",
    "PE Ratio": "pe",
    "PS Ratio": "ps",
    "Return on Equity (ROE)": "roe",
    "Dividend Yield": "dividend_yield",
    "Market Cap": "market_cap",
}


def _fetch_html(ticker: str) -> str:
    # Download the ratios page for a single ticker.
    url = BASE_URL_TEMPLATE.format(ticker=ticker.lower())
    resp = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": USER_AGENT},
    )
    resp.raise_for_status()
    return resp.text

# Normalize common numeric formats (commas, percents, N/A).
def _to_number(text: str) -> Optional[float]:
    t = text.strip()
    if not t or t in {"-", "N/A"}:
        return None
    t = t.replace(",", "")
    if t.endswith("%"):
        try:
            return float(t[:-1])
        except ValueError:
            return None
    try:
        return float(t)
    except ValueError:
        return None


# Extract metrics from the StockAnalysis ratios table.
# look for a table that contains a "Current" column and then map row labels to our fields.
def _parse_metrics(html: str, ticker: str) -> Optional[Dict[str, float]]:
    # Parse the raw HTML into a BeautifulSoup object so we can navigate it
    soup = BeautifulSoup(html, "html.parser")

    # Dictionary where we will store the extracted metrics
    # Key = internal field name, Value = numeric metric
    metrics: Dict[str, float] = {}

    # Find the table that has a "Current" column and read matching rows.
    tables = soup.find_all("table")
    
    # Iterate through each table to find the one that contains a "Current" column
    for table in tables:
        # Get all rows in this table
        rows = table.find_all("tr")
        if not rows:
            # Skip empty tables
            continue

        # This will store the column index of the "Current" column
        current_idx = None

        # First pass: locate which column is labeled "Current"
        for row in rows:
            # Get all header/data cells in this row
            cells = row.find_all(["th", "td"])
            # Extract clean text from each cell
            labels = [c.get_text(strip=True) for c in cells]
            
            # Check if this row contains the "Current" column header
            if "Current" in labels:
                # Save the index of the "Current" column
                current_idx = labels.index("Current")
                break

        # If this table does not contain a "Current" column, skip it
        if current_idx is None:
            continue

        # Second pass: extract relevant metric values from this table
        for row in rows:
            cells = row.find_all(["th", "td"])

            # Ensure this row has enough columns to access current_idx
            if len(cells) <= current_idx:
                continue

            # The first cell is assumed to be the row label (metric name)
            label = cells[0].get_text(strip=True)

            # Only process rows that match labels we care about
            # (LABEL_TO_FIELD maps table labels to internal metric names)
            if label not in LABEL_TO_FIELD:
                continue

            # Extract the value under the "Current" column
            value_text = cells[current_idx].get_text(strip=True)

            # Convert the text (e.g. "12.34%" or "1.5B") to a float
            value = _to_number(value_text)

            # If conversion was successful, store it in our metrics dict
            if value is not None:
                metrics[LABEL_TO_FIELD[label]] = value
        
        # If we successfully extracted metrics from this table,
        # stop searching other tables
        if metrics:
            break

    # If no metrics were found in any table, return None
    if not metrics:
        return None
    
    # Otherwise return the extracted metrics dictionary
    return metrics


# Iterate through tickers, scrape metrics, and write a CSV.
def scrape_all() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    rows = []
    total = len(TICKERS)
    for idx, ticker in enumerate(TICKERS, start=1):
        try:
            print(f"[{idx}/{total}] Scraping {ticker}...")
            html = _fetch_html(ticker)
            metrics = _parse_metrics(html, ticker)
            if not metrics:
                print(f"[WARN] No metrics parsed for {ticker}; skipping")
                continue

            row = {"ticker": ticker}
            for field in METRIC_FIELDS:
                row[field] = metrics.get(field)
            rows.append(row)
        except Exception as e:
            print(f"[ERROR] Failed for {ticker}: {e}")
        finally:
            # Rate-limit requests to be polite.
            time.sleep(REQUEST_DELAY_SECONDS)

    if not rows:
        print("[WARN] No data scraped; stats.csv not written.")
        return

    # Write the aggregated rows once at the end.
    with open(STATS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ticker"] + METRIC_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {STATS_CSV}")


if __name__ == "__main__":
    scrape_all()
