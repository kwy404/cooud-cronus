# SESSION-HANDOFF — 2026-09-08 (W-1 implemented)

## Invariant (user)

`cronus-kernel` and `cronus-ui` are **read-only**. Kernel edits from this session were **reverted**. Converted `.cronus` lives only in this pack `output/`.

## Current spec task

Wave 0 remainder: **Input + Label** (kernel `input()` still hardcodes `#0a0a0a` / amber).

## Completed this session

- First deliverable (SDD, inventory, gaps, harness, parity init).
- **W-1-TOKENS-BUTTON** implemented without a new tokenizer keyword.
  - `theme.rs`: aurora/neutral × light/dark `--cronus-*` + `BUTTON_PRIMITIVE_CSS`
  - `components.rs::button` / `button_ex`: variants, sizes, href→link, disabled, `data-slot`
  - `ui/component.rs` `layout:inline` maps destructive/link/icon
  - `layout.rs` injects semantic tokens + `data-cronus-theme/mode` on the document root
  - Demo `demos/ui-parity/button.cronus`
  - LANGUAGE.md §6.1 REAL
- Tests: **+11**, full suite **220 passed / 1 pre-existing fail** (`dump::detect` Windows path).

## Parity

| id | status |
|---|---|
| TOKENS | FUNCTIONAL_PARITY (5 themes not all present) |
| THEME | FUNCTIONAL_PARITY (overrides/looks incomplete) |
| W0-BUTTON | FUNCTIONAL_PARITY (HTML+tests; no visual screenshot harness yet) |

Not VERIFIED: missing browser screenshots / contrast run.

## Failing gates (pre-existing)

- `dump::detect::tests::test_hero_extraction_developer_landing` NotFound on Windows
- source `bun run lint` biome not on PATH

## Output folder (no mix-up)

Converted `.cronus` UI lives in:

`C:\Users\Hadouken Game Center\Desktop\cooud\cronus-ui-in-cronus-language\output\`

Not inside `cronus-ui`. Kernel stays language/runtime.

## Exact next action

1. Characterize source Input+Label (`packages/ui/src/components/input.tsx`, `label.tsx`).
2. Rewrite `components.rs::input` off palette hex/amber; add `data-slot="input"`, focus ring token, disabled.
3. Tests + demo; do not touch dump/detect.

## Do not

- Patch `src/server/router.rs` / `api.rs`
- Mark midnight/sunset/emerald REAL
- Claim VERIFIED without visual evidence
