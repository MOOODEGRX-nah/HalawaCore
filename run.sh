#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [ "$(id -u)" = 0 ]; then
  echo 'Run HalawaCore as your normal desktop user, without sudo.' >&2
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  echo 'Create the environment first: python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt' >&2
  exit 1
fi
exec .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port "${HALAWACORE_PORT:-8000}" --workers 1 --no-access-log
