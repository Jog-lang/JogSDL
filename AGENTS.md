# Agents (JogSDL)

## Jog knowledge

- Jog language notes, plans, checklists and the friction log live in JogDocs:
  Fedora `~/Documents/Projects/Jog/JogDocs` (or `/home/plague_doc/Documents/Projects/Jog/JogDocs`);
  Windows `D:/Projects/Jog/JogDocs`
  (https://github.com/Jog-lang/JogDocs).
- Read JogDocs `AGENTS.md` first, then `guide/JogQuickRef.md` before writing or reviewing Jog.
- Agent skills canon: JogDocs `.agents/skills/` (pointer: `.agents/skills/README.md` here). See `guide/UsingJogDocs.md`.
- Log rough edges in JogDocs `bootstrap/Friction.md`. Prefer the Fedora tree for SDL smoke.

## This repo

- Hand-written SDL3 bindings and demos for Jog. Fedora path: `~/Documents/Projects/Jog/JogSDL`.
- Root `sdl/` + `examples/` target develop/`jogc`. JogCompiler v2 demos live under `v2/`.
- Public apps import `jog_sdl.sdl` only; raw `SDL_*` lives in unexported `sdl3`.
- Ivan writes the Jog bindings and demos by hand. Do not implement Jog features here unless asked; explain, review, and point at the spec.
- Build/smoke with the local `jog` / `jog-v2` / `jog-build` Ivan already uses; see `README.md`.
