#!/usr/bin/env bash
#
# Bump the Brinkpy version in every file that records it.
#
# Usage:
#   scripts/bump_version.sh <new-version> [--release]
#
# Updates:
#   pyproject.toml        version = "X.Y.Z"
#   brinkpy/__init__.py   __version__ = "X.Y.Z"
#   CITATION.cff          version: X.Y.Z and date-released: <today>
#
# With --release, also commits only those three files as "Release vX.Y.Z"
# and creates an annotated tag vX.Y.Z. Nothing is pushed; the script prints
# the push command and the link for creating the GitHub release, which
# triggers the PyPI publish workflow and the Zenodo archive.

set -euo pipefail

usage() {
  echo "Usage: $0 <new-version> [--release]" >&2
  echo "Example: $0 0.1.1 --release" >&2
  exit 1
}

NEW=""
RELEASE=0
for arg in "$@"; do
  case "$arg" in
    --release) RELEASE=1 ;;
    -h|--help) usage ;;
    -*) echo "Unknown option: $arg" >&2; usage ;;
    *) [ -z "$NEW" ] && NEW="$arg" || usage ;;
  esac
done
[ -n "$NEW" ] || usage

if ! [[ "$NEW" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: version must look like X.Y.Z (got '$NEW')." >&2
  exit 1
fi

# Run from the repository root regardless of where the script is called from.
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

FILES=(pyproject.toml brinkpy/__init__.py CITATION.cff)
TAG="v$NEW"
TODAY="$(date +%F)"

CURRENT="$(sed -n 's/^version = "\([^"]*\)"$/\1/p' pyproject.toml | head -1)"
if [ -z "$CURRENT" ]; then
  echo "Error: could not read the current version from pyproject.toml." >&2
  exit 1
fi

# Require the new version to be strictly greater than the current one.
version_gt() {
  local IFS=.
  local -a a=($1) b=($2)
  for i in 0 1 2; do
    if ((10#${a[i]} > 10#${b[i]})); then return 0; fi
    if ((10#${a[i]} < 10#${b[i]})); then return 1; fi
  done
  return 1
}
if ! version_gt "$NEW" "$CURRENT"; then
  echo "Error: new version $NEW must be greater than current version $CURRENT." >&2
  exit 1
fi

if [ "$RELEASE" -eq 1 ]; then
  # The release commit must match exactly what is being released, so refuse
  # if anything besides the version files has uncommitted changes.
  OTHER_CHANGES="$(git status --porcelain --untracked-files=no -- . \
    ':!pyproject.toml' ':!brinkpy/__init__.py' ':!CITATION.cff')"
  if [ -n "$OTHER_CHANGES" ]; then
    echo "Error: --release needs a clean working tree apart from the version files." >&2
    echo "Commit or stash these first:" >&2
    echo "$OTHER_CHANGES" >&2
    exit 1
  fi
  if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
    echo "Error: tag $TAG already exists locally." >&2
    exit 1
  fi
  if git ls-remote --exit-code --tags origin "refs/tags/$TAG" >/dev/null 2>&1; then
    echo "Error: tag $TAG already exists on origin." >&2
    exit 1
  fi
fi

# Only the first top-level `version = ` line (the [project] version) changes.
perl -pi -e '$done ||= s/^version = "[^"]*"$/version = "'"$NEW"'"/' pyproject.toml
perl -pi -e 's/^__version__ = "[^"]*"/__version__ = "'"$NEW"'"/' brinkpy/__init__.py
perl -pi -e 's/^version: .*$/version: '"$NEW"'/; s/^date-released: .*$/date-released: '"$TODAY"'/' CITATION.cff

# Confirm every file now carries the new version.
grep -q "^version = \"$NEW\"$" pyproject.toml || { echo "Error: pyproject.toml not updated." >&2; exit 1; }
grep -q "^__version__ = \"$NEW\"" brinkpy/__init__.py || { echo "Error: brinkpy/__init__.py not updated." >&2; exit 1; }
grep -q "^version: $NEW$" CITATION.cff || { echo "Error: CITATION.cff not updated." >&2; exit 1; }

echo "Version bumped: $CURRENT -> $NEW"
git --no-pager diff -- "${FILES[@]}"

if [ "$RELEASE" -eq 0 ]; then
  echo
  echo "Files updated but not committed. To release, commit them and tag $TAG,"
  echo "or rerun with --release next time to do both."
  exit 0
fi

git commit -q -m "Release $TAG" -- "${FILES[@]}"
git tag -a "$TAG" -m "Release $TAG"

REPO_URL="$(git remote get-url origin | sed -e 's/\.git$//' -e 's#^git@github.com:#https://github.com/#')"

echo
echo "Committed \"Release $TAG\" and created tag $TAG (not pushed yet)."
echo
echo "Next steps:"
echo "  1. Push the commit and the tag:"
echo "       git push && git push origin $TAG"
echo "  2. Create the GitHub release from tag $TAG:"
echo "       $REPO_URL/releases/new?tag=$TAG"
echo "     Publishing the release uploads $NEW to PyPI and archives it on Zenodo."
