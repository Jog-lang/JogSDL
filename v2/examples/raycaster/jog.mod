# Jog v2 Wolfenstein-style software raycaster (Q16 DDA; float extern ABI fixed upstream (JOG-89)).
# Browser build: see ../raycaster-emscripten (JOG-90).
module raycaster
version 0.1.0
root main.jog
source world.jog
source ../../sdl.jog
source ../../sdl3.jog
link.linux SDL3
link.emscripten SDL3
libdir.linux ../../../prefix/lib64
libdir.linux ../../../prefix/lib
libdir.emscripten ../../../prefix-emscripten/lib
