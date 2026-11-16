#!/usr/bin/env bash
#
# Copy data_models.py from the API repository into the CLI, so both always
# use the same models. The API copy is the source of truth: edit it there,
# then run this script. Never edit the CLI copy by hand.
#
# Usage:
#   scripts/sync_data_models.sh           copy the API file into the CLI
#   scripts/sync_data_models.sh --check   only report whether they match
#                                         (exit 1 if they differ)
#
# The API repository is expected next to this one (../brinkpy-api). Set
# BRINKPY_API_DIR to use another location.
#
# The CLI copy starts with one extra header line saying that it is
# generated. Everything after that line must match the API file exactly.

set -euo pipefail

CHECK=0
case "${1:-}" in
  "") ;;
  --check) CHECK=1 ;;
  -h|--help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *) echo "Unknown option: $1" >&2; exit 2 ;;
esac

# Run from the repository root regardless of where the script is called from.
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

API_DIR="${BRINKPY_API_DIR:-../brinkpy-api}"
SRC="$API_DIR/src/config/data_models.py"
DST="brinkpy/config/data_models.py"
HEADER="# Generated from brinkpy-api/src/config/data_models.py by scripts/sync_data_models.sh. Do not edit by hand."

if [ ! -f "$SRC" ]; then
  echo "Error: $SRC not found. Set BRINKPY_API_DIR to the brinkpy-api folder." >&2
  exit 2
fi

in_sync() {
  [ -f "$DST" ] && [ "$(head -n 1 "$DST")" = "$HEADER" ] && tail -n +2 "$DST" | cmp -s - "$SRC"
}

if [ "$CHECK" -eq 1 ]; then
  if in_sync; then
    echo "data_models.py matches the API copy."
    exit 0
  fi
  echo "data_models.py differs from the API copy ($SRC)." >&2
  echo "Edit the API copy, then run scripts/sync_data_models.sh." >&2
  exit 1
fi

if in_sync; then
  echo "data_models.py already matches the API copy. Nothing to do."
  exit 0
fi

{ echo "$HEADER"; cat "$SRC"; } > "$DST.tmp"
mv "$DST.tmp" "$DST"
echo "Copied $SRC to $DST."
git --no-pager diff --stat -- "$DST"
