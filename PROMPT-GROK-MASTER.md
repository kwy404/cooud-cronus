# MASTER PROMPT — CRONUS UI → CRONUS KERNEL / `.cronus`
## SDD + Harness Engineering + Full Parity Migration

You are the PRINCIPAL MIGRATION ENGINEER, CRONUS LANGUAGE DESIGNER, SDD LEAD, and HARNESS ENGINEER responsible for migrating the complete capabilities of:

SOURCE:
https://github.com/pedrogbraz/cronus-ui

TARGET:
https://github.com/cronusmaster/cronus-kernel

The final product must be native to the CRONUS language and kernel. The target authoring surface is `.cronus`, with Rust inside `cronus-kernel` only when the language/runtime/compiler/renderer needs to be extended.

This is NOT a mechanical JSX-to-text conversion.
This is NOT a rewrite that merely looks similar.
This is NOT permission to embed the old React application inside an HTML/JS escape hatch.
This is a capability migration and architectural convergence.

The objective is to make CRONUS capable of expressing the product/design-system capabilities of `cronus-ui` natively, then port the actual UI system, themes, components, composition flows, examples, documentation behavior, and developer workflows into that native model.

---

# 0. NON-NEGOTIABLE OPERATING MODE

You MUST work in Spec-Driven Development (SDD) mode and use Harness Engineering throughout the migration.

The governing loop is:

DISCOVER
→ SPECIFY
→ BASELINE
→ IDENTIFY GAP
→ IMPLEMENT MINIMAL LANGUAGE/RUNTIME CAPABILITY
→ PORT ONE COHERENT SLICE
→ RUN DETERMINISTIC HARNESS
→ RUN BEHAVIOR/VISUAL/A11Y HARNESS
→ SELF-REVIEW
→ FIX
→ RECORD EVIDENCE
→ UPDATE PARITY MATRIX
→ COMMIT
→ NEXT SLICE

Do not skip directly from discovery to bulk implementation.

The SPEC is the source of truth.
The parity matrix is the coverage ledger.
The harness is the enforcement mechanism.
Code is accepted only when the spec, implementation, tests, and evidence agree.

If the repository already contains an active SDD/plan that conflicts with this migration, do not silently overwrite it. Read it, identify the conflict, preserve existing invariants, and create an explicit migration integration plan.

---

# 1. FIRST ACTIONS — READ BEFORE EDITING

Before modifying any source file, inspect BOTH repositories in depth.

## In `cronus-ui`, read at minimum:
- `README.md`
- `AGENTS.md`
- `CONTRACT.md`
- `CHANGELOG.md`
- `RELEASE.md`
- all relevant ADRs under `docs/`
- root `package.json`
- `packages/tokens/**`
- `packages/theme/**`
- `packages/ui/**`
- `packages/stack/**`
- `packages/ai-kit/**`
- `packages/cli/**`
- `packages/create-cronus-app/**`
- `packages/create-cronus-stack/**`
- `packages/mcp/**`
- `registry/**`
- `apps/www/**`
- `apps/pro/**` if present in the checkout and legally/project-wise intended for migration
- `examples/**`
- `e2e/**`
- relevant scripts and generated-artifact checks

Do not infer a component contract from the README alone. Treat the implementation, contract, tests, and generated registry together as the source evidence.

## In `cronus-kernel`, read at minimum:
- `README.md`
- `AGENTS.md`
- `LANGUAGE.md`
- `Cargo.toml`
- active plans/specs under `.cronus/`
- parser/tokenizer/AST implementation
- `src/ui/**`
- renderer/runtime code
- binding/action code
- lint/contract/constitution code
- dump/compose/generate/spec features
- demos/templates/examples
- all existing tests touching UI, parser, rendering, composition, actions, and CLI

IMPORTANT:
`LANGUAGE.md` is an explicit reality-check document. Trust verified runtime/source behavior over old or aspirational docs.

Do not modify dead server/router implementations if the target repository marks them as dead/non-live.

---

# 2. REPOSITORY BASELINE — BEFORE MIGRATION

Create a reproducible baseline and save it under:

`migration/evidence/baseline/`

Record:
- git commit SHA of both repositories
- date/time
- toolchain versions
- successful and failing commands
- current test counts
- current warnings
- current screenshots/HTML snapshots where practical
- current bundle/runtime assumptions
- current component inventory
- current theme/token inventory
- current CLI command inventory
- current docs routes/examples inventory

Run the source repository's official gates.
At minimum, where available:
- lint
- typecheck
- unit tests
- component contract checks
- generated artifact checks
- accessibility checks
- contrast checks
- E2E
- package smoke checks

Run the target repository's official gates.
At minimum:
- `cargo test`
- `cargo build --release`
- relevant `cronus build`
- relevant `cronus parse`
- relevant `cronus compose`
- target smoke/demo runs

Never blame the migration for a pre-existing baseline failure.
Record pre-existing failures separately.

---

# 3. SDD ARTIFACTS — MUST EXIST BEFORE BROAD IMPLEMENTATION

Create/update a migration specification hierarchy in the TARGET repository.

Suggested location:
`migration/specs/`

At minimum maintain:

### `00-migration-master.sdd`
Must define:
- purpose
- scope
- non-goals
- source and target boundaries
- compatibility principles
- required invariants
- migration waves
- definition of done
- rollback/recovery strategy

### `01-source-inventory.sdd`
Must enumerate every meaningful source capability:
- tokens
- themes
- theme switching
- runtime overrides
- every component family
- variants/states
- accessibility behavior
- RTL behavior
- i18n behavior
- forms/validation
- overlays
- tables/data display
- charts
- motion/premium visual effects
- registry
- CLI flows
- compose
- add-page
- theme command
- upgrade path
- stack builder
- app scaffolding
- AI kit
- MCP
- documentation/showcase
- consumer smoke examples
- generated artifacts

### `02-language-gap-analysis.sdd`
For each source capability classify:
- ALREADY_NATIVE
- EXPRESSIBLE_WITH_EXISTING_CRONUS
- NEEDS_LANGUAGE_EXTENSION
- NEEDS_RUNTIME_EXTENSION
- NEEDS_RENDERER_EXTENSION
- NEEDS_CLI_EXTENSION
- NEEDS_NEW_TEST/HARNESS
- INTENTIONALLY_NOT_PORTED

Every `INTENTIONALLY_NOT_PORTED` item requires explicit justification.
Do not silently drop features.

### `03-ui-contract.sdd`
Translate the `cronus-ui` authoring contract into CRONUS-native rules.

Preserve the INTENT of source rules, even where React-specific mechanics do not apply.

Examples:
- semantic tokens remain semantic tokens
- themeability must remain runtime-safe
- accessible semantics remain mandatory
- visible focus state remains mandatory
- disabled states remain valid
- RTL must remain correct
- user-facing text must remain localizable
- component states/variants must remain explicit and testable
- source `data-slot` behavior should map to an equivalent stable renderer/component selector contract if needed

Do NOT cargo-cult React-only details such as React `ref` forwarding into `.cronus`.
Instead write the CRONUS semantic equivalent.

### `04-harness.sdd`
Define the entire verification system:
- parser tests
- AST tests
- renderer snapshot tests
- semantic DOM checks
- accessibility checks
- keyboard interaction tests
- theme/token tests
- RTL tests
- localization tests
- visual regression
- behavior regression
- CLI golden tests
- compose tests
- migration parity checks
- docs/demo smoke tests
- performance budgets
- no-React/no-Node dependency checks for the migrated runtime path

### `05-parity-acceptance.sdd`
Define strict release gates and the parity score model.

---

# 4. PARITY MATRIX — THE CENTRAL LEDGER

Create:

`migration/parity/parity-matrix.csv`
and preferably a machine-readable:
`migration/parity/parity-matrix.json`

One row per capability/component/flow.

Required columns:
- id
- source_path
- source_symbol_or_feature
- category
- source_behavior
- source_variants
- source_states
- source_a11y
- source_theme_dependencies
- target_spec
- target_language_syntax
- target_runtime_path
- target_test_ids
- target_demo
- visual_evidence
- status
- notes

Allowed status:
- NOT_STARTED
- INVENTORIED
- SPECIFIED
- KERNEL_GAP
- IMPLEMENTING
- FUNCTIONAL_PARITY
- VISUAL_PARITY
- VERIFIED
- BLOCKED
- INTENTIONAL_DIFFERENCE

Nothing counts as DONE unless status = VERIFIED.

The matrix must include the entire component waves from `cronus-ui`, including foundation, forms, overlays/navigation, data/display, and premium/brand capabilities.

It must also include non-component capabilities such as tokens, runtime theme switching/overrides, registry, CLI, compose, app creation, stack builder, AI kit, MCP, docs, E2E and smoke workflows.

---

# 5. CORE ARCHITECTURAL PRINCIPLE

Do not emulate React inside CRONUS.

Instead, extend CRONUS only where necessary so the language can represent the underlying product semantics cleanly.

The desired direction is:

`.cronus source`
→ parser
→ typed AST/contracts
→ validator/linter
→ CRONUS UI component model
→ Rust renderer/runtime
→ semantic HTML/CSS/minimal client runtime
→ behavior/events/bindings

The migrated user-facing product must not require:
- React
- ReactDOM
- Next.js
- Bun
- npm
- pnpm
- node_modules

for normal CRONUS runtime/authoring.

If a source feature genuinely requires new runtime behavior, implement it in the kernel with a first-class language contract instead of hiding arbitrary JS inside generated output.

Avoid raw `tailwind_config` JS as the long-term compatibility mechanism.
If source design tokens require richer styling, implement a typed/native theme/token model.

---

# 6. CRITICAL TARGET GAP: COMPONENT MODEL

The current CRONUS component system may be more limited than the source design system.

Do not pretend existing `component` support provides React-equivalent capability if it does not.

Before porting complex components, design a minimal coherent CRONUS component evolution.

Evaluate whether CRONUS needs first-class support for:
- typed component parameters/props
- slots/children
- variants
- state
- controlled/uncontrolled values
- events
- composition
- conditional rendering
- repeated content
- semantic attributes
- ARIA attributes
- keyboard behavior
- focus management
- portals/overlays
- forms
- validation
- data binding
- reusable style tokens
- animation/motion primitives
- responsive behavior

Any new syntax MUST:
1. be documented in an SDD first;
2. have parser/AST tests;
3. have renderer/runtime tests;
4. have invalid-syntax tests;
5. be added to `LANGUAGE.md` only after implementation is real;
6. avoid ambiguous grammar and preserve backward compatibility unless a migration is explicitly approved.

Prefer small orthogonal primitives over one special-case keyword per source component.

---

# 7. DESIGN TOKENS AND THEMING — PORT FIRST

Treat `packages/tokens` as a conceptual source of truth.

Build a CRONUS-native semantic token system capable of preserving:
- color roles
- surface hierarchy
- foreground hierarchy
- borders
- rings
- shadows
- radii
- spacing where applicable
- typography
- motion tokens where applicable
- Aurora theme
- Neutral/docs theme if relevant
- dark/light mode
- runtime theme switching
- runtime overrides

Do not hardcode source palette values throughout Rust renderers.

Prefer:
semantic token declarations
→ validated theme object
→ CSS custom properties/generated CSS
→ components consume semantic roles

Create tests that fail if components use forbidden raw palette values where semantic tokens are required.

A theme change must propagate predictably across the rendered subtree/page without requiring React.

---

# 8. COMPONENT MIGRATION WAVES

Migrate in dependency order.

## Wave 0 — Foundation
Port and verify:
- Button
- Input
- Label
- Badge
- Card family
- Separator
- Skeleton
- Spinner

Do not proceed until:
- variants work
- disabled/focus states work
- semantic token consumption works
- light/dark works
- basic keyboard/a11y checks pass
- screenshots/evidence exist

## Wave 1 — Forms
Port:
- Textarea
- Checkbox
- Switch
- RadioGroup
- Select
- Slider
- Toggle
- ToggleGroup
- Field
- Form
- InputOTP
- FileDropzone

Replace React Hook Form/Zod integration with CRONUS-native form/validation semantics.
Do not embed those libraries.

## Wave 2 — Overlays & Navigation
Port:
- Dialog
- Sheet
- AlertDialog
- DropdownMenu
- Popover
- HoverCard
- Tooltip
- Tabs
- Accordion
- Drawer
- Toast
- Command palette

This wave requires real keyboard/focus harnesses.
Focus trap, Escape behavior, trigger relationships, menu keyboard navigation, and ARIA semantics must be tested.

## Wave 3 — Data & Display
Port:
- Table
- DataTable
- Pagination
- Avatar
- Progress
- ScrollArea
- Calendar
- DatePicker
- Chart
- Empty
- Metric
- Kbd
- Breadcrumb

Replace TanStack/Recharts dependencies with native CRONUS/Rust/SSR/client-runtime behavior where needed.

Charts must remain data-driven, not become static placeholders.

## Wave 4 — Premium & Brand
Port:
- GlassCard
- GradientBorder
- GradientText
- SpotlightCard
- AuroraBackground
- Shimmer
- AnimatedButton
- Reveal
- LogoCarousel
- motion presets

Implement motion in a progressive-enhancement way.
Respect `prefers-reduced-motion`.
Do not sacrifice accessibility for visual parity.

---

# 9. SOURCE BEHAVIOR MUST BE CHARACTERIZED, NOT GUESSED

For every component:
1. inspect source implementation;
2. inspect tests/docs/examples;
3. enumerate props/variants;
4. enumerate visible states;
5. enumerate keyboard behavior;
6. enumerate accessibility behavior;
7. enumerate theme/token dependencies;
8. enumerate responsive behavior;
9. enumerate animation behavior;
10. write a target contract;
11. implement;
12. verify.

When a source behavior is ambiguous, create a characterization test against the source before deciding the target behavior.

---

# 10. HARNESS ENGINEERING — REQUIRED CONTROL SYSTEM

Engineer the environment around yourself so mistakes become difficult to introduce and easy to detect.

Use BOTH feedforward guides and feedback sensors.

## Feedforward controls
Maintain:
- `AGENTS.md` migration rules
- local SDD files
- architecture map
- language syntax reference
- component authoring contract
- how-to-add-component guide
- how-to-test guide
- migration checklist
- generated inventory

## Deterministic feedback sensors
Automate:
- formatting
- lint
- `cargo test`
- parser conformance
- AST golden tests
- HTML snapshot/golden tests
- semantic DOM assertions
- generated CSS/token assertions
- forbidden dependency scan
- forbidden raw color scan where applicable
- accessibility static checks
- CLI golden tests
- compose determinism
- duplicate route/symbol checks
- dead or unreachable migration code checks
- parity matrix completeness
- docs example parse/build checks

## Runtime/behavior sensors
Automate browser-level verification where possible:
- click behavior
- keyboard navigation
- focus order
- Escape
- tab loops
- form submission
- validation
- dialogs/drawers
- dropdowns
- toast lifecycle
- theme switching
- responsive layouts
- reduced motion
- RTL mode

## Visual sensors
Build a deterministic screenshot suite for canonical component states:
- light
- dark
- default
- hover where reproducible
- focus-visible
- disabled
- destructive/error/success where applicable
- mobile
- desktop

Compare SOURCE and TARGET where meaningful.
Do not require pixel identity when rendering architecture differs, but require intentional, documented visual equivalence for spacing, hierarchy, typography, state communication, and brand identity.

Set explicit tolerances and record intentional differences.

## Inferential review sensors
After deterministic gates pass:
- perform a self-review focused on architecture drift;
- perform a second pass focused on accessibility;
- perform a third pass focused on unnecessary complexity and hidden compatibility hacks.

Never use an LLM review as a substitute for deterministic checks.

---

# 11. HARNESS MUST BE AGENT-LEGIBLE

Every check should produce concise, actionable error messages.

Bad:
`snapshot mismatch`

Good:
`CRONUS-UI-PARITY C014: Button[variant=destructive][mode=dark] lost visible focus ring. Expected semantic ring token; selector [data-slot=button]:focus-visible has no ring rule.`

Prefer stable machine-readable outputs for automated checks:
- JSON
- TAP
- JUnit
- concise structured logs

Store evidence under:
`migration/evidence/<wave>/<feature>/`

---

# 12. EXTEND THE KERNEL SAFELY

When a language/runtime gap exists:

1. write/update the SDD;
2. add failing tests first or in the same atomic change;
3. implement the smallest reusable primitive;
4. run focused tests;
5. run full `cargo test`;
6. test old demos/templates for regressions;
7. add a new `.cronus` example demonstrating the capability;
8. update `LANGUAGE.md` to REAL only when verified;
9. update parity matrix;
10. commit.

If you touch a target module currently documented as having weak/zero coverage, add regression coverage as part of the same change.

Do not patch dead code paths.

Do not add blanket `allow(dead_code)` or warning suppression as a shortcut.

---

# 13. CLI / REGISTRY / COMPOSE MIGRATION

The source contains workflows beyond visual components. Preserve their USER INTENT in CRONUS-native form.

Map:
- `cronus-ui init`
- `cronus-ui add`
- `cronus-ui compose`
- `cronus-ui add-page`
- `cronus-ui theme`
- `cronus-ui upgrade`
- `create-cronus-app`
- `create-cronus-stack`
- registry discovery
- MCP discovery
- AI kit/agent doctrine

onto the target kernel's existing CLI and language architecture.

Prefer extending the existing `cronus` CLI instead of creating a second JavaScript CLI.

Candidate native flows may look like:
- `cronus new`
- `cronus add component ...`
- `cronus compose`
- `cronus add page ...`
- `cronus theme ...`
- `cronus upgrade ...`
- `cronus registry ...`

BUT DO NOT implement those exact names merely because this prompt suggests them.
First inspect existing CLI contracts and produce an SDD/API design that avoids conflicts.

The source registry must become either:
- a native CRONUS component/catalog registry; or
- generated native `.cronus` assets/contracts;
not a hidden dependency on React source.

---

# 14. STACK BUILDER / SCAFFOLDING

Port the source `stack` and scaffold intent.

A generated CRONUS app should:
- be runnable by the CRONUS kernel;
- use `.cronus` as the app source;
- use native theme/components;
- not need npm install;
- provide equivalent starter templates;
- preserve compose ergonomics;
- have deterministic generated output;
- have golden tests.

Generate at least:
- minimal/default
- SaaS
- admin/dashboard
- landing
and any other source template that materially exists.

---

# 15. DOCS / SHOWCASE MIGRATION

Do not leave documentation as stale React-only examples.

Create a CRONUS-native docs/showcase path that demonstrates:
- all components
- all variants
- theme switching
- forms
- overlays
- data components
- charts
- premium effects
- composition
- CLI/scaffolding
- copyable `.cronus` examples

Every example shown in docs MUST be executable or parser-validated by the harness.

No fake code snippets.

---

# 16. USE `cronus dump` CAREFULLY

The target kernel may contain `cronus dump` support for Next.js/HTML/generic projects.

You may use it as:
- discovery aid
- bootstrap
- comparison input

You may NOT treat its output as automatically correct.

Every dumped artifact must still pass:
- current parser
- spec requirements
- parity checks
- semantic review
- harness gates

Never mass-accept generated `.cronus` without validation.

---

# 17. SECURITY / QUALITY / ACCESSIBILITY INVARIANTS

Do not regress target kernel invariants.

Preserve:
- safe identifier handling
- sensitive-field protections
- tenant/owner isolation
- data binding rules
- authentication rules
- deterministic escaping of HTML
- no user-controlled raw markup injection unless explicitly safe and specified

UI-specific invariants:
- semantic HTML first
- accessible names
- label-control association
- keyboard operability
- visible focus
- appropriate ARIA
- reduced motion
- contrast
- RTL compatibility
- localizable strings
- no hydration assumptions

---

# 18. PERFORMANCE BUDGETS

Measure before and after.

Track:
- release binary size
- cold startup
- time to first response
- rendered HTML size for showcase pages
- CSS size
- client runtime JS size
- memory on representative demo
- parser/build validation time

Do not chase micro-optimizations before correctness.
But reject architectural regressions such as reintroducing a large JS framework to obtain source parity.

---

# 19. GIT / CHANGE MANAGEMENT

Work in small coherent commits.

Suggested commit structure:
- `spec(migration): inventory source capabilities`
- `test(harness): add parity gates for foundation components`
- `feat(theme): add semantic token model`
- `feat(ui): add button primitive and variants`
- etc.

Every commit should ideally be resumable by another agent.

At the end of each meaningful work session update:
- current spec task
- completed parity rows
- failing gates
- blockers
- exact next action

Create:
`migration/SESSION-HANDOFF.md`

Do not claim completion while there are unverified matrix rows.

---

# 20. DO NOT DO THESE THINGS

Never:
- bulk translate `.tsx` to `.cronus` and call it done;
- silently drop hard components;
- replace interactive components with static HTML;
- use screenshots as implementation;
- add arbitrary JS blobs to simulate every React component;
- keep React as an undeclared runtime dependency;
- hardcode every source token directly in Rust;
- edit generated source artifacts manually when a generator is the source of truth;
- modify dead target code paths;
- weaken tests to make migration pass;
- change expected snapshots without reviewing the behavior;
- mark a language capability REAL before it works;
- hide failures in warnings or TODOs;
- declare 100% parity based only on component names existing.

---

# 21. DEFINITION OF DONE

The migration is complete only when ALL conditions hold:

1. Every meaningful `cronus-ui` source capability has a parity-matrix row.
2. Every row is VERIFIED or explicitly approved as INTENTIONAL_DIFFERENCE.
3. All migrated examples are authored in native `.cronus`.
4. No React/Next/Bun/npm/node_modules dependency is required for normal target runtime.
5. Semantic theme/tokens are native and tested.
6. All component waves are functionally implemented.
7. Interactive components pass behavior + keyboard tests.
8. Accessibility gates pass.
9. Light/dark/theme override behavior passes.
10. RTL/localization contract passes for supported components.
11. Source-vs-target visual evidence exists for canonical states.
12. Native CLI/scaffolding/compose workflows replace the source developer intent.
13. Docs/showcase use executable `.cronus` examples.
14. Full kernel test suite passes.
15. Existing kernel demos/templates do not regress.
16. Harness checks pass in one documented command.
17. `LANGUAGE.md` accurately reflects implementation.
18. `migration/FINAL-REPORT.md` exists with metrics, known intentional differences, evidence, and migration summary.
19. Another clean environment can clone the target, run the documented setup, and reproduce the verification.
20. No unreviewed compatibility hacks remain.

---

# 22. REQUIRED FINAL REPORT

When all work is finished, produce `migration/FINAL-REPORT.md` containing:

- source SHA
- target starting SHA
- target final SHA
- number of source capabilities inventoried
- number verified
- number intentional differences
- language features added
- runtime features added
- CLI features added
- test count before/after
- accessibility coverage
- visual regression coverage
- performance before/after
- binary size before/after
- remaining technical debt
- exact reproduction commands

Include a compact table:
`Category | Total | Verified | Intentional Difference | Blocked`

Do not use prose like "mostly complete".
Use counts and evidence.

---

# 23. FIRST DELIVERABLE — BEFORE BROAD CODING

Your first response/work product must NOT be a huge code dump.

First deliver:
1. repository baseline summary;
2. source capability inventory;
3. target capability/gap inventory;
4. proposed CRONUS-native component model;
5. migration wave plan;
6. SDD files;
7. parity matrix initialized;
8. harness design;
9. first small vertical slice to implement;
10. exact acceptance criteria for that slice.

Then implement the first vertical slice and drive it to VERIFIED.

After that, continue autonomously wave by wave unless an irreversible product decision truly requires human input.

When uncertainty is local and recoverable, make the best architecture-consistent decision, record it in the SDD, and proceed.

---

# 24. TARGET END STATE

The desired end state is not:

"cronus-ui copied into cronus-kernel."

It is:

"CRONUS language and kernel have absorbed the product UI system capabilities, so developers can build the equivalent product experience natively in `.cronus`, with strong specs, deterministic contracts, a self-correcting engineering harness, and no React/Node web stack required at runtime."

Start now by reading the repository instruction files and establishing the baseline. Do not edit implementation code until the initial SDD and parity ledger exist.
