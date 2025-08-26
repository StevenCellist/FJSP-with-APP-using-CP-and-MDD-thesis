#!/usr/bin/env bash
set -euo pipefail

# Script: run_all.sh
# Usage: ./run_all.sh [TARGET_DIR]
# For each regular file in TARGET_DIR (non-recursively),
# invokes: cargo run -- <filepath>, skipping any that end with 'b.txt'

TARGET_DIR="${1:-.}"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: '$TARGET_DIR' is not a directory" >&2
  exit 1
fi

echo "-> Running in directory: $TARGET_DIR"

for filepath in "$TARGET_DIR"/*; do
  # only regular files
  [[ -f "$filepath" ]] || continue

  # SKIP any file ending in 'b.txt'
  # if [[ "$filepath" == *b.txt ]]; then
  #   echo "Skipping $filepath"
  #   continue
  # fi

  echo "----------------------------------------"
  echo "Running cargo with argument: $filepath"
  cargo run --release "$filepath" 1 60
done

echo "-> All done."
