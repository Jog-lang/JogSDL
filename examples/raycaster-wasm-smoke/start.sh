#!/usr/bin/env bash
# Build (if needed) and run the headless Wasm CPU-3D smoke under node.
# Usage: ./start.sh [--rebuild] [--build-only]
# No SDL / no HTTP server — proves pitch/mesh/occlusion + RTC go bands.
set -euo pipefail

EXAMPLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$EXAMPLE_DIR/../.." && pwd)"
# shellcheck source=../../scripts/emscripten-example-env.sh
source "$ROOT/scripts/emscripten-example-env.sh"

HTML=smoke.html
JS=smoke.js
REBUILD=0
BUILD_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --rebuild) REBUILD=1; shift ;;
    --build-only) BUILD_ONLY=1; shift ;;
    -h|--help)
      echo "Usage: $0 [--rebuild] [--build-only]"
      exit 0
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

emscripten_ensure_env

if [[ "$REBUILD" -eq 1 || ! -f "$EXAMPLE_DIR/out/$JS" ]]; then
  # Headless: no libSDL3 / prefix-emscripten required.
  emscripten_build_html "$EXAMPLE_DIR" "$HTML"
else
  echo "Using existing out/$JS (pass --rebuild to force)"
fi

if [[ "$BUILD_ONLY" -eq 1 ]]; then
  echo "Built $EXAMPLE_DIR/out/$HTML"
  exit 0
fi

if ! command -v node >/dev/null 2>&1; then
  echo "error: node required to run out/$JS" >&2
  exit 1
fi

exec node "$EXAMPLE_DIR/out/$JS"
