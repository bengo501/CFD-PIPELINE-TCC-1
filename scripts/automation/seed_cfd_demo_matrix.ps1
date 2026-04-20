param(
    [string]$BackendUrl = "http://localhost:8000"
)

Write-Host ""
Write-Host "=== cfd: criar matriz de simulacoes demo (2 de cada status) ===" -ForegroundColor Cyan

# descobrir raiz do projeto a partir da pasta scripts/automation
$thisScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot   = Split-Path -Parent $thisScriptDir

function Get-OrCreateBed {
    param(
        [string]$BedName,
        [string]$Description
    )

    # tentar buscar por nome (via parametro search)
    $searchUrl = "$BackendUrl/api/beds?search=$([uri]::EscapeDataString($BedName))"
    try {
        $resp = Invoke-RestMethod -Method Get -Uri $searchUrl
        if ($resp -and $resp.total -gt 0 -and $resp.items.Count -gt 0) {
            $bed = $resp.items[0]
            Write-Host "bed existente encontrado: id=$($bed.id) nome=$($bed.name)" -ForegroundColor DarkGreen
            return $bed
        }
    }
    catch {
        Write-Host "nao foi possivel buscar bed '$BedName', tentando criar..." -ForegroundColor DarkYellow
    }

    # criar novo bed
    $bedBody = @{
        name        = $BedName
        description = $Description
        diameter    = 0.06
        height      = 0.12
        wall_thickness   = 0.002
        particle_count    = 800
        particle_diameter = 0.004
        particle_kind     = "sphere"
        packing_method    = "rigid_body"
        porosity          = 0.42
        parameters_json   = $null
    }

    $bedUrl = "$BackendUrl/api/beds"
    Write-Host "criando bed demo '$BedName'..." -ForegroundColor Yellow
    try {
        $bed = Invoke-RestMethod -Method Post -Uri $bedUrl -ContentType "application/json" -Body ($bedBody | ConvertTo-Json -Depth 5)
        Write-Host "bed criado: id=$($bed.id)" -ForegroundColor Green
        return $bed
    }
    catch {
        Write-Host "falha ao criar bed '$BedName': $_" -ForegroundColor Red
        throw
    }
}

function New-DemoSimulation {
    param(
        [object]$Bed,
        [string]$Name,
        [string]$Description,
        [string]$Regime,
        [string]$Status,
        [int]$Progress,
        [double]$PressureDrop = $null,
        [double]$AverageVelocity = $null,
        [double]$ReynoldsNumber = $null,
        [switch]$CreateResults
    )

    Write-Host ""
    Write-Host "---- criando simulacao demo: $Name ----" -ForegroundColor Yellow

    # 1) criar simulacao (status inicial 'pending')
    $simBody = @{
        bed_id           = $Bed.id
        name             = $Name
        description      = $Description
        regime           = $Regime
        inlet_velocity   = 0.18
        fluid_density    = 1000.0
        fluid_viscosity  = 0.001
        solver           = "simpleFoam"
        max_iterations   = 900
        convergence_criteria = 0.0001
        parameters_json  = @{}
    }

    $simUrl = "$BackendUrl/api/simulations"
    $simulation = Invoke-RestMethod -Method Post -Uri $simUrl -ContentType "application/json" -Body ($simBody | ConvertTo-Json -Depth 5)
    Write-Host "simulacao criada: id=$($simulation.id)" -ForegroundColor Green

    # 2) atualizar status/progresso e metricas principais
    $updateBody = @{
        status           = $Status
        progress         = $Progress
    }
    if ($PressureDrop -ne $null)    { $updateBody["pressure_drop"]    = $PressureDrop }
    if ($AverageVelocity -ne $null) { $updateBody["average_velocity"] = $AverageVelocity }
    if ($ReynoldsNumber -ne $null)  { $updateBody["reynolds_number"]  = $ReynoldsNumber }

    $updateUrl = "$BackendUrl/api/simulations/$($simulation.id)"
    $simulation = Invoke-RestMethod -Method Patch -Uri $updateUrl -ContentType "application/json" -Body ($updateBody | ConvertTo-Json -Depth 5)
    Write-Host "status atualizado para '$($simulation.status)' (progress=$($simulation.progress)%)" -ForegroundColor Green

    # 3) criar resultados detalhados (apenas para simulacoes completadas)
    if ($CreateResults) {
        $resultsUrl = "$BackendUrl/api/results/bulk"
        $results = @(
            @{
                simulation_id = $simulation.id
                result_type   = "metric"
                name          = "pressure_drop"
                value         = $PressureDrop
                unit          = "Pa"
                data_json     = $null
                file_path     = $null
                file_type     = $null
                timestep      = $null
            },
            @{
                simulation_id = $simulation.id
                result_type   = "metric"
                name          = "average_velocity"
                value         = $AverageVelocity
                unit          = "m/s"
                data_json     = $null
                file_path     = $null
                file_type     = $null
                timestep      = $null
            },
            @{
                simulation_id = $simulation.id
                result_type   = "metric"
                name          = "reynolds_number"
                value         = $ReynoldsNumber
                unit          = ""
                data_json     = $null
                file_path     = $null
                file_type     = $null
                timestep      = $null
            }
        )

        Write-Host "criando resultados metricos para simulacao id=$($simulation.id)..." -ForegroundColor Yellow
        $null = Invoke-RestMethod -Method Post -Uri $resultsUrl -ContentType "application/json" -Body ($results | ConvertTo-Json -Depth 5)
        Write-Host "resultados criados." -ForegroundColor Green
    }
}

try {
    $bed = Get-OrCreateBed -BedName "demo_bed_matrix" -Description "leito demo com 2 simulacoes por status"

    # 2 pendentes
    New-DemoSimulation -Bed $bed `
        -Name "demo_pending_1" `
        -Description "simulacao pendente 1" `
        -Regime "laminar" `
        -Status "pending" `
        -Progress 0

    New-DemoSimulation -Bed $bed `
        -Name "demo_pending_2" `
        -Description "simulacao pendente 2" `
        -Regime "turbulent" `
        -Status "pending" `
        -Progress 0

    # 2 em execucao
    New-DemoSimulation -Bed $bed `
        -Name "demo_running_1" `
        -Description "simulacao em execucao 1" `
        -Regime "laminar" `
        -Status "running" `
        -Progress 30

    New-DemoSimulation -Bed $bed `
        -Name "demo_running_2" `
        -Description "simulacao em execucao 2" `
        -Regime "turbulent" `
        -Status "running" `
        -Progress 70

    # 2 concluidas (com resultados)
    New-DemoSimulation -Bed $bed `
        -Name "demo_completed_1" `
        -Description "simulacao concluida 1" `
        -Regime "laminar" `
        -Status "completed" `
        -Progress 100 `
        -PressureDrop 100.0 `
        -AverageVelocity 0.20 `
        -ReynoldsNumber 900 `
        -CreateResults

    New-DemoSimulation -Bed $bed `
        -Name "demo_completed_2" `
        -Description "simulacao concluida 2" `
        -Regime "turbulent" `
        -Status "completed" `
        -Progress 100 `
        -PressureDrop 140.0 `
        -AverageVelocity 0.26 `
        -ReynoldsNumber 1300 `
        -CreateResults

    # 2 falhadas
    New-DemoSimulation -Bed $bed `
        -Name "demo_failed_1" `
        -Description "simulacao que falhou 1" `
        -Regime "laminar" `
        -Status "failed" `
        -Progress 40

    New-DemoSimulation -Bed $bed `
        -Name "demo_failed_2" `
        -Description "simulacao que falhou 2" `
        -Regime "turbulent" `
        -Status "failed" `
        -Progress 80
}
catch {
    Write-Error "falha ao criar matriz de simulacoes demo: $_"
    exit 1
}

Write-Host ""
Write-Host "pronto! 2 simulacoes de cada status criadas. confira no dashboard e nas paginas de simulacao/banco de dados." -ForegroundColor Cyan

