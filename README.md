# JogSDL

Hand-written [SDL3](https://www.libsdl.org/) bindings for the [Jog](https://github.com/Jog-lang) language, plus a window smoke app and a Wolfenstein-style software raycaster.

Linux x86-64 is the first supported target. Windows and macOS `link.*` lines are listed in `jog.mod` for later.

**JogCompiler v2:** see [`v2/`](v2/) — use `jog-v2` (set `JOG=~/.local/bin/jog-v2`; do not leave `$JOG` on seed). `jog-build` + `libdir` → rpath (no `LD_LIBRARY_PATH`). The v2 raycaster is a proto-3D float camera (`Vec2` + view basis), doors, and mouse look (`std.math` + `object` on wasm). Root `sdl/` + `examples/` remain the develop/`jogc` layout.

| | |
|---|---|
| Repo | https://github.com/Jog-lang/JogSDL |
| Local path | `/home/plague_doc/Documents/Projects/Jog/JogSDL` |
| SDL3 pin | **3.4.18** |
| Tarball sha256 | `9c75cf16330322c217dedd2e0609f1124f1b54b8633e763467b4684d0f4334a3` |

## Two-layer model

Public apps import **`jog_sdl.sdl`** and exported **`jog_sdl.sdl.*`** subpackages. Raw `@link("SDL3")` / `SDL_*` live in unexported **`sdl3.*`** packages.

```
app  →  sdl / sdl.* (Jog names, errors, handles)  →  sdl3.* (extern)  →  libSDL3
```

| Package | Role |
|---|---|
| `sdl` | Facade: `Init` / `Quit`, `SDLError`, shared constants. |
| `sdl.window` / `sdl.render` / `sdl.events` / `sdl.input` / `sdl.timer` / `sdl.opengl` | Hand-written idiomatic demos API. |
| `sdl.<category>` | Idiomatic wrappers over `sdl3.<category>` (~1000 short names; `SDLError?`, handles). Variadics / macro-only entry points omitted — see JogDocs Friction. |
| `sdl3.<category>` | Internal raw externs (~1100 `SDL_*` symbols, pin 3.4.18). |

## Layout

```
JogSDL/
  jog.mod                 # module jog_sdl (library), export sdl + sdl.*, link + libdir
  sdl/sdl.jog             # Init/Quit facade + SDLError + constants
  sdl/<category>/         # idiomatic packages (window, render, audio, …)
  sdl3/<category>/        # raw @link("SDL3") per SDL header category
  examples/window/        # window_demo executable
  examples/raycaster/     # Wolfenstein-style DDA software raycaster
  v2/                     # jog-v2 library + demos (require jog_sdl)
  scripts/fetch-sdl3.sh
  scripts/build-sdl3.sh
  scripts/build-sdl3-emscripten.sh
  scripts/check-sdl3-sync.sh
  scripts/check-idiomatic-sdl.sh
  scripts/gen_sdl3_bindings.py
  scripts/gen_idiomatic_sdl.py
  scripts/gen_idiomatic_sdl_v2.py
  prefix/                 # local SDL3 install (gitignored)
  prefix-emscripten/      # Emscripten static SDL3 (gitignored)
  vendor/SDL3-3.4.18/     # extracted source (gitignored)
```

### Wave status (SDL3 3.4.18)

| Wave | Categories | Status |
|---|---|---|
| 0 | Package split, v2 library, sync script | done |
| A | init, error, hints, properties, log, assert, version, selective stdinc | done (raw) |
| B | video, render, pixels, blendmode, rect, surface, clipboard, vulkan, metal, camera | done (raw) |
| C | events, keyboard, keycode, scancode, mouse, joystick, gamepad, touch, pen, sensor, hidapi | done (raw) |
| D–K | haptic, audio, gpu, thread/mutex/atomic, timer/time, filesystem/storage/iostream/asyncio, platform/cpuinfo/endian/bits, loadso/process/power/messagebox/dialog/tray/locale/system/guid/misc/main, thin GL bridge | done (raw) |

Keep root and `v2/sdl3` aligned: `./scripts/check-sdl3-sync.sh`.

## Build SDL3 into `prefix/`

Needs `cmake`, `ninja`, `curl`, and the usual X11/Wayland/audio development packages on Fedora. Install only what CMake reports if configure fails.

```bash
cd /home/plague_doc/Documents/Projects/Jog/JogSDL
chmod +x scripts/*.sh
./scripts/fetch-sdl3.sh
./scripts/build-sdl3.sh
```

That installs shared `libSDL3.so` under `prefix/lib` (or `prefix/lib64`) and headers under `prefix/include/SDL3/`. On Fedora, if CMake installs only `lib64`, the script also creates `prefix/lib` → `lib64` so `libdir.linux ./prefix/lib` does not warn (F15).

## Day to day

- Open this folder in Cursor (JogLSP already installed on this machine).
- Compiler / build tool: `JOG=~/.local/bin/jog`, `JOG_BUILD=~/.local/bin/jog-build`.
- Rebuild SDL only when upgrading the pin (`SDL3_VERSION` / sha256 in `scripts/fetch-sdl3.sh`).
- Extend `sdl3/<category>/` for new raw APIs; wrap them in `sdl/<category>/` before apps use them.
- After changing raw externs: `./scripts/check-sdl3-sync.sh`.

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

`SDL_test_*`, `SDL_oldnames`, glext dump, full stdinc dump, headers absent from 3.4.18, bindgen as a build step, Windows CI, publishing to a registry.
