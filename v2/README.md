# JogSDL for JogCompiler v2

Native Linux x86-64 and **wasm32-emscripten** bindings/demos for **`jog-v2` / `jog-build`** (`jog 0.2.11-v2`+; JOG-89 + JOG-90 + JOG-95/96 surfaces).

Root `sdl/` + `examples/` stay on develop/`jogc`. This tree is the v2 port (JOG-64 + JOG-89 + JOG-90 + JOG-105 proto-3D).

## Layout

```
v2/
  sdl3.jog                      # @link("SDL3") raw externs (+ relative mouse)
  sdl.jog                       # Window / Renderer / Texture / FRect / mouse / keys
  examples/window/              # native smoke (~1.5s auto-exit, while-loop)
  examples/raycaster/           # proto-3D: float Vec2 + view basis, doors, mouse look
  examples/window-emscripten/   # browser window via jog_host_run_loop (JOG-90)
  examples/raycaster-emscripten/# browser proto-3D raycaster (object App state)
```

## Prerequisites

- `jog-v2` + `jog-build` on `PATH` (or `JOG` / `JOG_BUILD`) — needs **0.2.11-v2** (`std` + `object` + emscripten)
- Native SDL3 in `../prefix` via repo `scripts/build-sdl3.sh` (creates `prefix/lib` → `lib64` symlink on Fedora)
- Browser: emsdk (`source ~/emsdk/emsdk_env.sh`) + `scripts/build-sdl3-emscripten.sh` → `../prefix-emscripten/`

## Build & run (native, rpath — no `LD_LIBRARY_PATH`)

```bash
export JOG=~/.local/bin/jog-v2   # or JogCompiler-v2/zig-out/bin/jog
export JOG_BUILD=~/.local/bin/jog-build

cd examples/window
"$JOG_BUILD" build -o out/window_demo && ./out/window_demo

cd ../raycaster
"$JOG_BUILD" build -o out/raycaster && ./out/raycaster
# agent/CI soft-exit after ~180 frames:
JOGSDL_RAYCASTER_SMOKE=1 ./out/raycaster
```

## Build & run (Emscripten / browser)

```bash
source ~/emsdk/emsdk_env.sh
# once: ../scripts/build-sdl3-emscripten.sh

export JOG=/path/to/JogCompiler-v2/zig-out/bin/jog

cd examples/window-emscripten
"$JOG" build . --target wasm32-emscripten -o out/window.html
python3 -m http.server -d out 8000
# open http://127.0.0.1:8000/window.html

cd ../raycaster-emscripten
"$JOG" build . --target wasm32-emscripten -o out/raycaster.html
python3 -m http.server -d out 8000
# open http://127.0.0.1:8000/raycaster.html
```

`jog-build build --target wasm32-emscripten` also works once `JOG` points at a JOG-90 compiler (JogBuild already forwards the target).

## JOG-89 / JOG-90 / JOG-105 surfaces

- Package-level `val` constants; `jogrt_alloc` 4 MiB heap; float extern ABI (native)
- Raycaster uses `import std.math` (sin/cos/floor) and float `Vec2` + `ViewBasis` (dir|plane columns)
- Interactive door cells (E/Space); relative mouse look; WASD + arrow turn
- Emscripten: IR→C→emcc; `link.emscripten` / `libdir.emscripten`; returning `jog_host_run_loop(tick)`
- Wasm raycaster keeps state in an `object App` singleton (JOG-96 path around F17)
- Native SDL demos keep platform `while` (F16: host_run_loop + SDL present still flaky on native)

## Controls (raycaster)

- **W/A/S/D** — move / strafe along view basis
- **Left/Right** or **mouse X** (relative mode) — yaw (rotates both basis columns)
- **E** or **Space** — toggle door cell ahead
- **Escape** / window close — quit
- Native default stays open for play; set `JOGSDL_RAYCASTER_SMOKE=1` for the ~180-frame agent/CI soft exit

## Limits

- Freestanding `wasm32` (no emcc) is not on v2; browser+SDL is `wasm32-emscripten` only.
- FRect layout vs `SDL_FRect` packing is still coarse (8-byte field slots); demos still smoke-present (F18).
- Coroutines/`go` abort under emscripten (no stack switch).
- Still a 2.5D column caster — not a full 3D transform pipeline / textured world.
