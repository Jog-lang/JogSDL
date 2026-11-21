# JogSDL Friction — V1 closures

Canonical log: JogDocs `bootstrap/Friction.md`.

## Fixed (Wave 2)

| Item | Notes |
|---|---|
| GPU data-plane (dust2 KEEP) | `#36` createinfo pack plane, swapchain `*u32`, clear/mesh smoke. Engine `JOGENGINE_PRESENT=gpu` green. |
| Texture.lock / null→`*T` / package `&` | JogCompiler #42 |
| Cross-module `draw_texture_rect` | JogCompiler #43 |

## Won't fix for V1

| Gap | Reason | Follow-up |
|---|---|---|
| Variadic wrappers (`SDL_Log*`, `SDL_SetError`, `SDL_IOprintf`) | Jog cannot wrap `...` outside `extern` | [[design/language/CInterop]] / bindgen After V1; call raw `extern` or skip |
| Macro-only thread symbols (`SDL_CreateThread*`) | Header macros over `*Runtime`; short names not in libSDL3 | Use `*Runtime` exports (already bound) |
| Typed function-pointer callbacks | No Jog callback type / C fn-ptr ABI yet | CInterop After V1; `*void` userdata slots where needed |
| Remaining by-value SDL structs without layouts | Generator omits nested by-value without hand layouts | Expand layouts category-by-category; GPU KEEP pack helpers cover mesh present |

## Residual lists

Generator skip lists: `scripts/idiomatic_friction.txt`, `scripts/idiomatic_friction_v2.txt`.
These are intentional omissions, not silent gaps.

jog-v2 IR call arity is **16** (stack args + SysV pad in JogCompiler #43). Older “>8 args” skips in `idiomatic_friction_v2.txt` are historical; regenerate when next touching the idiomatic surface.
