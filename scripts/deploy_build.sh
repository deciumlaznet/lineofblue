#!/usr/bin/env bash
# Replit publish build step for the private site: install the web server's packages and build the pages.
# The publish build in .replit runs:  cd lob && (git pull --ff-only origin main || true) && bash scripts/deploy_build.sh
set -euo pipefail
cd "$(dirname "$0")/.."
npm ci --prefix web --omit=dev --no-audit --no-fund
python3 scripts/build.py
echo "Site built at $(git rev-parse --short HEAD 2>/dev/null || echo unknown)."
