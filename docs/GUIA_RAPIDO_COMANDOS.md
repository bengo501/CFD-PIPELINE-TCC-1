# guia rápido de comandos - github scrumban

guia prático com comandos prontos para usar no dia a dia.

---

## 🚀 configuração inicial (executar uma vez)

### opção 1: script automatizado (recomendado)

```powershell
# powershell (windows)
.\setup_github_scrumban.ps1

# ou com flags
.\setup_github_scrumban.ps1 -AutoYes          # responder sim para tudo
.\setup_github_scrumban.ps1 -SkipMigration    # pular migração de tarefas
```

```bash
# bash (linux/mac/wsl)
chmod +x setup_github_scrumban.sh
./setup_github_scrumban.sh
```

### opção 2: passo a passo manual

```bash
# 1. autenticar no github
gh auth login

# 2. criar labels
gh label create "priority-high" --color "d93f0b" --description "alta prioridade"
gh label create "component-dsl" --color "1d76db" --description "componente dsl"
# ... (ver lista completa no script)

# 3. criar milestone sprint 1
gh api repos/:owner/:repo/milestones -X POST \
  -f title="Sprint 1" \
  -f state="open" \
  -f due_on="2025-10-27T23:59:59Z"

# 4. migrar tarefas kanbn
python .github/migrate_kanbn_to_github.py          # dry-run
python .github/migrate_kanbn_to_github.py --execute # executar

# 5. criar estrutura de sprints
mkdir sprints
cp .github/SPRINT_TEMPLATE.md sprints/sprint-01.md
```

---

## 📝 gerenciar issues

### criar issues

```bash
# feature
gh issue create \
  --title "[FEATURE] análise automática de resultados" \
  --body "descrição detalhada..." \
  --label "type-feature,priority-high,component-automation" \
  --milestone "Sprint 1"

# bug
gh issue create \
  --title "[BUG] erro ao compilar .bed" \
  --body "passos para reproduzir..." \
  --label "type-bug,priority-critical,component-dsl"

# task
gh issue create \
  --title "[TASK] atualizar documentação" \
  --body "checklist de tarefas..." \
  --label "type-task,priority-medium,component-docs"

# usando template (interativo)
gh issue create --web
```

### listar issues

```bash
# todas abertas
gh issue list

# por label
gh issue list --label "priority-high"
gh issue list --label "component-blender"
gh issue list --label "type-bug"

# por milestone (sprint)
gh issue list --milestone "Sprint 1"

# por assignee
gh issue list --assignee "@me"
gh issue list --assignee "usuario"

# todas (abertas + fechadas)
gh issue list --state all

# formato json
gh issue list --json number,title,labels,state

# filtro avançado
gh issue list --label "priority-high" --milestone "Sprint 1" --state open
```

### atualizar issues

```bash
# adicionar label
gh issue edit 101 --add-label "status-in-progress"

# remover label
gh issue edit 101 --remove-label "status-in-progress"
gh issue edit 101 --add-label "status-review"

# assignar para você
gh issue edit 101 --add-assignee @me

# adicionar milestone
gh issue edit 101 --milestone "Sprint 1"

# alterar título
gh issue edit 101 --title "[FEATURE] novo título"

# adicionar comentário
gh issue comment 101 --body "bloqueio: falta acesso ao servidor"

# fechar issue
gh issue close 101 --comment "resolvido em #PR123"

# reabrir issue
gh issue reopen 101
```

### visualizar issues

```bash
# ver detalhes no terminal
gh issue view 101

# abrir no browser
gh issue view 101 --web

# ver comentários
gh issue view 101 --comments
```

---

## 🌿 workflow git + issues

### começar trabalho em issue

```bash
# 1. atualizar issue
gh issue edit 101 --add-label "status-in-progress" --add-assignee @me

# 2. criar branch
git checkout -b feature/101-analise-resultados

# 3. trabalhar
# ... fazer mudanças ...

# 4. commit (conventional commits)
git add .
git commit -m "feat: implementar análise de resultados (#101)"

# 5. push
git push origin feature/101-analise-resultados

# 6. criar pr
gh pr create \
  --title "feat: análise de resultados (#101)" \
  --body "closes #101" \
  --label "status-review"

# 7. atualizar issue
gh issue edit 101 --add-label "status-review"
```

### revisar código

```bash
# listar prs abertas
gh pr list

# ver pr
gh pr view 123

# fazer checkout da pr para testar
gh pr checkout 123

# aprovar
gh pr review 123 --approve --body "lgtm! código bem estruturado"

# solicitar mudanças
gh pr review 123 --request-changes --body "favor adicionar testes"

# comentar
gh pr review 123 --comment --body "consideração sobre performance..."

# merge (após aprovação)
gh pr merge 123 --squash --delete-branch

# a issue fecha automaticamente se o pr tinha "closes #101"
```

---

## 🏃 daily standup

### atualizar status diário

```bash
# 1. ver suas issues em progresso
gh issue list --assignee @me --label "status-in-progress"

# 2. atualizar sprint doc
code sprints/sprint-01.md
# adicionar entrada no daily standup:
# dia X:
# @seu-usuario:
#   - fez: implementou análise de perda de carga (#101)
#   - fará: implementar análise de velocidade (#101)
#   - bloqueios: nenhum

# 3. commit do sprint doc
git add sprints/sprint-01.md
git commit -m "docs: atualizar daily standup dia X"
git push
```

---

## 📊 métricas e relatórios

### velocity

```bash
# issues fechadas na sprint 1
gh issue list --milestone "Sprint 1" --state closed --json number,title

# calcular story points manualmente ou usar script:
python -c "
import subprocess
import json

result = subprocess.run(
    ['gh', 'issue', 'list', '--milestone', 'Sprint 1', '--state', 'closed', '--json', 'number,body'],
    capture_output=True, text=True
)

issues = json.loads(result.stdout)
total_points = 0

for issue in issues:
    # extrair story points do corpo (ex: '8 story points')
    import re
    match = re.search(r'(\d+)\s*story points?', issue['body'], re.IGNORECASE)
    if match:
        total_points += int(match.group(1))

print(f'velocity sprint 1: {total_points} pts')
"
```

### cycle time

```bash
# tempo entre "in progress" e "done" para cada issue
# usar github api para pegar timestamps de events

gh api graphql -f query='
{
  repository(owner: "bengo501", name: "CFD-PIPELINE-TCC-1") {
    issue(number: 101) {
      title
      timelineItems(first: 100, itemTypes: [LABELED_EVENT, CLOSED_EVENT]) {
        nodes {
          ... on LabeledEvent {
            label { name }
            createdAt
          }
          ... on ClosedEvent {
            createdAt
          }
        }
      }
    }
  }
}'
```

---

## 🔍 busca avançada

### filtros combinados

```bash
# bugs críticos abertos
gh issue list --label "type-bug,priority-critical" --state open

# features da sprint 1 ainda abertas
gh issue list --label "type-feature" --milestone "Sprint 1" --state open

# todas as tarefas do componente dsl
gh issue list --label "component-dsl" --state all

# issues assignadas para você em review
gh issue list --assignee @me --label "status-review"

# issues sem assignee (disponíveis para pegar)
gh issue list --json number,title,assignees | \
  jq '.[] | select(.assignees | length == 0)'
```

---

## 📦 automações do projeto

### testes automatizados

```bash
# rodar suite de testes completa
python scripts/automation/run_tests.py

# rodar apenas testes de componente específico
python scripts/automation/run_tests.py --component dsl
```

### geração em lote

```bash
# gerar múltiplos leitos para estudo paramétrico
python scripts/automation/batch_generate.py

# exemplo: variar diâmetro
python scripts/automation/batch_generate.py \
  --param diameter \
  --values 0.05,0.075,0.1 \
  --output batch_diameter
```

### limpeza

```bash
# limpar arquivos temporários
python scripts/automation/cleanup.py

# limpeza agressiva (cuidado!)
python scripts/automation/cleanup.py --aggressive
```

---

## 🎯 comandos do bed_wizard

### gerar leito interativo

```bash
cd dsl
python bed_wizard.py

# escolher:
# 1. modo completo (cfd)
# 2. modo blender (só 3d)
# 3. modo blender interativo (abre blender)
# 4. ajuda
# 5. documentação
```

### gerar leito via linha de comando

```bash
# criar arquivo .bed diretamente
cat > meu_leito.bed << EOF
bed {
  diameter: 0.05m
  height: 0.1m
  wall_thickness: 0.002m
}

particles {
  count: 100
  kind: sphere
  diameter: 0.005m
}

packing {
  method: rigid_body
}

export {
  formats: blend, stl
}
EOF

# compilar
python dsl/bed_compiler_antlr_standalone.py meu_leito.bed

# gerar 3d
cd ..
python scripts/standalone_scripts/executar_leito_headless.py
```

---

## 🐳 containerização (futuro)

### docker compose

```bash
# quando implementado:
docker-compose up -d

# executar simulação no container
docker-compose exec openfoam ./Allrun

# visualizar no browser
firefox http://localhost:3000  # dashboard
```

---

## 📚 documentação útil

### abrir documentação

```bash
# html interativo
start dsl/documentacao.html  # windows
xdg-open dsl/documentacao.html  # linux

# markdown
code .github/GITHUB_PROJECTS_SETUP.md
code .github/SPRINT_TEMPLATE.md
code ARQUITETURA_PROJETO.md
```

### links rápidos

```bash
# abrir repo no browser
gh repo view --web

# abrir projects
gh api user -q .login  # pegar username
start "https://github.com/users/SEU_USERNAME/projects"

# abrir actions (ci/cd quando implementado)
gh run list
gh run view --web
```

---

## ⚡ aliases úteis

adicione ao seu `.bashrc` ou `$PROFILE` (powershell):

```bash
# bash
alias ghil='gh issue list'
alias ghic='gh issue create'
alias ghpl='gh pr list'
alias ghpc='gh pr create'
alias ghpm='gh pr merge --squash --delete-branch'

# sprint atual
alias sprint='code sprints/sprint-01.md'

# testes rápidos
alias test='python scripts/automation/run_tests.py'
alias clean='python scripts/automation/cleanup.py'

# bed wizard
alias bed='cd dsl && python bed_wizard.py && cd ..'
```

```powershell
# powershell
function ghil { gh issue list $args }
function ghic { gh issue create $args }
function ghpl { gh pr list $args }
function ghpc { gh pr create $args }
function sprint { code sprints/sprint-01.md }
function test { python scripts/automation/run_tests.py }
function bed { cd dsl; python bed_wizard.py; cd .. }
```

---

## 🆘 troubleshooting

### autenticação expirou

```bash
gh auth login
gh auth status
```

### issue não aparece no project

```bash
# adicionar manualmente via web
gh issue view 101 --web
# clicar em "Projects" no painel direito
```

### milestone não encontrada

```bash
# listar milestones
gh api repos/:owner/:repo/milestones

# criar se não existir
gh api repos/:owner/:repo/milestones -X POST \
  -f title="Sprint 1" \
  -f state="open"
```

### label não encontrada

```bash
# listar labels
gh label list

# criar se não existir
gh label create "priority-high" --color "d93f0b"
```

---

## ✅ checklist rápido sprint

```bash
# início sprint
[ ] gh api repos/:owner/:repo/milestones -X POST ...  # criar milestone
[ ] gh issue list --milestone "Sprint X"              # selecionar issues
[ ] cp .github/SPRINT_TEMPLATE.md sprints/sprint-X.md # criar doc sprint
[ ] code sprints/sprint-X.md                          # planning meeting

# durante sprint
[ ] daily standup 9h30                                # atualizar board
[ ] gh issue edit X --add-label "status-in-progress"  # pegar tarefa
[ ] git checkout -b feature/X-nome                    # criar branch
[ ] gh pr create ...                                  # criar pr
[ ] gh pr review ... --approve                        # revisar código
[ ] gh pr merge ... --squash                          # merge

# final sprint
[ ] gh issue list --milestone "Sprint X" --state closed  # verificar conclusões
[ ] code sprints/sprint-X.md                          # review meeting
[ ] code sprints/sprint-X.md                          # retrospective
[ ] calcular velocity                                 # métricas
```

---

## 🎓 recursos

- **gh cli manual:** `gh help` ou https://cli.github.com/manual/
- **github projects:** https://docs.github.com/en/issues/planning-and-tracking-with-projects
- **conventional commits:** https://www.conventionalcommits.org/
- **scrumban:** `.github/GITHUB_PROJECTS_SETUP.md`

---

**dúvidas?** abra uma issue: `gh issue create --title "[DOCS] dúvida sobre X"`

