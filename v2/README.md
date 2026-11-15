# JogSDL for JogCompiler v2

Native Linux x86-64 and **wasm32-emscripten** bindings/demos for **`jog-v2` / `jog-build`** (`jog 0.2.11-v2`+; JOG-89 + JOG-90 + JOG-95/96 surfaces).

Root `sdl/` + `examples/` stay on develop/`jogc`. This tree is the v2 port (JOG-64 + JOG-89 + JOG-90 + JOG-105 proto-3D).

## Layout

```
v2/
  sdl3.jog                      # @link("SDL3") raw externs (+ relative mouse)
  sdl.jog                       # Window / Renderer / Texture / FRect / mouse / keys
  examples/window/              # native smoke (~1.5s auto-exit, while-loop)
  examples/raycaster/           # proto-3D: pitch, textures, cube, parallel bands
  examples/raycaster/timing.jog # GetTicks dt + Delay-to-cap ~60 FPS (JogSDL #19)
  examples/raycaster/texture.jog# CPU PPM/ARGB atlas load + sample(u,v) (JogSDL #20)
  examples/raycaster/mesh.jog   # soft-raster textured cube; depth-test vs walls (JogSDL #22)
  examples/raycaster/parallel.jog # go/Dispatcher column bands (native; JogSDL #23)
  examples/texture_selftest/    # no-window smoke for texture.jog
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
# agent/CI soft-exit after ~180 frames (PARALLEL bands by default after #23):
JOGSDL_RAYCASTER_SMOKE=1 ./out/raycaster
# force single-thread wall pass:
JOGSDL_RAYCASTER_SERIAL=1 JOGSDL_RAYCASTER_SMOKE=1 ./out/raycaster
```

One-liner from `v2/examples/raycaster/`:

```bash
JOG=~/.local/bin/jog-v2 jog-build build -o out/raycaster && ./out/raycaster
```

Native parallel bands need a JogCompiler with [JogCompiler #33](https://github.com/Jog-lang/JogCompiler/pull/33) (package `*byte` index meta + coro TLS on **GS**, not FS, so glibc/SDL malloc survives `dispatcher_pool`).

CPU texture substrate (no SDL window; after JogSDL #20):

```bash
cd v2/examples/texture_selftest
JOG=~/.local/bin/jog-v2 jog-build build -o out/texture_selftest && ./out/texture_selftest
# writes /tmp/jogsdl_texture_selftest.ppm
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
- **Mouse Y** (relative mode) — pitch: shifts the horizon / wall strips (classic raycaster look-up/down, not 6DOF); clamped (JogSDL #18)
- **E** or **Space** — toggle door cell ahead
- **Escape** / window close — quit
- Native default stays open for play; set `JOGSDL_RAYCASTER_SMOKE=1` for the ~180-frame agent/CI soft exit
- `JOGSDL_RAYCASTER_SERIAL=1` — force single-thread wall columns (no `go` pool); default after #23 is PARALLEL

## Frame timing / FPS (JogSDL #19)

- Native loop uses `SDL_GetTicks` for real `dt` (first frame forced to `0.016`; hitch clamp `(0, 0.05]`).
- Target ~60 FPS at demo resolution (160×100): `Delay` only when the CPU frame finishes under a 16 ms budget.
- Every 60 frames, stderr logs `timing fps=… dt_ms=… cpu_ms=…` (Fedora smoke: ~`fps=62 dt_ms=16` on both SERIAL and PARALLEL; `cpu_ms` often `0` at ms tick resolution).
- Acceptance: stable ~60 FPS on Fedora at 160×100 under mesh+walls with parallel bands (#23).

## Soft-raster cube + depth (JogSDL #22)

- Per-column DDA depth buffer (second pass after walls — avoids Jog package-ptr store issues when interleaved with FB pokes).
- `mesh.jog`: moving textured cube — yaw/pitch view projection, perspective-correct UV via `texture.jog`, depth-test against wall columns.
- Animates on real `dt` from timing helpers (orbit + spin); scalar package temps only (no struct returns on the hot path).
- Smoke (`JOGSDL_RAYCASTER_SMOKE=1`): `mesh cube multi-color ok` + `mesh cube occluded ok`; PPM `/tmp/jogsdl_raycaster_fb.ppm` shows checker red/blue; center-column occlusion behind the door.

## Parallel column bands (JogSDL #23)

- Native only: `parallel.jog` partitions wall columns across four `go` workers on a V2 `Dispatcher` pool (`dispatcher_pool(4)` before SDL Init).
- Disjoint ranges `[0,40)`, `[40,80)`, `[80,120)`, `[120,160)`; join via `coro_drain` before mesh/present. Mesh stays on the main thread after join.
- **PARALLEL** (default): smoke prints `parallel bands via go/Dispatcher (4 workers)`.
- **SERIAL**: `JOGSDL_RAYCASTER_SERIAL=1` → one-thread `render_columns_range` (no pool).
- **Wasm / emscripten:** stays serial — `raycaster-emscripten` does not use `parallel.jog` / `go` (`go` aborts under emcc).
- Requires [JogCompiler #33](https://github.com/Jog-lang/JogCompiler/pull/33): package `var x: *byte` stride-1 indexing + coro TLS on **GS** (FS clobbered glibc → SDL malloc SIGSEGV).

## CPU 3D wave (pitch / texture / mesh / threads)

| Piece | Status | Notes |
|-------|--------|-------|
| Pitch (mouse Y / horizon) | JogSDL #18 | Classic horizon shift only — not 6DOF |
| Frame timing / FPS harness | JogSDL #19 | Real dt + Delay-to-cap; ~60 FPS @ 160×100 |
| CPU texture load/`sample(u,v)` | JogSDL #20 | Shared walls/mesh substrate; wall sampling in frame path still optional |
| Soft-raster textured mesh + depth | JogSDL #22 | Moving cube + per-column wall depth; see above |
| Column/band `go` Dispatcher | JogSDL #23 | PARALLEL default / SERIAL env; needs JogCompiler #33; wasm serial |

## Limits

- Freestanding `wasm32` (no emcc) is not on v2; browser+SDL is `wasm32-emscripten` only.
- FRect layout vs `SDL_FRect` packing is still coarse (8-byte field slots); demos still smoke-present (F18).
- Coroutines/`go` abort under emscripten (no stack switch) — wasm raycaster keeps the serial `render_frame` path.
- Still a 2.5D column caster + soft-raster cube (not a full 3D engine). Pitch is horizon shift only; mesh uses yaw/pitch projection and per-column wall depth. Native wall columns may run PARALLEL via `go`/`Dispatcher`.
- **Raycaster / jog develop:** numeric `as` is convert (JogCompiler #30). Do not revive the old IEEE 2^52 `i_to_f` bitcast helper — after #30 it sitofps `F52+n` and paints a solid door-colored frame. Struct returns still bump-alloc with no free (keep camera/DDA/mesh as package scalars). Parallel bands also need JogCompiler #33 (package `*byte` + GS coro TLS). See JogDocs Friction ([JogDocs #20](https://github.com/Jog-lang/JogDocs/pull/20) marks raw_ptr extern meta fixed; struct-return OOM remains open).
