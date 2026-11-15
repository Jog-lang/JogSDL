# JogSDL

Hand-written [SDL3](https://www.libsdl.org/) bindings for the [Jog](https://github.com/Jog-lang) language, plus a window smoke app and a Wolfenstein-style software raycaster.

Linux x86-64 is the first supported target. Windows and macOS `link.*` lines are listed in `jog.mod` for later.

**Toolchain:** **jog-v2 only** (`JOG=~/.local/bin/jog-v2`). Seed C `jog` and develop/`jogc` are historical — not live targets for this repo. Prefer `jog-build` + `libdir` (rpath); avoid leaving `$JOG` pointed at seed.

| | |
|---|---|
| Repo | https://github.com/Jog-lang/JogSDL |
| Local path | `/home/plague_doc/Documents/Projects/Jog/JogSDL` |
| SDL3 pin | **3.4.18** |
| Tarball sha256 | `9c75cf16330322c217dedd2e0609f1124f1b54b8633e763467b4684d0f4334a3` |

## Two-layer model

Public apps import **`jog_sdl.sdl`** and **`sdl.*`** packages. Raw `@link("SDL3")` / `SDL_*` live in unexported **`sdl3.*`**.

```
app  →  sdl / sdl.* (Jog names, errors, handles, enum+pack flags)  →  sdl3.* (extern)  →  libSDL3
```

| Package | Role |
|---|---|
| `sdl` | Facade: `Init(...InitFlag)` / `Quit`, `SDLError`, shared enums/constants. |
| `sdl.window` / `sdl.render` / `sdl.events` / `sdl.input` / `sdl.timer` | Hand-written idiomatic demos API. |
| `sdl.<category>` | Idiomatic wrappers over `sdl3.<category>`. Variadics / macro-only entry points omitted — see JogDocs Friction. |
| `sdl3.<category>` | Internal raw externs (~1100 `SDL_*` symbols, pin 3.4.18). |

API docs live in **comments on Jog declarations** (plus links to the [SDL3 wiki](https://wiki.libsdl.org/SDL3)).

## Layout

```
JogSDL/
  jog.mod                 # module jog_sdl (library), export sdl + sdl.*, link + libdir
  sdl/sdl.jog             # Init/Quit facade + SDLError + flag enums
  sdl/<category>/         # idiomatic packages (window, render, audio, …)
  sdl3/<category>/        # raw @link("SDL3") per SDL header category
  examples/window/        # window_demo executable
  examples/raycaster/     # software raycaster (float camera / doors / mouse look)
  scripts/fetch-sdl3.sh
  scripts/build-sdl3.sh
  scripts/build-sdl3-emscripten.sh
  scripts/check-sdl3-sync.sh
  scripts/check-idiomatic-sdl.sh
  scripts/check-sdl-public-api.sh
  scripts/gen_sdl3_bindings.py
  scripts/gen_idiomatic_sdl.py
  prefix/                 # local SDL3 install (gitignored)
  prefix-emscripten/      # Emscripten static SDL3 (gitignored)
  vendor/SDL3-3.4.18/     # extracted source (gitignored)
```

### Wave status (SDL3 3.4.18)

| Wave | Categories | Status |
|---|---|---|
| 0 | Package split, sync script | done |
| A | init, error, hints, properties, log, assert, version, selective stdinc | done (raw) |
| B | video, render, pixels, blendmode, rect, surface, clipboard, vulkan, metal, camera | done (raw) |
| C | events, keyboard, keycode, scancode, mouse, joystick, gamepad, touch, pen, sensor, hidapi | done (raw) |
| D–K | haptic, audio, gpu, thread/mutex/atomic, timer/time, filesystem/storage/iostream/asyncio, platform/cpuinfo/endian/bits, loadso/process/power/messagebox/dialog/tray/locale/system/guid/misc/main, thin GL bridge | done (raw) |

After changing raw externs: `./scripts/check-sdl3-sync.sh`. Public signature gate: `./scripts/check-sdl-public-api.sh`.

## Build SDL3 into `prefix/`

Needs `cmake`, `ninja`, `curl`, and the usual X11/Wayland/audio development packages on Fedora.

```bash
cd /home/plague_doc/Documents/Projects/Jog/JogSDL
chmod +x scripts/*.sh
./scripts/fetch-sdl3.sh
./scripts/build-sdl3.sh
```

That installs shared `libSDL3.so` under `prefix/lib` (or `prefix/lib64`) and headers under `prefix/include/SDL3/`. On Fedora, if CMake installs only `lib64`, the script also creates `prefix/lib` → `lib64` so `libdir.linux ./prefix/lib` does not warn.

## Day to day

- Open this folder in Cursor (JogLSP already installed on this machine).
- Compiler / build tool: `JOG=~/.local/bin/jog-v2`, `JOG_BUILD=~/.local/bin/jog-build`.
- Rebuild SDL only when upgrading the pin (`SDL3_VERSION` / sha256 in `scripts/fetch-sdl3.sh`).
- Extend `sdl3/<category>/` for new raw APIs; wrap them in `sdl/<category>/` before apps use them.

### Check / gates

```bash
export JOG=~/.local/bin/jog-v2
cd /home/plague_doc/Documents/Projects/Jog/JogSDL
./scripts/check-sdl3-sync.sh
./scripts/check-idiomatic-sdl.sh
./scripts/check-sdl-public-api.sh
```

### Build and run the smoke app

`jog.mod` lists `libdir.linux ./prefix/lib64` (and `./prefix/lib`). After `scripts/build-sdl3.sh`, `jog-build` merges those paths and passes `--libdir` to `jog` (rpath on native).

```bash
export JOG=~/.local/bin/jog-v2
export JOG_BUILD=~/.local/bin/jog-build
ROOT=/home/plague_doc/Documents/Projects/Jog/JogSDL

cd "$ROOT/examples/window"
"$JOG" build . -o out/window_demo
./out/window_demo
# or: "$JOG_BUILD" build -o out/window_demo && "$JOG_BUILD" run
```

Close the window or press Escape to exit.

### Raycaster

Proto-3D float camera (`Vec2` + view basis), doors, mouse look; optional parallel column bands via `go`/Dispatcher.

```bash
export JOG=~/.local/bin/jog-v2
cd "$ROOT/examples/raycaster"
"$JOG" build . -o out/raycaster
JOGSDL_RAYCASTER_SMOKE=1 ./out/raycaster
```

Controls: **W/A/S/D** move, **arrows / mouse** look, **E/Space** door, **Escape** quit.

## Browser (Emscripten)

Requires [emsdk](https://emscripten.org/) (`emcc` / `emcmake` on `PATH`) and jog-v2 with `--target wasm32-emscripten`.

```bash
source ~/emsdk/emsdk_env.sh
cd /home/plague_doc/Documents/Projects/Jog/JogSDL
./scripts/fetch-sdl3.sh
./scripts/build-sdl3-emscripten.sh   # → prefix-emscripten/lib/libSDL3.a

export JOG=~/.local/bin/jog-v2
export JOG_BUILD=~/.local/bin/jog-build

cd examples/raycaster-emscripten
"$JOG_BUILD" build --target wasm32-emscripten -o out/raycaster.html
```

`jog.mod` carries `link.emscripten SDL3` and `libdir.emscripten ./prefix-emscripten/lib`.

## Out of scope

`SDL_test_*`, `SDL_oldnames`, glext dump, full stdinc dump, headers absent from 3.4.18, bindgen as a build step, Windows CI, publishing to a registry.
