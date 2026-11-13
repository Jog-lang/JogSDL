# JogSDL for JogCompiler v2

Native Linux x86-64 bindings and demos for **`jog-v2` / `jog-build`** (JOG-89 surfaces on `jog 0.2.6-v2`+).

Root `sdl/` + `examples/` stay on develop/`jogc`. This tree is the v2 port (JOG-64 + JOG-89).

## Layout

```
v2/
  sdl3.jog              # @link("SDL3") raw externs
  sdl.jog               # Window / Renderer / Texture / FRect (f32); package vals
  examples/window/      # smoke (~1.5s auto-exit)
  examples/raycaster/   # Q16 raycaster, 160×100 FB in 640×400 window (120 frames)
```

## Prerequisites

- `jog-v2` + `jog-build` on `PATH` (or `JOG` / `JOG_BUILD`) — needs **0.2.6-v2** (JOG-89)
- SDL3 in `../prefix` via repo `scripts/build-sdl3.sh`

## Build & run (rpath — no `LD_LIBRARY_PATH`)

```bash
export JOG=~/.local/bin/jog-v2   # or JogCompiler-v2/zig-out/bin/jog
export JOG_BUILD=~/.local/bin/jog-build

cd examples/window
"$JOG_BUILD" build -o out/window_demo && ./out/window_demo

cd ../raycaster
"$JOG_BUILD" build -o out/raycaster && ./out/raycaster
```

## JOG-89 surfaces now used

- Package-level `val` constants (no zero-arg const fns)
- `jogrt_alloc` 4 MiB heap for the framebuffer (no libc `malloc`)
- Float extern ABI fixed upstream (libm); raycaster keeps Q16 DDA by choice
- `jog_host_run_loop` available upstream; window smoke still uses a platform `while` (SDL+tick still flaky)

## Limits

- No Emscripten/`wasm32-emscripten` on JogCompiler v2 yet (JOG-90).
- Struct package globals and `host_run_loop` + SDL present still need care; see project friction log.
