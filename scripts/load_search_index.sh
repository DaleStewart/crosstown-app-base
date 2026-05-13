#!/usr/bin/env sh
# Wrapper for azd postprovision hook (POSIX).
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
. .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet azure-identity azure-search-documents azure-cosmos
python scripts/load_search_index.py
