# Proto-3D raycaster for --target wasm32-emscripten (JOG-90 + JOG-105).
module raycaster_emscripten
version 0.1.0
root main.jog
source ../raycaster/math2d.jog
source ../raycaster/world.jog
source ../../sdl.jog
source ../../sdl3.jog
link.emscripten SDL3
libdir.emscripten ../../../prefix-emscripten/lib
