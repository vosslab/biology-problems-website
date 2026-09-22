#!/usr/bin/env bash
# Run the Playwright browser test suite. playwright.config.ts owns the server.

set -euo pipefail

# Usage
usage() {
	cat <<'USAGE'
Usage: run_playwright_tests.sh [-h|--help] [--build] [PLAYWRIGHT_ARGS...]

  -h, --help    Print this help and exit 0.
  --build       Force a 'mkdocs build' pass before running tests.

Any remaining arguments are forwarded to 'npx playwright test'.
USAGE
}

# Parse script-level flags; collect the rest for playwright.
FORCE_BUILD=0
PLAYWRIGHT_ARGS=()

while [ "$#" -gt 0 ]; do
	case "$1" in
		-h|--help)
			usage
			exit 0
			;;
		--build)
			FORCE_BUILD=1
			shift
			;;
		*)
			PLAYWRIGHT_ARGS+=("$1")
			shift
			;;
	esac
done

cd "$(git rev-parse --show-toplevel)"

# Preflight: ensure required tools and project state are present.
command -v node >/dev/null 2>&1 || { echo "ERROR: node not found on PATH. Install Node.js first." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "ERROR: npm not found on PATH. Install Node.js first." >&2; exit 1; }

if [ ! -d node_modules ]; then
	echo "ERROR: node_modules/ missing. Run 'npm install' first." >&2
	exit 1
fi

if [ ! -f playwright.config.ts ]; then
	echo "ERROR: playwright.config.ts not found at repo root." >&2
	echo "  Is this the right repo? Expected: $(pwd)/playwright.config.ts" >&2
	exit 1
fi

# Build gate: rebuild the MkDocs site when forced or when the built output is
# not yet present. A normal run otherwise relies on the config's webServer.
if [ "$FORCE_BUILD" -eq 1 ] || [ ! -d site ]; then
	if ! command -v mkdocs >/dev/null 2>&1; then
		echo "ERROR: mkdocs not found on PATH. Install MkDocs first." >&2
		exit 1
	fi
	echo "==> running mkdocs build..."
	mkdocs build
fi

# Run Playwright; capture exit code so we can print the summary line.
# ${arr[@]+...} expands to nothing when the array is empty under set -u (bash 3.2 safe).
# [*] on the echo joins args into one display string; [@] on the run line preserves word splitting.
echo "==> npx playwright test ${PLAYWRIGHT_ARGS[*]+"${PLAYWRIGHT_ARGS[*]}"}"
PW_EXIT=0
set +e  # allow playwright to exit non-zero; captured in PW_EXIT below
npx playwright test ${PLAYWRIGHT_ARGS[@]+"${PLAYWRIGHT_ARGS[@]}"}
PW_EXIT=$?
set -e  # re-enable exit-on-error

# Summary line.
if [ "$PW_EXIT" -eq 0 ]; then
	echo "PASS: playwright tests passed."
else
	echo "FAIL: playwright tests failed (exit code $PW_EXIT)."
fi

exit "$PW_EXIT"
