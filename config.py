# Universe of tickers to scrape.
TICKERS = [
    "AAPL", "MSFT", "NVDA", "META", "GOOGL",
    "AMZN", "NFLX", "AVGO", "CRM", "ADSK",
]

# Label used in plot titles.
SECTOR_NAME = "US Big Tech"

# StockAnalysis ratios page (static HTML, easy to scrape).
# Example: https://stockanalysis.com/stocks/aapl/financials/ratios/
BASE_URL_TEMPLATE = "https://stockanalysis.com/stocks/{ticker}/financials/ratios/"

# Metrics we care about per ticker; keys are column names in the CSV we build.
METRIC_FIELDS = [
    "price",
    "pe",
    "ps",
    "roe",
    "dividend_yield",
    "market_cap",
]
