#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

echo "==> Setting up Learning OS development environment..."

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "    Virtual environment created at $VENV_DIR"
else
    echo "    Virtual environment already exists, skipping creation."
fi

# Activate and install dependencies
source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q
pip install -r "$PROJECT_DIR/backend/requirements.txt"

# Initialize SQLite database directory and tables
mkdir -p "$PROJECT_DIR/backend/data"

DB_INIT_SCRIPT="$PROJECT_DIR/backend/db/init.sql"
if [ -f "$DB_INIT_SCRIPT" ]; then
    sqlite3 "$PROJECT_DIR/backend/data/learning_os.db" < "$DB_INIT_SCRIPT"
    echo "    Database initialized."
else
    echo "    No init.sql found — database will be created on first run."
fi

echo ""
echo "============================================"
echo "  Setup complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  source .venv/bin/activate"
echo "  sh scripts/dev.sh"
