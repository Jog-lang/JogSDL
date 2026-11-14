# Proves keyboard byte-index + event u32 mask + f32→f64 mouse bits (no live typing).
module input_selftest
version 0.1.0
root main.jog
source ../../sdl.jog
source ../../sdl3.jog
link.linux SDL3
libdir.linux ../../../prefix/lib64
libdir.linux ../../../prefix/lib
