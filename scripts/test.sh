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

cd "$PROJECT_DIR/backend"

echo "==> Running ruff check..."
ruff check .
RUFF_EXIT=$?

echo ""
echo "==> Running pytest..."
pytest tests/ -v
PYTEST_EXIT=$?

echo ""
if [ $RUFF_EXIT -eq 0 ] && [ $PYTEST_EXIT -eq 0 ]; then
    echo "All checks passed."
    exit 0
else
    echo "Some checks failed (ruff: $RUFF_EXIT, pytest: $PYTEST_EXIT)."
    exit 1
fi
