# Jog v2 window demo for --target wasm32-emscripten (JOG-90).
# Returning jog_host_run_loop(tick); scalar pointer globals only.
module window_emscripten
version 0.1.0
root main.jog
require jog_sdl ../..
link.emscripten SDL3
libdir.emscripten ../../prefix-emscripten/lib
