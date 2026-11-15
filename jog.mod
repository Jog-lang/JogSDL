# Hand-written SDL3 bindings for Jog (Linux x86-64 first).
# Public apps import jog_sdl.sdl (+ sdl.* subpackages); package sdl3 stays internal.
module jog_sdl
version 0.1.0
kind library
jog 0.0.1

export sdl
export sdl.assert
export sdl.asyncio
export sdl.atomic
export sdl.audio
export sdl.bits
export sdl.blendmode
export sdl.camera
export sdl.clipboard
export sdl.cpuinfo
export sdl.dialog
export sdl.endian
export sdl.error
export sdl.events
export sdl.filesystem
export sdl.gamepad
export sdl.gpu
export sdl.guid
export sdl.haptic
export sdl.hidapi
export sdl.hints
export sdl.init
export sdl.input
export sdl.iostream
export sdl.joystick
export sdl.keyboard
export sdl.keycode
export sdl.loadso
export sdl.locale
export sdl.log
export sdl.main
export sdl.messagebox
export sdl.metal
export sdl.misc
export sdl.mouse
export sdl.mutex
export sdl.opengl
export sdl.pen
export sdl.pixels
export sdl.platform
export sdl.power
export sdl.process
export sdl.properties
export sdl.rect
export sdl.render
export sdl.scancode
export sdl.sensor
export sdl.stdinc
export sdl.storage
export sdl.surface
export sdl.system
export sdl.thread
export sdl.time
export sdl.timer
export sdl.touch
export sdl.tray
export sdl.version
export sdl.video
export sdl.vulkan
export sdl.window

link.linux SDL3
link.windows SDL3
link.macos SDL3
link.emscripten SDL3

# Portable relative search paths for a repo-local SDL3 prefix (scripts/build-sdl3.sh).
# Host-only paths can instead go in a gitignored jog.local.mod next to the app.
libdir.linux ./prefix/lib64
libdir.linux ./prefix/lib
libdir.macos ./prefix/lib
libdir.windows ./prefix/lib
# Static libSDL3.a from scripts/build-sdl3-emscripten.sh → prefix-emscripten/.
libdir.emscripten ./prefix-emscripten/lib
