param(
    [string]$BackendUrl = "http://localhost:8000"
)

Write-Host ""
Write-Host "=== cfd: criando TODOS os dados demo (baseline + estados extras) ===" -ForegroundColor Cyan

$thisScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

try {
    # script baseline: dois casos concluidos com results.json sintetico
    & (Join-Path $thisScriptDir "seed_cfd_demo_data.ps1") -BackendUrl $BackendUrl

    # script extra: diferentes estados de simulacao + resultados metricos
    & (Join-Path $thisScriptDir "seed_cfd_demo_statuses.ps1") -BackendUrl $BackendUrl
}
catch {
    Write-Error "falha ao executar scripts de seed demo: $_"
    exit 1
}

Write-Host ""
Write-Host "pronto! abra o frontend e confira Dashboard, Simulacao e Banco de Dados com varios exemplos." -ForegroundColor Cyan

