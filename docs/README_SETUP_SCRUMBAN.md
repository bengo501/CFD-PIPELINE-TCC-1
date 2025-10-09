# 🚀 setup github scrumban - guia visual

guia completo ilustrado para configurar gerenciamento scrumban no github projects.

---

## 📦 o que foi criado

```
projeto/
├── .github/
│   ├── SPRINT_TEMPLATE.md              # 📋 template sprint (300 linhas)
│   ├── GITHUB_PROJECTS_SETUP.md        # 📖 guia completo (600 linhas)
│   ├── migrate_kanbn_to_github.py      # 🔄 migração automática
│   └── ISSUE_TEMPLATE/
│       ├── feature.md                  # ✨ template feature
│       ├── bug.md                      # 🐛 template bug
│       └── task.md                     # 📝 template task
├── setup_github_scrumban.ps1           # 🪟 script windows
├── setup_github_scrumban.sh            # 🐧 script linux/mac
├── GUIA_RAPIDO_COMANDOS.md             # ⚡ cheat sheet comandos
└── comandos_github_scrumban.md         # 📝 será criado pelo script
```

**total:** ~2000 linhas de documentação + automação

---

## 🎯 execução rápida (3 opções)

### opção 1: script automatizado completo ⭐ recomendado

```powershell
# windows powershell
.\setup_github_scrumban.ps1 -AutoYes
```

**o que faz:**
1. ✅ verifica gh cli instalado
2. 🔐 autentica no github
3. 🏷️ cria 20 labels padronizadas
4. 📅 cria milestone "Sprint 1"
5. 🔄 migra tarefas .kanbn → issues
6. 🔒 configura branch protection
7. 📁 cria estrutura sprints/
8. 📝 gera comandos_github_scrumban.md

**tempo:** 2-3 minutos

---

### opção 2: script interativo

```powershell
# windows powershell (com confirmações)
.\setup_github_scrumban.ps1
```

**o que acontece:**
```
[1/8] verificando dependências...
[ok] github cli instalado: gh version 2.57.0

criar novo projeto? (s/n) [s]: s          ← você confirma
migrar tarefas? (s/n) [s]: s              ← você confirma
criar issue exemplo? (s/n) [n]: n         ← você confirma
configurar branch protection? (s/n) [s]: s ← você confirma
```

**tempo:** 3-5 minutos (com interações)

---

### opção 3: manual passo a passo

```bash
# 1. autenticar
gh auth login

# 2. criar labels
gh label create "priority-high" --color "d93f0b"
# ... (20 labels)

# 3. migrar tarefas
python .github/migrate_kanbn_to_github.py --execute

# 4. criar estrutura
mkdir sprints
cp .github/SPRINT_TEMPLATE.md sprints/sprint-01.md
```

**tempo:** 10-15 minutos

---

## 📸 resultado visual esperado

### 1. labels criadas

```
🔴 priority-critical
🔴 priority-high
🟡 priority-medium
🟢 priority-low

🔵 component-dsl
🟣 component-blender
🔵 component-openfoam
🟢 component-automation
⚪ component-tests
🟣 component-docs
🔵 component-cicd

🟡 status-in-progress
🟢 status-review
🔴 status-blocked

🔵 type-feature
🔴 type-bug
⚪ type-task
🟣 type-epic

⚪ sprint-1
⚪ sprint-2
```

### 2. milestone criada

```
📅 Sprint 1
   início: 14/10/2025
   término: 27/10/2025 (2 semanas)
   descrição: primeira sprint - análise e ci/cd
   issues: 0 / 3
```

### 3. issues migradas (exemplo)

```
#1  [FEATURE] implementação dsl e compilador antlr
    🏷️ type-feature, priority-high, component-dsl, status-done
    
#2  [FEATURE] integração blender headless
    🏷️ type-feature, priority-high, component-blender, status-done
    
#3  [FEATURE] wizard interativo bed_wizard.py
    🏷️ type-feature, priority-high, component-dsl, status-done

...

#101 [FEATURE] análise automática de resultados
     🏷️ type-feature, priority-high, component-automation
     📅 Sprint 1
     
#105 [TASK] configurar ci/cd pipeline
     🏷️ type-task, priority-high, component-cicd
     📅 Sprint 1
```

### 4. estrutura de pastas

```
sprints/
└── sprint-01.md           # ← criado automaticamente
                             contém: planning, dailies, review, retro
```

---

## 🖥️ configurar github project (manual)

### passo 1: acessar projects

1. **abrir url:**
   ```
   https://github.com/users/SEU_USERNAME/projects
   ```

2. **clicar em:** `New project`

3. **escolher:** `Board` (kanban)

4. **preencher:**
   ```
   nome: CFD Pipeline - Scrumban
   descrição: gerenciamento kanban + scrum do projeto cfd-pipeline-tcc
   visibilidade: public
   ```

5. **criar projeto**

---

### passo 2: configurar colunas

**estado inicial:**
```
┌──────┬──────────┬──────┐
│ Todo │ In Prog  │ Done │
└──────┴──────────┴──────┘
```

**adicionar colunas:**

1. clicar no `+` depois de "Done"
2. adicionar: `Backlog` (antes de Todo)
3. adicionar: `Review` (entre In Progress e Done)

**estado final:**
```
┌─────────┬──────┬──────────┬────────┬──────┐
│ Backlog │ Todo │ In Prog  │ Review │ Done │
└─────────┴──────┴──────────┴────────┴──────┘
```

**configurar wip limit:**

1. clicar nos `...` na coluna "In Progress"
2. selecionar: `Set column limit`
3. definir: `3` (máximo 3 tarefas simultâneas)

---

### passo 3: adicionar campos customizados

**acessar settings:**
1. clicar em `...` (canto superior direito)
2. selecionar: `Settings`
3. rolar até: `Custom fields`

**campos a adicionar:**

#### campo 1: priority
```
nome: Priority
tipo: Single select
opções:
  🔴 Critical
  🔴 High
  🟡 Medium
  🟢 Low
```

#### campo 2: story points
```
nome: Story Points
tipo: Number
```

#### campo 3: sprint
```
nome: Sprint
tipo: Iteration
duração: 2 weeks
data início: próxima segunda-feira
```

#### campo 4: component
```
nome: Component
tipo: Single select
opções:
  - DSL
  - Blender
  - OpenFOAM
  - Automation
  - Tests
  - Docs
  - CI/CD
```

---

### passo 4: configurar automações

**workflows a ativar:**

1. **item added to project**
   - quando: nova issue adicionada
   - então: mover para "Backlog"

2. **item assigned**
   - quando: issue assignada
   - então: mover para "In Progress"

3. **pull request merged**
   - quando: pr merged
   - então: mover para "Done"

4. **issue closed**
   - quando: issue fechada
   - então: mover para "Done"

---

### passo 5: adicionar issues ao projeto

**opção a: via web (manual)**

1. abrir issue: `https://github.com/USER/REPO/issues/101`
2. painel direito → `Projects`
3. selecionar: `CFD Pipeline - Scrumban`
4. definir `Status`: `Todo` ou `Backlog`

**opção b: em lote (via script)**

```python
# adicionar todas issues a um projeto
# nota: requer project id (pegar via api)

import subprocess
import json

# listar issues
result = subprocess.run(
    ['gh', 'issue', 'list', '--json', 'number', '--limit', '100'],
    capture_output=True, text=True
)
issues = json.loads(result.stdout)

# adicionar ao projeto (manual via web por enquanto)
for issue in issues:
    print(f"adicionar issue #{issue['number']} ao projeto")
    # gh cli ainda não suporta adicionar a project v2
```

---

## 📊 board scrumban final

```
┌───────────────────┬─────────────────┬─────────────────┬─────────────────┬───────────────────┐
│ BACKLOG           │ TODO            │ IN PROGRESS     │ REVIEW          │ DONE              │
│                   │                 │ (WIP: 3)        │                 │                   │
├───────────────────┼─────────────────┼─────────────────┼─────────────────┼───────────────────┤
│ #102 api rest     │ #101 análise    │ #105 ci/cd      │                 │ #001 dsl          │
│ 🟡 8pts           │ 🔴 8pts         │ 🔴 5pts         │                 │ ✅ 8pts           │
│ @unassigned       │ @dev1           │ @dev2           │                 │ @dev1             │
│                   │                 │                 │                 │                   │
│ #103 dashboard    │ #104 docker     │                 │                 │ #002 blender      │
│ 🟡 13pts          │ 🔴 8pts         │                 │                 │ ✅ 13pts          │
│ @unassigned       │ @unassigned     │                 │                 │ @dev1             │
│                   │                 │                 │                 │                   │
│ #106 postgresql   │                 │                 │                 │ #003 wizard       │
│ 🟡 5pts           │                 │                 │                 │ ✅ 5pts           │
│                   │                 │                 │                 │                   │
│                   │                 │                 │                 │ ... (8 total)     │
└───────────────────┴─────────────────┴─────────────────┴─────────────────┴───────────────────┘

sprint 1: 21pts planejados | velocity atual: 0pts | burndown: 21 → 0 em 10 dias
```

---

## 🎬 workflow diário

### morning standup (9h30, 15 min)

```bash
# 1. ver suas tarefas
gh issue list --assignee @me --label "status-in-progress"

# 2. atualizar sprint doc
code sprints/sprint-01.md

# adicionar:
# dia 5 (14/10):
# @seu-usuario:
#   - fez: implementei extração de dados openfoam (#101)
#   - fará: criar gráficos matplotlib (#101)
#   - bloqueios: nenhum

# 3. commit
git add sprints/sprint-01.md
git commit -m "docs: daily standup dia 5"
git push
```

---

### pegar nova tarefa

```bash
# 1. ver tarefas disponíveis
gh issue list --label "sprint-1" --json number,title,labels

# 2. escolher e assignar
gh issue edit 101 --add-assignee @me --add-label "status-in-progress"

# 3. criar branch
git checkout -b feature/101-analise-resultados

# 4. trabalhar
# ... implementar ...
```

---

### criar pr

```bash
# 1. commit
git add .
git commit -m "feat: implementar análise de resultados (#101)

- extrair dados perda de carga
- extrair dados velocidade
- gerar gráficos matplotlib
- exportar relatório pdf

closes #101"

# 2. push
git push origin feature/101-analise-resultados

# 3. criar pr
gh pr create \
  --title "feat: análise de resultados (#101)" \
  --body "
## descrição
implementa análise automática de resultados.

## mudanças
- extrair perda de carga
- extrair velocidade
- gráficos matplotlib
- relatório pdf

## testes
- [x] teste unitário análise
- [x] teste geração pdf

## closes
closes #101
" \
  --label "status-review"

# 4. atualizar issue
gh issue edit 101 --add-label "status-review" --remove-label "status-in-progress"
```

---

### revisar pr

```bash
# 1. listar prs para revisar
gh pr list --label "status-review"

# 2. ver pr
gh pr view 123

# 3. fazer checkout para testar
gh pr checkout 123
python scripts/automation/run_tests.py  # testar

# 4. aprovar
gh pr review 123 --approve --body "código bem estruturado, testes passando ✅"

# 5. merge
gh pr merge 123 --squash --delete-branch

# a issue #101 fecha automaticamente!
```

---

## 📈 final de sprint

### sprint review (demo)

```bash
# 1. editar sprint doc
code sprints/sprint-01.md

# adicionar na seção "sprint review":
# data: 27/10/2025
# participantes: @dev1, @dev2, @po
#
# entregáveis:
# - ✅ #101 análise de resultados - aceito
#   demo: extração automática de métricas
#   feedback: adicionar mais gráficos
#
# - ✅ #105 ci/cd - aceito
#   demo: testes no github actions
#
# métricas:
# - velocity: 13 pts (planejado: 21)
# - taxa conclusão: 62%

# 2. commit
git add sprints/sprint-01.md
git commit -m "docs: sprint 1 review"
git push
```

---

### retrospectiva

```bash
# adicionar na seção "retrospectiva":
# 
# start (começar):
# - usar conventional commits
# - tdd para features complexas
#
# stop (parar):
# - prs grandes demais
# - deixar issues sem assignee
#
# continue (continuar):
# - daily standups às 9h30
# - documentação excelente
#
# action items:
# - [ ] @dev1: configurar pre-commit hooks
# - [ ] @time: template pr com checklist
```

---

## ✅ checklist completo

### setup inicial (fazer uma vez)

- [ ] executar: `.\setup_github_scrumban.ps1 -AutoYes`
- [ ] criar github project via web
- [ ] adicionar colunas: backlog, todo, in progress, review, done
- [ ] configurar wip limits (in progress: 3)
- [ ] adicionar campos customizados: priority, story points, sprint, component
- [ ] ativar workflows de automação
- [ ] adicionar issues ao projeto
- [ ] convidar colaboradores

### planning sprint 1

- [ ] criar milestone "Sprint 1"
- [ ] copiar template: `sprints/sprint-01.md`
- [ ] selecionar issues do backlog
- [ ] estimar story points (planning poker)
- [ ] atribuir responsáveis
- [ ] mover para "todo"
- [ ] commit sprint doc

### durante sprint (diário)

- [ ] daily standup 9h30 (15min)
- [ ] atualizar sprint doc
- [ ] mover issues no board
- [ ] trabalhar em tarefas
- [ ] criar prs
- [ ] revisar código
- [ ] merge

### final sprint

- [ ] sprint review (demo)
- [ ] calcular velocity
- [ ] retrospectiva
- [ ] atualizar sprint doc
- [ ] planejar sprint 2

---

## 🎓 recursos adicionais

### documentação criada

| arquivo | descrição | linhas |
|---------|-----------|--------|
| `.github/SPRINT_TEMPLATE.md` | template sprint completo | 300 |
| `.github/GITHUB_PROJECTS_SETUP.md` | guia configuração detalhado | 600 |
| `.github/migrate_kanbn_to_github.py` | script migração | 200 |
| `GUIA_RAPIDO_COMANDOS.md` | cheat sheet comandos | 400 |
| `setup_github_scrumban.ps1` | script setup windows | 300 |

**total:** ~1800 linhas

### links úteis

- **gh cli manual:** https://cli.github.com/manual/
- **github projects:** https://docs.github.com/projects
- **conventional commits:** https://conventionalcommits.org/
- **scrumban guide:** https://scrumban.org/

---

## 🆘 suporte

**dúvidas ou problemas?**

```bash
# abrir issue
gh issue create \
  --title "[DOCS] dúvida sobre setup scrumban" \
  --body "descrição da dúvida..." \
  --label "component-docs,priority-medium"
```

**ou consultar:**
- `.github/GITHUB_PROJECTS_SETUP.md` (guia completo)
- `GUIA_RAPIDO_COMANDOS.md` (cheat sheet)

---

**sucesso no seu projeto! 🚀**

