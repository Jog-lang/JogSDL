# JogSDL

Hand-written [SDL3](https://www.libsdl.org/) bindings for the [Jog](https://github.com/Jog-lang) language, plus a window smoke app and a Wolfenstein-style software raycaster.

Linux x86-64 is the first supported target. Windows and macOS `link.*` lines are listed in `jog.mod` for later.

**JogCompiler v2:** see [`v2/`](v2/) — `jog-v2` / `jog-build` demos with `libdir` → rpath (no `LD_LIBRARY_PATH`). Root `sdl/` + `examples/` remain the develop/`jogc` layout.

| | |
|---|---|
| Repo | https://github.com/Jog-lang/JogSDL |
| Local path | `/home/plague_doc/Documents/Projects/Jog/JogSDL` |
| SDL3 pin | **3.4.18** |
| Tarball sha256 | `9c75cf16330322c217dedd2e0609f1124f1b54b8633e763467b4684d0f4334a3` |

## Two-layer model

Public apps import **`jog_sdl.sdl` only**. Raw `@link("SDL3")` / `SDL_*` symbols live in unexported package **`sdl3`** and are not part of the module export list.

```
app  →  package sdl (Jog names, errors, Window/Renderer/Texture)  →  package sdl3 (extern)  →  libSDL3
```

| Package | Role |
|---|---|
| `sdl` | Exported. `Init` / `Quit`, `CreateWindow` / `CreateWindowAndRenderer`, `Window` / `Renderer` / `Texture`, `PollEvent`, `KeyboardIsDown`, `GetTicks`, `Delay`, `SDLError`, Jog constants. |
| `sdl3` | Internal. `@link`, `@opaque`, `SDL_Event` / `SDL_FRect` / `SDL_Rect` layout, `zero_event` / `frect`. |

## Layout

```
JogSDL/
  jog.mod                 # module jog_sdl (library), export sdl, link.linux SDL3, libdir
  sdl/sdl.jog             # idiomatic Jog API
  sdl3/sdl3.jog           # raw extern bindings (unexported)
  examples/window/        # window_demo executable
  examples/raycaster/     # Wolfenstein-style DDA software raycaster
  scripts/fetch-sdl3.sh
  scripts/build-sdl3.sh
  scripts/build-sdl3-emscripten.sh
  prefix/                 # local SDL3 install (gitignored)
  prefix-emscripten/      # Emscripten static SDL3 (gitignored)
  vendor/SDL3-3.4.18/     # extracted source (gitignored)
```

## Build SDL3 into `prefix/`

Needs `cmake`, `ninja`, `curl`, and the usual X11/Wayland/audio development packages on Fedora. Install only what CMake reports if configure fails.

```bash
cd /home/plague_doc/Documents/Projects/Jog/JogSDL
chmod +x scripts/*.sh
./scripts/fetch-sdl3.sh
./scripts/build-sdl3.sh
```

That installs shared `libSDL3.so` under `prefix/lib` (or `prefix/lib64`) and headers under `prefix/include/SDL3/`.

## Day to day

- Open this folder in Cursor (JogLSP already installed on this machine).
- Compiler / build tool: `JOG=~/.local/bin/jog`, `JOG_BUILD=~/.local/bin/jog-build`.
- Rebuild SDL only when upgrading the pin (`SDL3_VERSION` / sha256 in `scripts/fetch-sdl3.sh`).
- Extend `sdl3/sdl3.jog` for new raw APIs; wrap them in `sdl/sdl.jog` before apps use them.

### Check the library

```bash
export JOG=~/.local/bin/jog
export JOG_ROOT=/home/plague_doc/Documents/Projects/Jog/JogCompiler
cd /home/plague_doc/Documents/Projects/Jog/JogSDL
"$JOG" check
```

### Build and run the smoke app

`jog.mod` lists portable `libdir.linux ./prefix/lib64` (and `./prefix/lib`), so **linking no longer needs `LIBRARY_PATH`**. After `scripts/build-sdl3.sh`, `jog-build` merges those paths and passes `--libdir` to `jog`.

Host-only discovery (a prefix outside the tree) goes in a gitignored `jog.local.mod` next to the app, e.g. under `examples/window/` (see `jog.local.mod.example`).

**Runtime** still needs the loader to find `libSDL3.so` until rpath lands — keep `LD_LIBRARY_PATH` (or install SDL system-wide) for `run`:

```bash
export JOG=~/.local/bin/jog
export JOG_BUILD=~/.local/bin/jog-build
export JOG_ROOT=/home/plague_doc/Documents/Projects/Jog/JogCompiler
ROOT=/home/plague_doc/Documents/Projects/Jog/JogSDL
LIBDIR="$ROOT/prefix/lib64"
[[ -d "$LIBDIR" ]] || LIBDIR="$ROOT/prefix/lib"
export LD_LIBRARY_PATH="$LIBDIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

cd "$ROOT/examples/window"
unset LIBRARY_PATH
"$JOG_BUILD" build -o out/window_demo
"$JOG_BUILD" run
```

Close the window or press Escape to exit (SDL3 delivers `EVENT_WINDOW_CLOSE_REQUESTED`; the smoke app also accepts `EVENT_QUIT` / Escape).

### Raycaster

Wolfenstein-style v1: fixed grid map, per-column DDA, flat-colored walls (side shading), WASD + turn, software ARGB framebuffer uploaded through a streaming texture.

```bash
# same JOG / JOG_BUILD / JOG_ROOT / LD_LIBRARY_PATH as above
cd "$ROOT/examples/raycaster"
unset LIBRARY_PATH
"$JOG_BUILD" build -o out/raycaster
"$JOG_BUILD" run
# map/DDA unit tests (+ require.test mock smoke):
"$JOG_BUILD" test
```

Controls: **W/A/S/D** move, **Left/Right** turn, **Escape** or window close to quit.

Fedora build deps for SDL3 (system install when you have sudo): see [SDL README-linux](https://wiki.libsdl.org/SDL3/README-linux#build-dependencies). Without sudo, this checkout can unpack `-devel` RPMs into `.deps/` and `scripts/build-sdl3.sh` will pick that up via `PKG_CONFIG_PATH`.


## Browser (Emscripten)

Requires [emsdk](https://emscripten.org/) (`emcc` / `emcmake` on `PATH`) and a compiler that accepts `--target wasm32-emscripten`.

```bash
source ~/emsdk/emsdk_env.sh   # or your emsdk path
cd /home/plague_doc/Documents/Projects/Jog/JogSDL
./scripts/fetch-sdl3.sh
./scripts/build-sdl3-emscripten.sh   # → prefix-emscripten/lib/libSDL3.a

export JOG=/path/to/jog   # seed or develop with wasm32-emscripten
export JOG_BUILD=/path/to/jog-build
export JOG_ROOT=/home/plague_doc/Documents/Projects/Jog/JogCompiler-seed   # or develop

cd examples/raycaster
"$JOG_BUILD" build --target wasm32-emscripten -o out/raycaster.html
# Serve out/ (emcc shell) over HTTP and open raycaster.html
```

`jog.mod` carries `link.emscripten SDL3` and `libdir.emscripten ./prefix-emscripten/lib`. The demos use `@export jog_app_iterate` + `jog_host_run_loop()` so one source works on desktop and in the browser.

## Out of scope

Full SDL3 surface, textured walls/sprites/audio, bindgen, Windows CI, publishing to a registry.
