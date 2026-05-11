#!/usr/bin/env bash
# Examples:
#   ./run.sh --status
#   ./run.sh --limit 3
#   ./run.sh --type audio --limit 1
#   ./run.sh --file "photo name"
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
python3 main.py "$@"
