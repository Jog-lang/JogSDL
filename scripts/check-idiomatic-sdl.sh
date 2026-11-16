#!/usr/bin/env bash
# Non-empty sdl/* when sdl3 has SDL_* (KEEP/const cats exempt from emptiness).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEEP='window|render|events|input|timer|opengl|surface'
CONST='bits|endian|pen|keycode|scancode|stdinc'
fail=0
for raw in "$ROOT"/sdl3/*/*.jog; do
  cat="$(basename "$(dirname "$raw")")"
  [[ "$cat" =~ ^($KEEP)$ ]] && continue
  n_ext="$(grep -cE '^\s*fn SDL_' "$raw" || true)"
  [[ "$n_ext" -eq 0 ]] && continue
  wrap="$ROOT/sdl/$cat/$cat.jog"
  if [[ ! -f "$wrap" ]]; then
    echo "check-idiomatic-sdl: missing $wrap" >&2
    fail=1
    continue
  fi
  n_fn="$(grep -cE '^(fn |val |enum |struct )' "$wrap" || true)"
  if [[ "$n_fn" -eq 0 && ! "$cat" =~ ^($CONST)$ ]]; then
    echo "check-idiomatic-sdl: empty stub $wrap" >&2
    fail=1
  fi
done
if [[ "$fail" -ne 0 ]]; then
  echo "check-idiomatic-sdl: FAIL" >&2
  exit 1
fi
echo "check-idiomatic-sdl: OK"
