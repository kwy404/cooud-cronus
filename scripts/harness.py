"""Harness: native .cronus only. No TSX / HTML / CSS escape hatch."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_UI = Path(r"C:\Users\Hadouken Game Center\Desktop\cooud\cronus-ui\packages\ui\src\components")
SRC_REG = Path(r"C:\Users\Hadouken Game Center\Desktop\cooud\cronus-ui\registry")
SRC_PKGS = Path(r"C:\Users\Hadouken Game Center\Desktop\cooud\cronus-ui\packages")

HATCH_LINE = re.compile(
    r"""style_block | \btailwind_config\b | \btemplate\s+" """,
    re.I | re.X,
)
MARKUP_LINE = re.compile(
    r"""
    </?(div|nav|section|span|svg|button|html|body|head|style|script|img|input|textarea|select|!DOCTYPE)\b
    | <a(/|>|\s)
    | from\s+['\"]react
    | import\s+React
    """,
    re.I | re.X,
)

TEXT_EXTS = {".cronus", ".md", ".sdd", ".py", ".txt", ".csv", ".json", ".ps1", ".bat"}

SKIP_DIRS = {
    "workspace",
    "migration-staging",
    "compiler",
    "bin",
    ".git",
    "node_modules",
}

FORBIDDEN_EXTS = {".html", ".htm", ".css", ".tsx", ".jsx", ".vue", ".scss"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
PREVIEW_DIRS = ("docs/preview", "output/preview")


def iter_cronus() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.cronus"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def scan_forbidden_files() -> list[str]:
    hits = []
    for child in ROOT.iterdir():
        if child.name in SKIP_DIRS or child.name.startswith("."):
            continue
        stack = [child] if child.is_dir() else []
        if child.is_file() and child.suffix.lower() in FORBIDDEN_EXTS:
            hits.append(child.name)
        while stack:
            d = stack.pop()
            if d.name in SKIP_DIRS:
                continue
            try:
                entries = list(d.iterdir())
            except OSError:
                continue
            for p in entries:
                if p.name in SKIP_DIRS or p.name == "node_modules":
                    continue
                if p.is_dir():
                    stack.append(p)
                elif p.is_file() and p.suffix.lower() in FORBIDDEN_EXTS:
                    hits.append(str(p.relative_to(ROOT)).replace("\\", "/"))
    return sorted(hits)


def scan_preview_not_images() -> list[str]:
    hits = []
    for rel in PREVIEW_DIRS:
        d = ROOT / rel
        if not d.is_dir():
            continue
        for p in d.iterdir():
            if not p.is_file():
                continue
            if p.name.lower() == "readme.md":
                continue
            if p.suffix.lower() not in IMAGE_EXTS:
                hits.append(str(p.relative_to(ROOT)).replace("\\", "/"))
    return sorted(hits)


def iter_text() -> list[Path]:
    out = []
    for child in ROOT.iterdir():
        if child.name in SKIP_DIRS or child.name.startswith("."):
            continue
        stack = [child] if child.is_dir() else []
        if child.is_file() and child.suffix.lower() in TEXT_EXTS:
            out.append(child)
        while stack:
            d = stack.pop()
            if d.name in SKIP_DIRS:
                continue
            try:
                entries = list(d.iterdir())
            except OSError:
                continue
            for p in entries:
                if p.name in SKIP_DIRS or p.name == "node_modules":
                    continue
                if p.is_dir():
                    stack.append(p)
                elif p.is_file() and p.suffix.lower() in TEXT_EXTS:
                    out.append(p)
    return sorted(out)


def scan_forbidden(paths: list[Path]) -> list[dict]:
    hits = []
    skip_names = {"harness.py"}
    for path in paths:
        if path.name in skip_names:
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if rel in {"harness/report.md", "harness/report.json"}:
            continue
        text = path.read_text(encoding="utf-8")
        is_cronus = path.suffix.lower() == ".cronus"
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("##"):
                continue
            if MARKUP_LINE.search(line) or (is_cronus and HATCH_LINE.search(line)):
                hits.append(
                    {
                        "file": rel,
                        "line": i,
                        "excerpt": line.strip()[:160],
                    }
                )
    return hits


def inventory() -> dict:
    src_ui = sorted(
        p.stem for p in SRC_UI.glob("*.tsx") if not p.stem.endswith(".test")
    ) if SRC_UI.exists() else []
    dst_ui = sorted(
        p.stem
        for p in (ROOT / "packages" / "ui").glob("*.cronus")
        if p.stem != "index"
    )
    src_blocks = sorted(
        p.stem for p in SRC_REG.glob("*.json") if p.stem not in {"index", "meta", "cn"}
    ) if SRC_REG.exists() else []
    dst_blocks = sorted(p.stem for p in (ROOT / "packages" / "blocks").glob("*.cronus"))
    src_pkgs = sorted(p.name for p in SRC_PKGS.iterdir() if p.is_dir()) if SRC_PKGS.exists() else []
    dst_pkgs = sorted(p.name for p in (ROOT / "packages").iterdir() if p.is_dir())
    return {
        "ui_source": len(src_ui),
        "ui_target": len(dst_ui),
        "ui_missing": sorted(set(src_ui) - set(dst_ui)),
        "ui_extra": sorted(set(dst_ui) - set(src_ui)),
        "blocks_source": len(src_blocks),
        "blocks_target": len(dst_blocks),
        "blocks_missing": sorted(set(src_blocks) - set(dst_blocks)),
        "packages_source": src_pkgs,
        "packages_target": dst_pkgs,
        "packages_missing": sorted(set(src_pkgs) - set(dst_pkgs)),
    }


def _cronus_exe() -> Path | None:
    exe = ROOT / "bin" / "cronus.exe"
    if exe.exists():
        return exe
    exe = ROOT / "bin" / "cronus"
    return exe if exe.exists() else None


def try_parse() -> dict:
    exe = _cronus_exe()
    app = ROOT / "apps" / "dashboard" / "app.cronus"
    if not exe:
        return {"status": "SKIPPED", "reason": "bin/cronus.exe missing — run scripts/CRIAR-COMPILER.bat"}
    try:
        proc = subprocess.run(
            [str(exe), "parse", str(app)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ROOT),
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        val = subprocess.run(
            [str(exe), "validate", str(app)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ROOT),
        )
        val_out = (val.stdout or "") + (val.stderr or "")
        ok = proc.returncode == 0 and val.returncode == 0
        return {
            "status": "PASS" if ok else "FAIL",
            "code": proc.returncode,
            "output": out[-2000:],
            "validate": val_out[-2000:],
            "validate_code": val.returncode,
        }
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}


def parse_all_cronus() -> dict:
    exe = _cronus_exe()
    files = iter_cronus()
    if not exe:
        return {"status": "SKIPPED", "total": len(files), "ok": 0, "fail": []}
    fail = []
    ok = 0
    for path in files:
        proc = subprocess.run(
            [str(exe), "parse", str(path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(ROOT),
        )
        if proc.returncode == 0:
            ok += 1
        else:
            msg = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
            fail.append(
                {
                    "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "error": msg[0] if msg else "parse failed",
                }
            )
    return {
        "status": "PASS" if not fail else "FAIL",
        "total": len(files),
        "ok": ok,
        "fail": fail,
    }


def write_report(data: dict) -> Path:
    dst = ROOT / "harness" / "report.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    inv = data["inventory"]
    parse = data["parse"]
    hits = data["forbidden"]
    lines = [
        "# Harness report",
        "",
        f"generated: {data['generated']}",
        "",
        "## Gate: no page markup in the repo",
        "",
        f"status: **{data['forbidden_status']}**",
        f"hits in .cronus: {len(hits)}",
        f"html/css/tsx files in repo: {len(data.get('forbidden_files') or [])}",
        f"preview not image: {len(data.get('preview_not_images') or [])}",
        "",
    ]
    file_hits = data.get("forbidden_files") or []
    preview_hits = data.get("preview_not_images") or []
    if preview_hits:
        lines.append("Preview must be image only:")
        lines.append("")
        for f in preview_hits:
            lines.append(f"- `{f}`")
        lines.append("")
    if file_hits:
        lines.append("Forbidden files (HTML/CSS/TSX must not live here):")
        lines.append("")
        for f in file_hits:
            lines.append(f"- `{f}`")
        lines.append("")
    if hits:
        lines.append("| file | line | excerpt |")
        lines.append("|---|---|---|")
        for h in hits[:80]:
            excerpt = h["excerpt"].replace("|", "\\|")
            lines.append(f"| `{h['file']}` | {h['line']} | `{excerpt}` |")
        lines.append("")
        lines.append("VERIFY: remove style_block / template markup. Kernel renders.")
        lines.append("")
    else:
        lines.append("No page markup in authoring files. Source is `.cronus`.")
        lines.append("")

    lines += [
        "## Gate: parse apps/dashboard/app.cronus",
        "",
        f"status: **{parse.get('status')}**",
        "",
    ]
    if parse.get("reason"):
        lines.append(f"reason: {parse['reason']}")
        lines.append("")
    if parse.get("output"):
        lines.append("```")
        lines.append(parse["output"].strip())
        lines.append("```")
        lines.append("")
    if parse.get("validate"):
        lines.append("validate:")
        lines.append("```")
        lines.append(parse["validate"].strip())
        lines.append("```")
        lines.append("")

    pall = data.get("parse_all") or {}
    lines += [
        "## Gate: parse every `.cronus`",
        "",
        f"status: **{pall.get('status')}**",
        f"ok: {pall.get('ok')} / {pall.get('total')}",
        "",
    ]
    for item in (pall.get("fail") or [])[:40]:
        lines.append(f"- `{item['file']}`: {item['error']}")
    if pall.get("fail"):
        lines.append("")

    lines += [
        "## Inventory vs cronus-ui",
        "",
        f"- UI families: source {inv['ui_source']} / target {inv['ui_target']}",
        f"- blocks: source {inv['blocks_source']} / target {inv['blocks_target']}",
        f"- packages source: {', '.join(inv['packages_source']) or '(offline)'}",
        f"- packages target: {', '.join(inv['packages_target'])}",
        "",
    ]
    if inv["ui_missing"]:
        lines.append("UI missing: " + ", ".join(inv["ui_missing"]))
        lines.append("")
    if inv["blocks_missing"]:
        lines.append("blocks missing: " + ", ".join(inv["blocks_missing"]))
        lines.append("")
    if inv["packages_missing"]:
        lines.append("packages missing: " + ", ".join(inv["packages_missing"]))
        lines.append("")
    if inv["ui_extra"]:
        lines.append("UI extra (not in source tsx): " + ", ".join(inv["ui_extra"]))
        lines.append("")

    lines += [
        "## VERIFY (agent)",
        "",
        "Regra Zedd (fechou): HTML nao entra. O HTML e o `.cronus`. Kernel emite a pagina.",
        "1. `apps/dashboard/app.cronus` is native sections only (sidebar, kpi, progress, tabs, chart, table, empty).",
        "2. `cronus parse apps/dashboard/app.cronus` succeeds after `scripts/CRIAR-COMPILER.bat`.",
        "3. No file in this repo contains page markup. Source is `.cronus` only.",
        "4. Catalog files in `packages/ui` are contracts (variants/slots), not React ports — visual parity of 173 widgets is NOT VERIFIED.",
        "5. Pixel chrome is a LANGUAGE GAP. Do not re-embed page markup to fake it.",
        "6. Preview is image only (`docs/preview/*.png`).",
        "",
        f"overall: **{data['overall']}**",
        "",
    ]
    dst.write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "harness" / "report.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8"
    )
    return dst


def main() -> int:
    cronus_files = iter_cronus()
    hits = scan_forbidden(iter_text())
    file_hits = scan_forbidden_files()
    preview_hits = scan_preview_not_images()
    inv = inventory()
    parse = try_parse()
    parse_all = parse_all_cronus()
    forbidden_status = "FAIL" if hits or file_hits or preview_hits else "PASS"
    parse_ok = parse.get("status") in {"PASS", "SKIPPED"}
    all_ok = parse_all.get("status") in {"PASS", "SKIPPED"}
    overall = "PASS" if forbidden_status == "PASS" and parse_ok and all_ok else "FAIL"
    if parse.get("status") == "SKIPPED" and forbidden_status == "PASS":
        overall = "PASS_WITH_GAPS"
    data = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cronus_files": len(cronus_files),
        "forbidden": hits,
        "forbidden_files": file_hits,
        "preview_not_images": preview_hits,
        "forbidden_status": forbidden_status,
        "inventory": inv,
        "parse": parse,
        "parse_all": parse_all,
        "overall": overall,
    }
    path = write_report(data)
    print(
        f"files={len(cronus_files)} forbidden_lines={len(hits)} "
        f"forbidden_files={len(file_hits)} preview_bad={len(preview_hits)} "
        f"parse={parse.get('status')} parse_all={parse_all.get('ok')}/{parse_all.get('total')} "
        f"overall={overall}"
    )
    print(path)
    if forbidden_status == "FAIL":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
