# script para configurar github projects com scrumban
# execute no powershell: .\setup_github_scrumban.ps1

param(
    [switch]$SkipMigration,
    [switch]$AutoYes
)

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURADOR GITHUB PROJECTS + SCRUMBAN" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# ==============================================================================
# PASSO 1: VERIFICAR DEPENDÊNCIAS
# ==============================================================================
Write-Host "[1/8] verificando dependências..." -ForegroundColor Yellow

# verificar gh cli
try {
    $ghVersion = gh --version 2>&1 | Select-String "gh version"
    Write-Host "[ok] github cli instalado: $ghVersion" -ForegroundColor Green
} catch {
    Write-Host "[erro] github cli não encontrado" -ForegroundColor Red
    Write-Host "instale: winget install GitHub.cli" -ForegroundColor Yellow
    exit 1
}

# verificar autenticação
try {
    gh auth status 2>&1 | Out-Null
    Write-Host "[ok] autenticado no github" -ForegroundColor Green
} catch {
    Write-Host "[aviso] não autenticado no github" -ForegroundColor Yellow
    Write-Host "executando autenticação..." -ForegroundColor Yellow
    gh auth login
}

# verificar python
try {
    $pythonVersion = python --version
    Write-Host "[ok] python instalado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[erro] python não encontrado" -ForegroundColor Red
    exit 1
}

# ==============================================================================
# PASSO 2: CRIAR GITHUB PROJECT (MANUAL)
# ==============================================================================
Write-Host ""
Write-Host "[2/8] criando github project..." -ForegroundColor Yellow

if (-not $AutoYes) {
    $criarProjeto = Read-Host "criar novo projeto? (s/n) [s]"
    if ([string]::IsNullOrWhiteSpace($criarProjeto)) { $criarProjeto = "s" }
} else {
    $criarProjeto = "s"
}

if ($criarProjeto -eq "s") {
    Write-Host "[atenção] gh cli ainda não suporta criar projects via comando" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "siga estes passos manualmente:" -ForegroundColor Cyan
    
    $username = gh api user -q .login
    Write-Host "1. acesse: https://github.com/users/$username/projects" -ForegroundColor White
    Write-Host "2. clique em 'New project'" -ForegroundColor White
    Write-Host "3. escolha template: 'Board'" -ForegroundColor White
    Write-Host "4. nome: 'CFD Pipeline - Scrumban'" -ForegroundColor White
    Write-Host "5. descrição: 'gerenciamento kanban + scrum do projeto cfd-pipeline-tcc'" -ForegroundColor White
    Write-Host ""
    
    if (-not $AutoYes) {
        Read-Host "pressione enter após criar o projeto"
    }
    
    Write-Host "[ok] projeto criado" -ForegroundColor Green
} else {
    Write-Host "[skip] pulando criação de projeto" -ForegroundColor Yellow
}

# ==============================================================================
# PASSO 3: CRIAR LABELS PADRONIZADAS
# ==============================================================================
Write-Host ""
Write-Host "[3/8] criando labels padronizadas..." -ForegroundColor Yellow

$labels = @(
    @{name="priority-critical"; color="b60205"; description="prioridade crítica"},
    @{name="priority-high"; color="d93f0b"; description="prioridade alta"},
    @{name="priority-medium"; color="fbca04"; description="prioridade média"},
    @{name="priority-low"; color="0e8a16"; description="prioridade baixa"},
    @{name="component-dsl"; color="1d76db"; description="componente dsl"},
    @{name="component-blender"; color="5319e7"; description="componente blender"},
    @{name="component-openfoam"; color="0052cc"; description="componente openfoam"},
    @{name="component-automation"; color="006b75"; description="componente automação"},
    @{name="component-tests"; color="bfdadc"; description="componente testes"},
    @{name="component-docs"; color="d4c5f9"; description="componente documentação"},
    @{name="component-cicd"; color="bfd4f2"; description="componente ci/cd"},
    @{name="status-in-progress"; color="fbca04"; description="em progresso"},
    @{name="status-review"; color="0e8a16"; description="em revisão"},
    @{name="status-blocked"; color="b60205"; description="bloqueado"},
    @{name="type-feature"; color="a2eeef"; description="nova funcionalidade"},
    @{name="type-bug"; color="d73a4a"; description="correção de bug"},
    @{name="type-task"; color="c5def5"; description="tarefa técnica"},
    @{name="type-epic"; color="3e4b9e"; description="épico"},
    @{name="sprint-1"; color="ededed"; description="sprint 1"},
    @{name="sprint-2"; color="ededed"; description="sprint 2"}
)

$labelsCriadas = 0
foreach ($label in $labels) {
    # verificar se label já existe
    $existente = gh label list --json name | ConvertFrom-Json | Where-Object { $_.name -eq $label.name }
    
    if ($existente) {
        Write-Host "[skip] label '$($label.name)' já existe" -ForegroundColor Yellow
    } else {
        try {
            gh label create $label.name --color $label.color --description $label.description 2>&1 | Out-Null
            Write-Host "[ok] label '$($label.name)' criada" -ForegroundColor Green
            $labelsCriadas++
        } catch {
            Write-Host "[erro] falha ao criar label '$($label.name)'" -ForegroundColor Red
        }
    }
}

Write-Host "[ok] labels criadas: $labelsCriadas / $($labels.Count)" -ForegroundColor Green

# ==============================================================================
# PASSO 4: CRIAR MILESTONES PARA SPRINTS
# ==============================================================================
Write-Host ""
Write-Host "[4/8] criando milestones para sprints..." -ForegroundColor Yellow

# calcular data de término (2 semanas a partir de agora)
$dueDate = (Get-Date).AddDays(14).ToString("yyyy-MM-ddT23:59:59Z")

try {
    $milestones = gh api repos/:owner/:repo/milestones | ConvertFrom-Json
    $sprint1Existe = $milestones | Where-Object { $_.title -eq "Sprint 1" }
    
    if ($sprint1Existe) {
        Write-Host "[skip] milestone 'Sprint 1' já existe" -ForegroundColor Yellow
    } else {
        gh api repos/:owner/:repo/milestones -X POST `
            -f title="Sprint 1" `
            -f state="open" `
            -f description="primeira sprint - análise e ci/cd" `
            -f due_on="$dueDate" | Out-Null
        Write-Host "[ok] milestone 'Sprint 1' criada" -ForegroundColor Green
    }
} catch {
    Write-Host "[erro] falha ao criar milestone: $_" -ForegroundColor Red
}

# ==============================================================================
# PASSO 5: MIGRAR TAREFAS KANBN → ISSUES
# ==============================================================================
Write-Host ""
Write-Host "[5/8] migrando tarefas kanbn para issues..." -ForegroundColor Yellow

if ($SkipMigration) {
    Write-Host "[skip] migração desabilitada (flag --SkipMigration)" -ForegroundColor Yellow
} else {
    if (-not $AutoYes) {
        $migrar = Read-Host "migrar tarefas do .kanbn para github issues? (s/n) [s]"
        if ([string]::IsNullOrWhiteSpace($migrar)) { $migrar = "s" }
    } else {
        $migrar = "s"
    }
    
    if ($migrar -eq "s") {
        Write-Host "executando dry-run..." -ForegroundColor Cyan
        python .github/migrate_kanbn_to_github.py
        
        Write-Host ""
        if (-not $AutoYes) {
            $confirma = Read-Host "confirma migração? (s/n) [s]"
            if ([string]::IsNullOrWhiteSpace($confirma)) { $confirma = "s" }
        } else {
            $confirma = "s"
        }
        
        if ($confirma -eq "s") {
            Write-Host "migrando tarefas..." -ForegroundColor Cyan
            python .github/migrate_kanbn_to_github.py --execute
            Write-Host "[ok] tarefas migradas" -ForegroundColor Green
        } else {
            Write-Host "[skip] migração cancelada" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[skip] pulando migração" -ForegroundColor Yellow
    }
}

# ==============================================================================
# PASSO 6: CRIAR ISSUE DE EXEMPLO
# ==============================================================================
Write-Host ""
Write-Host "[6/8] exemplo: criar issue manualmente..." -ForegroundColor Yellow

if (-not $AutoYes) {
    $criarIssue = Read-Host "criar issue de exemplo? (s/n) [n]"
    if ([string]::IsNullOrWhiteSpace($criarIssue)) { $criarIssue = "n" }
} else {
    $criarIssue = "n"
}

if ($criarIssue -eq "s") {
    $issueBody = @"
## descrição
implementar análise automática de resultados de simulações openfoam.

## tarefas
- [ ] extrair dados de perda de carga
- [ ] extrair dados de velocidade
- [ ] gerar gráficos matplotlib
- [ ] exportar relatório pdf

## prioridade
alta

## estimativa
8 story points (3-4 dias)
"@
    
    try {
        gh issue create `
            --title "[FEATURE] análise automática de resultados" `
            --body $issueBody `
            --label "type-feature,priority-high,component-automation" `
            --milestone "Sprint 1"
        Write-Host "[ok] issue de exemplo criada" -ForegroundColor Green
    } catch {
        Write-Host "[erro] falha ao criar issue: $_" -ForegroundColor Red
    }
} else {
    Write-Host "[skip] pulando criação de issue" -ForegroundColor Yellow
}

# ==============================================================================
# PASSO 7: CONFIGURAR BRANCH PROTECTION
# ==============================================================================
Write-Host ""
Write-Host "[7/8] configurando proteção de branch..." -ForegroundColor Yellow

if (-not $AutoYes) {
    $proteger = Read-Host "configurar proteção da branch main? (s/n) [s]"
    if ([string]::IsNullOrWhiteSpace($proteger)) { $proteger = "s" }
} else {
    $proteger = "s"
}

if ($proteger -eq "s") {
    Write-Host "configurando branch protection para 'main'..." -ForegroundColor Cyan
    
    try {
        gh api repos/:owner/:repo/branches/main/protection `
            -X PUT `
            -f required_status_checks='null' `
            -f enforce_admins=false `
            -F required_pull_request_reviews='{"required_approving_review_count":1}' `
            -F restrictions='null' 2>&1 | Out-Null
        Write-Host "[ok] branch protection ativada" -ForegroundColor Green
    } catch {
        Write-Host "[aviso] falha ao ativar branch protection (pode requerer permissões admin)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[skip] pulando branch protection" -ForegroundColor Yellow
}

# ==============================================================================
# PASSO 8: CRIAR ESTRUTURA DE SPRINTS
# ==============================================================================
Write-Host ""
Write-Host "[8/8] criando estrutura de sprints..." -ForegroundColor Yellow

# criar diretório sprints
if (-not (Test-Path "sprints")) {
    New-Item -ItemType Directory -Path "sprints" | Out-Null
}

# copiar template para sprint 1
if (-not (Test-Path "sprints/sprint-01.md")) {
    Copy-Item ".github/SPRINT_TEMPLATE.md" "sprints/sprint-01.md"
    
    # substituir placeholders
    $sprint1Content = Get-Content "sprints/sprint-01.md" -Raw
    $sprint1Content = $sprint1Content -replace "sprint X", "sprint 1"
    $sprint1Content = $sprint1Content -replace "dd/mm/yyyy", (Get-Date).ToString("dd/MM/yyyy")
    $sprint1Content | Set-Content "sprints/sprint-01.md"
    
    Write-Host "[ok] sprint 1 criado: sprints/sprint-01.md" -ForegroundColor Green
} else {
    Write-Host "[skip] sprint 1 já existe" -ForegroundColor Yellow
}

# ==============================================================================
# FINALIZAÇÃO
# ==============================================================================
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAÇÃO CONCLUÍDA!" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "próximos passos:" -ForegroundColor Yellow
Write-Host ""

$username = gh api user -q .login

Write-Host "1. configurar github project (manual):" -ForegroundColor Cyan
Write-Host "   - acesse: https://github.com/users/$username/projects" -ForegroundColor White
Write-Host "   - adicione colunas: Backlog, Todo, In Progress, Review, Done" -ForegroundColor White
Write-Host "   - configure wip limits (In Progress: max 3)" -ForegroundColor White
Write-Host "   - adicione campos customizados: Priority, Story Points, Sprint, Component" -ForegroundColor White
Write-Host ""
Write-Host "2. adicionar issues ao projeto:" -ForegroundColor Cyan
Write-Host "   gh issue list --json number,title" -ForegroundColor White
Write-Host "   # adicione manualmente cada issue ao projeto via web" -ForegroundColor Gray
Write-Host ""
Write-Host "3. iniciar sprint 1:" -ForegroundColor Cyan
Write-Host "   - edite: sprints/sprint-01.md" -ForegroundColor White
Write-Host "   - selecione issues para a sprint" -ForegroundColor White
Write-Host "   - faça sprint planning com o time" -ForegroundColor White
Write-Host ""
Write-Host "4. daily standup (9h30):" -ForegroundColor Cyan
Write-Host "   - atualizar board no github projects" -ForegroundColor White
Write-Host "   - registrar em: sprints/sprint-01.md" -ForegroundColor White
Write-Host ""
Write-Host "documentação completa:" -ForegroundColor Yellow
Write-Host "  - .github/GITHUB_PROJECTS_SETUP.md" -ForegroundColor White
Write-Host "  - .github/SPRINT_TEMPLATE.md" -ForegroundColor White
Write-Host ""

# criar arquivo de comandos úteis
$comandosUteis = @"
# comandos úteis github cli + scrumban

## listar issues
gh issue list
gh issue list --label "priority-high"
gh issue list --milestone "Sprint 1"
gh issue list --state all

## criar issue
gh issue create --title "[FEATURE] título" --body "descrição" --label "type-feature"

## atualizar issue
gh issue edit 123 --add-label "status-in-progress"
gh issue edit 123 --add-assignee @me
gh issue edit 123 --milestone "Sprint 1"

## fechar issue
gh issue close 123

## listar labels
gh label list

## listar milestones
gh api repos/:owner/:repo/milestones

## criar pr
gh pr create --title "feat: descrição" --body "closes #123"

## revisar pr
gh pr review 456 --approve

## merge pr
gh pr merge 456 --squash --delete-branch

## visualizar projeto
gh project list

## executar scripts
python .github/migrate_kanbn_to_github.py          # dry-run
python .github/migrate_kanbn_to_github.py --execute # executar

python scripts/automation/run_tests.py              # testes
python scripts/automation/batch_generate.py         # gerar lotes
python scripts/automation/cleanup.py                # limpar temp

## abrir browser
gh repo view --web
gh issue view 123 --web
gh pr view 456 --web
"@

$comandosUteis | Set-Content "comandos_github_scrumban.md"
Write-Host "[ok] criado: comandos_github_scrumban.md" -ForegroundColor Green
Write-Host ""

