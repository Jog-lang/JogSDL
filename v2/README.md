# JogSDL for JogCompiler v2

Native Linux x86-64 bindings and demos for **`jog-v2` / `jog-build`** (parity #19+).

Root `sdl/` + `examples/` stay on develop/`jogc`. This tree is the JOG-64 port.

## Layout

```
v2/
  sdl3.jog              # @link("SDL3") raw externs
  sdl.jog               # Window / Renderer / Texture / FRect (f32)
  examples/window/      # smoke (~1.5s auto-exit)
  examples/raycaster/   # Q16 raycaster, 128×80 FB in 640×400 window (20 frames)
```

## Prerequisites

- `jog-v2` + `jog-build` on `PATH` (or `JOG` / `JOG_BUILD`)
- SDL3 in `../prefix` via repo `scripts/build-sdl3.sh`

## Build & run (rpath — no `LD_LIBRARY_PATH`)

```bash
export JOG=~/.local/bin/jog-v2
export JOG_BUILD=~/.local/bin/jog-build

cd examples/window
"$JOG_BUILD" build -o out/window_demo && ./out/window_demo

cd ../raycaster
"$JOG_BUILD" build -o out/raycaster && ./out/raycaster
```

Verified: both exit cleanly with `RUNPATH` pointing at `prefix/lib64`.

## Limits (see project friction log)

- No Emscripten/`wasm32-emscripten` on JogCompiler v2 yet.
- Raycaster uses a short frame cap and reduced FB until heavy present loops are fixed upstream.
- Package consts are zero-arg fns; libc `malloc` for the pixel buffer (64KiB bump heap).
