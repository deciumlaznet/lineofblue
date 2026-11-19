#!/usr/bin/env bash
# Replit entry point. Pulls the latest merged code from GitHub main, then runs the given command, so Replit
# always runs what is on GitHub and nobody pastes commands into the shell.
#   bash scripts/update_and_run.sh                         (update only)
#   bash scripts/update_and_run.sh bash scripts/ingest_all.sh   (update, then run every approved source)
set -euo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only --quiet origin main
echo "Up to date with GitHub main at $(git rev-parse --short HEAD)."
if [ $# -gt 0 ]; then exec "$@"; fi
