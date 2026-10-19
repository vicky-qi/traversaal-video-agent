#!/usr/bin/env bash
# Start Traversaal Video Studio and open it in the browser.
# Usage: ./start.sh        (run ./setup.sh once first)
set -euo pipefail
cd "$(dirname "$0")"
PORT="${STUDIO_PORT:-8765}"
URL="http://127.0.0.1:$PORT"
( sleep 2; if command -v open >/dev/null 2>&1; then open "$URL"; elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL"; fi ) &
exec render/env.sh python app/server.py
