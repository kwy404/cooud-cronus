# packages

Pacotes nativos `.cronus` (nao npm). Espelho do monorepo cronus-ui.

| Pasta | Fonte | Conteudo |
|---|---|---|
| `tokens/` | `@cronus-ui/tokens` | 11 arquivos (5 presets × light/dark) |
| `theme/` | `@cronus-ui/theme` | aurora / neutral / midnight / sunset / emerald |
| `ui/` | `@cronus-ui/ui` | **173** familias (barrel inteiro) |
| `blocks/` | `registry/*.json` | **307** blocks |
| `stack/` | `@cronus-ui/stack` | scaffold nativo |
| `cli/` | `cronus-ui` CLI | aponta para `bin/cronus.exe` |
| `mcp/` | `packages/mcp` | 14 tools, sem Node |
| `ai-kit/` | `@cronus-ui/ai-kit` | doutrina |
| `create-cronus-app/` | `create-cronus-app` | templates default / dashboard / marketing |
| `create-cronus-stack/` | `create-cronus-stack` | compose nativo |

Pastas no disco: ai-kit, blocks, cli, create-cronus-app, create-cronus-stack, mcp, stack, theme, tokens, ui

Compilador: `scripts/setup.ps1` → `compiler/cronus-kernel` → `bin/cronus.exe`.
