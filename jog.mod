# JogSDL — kind library with directory source trees (shareable .jogz).
module jog_sdl
version 0.1.0
kind library

source sdl
source sdl3

# KEEP / public idiomatic surface. `export sdl` also covers sdl.<sub> for outsiders.
export sdl
export sdl.window
export sdl.render
export sdl.events
export sdl.input
export sdl.timer
export sdl.init

link.linux SDL3
link.emscripten SDL3
libdir.linux ./prefix/lib64
libdir.linux ./prefix/lib
libdir.emscripten ./prefix-emscripten/lib
