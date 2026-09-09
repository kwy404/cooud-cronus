# First deliverable — Cronus UI → Cronus Kernel

Status: **specified, not implemented**. No kernel/UI source was edited.
Date: 2026-09-08
Pack: `cronus-ui-in-cronus-language/`
Canonical specs after this drop: `workspace/cronus-kernel/migration/` (mirrored in this pack under `specs/`, `harness/`, `migration/`).

Existing kernel plan `.cronus/PLAN-2026-04-10.md` is **active**. It is not overwritten. Integration rules: `specs/06-kernel-plan-integration.sdd`.

---

## 1. Repository baseline summary

| | Source `cronus-ui` | Target `cronus-kernel` |
|---|---|---|
| Path | `C:\Users\Hadouken Game Center\Desktop\cooud\cronus-ui` | `C:\Users\Hadouken Game Center\Desktop\cooud\cronus-kernel` |
| SHA | `b9c8635f200f2d1c8fc6fa08d7b8b3dc0557a814` | `ddce3e0b8c8140c934fc99885d5ef72d60092635` |
| Tip | `chore(registry): pin dos itens a @cronus-ui/ui@0.7.3` (2026-09-07) | `chore: add Cargo.lock, .gitignore, fix repo URLs` (2026-04-10) |
| Branch | `main...origin/main` (clean) | `main...origin/main` (clean) |

Toolchain at capture (`migration-staging/meta.txt`):

- git 2.54.0.windows.1
- rustc / cargo 1.96.0
- bun 1.3.14
- node v24.16.0
- host Windows

Workspace wiring: pack `workspace/cronus-ui` and `workspace/cronus-kernel` are NTFS junctions to those checkouts (not a second clone).

### Source gates (attempted)

| Gate | Result | Notes |
|---|---|---|
| `bun run lint` (`biome check .`) | **PRE-EXISTING FAIL** | `bun: command not found: biome` — script does not resolve `@biomejs/biome` on this PATH. Not caused by migration. |
| typecheck / vitest / contract / registry / a11y / e2e | **NOT RUN YET** | Deferred; Playwright needs `bun run build` first. Recorded as baseline TODO. |

### Target gates (attempted)

| Gate | Result | Notes |
|---|---|---|
| `cargo test --offline` | **PRE-EXISTING FAIL** | No `argon2` in local cargo cache; `target/` absent. |
| `cargo test` (network) | **PRE-EXISTING FAIL 209/210** | `dump::detect::tests::test_hero_extraction_developer_landing` panics `NotFound` (Windows path). 7 `unexpected_cfgs` warnings. Log: `migration/evidence/baseline/cargo-test.log`. |
| `cargo build --release` | **NOT RUN YET** | Deps now cached; run with slice 1. |
| `cronus build/parse/compose` | **NOT RUN YET** | Debug test binary exists under `target/debug/deps/`. |

AGENTS.md claims **203** inline `#[test]`s, **zero** coverage on `src/ui/**`, `render.rs`, `binding.rs`. LANGUAGE.md last verified **2026-04-10**. Trust LANGUAGE.md over older docs.

Dead code (do not patch): `src/server/router.rs`, `src/server/api.rs` (not in `mod.rs`); `CronusServer` in `server/mod.rs` has zero call sites. Live dispatcher is `src/main.rs::handle_request_inner`.

---

## 2. Source capability inventory (cronus-ui 0.7.3)

Full ledger: `specs/01-source-inventory.sdd`.

**Product category** (ADR 0003): product UI system (compose + live theme + authoring contract). Catalog is the means, not the category.

**Authoring contract** (`CONTRACT.md`): semantic tokens only; CVA variants; `ref` (React — do not cargo-cult); `data-slot`; `asChild`/Slot; focus-visible ring; RTL logical properties; i18n via `labels` props; no locale-env formatting.

**Tokens** (`packages/tokens`): themes `aurora | neutral | midnight | sunset | emerald`; modes `light | dark`. Roles: primary/accent + `*-text` strong variants, surface ladder (base/inset/raised/overlay/elevated/floating), fg ladder, border/ring, success/warning/error/info + strong text, radius, fonts, chart1–5, shadows. CSS vars `--cronus-*`. Contrast gated by `scripts/contrast.mjs`.

**Theme** (`packages/theme`): `CronusUIProvider` writes `data-cronus-theme` / `data-cronus-mode` / `.dark`; runtime `overrides` as CSS vars; optional `localStorage`; subtree theming (`asRoot`).

**UI barrel**: `packages/ui/src/index.ts`. **~185 component modules** (325 `*.tsx` counting tests). Waves in source comments go to Wave 6 (motion harvest) and Wave 5 (layout/app nav) — **beyond the seed matrix Wave 0–4**.

**CLI** (`cronus-ui`): `init`, `add`, `compose`, `add-page`, `list`, `diff`, `upgrade`, `theme set`, `theme add`, `ai`.

**Also**: registry (generated), stack builder, create-cronus-app (default SaaS, ADR 0007), create-cronus-stack, MCP, apps/www (OSS docs :4747), apps/pro (additive origin, ADR 0005/0006), examples/smoke-next + smoke-vite, e2e a11y/contrast/flows/visual.

**ADRs**: 0001 literal colors; 0002 forwardRef; 0003 product UI system; 0004 looks; 0005/0006 Pro; 0007 create-app default SaaS.

**Intentionally React-only mechanics** (map intent, drop mechanism): `forwardRef`, `asChild` Slot, `"use client"`, RHF/Zod, TanStack Table, Recharts, Next.js.

---

## 3. Target capability / gap inventory (cronus-kernel)

Authoritative: `LANGUAGE.md` (2026-04-10). Full gap table: `specs/02-language-gap-analysis.sdd`.

CRONUS is a **declarative full-stack language** compiling to one Rust binary (`cronus-lang` / bin `cronus`). No `[lib]`, no workspace. SSR HTML + Tailwind CDN + ~2KB vanilla JS (`src/render.rs`). **Not** a design-system component library today.

| Area | Reality | Gap class |
|---|---|---|
| `component Name { ... }` | LANGUAGE.md §6 is **stale**. Parser + `main.rs` already do params, `template` `{{p}}`, `state`, `@click` (tiny per-instance JS). Demo: `demos/component-test/v2.cronus`. `src/ui/component.rs` is a **second** layout-preset dispatcher. `src/components.rs::button` exists but fails the source contract (uppercase, `danger`, no `data-slot`, mixed palettes). | NEEDS_RENDERER_EXTENSION on the existing helper; no new keyword for slice 1 |
| Typed props / slots / variants / CVA | No first-class variant enum, no slots, no `data-slot` contract | NEEDS_LANGUAGE_EXTENSION + RENDERER |
| Semantic tokens | `style { theme dark accent blue }`; `tailwind_config` JS scraped into `ThemeTokens` with **hardcoded hex Obsidian defaults** (`src/theme.rs`) | NEEDS_LANGUAGE_EXTENSION + RUNTIME. Do not keep JS config as SoT |
| Theme switch / overrides | `dark-mode` section; not aurora/neutral + CSS-var override model | NEEDS_RUNTIME_EXTENSION |
| Foundation primitives (Button, Input, …) | Absent as DS primitives. Entity fields render native form controls by type | NEEDS_RENDERER_EXTENSION |
| Page sections | **39 canonical** types (hero, form, table, chart SVG bar/line/area/donut, modal, sheet, drawer, popover, tabs, …) | EXPRESSIBLE_WITH_EXISTING_CRONUS for *page blocks*; not DS parity |
| Forms | Entity + `section form` + field types. No RHF/Zod equivalent | NEEDS_RUNTIME_EXTENSION for validation semantics |
| Overlays | Section types exist; **zero** `src/ui` tests; keyboard/focus trap unknown | NEEDS_NEW_TEST/HARNESS + likely RENDERER |
| CLI | `run`, `build`, `parse`, `new`, `compose`, `dump`, `theme` is **not** a cronus-ui theme command | NEEDS_CLI_EXTENSION with SDD — **do not steal `compose`/`new` names blindly** |
| React/Node runtime | Not required. Preserve this. | — |

`src/ui/component.rs` and `src/ui/mod.rs` both `#![allow(dead_code, unused_imports, unused_variables)]`. Migration must not add more blanket allows.

---

## 4. Proposed CRONUS-native component model

Do **not** emulate React. Prefer **small orthogonal primitives**.

### 4.1 Token pipeline (Wave −1, first)

```
semantic token declarations in .cronus
  → validated Theme object (Rust)
  → CSS custom properties on :root / [data-cronus-theme][data-cronus-mode]
  → primitives consume roles only
```

Themes/modes from source: 5 × 2. Overrides = CSS var patch, no React.

### 4.2 Primitive vs section

- **Section** (already REAL): page-level blocks (`hero`, `form`, `table`). Keep.
- **Primitive**: design-system control (`Button`, `Input`, …) rendered from a **catalog**, not one keyword per component.

Proposed authoring (SDD before parser change; may map onto existing `component` AST first):

```cronus
theme {
  name aurora
  mode dark
}

ui Button {
  variant primary
  size md
  "Save"
}
```

If we can express this with current `component Button layout:primitive { variant:primary size:md label "Save" }` **without** new keywords, do that first (LANGUAGE.md: params already parse). New `ui` keyword only if grammar is ambiguous.

### 4.3 Contract mapping (intent, not React)

| Source | CRONUS equivalent |
|---|---|
| semantic tokens | CSS vars `--cronus-*` |
| CVA variants | explicit `variant`/`size` fields, validated enum |
| `data-slot` | same attribute on root HTML |
| `ref` | omit |
| `asChild` | `href` present → render link; else button |
| focus ring | `focus-visible` + `ring` token |
| disabled | `disabled` + opacity/pointer-events |
| RTL | logical CSS |
| i18n | no hardcoded user strings in primitives; text is author content |
| labels prop | authored `.cronus` strings |

### 4.4 Later primitives (not first slice)

slots/children, events, overlays/portals, form control binding, motion + `prefers-reduced-motion`. Each gets its own SDD.

---

## 5. Migration wave plan

| Wave | Content | Gate to next |
|---|---|---|
| **−1 Tokens** | Native semantic tokens, 5 themes × 2 modes, overrides, forbidden raw palette lint | CSS vars round-trip tests green |
| **0 Foundation** | Button, Input, Label, Badge, Card, Separator, Skeleton, Spinner | variants, disabled/focus, light/dark, a11y, evidence |
| **1 Forms** | Textarea, Checkbox, Switch, RadioGroup, Select, Slider, Toggle, ToggleGroup, Field, Form, InputOTP, FileDropzone + native validation | no RHF/Zod |
| **2 Overlays/nav** | Dialog, Sheet, AlertDialog, Dropdown, Popover, HoverCard, Tooltip, Tabs, Accordion, Drawer, Toast, Command | keyboard/focus harness |
| **3 Data** | Table, DataTable, Pagination, Avatar, Progress, ScrollArea, Calendar, DatePicker, Chart, Empty, Metric, Kbd, Breadcrumb | charts remain data-driven |
| **4 Premium** | GlassCard, Gradient*, Spotlight, Aurora, Shimmer, AnimatedButton, Reveal, LogoCarousel, motion | `prefers-reduced-motion` |
| **5 Layout** (source Wave 5, missing from seed) | AppShell, Sidebar, Navbar/Menubar, NavigationMenu, Toolbar, ModeToggle, … | inventory complete first |
| **6 Motion harvest** (source Wave 6) | AnimatedList/Number, Marquee, patterns, … | progressive enhancement |
| **7 Tooling** | registry, CLI mapping, compose/scaffold, stack, AI kit, MCP, docs | no second JS CLI |
| **8 Showcase** | native docs with executable `.cronus` examples | harness parses every snippet |

Seed parity CSV had **68** rows and **misses** most of Waves 5–6 plus many Wave 3 charts. Matrix expanded; nothing is VERIFIED.

---

## 6–8. SDD / parity / harness

Written under `specs/` and copied to `workspace/cronus-kernel/migration/`.

Harness design: `specs/04-harness.sdd`. First command (to be implemented with slice 1):

```
cargo test --manifest-path workspace/cronus-kernel/Cargo.toml
# later: cronus migration-check   (single documented command — not invented yet)
```

---

## 9. First vertical slice

**Name:** `W-1-TOKENS-BUTTON`  
**Spec:** `specs/07-first-slice.sdd`

Ship **native semantic tokens + Button** as one vertical slice (tokens without a consumer cannot be verified; Button without tokens hardcodes color).

Out of slice: Input and the rest of Wave 0, overlays, CLI, dump, React.

---

## 10. Acceptance criteria for slice `W-1-TOKENS-BUTTON`

A row is VERIFIED only if **all** hold:

1. SDD for tokens + Button exists and matches implementation.
2. Parser tests: valid theme/token block (or the chosen syntax) and valid Button primitive; invalid syntax rejected.
3. Renderer tests: HTML for Button variants `primary|secondary|outline|ghost|destructive|link` and sizes `sm|md|lg|icon|icon-sm`.
4. Root has `data-slot="button"` and `data-variant`.
5. Default `type="button"` (source behavior).
6. Disabled: attribute + non-interactive styling.
7. Focus-visible uses **ring token**, not a raw color.
8. Styles consume **semantic tokens only** (forbidden: `bg-zinc-*`, hardcoded palette scales). Destructive may use `color-mix` on `--cronus-error` as in source.
9. Light and dark (at least `aurora` + `neutral`) change Button via CSS vars without React.
10. `href` present → link; else button (asChild intent).
11. Demo `.cronus` file in kernel demos/templates parses and renders.
12. Full `cargo test` green; existing demos still parse.
13. `LANGUAGE.md` updated **only for what actually works**, marked REAL.
14. Evidence under `migration/evidence/w-1/button/` (image snapshot).
15. Parity rows `TOKENS`, `THEME` (minimal), `W0-BUTTON` → `VERIFIED` or `FUNCTIONAL_PARITY` with notes; **not** claimed complete for all 5 themes until those themes are generated.

Then implement that slice. Not before these specs landed (they have now).
