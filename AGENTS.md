# AGENTS.md — Cronus UI → Cronus Kernel Migration Workspace

Before touching implementation code:

1. Read `PROMPT-GROK-MASTER.md`.
2. Read all files under `specs/`.
3. Read `cronus-ui/AGENTS.md`, `cronus-ui/CONTRACT.md`, and relevant ADRs.
4. Read `cronus-kernel/AGENTS.md` and `cronus-kernel/LANGUAGE.md`.
5. Establish baseline evidence.
6. Update specs and parity matrix before broad implementation.

Operating model:
SPEC → IMPLEMENT → HARNESS → SELF-CORRECT → EVIDENCE → PARITY UPDATE.

Never claim completion from file existence alone.
A migrated capability is complete only when it is VERIFIED by tests/evidence.

**HTML nao entra.** Voce nao escreve HTML/CSS/TSX. O `.cronus` e a pagina. O kernel e quem emite HTML na saida do `cronus parse` / `cronus run`. `style_block` e `template "<div..."` sao escape hatch — proibidos. Fechou.

Do not use React/Next/Node as a hidden target runtime.
Do not patch dead kernel paths.
Do not weaken tests to obtain green status.

Land work on GitHub as a pull request against **cooud-cronus** (not direct push to `cronus-kernel` or `cronus-ui` main).
Kernel/UI checkouts are read for evidence; converted `.cronus` lives in `output/`.
Kernel language/runtime edits, when needed, go in the same PR series on cooud-cronus.
