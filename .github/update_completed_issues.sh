#!/bin/bash
# script para atualizar issues concluídas no github

echo "=========================================="
echo " atualizando issues concluidas no github"
echo "=========================================="

# verificar gh cli
if ! command -v gh &> /dev/null; then
    echo "[ERRO] gh cli nao instalado"
    echo "instale: https://cli.github.com/"
    exit 1
fi

# verificar autenticacao
gh auth status || {
    echo "[ERRO] gh cli nao autenticado"
    echo "execute: gh auth login"
    exit 1
}

# fechar issues concluidas (sprint 1)
echo ""
echo "fechando issues do sprint 1..."
gh issue close 1 --comment "concluido: dsl .bed + compilador antlr implementados. gramática completa, parser python gerado, normalização si, validação sintaxe."
gh issue close 2 --comment "concluido: bed wizard com 6 modos (interativo, edição, blender, blender interativo, ajuda, documentação). 47 parâmetros validados."
gh issue close 7 --comment "concluido: kanban/scrumban configurado. 50+ tasks, templates sprint/issue, documentação completa."
gh issue close 8 --comment "concluido: github projects integrado. scripts migração, labels, milestones, guias setup."

# fechar issues concluidas (sprint 2)
echo ""
echo "fechando issues do sprint 2..."
gh issue close 3 --comment "concluido: blender headless integrado. leito_extracao.py 500+ linhas, física rigid body, exportação stl, executor headless."
gh issue close 4 --comment "concluido: setup openfoam automatizado. setup_openfoam_case.py 890 linhas, geração casos completos, integração dsl."
gh issue close 5 --comment "concluido: testes e2e automatizados. 6 testes cobrindo pipeline completo (dsl → 3d → cfd), estrutura outputs organizada."
gh issue close 6 --comment "concluido: documentação pipeline completa. README 420+ linhas, UML 12 diagramas, guias openfoam, automações, badges."

# fechar issues concluidas (sprint 3)
echo ""
echo "fechando issues do sprint 3..."
gh issue close 18 --comment "concluido: backend fastapi com api rest. 15 endpoints, validação pydantic, integração bed/blender/openfoam, swagger docs."
gh issue close 19 --comment "concluido: frontend react com interface web. formulário parâmetros, monitoramento jobs, download arquivos, design responsivo."

# adicionar labels de conclusão
echo ""
echo "atualizando labels..."
for issue in 1 2 3 4 5 6 7 8 18 19; do
    gh issue edit $issue --add-label "status-done"
done

# criar milestones (sprints)
echo ""
echo "criando milestones..."

# sprint 1
gh milestone create "Sprint 1 - Fundação" \
    --description "DSL, compilador ANTLR, bed wizard, kanban" \
    --due-date 2025-09-22 2>/dev/null || echo "milestone sprint 1 já existe"

# sprint 2
gh milestone create "Sprint 2 - Modelagem" \
    --description "Blender headless, OpenFOAM automatizado, testes E2E" \
    --due-date 2025-10-07 2>/dev/null || echo "milestone sprint 2 já existe"

# sprint 3
gh milestone create "Sprint 3 - Web e API" \
    --description "FastAPI backend, React frontend, integração full-stack" \
    --due-date 2025-10-09 2>/dev/null || echo "milestone sprint 3 já existe"

# sprint 4 (documentação)
gh milestone create "Sprint 4 - Documentação" \
    --description "Bibliografia, referencial teórico, docs técnicas completas" \
    --due-date 2025-10-09 2>/dev/null || echo "milestone sprint 4 já existe"

# sprint 5 (próxima)
gh milestone create "Sprint 5 - Correções" \
    --description "Bugs, validação, pipeline completo" \
    --due-date 2025-10-17 2>/dev/null || echo "milestone sprint 5 já existe"

# associar issues aos milestones
echo ""
echo "associando issues aos milestones..."

# sprint 1
gh issue edit 1 --milestone "Sprint 1 - Fundação" 2>/dev/null
gh issue edit 2 --milestone "Sprint 1 - Fundação" 2>/dev/null
gh issue edit 7 --milestone "Sprint 1 - Fundação" 2>/dev/null
gh issue edit 8 --milestone "Sprint 1 - Fundação" 2>/dev/null

# sprint 2
gh issue edit 3 --milestone "Sprint 2 - Modelagem" 2>/dev/null
gh issue edit 4 --milestone "Sprint 2 - Modelagem" 2>/dev/null
gh issue edit 5 --milestone "Sprint 2 - Modelagem" 2>/dev/null
gh issue edit 6 --milestone "Sprint 2 - Modelagem" 2>/dev/null

# sprint 3
gh issue edit 18 --milestone "Sprint 3 - Web e API" 2>/dev/null
gh issue edit 19 --milestone "Sprint 3 - Web e API" 2>/dev/null

# sprint 5 (pendentes)
echo ""
echo "associando issues pendentes ao sprint 5..."
gh issue edit 20 --milestone "Sprint 5 - Correções" 2>/dev/null
gh issue edit 21 --milestone "Sprint 5 - Correções" 2>/dev/null
gh issue edit 22 --milestone "Sprint 5 - Correções" 2>/dev/null
gh issue edit 25 --milestone "Sprint 5 - Correções" 2>/dev/null

# fechar milestones completos
echo ""
echo "fechando milestones concluídos..."
gh milestone close "Sprint 1 - Fundação" 2>/dev/null || true
gh milestone close "Sprint 2 - Modelagem" 2>/dev/null || true
gh milestone close "Sprint 3 - Web e API" 2>/dev/null || true
gh milestone close "Sprint 4 - Documentação" 2>/dev/null || true

echo ""
echo "=========================================="
echo " atualizacao concluida!"
echo "=========================================="
echo ""
echo "resumo:"
echo "- 10 issues fechadas"
echo "- 5 milestones criados"
echo "- 4 milestones fechados (sprints 1-4)"
echo "- 1 milestone ativo (sprint 5)"
echo ""
echo "verificar:"
echo "  gh issue list --state closed"
echo "  gh milestone list"
echo ""

