# webscrape-data – Big Tech Valuation Map

Goal: scrape key ratios for a small universe of big tech stocks from
StockAnalysis (static HTML), compute simple value/quality scores, and
visualize which names look relatively "cheap and good" vs "expensive and weak".

Universe (initial):
- AAPL, MSFT, NVDA, META, GOOGL, AMZN, NFLX, AVGO, CRM, ADSK

Stack:
- Python 3
- `requests`
- `beautifulsoup4`
- `pandas`
- `matplotlib`

## Layout

- `config.py`  – ticker list, constants
- `scrape.py`  – fetch HTML for each ticker, parse ratios -> `data/stats.csv`
- `analyze.py` – load stats, compute value/quality scores -> `data/scored.csv`
- `plot.py`    – read scored data and output plots in `plots/`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local `.env` (not committed) with your User-Agent:

```bash
echo 'SCRAPER_USER_AGENT="webscrape-data/1.0 (student project; contact: you@example.com)"' > .env
```

## Run

1) Scrape stats:
```bash
python3 scrape.py
```

2) Compute scores:
```bash
python3 analyze.py
```

3) Generate plots:
```bash
python3 plot.py
```

**Or**

Do all together:
```bash
bash run_scrape.sh
```

Result: scatter plot(s) showing a value/quality map for the chosen big tech stocks.

## Plot interpretation

Metric definitions:

- `pe`: price-to-earnings ratio.
- `ps`: price-to-sales ratio.
- `roe`: return on equity (%).
- `dividend_yield`: annual dividend / price (%).
- `*_norm`: min-max normalized within the ticker set.

How the scores are computed (normalized within this ticker set):

- `pe_norm`, `ps_norm` are min-max scaled; lower is better.
- `value_score = 1 / (1 + pe_norm + ps_norm)` so lower P/E and P/S -> higher score.
- `roe_norm`, `dividend_yield_norm` are min-max scaled; higher is better.
- `quality_score = mean(roe_norm, dividend_yield_norm)`; higher is better.

`plots/value_vs_quality.png` is a scatter of each ticker on two composite scores:

- **X-axis (Value score):** higher = cheaper. It’s built from lower P/E and P/S.
- **Y-axis (Quality score):** higher = stronger fundamentals. It’s built from
  higher ROE and dividend yield.


How to read it:

- **Top-right:** relatively cheap *and* high quality (best quadrant).
- **Bottom-left:** relatively expensive *and* weak quality (worst quadrant).
- **Top-left:** high quality but expensive.
- **Bottom-right:** cheap but lower quality.

## Notes

- Source: StockAnalysis ratios page (example)
- `https://stockanalysis.com/stocks/aapl/financials/ratios/`
- Metrics scraped:
  `price`, `pe`, `ps`, `roe`, `dividend_yield`, `market_cap`
- `market_cap` on StockAnalysis ratios pages is listed in **millions USD**.
