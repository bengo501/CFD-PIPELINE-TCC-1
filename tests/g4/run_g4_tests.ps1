# Script PowerShell para executar testes G4
# Uso: .\run_g4_tests.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONJUNTO G4 - TESTES AUTOMATIZADOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se backend está rodando
Write-Host "[1/5] Verificando backend..." -ForegroundColor Yellow
$backendOnline = $false
$endpoints = @(
    "http://localhost:8000/health",
    "http://localhost:8000/api/status",
    "http://localhost:8000/docs"
)
foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -in @(200, 404)) {
            $backendOnline = $true
            break
        }
    } catch {
        continue
    }
}
if (-not $backendOnline) {
    Write-Host "  ✗ Backend não está respondendo!" -ForegroundColor Red
    Write-Host "     Inicie o backend antes de executar os testes." -ForegroundColor Yellow
    Write-Host "     Execute: cd backend; .\EXECUTAR.bat" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "  ✓ Backend está rodando" -ForegroundColor Green
}

# Verificar pré-requisitos
Write-Host ""
Write-Host "[2/5] Verificando pré-requisitos..." -ForegroundColor Yellow

# Verificar Blender
$blenderFound = $false
$blenderPaths = @(
    "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
)
foreach ($path in $blenderPaths) {
    if (Test-Path $path) {
        Write-Host "  ✓ Blender encontrado: $path" -ForegroundColor Green
        $blenderFound = $true
        break
    }
}
if (-not $blenderFound) {
    Write-Host "  ⚠ Blender não encontrado (alguns testes podem falhar)" -ForegroundColor Yellow
}

# Verificar WSL
try {
    $wsl = wsl --list --quiet 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ WSL está instalado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ WSL não encontrado (testes CFD podem falhar)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ WSL não encontrado (testes CFD podem falhar)" -ForegroundColor Yellow
}

# Executar testes
Write-Host ""
Write-Host "[3/5] Executando testes G4..." -ForegroundColor Yellow
Write-Host ""

$testScript = Join-Path $PSScriptRoot "test_g4_suite.py"
$pythonCmd = "python"

# Verificar Python
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "  Usando: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ Python não encontrado!" -ForegroundColor Red
    exit 1
}

# Executar script Python (versão simplificada que usa API)
$testScriptSimplified = Join-Path $PSScriptRoot "test_g4_simplified.py"
Write-Host "  Executando: python $testScriptSimplified" -ForegroundColor Gray
Write-Host ""

& $pythonCmd $testScriptSimplified

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[4/5] Testes concluídos!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[4/5] Alguns testes falharam. Verifique os logs." -ForegroundColor Yellow
}

# Gerar resumo
Write-Host ""
Write-Host "[5/5] Gerando resumo..." -ForegroundColor Yellow

$resultsDir = Join-Path $PSScriptRoot "results"
if (Test-Path $resultsDir) {
    $metricsFile = Join-Path $resultsDir "g4_metrics.csv"
    $reportFile = Join-Path $resultsDir "g4_report.txt"
    
    if (Test-Path $metricsFile) {
        Write-Host "  ✓ Métricas: $metricsFile" -ForegroundColor Green
    }
    
    if (Test-Path $reportFile) {
        Write-Host "  ✓ Relatório: $reportFile" -ForegroundColor Green
        Write-Host ""
        Write-Host "Últimas linhas do relatório:" -ForegroundColor Cyan
        Get-Content $reportFile -Tail 20
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTES CONCLUÍDOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

