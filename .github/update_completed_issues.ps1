# script powershell para atualizar issues concluidas no github

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " atualizando issues concluidas no github" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# verificar gh cli
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "[ERRO] gh cli nao instalado" -ForegroundColor Red
    Write-Host "instale: https://cli.github.com/"
    exit 1
}

# verificar autenticacao
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] gh cli nao autenticado" -ForegroundColor Red
    Write-Host "execute: gh auth login"
    exit 1
}

# fechar issues concluidas (sprint 1)
Write-Host ""
Write-Host "fechando issues do sprint 1..." -ForegroundColor Yellow

gh issue close 1 --comment "concluido: dsl .bed + compilador antlr implementados. gramatica completa, parser python gerado, normalizacao si, validacao sintaxe."
gh issue close 2 --comment "concluido: bed wizard com 6 modos (interativo, edicao, blender, blender interativo, ajuda, documentacao). 47 parametros validados."
gh issue close 7 --comment "concluido: kanban/scrumban configurado. 50+ tasks, templates sprint/issue, documentacao completa."
gh issue close 8 --comment "concluido: github projects integrado. scripts migracao, labels, milestones, guias setup."

# fechar issues concluidas (sprint 2)
Write-Host ""
Write-Host "fechando issues do sprint 2..." -ForegroundColor Yellow

gh issue close 3 --comment "concluido: blender headless integrado. leito_extracao.py 500+ linhas, fisica rigid body, exportacao stl, executor headless."
gh issue close 4 --comment "concluido: setup openfoam automatizado. setup_openfoam_case.py 890 linhas, geracao casos completos, integracao dsl."
gh issue close 5 --comment "concluido: testes e2e automatizados. 6 testes cobrindo pipeline completo (dsl → 3d → cfd), estrutura outputs organizada."
gh issue close 6 --comment "concluido: documentacao pipeline completa. README 420+ linhas, UML 12 diagramas, guias openfoam, automacoes, badges."

# fechar issues concluidas (sprint 3)
Write-Host ""
Write-Host "fechando issues do sprint 3..." -ForegroundColor Yellow

gh issue close 18 --comment "concluido: backend fastapi com api rest. 15 endpoints, validacao pydantic, integracao bed/blender/openfoam, swagger docs."
gh issue close 19 --comment "concluido: frontend react com interface web. formulario parametros, monitoramento jobs, download arquivos, design responsivo."

# adicionar labels de conclusao
Write-Host ""
Write-Host "atualizando labels..." -ForegroundColor Yellow

$completedIssues = @(1, 2, 3, 4, 5, 6, 7, 8, 18, 19)
foreach ($issue in $completedIssues) {
    gh issue edit $issue --add-label "status-done"
}

# criar milestones (sprints)
Write-Host ""
Write-Host "criando milestones..." -ForegroundColor Yellow

# sprint 1
gh milestone create "Sprint 1 - Fundacao" --description "DSL, compilador ANTLR, bed wizard, kanban" --due-date 2025-09-22 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "milestone sprint 1 ja existe" -ForegroundColor Gray }

# sprint 2
gh milestone create "Sprint 2 - Modelagem" --description "Blender headless, OpenFOAM automatizado, testes E2E" --due-date 2025-10-07 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "milestone sprint 2 ja existe" -ForegroundColor Gray }

# sprint 3
gh milestone create "Sprint 3 - Web e API" --description "FastAPI backend, React frontend, integracao full-stack" --due-date 2025-10-09 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "milestone sprint 3 ja existe" -ForegroundColor Gray }

# sprint 4
gh milestone create "Sprint 4 - Documentacao" --description "Bibliografia, referencial teorico, docs tecnicas completas" --due-date 2025-10-09 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "milestone sprint 4 ja existe" -ForegroundColor Gray }

# sprint 5
gh milestone create "Sprint 5 - Correcoes" --description "Bugs, validacao, pipeline completo" --due-date 2025-10-17 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "milestone sprint 5 ja existe" -ForegroundColor Gray }

# associar issues aos milestones
Write-Host ""
Write-Host "associando issues aos milestones..." -ForegroundColor Yellow

# sprint 1
gh issue edit 1 --milestone "Sprint 1 - Fundacao" 2>$null
gh issue edit 2 --milestone "Sprint 1 - Fundacao" 2>$null
gh issue edit 7 --milestone "Sprint 1 - Fundacao" 2>$null
gh issue edit 8 --milestone "Sprint 1 - Fundacao" 2>$null

# sprint 2
gh issue edit 3 --milestone "Sprint 2 - Modelagem" 2>$null
gh issue edit 4 --milestone "Sprint 2 - Modelagem" 2>$null
gh issue edit 5 --milestone "Sprint 2 - Modelagem" 2>$null
gh issue edit 6 --milestone "Sprint 2 - Modelagem" 2>$null

# sprint 3
gh issue edit 18 --milestone "Sprint 3 - Web e API" 2>$null
gh issue edit 19 --milestone "Sprint 3 - Web e API" 2>$null

# sprint 5 (pendentes)
Write-Host ""
Write-Host "associando issues pendentes ao sprint 5..." -ForegroundColor Yellow
gh issue edit 20 --milestone "Sprint 5 - Correcoes" 2>$null
gh issue edit 21 --milestone "Sprint 5 - Correcoes" 2>$null
gh issue edit 22 --milestone "Sprint 5 - Correcoes" 2>$null
gh issue edit 25 --milestone "Sprint 5 - Correcoes" 2>$null

# fechar milestones completos
Write-Host ""
Write-Host "fechando milestones concluidos..." -ForegroundColor Yellow
gh milestone close "Sprint 1 - Fundacao" 2>$null
gh milestone close "Sprint 2 - Modelagem" 2>$null
gh milestone close "Sprint 3 - Web e API" 2>$null
gh milestone close "Sprint 4 - Documentacao" 2>$null

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " atualizacao concluida!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "resumo:"
Write-Host "- 10 issues fechadas"
Write-Host "- 5 milestones criados"
Write-Host "- 4 milestones fechados (sprints 1-4)"
Write-Host "- 1 milestone ativo (sprint 5)"
Write-Host ""
Write-Host "verificar:"
Write-Host "  gh issue list --state closed"
Write-Host "  gh milestone list"
Write-Host ""

