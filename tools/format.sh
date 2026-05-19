#!/usr/bin/env bash
# Format and quick-check the codebase. Requires `ruff` (pip install ruff).
set -e
cd "$(dirname "$0")/.."
ruff format src reference tests tools
ruff check --fix src reference tests tools
