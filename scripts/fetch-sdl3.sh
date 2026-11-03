#!/usr/bin/env bash
# Download and extract SDL3 into vendor/SDL3-${SDL3_VERSION}/.
set -euo pipefail

SDL3_VERSION="${SDL3_VERSION:-3.4.18}"
# Official release tarball (https://www.libsdl.org/release/)
SDL3_URL="https://www.libsdl.org/release/SDL3-${SDL3_VERSION}.tar.gz"
# sha256 of SDL3-3.4.18.tar.gz (verified 2026-11-03)
SDL3_SHA256="${SDL3_SHA256:-9c75cf16330322c217dedd2e0609f1124f1b54b8633e763467b4684d0f4334a3}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENDOR="$ROOT/vendor"
TARBALL="$VENDOR/SDL3-${SDL3_VERSION}.tar.gz"
SRC="$VENDOR/SDL3-${SDL3_VERSION}"

mkdir -p "$VENDOR"

if [[ -d "$SRC" && -f "$SRC/CMakeLists.txt" ]]; then
  echo "SDL3 ${SDL3_VERSION} already present at $SRC"
  exit 0
fi

if [[ ! -f "$TARBALL" ]]; then
  echo "Downloading $SDL3_URL"
  curl -fL --retry 3 -o "$TARBALL" "$SDL3_URL"
fi

echo "$SDL3_SHA256  $TARBALL" | sha256sum -c -
rm -rf "$SRC"
tar -xzf "$TARBALL" -C "$VENDOR"
echo "Extracted to $SRC"
