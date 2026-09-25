#!/usr/bin/env bash
# Builds the folder that actually gets published: a copy of site/ WITHOUT
# internal files (the paid guide, preview screenshots, hosting notes, this script).
# Usage: bash site/make-public-copy.sh   ->  creates ./site-public next to site/
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT="$(dirname "$SRC")/site-public"
rm -rf "$OUT"
mkdir -p "$OUT"
( cd "$SRC" && find . -type f \
    ! -path './_preview/*' \
    ! -path './products/_deliverables/*' \
    ! -name 'HOSTING.md' \
    ! -name 'make-public-copy.sh' \
    -print0 | while IFS= read -r -d '' f; do
        mkdir -p "$OUT/$(dirname "$f")"; cp "$f" "$OUT/$f"; done )
echo "Public copy ready: $OUT"
find "$OUT" -type f | sed "s|$OUT/||" | sort
if find "$OUT" -name '*.pdf' -o -name '*setup-guide*' | grep -q .; then
  echo "ERROR: paid guide found in public copy" >&2; exit 1
fi
# Anything that isn't a web file (notes, scripts, screenshots, dotfiles) is internal.
if find "$OUT" -type f \( -name '*.md' -o -name '*.sh' -o -name '*.png' -o -name '.*' \) | grep -q .; then
  echo "ERROR: internal file found in public copy:" >&2
  find "$OUT" -type f \( -name '*.md' -o -name '*.sh' -o -name '*.png' -o -name '.*' \) >&2; exit 1
fi
