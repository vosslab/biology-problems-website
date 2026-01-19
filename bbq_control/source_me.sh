#!/usr/bin/env bash

THIS_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REPO_TOPLEVEL_DIR="$(git -C "$THIS_SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: $THIS_SCRIPT_DIR is not inside a Git repository." >&2
  return 1 2>/dev/null || exit 1
}

REPO_PARENT_DIR="$(dirname "$REPO_TOPLEVEL_DIR")"
CLEANPATH_PY="$REPO_PARENT_DIR/junk-drawer/cleanpath.py"
SETTINGS_YAML="$REPO_TOPLEVEL_DIR/bbq_control/bbq_settings.yml"
PYTHON_BIN="/opt/homebrew/opt/python@3.12/bin/python3.12"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

read_setting_path() {
  local yaml_path="$1"
  local key_path="$2"
  if [[ ! -f "$yaml_path" ]]; then
    echo ""
    return
  fi
  "$PYTHON_BIN" -c "import sys,functools,yaml; data=yaml.safe_load(open(sys.argv[1])) or {}; cur=functools.reduce(lambda val, part: val.get(part, {}) if isinstance(val, dict) else {}, sys.argv[2].split('.'), data); print(cur if isinstance(cur, str) else '')" "$yaml_path" "$key_path" 2>/dev/null
}

expand_path() {
  local path_value="$1"
  if [[ -z "$path_value" ]]; then
    echo ""
    return
  fi
  if [[ "$path_value" == "~"* ]]; then
    path_value="${path_value/#\~/$HOME}"
  fi
  echo "$path_value"
}

BP_ROOT="$(read_setting_path "$SETTINGS_YAML" "paths.bp_root")"
QTI_PACKAGE_MAKER_DIR="$(read_setting_path "$SETTINGS_YAML" "paths.qti_package_maker")"

if [[ -z "$BP_ROOT" ]]; then
  BP_ROOT="$REPO_PARENT_DIR/biology-problems/problems"
fi
BP_ROOT="$(expand_path "$BP_ROOT")"

if [[ -z "$QTI_PACKAGE_MAKER_DIR" ]]; then
  QTI_PACKAGE_MAKER_DIR="$REPO_PARENT_DIR/qti_package_maker"
fi
QTI_PACKAGE_MAKER_DIR="$(expand_path "$QTI_PACKAGE_MAKER_DIR")"

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
