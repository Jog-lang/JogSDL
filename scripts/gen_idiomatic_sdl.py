#!/usr/bin/env python3
"""Generate idiomatic sdl.<cat> wrappers over sdl3.<cat> raw externs.

Hand-maintained packages (window/render/events/input/timer/opengl + facade)
are left untouched. Skips variadic C functions (Friction). Qualifies SDL_*
types via `raw.` / cross-package imports. bool → SDLError?.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Do not overwrite these hand-written packages.
KEEP = {"window", "render", "events", "input", "timer", "opengl", "surface"}

# SDL header macros — not exported from libSDL3 (only *Runtime symbols exist).
SKIP_SYMBOLS = {
    "CreateThread",
    "CreateThreadWithProperties",
}

# Categories that live only as constants / thin re-exports.
CONST_ONLY = {"keycode", "scancode", "bits", "endian", "pen"}

# Opaque short name → owning sdl3 package (for cross-imports).
OPAQUE_OWNER: dict[str, str] = {
    "SDL_Window": "video",
    "SDL_Renderer": "video",
    "SDL_Texture": "render",
    "SDL_Surface": "surface",
    "SDL_AudioStream": "audio",
    "SDL_AudioSpec": "audio",
    "SDL_Joystick": "joystick",
    "SDL_Gamepad": "gamepad",
    "SDL_Haptic": "haptic",
    "SDL_Sensor": "sensor",
    "SDL_Camera": "camera",
    "SDL_Cursor": "mouse",
    "SDL_Mutex": "mutex",
    "SDL_RWLock": "mutex",
    "SDL_Semaphore": "mutex",
    "SDL_Condition": "mutex",
    "SDL_InitState": "mutex",
    "SDL_Thread": "thread",
    "SDL_IOStream": "iostream",
    "SDL_Storage": "storage",
    "SDL_AsyncIO": "asyncio",
    "SDL_AsyncIOQueue": "asyncio",
    "SDL_Process": "process",
    "SDL_SharedObject": "loadso",
    "SDL_Tray": "tray",
    "SDL_TrayMenu": "tray",
    "SDL_TrayEntry": "tray",
    "SDL_MetalView": "metal",
    "SDL_hid_device": "hidapi",
    "SDL_GUID": "guid",
    "SDL_Palette": "pixels",
    "SDL_PixelFormatDetails": "pixels",
    "SDL_Color": "pixels",
    "SDL_FColor": "pixels",
    "SDL_Rect": "rect",
    "SDL_FRect": "rect",
    "SDL_Point": "rect",
    "SDL_FPoint": "rect",
    "SDL_Event": "events",
    "SDL_GPUDevice": "gpu",
    "SDL_GPUBuffer": "gpu",
    "SDL_GPUTransferBuffer": "gpu",
    "SDL_GPUTexture": "gpu",
    "SDL_GPUSampler": "gpu",
    "SDL_GPUShader": "gpu",
    "SDL_GPUComputePipeline": "gpu",
    "SDL_GPUGraphicsPipeline": "gpu",
    "SDL_GPUCommandBuffer": "gpu",
    "SDL_GPURenderPass": "gpu",
    "SDL_GPUComputePass": "gpu",
    "SDL_GPUCopyPass": "gpu",
    "SDL_GPUFence": "gpu",
}

FN_RE = re.compile(
    r"^\s*fn (SDL_([A-Za-z0-9_]+))\((.*?)\)(?::\s*(.+))?$",
    re.M,
)

JOG_KEYWORDS = {
    "type", "import", "export", "fn", "struct", "interface", "context",
    "error", "return", "defer", "with", "for", "if", "else", "when",
    "break", "continue", "go", "null", "true", "false", "var", "val",
}


def parse_externs(text: str) -> list[dict]:
    fns = []
    for m in FN_RE.finditer(text):
        full, short, params, ret = m.group(1), m.group(2), m.group(3).strip(), (m.group(4) or "void").strip()
        fns.append({"full": full, "short": short, "params": params, "ret": ret})
    return fns


def parse_opaques(text: str) -> list[str]:
    return re.findall(r"@opaque struct (SDL_\w+)", text)


def split_params(params: str) -> list[tuple[str, str]]:
    if not params:
        return []
    parts: list[str] = []
    depth = 0
    cur: list[str] = []
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
    out: list[tuple[str, str]] = []
    for i, p in enumerate(parts):
        if p == "...":
            out.append(("...", "..."))
            continue
        if ":" not in p:
            out.append((f"arg{i}", p))
            continue
        name, typ = p.split(":", 1)
        name, typ = name.strip(), typ.strip()
        if name in JOG_KEYWORDS:
            name = name + "_"
        out.append((name, typ))
    return out


def strip_sdl_prefix_type(typ: str) -> str | None:
    """If typ references an SDL_ name, return that name; else None."""
    m = re.search(r"(SDL_[A-Za-z0-9_]+)", typ)
    return m.group(1) if m else None


def qualify_type(typ: str, cat: str, imports: set[str]) -> str:
    """Qualify SDL_* type refs for use in the idiomatic package."""
    name = strip_sdl_prefix_type(typ)
    if not name:
        return typ
    owner = OPAQUE_OWNER.get(name, cat)
    if owner == cat:
        return typ.replace(name, f"raw.{name}")
    # cross-package: import sdl3.owner as owner_alias — use owner.name
    # Prefer importing the owning sdl3 package under its folder name.
    imports.add(f"import sdl3.{owner}")
    # Avoid double-qualifying already-qualified names from raw files (video.SDL_Window)
    if "." in typ and not typ.startswith("*") and "SDL_" in typ:
        # e.g. already `video.SDL_Window` inside *video.SDL_Window from raw — rewrite
        pass
    # Replace package-qualified forms from raw: video.SDL_Window → video.SDL_Window (sdl3.video)
    # Raw files may already say *video.SDL_Window — map to *video.SDL_Window via import sdl3.video
    if re.search(rf"(?<![\w.]){re.escape(owner)}\.{re.escape(name)}\b", typ):
        return typ  # already owner.Name with import sdl3.owner
    # Bare or *SDL_Name / *const SDL_Name
    return re.sub(rf"(?<![\w.]){re.escape(name)}\b", f"{owner}.{name}", typ)


def handle_name(opaque: str) -> str:
    # SDL_AudioStream → AudioStream; SDL_hid_device → HidDevice
    if opaque.startswith("SDL_"):
        rest = opaque[4:]
    else:
        rest = opaque
    if rest.startswith("hid_"):
        return "Hid" + "".join(p.title() for p in rest[4:].split("_"))
    return rest


def emit_category(cat: str, raw_path: Path, out_path: Path, friction: list[str]) -> tuple[int, int]:
    text = raw_path.read_text()
    fns = parse_externs(text)
    opaques = parse_opaques(text)
    # Also treat non-opaque structs defined in this package as owned.
    for m in re.finditer(r"^struct (SDL_\w+)", text, re.M):
        OPAQUE_OWNER.setdefault(m.group(1), cat)

    imports: set[str] = {f"import sdl3.{cat} as raw"}
    needs_c = "c." in text or "c.char" in text or "c.int" in text or "c.size_t" in text
    needs_sdl = False

    wrapped = 0
    skipped = 0
    body: list[str] = []
    seen_methods: set[str] = set()

    # Handle structs for local opaques
    for op in opaques:
        h = handle_name(op)
        body.append(f"struct {h} {{")
        body.append(f"    ptr: *raw.{op}?")
        body.append("}")
        body.append("")
        body.append(f"fn empty_{h.lower()}(): {h} {{")
        body.append(f"    var h: {h}")
        body.append("    return h")
        body.append("}")
        body.append("")

    for fn in fns:
        if fn["short"] in SKIP_SYMBOLS:
            friction.append(f"{cat}: skip macro-only {fn['full']} (use *Runtime)")
            skipped += 1
            continue
        params = split_params(fn["params"])
        if any(n == "..." or t == "..." for n, t in params):
            friction.append(f"{cat}: skip variadic {fn['full']}")
            skipped += 1
            continue

        # Build param list + call args
        jparams: list[str] = []
        call_args: list[str] = []
        for name, typ in params:
            qtyp = qualify_type(typ, cat, imports)
            # Fix raw-qualified cross forms like *video.SDL_Window when import is sdl3.video
            # If typ already had video.SDL_Window from raw file, qualify_type may have left it —
            # ensure import sdl3.video exists (done in qualify when owner!=cat).
            jparams.append(f"{name}: {qtyp}")
            call_args.append(name)

        jp = ", ".join(jparams)
        ap = ", ".join(call_args)
        ret = fn["ret"]
        jname = fn["short"]

        # DestroyX(handle) → method on handle when single opaque arg of this package.
        # Only one destroy method per handle type.
        if jname.startswith("Destroy") and len(params) == 1:
            pname, ptyp = params[0]
            op = strip_sdl_prefix_type(ptyp)
            if op and op in opaques:
                h = handle_name(op)
                key = f"{h}.destroy"
                if key in seen_methods:
                    # Keep a free function alias instead of a duplicate method.
                    qpt = qualify_type(ptyp, cat, imports)
                    body.append(f"fn {jname}({pname}: {qpt}) {{")
                    body.append(f"    raw.{fn['full']}({pname})")
                    body.append("}")
                    body.append("")
                    wrapped += 1
                    continue
                seen_methods.add(key)
                body.append(f"fn {h}.destroy() {{")
                body.append("    if self.ptr != null {")
                body.append(f"        raw.{fn['full']}(self.ptr!!)")
                body.append("    }")
                body.append("}")
                body.append("")
                wrapped += 1
                continue

        # Create*/Open* returning *Opaque? → (Handle, SDLError?)
        # Non-optional *Opaque returns stay as thin pointer wrappers (raw C may omit ?).
        ret_op = strip_sdl_prefix_type(ret) if ret not in ("void", "bool") else None
        is_opt_ptr = ret_op and ret.rstrip().endswith("?") and ("*" in ret) and ret_op in opaques
        if is_opt_ptr and (jname.startswith("Create") or jname.startswith("Open") or jname.startswith("Acquire")):
            needs_sdl = True
            h = handle_name(ret_op)
            body.append(f"fn {jname}({jp}): ({h}, sdl.SDLError?) {{")
            body.append(f"    val ptr = raw.{fn['full']}({ap})")
            body.append("    if ptr == null {")
            body.append(f"        return empty_{h.lower()}(), sdl.last_error(\"{jname} failed\")")
            body.append("    }")
            body.append(f"    var h: {h}")
            body.append("    h.ptr = ptr")
            body.append("    return h, null")
            body.append("}")
            body.append("")
            wrapped += 1
            continue

        qret = "void" if ret == "void" else qualify_type(ret, cat, imports)

        if ret == "bool":
            needs_sdl = True
            body.append(f"fn {jname}({jp}): sdl.SDLError? {{")
            body.append(f"    if !raw.{fn['full']}({ap}) {{")
            body.append(f"        return sdl.last_error(\"{jname} failed\")")
            body.append("    }")
            body.append("    return null")
            body.append("}")
        elif ret == "void":
            body.append(f"fn {jname}({jp}) {{")
            body.append(f"    raw.{fn['full']}({ap})")
            body.append("}")
        else:
            body.append(f"fn {jname}({jp}): {qret} {{")
            body.append(f"    return raw.{fn['full']}({ap})")
            body.append("}")
        body.append("")
        wrapped += 1

    # Assemble file
    header = [
        f"// Idiomatic wrappers over sdl3.{cat}.",
        f"// Variadic / unexpressible C entry points are omitted — see JogDocs Friction.",
    ]
    # Order imports: sdl3.cat as raw, other sdl3.*, sdl, std.c
    other_imports = sorted(i for i in imports if not i.startswith("import sdl3." + cat))
    header.append(f"import sdl3.{cat} as raw")
    header.extend(other_imports)
    if needs_sdl:
        header.append("import sdl")
    if needs_c or any("c." in line for line in body):
        header.append("import std.c")
    header.append("")

    # Fix cross-type refs that still say video.SDL_Window etc. without ensuring
    # the import alias matches: we use `import sdl3.video` → package alias `video`.
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(header + body))
    return wrapped, skipped


def emit_const_reexport(cat: str, raw_path: Path, out_path: Path) -> int:
    text = raw_path.read_text()
    vals = re.findall(r"^(val\s+SDL_\w+\s*:[^=]+=.+)$", text, re.M)
    # keycode uses SDLK_
    vals += re.findall(r"^(val\s+SDLK_\w+\s*:[^=]+=.+)$", text, re.M)
    fns = parse_externs(text)
    if not vals and not fns:
        # empty raw — note only (no unused import)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            f"// Idiomatic sdl.{cat} — see sdl3.{cat} for raw bindings (no short aliases yet).\n"
        )
        return 0

    # Re-declare constants with shorter names (no need for `raw` import).
    const_lines: list[str] = []
    n = 0
    for v in vals:
        m = re.match(r"val\s+(SDL_?(?:K_)?[A-Za-z0-9_]+)\s*:\s*(\w+)\s*=\s*(.+)$", v)
        if not m:
            continue
        name, typ, expr = m.group(1), m.group(2), m.group(3)
        short = name[4:] if name.startswith("SDL_") else name
        const_lines.append(f"val {short}: {typ} = {expr}")
        n += 1

    fn_lines: list[str] = []
    needs_sdl = False
    needs_c = False
    for fn in fns:
        params = split_params(fn["params"])
        if any(t == "..." for _, t in params):
            continue
        jparams = ", ".join(f"{nm}: {t}" for nm, t in params)
        ap = ", ".join(nm for nm, _ in params)
        if "c." in jparams or "c." in fn["ret"]:
            needs_c = True
        if fn["ret"] == "bool":
            needs_sdl = True
            fn_lines.append(f"fn {fn['short']}({jparams}): sdl.SDLError? {{")
            fn_lines.append(f"    if !raw.{fn['full']}({ap}) {{ return sdl.last_error(\"{fn['short']} failed\") }}")
            fn_lines.append("    return null")
            fn_lines.append("}")
        elif fn["ret"] == "void":
            fn_lines.append(f"fn {fn['short']}({jparams}) {{ raw.{fn['full']}({ap}) }}")
        else:
            fn_lines.append(f"fn {fn['short']}({jparams}): {fn['ret']} {{ return raw.{fn['full']}({ap}) }}")
        fn_lines.append("")
        n += 1

    lines = [f"// Idiomatic re-exports / wrappers for sdl3.{cat}."]
    if fn_lines:
        lines.append(f"import sdl3.{cat} as raw")
    if needs_sdl:
        lines.append("import sdl")
    if needs_c:
        lines.append("import std.c")
    lines.append("")
    lines.extend(const_lines)
    if const_lines and fn_lines:
        lines.append("")
    lines.extend(fn_lines)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    return n


def main() -> int:
    friction: list[str] = []
    total_w = total_s = 0
    cats = sorted(p.name for p in (ROOT / "sdl3").iterdir() if p.is_dir())
    for cat in cats:
        if cat in KEEP:
            continue
        raw_path = ROOT / "sdl3" / cat / f"{cat}.jog"
        if not raw_path.exists():
            continue
        out_path = ROOT / "sdl" / cat / f"{cat}.jog"
        if cat in CONST_ONLY or cat in ("stdinc",):
            n = emit_const_reexport(cat, raw_path, out_path)
            print(f"{cat}: const/reexport {n}")
            total_w += n
            continue
        # opengl raw is empty note — skip overwrite of hand-written sdl/opengl
        if cat == "opengl":
            continue
        w, s = emit_category(cat, raw_path, out_path, friction)
        print(f"{cat}: wrapped={w} skipped={s}")
        total_w += w
        total_s += s

    fr_path = ROOT / "scripts" / "idiomatic_friction.txt"
    fr_path.write_text("\n".join(friction) + ("\n" if friction else ""))
    print(f"TOTAL wrapped={total_w} skipped={total_s} friction={len(friction)} → {fr_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
