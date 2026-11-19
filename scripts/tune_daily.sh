#!/usr/bin/env bash
# Daily search tuning (Replit scheduled job): bash scripts/update_and_run.sh bash scripts/tune_daily.sh
# 1. Telegram: sample the channels that yesterday's channels forwarded from (free; reads only).
# 2. X: run the next probe round (10 posts a variant, inside the daily and monthly caps).
# 3. Score it with tune.py (needs OPENROUTER_API_KEY; without it this step stops and nothing is billed).
set -uo pipefail
cd "$(dirname "$0")/.."
python ingest/telegram/sample_channels.py --snowball || echo "Telegram sample failed (see above)."
next=$(python ingest/tune.py --next-probe)
if [ -n "$next" ]; then node ingest/x/probe.mjs "$next" || echo "X probe failed (see above)."; else echo "No new X probe round waiting."; fi
python ingest/tune.py || echo "Scoring skipped (see above)."
