#!/usr/bin/env bash
# Verify idiomatic sdl.* packages are non-empty when sdl3.* has SDL_* externs.
# Hand-written demo packages may be thin; generated categories must wrap ≥1 symbol
# or be an intentional const/note package (bits/endian/pen/keycode/scancode/stdinc).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEEP='window|render|events|input|timer|opengl'
CONST='bits|endian|pen|keycode|scancode|stdinc'
fail=0
for raw in "$ROOT"/sdl3/*/*.jog; do
  cat="$(basename "$(dirname "$raw")")"
  [[ "$cat" =~ ^($KEEP)$ ]] && continue
  n_ext="$(grep -cE '^\s*fn SDL_' "$raw" || true)"
  [[ "$n_ext" -eq 0 ]] && continue
  wrap="$ROOT/sdl/$cat/$cat.jog"
  if [[ ! -f "$wrap" ]]; then
    echo "check-idiomatic-sdl: missing $wrap (raw has $n_ext SDL_*)" >&2
    fail=1
    continue
  fi
  n_fn="$(grep -cE '^(fn |val )' "$wrap" || true)"
  if [[ "$n_fn" -eq 0 && ! "$cat" =~ ^($CONST)$ ]]; then
    echo "check-idiomatic-sdl: empty stub $wrap (raw has $n_ext SDL_*)" >&2
    fail=1
  fi
done
# v2: same idea for generated cats (hand-written KEEP dirs excluded)
for raw in "$ROOT"/v2/sdl3/*/*.jog; do
  cat="$(basename "$(dirname "$raw")")"
  [[ "$cat" =~ ^($KEEP)$ ]] && continue
  n_ext="$(grep -cE '^\s*fn SDL_' "$raw" || true)"
  [[ "$n_ext" -eq 0 ]] && continue
  wrap="$ROOT/v2/sdl/$cat/$cat.jog"
  if [[ ! -f "$wrap" ]]; then
    echo "check-idiomatic-sdl: missing v2 $wrap" >&2
    fail=1
    continue
  fi
  n_fn="$(grep -cE '^(fn |val )' "$wrap" || true)"
  if [[ "$n_fn" -eq 0 && ! "$cat" =~ ^($CONST)$ ]]; then
    echo "check-idiomatic-sdl: empty v2 stub $wrap" >&2
    fail=1
  fi
done
if [[ "$fail" -ne 0 ]]; then
  echo "check-idiomatic-sdl: FAIL" >&2
  exit 1
fi
echo "check-idiomatic-sdl: OK"
