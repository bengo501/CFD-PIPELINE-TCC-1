# guia manual para criar github project (visual e detalhado)

como a api do github projects requer permissões especiais (`project` scope), este guia te ensina a criar manualmente de forma rápida e eficiente.

---

## 🎯 resumo

**tempo total:** 5-7 minutos  
**dificuldade:** fácil  
**resultado:** github project completo com todas as issues organizadas

---

## 📋 passo 1: criar projeto (2 minutos)

### 1.1 acessar projects

```bash
# abrir no browser
start https://github.com/bengo501?tab=projects
```

ou manualmente:
1. ir para: https://github.com/bengo501
2. clicar na aba: **Projects**

### 1.2 criar novo projeto

1. clicar: **New project**
2. escolher template: **Board** ← importante!
3. preencher:
   ```
   Nome: CFD Pipeline - Scrumban
   ```
4. clicar: **Create project**

✅ projeto criado!

---

## 📊 passo 2: configurar board (1 minuto)

### 2.1 adicionar coluna "Backlog"

1. no canto inferior esquerdo, clicar: **+ Add column**
2. nome: `Backlog`
3. arrastar coluna para **primeira posição** (antes de "Todo")

### 2.2 adicionar coluna "Review"

1. clicar novamente: **+ Add column**
2. nome: `Review`
3. arrastar para **entre "In Progress" e "Done"**

### 2.3 configurar wip limit

1. clicar nos **`...`** na coluna "In Progress"
2. selecionar: **Set column limit**
3. digitar: `3`
4. salvar

**resultado:**
```
┌─────────┬──────┬──────────┬────────┬──────┐
│ Backlog │ Todo │ In Prog  │ Review │ Done │
│         │      │ (max 3)  │        │      │
└─────────┴──────┴──────────┴────────┴──────┘
```

---

## 🏷️ passo 3: adicionar campos customizados (2 minutos)

### 3.1 acessar settings

1. clicar em **`...`** (canto superior direito do board)
2. selecionar: **Settings**
3. rolar até: **Custom fields**

### 3.2 criar campo "Priority"

1. clicar: **+ New field**
2. preencher:
   ```
   Field name: Priority
   Field type: Single select
   ```
3. adicionar opções:
   ```
   🔴 Critical
   🔴 High
   🟡 Medium
   🟢 Low
   ```
4. salvar

### 3.3 criar campo "Story Points"

1. clicar: **+ New field**
2. preencher:
   ```
   Field name: Story Points
   Field type: Number
   ```
3. salvar

### 3.4 criar campo "Component"

1. clicar: **+ New field**
2. preencher:
   ```
   Field name: Component
   Field type: Single select
   ```
3. adicionar opções:
   ```
   DSL
   Blender
   OpenFOAM
   Automation
   Tests
   Docs
   CI/CD
   API
   Frontend
   ```
4. salvar

### 3.5 criar campo "Sprint"

1. clicar: **+ New field**
2. preencher:
   ```
   Field name: Sprint
   Field type: Iteration
   Duration: 2 weeks
   Start date: [próxima segunda-feira]
   ```
3. adicionar iterations:
   ```
   Sprint 1
   Sprint 2
   ```
4. salvar

✅ campos criados!

---

## 📝 passo 4: adicionar issues ao projeto (2 minutos)

### 4.1 adicionar em lote

1. no board, clicar: **+ Add item** (ou teclar `C`)
2. digitar: `#` (vai aparecer lista de issues)
3. selecionar issues **#2 a #17** (15 issues)
4. pressionar **Enter** para cada

**dica:** adicione todas de uma vez:
- `#2`, Enter
- `#3`, Enter
- ...
- `#17`, Enter

✅ todas as issues adicionadas!

---

## 🎨 passo 5: organizar issues por status (2 minutos)

### 5.1 mover issues concluídas para "Done"

arrastar para coluna **Done**:
- #2 - DSL
- #3 - Blender
- #4 - Wizard
- #5 - OpenFOAM
- #6 - Automação instalação
- #7 - Automação testes
- #8 - Testes E2E
- #9 - Documentação

### 5.2 mover issues da sprint 1 para "Todo"

arrastar para coluna **Todo**:
- #10 - Análise de resultados
- #11 - Docker
- #12 - CI/CD

### 5.3 mover issues restantes para "Backlog"

arrastar para coluna **Backlog**:
- #13 - API
- #14 - Dashboard
- #15 - PostgreSQL
- #16 - MinIO
- #17 - Otimização

**resultado:**
```
┌─────────────┬─────────────┬──────────┬────────┬─────────────┐
│ Backlog     │ Todo        │ In Prog  │ Review │ Done        │
│ #13-#17 (5) │ #10-#12 (3) │          │        │ #2-#9 (8)   │
└─────────────┴─────────────┴──────────┴────────┴─────────────┘
```

---

## 🔢 passo 6: preencher metadados (3-5 minutos)

### 6.1 issues concluídas (#2-#9)

para cada issue, clicar nela e preencher:

**#2 - DSL:**
```
Priority: High
Story Points: 8
Component: DSL
Status: Done
```

**#3 - Blender:**
```
Priority: High
Story Points: 13
Component: Blender
Status: Done
```

**#4 - Wizard:**
```
Priority: High
Story Points: 5
Component: DSL
Status: Done
```

**#5 - OpenFOAM:**
```
Priority: High
Story Points: 8
Component: OpenFOAM
Status: Done
```

**#6 - Automação instalação:**
```
Priority: High
Story Points: 8
Component: Automation
Status: Done
```

**#7 - Automação testes:**
```
Priority: High
Story Points: 8
Component: Tests
Status: Done
```

**#8 - Testes E2E:**
```
Priority: High
Story Points: 5
Component: Tests
Status: Done
```

**#9 - Documentação:**
```
Priority: High
Story Points: 8
Component: Docs
Status: Done
```

**total concluído:** 63 story points

---

### 6.2 issues sprint 1 (#10-#12)

**#10 - Análise de resultados:**
```
Priority: High
Story Points: 8
Component: Automation
Status: Todo
Sprint: Sprint 1
```

**#11 - Docker:**
```
Priority: High
Story Points: 8
Component: CI/CD
Status: Todo
Sprint: Sprint 1
```

**#12 - CI/CD:**
```
Priority: High
Story Points: 5
Component: CI/CD
Status: Todo
Sprint: Sprint 1
```

**total sprint 1:** 21 story points

---

### 6.3 issues backlog (#13-#17)

**#13 - API:**
```
Priority: Medium
Story Points: 8
Component: API
Status: Backlog
```

**#14 - Dashboard:**
```
Priority: Medium
Story Points: 13
Component: Frontend
Status: Backlog
```

**#15 - PostgreSQL:**
```
Priority: Medium
Story Points: 5
Component: Automation
Status: Backlog
```

**#16 - MinIO:**
```
Priority: Medium
Story Points: 5
Component: Automation
Status: Backlog
```

**#17 - Otimização:**
```
Priority: Low
Story Points: 5
Component: Automation
Status: Backlog
```

---

## ⚙️ passo 7: ativar workflows (opcional, 1 minuto)

### 7.1 acessar workflows

1. no projeto, clicar: **`...`** → **Workflows**

### 7.2 ativar workflows úteis

ativar:
- ✅ **Auto-add to project** (quando issue criada)
- ✅ **Item closed** → move para "Done"
- ✅ **Auto-archive items** (opcional)

---

## ✅ checklist completo

- [ ] projeto criado
- [ ] colunas configuradas (Backlog, Todo, In Progress, Review, Done)
- [ ] wip limit configurado (In Progress: 3)
- [ ] campos criados (Priority, Story Points, Component, Sprint)
- [ ] issues #2-#17 adicionadas
- [ ] issues organizadas por status
- [ ] metadados preenchidos (#2-#9)
- [ ] metadados preenchidos (#10-#12)
- [ ] metadados preenchidos (#13-#17)
- [ ] workflows ativados

---

## 📊 resultado final

### visão geral

```
project: CFD Pipeline - Scrumban
issues: 16 total
story points: 84 total

status:
  Done: 8 issues (63 pts)
  Todo: 3 issues (21 pts) - Sprint 1
  Backlog: 5 issues

velocity histórico: 63 pts (8 sprints equivalentes)
```

### board final

```
┌───────────────────┬─────────────────┬─────────────┬────────┬──────────────┐
│ BACKLOG           │ TODO            │ IN PROGRESS │ REVIEW │ DONE         │
│                   │                 │ (WIP: 3)    │        │              │
├───────────────────┼─────────────────┼─────────────┼────────┼──────────────┤
│ #13 API           │ #10 Análise     │             │        │ #2 DSL       │
│ 🟡 Medium, 8pts   │ 🔴 High, 8pts   │             │        │ ✅ High, 8pts│
│ API               │ Automation      │             │        │ DSL          │
│                   │ Sprint 1        │             │        │              │
│                   │                 │             │        │ #3 Blender   │
│ #14 Dashboard     │ #11 Docker      │             │        │ ✅ High, 13  │
│ 🟡 Medium, 13pts  │ 🔴 High, 8pts   │             │        │              │
│ Frontend          │ CI/CD           │             │        │ #4-#9 (6)    │
│                   │ Sprint 1        │             │        │ (55 pts)     │
│                   │                 │             │        │              │
│ #15-#17 (3)       │ #12 CI/CD       │             │        │              │
│ (15 pts)          │ 🔴 High, 5pts   │             │        │              │
│                   │ Sprint 1        │             │        │              │
└───────────────────┴─────────────────┴─────────────┴────────┴──────────────┘
```

---

## 🔜 próximos passos

### 1. editar sprint planning

```bash
code sprints/sprint-01.md
```

preencher:
- objetivo da sprint
- backlog selecionado
- critérios de sucesso

### 2. iniciar trabalho

```bash
# pegar issue
gh issue edit 10 --add-assignee @me

# criar branch
git checkout -b feature/10-analise-resultados
```

### 3. daily standup (9h30)

atualizar:
- board no github projects
- sprints/sprint-01.md

---

## 💡 dicas

### atalhos úteis

- `C` - criar novo item
- `E` - editar item
- `Del` - deletar item
- `Cmd/Ctrl + K` - buscar

### visualizações

criar views customizadas:
1. clicar: **+ New view**
2. tipos:
   - **Table** - ver todos os campos
   - **Board** - kanban visual
   - **Roadmap** - timeline

### filtros

exemplos úteis:
```
status:Todo sprint:"Sprint 1"
priority:High assignee:@me
status:Done -status:archived
```

---

## 📚 documentação

- guia completo: `.github/GITHUB_PROJECTS_SETUP.md`
- cheat sheet: `GUIA_RAPIDO_COMANDOS.md`
- template sprint: `.github/SPRINT_TEMPLATE.md`

---

**parabéns! seu github project está pronto! 🎉**

