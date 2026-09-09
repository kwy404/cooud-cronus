# cooud-cronus

Cronus UI e dashboard Cooud em **`.cronus` nativo**.

**Nao se escreve HTML.** So `.cronus`. O HTML, se existir, e por tras — saida do `cronus run`, gerada pelo kernel. Nao entra no repo. Sem `.html`, sem CSS, sem TSX, sem `style_block`, sem `template`.

## Harness

```powershell
python scripts\harness.py
.\scripts\CRIAR-COMPILER.bat
.\bin\cronus.exe parse .\apps\dashboard\app.cronus
```

Ultimo run: `harness/report.md`

- forbidden HTML/CSS/TSX em `.cronus`: **PASS** (0 hits)
- `cronus parse apps/dashboard/app.cronus`: **PASS** — App `"Cooud"` · 7 entities · 6 pages · port 4747
- catalogo UI 173 / blocks 307: presente, **contrato** (nao visual VERIFIED)

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
