# cooud-cronus

Cronus UI em `.cronus` + dashboard Cooud.

**Nao e um app Node.** Nao tem `node_modules`. Sem o compilador o `.cronus` e so fonte — nao quebra o git, mas nao executa.

## Como nao quebrar

| Peca | Onde | Como entra no clone |
|---|---|---|
| Pacotes UI | `packages/ui` (173 `.cronus`) | ja no git |
| Blocks | `packages/blocks` (307) | ja no git |
| Tokens / theme | `packages/tokens` `packages/theme` | ja no git |
| Stack / cli / mcp / ai-kit | `packages/` | ja no git |
| create-cronus-app / create-cronus-stack | `packages/` | ja no git |
| App dashboard | `apps/dashboard/app.cronus` | ja no git |
| Compilador `cronus` | `compiler/cronus-kernel` → `bin/cronus.exe` | **nao** vai no git; `scripts/setup.ps1` clona + `cargo build` |

```powershell
git clone https://github.com/kwy404/cooud-cronus.git
cd cooud-cronus
.\scripts\CRIAR-COMPILER.bat
.\bin\cronus.exe parse .\apps\dashboard\app.cronus
```

Precisa de **Rust** (`https://rustup.rs`) e **Git**. Sem isso o parse nao roda — os arquivos `.cronus` continuam no repo.

## Packages (tudo no git)

```
packages/
  tokens/              5 presets x light/dark (CSS vars do cronus-ui)
  theme/               aurora / neutral / midnight / sunset / emerald
  ui/                  173 familias (barrel inteiro, CVA variants, slots, exports)
  blocks/              307 blocks do registry
  stack/               scaffold nativo
  cli/                 -> bin/cronus.exe (nao npm)
  mcp/                 14 tools, sem Node
  ai-kit/              doutrina
  create-cronus-app/   templates default / dashboard / marketing
  create-cronus-stack/ compose nativo
apps/
  dashboard/           dashboard.cooud.com
compiler/              cronus-kernel (clone no setup)
```

Regenerar o catalogo: `python scripts/gen-packages.py` (le `../cronus-ui`).

## Cooud Dashboard

`cronus parse apps/dashboard/app.cronus` → App `"Cooud"` · 1 page · port 4747

![Cooud Dashboard](docs/preview/cooud-dashboard.png)

## Catalogo

![Wave 0](docs/preview/showcase-w0.png)
![Wave 1](docs/preview/showcase-w1.png)
![Wave 2](docs/preview/showcase-w2.png)
![Wave 3](docs/preview/showcase-w3.png)
![Wave 4](docs/preview/showcase-w4.png)
