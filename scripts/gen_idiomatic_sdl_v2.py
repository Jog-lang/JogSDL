#!/usr/bin/env python3
"""Generate v2 flat-merge idiomatic sdl/<cat> wrappers over SDL_* externs.

v2 has no package namespaces when required — call SDL_* directly.
Skip symbols already defined in hand-written v2/sdl packages.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEEP_DIRS = {"window", "render", "events", "input", "timer"}  # hand-written

# JogCompiler-v2 IR call arity hard limit (args.len + context arity > 8 → TooManyArgs).
V2_MAX_ARGS = 8

# SDL header macros — not exported from libSDL3 (only *Runtime symbols exist).
SKIP_SYMBOLS = {
    "CreateThread",
    "CreateThreadWithProperties",
}

EXISTING = {
    "Init", "Quit", "CreateWindow", "Window", "Renderer", "Texture", "FRect", "frect",
    "Event", "PollEventHas", "EventType", "EventScancode", "KeyboardIsDown",
    "MouseDelta", "GetRelativeMouseDelta", "ReadRelativeMouse", "f32_slot_to_f64",
    "f32bits_to_f64", "UpdateTextureRaw", "DrawTextureRaw", "SetDrawColorRaw",
    "ClearRaw", "PresentRaw", "Delay", "GetTicks",
    "INIT_VIDEO", "EVENT_QUIT", "EVENT_WINDOW_CLOSE_REQUESTED", "EVENT_KEY_DOWN",
    "EVENT_KEY_UP", "EVENT_MOUSE_MOTION", "WINDOW_RESIZABLE", "SCANCODE_A",
    "SCANCODE_D", "SCANCODE_E", "SCANCODE_Q", "SCANCODE_S", "SCANCODE_W",
    "SCANCODE_ESCAPE", "SCANCODE_SPACE", "SCANCODE_RIGHT", "SCANCODE_LEFT",
    "PIXELFORMAT_ARGB8888", "TEXTUREACCESS_STREAMING",
}

FRICTION: list[str] = []

FN_RE = re.compile(r"^\s*fn (SDL_([A-Za-z0-9_]+))\((.*?)\)(?::\s*(.+))?$", re.M)
JOG_KW = {"type", "import", "export", "fn", "struct", "interface", "context", "error"}


def split_params(params: str) -> list[tuple[str, str]]:
    if not params.strip():
        return []
    parts, depth, cur = [], 0, []
    for ch in params:
        if ch == "(":
            depth += 1
            cur.append(ch)
        elif ch == ")":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur).strip())
    out = []
    for i, p in enumerate(parts):
        if p == "...":
            out.append(("...", "..."))
            continue
        if ":" not in p:
            out.append((f"arg{i}", p))
            continue
        n, t = p.split(":", 1)
        n, t = n.strip(), t.strip()
        if n in JOG_KW:
            n = n + "_"
        out.append((n, t))
    return out


def map_type(t: str) -> str:
    t = t.strip()
    if t == "...":
        return "..."
    if t in ("bool",):
        return "i32"
    if t.startswith("c."):
        if "size" in t:
            return "u64"
        return "i32"
    if "*" in t:
        stars = t.count("*")
        return ("*" * min(stars, 2)) + "byte"
    if t in ("u8", "u16", "u32", "u64", "i8", "i16", "i32", "i64", "f32", "f64", "usize", "isize"):
        return t
    # by-value SDL struct — use *byte out-param style isn't available; skip at fn level
    if t.startswith("SDL_") or t.startswith("raw.") or "." in t:
        return None  # signal skip
    return t


def emit_cat(cat: str, raw_path: Path, out_path: Path) -> tuple[int, int]:
    text = raw_path.read_text()
    # constants
    lines = [
        f"// Idiomatic v2 wrappers for SDL {cat} (flat merge; calls SDL_* directly).",
        f"// Variadics / by-value structs omitted — see JogDocs Friction.",
        "",
    ]
    n = 0
    skipped = 0
    for m in re.finditer(r"^val\s+(SDL_?(?:K_)?[A-Za-z0-9_]+)\s*:\s*(\w+)\s*=\s*(.+)$", text, re.M):
        name, typ, expr = m.group(1), m.group(2), m.group(3)
        short = name[4:] if name.startswith("SDL_") else name
        if short in EXISTING or name in EXISTING:
            continue
        lines.append(f"val {short}: {typ} = {expr}")
        EXISTING.add(short)
        n += 1

    for m in FN_RE.finditer(text):
        full, short, params, ret = m.group(1), m.group(2), m.group(3).strip(), (m.group(4) or "void").strip()
        if short in EXISTING or short in SKIP_SYMBOLS:
            if short in SKIP_SYMBOLS:
                FRICTION.append(f"v2/{cat}: skip macro-only {full} (use *Runtime)")
            skipped += 1
            continue
        ps = split_params(params)
        if any(t == "..." for _, t in ps):
            FRICTION.append(f"v2/{cat}: skip variadic {full}")
            skipped += 1
            continue
        if len(ps) > V2_MAX_ARGS:
            FRICTION.append(f"v2/{cat}: skip {full} — {len(ps)} args > jog-v2 IR limit {V2_MAX_ARGS}")
            skipped += 1
            continue
        mapped = []
        ok = True
        for pname, ptyp in ps:
            mt = map_type(ptyp)
            if mt is None:
                ok = False
                break
            mapped.append((pname, mt))
        if not ok:
            FRICTION.append(f"v2/{cat}: skip {full} — by-value SDL struct / unmapped type")
            skipped += 1
            continue
        r = "void" if ret == "void" else map_type(ret)
        if r is None:
            FRICTION.append(f"v2/{cat}: skip {full} — unmapped return type")
            skipped += 1
            continue
        # v2 bool is i32 already on many externs
        if r == "i32" and ret == "bool":
            r = "i32"
        jp = ", ".join(f"{a}: {b}" for a, b in mapped)
        ap = ", ".join(a for a, _ in mapped)
        if r == "void":
            lines.append(f"fn {short}({jp}) {{")
            lines.append(f"    {full}({ap})")
            lines.append("}")
        else:
            lines.append(f"fn {short}({jp}): {r} {{")
            lines.append(f"    return {full}({ap})")
            lines.append("}")
        lines.append("")
        EXISTING.add(short)
        n += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    return n, skipped


def main() -> int:
    total = skip = 0
    for d in sorted((ROOT / "v2" / "sdl3").iterdir()):
        if not d.is_dir():
            continue
        cat = d.name
        if cat in KEEP_DIRS:
            continue
        raw = d / f"{cat}.jog"
        if not raw.exists():
            continue
        # Don't create opengl under v2 unless useful — root has sdl/opengl; v2 can get thin too
        n, s = emit_cat(cat, raw, ROOT / "v2" / "sdl" / cat / f"{cat}.jog")
        print(f"v2 {cat}: {n} skipped={s}")
        total += n
        skip += s

    # Refresh v2/jog.mod source list
    sources = []
    for pattern in ["sdl3/**/*.jog", "sdl/**/*.jog"]:
        for p in sorted((ROOT / "v2").glob(pattern)):
            rel = p.relative_to(ROOT / "v2").as_posix()
            if rel == "sdl/sdl.jog":
                continue
            sources.append(rel)
    lines = [
        "# JogSDL library for JogCompiler v2 (flat source merge via require).",
        "# Examples: require jog_sdl ../..",
        "module jog_sdl",
        "version 0.1.0",
        "",
        "root sdl/sdl.jog",
        "",
    ]
    for s in sources:
        lines.append(f"source {s}")
    lines += [
        "",
        "link.linux SDL3",
        "link.emscripten SDL3",
        "libdir.linux ../prefix/lib64",
        "libdir.linux ../prefix/lib",
        "libdir.emscripten ../prefix-emscripten/lib",
        "",
    ]
    (ROOT / "v2" / "jog.mod").write_text("\n".join(lines))
    friction_path = ROOT / "scripts" / "idiomatic_friction_v2.txt"
    friction_path.write_text("\n".join(FRICTION) + ("\n" if FRICTION else ""))
    print(f"TOTAL v2 wrapped={total} skipped={skip} sources={len(sources)} friction={len(FRICTION)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
