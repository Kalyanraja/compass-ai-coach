#!/usr/bin/env sh
# Compass AI Engineering Enablement Coach - launcher for macOS/Linux.
# Needs only Python 3.9+ (standard library). No pip install, no internet, no API keys.
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
echo "Starting Compass on http://127.0.0.1:8765/"
exec "$PY" -m compass "$@"
