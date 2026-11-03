#!/usr/bin/env bash
# Configure, build, and install SDL3 into the repo-local prefix/.
set -euo pipefail

SDL3_VERSION="${SDL3_VERSION:-3.4.18}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/vendor/SDL3-${SDL3_VERSION}"
BUILD="$SRC/build"
PREFIX="$ROOT/prefix"

if [[ ! -f "$SRC/CMakeLists.txt" ]]; then
  echo "Missing $SRC — run scripts/fetch-sdl3.sh first" >&2
  exit 1
fi

mkdir -p "$BUILD" "$PREFIX"

# Optional local unpack of Fedora -devel RPMs (when sudo install is unavailable).
DEPS="$ROOT/.deps"
if [[ -d "$DEPS/usr" ]]; then
  export PKG_CONFIG_PATH="$DEPS/usr/lib64/pkgconfig:$DEPS/usr/share/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
  export CMAKE_PREFIX_PATH="$DEPS/usr${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
  export CPATH="$DEPS/usr/include${CPATH:+:$CPATH}"
  export LIBRARY_PATH="$DEPS/usr/lib64${LIBRARY_PATH:+:$LIBRARY_PATH}"
fi

cmake -S "$SRC" -B "$BUILD" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DSDL_SHARED=ON \
  -DSDL_STATIC=OFF \
  -DSDL_TEST_LIBRARY=OFF \
  -DSDL_KMSDRM=OFF

cmake --build "$BUILD"
cmake --install "$BUILD"

echo "Installed SDL3 ${SDL3_VERSION} to $PREFIX"
ls -la "$PREFIX/lib"/libSDL3.so* 2>/dev/null || ls -la "$PREFIX/lib64"/libSDL3.so* 2>/dev/null || true
