# cooud-cronus

Cronus UI e dashboard Cooud em **`.cronus` nativo**.

**HTML nao entra.** O HTML e o `.cronus`. Voce escreve `app` / `page` / `section` / `entity`. O kernel vira isso em pagina. Sem TSX, sem CSS, sem `style_block`, sem `template "<div"`. Fechou.

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

O PNG em `docs/preview/` e o **alvo visual**. O HTML antigo foi para `migration/evidence/forbidden-html/` — nao volta.

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
