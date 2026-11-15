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
- **Supported toolchain: jog-v2 only** (`~/.local/bin/jog-v2`). Seed C `jog` and develop/`jogc` are history/lookup only — do not target them for demos or new bindings.
- Flat layout: `sdl/` (public), `sdl3/` (unexported raw `@link`), `examples/` at repo root. There is no nested `v2/` tree.
- Public apps import `jog_sdl.sdl` / `sdl.*` only; raw `SDL_*` lives in unexported `sdl3`.
- If jog-v2 lacks a feature that blocks idiomatic `sdl.*` (packs, enums, handles, errors, …): note it in JogDocs `bootstrap/Friction.md`, fix the compiler, then resume — do not invent JogSDL workarounds.
- Ivan writes the Jog bindings and demos by hand. Do not invent Jog language features here; explain, review, and point at the spec.
- Build/smoke with `jog-v2` / `jog-build`; see `README.md`.
