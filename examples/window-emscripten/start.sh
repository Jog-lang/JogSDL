#!/usr/bin/env bash
# Build (if needed) and serve the Emscripten window smoke in a browser.
# Usage: ./start.sh [--rebuild] [--serve-only] [--port N]
set -euo pipefail

EXAMPLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$EXAMPLE_DIR/../.." && pwd)"
# shellcheck source=../../scripts/emscripten-example-env.sh
source "$ROOT/scripts/emscripten-example-env.sh"

HTML=window.html
PORT="${PORT:-8000}"
REBUILD=0
SERVE_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --rebuild) REBUILD=1; shift ;;
    --serve-only) SERVE_ONLY=1; shift ;;
    --port) PORT="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--rebuild] [--serve-only] [--port N]"
      exit 0
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "$SERVE_ONLY" -eq 0 ]]; then
  emscripten_ensure_env
  emscripten_ensure_sdl_prefix "$ROOT"
  if [[ "$REBUILD" -eq 1 || ! -f "$EXAMPLE_DIR/out/$HTML" ]]; then
    emscripten_build_html "$EXAMPLE_DIR" "$HTML"
  else
    echo "Using existing out/$HTML (pass --rebuild to force)"
  fi
fi

emscripten_serve_out "$EXAMPLE_DIR" "$HTML" "$PORT"
