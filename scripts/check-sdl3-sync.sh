#!/usr/bin/env bash
# Count raw SDL_* externs in sdl3/ (single-tree after v2→root promotion).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ ! -d "$ROOT/sdl3" ]]; then
  echo "check-sdl3-sync: missing sdl3/" >&2
  exit 2
fi
n="$(rg -N --no-filename -o 'fn (SDL_[A-Za-z0-9_]+)\s*\(' "$ROOT/sdl3" -g '*.jog' | sed -E 's/^fn (SDL_[A-Za-z0-9_]+) \($/\1/;s/^fn (SDL_[A-Za-z0-9_]+)\($/\1/' | sort -u | wc -l)"
echo "check-sdl3-sync: sdl3 has ${n} SDL_* externs"
if [[ "$n" -lt 1000 ]]; then
  echo "check-sdl3-sync: expected ≥1000 symbols" >&2
  exit 1
fi
echo "check-sdl3-sync: OK"
