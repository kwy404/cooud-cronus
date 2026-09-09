# cooud-cronus

Cronus UI e dashboard Cooud em **`.cronus` nativo**.

**Nao entra markup de pagina neste repo.** So `.cronus` (preview e imagem). A pagina, se existir, e por tras — saida do `cronus run`. Sem `style_block`, sem `template`.

## Harness

```powershell
python scripts\harness.py
.\scripts\CRIAR-COMPILER.bat
.\bin\cronus.exe parse .\apps\dashboard\app.cronus
```

Ultimo run: `harness/report.md`

- markup no repo: **PASS** (0 hits, 0 arquivos proibidos)
- `cronus parse` + `validate` dashboard: **PASS**
- parse de todos os `.cronus`: **564/564 PASS**
- catalogo UI 173 / blocks 307: **comportamento nativo** (params, state, field/action, tests). Parse 564/564.

## Cooud (end to end nativo)

`apps/dashboard/app.cronus`

- rail: Inicio, Analytics, Historico, Rede, Apps, Ajustes
- Saldo, Auto + D3, Boost, Transacoes, Repasses
- Receita bruta / liquida, Pedidos, Ticket medio
- Meta de faturamento R$ 100.000 (Titanium)
- tabs Transacoes | Resumo, filtros Este mes / Todos os projetos
- chart + table vazios (bind Transaction / Payout)

Preview e **so imagem** (`docs/preview/*.png`). Sem `.html`.

## Packages

```
packages/ui        173 familias
packages/blocks    307
packages/tokens    5 presets x light/dark
packages/theme
packages/stack cli mcp ai-kit
packages/create-cronus-app
packages/create-cronus-stack
```

Compilador **nao** vai no git: `scripts/CRIAR-COMPILER.bat` clona cronus-kernel e gera `bin/cronus.exe`.
