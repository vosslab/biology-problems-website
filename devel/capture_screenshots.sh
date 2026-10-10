#!/usr/bin/env bash
# Refresh all managed documentation screenshots and the MATCH demonstration.

set -e
capture_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$capture_directory/.."
source source_me.sh
exec node "$capture_directory/capture_screenshots.mjs" "$@"
