"""Regenerate packages/ from cronus-ui sources as native .cronus."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\Hadouken Game Center\Desktop\cooud\cronus-ui")
UI_SRC = SRC / "packages" / "ui" / "src" / "components"
REG = SRC / "registry"
TOKENS_CSS = SRC / "packages" / "tokens" / "styles" / "tokens.css"

OVERLAY = {
    "dialog",
    "alert-dialog",
    "sheet",
    "drawer",
    "popover",
    "hover-card",
    "dropdown-menu",
    "context-menu",
    "menubar",
    "command",
    "combobox",
    "tooltip",
    "lightbox",
    "invite-dialog",
    "confirmation-dialog",
    "morphing-popover",
    "navigation-menu",
}
STACK = {
    "card",
    "table",
    "data-table",
    "sidebar",
    "app-shell",
    "calendar",
    "form",
    "field",
    "kanban",
    "scheduler",
    "chart",
    "area-chart",
    "bar-chart",
    "line-chart",
    "pie-chart",
    "radar-chart",
    "heatmap",
    "heatmap-chart",
    "empty",
    "banner",
    "glass-card",
    "spotlight-card",
    "tilt-card",
    "flip-card",
    "carousel",
    "accordion",
    "tabs",
    "stepper",
    "timeline",
    "terminal",
    "json-viewer",
    "notification-center",
    "workspace-switcher",
    "video-player",
    "rich-text-editor",
}


def ident(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in name.replace("_", "-").split("-") if part)


def layout_for(name: str) -> str:
    if name in OVERLAY:
        return "overlay"
    if name in STACK or name.endswith("-chart"):
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
        keys = []
        for am in re.finditer(r"(?:^|\n)\s*(?:\"([^\"]+)\"|([A-Za-z_][\w-]*))\s*:", inner):
            keys.append(am.group(1) or am.group(2))
        if keys:
            out[key] = keys
        i += end
    return out


def extract_defaults(src: str) -> dict[str, str]:
    m = re.search(r"defaultVariants\s*:\s*\{([^}]+)\}", src)
    if not m:
        return {}
    found = re.findall(r"([A-Za-z_][\w-]*)\s*:\s*[\"']?([^,\"'\s}]+)", m.group(1))
    return {k: v for k, v in found}


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
    if name.endswith(("Props", "Variants", "Spring", "Option", "Point")):
        return False
    return True


def wave_map() -> dict[str, str]:
    index = (SRC / "packages" / "ui" / "src" / "index.ts").read_text(encoding="utf-8")
    current = "catalog"
    mapping: dict[str, str] = {}
    for line in index.splitlines():
        wm = re.search(r"Wave\s+(\d+)\s+[—-]\s+(.+?)\s+[─-]", line)
        if wm:
            current = f"wave {wm.group(1)} - {wm.group(2).strip()}"
            continue
        for m in re.finditer(r'from "./components/([a-z0-9-]+)\.js"', line):
            mapping[m.group(1)] = current
    return mapping


def gen_ui() -> int:
    dst = ROOT / "packages" / "ui"
    dst.mkdir(parents=True, exist_ok=True)
    waves = wave_map()
    stems: list[str] = []
    for path in sorted(UI_SRC.glob("*.tsx")):
        name = path.stem
        if name.endswith(".test"):
            continue
        src = path.read_text(encoding="utf-8")
        feat = ident(name)
        variants = extract_variants(src)
        defaults = extract_defaults(src)
        exports = extract_exports(src)
        slots = extract_slots(src)
        comps = [e for e in exports if is_comp_export(e)]
        if feat not in comps:
            comps = [feat] + comps
        params = ["label: text"]
        body_lines = [f'  label "{feat}"']
        if "variant" in variants:
            params.append("variant: text")
            body_lines.append(f'  variant "{defaults.get("variant", variants["variant"][0])}"')
        if "size" in variants:
            params.append("size: text")
            body_lines.append(f'  size "{defaults.get("size", variants["size"][0])}"')
        param_s = ", ".join(params)
        comments = [
            f"## {feat}",
            f"## source: packages/ui/src/components/{name}.tsx",
            f"## {waves.get(name, 'catalog')}",
        ]
        if comps:
            comments.append("## exports: " + ", ".join(comps))
        if slots:
            comments.append("## slots: " + ", ".join(slots))
        for vk, vv in variants.items():
            comments.append(f"## variants.{vk}: " + ", ".join(vv))
        if defaults:
            comments.append(
                "## defaults: " + " ".join(f"{k}={v}" for k, v in defaults.items())
            )
        blocks = [
            "\n".join(comments),
            "",
            f"component {feat}({param_s}) layout:{layout_for(name)} style:{name} {{",
            *body_lines,
            "}",
        ]
        for extra in comps:
            if extra == feat:
                continue
            slug = re.sub(r"(?<!^)(?=[A-Z])", "-", extra).lower()
            blocks += [
                "",
                f"component {extra}(label: text) layout:inline style:{slug} {{",
                f'  label "{extra}"',
                "}",
            ]
        (dst / f"{name}.cronus").write_text("\n".join(blocks) + "\n", encoding="utf-8")
        stems.append(name)

    for extra in dst.glob("*.cronus"):
        if extra.stem not in stems and extra.stem != "index":
            stems.append(extra.stem)
    stems = sorted(set(stems))

    imports = "\n".join(f'import "{n}.cronus"' for n in stems)
    (dst / "index.cronus").write_text(
        f"## @cooud-cronus/ui — {len(stems)} families from cronus-ui barrel\n\n{imports}\n",
        encoding="utf-8",
    )
    return len(stems)


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
        kind = data.get("type", "registry:block")
        deps = data.get("registryDependencies") or []
        npm = data.get("dependencies") or []
        feat = ident(stem)
        lines = [
            f"## Block {feat}",
            f"## source: registry/{stem}.json",
            f"## type: {kind}",
        ]
        if deps:
            lines.append("## registryDependencies: " + ", ".join(deps))
        if npm:
            lines.append("## npm: " + ", ".join(npm))
        lines += [
            "",
            f"component {feat}Block layout:stack style:{stem} {{",
            f'  label "{feat}"',
            "}",
            "",
        ]
        (dst / f"{stem}.cronus").write_text("\n".join(lines), encoding="utf-8")
        n += 1
    return n


def css_vars(block: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in re.finditer(r"--cronus-([a-z0-9-]+)\s*:\s*([^;]+);", block, re.S):
        val = " ".join(m.group(2).split())
        out.append((m.group(1), val))
    return out


def gen_tokens() -> int:
    dst = ROOT / "packages" / "tokens"
    dst.mkdir(parents=True, exist_ok=True)
    css = TOKENS_CSS.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(\[data-cronus-theme="(\w+)"\](?:\[data-cronus-mode="(\w+)"\])?)\s*\{',
    )
    files = 0
    index_imports: list[str] = []
    for m in pattern.finditer(css):
        theme = m.group(2)
        mode = m.group(3)
        block, _ = brace_block(css, m.start())
        vars_ = css_vars(block)
        if not vars_:
            continue
        if mode:
            stem = f"{theme}-{mode}"
            theme_kw = "dark" if mode == "dark" else "light"
        else:
            stem = theme
            theme_kw = "light" if theme == "neutral" else "dark"
        primary = next((v for k, v in vars_ if k == "primary"), "")
        accent = next((v for k, v in vars_ if k == "accent"), primary)
        comments = [
            f"## tokens {stem}",
            "## source: packages/tokens/styles/tokens.css",
        ]
        for k, v in vars_:
            comments.append(f"## --cronus-{k}: {v}")
        body = [
            "\n".join(comments),
            "",
            "style {",
            f"  theme {theme_kw}",
            f"  preset {theme}",
            '  accent white',
            '  font "Inter"',
            "}",
            "",
        ]
        fname = f"{stem}.cronus"
        (dst / fname).write_text("\n".join(body), encoding="utf-8")
        index_imports.append(f'import "{fname}"')
        files += 1

    (dst / "tokens.cronus").write_text(
        "\n".join(
            [
                "## @cooud-cronus/tokens",
                "## Semantic roles from cronus-ui packages/tokens.",
                "## presets: aurora, neutral, midnight, sunset, emerald × light/dark",
                "",
                "style {",
                "  theme dark",
                "  preset aurora",
                "  accent white",
                '  font "Inter"',
                "}",
                "",
                *index_imports,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return files + 1


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.lstrip("\n") if False else text, encoding="utf-8")


def gen_rest() -> None:
    write(
        ROOT / "packages" / "theme" / "theme.cronus",
        """## @cooud-cronus/theme
## Presets from @cronus-ui/theme + tokens. Runtime is cronus-kernel style {}, not React.

style {
  theme dark
  preset aurora
}

component ModeToggle layout:inline style:mode-toggle {
  label "Mode"
}

component ThemeAurora layout:stack style:aurora { label "aurora" }
component ThemeNeutral layout:stack style:neutral { label "neutral" }
component ThemeMidnight layout:stack style:midnight { label "midnight" }
component ThemeSunset layout:stack style:sunset { label "sunset" }
component ThemeEmerald layout:stack style:emerald { label "emerald" }
""",
    )

    write(
        ROOT / "packages" / "stack" / "stack.cronus",
        """## @cooud-cronus/stack
## Native stack builder. Runtime is cronus-kernel, not Next/npm.

app "Stack" {
  port 5175
  database sqlite "./stack.db"
  theme dark
}

style {
  theme dark
  accent white
  font "Inter"
}

page "/" {
  section hero {
    title "Cronus Stack"
    subtitle "Scaffold nativo .cronus"
  }

  section web {
    title "Web"
    item "cronus-kernel" icon:layers
    item "none" icon:circle-slash
  }

  section backend {
    title "Backend"
    item "cronus-kernel" icon:server
    item "none" icon:circle-slash
  }

  section database {
    title "Database"
    item "sqlite" icon:database
    item "postgres" icon:database
  }

  section auth {
    title "Auth"
    item "cronus-auth" icon:shield
    item "none" icon:circle-slash
  }
}
""",
    )

    write(
        ROOT / "packages" / "cli" / "cli.cronus",
        """## @cooud-cronus/cli
## Nao e o npm `cronus-ui`. O CLI e o binario Rust em bin/cronus.exe
## build: scripts/setup.ps1  |  scripts/CRIAR-COMPILER.bat
##
## kernel: parse | run | build | new | compose | dump | lint
## cronus-ui npm map:
##   init      -> cronus new
##   add       -> copy packages/ui/<name>.cronus
##   compose   -> cronus compose
##   theme     -> packages/theme + tokens
##   list      -> packages/ui + packages/blocks
##   upgrade   -> git pull deste repo
##   diff      -> git diff
##   add-page  -> page block em apps/

app "Cli" {
  port 4749
}
""",
    )
    write(
        ROOT / "packages" / "cli" / "README.md",
        """# cli

Nao e o npm `cronus-ui`. O CLI e o binario Rust:

`bin/cronus.exe` (build: `scripts/setup.ps1`)

Comandos do kernel: parse, run, build, new, compose, dump.

Mapa npm -> nativo em `cli.cronus`.
""",
    )

    write(
        ROOT / "packages" / "mcp" / "mcp.cronus",
        """## @cooud-cronus/mcp
## Registry MCP do cronus-ui (Node) nao e o runtime. Descoberta nativa:
##   cronus CLI + packages/ui + packages/blocks + packages/tokens
##
## tools (intencao, sem Node):
##   list_components
##   list_blocks
##   list_catalog
##   match_catalog
##   search_registry
##   get_design_context
##   get_component
##   get_install_command
##   install_component
##   upgrade_components
##   apply_theme
##   compose_app
##   add_page
##   set_theme

app "Mcp" {
  port 4750
}
""",
    )
    write(
        ROOT / "packages" / "mcp" / "README.md",
        """# mcp

Registry MCP do cronus-ui (Node) nao e portado como runtime.

Descoberta nativa: `cronus` CLI + `packages/ui` + `packages/blocks`.

Lista de tools em `mcp.cronus`.
""",
    )

    write(
        ROOT / "packages" / "ai-kit" / "ai-kit.cronus",
        """## @cooud-cronus/ai-kit
## Doutrina de agentes. Nao instala configs Claude/Cursor daqui.
## Fonte: AGENTS.md, PROMPT-GROK-MASTER.md, packages/ai-kit/templates do cronus-ui.
##
## presets: base, saas, agency, fintech, oss
## skills: ui-add, compose, theme, upgrade, ship-pr, code-review, evidence-check
## Assistants leem AGENTS.md na raiz.

app "AiKit" {
  port 4751
}
""",
    )
    write(
        ROOT / "packages" / "ai-kit" / "README.md",
        """# ai-kit

Doutrina de agentes: ver AGENTS.md na raiz e PROMPT-GROK-MASTER.md.

Nao instala configs Claude/Cursor daqui — o app gerado pelo kernel usa `cronus context`.
""",
    )

    write(
        ROOT / "packages" / "create-cronus-app" / "create-cronus-app.cronus",
        """## @cooud-cronus/create-cronus-app
## Scaffold nativo. Nao e Next.js.
## npm: create-cronus-app --template default|dashboard|marketing
## nativo: cronus new <name>  +  copiar templates deste pacote
##
## templates: default, dashboard, marketing
## themes: aurora, neutral, midnight, sunset, emerald
## modes: dark, light

app "CreateCronusApp" {
  port 3000
  theme dark
}
""",
    )
    write(
        ROOT / "packages" / "create-cronus-app" / "default.cronus",
        """## template default — app minimo .cronus

app "App" {
  port 3000
  theme dark
}

style {
  theme dark
  preset aurora
  accent white
  font "Inter"
}

page "/" {
  section hero {
    title "Cronus"
    subtitle "Product UI in .cronus"
  }
}
""",
    )
    write(
        ROOT / "packages" / "create-cronus-app" / "dashboard.cronus",
        """## template dashboard — aponta para apps/dashboard (Cooud)

app "Dashboard" {
  port 4747
  database sqlite "./cooud.db"
  theme dark
}

style {
  theme dark
  accent white
  font "Inter"
}

page "/" {
  section kpi {
    title "Saldo"
    value "R$ 0,00"
  }
}
""",
    )
    write(
        ROOT / "packages" / "create-cronus-app" / "marketing.cronus",
        """## template marketing — landing nativa

app "Marketing" {
  port 3000
  theme dark
}

style {
  theme dark
  preset aurora
  accent white
  font "Inter"
}

page "/" {
  section hero {
    title "Cronus"
    subtitle "Compose de produto em .cronus"
  }

  section pricing {
    title "Planos"
    item "Free"
    item "Pro"
  }

  section faq {
    title "FAQ"
  }
}
""",
    )
    write(
        ROOT / "packages" / "create-cronus-app" / "README.md",
        """# create-cronus-app

Scaffold nativo `.cronus` (nao Next.js).

```
cronus new meu-app
copy packages/create-cronus-app/default.cronus meu-app/app.cronus
```

Templates: `default.cronus`, `dashboard.cronus`, `marketing.cronus`.
Dashboard de produto: `apps/dashboard/app.cronus`.
""",
    )

    write(
        ROOT / "packages" / "create-cronus-stack" / "create-cronus-stack.cronus",
        """## @cooud-cronus/create-cronus-stack
## Scaffold de stack nativo. Nao e bun create.
## npm: create-cronus-stack [name] --web --backend --db
## nativo: cronus compose + packages/stack/stack.cronus

app "CreateCronusStack" {
  port 5175
  theme dark
}
""",
    )
    write(
        ROOT / "packages" / "create-cronus-stack" / "README.md",
        """# create-cronus-stack

Scaffold de stack nativo. Catalogo em `packages/stack/stack.cronus`.

```
cronus compose
```
""",
    )


def main() -> None:
    ui = gen_ui()
    blocks = gen_blocks()
    tokens = gen_tokens()
    gen_rest()
    pkgs = sorted(p.name for p in (ROOT / "packages").iterdir() if p.is_dir())
    write(
        ROOT / "packages" / "README.md",
        f"""# packages

Pacotes nativos `.cronus` (nao npm). Espelho do monorepo cronus-ui.

| Pasta | Fonte | Conteudo |
|---|---|---|
| `tokens/` | `@cronus-ui/tokens` | {tokens} arquivos (5 presets × light/dark) |
| `theme/` | `@cronus-ui/theme` | aurora / neutral / midnight / sunset / emerald |
| `ui/` | `@cronus-ui/ui` | **{ui}** familias (barrel inteiro) |
| `blocks/` | `registry/*.json` | **{blocks}** blocks |
| `stack/` | `@cronus-ui/stack` | scaffold nativo |
| `cli/` | `cronus-ui` CLI | aponta para `bin/cronus.exe` |
| `mcp/` | `packages/mcp` | 14 tools, sem Node |
| `ai-kit/` | `@cronus-ui/ai-kit` | doutrina |
| `create-cronus-app/` | `create-cronus-app` | templates default / dashboard / marketing |
| `create-cronus-stack/` | `create-cronus-stack` | compose nativo |

Pastas no disco: {", ".join(pkgs)}

Compilador: `scripts/setup.ps1` → `compiler/cronus-kernel` → `bin/cronus.exe`.
""",
    )
    print("ui", ui)
    print("blocks", blocks)
    print("tokens", tokens)
    print("packages", pkgs)


if __name__ == "__main__":
    main()
