# Full CPU-3D raycaster for --target wasm32-emscripten (JOG-90 + JOG-121).
# Shares texture/mesh/parallel/timing/world with native; tick via jog_host_run_loop.
# go bands: run-to-completion under emscripten (JogCompiler RTC); yield still unsupported.
module raycaster_emscripten
version 0.1.0
root main.jog
source ../raycaster/math2d.jog
source ../raycaster/world.jog
source ../raycaster/texture.jog
source ../raycaster/mesh.jog
source ../raycaster/parallel.jog
source ../raycaster/timing.jog
source ../../sdl.jog
source ../../sdl3.jog
link.emscripten SDL3
libdir.emscripten ../../../prefix-emscripten/lib
