# Smoke: CreateGPUDevice → ClaimWindow → swapchain clear → submit.
module gpu_clear_smoke
version 0.1.0
root main.jog
require jog_sdl ../..
link.linux SDL3
libdir.linux ../../prefix/lib64
libdir.linux ../../prefix/lib
