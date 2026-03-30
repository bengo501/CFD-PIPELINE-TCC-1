param(
    [string]$BackendUrl = "http://localhost:8000"
)

Write-Host ""
Write-Host "=== cfd: criar casos de teste demo no backend ===" -ForegroundColor Cyan

# descobrir raiz do projeto a partir da pasta scripts/automation
$thisScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot   = Split-Path -Parent $thisScriptDir

$generatedCfdDir = Join-Path $projectRoot "generated\cfd"
if (!(Test-Path $generatedCfdDir)) {
    New-Item -ItemType Directory -Path $generatedCfdDir | Out-Null
}

function New-DemoCase {
    param(
        [string]$BedName,
        [string]$SimulationName,
        [string]$CaseDirName,
        [double]$PressureDrop,
        [double]$AverageVelocity,
        [double]$ReynoldsNumber,
        [int]$MeshCells
    )

    Write-Host ""
    Write-Host "---- criando demo: $SimulationName ----" -ForegroundColor Yellow

    # 1) criar bed (ou reutilizar se ja existir)
    $bedSearchUrl = "$BackendUrl/api/beds?name=$([uri]::EscapeDataString($BedName))"
    try {
        $existingBeds = Invoke-RestMethod -Method Get -Uri $bedSearchUrl
    }
    catch {
        $existingBeds = @()
    }

    if ($existingBeds -and $existingBeds.Count -gt 0) {
        $bed = $existingBeds[0]
        Write-Host "bed existente encontrado: id=$($bed.id) nome=$($bed.name)" -ForegroundColor DarkGreen
    }
    else {
        $bedBody = @{
            name        = $BedName
            description = "leito demo criado por seed_cfd_demo_data.ps1"
            diameter    = 0.05
            height      = 0.10
            wall_thickness = 0.002
            particle_count  = 100
            particle_diameter = 0.005
            particle_kind     = "sphere"
            packing_method    = "rigid_body"
            porosity          = 0.40
            parameters_json   = $null
        }

        $bedUrl = "$BackendUrl/api/beds"
        Write-Host "criando bed demo '$BedName'..." -ForegroundColor Yellow
        $bed = Invoke-RestMethod -Method Post -Uri $bedUrl -ContentType "application/json" -Body ($bedBody | ConvertTo-Json -Depth 5)
        Write-Host "bed criado: id=$($bed.id)" -ForegroundColor Green
    }

    # 2) criar simulacao
    $simBody = @{
        bed_id      = $bed.id
        name        = $SimulationName
        description = "simulacao demo sem openfoam real (dados sinteticos)"
        regime      = "laminar"
        inlet_velocity   = 0.10
        fluid_density    = 1000.0
        fluid_viscosity  = 0.001
        solver           = "simpleFoam"
        max_iterations   = 1000
        convergence_criteria = 0.0001
        case_directory   = "generated/cfd/$CaseDirName"
        parameters_json  = @{}
    }

    $simUrl = "$BackendUrl/api/simulations"
    Write-Host "criando simulacao demo '$SimulationName'..." -ForegroundColor Yellow
    $simulation = Invoke-RestMethod -Method Post -Uri $simUrl -ContentType "application/json" -Body ($simBody | ConvertTo-Json -Depth 5)
    Write-Host "simulacao criada: id=$($simulation.id)" -ForegroundColor Green

    # 3) gerar results.json sintético no diretorio esperado
    $caseDir = Join-Path $generatedCfdDir $CaseDirName
    if (!(Test-Path $caseDir)) {
        New-Item -ItemType Directory -Path $caseDir | Out-Null
    }

    $now = Get-Date

    $results = @{
        case_name        = $CaseDirName
        created_at       = $now.ToString("s")
        completed_at     = $now.AddMinutes(2).ToString("s")
        solver           = "simpleFoam"
        execution_time   = 120.0
        mesh_cells_count = $MeshCells
        mesh_quality     = "good"
        pressure_drop    = $PressureDrop
        average_velocity = $AverageVelocity
        reynolds_number  = $ReynoldsNumber
        log_file         = "generated/cfd/$CaseDirName/log.simpleFoam"
        metrics          = @{
            pressure_drop = @{
                value = $PressureDrop
                unit  = "Pa"
            }
            average_velocity = @{
                value = $AverageVelocity
                unit  = "m/s"
            }
            reynolds_number = @{
                value = $ReynoldsNumber
                unit  = ""
            }
        }
    }

    $resultsPath = Join-Path $caseDir "results.json"
    $results | ConvertTo-Json -Depth 5 | Set-Content -Path $resultsPath -Encoding UTF8
    Write-Host "results.json demo criado em: $resultsPath" -ForegroundColor Green

    # 4) ingerir resultados no backend
    $ingestUrl = "$BackendUrl/api/simulations/$($simulation.id)/ingest-results"
    Write-Host "ingerindo resultados no backend..." -ForegroundColor Yellow
    $null = Invoke-RestMethod -Method Post -Uri $ingestUrl
    Write-Host "ingestao concluida para simulacao id=$($simulation.id)." -ForegroundColor Green
}

try {
    # dois casos demo simples
    New-DemoCase -BedName "demo_bed_fino" -SimulationName "demo_sim_fino" -CaseDirName "demo_sim_fino" `
        -PressureDrop 120.0 -AverageVelocity 0.20 -ReynoldsNumber 800 -MeshCells 150000

    New-DemoCase -BedName "demo_bed_grosso" -SimulationName "demo_sim_grosso" -CaseDirName "demo_sim_grosso" `
        -PressureDrop 80.0 -AverageVelocity 0.15 -ReynoldsNumber 600 -MeshCells 90000
}
catch {
    Write-Error "falha ao criar dados demo: $_"
    exit 1
}

Write-Host ""
Write-Host "pronto! abra o dashboard e confira as simulacoes demo criadas." -ForegroundColor Cyan

