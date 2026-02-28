#!/usr/bin/env bash

set -u -o pipefail

if [[ -f ".venv/bin/activate" ]]; then
  # Linux/macOS style virtual environment
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
elif [[ -f ".venv/Scripts/activate" ]]; then
  # Windows virtual environment (Git Bash)
  # shellcheck disable=SC1091
  source ".venv/Scripts/activate"
else
  echo "Virtual environment activation script not found in .venv"
  exit 1
fi

python -m pytest -q
test_exit_code=$?

if [[ $test_exit_code -eq 0 ]]; then
  exit 0
else
  exit 1
fi
