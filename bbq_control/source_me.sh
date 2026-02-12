#!/usr/bin/env bash

source $HOME/.bashrc

THIS_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROBLEMS_ROOT_DIR="$(cd "$THIS_SCRIPT_DIR/../.." && pwd)"
USER_ROOT_DIR="$(dirname "$PROBLEMS_ROOT_DIR")"
CLEANPATH_PY="$USER_ROOT_DIR/junk-drawer/cleanpath.py"
BP_ROOT="$PROBLEMS_ROOT_DIR/biology-problems/problems"
QTI_PACKAGE_MAKER_DIR="$PROBLEMS_ROOT_DIR/qti_package_maker"

BIOLOGY_PROBLEMS_DIR="$BP_ROOT"
if [[ "$(basename "$BP_ROOT")" == "problems" ]]; then
  BIOLOGY_PROBLEMS_DIR="$(dirname "$BP_ROOT")"
fi

SETUP_SCRIPT="$QTI_PACKAGE_MAKER_DIR/source_me_for_testing.sh"
if [[ ! -f "$SETUP_SCRIPT" ]]; then
  echo "Error: missing $SETUP_SCRIPT" >&2
  return 1 2>/dev/null || exit 1
fi

if [[ ! -d "$BIOLOGY_PROBLEMS_DIR" ]]; then
  echo "Error: missing $BIOLOGY_PROBLEMS_DIR" >&2
  return 1 2>/dev/null || exit 1
fi

# shellcheck source=/dev/null
source "$SETUP_SCRIPT"

PYTHONPATH_PROPOSED="$BIOLOGY_PROBLEMS_DIR"
if [[ -n "$QTI_PACKAGE_MAKER_DIR" ]]; then
  PYTHONPATH_PROPOSED="$PYTHONPATH_PROPOSED:$QTI_PACKAGE_MAKER_DIR"
fi
if [[ -n "${PYTHONPATH-}" ]]; then
  PYTHONPATH_PROPOSED="$PYTHONPATH_PROPOSED:${PYTHONPATH-}"
fi

if [[ -x "$CLEANPATH_PY" ]]; then
  export PYTHONPATH="$("$CLEANPATH_PY" -p "$PYTHONPATH_PROPOSED")"
else
  export PYTHONPATH="$PYTHONPATH_PROPOSED"
fi

echo "PYTHONPATH is now: $PYTHONPATH"
echo "You can now run generators with: python3 path/to/script.py"
