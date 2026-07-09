#!/usr/bin/env bash
# Thin wrapper — see sync_100k_agent.py
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/sync_100k_agent.py" "$@"
