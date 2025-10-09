# script para configurar todos milestones e associar issues

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " configurando milestones e issues" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# verificar autenticacao
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] gh cli nao autenticado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "1. atualizando milestone existente 'Sprint 1'..." -ForegroundColor Yellow

# atualizar sprint 1 existente
gh api -X PATCH "repos/:owner/:repo/milestones/1" `
    -f title="Sprint 1 - Fundacao" `
    -f description="DSL .bed, compilador ANTLR, bed wizard, kanban/scrumban" `
    -f due_on="2025-09-22T23:59:59Z" `
    -f state="closed" | Out-Null

Write-Host "  [OK] Sprint 1 atualizado e fechado" -ForegroundColor Green

Write-Host ""
Write-Host "2. criando novos milestones..." -ForegroundColor Yellow

# funcao para criar milestone
function Create-Milestone {
    param(
        [string]$Title,
        [string]$Description,
        [string]$DueDate,
        [string]$State = "open"
    )
    
    try {
        $result = gh api -X POST "repos/:owner/:repo/milestones" `
            -f title="$Title" `
            -f description="$Description" `
            -f due_on="$DueDate" `
            -f state="$State" 2>&1 | ConvertFrom-Json
        
        Write-Host "  [OK] $Title (milestone #$($result.number))" -ForegroundColor Green
        return $result.number
    } catch {
        Write-Host "  [AVISO] $Title (pode ja existir)" -ForegroundColor Yellow
        return $null
    }
}

# criar sprints 2-8
$sprint2 = Create-Milestone `
    -Title "Sprint 2 - Modelagem" `
    -Description "Blender headless, OpenFOAM automatizado, testes E2E, documentacao" `
    -DueDate "2025-10-07T23:59:59Z" `
    -State "closed"

$sprint3 = Create-Milestone `
    -Title "Sprint 3 - Web e API" `
    -Description "FastAPI backend, React frontend, integracao full-stack" `
    -DueDate "2025-10-09T23:59:59Z" `
    -State "closed"

$sprint4 = Create-Milestone `
    -Title "Sprint 4 - Documentacao" `
    -Description "Bibliografia completa, referencial teorico, docs tecnicas" `
    -DueDate "2025-10-09T23:59:59Z" `
    -State "closed"

$sprint5 = Create-Milestone `
    -Title "Sprint 5 - Correcoes" `
    -Description "Corrigir bugs criticos, validacao, pipeline OpenFOAM completo" `
    -DueDate "2025-10-17T23:59:59Z" `
    -State "open"

$sprint6 = Create-Milestone `
    -Title "Sprint 6 - Persistencia" `
    -Description "PostgreSQL, MinIO artefatos, visualizacao 3D (Three.js)" `
    -DueDate "2025-11-01T23:59:59Z" `
    -State "open"

$sprint7 = Create-Milestone `
    -Title "Sprint 7 - Validacao Cientifica" `
    -Description "Validacao com equacao de Ergun, estudo de malha GCI" `
    -DueDate "2025-11-15T23:59:59Z" `
    -State "open"

$sprint8 = Create-Milestone `
    -Title "Sprint 8 - Finalizacao TCC1" `
    -Description "Proposta TCC1, apresentacao, documentacao final" `
    -DueDate "2025-11-30T23:59:59Z" `
    -State "open"

Write-Host ""
Write-Host "3. obtendo mapeamento de milestones..." -ForegroundColor Yellow

# obter todos milestones
$allMilestones = gh api "repos/:owner/:repo/milestones?state=all" | ConvertFrom-Json

# criar hashtable title -> number
$milestoneMap = @{}
foreach ($ms in $allMilestones) {
    $milestoneMap[$ms.title] = $ms.number
    Write-Host "  $($ms.title) = milestone #$($ms.number)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "4. associando issues aos milestones..." -ForegroundColor Yellow

# funcao para associar issue
function Set-IssueMilestone {
    param(
        [int]$IssueNumber,
        [string]$MilestoneTitle
    )
    
    if ($milestoneMap.ContainsKey($MilestoneTitle)) {
        $milestoneNumber = $milestoneMap[$MilestoneTitle]
        
        try {
            gh api -X PATCH "repos/:owner/:repo/issues/$IssueNumber" `
                -F milestone=$milestoneNumber | Out-Null
            
            Write-Host "  [OK] issue #$IssueNumber -> $MilestoneTitle" -ForegroundColor Green
        } catch {
            Write-Host "  [ERRO] issue #$IssueNumber -> $MilestoneTitle" -ForegroundColor Red
        }
    } else {
        Write-Host "  [ERRO] milestone '$MilestoneTitle' nao encontrado" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Sprint 1 - Fundacao..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 1 -MilestoneTitle "Sprint 1 - Fundacao"
Set-IssueMilestone -IssueNumber 2 -MilestoneTitle "Sprint 1 - Fundacao"
Set-IssueMilestone -IssueNumber 7 -MilestoneTitle "Sprint 1 - Fundacao"
Set-IssueMilestone -IssueNumber 8 -MilestoneTitle "Sprint 1 - Fundacao"

Write-Host ""
Write-Host "Sprint 2 - Modelagem..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 3 -MilestoneTitle "Sprint 2 - Modelagem"
Set-IssueMilestone -IssueNumber 4 -MilestoneTitle "Sprint 2 - Modelagem"
Set-IssueMilestone -IssueNumber 5 -MilestoneTitle "Sprint 2 - Modelagem"
Set-IssueMilestone -IssueNumber 6 -MilestoneTitle "Sprint 2 - Modelagem"

Write-Host ""
Write-Host "Sprint 3 - Web e API..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 18 -MilestoneTitle "Sprint 3 - Web e API"
Set-IssueMilestone -IssueNumber 19 -MilestoneTitle "Sprint 3 - Web e API"

Write-Host ""
Write-Host "Sprint 5 - Correcoes..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 20 -MilestoneTitle "Sprint 5 - Correcoes"
Set-IssueMilestone -IssueNumber 21 -MilestoneTitle "Sprint 5 - Correcoes"
Set-IssueMilestone -IssueNumber 22 -MilestoneTitle "Sprint 5 - Correcoes"
Set-IssueMilestone -IssueNumber 25 -MilestoneTitle "Sprint 5 - Correcoes"

Write-Host ""
Write-Host "Sprint 6 - Persistencia..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 23 -MilestoneTitle "Sprint 6 - Persistencia"
Set-IssueMilestone -IssueNumber 26 -MilestoneTitle "Sprint 6 - Persistencia"
Set-IssueMilestone -IssueNumber 27 -MilestoneTitle "Sprint 6 - Persistencia"

Write-Host ""
Write-Host "Sprint 7 - Validacao Cientifica..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 28 -MilestoneTitle "Sprint 7 - Validacao Cientifica"
Set-IssueMilestone -IssueNumber 29 -MilestoneTitle "Sprint 7 - Validacao Cientifica"

Write-Host ""
Write-Host "Sprint 8 - Finalizacao TCC1..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 30 -MilestoneTitle "Sprint 8 - Finalizacao TCC1"
Set-IssueMilestone -IssueNumber 31 -MilestoneTitle "Sprint 8 - Finalizacao TCC1"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " configuracao completa!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "resumo:"
Write-Host "- 8 milestones criados/atualizados"
Write-Host "- 17 issues associadas aos milestones"
Write-Host "- 4 milestones fechados (sprints 1-4)"
Write-Host "- 4 milestones abertos (sprints 5-8)"
Write-Host ""
Write-Host "verificar em:" -ForegroundColor Cyan
Write-Host "  https://github.com/bengo501/CFD-PIPELINE-TCC-1/milestones" -ForegroundColor Cyan
Write-Host ""

