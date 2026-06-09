#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Run scripts/setup.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "Backend running at http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --app-dir "$PROJECT_DIR/backend"
