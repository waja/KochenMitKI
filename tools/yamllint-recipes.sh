#!/usr/bin/env bash
set -euo pipefail

for file in "$@"; do
  delims=$(awk '/^---$/ { count++; if (count == 2) exit } END { print count + 0 }' "$file")

  if [ "$delims" -ne 2 ]; then
    echo "FAIL $file: expected 2 delimiters, found $delims" >&2
    exit 1
  fi

  awk '/^---$/{c++; print; next} c==1' "$file" > /tmp/fm.yaml

  if ! yamllint -c .yamllint /tmp/fm.yaml; then
    echo "FAIL $file: invalid frontmatter" >&2
    exit 1
  fi
done