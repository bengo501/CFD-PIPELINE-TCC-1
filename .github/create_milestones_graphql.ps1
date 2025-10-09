# script para criar milestones via github api graphql

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " criando milestones (sprints) via api" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# verificar autenticacao
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] gh cli nao autenticado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "obtendo informacoes do repositorio..." -ForegroundColor Yellow

# obter owner e repo do repositorio atual
$repoInfo = gh repo view --json owner,name | ConvertFrom-Json
$owner = $repoInfo.owner.login
$repo = $repoInfo.name

Write-Host "repositorio: $owner/$repo" -ForegroundColor Green

# obter repository id
$query = @"
query {
  repository(owner: \"$owner\", name: \"$repo\") {
    id
  }
}
"@

$repoId = (gh api graphql -f query=$query | ConvertFrom-Json).data.repository.id
Write-Host "repository id: $repoId" -ForegroundColor Green

Write-Host ""
Write-Host "criando milestones (sprints)..." -ForegroundColor Yellow

# funcao para criar milestone
function Create-Milestone {
    param(
        [string]$RepositoryId,
        [string]$Title,
        [string]$Description,
        [string]$DueDate
    )
    
    $mutation = @"
mutation {
  createMilestone(input: {
    repositoryId: \"$RepositoryId\"
    title: \"$Title\"
    description: \"$Description\"
    dueOn: \"$DueDate\"
  }) {
    milestone {
      number
      title
    }
  }
}
"@
    
    try {
        $result = gh api graphql -f query=$mutation 2>&1
        if ($LASTEXITCODE -eq 0) {
            $milestoneData = ($result | ConvertFrom-Json).data.createMilestone.milestone
            Write-Host "  [OK] criado: $Title (#$($milestoneData.number))" -ForegroundColor Green
            return $milestoneData.number
        } else {
            Write-Host "  [AVISO] $Title ja existe ou erro" -ForegroundColor Yellow
            return $null
        }
    } catch {
        Write-Host "  [AVISO] $Title ja existe" -ForegroundColor Yellow
        return $null
    }
}

# criar sprints
Write-Host ""

$sprint1 = Create-Milestone -RepositoryId $repoId `
    -Title "Sprint 1 - Fundacao" `
    -Description "DSL .bed, compilador ANTLR, bed wizard, kanban/scrumban" `
    -DueDate "2025-09-22T23:59:59Z"

$sprint2 = Create-Milestone -RepositoryId $repoId `
    -Title "Sprint 2 - Modelagem" `
    -Description "Blender headless, OpenFOAM automatizado, testes E2E, documentacao" `
    -DueDate "2025-10-07T23:59:59Z"

$sprint3 = Create-Milestone -RepositoryId $repoId `
    -Title "Sprint 3 - Web e API" `
    -Description "FastAPI backend, React frontend, integracao full-stack" `
    -DueDate "2025-10-09T23:59:59Z"

$sprint4 = Create-Milestone -RepositoryId $repoId `
    -Title "Sprint 4 - Documentacao" `
    -Description "Bibliografia completa, referencial teorico, docs tecnicas" `
    -DueDate "2025-10-09T23:59:59Z"

$sprint5 = Create-Milestone -RepositoryId $repoId `
    -Title "Sprint 5 - Correcoes" `
    -Description "Corrigir bugs, validacao, pipeline OpenFOAM completo" `
    -DueDate "2025-10-17T23:59:59Z"

$sprint6 = Create-Milestone -RepositoryId $repoId `
    -Title "Sprint 6 - Persistencia" `
    -Description "PostgreSQL, MinIO, visualizacao 3D (Three.js)" `
    -DueDate "2025-11-01T23:59:59Z"

$sprint7 = Create-Milestone -RepositoryId $repoId `
    -Title "Sprint 7 - Validacao Cientifica" `
    -Description "Validacao Ergun, estudo de malha GCI" `
    -DueDate "2025-11-15T23:59:59Z"

$sprint8 = Create-Milestone -RepositoryId $repoId `
    -Title "Sprint 8 - Finalizacao TCC1" `
    -Description "Proposta TCC1, apresentacao, documentacao final" `
    -DueDate "2025-11-30T23:59:59Z"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " milestones criados com sucesso!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "verificar milestones em:" -ForegroundColor Cyan
Write-Host "  https://github.com/$owner/$repo/milestones" -ForegroundColor Cyan
Write-Host ""

