"""Write packages/blocks with layout, copy, and composition from the registry."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = Path(r"C:\Users\Hadouken Game Center\Desktop\cooud\cronus-ui\registry")
UI_DIR = ROOT / "packages" / "ui"
DST = ROOT / "packages" / "blocks"

TW = re.compile(
    r"\b(flex|grid|inline|block|hidden|sr-only|contents|truncate|"
    r"size-|w-|h-|p-|px-|py-|m-|mx-|my-|gap-|text-|bg-|border|"
    r"rounded|shadow|items-|justify-|font-|leading-|tracking-|"
    r"opacity-|z-|inset-|top-|left-|right-|bottom-|absolute|relative|"
    r"overflow-|max-|min-|sm:|md:|lg:|xl:|2xl:|hover:|focus|data-|"
    r"aria-|disabled:|placeholder:|file:|peer|group|from-|to-|via-|"
    r"ring-|outline-|transition|animate-|whitespace-|pointer-|"
    r"select-|cursor-|shrink-|grow-|col-|row-|self-|place-|"
    r"backdrop-|blur-|drop-|space-|divide-|object-|aspect-)\b"
)
SKIP = {
    "true", "false", "react", "undefined", "null", "use client", "button",
    "submit", "email", "password", "text", "div", "span", "hidden", "number",
    "string", "boolean", "function", "const", "return", "className",
    "primary", "secondary", "outline", "ghost", "destructive", "link",
    "default", "sm", "md", "lg", "icon", "single", "multiple",
    "@cronus-ui/ui", "lucide-react", "cronus-invitation", "invitation",
}
ICONS = {
    "Sparkles", "ArrowRight", "Check", "Github", "Chrome", "Hexagon", "Menu",
    "Plus", "Inbox", "Send", "Lock", "ShieldCheck", "CreditCard", "X",
    "ChevronDown", "ChevronRight", "Search", "Bell", "Settings", "User",
    "Home", "Star", "Heart", "Mail", "Calendar", "Clock", "Globe",
}

UI_FAMILIES = {p.stem for p in UI_DIR.glob("*.cronus") if p.stem != "index"}
UI_PASCAL = {"".join(p[:1].upper() + p[1:] for p in n.split("-")): n for n in UI_FAMILIES}


def ident(name: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in name.replace("_", "-").split("-") if p)


def q(s: str) -> str:
    s = " ".join(s.split())[:90]
    return '"' + s.replace("\\", "").replace('"', "") + '"'


def is_copy(s: str) -> bool:
    s = " ".join(s.split())
    if len(s) < 3 or len(s) > 140:
        return False
    if s.lower() in SKIP:
        return False
    if any(ch in s for ch in "<>{}=;()[]`"):
        return False
    if s.startswith((",", ".", "+", "'", ":", "/", "@", "#")):
        return False
    if s.endswith((".js", ".tsx", ".ts", ".css", ".json")):
        return False
    if TW.search(s):
        return False
    if s.count("-") >= 3 and " " not in s:
        return False
    letters = sum(c.isalpha() or c.isspace() or c in ".,?'-+" for c in s)
    if letters / len(s) < 0.72:
        return False
    if not re.search(r"[A-Za-z]", s):
        return False
    if re.fullmatch(r"[a-z]+(?:-[a-z0-9]+)+", s):
        return False
    return True


def copy_of(content: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(raw: str) -> None:
        s = " ".join(raw.replace("\\n", " ").split())
        if not is_copy(s) or s in seen:
            return
        seen.add(s)
        found.append(s)

    for s in re.findall(r">\s*([A-Za-z][^<>{\n]{6,100}?)\s*\{", content):
        add(s)
    for s in re.findall(r">\s*([^<>{\n][^<>{\n]{2,120}?)\s*<", content):
        add(s)
    for _, val in re.findall(
        r'\b(title|subtitle|label|name|question|answer|description|heading|headline|cta|placeholder|badge|plan|price|detail)\s*:\s*"((?:[^"\\]|\\.)+)"',
        content,
    ):
        add(val)
    for s in re.findall(r'"((?:[^"\\]|\\.){3,120})"', content):
        add(s)
    return found


def composition(content: str) -> tuple[list[str], list[str]]:
    tags = re.findall(r"<([A-Z][A-Za-z0-9]+)", content)
    ui: list[str] = []
    icons: list[str] = []
    for t in tags:
        if t in ICONS or t.endswith(("Icon", "Increasing")):
            if t not in icons:
                icons.append(t)
            continue
        if t in {"Fragment", "Suspense", "StrictMode", "HTMLFormElement"}:
            continue
        slug = UI_PASCAL.get(t) or re.sub(r"(?<!^)(?=[A-Z])", "-", t).lower()
        sub = t.startswith(("Card", "Dialog", "Alert", "Empty", "Accordion", "Sheet", "Drawer", "Select", "Tabs"))
        if slug in UI_FAMILIES or t in UI_PASCAL or sub:
            if t not in ui:
                ui.append(t)
        elif t not in ui and t[0].isupper():
            if t not in icons:
                icons.append(t)
    return ui, icons


def kind_of(stem: str, rtype: str) -> str:
    if rtype == "registry:ui":
        return "ui"
    if rtype == "registry:lib":
        return "lib"
    if any(k in stem for k in ("login", "signup", "forgot-password", "otp", "magic-link", "auth")):
        return "auth"
    if any(k in stem for k in ("hero", "cta", "faq", "pricing", "footer", "navbar", "about",
                               "testimonial", "waitlist", "logo-cloud", "feature", "blog",
                               "contact", "changelog", "team")):
        return "marketing"
    if any(k in stem for k in ("dashboard", "analytics", "stats", "usage", "chart", "kpi")):
        return "data"
    if any(k in stem for k in ("checkout", "cart", "billing", "invoice", "payment", "order", "product")):
        return "commerce"
    if any(k in stem for k in ("empty", "error", "not-found", "maintenance", "success")):
        return "empty"
    if any(k in stem for k in ("settings", "account", "profile", "session", "security", "api-key")):
        return "settings"
    return "section"


def layout_meta(kind: str, stem: str, ui: list[str]) -> str:
    if kind == "auth":
        return "form-card"
    if stem.startswith("hero"):
        return "hero-center"
    if "pricing" in stem:
        return "pricing-grid"
    if "faq" in stem:
        return "faq-accordion"
    if "navbar" in stem or "footer" in stem:
        return "site-chrome"
    if kind == "data":
        return "dashboard-grid"
    if kind == "commerce":
        return "checkout-split"
    if kind == "empty":
        return "empty-center"
    if "Card" in ui and "Input" in ui:
        return "form-card"
    if "Accordion" in ui:
        return "faq-accordion"
    if "Sidebar" in ui or "AppShell" in ui:
        return "app-shell"
    if "Table" in ui or "DataTable" in ui:
        return "table-stack"
    return "stack"


def emit_block(stem: str, data: dict) -> str:
    feat = ident(stem)
    rtype = data.get("type", "registry:block")
    kind = kind_of(stem, rtype)
    files = data.get("files") or []
    content = files[0].get("content", "") if files else ""
    copy = copy_of(content)
    ui, icons = composition(content)
    deps = data.get("registryDependencies") or []
    meta = layout_meta(kind, stem, ui)

    comments = [
        f"## Block {feat}",
        f"## source: registry/{stem}.json",
        f"## type: {rtype}",
        f"## layout: {meta}",
        f"## compose: {', '.join(ui) if ui else 'native-sections'}",
    ]
    if icons:
        comments.append("## icons: " + ", ".join(icons[:8]))
    if deps:
        comments.append("## registryDependencies: " + ", ".join(deps))

    body: list[str] = [
        f"  meta {q(meta)}",
        f"  label {q(feat)}",
    ]
    headings = [c for c in copy if len(c) >= 8 and not c.endswith("?")]
    title = headings[0] if headings else (copy[0] if copy else feat)
    subtitle = headings[1] if len(headings) > 1 else (copy[1] if len(copy) > 1 else title)
    if kind == "auth":
        for prefer in (
            "Welcome back",
            "Create an account",
            "Join the workspace",
            "Forgot password",
            "Check your email",
            "Verify",
        ):
            hit = next((c for c in copy if prefer.lower() in c.lower()), None)
            if hit:
                title = hit
                break
    if stem.startswith("hero"):
        longish = [c for c in copy if len(c) > 20]
        if longish:
            title = longish[0]
            subtitle = longish[1] if len(longish) > 1 else subtitle
    body.append(f"  title {q(title)}")
    body.append(f"  subtitle {q(subtitle)}")

    for piece in ui[:12]:
        body.append(f"  slot {q(piece)}")

    tests: list[str] = []
    if kind == "auth":
        body += [
            "  state pending: boolean = false",
            "  field \"Email\"",
            "  field \"Password\"",
        ]
        preferred = "Sign in" if "login" in stem else "Sign up" if "signup" in stem else "Submit"
        for c in copy:
            if c.lower() in {"sign in", "sign up", "join workspace", "create account", "send link", "verify"}:
                preferred = c
                if "login" in stem and c.lower() == "sign in":
                    break
                if "signup" in stem and c.lower() == "sign up":
                    break
        body.append(f"  action {q(preferred)}")
        if any("forgot" in c.lower() for c in copy):
            body.append("  link \"Forgot password?\" -> \"/forgot-password\"")
        tests.append('  test "submit" {\n    fill email "you@company.com"\n    click "Submit"\n  }')
    elif kind == "marketing" or "pricing" in stem or "faq" in stem or stem.startswith("hero"):
        if "faq" in stem:
            questions = [c for c in copy if c.endswith("?")]
            for qn in questions[:6]:
                body.append(f"  item {q(qn)}")
        plans = [c for c in copy if c in {"Starter", "Pro", "Enterprise", "Free", "Hobby", "Team"}]
        for plan in plans:
            body.append(f"  plan {q(plan)}")
        buttons = [c for c in copy if c in {
            "Get started", "Start free trial", "Book a demo", "Learn more",
            "Subscribe", "Sign in", "Contact sales", "Start building",
        } or (c[0].isupper() and len(c.split()) <= 3 and any(w in c.lower() for w in ("start", "book", "get", "join", "subscribe", "learn")))]
        seen_btn: set[str] = set()
        for b in buttons:
            if b in seen_btn:
                continue
            seen_btn.add(b)
            body.append(f"  button {q(b)}")
            if len(seen_btn) >= 3:
                break
        if not seen_btn and copy:
            body.append(f"  cta {q(copy[0])}")
        click = next(iter(seen_btn), copy[0] if copy else feat)
        tests.append(f'  test "cta" {{\n    click {q(click)}\n  }}')
    elif kind == "commerce":
        for ph in [c for c in copy if "@" in c or c[0].isdigit() or c in {"MM / YY", "Card number"}][:4]:
            body.append(f"  field {q(ph)}")
        body.append("  action \"Pay\"")
        tests.append('  test "pay" {\n    click "Pay"\n  }')
    elif kind == "data":
        body.append("  columns \"name, value, status\"")
        for c in copy[:4]:
            if len(c.split()) <= 4:
                body.append(f"  item {q(c)}")
        tests.append(f'  test "reads" {{\n    expect visible {q(copy[0] if copy else feat)}\n  }}')
    elif kind == "empty":
        body.append("  action \"Go home\" -> \"/\"")
        tests.append('  test "empty" {\n    click "Go home"\n  }')
    elif kind == "settings":
        body += ["  field \"Name\"", "  action \"Save\""]
        tests.append('  test "save" {\n    click "Save"\n  }')
    elif kind == "ui":
        body.append("  action \"click\"")
        tests.append(f'  test "uses {feat}" {{\n    click {q(feat)}\n  }}')
    else:
        for c in copy[2:8]:
            if len(c.split()) <= 6:
                body.append(f"  item {q(c)}")
        tests.append(f'  test "use" {{\n    expect visible {q(copy[0] if copy else feat)}\n  }}')

    # leftover copy as items so nothing is dropped
    already = " ".join(body)
    extra = 0
    for c in copy:
        if c in already or extra >= 10:
            continue
        if len(c) > 80:
            continue
        body.append(f"  text {q(c)}")
        extra += 1

    lines = comments + ["", f"component {feat}Block(label: text) layout:stack style:{stem} {{"]
    lines += body
    lines += tests
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    skip = {"index", "meta", "cn"}
    n = 0
    kinds: dict[str, int] = {}
    for path in sorted(REG.glob("*.json")):
        if path.stem in skip:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        text = emit_block(path.stem, data)
        (DST / f"{path.stem}.cronus").write_text(text, encoding="utf-8")
        k = kind_of(path.stem, data.get("type", ""))
        kinds[k] = kinds.get(k, 0) + 1
        n += 1
    print("blocks", n, kinds)


if __name__ == "__main__":
    main()
