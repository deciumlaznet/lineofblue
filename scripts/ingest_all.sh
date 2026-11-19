#!/usr/bin/env bash
# Runs every approved source once, within each connector's own caps. Used by the Replit scheduled job.
set -uo pipefail
cd "$(dirname "$0")/.."
python ingest/telegram/run.py || echo "Telegram run failed (see above)."
node ingest/x/run.mjs || echo "X run failed (see above)."
python ingest/news/run.py || echo "News run failed (see above)."
