# compiler

O `.cronus` **não roda sozinho**. O compilador é o binário `cronus` do repo:

https://github.com/cronusmaster/cronus-kernel

Este diretório **não** commita o Rust. `scripts/setup.ps1` clona o kernel aqui e faz `cargo build --release`.

```
scripts\CRIAR-COMPILER.bat
.\bin\cronus.exe parse .\apps\dashboard\app.cronus
.\bin\cronus.exe run .\apps\dashboard\app.cronus
```

Requisitos: Git + Rust (`rustup`). Sem Node/npm para o runtime.
