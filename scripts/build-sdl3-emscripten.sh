#!/usr/bin/env bash
# Configure, build, and install a static SDL3 for Emscripten into prefix-emscripten/.
# Requires emsdk activated (emcmake / emcc on PATH).
set -euo pipefail

SDL3_VERSION="${SDL3_VERSION:-3.4.18}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/vendor/SDL3-${SDL3_VERSION}"
BUILD="$SRC/build-emscripten"
PREFIX="$ROOT/prefix-emscripten"

if ! command -v emcmake >/dev/null 2>&1; then
  echo "emcmake not found — source emsdk_env.sh first" >&2
  exit 1
fi

if [[ ! -f "$SRC/CMakeLists.txt" ]]; then
  echo "Missing $SRC — run scripts/fetch-sdl3.sh first" >&2
  exit 1
fi

mkdir -p "$BUILD" "$PREFIX"

emcmake cmake -S "$SRC" -B "$BUILD" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DSDL_SHARED=OFF \
  -DSDL_STATIC=ON \
  -DSDL_TEST_LIBRARY=OFF

cmake --build "$BUILD"
cmake --install "$BUILD"

echo "Installed SDL3 ${SDL3_VERSION} (Emscripten static) to $PREFIX"
ls -la "$PREFIX/lib"/libSDL3.a 2>/dev/null || ls -la "$PREFIX/lib64"/libSDL3.a 2>/dev/null || true
