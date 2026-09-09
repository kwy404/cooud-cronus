"""Emit packages/tokens as live style {} the kernel generate_css_vars reads."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = Path(r"C:\Users\Hadouken Game Center\Desktop\cooud\cronus-ui\packages\tokens\styles\tokens.css")
DST = ROOT / "packages" / "tokens"

HEX = {
    ("aurora", "dark"): {
        "accent-hex": "#0ea5e9",
        "background": "#09090b",
        "surface": "#111113",
        "text": "#fafaf9",
        "text-muted": "#a1a1aa",
        "border": "rgba(255,255,255,0.10)",
    },
    ("aurora", "light"): {
        "accent-hex": "#0070a3",
        "background": "#ffffff",
        "surface": "#f4f4f5",
        "text": "#18181b",
        "text-muted": "#52525b",
        "border": "rgba(0,0,0,0.10)",
    },
    ("neutral", "light"): {
        "accent-hex": "#18181b",
        "background": "#fafafa",
        "surface": "#ffffff",
        "text": "#18181b",
        "text-muted": "#52525b",
        "border": "#e4e4e7",
    },
    ("neutral", "dark"): {
        "accent-hex": "#e4e4e7",
        "background": "#111111",
        "surface": "#191919",
        "text": "#f4f4f5",
        "text-muted": "#a1a1aa",
        "border": "rgba(255,255,255,0.10)",
    },
    ("midnight", "dark"): {
        "accent-hex": "#6158e4",
        "background": "#09090b",
        "surface": "#111113",
        "text": "#fafaf9",
        "text-muted": "#a1a1aa",
        "border": "rgba(255,255,255,0.10)",
    },
    ("midnight", "light"): {
        "accent-hex": "#5b51dc",
        "background": "#ffffff",
        "surface": "#f4f4f5",
        "text": "#18181b",
        "text-muted": "#52525b",
        "border": "rgba(0,0,0,0.10)",
    },
    ("sunset", "dark"): {
        "accent-hex": "#fc9f30",
        "background": "#09090b",
        "surface": "#111113",
        "text": "#fafaf9",
        "text-muted": "#a1a1aa",
        "border": "rgba(255,255,255,0.10)",
    },
    ("sunset", "light"): {
        "accent-hex": "#c2410c",
        "background": "#ffffff",
        "surface": "#f4f4f5",
        "text": "#18181b",
        "text-muted": "#52525b",
        "border": "rgba(0,0,0,0.10)",
    },
    ("emerald", "dark"): {
        "accent-hex": "#10b981",
        "background": "#09090b",
        "surface": "#111113",
        "text": "#fafaf9",
        "text-muted": "#a1a1aa",
        "border": "rgba(255,255,255,0.10)",
    },
    ("emerald", "light"): {
        "accent-hex": "#047857",
        "background": "#ffffff",
        "surface": "#f4f4f5",
        "text": "#18181b",
        "text-muted": "#52525b",
        "border": "rgba(0,0,0,0.10)",
    },
}


def brace_block(src: str, start: int) -> tuple[str, int]:
    i = src.find("{", start)
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


def css_vars(block: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r"--cronus-([a-z0-9-]+)\s*:\s*([^;]+);", block, re.S):
        out.append((m.group(1), " ".join(m.group(2).split())))
    return out


def emit(theme: str, mode: str, vars_: list[tuple[str, str]]) -> str:
    hexmap = HEX.get((theme, mode), HEX[("aurora", "dark")])
    lines = [
        f"## tokens {theme} {mode}",
        "## live style {} — kernel generate_css_vars reads these keys",
        "",
        "style {",
        f"  theme {mode}",
        f"  preset {theme}",
        f'  accent "{hexmap["accent-hex"]}"',
        '  font "Inter"',
        "  radius 14px",
        f'  accent-hex "{hexmap["accent-hex"]}"',
        f'  background "{hexmap["background"]}"',
        f'  surface "{hexmap["surface"]}"',
        f'  text "{hexmap["text"]}"',
        f'  text-muted "{hexmap["text-muted"]}"',
        f'  border "{hexmap["border"]}"',
    ]
    for k, v in vars_:
        key = k.replace("-", "")
        if key in {"primary", "ring", "success", "warning", "error", "info"}:
            lines.append(f'  {k} "{v}"')
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    css = CSS.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(\[data-cronus-theme="(\w+)"\](?:\[data-cronus-mode="(\w+)"\])?)\s*\{'
    )
    n = 0
    for m in pattern.finditer(css):
        theme = m.group(2)
        mode = m.group(3)
        block, _ = brace_block(css, m.start())
        vars_ = css_vars(block)
        if not vars_:
            continue
        if mode:
            stem = f"{theme}-{mode}"
            theme_kw = mode
        else:
            stem = theme
            theme_kw = "light" if theme == "neutral" else "dark"
        (DST / f"{stem}.cronus").write_text(emit(theme, theme_kw, vars_), encoding="utf-8")
        n += 1

    aurora = (DST / "aurora.cronus").read_text(encoding="utf-8")
    (DST / "tokens.cronus").write_text(
        "## @cooud-cronus/tokens default = aurora dark\n\n" + aurora,
        encoding="utf-8",
    )
    print("tokens", n)


if __name__ == "__main__":
    main()
