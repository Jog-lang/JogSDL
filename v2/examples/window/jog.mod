# Jog v2 window smoke — idiomatic sdl over sdl3, jog-v2 + libdir/rpath.
module window_demo
version 0.1.0
root main.jog
source ../../sdl.jog
source ../../sdl3.jog
link.linux SDL3
libdir.linux ../../../prefix/lib64
libdir.linux ../../../prefix/lib
