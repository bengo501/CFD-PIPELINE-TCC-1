param(
    [Parameter(Mandatory = $true)]
    [string]$CaseName,

    [Parameter(Mandatory = $true)]
    [int]$SimulationId,

    [double]$PressureDrop,
    [double]$AverageVelocity,
    [double]$ReynoldsNumber,
    [int]$MeshCells,
    [string]$MeshQuality,

    [string]$BackendUrl = "http://localhost:8000",

    # caminho opcional para o python (por exemplo, "py" ou "python3")
    [string]$PythonExe = "python"
)

Write-Host ""
Write-Host "=== cfd: pos-processar caso e ingerir resultados no backend ===" -ForegroundColor Cyan

# descobrir raiz do projeto a partir da pasta scripts/automation
$thisScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot   = Split-Path -Parent $thisScriptDir

$caseDir = Join-Path $projectRoot "generated\cfd\$CaseName"

if (!(Test-Path $caseDir)) {
    Write-Error "diretorio do caso nao encontrado: $caseDir"
    exit 1
}

$postprocessScript = Join-Path $projectRoot "scripts\openfoam_scripts\postprocess_results.py"
if (!(Test-Path $postprocessScript)) {
    Write-Error "script de pos-processamento nao encontrado: $postprocessScript"
    exit 1
}

Write-Host "projeto.......: $projectRoot"
Write-Host "caso openfoam.: $caseDir"
Write-Host "simulation_id.: $SimulationId"
Write-Host "backend-url...: $BackendUrl"
Write-Host ""

# montar argumentos para o postprocess_results.py
$argsList = @(
    "`"$postprocessScript`"",
    "--case-dir", "`"$caseDir`""
)

if ($PSBoundParameters.ContainsKey("PressureDrop")) {
    $argsList += @("--pressure-drop", $PressureDrop)
}
if ($PSBoundParameters.ContainsKey("AverageVelocity")) {
    $argsList += @("--average-velocity", $AverageVelocity)
}
if ($PSBoundParameters.ContainsKey("ReynoldsNumber")) {
    $argsList += @("--reynolds-number", $ReynoldsNumber)
}
if ($PSBoundParameters.ContainsKey("MeshCells")) {
    $argsList += @("--mesh-cells", $MeshCells)
}
if ($PSBoundParameters.ContainsKey("MeshQuality") -and $MeshQuality) {
    $argsList += @("--mesh-quality", "`"$MeshQuality`"")
}

Write-Host "gerando results.json com postprocess_results.py..." -ForegroundColor Yellow
Write-Host "$PythonExe $($argsList -join ' ')" -ForegroundColor DarkGray

& $PythonExe @argsList
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Error "postprocess_results.py retornou codigo $exitCode. interrompendo."
    exit $exitCode
}

$resultsJson = Join-Path $caseDir "results.json"
if (!(Test-Path $resultsJson)) {
    Write-Error "results.json nao foi encontrado em: $resultsJson"
    exit 1
}

Write-Host "results.json gerado com sucesso em: $resultsJson" -ForegroundColor Green
Write-Host ""

# chamar endpoint de ingestao no backend
$ingestUrl = "$BackendUrl/api/simulations/$SimulationId/ingest-results"

Write-Host "enviando results.json para o backend..." -ForegroundColor Yellow
Write-Host "POST $ingestUrl" -ForegroundColor DarkGray

try {
    $response = Invoke-RestMethod -Method Post -Uri $ingestUrl
    Write-Host "ingestao concluida." -ForegroundColor Green
    if ($null -ne $response) {
        Write-Host ""
        Write-Host "resposta do backend:" -ForegroundColor Cyan
        $response | ConvertTo-Json -Depth 5
    }
}
catch {
    Write-Error "falha ao chamar endpoint de ingestao: $_"
    exit 1
}

Write-Host ""
Write-Host "pronto! abra o dashboard para visualizar os resultados." -ForegroundColor Cyan

