#!/bin/bash
# script para configurar github projects com scrumban
# execute passo a passo ou todo de uma vez

set -e  # parar em caso de erro

echo "======================================================================"
echo "  CONFIGURADOR GITHUB PROJECTS + SCRUMBAN"
echo "======================================================================"
echo ""

# cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # sem cor

# ==============================================================================
# PASSO 1: VERIFICAR DEPENDÊNCIAS
# ==============================================================================
echo "[1/8] verificando dependências..."

# verificar gh cli
if ! command -v gh &> /dev/null; then
    echo -e "${RED}[erro]${NC} github cli não encontrado"
    echo "instale: winget install GitHub.cli"
    exit 1
fi
echo -e "${GREEN}[ok]${NC} github cli instalado: $(gh --version | head -1)"

# verificar autenticação
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}[aviso]${NC} não autenticado no github"
    echo "executando autenticação..."
    gh auth login
fi
echo -e "${GREEN}[ok]${NC} autenticado no github"

# ==============================================================================
# PASSO 2: CRIAR GITHUB PROJECT
# ==============================================================================
echo ""
echo "[2/8] criando github project..."

# perguntar ao usuário
read -p "criar novo projeto? (s/n) [s]: " criar_projeto
criar_projeto=${criar_projeto:-s}

if [[ "$criar_projeto" == "s" ]]; then
    # criar projeto
    echo "criando projeto 'CFD Pipeline - Scrumban'..."
    
    # nota: gh project create ainda não está disponível na versão atual
    # vamos criar via web e fornecer instruções
    
    echo -e "${YELLOW}[atenção]${NC} gh cli ainda não suporta criar projects via comando"
    echo ""
    echo "siga estes passos manualmente:"
    echo "1. acesse: https://github.com/users/$(gh api user -q .login)/projects"
    echo "2. clique em 'New project'"
    echo "3. escolha template: 'Board'"
    echo "4. nome: 'CFD Pipeline - Scrumban'"
    echo "5. descrição: 'gerenciamento kanban + scrum do projeto cfd-pipeline-tcc'"
    echo ""
    read -p "pressione enter após criar o projeto..."
    
    echo -e "${GREEN}[ok]${NC} projeto criado"
else
    echo -e "${YELLOW}[skip]${NC} pulando criação de projeto"
fi

# ==============================================================================
# PASSO 3: CRIAR LABELS PADRONIZADAS
# ==============================================================================
echo ""
echo "[3/8] criando labels padronizadas..."

# array de labels (nome:cor:descrição)
labels=(
    "priority-critical:b60205:prioridade crítica"
    "priority-high:d93f0b:prioridade alta"
    "priority-medium:fbca04:prioridade média"
    "priority-low:0e8a16:prioridade baixa"
    "component-dsl:1d76db:componente dsl"
    "component-blender:5319e7:componente blender"
    "component-openfoam:0052cc:componente openfoam"
    "component-automation:006b75:componente automação"
    "component-tests:bfdadc:componente testes"
    "component-docs:d4c5f9:componente documentação"
    "component-cicd:bfd4f2:componente ci/cd"
    "status-in-progress:fbca04:em progresso"
    "status-review:0e8a16:em revisão"
    "status-blocked:b60205:bloqueado"
    "type-feature:a2eeef:nova funcionalidade"
    "type-bug:d73a4a:correção de bug"
    "type-task:c5def5:tarefa técnica"
    "type-epic:3e4b9e:épico"
    "sprint-1:ededed:sprint 1"
    "sprint-2:ededed:sprint 2"
)

for label in "${labels[@]}"; do
    IFS=':' read -r name color description <<< "$label"
    
    # verificar se label já existe
    if gh label list | grep -q "$name"; then
        echo -e "${YELLOW}[skip]${NC} label '$name' já existe"
    else
        gh label create "$name" --color "$color" --description "$description"
        echo -e "${GREEN}[ok]${NC} label '$name' criada"
    fi
done

echo -e "${GREEN}[ok]${NC} labels criadas: ${#labels[@]}"

# ==============================================================================
# PASSO 4: CRIAR MILESTONES PARA SPRINTS
# ==============================================================================
echo ""
echo "[4/8] criando milestones para sprints..."

# criar milestone sprint 1
if gh api repos/:owner/:repo/milestones | grep -q "Sprint 1"; then
    echo -e "${YELLOW}[skip]${NC} milestone 'Sprint 1' já existe"
else
    # calcular datas (próxima segunda + 2 semanas)
    due_date=$(date -d "next monday +13 days" +%Y-%m-%dT23:59:59Z 2>/dev/null || date -v +14d +%Y-%m-%dT23:59:59Z)
    
    gh api repos/:owner/:repo/milestones -X POST -f title="Sprint 1" -f state="open" -f description="primeira sprint - análise e ci/cd" -f due_on="$due_date"
    echo -e "${GREEN}[ok]${NC} milestone 'Sprint 1' criada"
fi

# ==============================================================================
# PASSO 5: MIGRAR TAREFAS KANBN → ISSUES
# ==============================================================================
echo ""
echo "[5/8] migrando tarefas kanbn para issues..."

read -p "migrar tarefas do .kanbn para github issues? (s/n) [s]: " migrar
migrar=${migrar:-s}

if [[ "$migrar" == "s" ]]; then
    # executar script de migração (dry-run primeiro)
    echo "executando dry-run..."
    python .github/migrate_kanbn_to_github.py
    
    echo ""
    read -p "confirma migração? (s/n) [s]: " confirma
    confirma=${confirma:-s}
    
    if [[ "$confirma" == "s" ]]; then
        echo "migrando tarefas..."
        python .github/migrate_kanbn_to_github.py --execute
        echo -e "${GREEN}[ok]${NC} tarefas migradas"
    else
        echo -e "${YELLOW}[skip]${NC} migração cancelada"
    fi
else
    echo -e "${YELLOW}[skip]${NC} pulando migração"
fi

# ==============================================================================
# PASSO 6: CRIAR ISSUES MANUALMENTE (EXEMPLO)
# ==============================================================================
echo ""
echo "[6/8] exemplo: criar issue manualmente..."

read -p "criar issue de exemplo? (s/n) [n]: " criar_issue
criar_issue=${criar_issue:-n}

if [[ "$criar_issue" == "s" ]]; then
    echo "criando issue de exemplo..."
    
    gh issue create \
        --title "[FEATURE] análise automática de resultados" \
        --body "$(cat <<EOF
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
EOF
)" \
        --label "type-feature,priority-high,component-automation" \
        --milestone "Sprint 1"
    
    echo -e "${GREEN}[ok]${NC} issue de exemplo criada"
else
    echo -e "${YELLOW}[skip]${NC} pulando criação de issue"
fi

# ==============================================================================
# PASSO 7: CONFIGURAR BRANCH PROTECTION
# ==============================================================================
echo ""
echo "[7/8] configurando proteção de branch..."

read -p "configurar proteção da branch main? (s/n) [s]: " proteger
proteger=${proteger:-s}

if [[ "$proteger" == "s" ]]; then
    echo "configurando branch protection para 'main'..."
    
    # requer code review antes de merge
    gh api repos/:owner/:repo/branches/main/protection \
        -X PUT \
        -f required_status_checks='null' \
        -f enforce_admins=false \
        -F required_pull_request_reviews='{"required_approving_review_count":1}' \
        -F restrictions='null' 2>/dev/null && \
        echo -e "${GREEN}[ok]${NC} branch protection ativada" || \
        echo -e "${YELLOW}[aviso]${NC} falha ao ativar branch protection (pode requerer permissões admin)"
else
    echo -e "${YELLOW}[skip]${NC} pulando branch protection"
fi

# ==============================================================================
# PASSO 8: CRIAR ESTRUTURA DE SPRINTS
# ==============================================================================
echo ""
echo "[8/8] criando estrutura de sprints..."

# criar diretório sprints
mkdir -p sprints

# copiar template para sprint 1
if [ ! -f "sprints/sprint-01.md" ]; then
    cp .github/SPRINT_TEMPLATE.md sprints/sprint-01.md
    
    # substituir placeholders
    sed -i 's/sprint X/sprint 1/g' sprints/sprint-01.md
    sed -i 's/dd\/mm\/yyyy/14\/10\/2025/g' sprints/sprint-01.md
    
    echo -e "${GREEN}[ok]${NC} sprint 1 criado: sprints/sprint-01.md"
else
    echo -e "${YELLOW}[skip]${NC} sprint 1 já existe"
fi

# ==============================================================================
# FINALIZAÇÃO
# ==============================================================================
echo ""
echo "======================================================================"
echo "  CONFIGURAÇÃO CONCLUÍDA!"
echo "======================================================================"
echo ""
echo "próximos passos:"
echo ""
echo "1. configurar github project (manual):"
echo "   - acesse: https://github.com/users/$(gh api user -q .login)/projects"
echo "   - adicione colunas: Backlog, Todo, In Progress, Review, Done"
echo "   - configure wip limits (In Progress: max 3)"
echo "   - adicione campos customizados: Priority, Story Points, Sprint, Component"
echo ""
echo "2. adicionar issues ao projeto:"
echo "   gh issue list --json number,title"
echo "   # adicione manualmente cada issue ao projeto via web"
echo ""
echo "3. iniciar sprint 1:"
echo "   - edite: sprints/sprint-01.md"
echo "   - selecione issues para a sprint"
echo "   - faça sprint planning com o time"
echo ""
echo "4. daily standup (9h30):"
echo "   - atualizar board no github projects"
echo "   - registrar em: sprints/sprint-01.md"
echo ""
echo "documentação completa:"
echo "  - .github/GITHUB_PROJECTS_SETUP.md"
echo "  - .github/SPRINT_TEMPLATE.md"
echo ""

