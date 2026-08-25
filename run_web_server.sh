#!/usr/bin/env bash
# run_web_server.sh - open a short-lived local preview of Biology Problems OER.

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "$script_dir" rev-parse --show-toplevel)"
readonly repo_root
cd "$repo_root"

source "$repo_root/source_me.sh"
export NO_MKDOCS_2_WARNING=1

readonly PREVIEW_SECONDS=300
readonly PREVIEW_ADDRESS="127.0.0.1:8000"
readonly PREVIEW_URL="http://$PREVIEW_ADDRESS/"
server_pid=""

stop_server() {
	if [[ -z "$server_pid" ]]; then
		return 0
	fi

	if kill -0 "$server_pid" 2>/dev/null; then
		kill "$server_pid" 2>/dev/null || true
	fi
	wait "$server_pid" 2>/dev/null || true
	server_pid=""
}

trap stop_server EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

printf 'Starting the Biology Problems OER preview at %s.\n' "$PREVIEW_URL"
printf '%s\n' \
	'The preview opens in your browser and stops after five minutes; press Ctrl-C to stop sooner.'
python3 -m mkdocs serve --dev-addr "$PREVIEW_ADDRESS" --open &
server_pid=$!
deadline=$((SECONDS + PREVIEW_SECONDS))

# Polling keeps the timeout portable on macOS, where GNU timeout is not included.
while kill -0 "$server_pid" 2>/dev/null; do
	if ((SECONDS >= deadline)); then
		printf 'Five-minute preview limit reached; stopping MkDocs.\n'
		stop_server
		exit 0
	fi
	sleep 1
done

# Preserve an early MkDocs failure so callers can detect startup errors.
if wait "$server_pid"; then
	server_status=0
else
	server_status=$?
fi
server_pid=""
exit "$server_status"
