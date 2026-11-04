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
