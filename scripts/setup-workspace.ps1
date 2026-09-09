$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Workspace = Join-Path $ProjectRoot "workspace"

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null

function Ensure-Repo {
    param(
        [string]$Url,
        [string]$Path
    )

    if (Test-Path (Join-Path $Path ".git")) {
        Write-Host "[OK] Repositorio ja existe: $Path"
        return
    }

    if (Test-Path $Path) {
        $items = Get-ChildItem -Force $Path
        if ($items.Count -gt 0) {
            throw "A pasta existe e nao esta vazia: $Path"
        }
        Remove-Item $Path -Force
    }

    Write-Host "[CLONE] $Url"
    git clone $Url $Path
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git nao foi encontrado no PATH. Instale/configure o Git e rode novamente."
}

Ensure-Repo "https://github.com/pedrogbraz/cronus-ui.git" (Join-Path $Workspace "cronus-ui")
Ensure-Repo "https://github.com/cronusmaster/cronus-kernel.git" (Join-Path $Workspace "cronus-kernel")

Write-Host ""
Write-Host "Workspace pronto:"
Write-Host "  $ProjectRoot"
Write-Host ""
Write-Host "Abra esta pasta inteira no Grok e use PROMPT-GROK-MASTER.md."
