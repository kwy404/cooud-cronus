$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Compiler = Join-Path $Root "compiler\cronus-kernel"
$Bin = Join-Path $Root "bin"

Write-Host "== cooud-cronus setup =="

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "Git nao esta no PATH."
}
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
  throw "Rust/cargo nao esta no PATH. Instale https://rustup.rs — o compilador .cronus e um binario Rust."
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root "compiler"), $Bin | Out-Null

if (-not (Test-Path (Join-Path $Compiler ".git")) -and -not (Test-Path (Join-Path $Compiler "Cargo.toml"))) {
  Write-Host "[compiler] clonando cronusmaster/cronus-kernel"
  git clone --depth 1 https://github.com/cronusmaster/cronus-kernel.git $Compiler
} else {
  Write-Host "[compiler] ja existe: $Compiler"
}

Write-Host "[compiler] cargo build --release (cronus.exe)"
Push-Location $Compiler
try {
  cargo build --release
} finally {
  Pop-Location
}

$built = Join-Path $Compiler "target\release\cronus.exe"
if (-not (Test-Path $built)) {
  $built = Join-Path $Compiler "target\release\cronus"
}
if (-not (Test-Path $built)) {
  throw "Build ok? Nao achei cronus em $Compiler\target\release"
}
Copy-Item $built (Join-Path $Bin (Split-Path $built -Leaf)) -Force
Write-Host "[ok] binario em $Bin"
Write-Host ""
Write-Host "Parse do dashboard:"
Write-Host "  .\bin\cronus.exe parse .\apps\dashboard\app.cronus"
