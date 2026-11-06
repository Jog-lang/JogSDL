# Hand-written SDL3 bindings for Jog (Linux x86-64 first).
# Public apps import jog_sdl.sdl only; package sdl3 stays internal.
module jog_sdl
version 0.1.0
kind library
jog 0.0.1

export sdl

link.linux SDL3
link.windows SDL3
link.macos SDL3

# Portable relative search paths for a repo-local SDL3 prefix (scripts/build-sdl3.sh).
# Host-only paths can instead go in a gitignored jog.local.mod next to the app.
libdir.linux ./prefix/lib64
libdir.linux ./prefix/lib
libdir.macos ./prefix/lib
libdir.windows ./prefix/lib
