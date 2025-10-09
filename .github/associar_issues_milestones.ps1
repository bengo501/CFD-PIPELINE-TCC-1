# script para associar issues aos milestones (sprints)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " associando issues aos milestones" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# verificar autenticacao
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] gh cli nao autenticado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "obtendo milestones..." -ForegroundColor Yellow

# obter todos milestones
$milestonesJson = gh api repos/:owner/:repo/milestones --paginate
$milestones = $milestonesJson | ConvertFrom-Json

# criar hashtable milestone_title -> milestone_number
$milestoneMap = @{}
foreach ($milestone in $milestones) {
    $milestoneMap[$milestone.title] = $milestone.number
    Write-Host "  $($milestone.title) = #$($milestone.number)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "associando issues aos milestones..." -ForegroundColor Yellow

# funcao para associar issue a milestone
function Set-IssueMilestone {
    param(
        [int]$IssueNumber,
        [string]$MilestoneTitle
    )
    
    if ($milestoneMap.ContainsKey($MilestoneTitle)) {
        $milestoneNumber = $milestoneMap[$MilestoneTitle]
        
        try {
            gh api -X PATCH "repos/:owner/:repo/issues/$IssueNumber" `
                -f milestone=$milestoneNumber 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] issue #$IssueNumber -> $MilestoneTitle" -ForegroundColor Green
            } else {
                Write-Host "  [ERRO] issue #$IssueNumber -> $MilestoneTitle" -ForegroundColor Red
            }
        } catch {
            Write-Host "  [ERRO] issue #$IssueNumber -> $MilestoneTitle" -ForegroundColor Red
        }
    } else {
        Write-Host "  [AVISO] milestone '$MilestoneTitle' nao encontrado" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "sprint 1 - fundacao..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 1 -MilestoneTitle "Sprint 1 - Fundacao"
Set-IssueMilestone -IssueNumber 2 -MilestoneTitle "Sprint 1 - Fundacao"
Set-IssueMilestone -IssueNumber 7 -MilestoneTitle "Sprint 1 - Fundacao"
Set-IssueMilestone -IssueNumber 8 -MilestoneTitle "Sprint 1 - Fundacao"

Write-Host ""
Write-Host "sprint 2 - modelagem..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 3 -MilestoneTitle "Sprint 2 - Modelagem"
Set-IssueMilestone -IssueNumber 4 -MilestoneTitle "Sprint 2 - Modelagem"
Set-IssueMilestone -IssueNumber 5 -MilestoneTitle "Sprint 2 - Modelagem"
Set-IssueMilestone -IssueNumber 6 -MilestoneTitle "Sprint 2 - Modelagem"

Write-Host ""
Write-Host "sprint 3 - web e api..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 18 -MilestoneTitle "Sprint 3 - Web e API"
Set-IssueMilestone -IssueNumber 19 -MilestoneTitle "Sprint 3 - Web e API"

Write-Host ""
Write-Host "sprint 5 - correcoes (pendentes)..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 20 -MilestoneTitle "Sprint 5 - Correcoes"
Set-IssueMilestone -IssueNumber 21 -MilestoneTitle "Sprint 5 - Correcoes"
Set-IssueMilestone -IssueNumber 22 -MilestoneTitle "Sprint 5 - Correcoes"
Set-IssueMilestone -IssueNumber 25 -MilestoneTitle "Sprint 5 - Correcoes"

Write-Host ""
Write-Host "sprint 6 - persistencia (pendentes)..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 23 -MilestoneTitle "Sprint 6 - Persistencia"
Set-IssueMilestone -IssueNumber 26 -MilestoneTitle "Sprint 6 - Persistencia"
Set-IssueMilestone -IssueNumber 27 -MilestoneTitle "Sprint 6 - Persistencia"

Write-Host ""
Write-Host "sprint 7 - validacao cientifica (pendentes)..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 28 -MilestoneTitle "Sprint 7 - Validacao Cientifica"
Set-IssueMilestone -IssueNumber 29 -MilestoneTitle "Sprint 7 - Validacao Cientifica"

Write-Host ""
Write-Host "sprint 8 - finalizacao tcc1 (pendentes)..." -ForegroundColor Cyan
Set-IssueMilestone -IssueNumber 30 -MilestoneTitle "Sprint 8 - Finalizacao TCC1"
Set-IssueMilestone -IssueNumber 31 -MilestoneTitle "Sprint 8 - Finalizacao TCC1"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " associacoes concluidas!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "verificar em:" -ForegroundColor Cyan
Write-Host "  https://github.com/bengo501/CFD-PIPELINE-TCC-1/milestones" -ForegroundColor Cyan
Write-Host ""
Write-Host "listar issues por milestone:" -ForegroundColor Cyan
Write-Host "  gh issue list --milestone 'Sprint 5 - Correcoes'" -ForegroundColor Gray
Write-Host ""

