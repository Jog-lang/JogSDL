# JogSDL

Hand-written [SDL3](https://www.libsdl.org/) bindings for the [Jog](https://github.com/Jog-lang) language, plus a small window smoke app.

Linux x86-64 is the first supported target. Windows and macOS `link.*` lines are listed in `jog.mod` for later.

| | |
|---|---|
| Repo | https://github.com/Jog-lang/JogSDL |
| Local path | `/home/plague_doc/Documents/Projects/Jog/JogSDL` |
| SDL3 pin | **3.4.18** |
| Tarball sha256 | `9c75cf16330322c217dedd2e0609f1124f1b54b8633e763467b4684d0f4334a3` |

## Two-layer model

Public apps import **`jog_sdl.sdl` only**. Raw `@link("SDL3")` / `SDL_*` symbols live in unexported package **`sdl3`** and are not part of the module export list.

```
app  →  package sdl (Jog names, errors, Window/Renderer)  →  package sdl3 (extern)  →  libSDL3
```

| Package | Role |
|---|---|
| `sdl` | Exported. `Init` / `Quit`, `CreateWindow`, `Window` / `Renderer` methods, `poll_event`, `Delay`, `SDLError`, Jog constants (`INIT_VIDEO`, …). |
| `sdl3` | Internal. `@link`, `@opaque`, `SDL_Event` / `SDL_FRect` layout, `zero_event` / `frect`. |

## Layout

```
JogSDL/
  jog.mod                 # module jog_sdl (library), export sdl, link.linux SDL3
  sdl/sdl.jog             # idiomatic Jog API
  sdl3/sdl3.jog           # raw extern bindings (unexported)
  examples/window/        # window_demo executable
  scripts/fetch-sdl3.sh
  scripts/build-sdl3.sh
  prefix/                 # local SDL3 install (gitignored)
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

Host-only discovery (a prefix outside the tree) goes in a gitignored `jog.local.mod` next to the app, e.g. under `examples/window/`:

```
libdir.linux /home/me/JogSDL/prefix/lib64
```

Or pass `--libdir` / set `JOG_LIBDIRS`. **Runtime** still needs the loader to find `libSDL3.so` until rpath lands — keep `LD_LIBRARY_PATH` (or install SDL system-wide) for `run`:

```bash
export JOG=~/.local/bin/jog
export JOG_BUILD=~/.local/bin/jog-build
# ~/.local/bin/jog needs JOG_ROOT (std/ + runtime/ next to a compiler checkout)
export JOG_ROOT=/home/plague_doc/Documents/Projects/Jog/JogCompiler
ROOT=/home/plague_doc/Documents/Projects/Jog/JogSDL
LIBDIR="$ROOT/prefix/lib64"
[[ -d "$LIBDIR" ]] || LIBDIR="$ROOT/prefix/lib"
# Link: no LIBRARY_PATH required when prefix/ matches jog.mod libdir.
# Run: still need the dynamic loader path (rpath follow-up).
export LD_LIBRARY_PATH="$LIBDIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

cd "$ROOT/examples/window"
# Prove link without LIBRARY_PATH:
unset LIBRARY_PATH
"$JOG_BUILD" build -o out/window_demo
"$JOG_BUILD" run
```

Or with the compiler directly:

```bash
cd "$ROOT/examples/window"
"$JOG" build --module jog_sdl="$ROOT" --libdir "$ROOT/prefix/lib64"
"$JOG" run --module jog_sdl="$ROOT" --libdir "$ROOT/prefix/lib64"
```

Needs a GUI session (`DISPLAY` or Wayland). On this machine: `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`. Close the window to exit cleanly (SDL3 delivers `EVENT_WINDOW_CLOSE_REQUESTED`; the smoke app also accepts `EVENT_QUIT`).

Fedora build deps for SDL3 (system install when you have sudo): see [SDL README-linux](https://wiki.libsdl.org/SDL3/README-linux#build-dependencies). Without sudo, this checkout can unpack `-devel` RPMs into `.deps/` and `scripts/build-sdl3.sh` will pick that up via `PKG_CONFIG_PATH`.

## Out of scope

Full SDL3 surface, audio/gamepad, Android/iOS, bindgen, Windows CI.
