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

**Stale `JOG`:** `jog-build` (0.2.5-v2+) always prefers `$JOG` first. If your shell still exports a seed/pre-v2 `jog` (e.g. from `~/.bashrc`), bare `jog-build build …` will parse this v2 `jog.mod` with the old compiler and fail with `unknown declaration 'root'` / `'source' is reserved` / `unknown target 'emscripten'`. Fix: `export JOG=~/.local/bin/jog-v2` (or `unset JOG` when `jog-v2` is on `PATH`). Check with `echo "$JOG"` and `jog-v2 --version` (expect `0.2.11-v2`).

## Build & run (native, rpath — no `LD_LIBRARY_PATH`)

From the JogSDL repo root (Fedora / Linux x86-64). Output binary is `out/raycaster` (not `raycater`).

```bash
export JOG=~/.local/bin/jog-v2   # required if $JOG still points at seed
export JOG_BUILD=~/.local/bin/jog-build

cd v2/examples/window
"$JOG_BUILD" build -o out/window_demo && ./out/window_demo

cd ../raycaster
"$JOG_BUILD" build -o out/raycaster && ./out/raycaster
# agent/CI soft-exit after ~180 frames:
JOGSDL_RAYCASTER_SMOKE=1 ./out/raycaster
```

One-liner from `v2/examples/raycaster/`:

```bash
JOG=~/.local/bin/jog-v2 jog-build build -o out/raycaster && ./out/raycaster
```

## Build & run (Emscripten / browser)

```bash
source ~/emsdk/emsdk_env.sh
# once from repo root: ./scripts/build-sdl3-emscripten.sh

export JOG=~/.local/bin/jog-v2   # or JogCompiler-v2/zig-out/bin/jog

cd v2/examples/window-emscripten
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
- **jog 0.2.11-v2 hot-path workarounds (raycaster):** `as` between `f64`/`i64` is a bitcast (use `lround` + IEEE `i_to_f`); bare `f64*f64` / `f64+f64` on package/field loads can lower to integer `imul`/`add` (force `a * 1.0 * b`); struct returns bump-alloc with no free (keep camera/DDA as package scalars). See JogDocs Friction.
