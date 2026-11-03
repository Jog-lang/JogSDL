# JogSDL

Hand-written [SDL3](https://www.libsdl.org/) bindings for the [Jog](https://github.com/Jog-lang) language, plus a small window smoke app.

Linux x86-64 is the first supported target. Windows and macOS `link.*` lines are listed in `jog.mod` for later.

| | |
|---|---|
| Repo | https://github.com/Jog-lang/JogSDL |
| Local path | `/home/plague_doc/Documents/Projects/Jog/JogSDL` |
| SDL3 pin | **3.4.18** |
| Tarball sha256 | `9c75cf16330322c217dedd2e0609f1124f1b54b8633e763467b4684d0f4334a3` |

## Layout

```
JogSDL/
  jog.mod                 # module jog_sdl (library), export sdl3, link.linux SDL3
  sdl3/sdl3.jog           # hand-written extern bindings
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
- Edit `sdl3/sdl3.jog` to add APIs; extend `examples/window` or add new examples.

### Check the library

```bash
export JOG=~/.local/bin/jog
export JOG_ROOT=/home/plague_doc/Documents/Projects/Jog/JogCompiler
cd /home/plague_doc/Documents/Projects/Jog/JogSDL
"$JOG" check
```

### Build and run the smoke app

Linker discovery uses the repo-local prefix. On this Fedora machine the working env is:

```bash
export JOG=~/.local/bin/jog
export JOG_BUILD=~/.local/bin/jog-build
# ~/.local/bin/jog needs JOG_ROOT (std/ + runtime/ next to a compiler checkout)
export JOG_ROOT=/home/plague_doc/Documents/Projects/Jog/JogCompiler
ROOT=/home/plague_doc/Documents/Projects/Jog/JogSDL
# On Fedora this machine, cmake installs to prefix/lib64.
LIBDIR="$ROOT/prefix/lib64"
[[ -d "$LIBDIR" ]] || LIBDIR="$ROOT/prefix/lib"
export LIBRARY_PATH="$LIBDIR${LIBRARY_PATH:+:$LIBRARY_PATH}"
export LD_LIBRARY_PATH="$LIBDIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CPATH="$ROOT/prefix/include${CPATH:+:$CPATH}"

cd "$ROOT/examples/window"
"$JOG_BUILD" run
```

Or with the compiler directly:

```bash
cd "$ROOT/examples/window"
"$JOG" build --module jog_sdl="$ROOT"
"$JOG" run --module jog_sdl="$ROOT"
```

Needs a GUI session (`DISPLAY` or Wayland). On this machine: `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`. Close the window to exit cleanly.

Fedora build deps for SDL3 (system install when you have sudo): see [SDL README-linux](https://wiki.libsdl.org/SDL3/README-linux#build-dependencies). Without sudo, this checkout can unpack `-devel` RPMs into `.deps/` and `scripts/build-sdl3.sh` will pick that up via `PKG_CONFIG_PATH`.

## Out of scope (skeleton)

Full SDL3 surface, audio/gamepad, Android/iOS, bindgen, Windows CI.
