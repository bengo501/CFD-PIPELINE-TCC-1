# script para preencher campos customizados do github project

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " preenchendo campos do github project" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# verificar autenticacao
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] gh cli nao autenticado" -ForegroundColor Red
    exit 1
}

$PROJECT_NUMBER = 2

Write-Host ""
Write-Host "1. obtendo project id e campos..." -ForegroundColor Yellow

# obter project id e campos
$query = @"
query {
  user(login: \"bengo501\") {
    projectV2(number: $PROJECT_NUMBER) {
      id
      title
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field {
            id
            name
            dataType
          }
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
          ... on ProjectV2IterationField {
            id
            name
            configuration {
              iterations {
                id
                title
                startDate
              }
            }
          }
        }
      }
    }
  }
}
"@

$result = gh api graphql -f query=$query | ConvertFrom-Json
$projectId = $result.data.user.projectV2.id
$fields = $result.data.user.projectV2.fields.nodes

Write-Host "  [OK] project id: $projectId" -ForegroundColor Green

# mapear campos
$fieldMap = @{}
foreach ($field in $fields) {
    $fieldMap[$field.name] = $field
    Write-Host "  encontrado campo: $($field.name) (tipo: $($field.dataType))" -ForegroundColor Gray
}

Write-Host ""
Write-Host "2. obtendo items do projeto..." -ForegroundColor Yellow

# obter todos items do projeto
$itemsQuery = @"
query {
  user(login: \"bengo501\") {
    projectV2(number: $PROJECT_NUMBER) {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              number
              title
            }
          }
        }
      }
    }
  }
}
"@

$itemsResult = gh api graphql -f query=$itemsQuery | ConvertFrom-Json
$items = $itemsResult.data.user.projectV2.items.nodes

Write-Host "  [OK] encontrados $($items.Count) items" -ForegroundColor Green

Write-Host ""
Write-Host "3. definindo mapeamento issue -> sprint..." -ForegroundColor Yellow

# mapeamento de issues para sprints
$issueSprintMap = @{
    1 = "Sprint 1 - Fundacao"
    2 = "Sprint 1 - Fundacao"
    7 = "Sprint 1 - Fundacao"
    8 = "Sprint 1 - Fundacao"
    3 = "Sprint 2 - Modelagem"
    4 = "Sprint 2 - Modelagem"
    5 = "Sprint 2 - Modelagem"
    6 = "Sprint 2 - Modelagem"
    18 = "Sprint 3 - Web e API"
    19 = "Sprint 3 - Web e API"
    20 = "Sprint 5 - Correcoes"
    21 = "Sprint 5 - Correcoes"
    22 = "Sprint 5 - Correcoes"
    25 = "Sprint 5 - Correcoes"
    23 = "Sprint 6 - Persistencia"
    26 = "Sprint 6 - Persistencia"
    27 = "Sprint 6 - Persistencia"
    28 = "Sprint 7 - Validacao Cientifica"
    29 = "Sprint 7 - Validacao Cientifica"
    30 = "Sprint 8 - Finalizacao TCC1"
    31 = "Sprint 8 - Finalizacao TCC1"
}

# mapeamento de issues para story points
$issuePointsMap = @{
    1 = 13; 2 = 8; 7 = 3; 8 = 3
    3 = 13; 4 = 13; 5 = 8; 6 = 5
    18 = 13; 19 = 13
    20 = 3; 21 = 8; 22 = 8; 25 = 5
    23 = 8; 26 = 5; 27 = 8
    28 = 13; 29 = 8
    30 = 8; 31 = 3
}

# mapeamento de issues para prioridade
$issuePriorityMap = @{
    21 = "High"  # bug critico
    22 = "High"  # pipeline openfoam
    25 = "High"  # pos-processamento
    28 = "High"  # validacao
    29 = "High"  # estudo malha
    30 = "High"  # proposta tcc1
    31 = "High"  # apresentacao
    20 = "Medium"
    23 = "Medium"
    26 = "Medium"
    27 = "Medium"
}

# mapeamento de issues para status
$issueStatusMap = @{
    1 = "Done"; 2 = "Done"; 3 = "Done"; 4 = "Done"
    5 = "Done"; 6 = "Done"; 7 = "Done"; 8 = "Done"
    18 = "Done"; 19 = "Done"
}

Write-Host "  [OK] mapeamentos definidos" -ForegroundColor Green

Write-Host ""
Write-Host "4. preenchendo campos..." -ForegroundColor Yellow

# funcao para atualizar campo
function Update-ProjectField {
    param(
        [string]$ItemId,
        [string]$FieldId,
        [string]$Value,
        [string]$IssueNumber,
        [string]$FieldName
    )
    
    $mutation = @"
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: \"$projectId\"
    itemId: \"$ItemId\"
    fieldId: \"$FieldId\"
    value: {
      text: \"$Value\"
    }
  }) {
    projectV2Item {
      id
    }
  }
}
"@
    
    try {
        gh api graphql -f query=$mutation | Out-Null
        Write-Host "  [OK] issue #$IssueNumber - $FieldName = $Value" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  [ERRO] issue #$IssueNumber - $FieldName" -ForegroundColor Red
        return $false
    }
}

$updated = 0

foreach ($item in $items) {
    $itemId = $item.id
    $issueNumber = $item.content.number
    
    if (-not $issueNumber) { continue }
    
    Write-Host ""
    Write-Host "processando issue #$issueNumber..." -ForegroundColor Cyan
    
    # story points
    if ($issuePointsMap.ContainsKey($issueNumber) -and $fieldMap.ContainsKey("Story Points")) {
        $points = $issuePointsMap[$issueNumber]
        if (Update-ProjectField -ItemId $itemId -FieldId $fieldMap["Story Points"].id `
            -Value $points -IssueNumber $issueNumber -FieldName "Story Points") {
            $updated++
        }
        Start-Sleep -Milliseconds 300
    }
    
    # priority
    if ($issuePriorityMap.ContainsKey($issueNumber) -and $fieldMap.ContainsKey("Priority")) {
        $priority = $issuePriorityMap[$issueNumber]
        if (Update-ProjectField -ItemId $itemId -FieldId $fieldMap["Priority"].id `
            -Value $priority -IssueNumber $issueNumber -FieldName "Priority") {
            $updated++
        }
        Start-Sleep -Milliseconds 300
    }
    
    # status
    if ($issueStatusMap.ContainsKey($issueNumber) -and $fieldMap.ContainsKey("Status")) {
        $status = $issueStatusMap[$issueNumber]
        if (Update-ProjectField -ItemId $itemId -FieldId $fieldMap["Status"].id `
            -Value $status -IssueNumber $issueNumber -FieldName "Status") {
            $updated++
        }
        Start-Sleep -Milliseconds 300
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " preenchimento concluido!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "resumo:"
Write-Host "- campos atualizados: $updated" -ForegroundColor Green
Write-Host ""
Write-Host "verificar projeto em:" -ForegroundColor Cyan
Write-Host "  https://github.com/users/bengo501/projects/2" -ForegroundColor Cyan
Write-Host ""
Write-Host "nota: campos Sprint (iteration) devem ser configurados manualmente" -ForegroundColor Yellow
Write-Host "      pois requerem IDs especificos de iteracoes" -ForegroundColor Yellow
Write-Host ""

