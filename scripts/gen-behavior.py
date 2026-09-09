"""Fill packages/ui and packages/blocks with native .cronus behavior."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\Hadouken Game Center\Desktop\cooud\cronus-ui")
UI_SRC = SRC / "packages" / "ui" / "src" / "components"
REG = SRC / "registry"

OVERLAY = {
    "dialog", "alert-dialog", "sheet", "drawer", "popover", "hover-card",
    "dropdown-menu", "context-menu", "menubar", "command", "combobox",
    "tooltip", "lightbox", "invite-dialog", "confirmation-dialog",
    "morphing-popover", "navigation-menu",
}
TOGGLE = {
    "checkbox", "switch", "toggle", "radio-group", "toggle-group",
}
INPUTS = {
    "input", "textarea", "select", "slider", "input-otp", "password-input",
    "number-input", "tags-input", "phone-input", "currency-input",
    "credit-card-input", "date-picker", "date-range-picker", "time-picker",
    "color-picker", "file-dropzone", "floating-label-input", "multi-select",
    "autocomplete", "combobox",
}
TABS = {
    "tabs", "accordion", "collapsible", "stepper", "expandable-tabs",
    "segmented-control",
}
NAV = {
    "sidebar", "breadcrumb", "pagination", "pill-nav", "toolbar",
    "app-shell", "navigation-menu",
}
DATA = {
    "table", "data-table", "tree-view", "json-viewer", "kanban",
    "timeline", "calendar", "scheduler",
}


def ident(name: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in name.replace("_", "-").split("-") if p)


def layout_for(name: str) -> str:
    if name in OVERLAY:
        return "overlay"
    if name in TABS or name in NAV or name in DATA or name.endswith("-chart") or name in {
        "card", "form", "field", "empty", "banner", "chart", "carousel",
    }:
        return "stack"
    return "inline"


def brace_block(src: str, start: int) -> tuple[str, int]:
    i = src.find("{", start)
    if i < 0:
        return "", start
    depth = 0
    j = i
    while j < len(src):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i + 1 : j], j + 1
        j += 1
    return src[i + 1 :], len(src)


def extract_variants(src: str) -> dict[str, list[str]]:
    m = re.search(r"variants\s*:\s*\{", src)
    if not m:
        return {}
    block, _ = brace_block(src, m.start())
    out: dict[str, list[str]] = {}
    i = 0
    while True:
        km = re.search(r"(?:^|\n)\s*(?:\"([^\"]+)\"|([A-Za-z_][\w-]*))\s*:\s*\{", block[i:])
        if not km:
            break
        key = km.group(1) or km.group(2)
        inner, end = brace_block(block[i:], km.start())
        keys = [am.group(1) or am.group(2) for am in re.finditer(
            r"(?:^|\n)\s*(?:\"([^\"]+)\"|([A-Za-z_][\w-]*))\s*:", inner
        )]
        if keys:
            out[key] = keys
        i += end
    return out


def extract_defaults(src: str) -> dict[str, str]:
    m = re.search(r"defaultVariants\s*:\s*\{([^}]+)\}", src)
    if not m:
        return {}
    return {k: v for k, v in re.findall(r"([A-Za-z_][\w-]*)\s*:\s*[\"']?([^,\"'\s}]+)", m.group(1))}


def extract_exports(src: str) -> list[str]:
    names: list[str] = []
    for m in re.finditer(r"export\s+(?:const|function|class|type|interface)\s+(\w+)", src):
        names.append(m.group(1))
    for m in re.finditer(r"export\s*\{([^}]+)\}", src):
        for part in m.group(1).split(","):
            raw = part.strip()
            if not raw or raw.startswith("type "):
                continue
            names.append(raw.split(" as ")[0].strip())
    seen: set[str] = set()
    out: list[str] = []
    for n in names:
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def extract_slots(src: str) -> list[str]:
    return sorted(set(re.findall(r'data-slot=["\']([^"\']+)["\']', src)))


def is_comp_export(name: str) -> bool:
    if not name or not name[0].isupper():
        return False
    return not name.endswith(("Props", "Variants", "Spring", "Option", "Point"))


def q(s: str) -> str:
    return '"' + s.replace("\\", "").replace('"', "")[:80] + '"'


def behavior_body(name: str, feat: str, variants: dict[str, list[str]], defaults: dict[str, str]) -> tuple[str, list[str]]:
    params = ["label: text", "disabled: boolean"]
    lines = [f'  label {q(feat)}']
    tests: list[str] = []

    if "variant" in variants:
        params.append("variant: text")
        lines.append(f'  variant {q(defaults.get("variant", variants["variant"][0]))}')
    if "size" in variants:
        params.append("size: text")
        lines.append(f'  size {q(defaults.get("size", variants["size"][0]))}')

    if name in TOGGLE:
        params.append("checked: boolean")
        lines.append("  state checked: boolean = false")
        lines.append("  action \"toggle\"")
        tests.append(f'  test "toggles {feat}" {{\n    click {q(feat)}\n  }}')
    elif name in OVERLAY:
        params.append("open: boolean")
        lines.append("  state open: boolean = false")
        lines.append("  title " + q(feat))
        lines.append("  action \"open\"")
        lines.append("  action \"close\"")
        tests.append(f'  test "opens {feat}" {{\n    click "open"\n    click "close"\n  }}')
    elif name in INPUTS:
        params.append("value: text")
        params.append("invalid: boolean")
        lines.append("  state value: text = \"\"")
        lines.append("  field " + q(feat))
        tests.append(f'  test "fills {feat}" {{\n    fill value "x"\n  }}')
    elif name in TABS:
        params.append("value: text")
        lines.append("  state value: text = \"one\"")
        lines.append("  tab \"one\"")
        lines.append("  tab \"two\"")
        lines.append("  tab \"three\"")
        tests.append(f'  test "switches {feat}" {{\n    click "two"\n  }}')
    elif name in NAV:
        lines.append("  item \"Home\" -> \"/\"")
        lines.append("  item \"Next\" -> \"/next\"")
        lines.append("  action \"navigate\"")
        tests.append(f'  test "navigates {feat}" {{\n    click "Home"\n  }}')
    elif name in DATA or name.endswith("-chart"):
        lines.append("  columns \"name, value, status\"")
        lines.append("  item \"Row\"")
        tests.append(f'  test "shows {feat}" {{\n    expect visible {q(feat)}\n  }}')
    else:
        lines.append("  action \"click\"")
        tests.append(f'  test "uses {feat}" {{\n    click {q(feat)}\n  }}')

    lines.append("  action \"focus\"")
    tests.append(f'  test "disabled {feat}" {{\n    expect visible {q(feat)}\n  }}')
    return ", ".join(params), lines + [""] + tests


def gen_ui() -> int:
    dst = ROOT / "packages" / "ui"
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    stems: list[str] = []
    for path in sorted(UI_SRC.glob("*.tsx")):
        name = path.stem
        if name.endswith(".test"):
            continue
        src = path.read_text(encoding="utf-8")
        feat = ident(name)
        variants = extract_variants(src)
        defaults = extract_defaults(src)
        exports = [e for e in extract_exports(src) if is_comp_export(e)]
        if feat not in exports:
            exports = [feat] + exports
        slots = extract_slots(src)
        params, body = behavior_body(name, feat, variants, defaults)
        comments = [
            f"## {feat}",
            f"## source: packages/ui/src/components/{name}.tsx",
            "## behavior: native component (state, items, tests). Kernel renders.",
        ]
        if exports:
            comments.append("## exports: " + ", ".join(exports))
        if slots:
            comments.append("## slots: " + ", ".join(slots))
        for vk, vv in variants.items():
            comments.append(f"## variants.{vk}: " + ", ".join(vv))
        blocks = [
            "\n".join(comments),
            "",
            f"component {feat}({params}) layout:{layout_for(name)} style:{name} {{",
            *body,
            "}",
        ]
        for extra in exports:
            if extra == feat:
                continue
            slug = re.sub(r"(?<!^)(?=[A-Z])", "-", extra).lower()
            blocks += [
                "",
                f"component {extra}(label: text, disabled: boolean) layout:inline style:{slug} {{",
                f"  label {q(extra)}",
                "  action \"click\"",
                "}",
            ]
        (dst / f"{name}.cronus").write_text("\n".join(blocks) + "\n", encoding="utf-8")
        stems.append(name)
        n += 1

    extra = [p.stem for p in dst.glob("*.cronus") if p.stem not in stems and p.stem != "index"]
    stems = sorted(set(stems + extra))
    (dst / "index.cronus").write_text(
        "## @cooud-cronus/ui catalog\n" + "\n".join(f"## {s}.cronus" for s in stems) + "\n",
        encoding="utf-8",
    )
    return n


TW = re.compile(
    r"^(flex|grid|inline|block|hidden|sr-only|size-|w-|h-|p-|m-|gap-|text-|bg-|border|"
    r"rounded|shadow|items-|justify-|font-|leading-|tracking-|opacity-|z-|inset|"
    r"absolute|relative|overflow|max-|min-|sm:|md:|lg:|xl:|hover:|focus|data-|aria-|"
    r"disabled:|placeholder:|file:|peer|group|from-|to-|via-|ring-|outline).*"
)


SKIP_COPY = {
    "true", "false", "react", "undefined", "null", "use client", "button",
    "submit", "email", "password", "text", "div", "span", "hidden",
}


def copy_strings(tsx: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for s in re.findall(r'"([^"\\]{3,70})"', tsx):
        if s in seen or s.lower() in SKIP_COPY:
            continue
        if any(ch in s for ch in "<>{}\\\n\r"):
            continue
        if TW.match(s) or re.search(r"(className|px-|py-|sm:|md:|lg:|bg-|text-|flex|gap-)", s):
            continue
        if s.endswith((".js", ".tsx", ".ts", ".css")) or s.startswith("@") or s.startswith("http"):
            continue
        letters = sum(c.isalpha() for c in s)
        if letters < 3:
            continue
        titled = bool(re.match(r"^[A-Z][A-Za-z0-9 +?.,'!/-]{2,69}$", s))
        sentence = " " in s and letters / max(len(s), 1) > 0.5
        if not (titled or sentence):
            continue
        seen.add(s)
        out.append(s)
        if len(out) >= 8:
            break
    return out


def block_kind(stem: str) -> str:
    if any(k in stem for k in ("login", "signup", "forgot-password", "otp", "magic-link", "auth")):
        return "auth"
    if any(k in stem for k in ("hero", "cta", "faq", "pricing", "footer", "navbar", "about",
                               "testimonial", "waitlist", "logo-cloud", "feature", "blog", "contact")):
        return "marketing"
    if any(k in stem for k in ("dashboard", "analytics", "stats", "usage", "chart", "kpi")):
        return "data"
    if any(k in stem for k in ("checkout", "cart", "billing", "invoice", "payment", "order")):
        return "commerce"
    if any(k in stem for k in ("empty", "error", "not-found", "maintenance", "success", "404")):
        return "empty"
    if any(k in stem for k in ("settings", "account", "profile", "team", "session", "security")):
        return "settings"
    return "card"


def gen_blocks() -> int:
    dst = ROOT / "packages" / "blocks"
    dst.mkdir(parents=True, exist_ok=True)
    skip = {"index", "meta", "cn"}
    n = 0
    for path in sorted(REG.glob("*.json")):
        stem = path.stem
        if stem in skip:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        feat = ident(stem)
        kind = block_kind(stem)
        title = " ".join(feat.replace("Block", "").split()) or feat
        title = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", title)
        parts = stem.split("--")
        subtitle = ident(parts[-1]).replace("-", " ") if len(parts) > 1 else title
        actions = {
            "auth": ["Sign in", "Sign up"],
            "marketing": ["Get started", "Learn more"],
            "data": ["View"],
            "commerce": ["Pay", "Continue"],
            "empty": ["Go home"],
            "settings": ["Save"],
            "card": [title],
        }[kind]
        deps = data.get("registryDependencies") or []
        comments = [
            f"## Block {feat}",
            f"## source: registry/{stem}.json",
            f"## type: {data.get('type', 'registry:block')}",
            f"## behavior: {kind}",
        ]
        if deps:
            comments.append("## registryDependencies: " + ", ".join(deps))

        body = [
            f"  title {q(title)}",
            f"  subtitle {q(subtitle)}",
        ]
        tests = []
        if kind == "auth":
            body += [
                "  state pending: boolean = false",
                "  field \"Email\"",
                "  field \"Password\"",
                f"  action {q(actions[0])}",
                "  link \"Forgot password?\" -> \"/forgot-password\"",
            ]
            tests.append('  test "submit auth" {\n    fill email "you@company.com"\n    click ' + q(actions[0]) + "\n  }")
        elif kind == "marketing":
            body += [f"  action {q(a)}" for a in actions[:3]]
            body.append("  cta " + q(actions[0]))
            tests.append("  test \"cta\" {\n    click " + q(actions[0]) + "\n  }")
        elif kind == "data":
            body += [
                "  columns \"name, value, status\"",
                "  item \"Row\"",
                "  value \"0\"",
            ]
            tests.append(f'  test "reads {feat}" {{\n    expect visible {q(title)}\n  }}')
        elif kind == "commerce":
            body += [
                "  field \"Card\"",
                "  value \"$0\"",
                f"  action {q(actions[0])}",
            ]
            tests.append("  test \"checkout\" {\n    click " + q(actions[0]) + "\n  }")
        elif kind == "empty":
            body.append("  action \"Go home\" -> \"/\"")
            tests.append('  test "empty" {\n    click "Go home"\n  }')
        elif kind == "settings":
            body += [
                "  field \"Name\"",
                "  action \"Save\"",
            ]
            tests.append('  test "save settings" {\n    click "Save"\n  }')
        else:
            body += [f"  action {q(a)}" for a in actions[:2]]
            tests.append("  test \"use block\" {\n    click " + q(actions[0]) + "\n  }")

        text = "\n".join(comments) + "\n\n"
        text += f"component {feat}Block(label: text) layout:stack style:{stem} {{\n"
        text += "\n".join(body) + "\n"
        text += "\n".join(tests) + "\n}\n"
        (dst / f"{stem}.cronus").write_text(text, encoding="utf-8")
        n += 1
    return n


def main() -> None:
    ui = gen_ui()
    blocks = gen_blocks()
    print("ui", ui)
    print("blocks", blocks)


if __name__ == "__main__":
    main()
