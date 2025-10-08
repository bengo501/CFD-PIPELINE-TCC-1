# guia de configuração github projects + issues

guia completo para configurar kanban scrumban no github projects integrado com issues.

---

## 📋 índice

1. [criar projeto no github](#1-criar-projeto-no-github)
2. [configurar views (visões)](#2-configurar-views)
3. [configurar fields (campos)](#3-configurar-fields)
4. [configurar automation](#4-configurar-automation)
5. [criar issues](#5-criar-issues)
6. [workflow diário](#6-workflow-diário)
7. [métricas e relatórios](#7-métricas-e-relatórios)

---

## 1️⃣ criar projeto no github

### passo 1.1: acessar projects

1. vá para seu repositório no github
2. clique na aba **"Projects"**
3. clique em **"New project"** (ou **"Link a project" > "New project"**)

### passo 1.2: escolher template

**opções:**
- **board** (kanban) ← escolher esta
- table (tabela)
- roadmap (timeline)

**configuração inicial:**
```
nome: CFD Pipeline - Scrumban
descrição: gerenciamento kanban + scrum do projeto cfd-pipeline-tcc
visibilidade: public (ou private)
```

### passo 1.3: estrutura inicial

o github projects cria automaticamente:
```
┌─────────┬──────────┬─────────────┐
│ Todo    │ In Prog  │ Done        │
│         │          │             │
└─────────┴──────────┴─────────────┘
```

---

## 2️⃣ configurar views (visões)

### view 1: board (kanban principal)

**configuração:**
1. clique no nome da view (canto superior esquerdo)
2. clique em **"⚙️ Settings"**
3. renomear para: **"Sprint Board"**

**adicionar colunas:**
1. clique no **"+"** depois da última coluna
2. adicionar:
   - **"Backlog"** (novo)
   - **"Todo"** (já existe)
   - **"In Progress"** (já existe)
   - **"Review"** (novo)
   - **"Done"** (já existe)

**configurar wip limits:**
1. clique nos **"..."** na coluna "In Progress"
2. selecione **"Set column limit"**
3. definir limite: **3** (máximo 3 tarefas simultâneas)

**resultado:**
```
┌─────────┬──────┬──────────┬────────┬──────┐
│ Backlog │ Todo │ In Prog  │ Review │ Done │
│         │      │ (max 3)  │        │      │
└─────────┴──────┴──────────┴────────┴──────┘
```

### view 2: sprint planning (tabela)

**criar nova view:**
1. clique no **"+"** ao lado do nome da view atual
2. selecione **"New view"**
3. escolher **"Table"**
4. renomear para: **"Sprint Planning"**

**colunas visíveis:**
- title (título)
- assignees (responsáveis)
- status (coluna kanban)
- priority (prioridade)
- sprint (sprint atual)
- story points (estimativa)
- labels (etiquetas)

### view 3: roadmap (timeline)

**criar view roadmap:**
1. adicionar view: **"New view" > "Roadmap"**
2. renomear para: **"Project Roadmap"**
3. configurar:
   - **start date:** data de início
   - **target date:** data de entrega
   - agrupar por: **sprint**

---

## 3️⃣ configurar fields (campos)

### campos padrão do github

```
✅ já existem:
- title
- assignees
- status
- labels
- milestone
- repository
```

### adicionar campos customizados

**passo 3.1: acessar field settings**
1. clique em **"..."** (canto superior direito)
2. selecione **"Settings"**
3. role até **"Custom fields"**

**passo 3.2: adicionar campo "priority"**
```
nome: Priority
tipo: Single select
opções:
  🔴 Critical
  🔴 High
  🟡 Medium
  🟢 Low
cor: vermelho, amarelo, verde
```

**passo 3.3: adicionar campo "story points"**
```
nome: Story Points
tipo: Number
```

**passo 3.4: adicionar campo "sprint"**
```
nome: Sprint
tipo: Iteration
duração: 2 weeks
data início: [data da próxima segunda]
```

**passo 3.5: adicionar campo "component"**
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

**passo 3.6: adicionar campo "type"**
```
nome: Type
tipo: Single select
opções:
  - Feature
  - Bug
  - Task
  - Epic
```

**resultado:**
```
campos disponíveis:
✅ title
✅ assignees
✅ status (backlog/todo/in progress/review/done)
✅ labels
✅ priority (critical/high/medium/low)
✅ story points (número)
✅ sprint (iteration)
✅ component (dsl/blender/openfoam/etc)
✅ type (feature/bug/task/epic)
```

---

## 4️⃣ configurar automation

### workflow 1: mover para "in progress" quando assignee é adicionado

**configuração:**
1. ir em **"⚙️ Workflows"**
2. ativar **"Item added to project"**
3. criar novo workflow:

```yaml
nome: auto-assign to in progress
quando: item é assignado
então: mover para "in progress"
```

### workflow 2: mover para "done" quando issue é fechada

**configuração:**
1. ativar **"Item closed"**
2. ação: mover para "done"

```yaml
nome: auto-close to done
quando: issue é fechada
então: mover para "done"
```

### workflow 3: adicionar label por status

**criar custom workflow:**
```yaml
nome: auto-label by status
quando: item move para coluna
então: adicionar label correspondente

regras:
- status = "in progress" → label "status: in-progress"
- status = "review" → label "status: review"
- status = "done" → label "status: done"
```

---

## 5️⃣ criar issues

### método 1: criar issue direto no board

**passo a passo:**
1. na view "Sprint Board"
2. clique no **"+"** na coluna desejada (ex: "Todo")
3. digitar título rápido: "implementar análise de resultados"
4. pressionar **Enter**
5. clicar na issue criada para adicionar detalhes

**adicionar detalhes:**
```
título: [FEATURE] implementar análise automática de resultados

descrição: [usar template de feature]

campos:
- assignees: @seu-usuario
- priority: High
- story points: 8
- sprint: Sprint 1
- component: Automation
- type: Feature
- labels: enhancement, priority-high
```

### método 2: criar issue no repositório

**passo a passo:**
1. ir na aba **"Issues"** do repositório
2. clicar em **"New issue"**
3. escolher template: **"Feature request"**
4. preencher template
5. no painel direito, adicionar ao projeto:
   - **Projects:** CFD Pipeline - Scrumban
   - **Status:** Todo (ou outra coluna)

### método 3: converter tarefas kanban em issues

**se você já tem tarefas no `.kanbn`:**

**script de conversão:**
```bash
# criar issues a partir das tarefas kanban
# exemplo: task-101.md → issue #101

# manual via github cli
gh issue create \
  --title "[FEATURE] análise automática de resultados" \
  --body-file .kanbn_boards/tcc1/.kanbn/tasks/task-101.md \
  --label "enhancement,priority-high" \
  --project "CFD Pipeline - Scrumban"
```

---

## 6️⃣ workflow diário

### rotina matinal (antes do standup)

```bash
# 1. atualizar projeto local
git pull origin main

# 2. acessar github projects
# url: https://github.com/users/[seu-user]/projects/[num]

# 3. verificar sprint board
- revisar coluna "in progress"
- identificar bloqueios
- atualizar status das tarefas
```

### durante o standup

**para cada dev:**
1. dizer o que fez (mostrar issues movidas para "review" ou "done")
2. dizer o que fará (apontar issue em "in progress")
3. mencionar bloqueios (adicionar comment na issue)

**no github:**
```
comentar na issue:
"@time bloqueio: preciso de acesso ao servidor openfoam"
```

### durante o dia

**ao começar tarefa:**
1. mover issue de "todo" para "in progress"
2. assignar para você
3. criar branch: `feature/101-analise-resultados`

**ao concluir tarefa:**
1. criar pr: "feat: implementar análise de resultados (#101)"
2. mover issue para "review"
3. solicitar code review

**ao aprovar review:**
1. merge pr
2. issue automaticamente move para "done"
3. branch automaticamente deletada

---

## 7️⃣ métricas e relatórios

### view: sprint metrics

**criar nova view tipo "table":**
```
nome: Sprint Metrics
filtros:
  - sprint = "current"
  - status != "done"
colunas:
  - title
  - assignees
  - story points
  - status
  - days in progress (calculado)
```

### usar github insights

**acessar:**
1. aba **"Insights"** do repositório
2. seção **"Projects"**

**métricas disponíveis:**
- velocity (story points por sprint)
- cycle time (tempo em "in progress")
- lead time (tempo total)
- throughput (issues fechadas por semana)

### criar dashboard custom

**usar github api:**
```python
# exemplo: buscar issues da sprint atual
import requests

url = "https://api.github.com/repos/[user]/[repo]/issues"
params = {
    "state": "all",
    "labels": "sprint-1",
    "per_page": 100
}

response = requests.get(url, params=params)
issues = response.json()

# calcular velocity
total_points = sum(issue['story_points'] for issue in issues if issue['state'] == 'closed')
print(f"velocity sprint 1: {total_points} pts")
```

---

## 📊 exemplo prático completo

### sprint 1 setup

**1. criar sprint iteration**
```
settings > custom fields > sprint
adicionar iteration:
  nome: Sprint 1
  início: 14/10/2025
  fim: 27/10/2025
```

**2. criar issues para sprint 1**

**issue #101:**
```
título: [FEATURE] implementar análise automática de resultados
template: feature request
campos:
  - assignees: @dev1
  - status: Todo
  - priority: High
  - story points: 8
  - sprint: Sprint 1
  - component: Automation
  - labels: enhancement, priority-high, sprint-1
```

**issue #105:**
```
título: [TASK] configurar ci/cd pipeline
template: task
campos:
  - assignees: @dev2
  - status: Todo
  - priority: High
  - story points: 5
  - sprint: Sprint 1
  - component: CI/CD
  - labels: task, priority-high, sprint-1
```

**3. durante sprint**

**dia 1:**
```
@dev1 move #101 de "todo" → "in progress"
@dev2 move #105 de "todo" → "in progress"

board:
┌─────────┬──────┬─────────────┬────────┬──────┐
│ Backlog │ Todo │ In Progress │ Review │ Done │
├─────────┼──────┼─────────────┼────────┼──────┤
│ #102    │ #104 │ #101 @dev1  │        │ #001 │
│ #103    │      │ #105 @dev2  │        │ #002 │
│         │      │             │        │ ...  │
└─────────┴──────┴─────────────┴────────┴──────┘
```

**dia 3:**
```
@dev2 completa #105
  - cria pr: "feat: ci/cd pipeline (#105)"
  - move para "review"
  - solicita review de @dev1

board:
┌─────────┬──────┬─────────────┬─────────┬──────┐
│ Backlog │ Todo │ In Progress │ Review  │ Done │
├─────────┼──────┼─────────────┼─────────┼──────┤
│ #102    │ #104 │ #101 @dev1  │ #105    │ ...  │
│ #103    │      │             │ @dev2   │      │
└─────────┴──────┴─────────────┴─────────┴──────┘
```

**dia 5:**
```
@dev1 aprova review #105
  - merge pr
  - #105 automaticamente move para "done"
  
@dev2 pega próxima tarefa
  - move #104 de "todo" → "in progress"
```

**dia 10 (final sprint):**
```
board final:
┌─────────┬──────┬─────────────┬────────┬──────┐
│ Backlog │ Todo │ In Progress │ Review │ Done │
├─────────┼──────┼─────────────┼────────┼──────┤
│ #102    │      │             │        │ #101 │
│ #103    │      │             │        │ #105 │
│ #106    │      │             │        │ #104 │
└─────────┴──────┴─────────────┴────────┴──────┘

métricas:
- story points concluídos: 21
- velocity: 21 pts
- cycle time médio: 6 dias
```

---

## 🔗 recursos úteis

### links oficiais
- [github projects docs](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [github projects beta](https://github.com/features/issues)
- [automation workflows](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project)

### integrações
- **zenhub:** extensão chrome para github
- **waffle:** kanban sobre github issues
- **github cli:** `gh project`, `gh issue`

### automação avançada
```bash
# github cli - criar issue
gh issue create --title "titulo" --body "corpo" --label "bug"

# github cli - adicionar ao projeto
gh issue edit 101 --add-project "CFD Pipeline"

# github cli - mover card
gh project item-edit --field Status="In Progress"
```

---

## ✅ checklist de configuração

- [ ] projeto criado no github
- [ ] views configuradas (board, table, roadmap)
- [ ] campos customizados adicionados (priority, story points, sprint, component)
- [ ] wip limits definidos (in progress: max 3)
- [ ] workflows de automação ativados
- [ ] templates de issues criados (feature, bug, task)
- [ ] primeira sprint criada (iteration)
- [ ] issues da sprint adicionadas ao projeto
- [ ] time adicionado como colaboradores
- [ ] documentação compartilhada com time

---

## 🎯 próximos passos

1. **criar primeiro sprint:**
   ```bash
   # adicionar issues #101, #105, #104
   # definir sprint 1 (2 semanas)
   # atribuir responsáveis
   ```

2. **executar sprint planning:**
   - reunião de 1-2h
   - selecionar issues do backlog
   - estimar story points
   - comprometer com escopo

3. **iniciar daily standups:**
   - horário fixo (9h30)
   - 15 minutos
   - atualizar board ao vivo

4. **ao final da sprint:**
   - sprint review (demo)
   - retrospectiva
   - planejar próxima sprint

---

quer que eu crie um script para automatizar a migração das tarefas do `.kanbn` para o github issues? 🚀

