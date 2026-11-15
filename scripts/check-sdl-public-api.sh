#!/usr/bin/env bash
# Grep gate: public sdl/ signatures must not leak SDL_*, *void, c.char, c.int.
# Allows those inside sdl3/ and in private helpers / comments.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
# Match exported-looking fn lines (start of line fn Name)
while IFS= read -r line; do
  file="${line%%:*}"
  rest="${line#*:}"
  # skip comments
  [[ "$rest" =~ ^[[:space:]]*// ]] && continue
  # skip private fns
  [[ "$rest" =~ private[[:space:]]+fn ]] && continue
  if echo "$rest" | rg -q 'SDL_|c\.char|c\.int|c\.size_t|\*void'; then
    # allow if it's a call body line inside function — we only want signatures
    if echo "$rest" | rg -q '^fn |^export fn '; then
      echo "check-sdl-public-api: $line" >&2
      fail=1
    fi
  fi
done < <(rg -n '^fn |^export fn ' "$ROOT/sdl" -g '*.jog' || true)

if [[ "$fail" -ne 0 ]]; then
  echo "check-sdl-public-api: FAIL" >&2
  exit 1
fi
echo "check-sdl-public-api: OK"
