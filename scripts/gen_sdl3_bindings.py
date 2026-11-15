#!/usr/bin/env python3
"""One-shot generator: SDL3 headers → Jog sdl3.<cat> raw externs (root + v2).

Not a build step / bindgen — produces checked-in hand-maintainable .jog files.
Skips (logged): function-pointer params, va_list, bitfields, and known friction.
Preserves existing hand-tuned type layouts when --merge-existing.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HDR_DIR_DEFAULT = Path(__file__).resolve().parents[1] / "prefix" / "include" / "SDL3"
ROOT = Path(__file__).resolve().parents[1]

# category → header file(s)
WAVES: dict[str, list[str]] = {
    # Wave A
    "init": ["SDL_init.h"],
    "error": ["SDL_error.h"],
    "hints": ["SDL_hints.h"],
    "properties": ["SDL_properties.h"],
    "log": ["SDL_log.h"],
    "assert": ["SDL_assert.h"],
    "version": ["SDL_version.h"],
    "stdinc": ["SDL_stdinc.h"],  # selective — filtered below
    # Wave B
    "video": ["SDL_video.h"],
    "render": ["SDL_render.h"],
    "pixels": ["SDL_pixels.h"],
    "blendmode": ["SDL_blendmode.h"],
    "rect": ["SDL_rect.h"],
    "surface": ["SDL_surface.h"],
    "clipboard": ["SDL_clipboard.h"],
    "vulkan": ["SDL_vulkan.h"],
    "metal": ["SDL_metal.h"],
    "camera": ["SDL_camera.h"],
    # Wave C
    "events": ["SDL_events.h"],
    "keyboard": ["SDL_keyboard.h"],
    "keycode": ["SDL_keycode.h"],
    "scancode": ["SDL_scancode.h"],
    "mouse": ["SDL_mouse.h"],
    "joystick": ["SDL_joystick.h"],
    "gamepad": ["SDL_gamepad.h"],
    "touch": ["SDL_touch.h"],
    "pen": ["SDL_pen.h"],
    "sensor": ["SDL_sensor.h"],
    "hidapi": ["SDL_hidapi.h"],
    # Wave D–K
    "haptic": ["SDL_haptic.h"],
    "audio": ["SDL_audio.h"],
    "gpu": ["SDL_gpu.h"],
    "thread": ["SDL_thread.h"],
    "mutex": ["SDL_mutex.h"],
    "atomic": ["SDL_atomic.h"],
    "timer": ["SDL_timer.h"],
    "time": ["SDL_time.h"],
    "filesystem": ["SDL_filesystem.h"],
    "storage": ["SDL_storage.h"],
    "iostream": ["SDL_iostream.h"],
    "asyncio": ["SDL_asyncio.h"],
    "platform": ["SDL_platform.h"],
    "cpuinfo": ["SDL_cpuinfo.h"],
    "endian": ["SDL_endian.h"],
    "bits": ["SDL_bits.h"],
    "loadso": ["SDL_loadso.h"],
    "process": ["SDL_process.h"],
    "power": ["SDL_power.h"],
    "messagebox": ["SDL_messagebox.h"],
    "dialog": ["SDL_dialog.h"],
    "tray": ["SDL_tray.h"],
    "locale": ["SDL_locale.h"],
    "system": ["SDL_system.h"],
    "guid": ["SDL_guid.h"],
    "misc": ["SDL_misc.h"],
    "main": ["SDL_main.h"],
    # Thin GL/EGL bridge (not glext dump)
    "opengl": ["SDL_video.h"],  # only GL-related from video; real bridge below
    "egl": ["SDL_egl.h"],
}

# Selective stdinc: only these symbols (types helpers used across bindings)
STDINC_ALLOW = {
    "SDL_malloc",
    "SDL_calloc",
    "SDL_realloc",
    "SDL_free",
    "SDL_aligned_alloc",
    "SDL_aligned_free",
    "SDL_GetNumAllocations",
    "SDL_getenv",
    "SDL_setenv",
    "SDL_unsetenv",
    "SDL_memcpy",
    "SDL_memmove",
    "SDL_memset",
    "SDL_memcmp",
    "SDL_strlen",
    "SDL_strnlen",
    "SDL_strlcpy",
    "SDL_strlcat",
    "SDL_strdup",
    "SDL_strndup",
    "SDL_atoi",
    "SDL_atof",
    "SDL_strcmp",
    "SDL_strncmp",
    "SDL_strcasecmp",
    "SDL_strncasecmp",
    "SDL_strchr",
    "SDL_strrchr",
    "SDL_strstr",
    "SDL_utf8strlen",
    "SDL_utf8strnlen",
    "SDL_wcslen",
    "SDL_wcsnlen",
    "SDL_abs",
    "SDL_min",
    "SDL_max",
    "SDL_clamp",
    "SDL_isalpha",
    "SDL_isalnum",
    "SDL_isdigit",
    "SDL_isspace",
    "SDL_toupper",
    "SDL_tolower",
    "SDL_crc16",
    "SDL_crc32",
    "SDL_murmur3_32",
    "SDL_rand",
    "SDL_rand_bits",
    "SDL_randf",
    "SDL_srand",
    "SDL_rand_r",
    "SDL_randf_r",
    "SDL_rand_bits_r",
    "SDL_iconv_string",
}

# Opaque types commonly referenced — declared once in owning category
OPAQUES: dict[str, str] = {
    "SDL_Window": "video",
    "SDL_Renderer": "video",  # forward in video; render uses video's
    "SDL_Texture": "render",
    "SDL_Surface": "surface",
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
    "SDL_AudioStream": "audio",
    "SDL_hid_device": "hidapi",
    "SDL_SharedObject": "loadso",
    "SDL_Process": "process",
    "SDL_Storage": "storage",
    "SDL_IOStream": "iostream",
    "SDL_AsyncIO": "asyncio",
    "SDL_AsyncIOQueue": "asyncio",
    "SDL_Tray": "tray",
    "SDL_TrayMenu": "tray",
    "SDL_TrayEntry": "tray",
    "SDL_MetalView": "metal",
}

FRICTION: list[str] = []

# Return type must not span `;` or newlines before SDLCALL (keeps one decl per match).
DECL_RE = re.compile(
    r"extern\s+SDL_DECLSPEC\s+([^\n;]+?)\s+SDLCALL\s+(SDL_\w+)\s*\(([^;]*?)\)\s*(?:SDL_[A-Z0-9_]+\([^)]*\))?\s*;",
    re.S,
)

# Strip attributes / annotations from C types
ATTR_RE = re.compile(
    r"\b(?:SDL_PRINTF_FORMAT_STRING|SDL_SCANF_FORMAT_STRING|SDL_MALLOC|SDL_ALLOC_SIZE\([^)]*\)|"
    r"SDL_ALLOC_SIZE2\([^)]*\)|SDL_INOUT_Z_CAP\([^)]*\)|SDL_OUT_Z_CAP\([^)]*\)|"
    r"SDL_IN_BYTECAP\([^)]*\)|SDL_INOUT_BYTECAP\([^)]*\)|SDL_OUT_BYTECAP\([^)]*\)|"
    r"SDL_OUT_CAP\([^)]*\)|SDL_INOUT_CAP\([^)]*\)|SDL_IN_CAP\([^)]*\)|"
    r"SDL_ACQUIRE\([^)]*\)|SDL_RELEASE\([^)]*\)|SDL_ACQUIRE_SHARED\([^)]*\)|"
    r"SDL_RELEASE_SHARED\([^)]*\)|SDL_RELEASE_GENERIC\([^)]*\)|"
    r"SDL_TRY_ACQUIRE\([^)]*\)|SDL_TRY_ACQUIRE_SHARED\([^)]*\)|"
    r"SDL_NO_THREAD_SAFETY_ANALYSIS|SDL_ANALYZER_NORETURN|SDL_DECLSPEC|"
    r"SDL_PRINTF_VARARG_FUNC\([^)]*\)|SDL_PRINTF_VARARG_FUNCV\([^)]*\)|"
    r"SDL_SCANF_VARARG_FUNC\([^)]*\)|SDL_SCANF_VARARG_FUNCV\([^)]*\)|"
    r"_Nonnull|_Nullable|_Null_unspecified)\b"
)


def clean_c(s: str) -> str:
    s = ATTR_RE.sub("", s)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def split_params(param_str: str) -> list[str]:
    param_str = clean_c(param_str)
    if not param_str or param_str == "void":
        return []
    parts: list[str] = []
    depth = 0
    cur = []
    for ch in param_str:
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
    return parts


def is_fn_ptr(p: str) -> bool:
    # Real callbacks look like: void (*cb)(int) or SDL_Foo (SDLCALL *cb)(…)
    if re.search(r"\(\\s*\*|\(\s*[\w\s]*\*|\*\)\s*\(", p):
        return True
    if "SDLCALL" in p and "(" in p:
        return True
    return False


def map_type_root(ctype: str, name_hint: str = "") -> str | None:
    """Map C type to Jog root type. None = unexpressible."""
    t = clean_c(ctype)
    t = t.replace("struct ", "").replace("enum ", "").replace("const const", "const")

    # function pointer
    if is_fn_ptr(t) or "(*)" in t.replace(" ", ""):
        return None

    if t == "va_list" or "va_list" in t:
        return None

    # pointers
    const = False
    while True:
        if t.startswith("const "):
            const = True
            t = t[6:].strip()
            continue
        break

    # trailing const / volatile
    t = re.sub(r"\bconst\b", "", t).strip()
    t = re.sub(r"\bvolatile\b", "", t).strip()
    t = re.sub(r"\s+", " ", t).strip()

    stars = 0
    while t.endswith("*"):
        stars += 1
        t = t[:-1].strip()
        if t.endswith("const"):
            const = True
            t = t[: -len("const")].strip()

    # base map
    base_map = {
        "void": "void",
        "bool": "bool",
        "char": "c.char",
        "unsigned char": "u8",
        "short": "c.short",
        "unsigned short": "c.ushort",
        "int": "c.int",
        "unsigned int": "c.uint",
        "unsigned": "c.uint",
        "long": "c.long",
        "unsigned long": "c.ulong",
        "long long": "c.longlong",
        "float": "f32",
        "double": "f64",
        "size_t": "c.size_t",
        "uintptr_t": "usize",
        "intptr_t": "isize",
        "Uint8": "u8",
        "Uint16": "u16",
        "Uint32": "u32",
        "Uint64": "u64",
        "Sint8": "i8",
        "Sint16": "i16",
        "Sint32": "i32",
        "Sint64": "i64",
        "SDL_PropertiesID": "u32",
        "SDL_TimerID": "u32",
        "SDL_DisplayID": "u32",
        "SDL_WindowID": "u32",
        "SDL_JoystickID": "u32",
        "SDL_KeyboardID": "u32",
        "SDL_MouseID": "u32",
        "SDL_TouchID": "u64",
        "SDL_FingerID": "u64",
        "SDL_SensorID": "u32",
        "SDL_AudioDeviceID": "u32",
        "SDL_CameraID": "u32",
        "SDL_HapticID": "u32",
        "SDL_PenID": "u32",
        "SDL_ThreadID": "u64",
        "SDL_Keycode": "u32",
        "SDL_Keymod": "u16",
        "SDL_Scancode": "u32",
        "SDL_PixelFormat": "u32",
        "SDL_Colorspace": "u32",
        "SDL_ScaleMode": "u32",
        "SDL_FlipMode": "u32",
        "SDL_BlendMode": "u32",
        "SDL_BlendFactor": "u32",
        "SDL_BlendOperation": "u32",
        "SDL_InitFlags": "u32",
        "SDL_WindowFlags": "u64",
        "SDL_RendererFlags": "u32",
        "SDL_EventType": "u32",
        "SDL_JoystickType": "u32",
        "SDL_GamepadType": "u32",
        "SDL_GamepadButton": "u32",
        "SDL_GamepadAxis": "u32",
        "SDL_PowerState": "u32",
        "SDL_DateFormat": "u32",
        "SDL_TimeFormat": "u32",
        "SDL_Folder": "u32",
        "SDL_PathType": "u32",
        "SDL_EnumerationResult": "u32",
        "SDL_GPUShaderFormat": "u32",
        "SDL_GPUTextureFormat": "u32",
        "SDL_GPUTextureType": "u32",
        "SDL_GPUSampleCount": "u32",
        "SDL_GPUCubeMapFace": "u32",
        "SDL_Time": "i64",
        "SDL_EGLDisplay": "*void",
        "SDL_EGLConfig": "*void",
        "SDL_EGLSurface": "*void",
        "SDL_EGLAttrib": "isize",
        "SDL_EGLint": "c.int",
        "wchar_t": "c.wchar",
        "SDL_iconv_t": "*void",
        "SDL_AssertState": "u32",
        "SDL_AssertData": "SDL_AssertData",
        "SDL_LogPriority": "u32",
        "SDL_LogCategory": "c.int",
        "SDL_PropertyType": "u32",
        "SDL_CameraPosition": "u32",
        "SDL_SystemTheme": "u32",
        "SDL_DisplayOrientation": "u32",
        "SDL_FlashOperation": "u32",
        "SDL_GLAttr": "u32",
        "SDL_GLProfile": "u32",
        "SDL_GLContextFlag": "u32",
        "SDL_GLContextReleaseFlag": "u32",
        "SDL_GLContextResetNotification": "u32",
        "SDL_HitTestResult": "u32",
        "SDL_MessageBoxFlags": "u32",
        "SDL_MessageBoxColorType": "u32",
        "SDL_MessageBoxButtonFlags": "u32",
        "SDL_FileDialogType": "u32",
        "SDL_ProcessIO": "u32",
        "SDL_IOStatus": "u32",
        "SDL_IOWhence": "u32",
        "SDL_AsyncIOResult": "u32",
        "SDL_AsyncIOTaskType": "u32",
        "SDL_ThreadPriority": "u32",
        "SDL_ThreadState": "u32",
        "SDL_MutexAccess": "u32",
        "SDL_AudioFormat": "u32",
        "SDL_EventAction": "u32",
        "SDL_MouseWheelDirection": "u32",
        "SDL_PenAxis": "u32",
        "SDL_hid_bus_type": "u32",
        "SDL_HapticEffectType": "u16",
        "SDL_HapticDirectionType": "u8",
        "SDL_TextureAccess": "c.int",
        "SDL_TextureAddressMode": "u32",
        "SDL_RendererLogicalPresentation": "u32",
        "SDL_GPUPresentMode": "u32",
        "SDL_GPUSwapchainComposition": "u32",
        "SDL_GPULoadOp": "u32",
        "SDL_GPUStoreOp": "u32",
        "SDL_GPUIndexElementSize": "u32",
        "SDL_GPUPrimitiveType": "u32",
        "SDL_GPUFillMode": "u32",
        "SDL_GPUCullMode": "u32",
        "SDL_GPUFrontFace": "u32",
        "SDL_GPUCompareOp": "u32",
        "SDL_GPUStencilOp": "u32",
        "SDL_GPUBlendOp": "u32",
        "SDL_GPUBlendFactor": "u32",
        "SDL_GPUVertexElementFormat": "u32",
        "SDL_GPUVertexInputRate": "u32",
        "SDL_GPUFilter": "u32",
        "SDL_GPUSamplerMipmapMode": "u32",
        "SDL_GPUSamplerAddressMode": "u32",
        "SDL_GPUTextureUsageFlags": "u32",
        "SDL_GPUBufferUsageFlags": "u32",
        "SDL_GPUColorComponentFlags": "u8",
        "SDL_GPUShaderStage": "u32",
        "SDL_SurfaceFlags": "u32",
        "SDL_AppResult": "u32",
        "SDL_Sandbox": "u32",
        "SDL_DateTime": "SDL_DateTime",
        "SDL_GUID": "SDL_GUID",
        "SDL_Point": "SDL_Point",
        "SDL_FPoint": "SDL_FPoint",
        "SDL_Rect": "SDL_Rect",
        "SDL_FRect": "SDL_FRect",
        "SDL_Color": "SDL_Color",
        "SDL_FColor": "SDL_FColor",
        "SDL_Palette": "SDL_Palette",
        "SDL_PixelFormatDetails": "SDL_PixelFormatDetails",
        "SDL_Finger": "SDL_Finger",
        "SDL_PathInfo": "SDL_PathInfo",
        "SDL_Locale": "SDL_Locale",
        "SDL_MessageBoxData": "SDL_MessageBoxData",
        "SDL_MessageBoxButtonData": "SDL_MessageBoxButtonData",
        "SDL_MessageBoxColor": "SDL_MessageBoxColor",
        "SDL_MessageBoxColorScheme": "SDL_MessageBoxColorScheme",
        "SDL_DialogFileFilter": "SDL_DialogFileFilter",
        "SDL_HapticEffect": "SDL_HapticEffect",
        "SDL_HapticDirection": "SDL_HapticDirection",
        "SDL_AudioSpec": "SDL_AudioSpec",
        "SDL_StorageInterface": "SDL_StorageInterface",
        "SDL_IOStreamInterface": "SDL_IOStreamInterface",
        "SDL_VirtualJoystickDesc": "SDL_VirtualJoystickDesc",
        "SDL_CameraSpec": "SDL_CameraSpec",
        "SDL_hid_device_info": "SDL_hid_device_info",
        "SDL_Event": "SDL_Event",
        "SDL_version": "SDL_version",
        "SDL_DisplayMode": "SDL_DisplayMode",
        "SDL_Vertex": "SDL_Vertex",
        "SDL_Texture": "SDL_Texture",
        "SDL_Surface": "SDL_Surface",
        "SDL_Camera": "SDL_Camera",
        "SDL_GLContext": "*void",
        "SDL_EGLContext": "*void",
        "SDL_FunctionPointer": "*void",
        "SDL_glob": "*void",
    }

    if t.endswith("Callback") or t.endswith("Function") or t.endswith("Predicate") or t.endswith("Handler"):
        # Function-pointer typedef — use *void (callers cast) or skip at param level.
        base = "*void" if stars == 0 else "void"
        # handled below via stars; force pointer
        if stars == 0:
            return "*void"
    if t in OPAQUES or t in ("SDL_Window", "SDL_Renderer"):
        base = t
    elif t in base_map:
        base = base_map[t]
    elif t.endswith("_t") and t.startswith("SDL_"):
        base = "u32"
    elif t.startswith("SDL_") and stars >= 1:
        # Prefer named opaque when we declare it; otherwise *void.
        if t in OPAQUES or t in ("SDL_Window", "SDL_Renderer", "SDL_Texture", "SDL_Surface",
                                   "SDL_Event", "SDL_Rect", "SDL_FRect", "SDL_Point", "SDL_FPoint",
                                   "SDL_Color", "SDL_FColor", "SDL_AudioSpec", "SDL_GUID",
                                   "SDL_version", "SDL_DisplayMode", "SDL_Palette"):
            base = t
        else:
            base = "void"
    elif t.startswith("SDL_") and stars == 0:
        # By-value unknown struct — skip (needs layout)
        FRICTION.append(f"by-value struct '{t}'")
        return None
    else:
        FRICTION.append(f"unknown type '{ctype}'")
        return None

    if base == "void" and stars == 0:
        return "void" if name_hint == "ret" else None

    out = base
    for i in range(stars):
        if i == stars - 1 and const and stars >= 1:
            out = f"*const {out}"
        else:
            # outermost pointer on returns of opaque often nullable — leave non-optional;
            # callers use ?* via wrappers. Keep *T for FFI parity with existing JogSDL.
            if const and i == 0 and stars == 1:
                out = f"*const {out}"
            else:
                out = f"*{out}"
    # Fix double application for single const pointer
    if stars == 1 and const and not out.startswith("*const "):
        out = f"*const {base}"
    elif stars == 1 and not const:
        out = f"*{base}"
    elif stars == 2:
        out = f"**{base}" if not const else f"**const {base}"
        # simplify: **T
        out = f"**{base}"
    elif stars >= 3:
        out = "*" * stars + base

    # Rebuild more carefully
    out = base
    if stars == 0:
        return out if out != "void" or name_hint == "ret" else "void"
    if stars == 1:
        return f"*const {base}" if const else f"*{base}"
    if stars == 2:
        return f"**{base}"
    return ("*" * stars) + base


def map_type_v2(ctype: str, name_hint: str = "") -> str | None:
    """v2 uses *byte for pointers and i32 for bool."""
    t = clean_c(ctype)
    if is_fn_ptr(t) or "va_list" in t:
        return None
    t = ATTR_RE.sub("", t)
    t = t.replace("struct ", "").replace("enum ", "")
    const = "const" in t
    t = re.sub(r"\bconst\b", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    stars = 0
    while t.endswith("*"):
        stars += 1
        t = t[:-1].strip()
    if t == "void" and stars == 0:
        return "void" if name_hint == "ret" else None
    if t == "bool":
        base = "i32"
    elif t in ("float",):
        base = "f32"
    elif t in ("double",):
        base = "f64"
    elif t in ("Uint8", "unsigned char"):
        base = "u8"
    elif t in ("Uint16",):
        base = "u16"
    elif t in ("Uint32", "SDL_PropertiesID", "SDL_InitFlags", "SDL_PixelFormat",
               "SDL_BlendMode", "SDL_EventType", "SDL_Keycode", "SDL_Scancode",
               "SDL_WindowID", "SDL_DisplayID", "SDL_JoystickID", "SDL_MouseID",
               "SDL_KeyboardID", "SDL_SensorID", "SDL_AudioDeviceID", "SDL_CameraID",
               "SDL_HapticID", "SDL_PenID", "SDL_TimerID", "SDL_Colorspace"):
        base = "u32"
    elif t in ("Uint64", "SDL_TouchID", "SDL_FingerID", "SDL_ThreadID", "SDL_WindowFlags"):
        base = "u64"
    elif t in ("Sint8",):
        base = "i8"
    elif t in ("Sint16", "SDL_Keymod"):
        base = "i16" if t != "SDL_Keymod" else "u16"
    elif t in ("Sint32", "int"):
        base = "i32"
    elif t in ("Sint64", "SDL_Time"):
        base = "i64"
    elif t in ("size_t",):
        base = "u64"
    elif t in ("char",):
        base = "byte"
    else:
        # any SDL struct / opaque → *byte when pointed, else skip value structs as *byte out-params only
        if stars == 0 and t.startswith("SDL_"):
            # pass-by-value structs — skip for v2 flat *byte style (Friction)
            FRICTION.append(f"v2 skip by-value struct {t}")
            return None
        base = "byte"

    if stars == 0:
        if base == "byte":
            return "u8"
        return base
    if stars == 1:
        return "*byte"
    if stars == 2:
        return "**byte"
    return "*" * stars + "byte"


def parse_param(p: str, v2: bool) -> tuple[str, str] | None:
    p = clean_c(p)
    if not p or p == "void":
        return None
    if p.strip() == "...":
        return ("...", "...")
    # Strip SAL / thread-safety attributes that confuse fn-ptr detection.
    p = ATTR_RE.sub("", p)
    p = re.sub(r"\s+", " ", p).strip()
    if is_fn_ptr(p):
        FRICTION.append(f"callback param: {p}")
        return None
    # name is last identifier; allow `char *title` (no space before name)
    m = re.match(r"^(.*?)(?:\s*\*+\s*|\s+)(\w+)$", p)
    if not m:
        # unnamed param e.g. `int` or `int *`
        stars = 0
        t = p
        while t.endswith("*"):
            stars += 1
            t = t[:-1].strip()
        ctype = t + ("*" * stars)
        name = "arg"
    else:
        left, name = m.group(1).strip(), m.group(2)
        # How many * between left and name?
        star_part = p[len(m.group(1)) : p.rfind(name)]
        stars = star_part.count("*")
        ctype = left + ("*" * stars)
    if name in ("type", "import", "export", "fn", "struct", "interface"):
        name = name + "_"
    mapper = map_type_v2 if v2 else map_type_root
    jt = mapper(ctype)
    if jt is None:
        return None
    return (name, jt)


def parse_functions(header_text: str, category: str) -> tuple[list[dict], list[str]]:
    skipped = []
    fns = []
    for m in DECL_RE.finditer(header_text):
        ret_c, name, params_c = m.group(1), m.group(2), m.group(3)
        if category == "stdinc" and name not in STDINC_ALLOW:
            continue
        # opengl category: only GL* window funcs from video — handled separately
        fns.append({"ret": clean_c(ret_c), "name": name, "params": params_c})
    return fns, skipped


def emit_fn_root(fn: dict) -> str | None:
    ret = map_type_root(fn["ret"], "ret")
    if ret is None:
        FRICTION.append(f"skip {fn['name']}: bad return {fn['ret']}")
        return None
    params = split_params(fn["params"])
    jog_params = []
    for i, p in enumerate(params):
        if p.strip() == "...":
            jog_params.append("...")
            continue
        parsed = parse_param(p, v2=False)
        if parsed is None:
            FRICTION.append(f"skip {fn['name']}: bad param {p}")
            return None
        pname, ptype = parsed
        if pname == "...":
            jog_params.append("...")
        else:
            if pname == "arg":
                pname = f"arg{i}"
            jog_params.append(f"{pname}: {ptype}")
    ret_s = "" if ret == "void" else f": {ret}"
    return f"    fn {fn['name']}({', '.join(jog_params)}){ret_s}"


def emit_fn_v2(fn: dict) -> str | None:
    ret = map_type_v2(fn["ret"], "ret")
    if ret is None:
        FRICTION.append(f"v2 skip {fn['name']}: bad return {fn['ret']}")
        return None
    params = split_params(fn["params"])
    jog_params = []
    for i, p in enumerate(params):
        if p.strip() == "...":
            # v2 may not support variadic well — skip
            FRICTION.append(f"v2 skip variadic {fn['name']}")
            return None
        parsed = parse_param(p, v2=True)
        if parsed is None:
            FRICTION.append(f"v2 skip {fn['name']}: bad param {p}")
            return None
        pname, ptype = parsed
        if pname == "arg":
            pname = f"arg{i}"
        jog_params.append(f"{pname}: {ptype}")
    ret_s = "" if ret == "void" else f": {ret}"
    return f"    fn {fn['name']}({', '.join(jog_params)}){ret_s}"


OPAQUE_BLOCK = {
    "video": ["SDL_Window", "SDL_Renderer"],
    "render": ["SDL_Texture"],
    "surface": ["SDL_Surface"],
    "gpu": [
        "SDL_GPUDevice", "SDL_GPUBuffer", "SDL_GPUTransferBuffer", "SDL_GPUTexture",
        "SDL_GPUSampler", "SDL_GPUShader", "SDL_GPUComputePipeline",
        "SDL_GPUGraphicsPipeline", "SDL_GPUCommandBuffer", "SDL_GPURenderPass",
        "SDL_GPUComputePass", "SDL_GPUCopyPass", "SDL_GPUFence",
    ],
    "joystick": ["SDL_Joystick"],
    "gamepad": ["SDL_Gamepad"],
    "haptic": ["SDL_Haptic"],
    "sensor": ["SDL_Sensor"],
    "camera": ["SDL_Camera"],
    "mouse": ["SDL_Cursor"],
    "mutex": ["SDL_Mutex", "SDL_RWLock", "SDL_Semaphore", "SDL_Condition", "SDL_InitState"],
    "thread": ["SDL_Thread"],
    "audio": ["SDL_AudioStream"],
    "hidapi": ["SDL_hid_device"],
    "loadso": ["SDL_SharedObject"],
    "process": ["SDL_Process"],
    "storage": ["SDL_Storage"],
    "iostream": ["SDL_IOStream"],
    "asyncio": ["SDL_AsyncIO", "SDL_AsyncIOQueue"],
    "tray": ["SDL_Tray", "SDL_TrayMenu", "SDL_TrayEntry"],
    "metal": ["SDL_MetalView"],
}


def write_category(cat: str, headers: list[Path], out_root: Path, out_v2: Path) -> tuple[int, int]:
    texts = []
    for h in headers:
        if not h.exists():
            print(f"missing header {h}", file=sys.stderr)
            continue
        texts.append(h.read_text(errors="replace"))
    blob = "\n".join(texts)
    fns, _ = parse_functions(blob, cat)

    root_lines = []
    v2_lines = []
    for fn in fns:
        r = emit_fn_root(fn)
        if r:
            root_lines.append(r)
        v = emit_fn_v2(fn)
        if v:
            v2_lines.append(v)

    # Dedup by function name (keep first)
    def dedup(lines: list[str]) -> list[str]:
        seen = set()
        out = []
        for ln in lines:
            m = re.search(r"fn (SDL_\w+)\(", ln)
            if not m:
                continue
            if m.group(1) in seen:
                continue
            seen.add(m.group(1))
            out.append(ln)
        return out

    root_lines = dedup(root_lines)
    v2_lines = dedup(v2_lines)

    opaques = OPAQUE_BLOCK.get(cat, [])
    opaque_src = "\n".join(f"@opaque struct {o}" for o in opaques)

    needs_c = any("c." in ln for ln in root_lines)
    imports = []
    if needs_c:
        imports.append("import std.c")
    # Cross-imports for common deps
    if cat == "render":
        imports.append("import sdl3.video")
        imports.append("import sdl3.rect")
    if cat in ("surface", "clipboard", "camera"):
        if cat == "surface":
            imports.append("import sdl3.rect")
            imports.append("import sdl3.pixels")
    if cat == "mouse":
        imports.append("import sdl3.video")
    if cat == "events":
        pass

    import_block = ("\n".join(imports) + "\n\n") if imports else "\n"

    root_body = f"""// Raw SDL3 {cat} — generated from headers; hand-maintain.
// Unexported — apps use jog_sdl.sdl*.
{import_block}{opaque_src + chr(10) + chr(10) if opaque_src else ""}@link("SDL3")
extern {{
{chr(10).join(root_lines)}
}}
"""
    # Fix render to use video.SDL_Window / video.SDL_Renderer
    if cat == "render":
        root_body = root_body.replace("*SDL_Window", "*video.SDL_Window")
        root_body = root_body.replace("*SDL_Renderer", "*video.SDL_Renderer")
        root_body = root_body.replace("*SDL_FRect", "*rect.SDL_FRect")
        root_body = root_body.replace("*SDL_Rect", "*rect.SDL_Rect")
        # don't double-prefix
        root_body = root_body.replace("*video.video.", "*video.")
        root_body = root_body.replace("*rect.rect.", "*rect.")

    v2_body = f"""// Raw SDL3 {cat} — v2 flat merge (generated).
@link("SDL3")
extern {{
{chr(10).join(v2_lines)}
}}
"""

    out_root.parent.mkdir(parents=True, exist_ok=True)
    out_v2.parent.mkdir(parents=True, exist_ok=True)
    out_root.write_text(root_body)
    out_v2.write_text(v2_body)
    return len(root_lines), len(v2_lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--headers", type=Path, default=HDR_DIR_DEFAULT)
    ap.add_argument("--only", nargs="*", help="Only these categories")
    ap.add_argument("--friction-out", type=Path, default=ROOT / "scripts" / "gen_friction.txt")
    args = ap.parse_args()

    cats = args.only or [c for c in WAVES if c not in ("opengl", "egl")]
    # Add thin GL bridge categories manually after

    total_r = total_v = 0
    for cat in cats:
        headers = [args.headers / h for h in WAVES[cat]]
        n_r, n_v = write_category(
            cat,
            headers,
            ROOT / "sdl3" / cat / f"{cat}.jog",
            ROOT / "v2" / "sdl3" / cat / f"{cat}.jog",
        )
        print(f"{cat}: root={n_r} v2={n_v}")
        total_r += n_r
        total_v += n_v

    # Thin GL/EGL bridge: extract only SDL_GL_* and SDL_EGL* from video + egl
    # (already mostly in video generation). Write egl stubs if header is passthrough.
    egl_h = args.headers / "SDL_egl.h"
    if egl_h.exists() and (not args.only or "egl" in args.only):
        # SDL_egl.h is mostly Khronos — bind only SDL_ prefixed if any
        text = egl_h.read_text(errors="replace")
        fns, _ = parse_functions(text, "egl")
        # usually none with SDL_ prefix in egl.h — video has SDL_EGL_*
        print(f"egl header SDL_ decls: {len(fns)}")

    args.friction_out.write_text("\n".join(sorted(set(FRICTION))) + "\n")
    print(f"TOTAL root={total_r} v2={total_v} friction_lines={len(set(FRICTION))}")
    print(f"friction → {args.friction_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
