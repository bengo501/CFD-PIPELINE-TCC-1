# script para adicionar issues e milestones ao github project existente

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " adicionando issues ao github project" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# verificar autenticacao
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] gh cli nao autenticado" -ForegroundColor Red
    exit 1
}

# informacoes do projeto
$PROJECT_URL = "https://github.com/users/bengo501/projects/2"
$PROJECT_NUMBER = 2

Write-Host ""
Write-Host "projeto alvo: $PROJECT_URL" -ForegroundColor Green

Write-Host ""
Write-Host "1. obtendo project id..." -ForegroundColor Yellow

# obter project id via graphql
$query = @"
query {
  user(login: \"bengo501\") {
    projectV2(number: $PROJECT_NUMBER) {
      id
      title
    }
  }
}
"@

try {
    $result = gh api graphql -f query=$query | ConvertFrom-Json
    $projectId = $result.data.user.projectV2.id
    $projectTitle = $result.data.user.projectV2.title
    
    Write-Host "  [OK] project id: $projectId" -ForegroundColor Green
    Write-Host "  [OK] project title: $projectTitle" -ForegroundColor Green
} catch {
    Write-Host "  [ERRO] nao foi possivel obter project id" -ForegroundColor Red
    Write-Host "  verifique se o projeto existe em: $PROJECT_URL" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "2. obtendo repository id..." -ForegroundColor Yellow

# obter repository id
$repoQuery = @"
query {
  repository(owner: \"bengo501\", name: \"CFD-PIPELINE-TCC-1\") {
    id
    name
  }
}
"@

$repoResult = gh api graphql -f query=$repoQuery | ConvertFrom-Json
$repoId = $repoResult.data.repository.id

Write-Host "  [OK] repository id: $repoId" -ForegroundColor Green

Write-Host ""
Write-Host "3. obtendo todas as issues..." -ForegroundColor Yellow

# listar todas issues (abertas e fechadas)
$issues = gh api "repos/bengo501/CFD-PIPELINE-TCC-1/issues?state=all&per_page=100" | ConvertFrom-Json

Write-Host "  [OK] encontradas $($issues.Count) issues" -ForegroundColor Green

Write-Host ""
Write-Host "4. adicionando issues ao projeto..." -ForegroundColor Yellow

# contador
$added = 0
$skipped = 0
$errors = 0

foreach ($issue in $issues) {
    $issueNumber = $issue.number
    $issueTitle = $issue.title
    $issueNodeId = $issue.node_id
    
    # mutation para adicionar issue ao projeto
    $addMutation = @"
mutation {
  addProjectV2ItemById(input: {
    projectId: \"$projectId\"
    contentId: \"$issueNodeId\"
  }) {
    item {
      id
    }
  }
}
"@
    
    try {
        gh api graphql -f query=$addMutation | Out-Null
        Write-Host "  [OK] issue #$issueNumber - $issueTitle" -ForegroundColor Green
        $added++
        Start-Sleep -Milliseconds 200  # evitar rate limit
    } catch {
        if ($_.Exception.Message -match "already exists") {
            Write-Host "  [SKIP] issue #$issueNumber ja existe no projeto" -ForegroundColor Gray
            $skipped++
        } else {
            Write-Host "  [ERRO] issue #$issueNumber - $($_.Exception.Message)" -ForegroundColor Red
            $errors++
        }
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " processo concluido!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "resumo:"
Write-Host "- issues adicionadas: $added" -ForegroundColor Green
Write-Host "- issues ja existentes: $skipped" -ForegroundColor Yellow
Write-Host "- erros: $errors" -ForegroundColor $(if ($errors -gt 0) { "Red" } else { "Green" })
Write-Host ""
Write-Host "verificar projeto em:" -ForegroundColor Cyan
Write-Host "  $PROJECT_URL" -ForegroundColor Cyan
Write-Host ""

# instrucoes de proximo passo
Write-Host "proximos passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. acesse o projeto:" -ForegroundColor White
Write-Host "   $PROJECT_URL" -ForegroundColor Gray
Write-Host ""
Write-Host "2. organize as issues nas colunas:" -ForegroundColor White
Write-Host "   - Done: issues #1-8, #18-19 (sprints 1-3 concluidos)" -ForegroundColor Gray
Write-Host "   - Todo: issues #20-31 (sprints 5-8 pendentes)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. configure campos customizados (se ainda nao fez):" -ForegroundColor White
Write-Host "   - Sprint (iteration): criar sprints 1-8" -ForegroundColor Gray
Write-Host "   - Priority: High, Medium, Low" -ForegroundColor Gray
Write-Host "   - Story Points: Number field" -ForegroundColor Gray
Write-Host "   - Status: Done, In Progress, Todo, Backlog" -ForegroundColor Gray
Write-Host ""
Write-Host "4. preencher campos manualmente ou via script:" -ForegroundColor White
Write-Host "   powershell -File .github\preencher_campos_projeto.ps1" -ForegroundColor Gray
Write-Host ""

