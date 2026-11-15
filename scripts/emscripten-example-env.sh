# Shared helpers for examples/*/start.sh (wasm32-emscripten).
# Sourced only; not meant to be run directly.

emscripten_ensure_env() {
  export JOG="${JOG:-$HOME/.local/bin/jog-v2}"
  export JOG_BUILD="${JOG_BUILD:-$HOME/.local/bin/jog-build}"

  if ! command -v emcc >/dev/null 2>&1; then
    local emsdk_env="${EMSDK_ENV:-$HOME/emsdk/emsdk_env.sh}"
    if [[ -f "$emsdk_env" ]]; then
      # shellcheck source=/dev/null
      source "$emsdk_env"
    fi
  fi
  if ! command -v emcc >/dev/null 2>&1; then
    echo "error: emcc not on PATH; source emsdk_env.sh first" >&2
    return 1
  fi
  if [[ ! -x "$JOG" ]]; then
    echo "error: jog binary not found at JOG=$JOG (jog-v2 only)" >&2
    return 1
  fi
}

emscripten_ensure_sdl_prefix() {
  local root="$1"
  local lib="$root/prefix-emscripten/lib/libSDL3.a"
  if [[ -f "$lib" ]]; then
    return 0
  fi
  echo "prefix-emscripten missing; fetching/building SDL3 for emscripten…"
  "$root/scripts/fetch-sdl3.sh"
  "$root/scripts/build-sdl3-emscripten.sh"
}

emscripten_build_html() {
  # Args: example_dir out_html_basename (e.g. window.html)
  local example_dir="$1"
  local out_name="$2"
  mkdir -p "$example_dir/out"
  (
    cd "$example_dir"
    if [[ -x "${JOG_BUILD:-}" ]]; then
      "$JOG_BUILD" build --target wasm32-emscripten -o "out/$out_name"
    else
      "$JOG" build . --target wasm32-emscripten -o "out/$out_name"
    fi
  )
}

emscripten_serve_out() {
  # Args: example_dir html_name [port]
  local example_dir="$1"
  local html_name="$2"
  local port="${3:-8000}"
  local out_dir="$example_dir/out"
  if [[ ! -f "$out_dir/$html_name" ]]; then
    echo "error: missing $out_dir/$html_name (build first)" >&2
    return 1
  fi
  echo "Serving $out_dir on http://127.0.0.1:${port}/${html_name}"
  echo "Ctrl-C to stop."
  exec python3 -m http.server -d "$out_dir" "$port"
}
