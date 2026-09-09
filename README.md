# cronus-ui-in-cronus-language

Destino da conversão: capacidades do `cronus-ui` autoradas em `.cronus`.

Irmãs em `Desktop/cooud/`:

- `cronus-ui` — fonte React (não editar para “portar”)
- `cronus-kernel` — linguagem e runtime
- **esta pasta** — sistema de UI nativo + pack de migração

## Layout

```
cronus-ui-in-cronus-language/
  output/          ← biblioteca .cronus convertida (o produto)
  specs/           ← SDD da migração
  harness/         ← parity matrix + checklist
  migration/       ← evidence, handoff
  workspace/       ← junctions para os dois repos
```

## output/

Aqui entram os `.cronus` do design system (tokens, Button, waves seguintes).
O kernel só implementa o que a linguagem precisa para renderizar isso.

## Workspace

`scripts\CRIAR-WORKSPACE.bat` liga/clona:

- `workspace\cronus-ui`
- `workspace\cronus-kernel`

Não sobrescreve repos que já existem.
