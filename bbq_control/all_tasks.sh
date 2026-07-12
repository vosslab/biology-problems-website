#!/usr/bin/env bash

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec /opt/homebrew/opt/python@3.12/bin/python3.12 "$script_dir/all_tasks.py" "$@"
