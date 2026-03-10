#!/usr/bin/env bash
set -euo pipefail

# Load environment variables if .env exists.
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

python3 scrape.py
python3 analyze.py
python3 plot.py
