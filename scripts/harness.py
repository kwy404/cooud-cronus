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

FORBIDDEN_LINE = re.compile(
    r"""
    style_block
    | \btailwind_config\b
    | \btemplate\s+"
    | <(div|nav|section|span|svg|button|html|body|style|img|a)\b
    | class=\\"
    | class='
    | from\s+['\"]react
    | \.tsx\b
    | import\s+React
    """,
    re.I | re.X,
)

SKIP_DIRS = {
    "workspace",
    "migration-staging",
    "compiler",
    "bin",
    ".git",
    "forbidden-html",
    "node_modules",
}


def iter_cronus() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.cronus"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def scan_forbidden(paths: list[Path]) -> list[dict]:
    hits = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("##"):
                continue
            if FORBIDDEN_LINE.search(line):
                hits.append(
                    {
                        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
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


def try_parse() -> dict:
    exe = ROOT / "bin" / "cronus.exe"
    if not exe.exists():
        exe = ROOT / "bin" / "cronus"
    app = ROOT / "apps" / "dashboard" / "app.cronus"
    if not exe.exists():
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
        return {
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "code": proc.returncode,
            "output": out[-4000:],
        }
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}


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
        "## Gate: no TSX / HTML / CSS in `.cronus`",
        "",
        f"status: **{data['forbidden_status']}**",
        f"hits: {len(hits)}",
        "",
    ]
    if hits:
        lines.append("| file | line | excerpt |")
        lines.append("|---|---|---|")
        for h in hits[:80]:
            excerpt = h["excerpt"].replace("|", "\\|")
            lines.append(f"| `{h['file']}` | {h['line']} | `{excerpt}` |")
        lines.append("")
        lines.append("VERIFY: remove style_block / template HTML / CSS / TSX. Kernel renders.")
        lines.append("")
    else:
        lines.append("No forbidden HTML/CSS/TSX in authoring `.cronus`.")
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
        "1. `apps/dashboard/app.cronus` is native sections only (sidebar, kpi, progress, tabs, chart, table, empty).",
        "2. `cronus parse apps/dashboard/app.cronus` succeeds after `scripts/CRIAR-COMPILER.bat`.",
        "3. No `.cronus` file contains `style_block`, `template \"<html>`, or TSX.",
        "4. Catalog files in `packages/ui` are contracts (variants/slots), not React ports — visual parity of 173 widgets is NOT VERIFIED.",
        "5. Pixel-identical Cooud chrome is a LANGUAGE GAP: kernel renderer owns HTML. Do not re-embed CSS.",
        "6. PNG previews in `docs/preview/` are visual targets, not the source of truth.",
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
    hits = scan_forbidden(cronus_files)
    inv = inventory()
    parse = try_parse()
    forbidden_status = "FAIL" if hits else "PASS"
    parse_ok = parse.get("status") in {"PASS", "SKIPPED"}
    overall = "PASS" if forbidden_status == "PASS" and parse_ok else "FAIL"
    if parse.get("status") == "SKIPPED" and forbidden_status == "PASS":
        overall = "PASS_WITH_GAPS"
    data = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cronus_files": len(cronus_files),
        "forbidden": hits,
        "forbidden_status": forbidden_status,
        "inventory": inv,
        "parse": parse,
        "overall": overall,
    }
    path = write_report(data)
    print(f"files={len(cronus_files)} forbidden={len(hits)} parse={parse.get('status')} overall={overall}")
    print(path)
    if forbidden_status == "FAIL":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
