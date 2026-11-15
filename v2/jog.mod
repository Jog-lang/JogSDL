# JogSDL library for JogCompiler v2 (flat source merge via require).
# Examples: require jog_sdl ../..
# Directory layout mirrors root sdl/ + sdl3/; v2 keeps *byte FFI and v2-only helpers.
module jog_sdl
version 0.1.0

# Facade first, then raw categories, then idiomatic helpers.
root sdl/sdl.jog

source sdl3/init/init.jog
source sdl3/error/error.jog
source sdl3/rect/rect.jog
source sdl3/video/video.jog
source sdl3/render/render.jog
source sdl3/events/events.jog
source sdl3/keyboard/keyboard.jog
source sdl3/mouse/mouse.jog
source sdl3/timer/timer.jog

source sdl/window/window.jog
source sdl/render/render.jog
source sdl/events/events.jog
source sdl/input/input.jog
source sdl/timer/timer.jog

link.linux SDL3
link.emscripten SDL3
libdir.linux ../prefix/lib64
libdir.linux ../prefix/lib
libdir.emscripten ../prefix-emscripten/lib
