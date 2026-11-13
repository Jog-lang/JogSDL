# Jog v2 window smoke — native + wasm32-emscripten (JOG-90).
module window_demo
version 0.1.0
root main.jog
source ../../sdl.jog
source ../../sdl3.jog
link.linux SDL3
link.emscripten SDL3
libdir.linux ../../../prefix/lib64
libdir.linux ../../../prefix/lib
libdir.emscripten ../../../prefix-emscripten/lib
