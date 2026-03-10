# This script computes simple "value" and "quality" scores for each stock
# based on the metrics scraped in stats.csv, and writes the results to scored.csv.

import os

import pandas as pd

from config import METRIC_FIELDS

# Absolute path to data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Absolute paths to input (stats) and output (scored) CSV files.
STATS_CSV = os.path.join(DATA_DIR, "stats.csv")
SCORED_CSV = os.path.join(DATA_DIR, "scored.csv")


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    # Work on a copy to avoid mutating the caller's DataFrame.
    df = df.copy()

    # Basic cleaning: convert numeric columns and drop rows missing core metrics.
    for col in METRIC_FIELDS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["pe", "roe"], how="any")

    # Normalize some metrics for scoring (z-score-ish or min-max)
    # For simplicity: min-max scaling where possible.
    def min_max(col: str):
        # Min-max scaling with safe handling for empty or constant columns.
        c = df[col]
        if c.dropna().empty:
            return pd.Series([0] * len(c), index=c.index)
        if c.max() == c.min():
            return pd.Series([0] * len(c), index=c.index)
        return (c - c.min()) / (c.max() - c.min())

    # Lower P/E and P/S are better for "value."
    df["pe_norm"] = min_max("pe")
    if "ps" in df.columns:
        df["ps_norm"] = min_max("ps")
    else:
        df["ps_norm"] = 0

    # Higher ROE and dividend yield are better for "quality."
    for col in ["roe", "dividend_yield"]:
        if col in df.columns:
            df[f"{col}_norm"] = min_max(col)
        else:
            df[f"{col}_norm"] = 0

    # Value score: cheaper (lower P/E, P/S) -> higher score.
    df["value_score"] = 1 / (1 + df["pe_norm"] + df["ps_norm"])

    # Quality score: average of normalized quality metrics.
    quality_components = ["roe_norm", "dividend_yield_norm"]
    df["quality_score"] = df[quality_components].mean(axis=1)

    return df


def main() -> None:
    # Entry point: load, score, and write output CSV.
    if not os.path.exists(STATS_CSV):
        print(f"stats.csv not found at {STATS_CSV}; run scrape.py first.")
        return

    # Read from `stats.csv`
    df = pd.read_csv(STATS_CSV)
    scored = compute_scores(df)

    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Write to `scored.csv`
    scored.to_csv(SCORED_CSV, index=False)
    print(f"Wrote scored data to {SCORED_CSV}")


if __name__ == "__main__":
    main()
