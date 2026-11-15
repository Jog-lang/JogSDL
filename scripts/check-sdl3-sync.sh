#!/usr/bin/env bash
# Compare raw SDL_* extern symbol sets between root sdl3/ and v2/sdl3/.
# Fails when either tree is missing a symbol the other declares.
# Wrapper-only names (no extern) are ignored by construction.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROOT_SDL3="$ROOT/sdl3"
V2_SDL3="$ROOT/v2/sdl3"

extract_symbols() {
  local dir="$1"
  # Match `fn SDL_Foo` inside extern blocks (and bare lines).
  rg -N --no-filename -o 'fn (SDL_[A-Za-z0-9_]+)\s*\(' "$dir" -g '*.jog' \
    | sed -E 's/^fn (SDL_[A-Za-z0-9_]+) \($/\1/' \
    | sed -E 's/^fn (SDL_[A-Za-z0-9_]+)\($/\1/' \
    | sort -u
}

if [[ ! -d "$ROOT_SDL3" || ! -d "$V2_SDL3" ]]; then
  echo "check-sdl3-sync: missing sdl3 trees under $ROOT" >&2
  exit 2
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

extract_symbols "$ROOT_SDL3" >"$tmp/root.txt"
extract_symbols "$V2_SDL3" >"$tmp/v2.txt"

only_root="$(comm -23 "$tmp/root.txt" "$tmp/v2.txt" || true)"
only_v2="$(comm -13 "$tmp/root.txt" "$tmp/v2.txt" || true)"

echo "check-sdl3-sync: root=$(wc -l <"$tmp/root.txt") symbols, v2=$(wc -l <"$tmp/v2.txt") symbols"

status=0
if [[ -n "$only_root" ]]; then
  echo "Symbols only in root sdl3/:" >&2
  echo "$only_root" >&2
  status=1
fi
if [[ -n "$only_v2" ]]; then
  echo "Symbols only in v2/sdl3/:" >&2
  echo "$only_v2" >&2
  status=1
fi

if [[ "$status" -eq 0 ]]; then
  echo "check-sdl3-sync: OK (identical SDL_* extern sets)"
fi
exit "$status"
