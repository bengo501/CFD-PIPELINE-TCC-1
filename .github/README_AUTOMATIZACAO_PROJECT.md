# automação completa github project

scripts python para criar e configurar github project v2 automaticamente.

---

## 📋 índice

1. [visão geral](#visão-geral)
2. [pré-requisitos](#pré-requisitos)
3. [uso rápido](#uso-rápido)
4. [scripts disponíveis](#scripts-disponíveis)
5. [o que é automatizado](#o-que-é-automatizado)
6. [configuração manual](#configuração-manual)
7. [troubleshooting](#troubleshooting)

---

## 🎯 visão geral

estes scripts automatizam a criação e configuração completa de um github project v2 com:

- ✅ criação do projeto
- ✅ campos customizados (priority, story points, component, sprint)
- ✅ adição de todas as issues
- ✅ preenchimento automático de metadados
- ✅ organização por status (done/todo/backlog)

**tempo de execução:** 2-3 minutos + ~2 minutos de configuração manual

---

## 📦 pré-requisitos

### 1. github cli instalado e autenticado

```bash
# verificar instalação
gh --version

# autenticar
gh auth login

# verificar autenticação
gh auth status
```

### 2. python 3.7+

```bash
python --version
```

### 3. issues criadas no repositório

as issues devem estar criadas (números 2-17).  
se não estiverem, execute primeiro:

```bash
python .github/migrate_kanbn_to_github.py --execute
```

---

## 🚀 uso rápido

### opção 1: script mestre (recomendado)

executa tudo automaticamente com pause para configuração manual:

```bash
python .github/setup_project_complete.py
```

**o que faz:**
1. cria projeto "CFD Pipeline - Scrumban"
2. adiciona campos customizados
3. adiciona todas as issues
4. pausa para configuração manual (colunas, sprints)
5. preenche metadados automaticamente

**duração:** ~5 minutos total

---

### opção 2: passo a passo

execute cada script individualmente:

#### passo 1: criar projeto

```bash
python .github/create_github_project.py
```

**resultado:**
- projeto criado
- campos: Priority, Story Points, Component, Sprint
- todas as issues adicionadas

**url do projeto:** será exibida no output

---

#### passo 2: configuração manual (2 minutos)

acesse o projeto e configure:

1. **adicionar colunas:**
   - arrastar "Backlog" do menu lateral
   - arrastar "Review" do menu lateral
   - ordem final: Backlog → Todo → In Progress → Review → Done

2. **configurar wip limit:**
   - clicar em `...` na coluna "In Progress"
   - "Set column limit" → `3`

3. **configurar sprints (iterations):**
   - settings → Sprint field
   - "Edit iterations"
   - adicionar:
     - Sprint 1 (próxima segunda + 2 semanas)
     - Sprint 2 (data seguinte + 2 semanas)

---

#### passo 3: preencher campos

```bash
python .github/populate_project_fields.py
```

**resultado:**
- priority definida para todas as issues
- story points preenchidos
- component atribuído
- status configurado (Done/Todo/Backlog)
- sprint 1 atribuída às issues prioritárias

---

## 📄 scripts disponíveis

### 1. `create_github_project.py`

**função:** cria projeto e estrutura inicial

**uso:**
```bash
python .github/create_github_project.py
```

**o que faz:**
- cria projeto v2 via graphql api
- adiciona campo "Priority" (Critical/High/Medium/Low)
- adiciona campo "Story Points" (número)
- adiciona campo "Component" (DSL/Blender/OpenFOAM/etc)
- adiciona campo "Sprint" (iteration)
- adiciona todas as issues ao projeto

**output:**
```
======================================================================
  CRIADOR AUTOMATICO DE GITHUB PROJECT
======================================================================

[1/7] verificando autenticacao...
[ok] usuario detectado: bengo501

[2/7] criando github project...
[ok] projeto criado!
    id: PVT_kwDOxxxxx
    numero: 1
    url: https://github.com/users/bengo501/projects/1

[3/7] configurando campos customizados...
[ok] campo 'Priority' criado
[ok] campo 'Story Points' criado
[ok] campo 'Component' criado
[ok] campo 'Sprint' criado

[4/7] buscando issues do repositorio...
[ok] encontradas 16 issues

[5/7] adicionando issues ao projeto...
[ok] 16/16 issues adicionadas

✅ projeto criado com sucesso!
```

---

### 2. `populate_project_fields.py`

**função:** preenche metadados das issues

**uso:**
```bash
python .github/populate_project_fields.py
```

**o que faz:**
- busca projeto "CFD Pipeline - Scrumban"
- para cada issue (2-17):
  - define Priority
  - define Story Points
  - define Component
  - move para status correto (Done/Todo/Backlog)
  - atribui Sprint 1 (se aplicável)

**mapeamento de metadados:**
```python
# issues concluidas (Done)
#2-#9: priority=High, status=Done, story_points=5-13

# sprint 1 (Todo)
#10: priority=High, story_points=8, component=Automation, sprint=Sprint 1
#11: priority=High, story_points=8, component=CI/CD, sprint=Sprint 1
#12: priority=High, story_points=5, component=CI/CD, sprint=Sprint 1

# backlog
#13-#17: priority=Medium/Low, status=Backlog
```

**output:**
```
======================================================================
  PREENCHEDOR AUTOMATICO DE CAMPOS
======================================================================

[1/5] buscando projeto...
[ok] projeto encontrado: CFD Pipeline - Scrumban (#1)
[ok] campos encontrados: ['Status', 'Priority', 'Story Points', 'Component', 'Sprint']

[3/5] preenchendo campos das issues...

[info] processando issue #2...
[ok] priority: High
[ok] story points: 8
[ok] component: DSL
[ok] status: Done

...

[ok] 16/16 issues configuradas

✅ campos preenchidos com sucesso!
```

---

### 3. `setup_project_complete.py`

**função:** script mestre que orquestra tudo

**uso:**
```bash
python .github/setup_project_complete.py
```

**fluxo:**
1. executa `create_github_project.py`
2. pausa para configuração manual
3. executa `populate_project_fields.py`
4. exibe resumo final

---

## ✅ o que é automatizado

### 100% automático

- ✅ criação do projeto v2
- ✅ adição de campos customizados
- ✅ adição de issues ao projeto
- ✅ preenchimento de priority
- ✅ preenchimento de story points
- ✅ preenchimento de component
- ✅ definição de status (done/todo/backlog)
- ✅ atribuição de sprint

### requer configuração manual

- ⚠️ adicionar colunas Backlog e Review
- ⚠️ configurar wip limits
- ⚠️ criar iterations (Sprint 1, Sprint 2)
- ⚠️ ativar workflows (opcional)

**motivo:** github projects api ainda não suporta 100% das configurações via api

---

## 🔧 configuração manual

### adicionar colunas

1. abrir projeto
2. clicar em `+` ao lado de "Done"
3. selecionar: "Backlog" (ou criar nova)
4. arrastar para primeira posição
5. repetir para "Review" (entre In Progress e Done)

**ordem final:**
```
Backlog → Todo → In Progress → Review → Done
```

---

### configurar wip limit

1. clicar em `...` na coluna "In Progress"
2. selecionar: "Set column limit"
3. digitar: `3`
4. salvar

---

### configurar sprints (iterations)

1. clicar em qualquer issue no projeto
2. painel direito → campo "Sprint"
3. clicar em "Edit field"
4. "Edit iterations"
5. adicionar:
   ```
   Sprint 1
     start: próxima segunda-feira
     duration: 2 weeks
   
   Sprint 2
     start: (automático após Sprint 1)
     duration: 2 weeks
   ```
6. salvar

---

## 🐛 troubleshooting

### erro: "not authenticated"

```bash
gh auth login
gh auth status
```

### erro: "project not found" ao popular campos

**causa:** projeto ainda não foi criado

**solução:**
```bash
python .github/create_github_project.py
```

### erro: "issue not found in project"

**causa:** issues não foram adicionadas ao projeto

**solução:** re-executar criação do projeto

### erro: "field not found"

**causa:** campos customizados não foram criados

**solução:**
```bash
# deletar projeto e recriar
python .github/create_github_project.py
```

### erro: "iteration not found" ao popular sprint

**causa:** iterations (Sprint 1, Sprint 2) não foram configuradas manualmente

**solução:** seguir passo "configurar sprints" acima

---

## 📊 resultado final esperado

### board visual

```
┌───────────────┬─────────────┬──────────────┬─────────────┬──────────────┐
│ BACKLOG       │ TODO        │ IN PROGRESS  │ REVIEW      │ DONE         │
│               │             │ (WIP: 3)     │             │              │
├───────────────┼─────────────┼──────────────┼─────────────┼──────────────┤
│ #13 API       │ #10 Análise │              │             │ #2 DSL       │
│ 🟡 8pts       │ 🔴 8pts     │              │             │ ✅ 8pts      │
│ Medium        │ High        │              │             │ High         │
│ API           │ Automation  │              │             │ DSL          │
│               │ Sprint 1    │              │             │              │
│               │             │              │             │              │
│ #14 Dashboard │ #11 Docker  │              │             │ #3 Blender   │
│ 🟡 13pts      │ 🔴 8pts     │              │             │ ✅ 13pts     │
│               │ Sprint 1    │              │             │              │
│               │             │              │             │              │
│ #15-#17       │ #12 CI/CD   │              │             │ #4-#9 (6)    │
│ (3 issues)    │ 🔴 5pts     │              │             │ (6 issues)   │
│               │ Sprint 1    │              │             │              │
└───────────────┴─────────────┴──────────────┴─────────────┴──────────────┘

sprint 1: 21pts planejados (3 issues)
velocity historico: 63pts (8 issues concluidas)
```

### métricas

```
total geral:
  issues: 16
  story points: 84

por status:
  Done: 8 issues (63 pts)
  Todo: 3 issues (21 pts) - Sprint 1
  Backlog: 5 issues

por prioridade:
  High: 11 issues
  Medium: 4 issues
  Low: 1 issue

por componente:
  DSL: 2 issues
  Blender: 1 issue
  OpenFOAM: 1 issue
  Automation: 5 issues
  Tests: 2 issues
  Docs: 1 issue
  CI/CD: 2 issues
  API: 1 issue
  Frontend: 1 issue
```

---

## 🔗 próximos passos

após executar os scripts:

1. **revisar projeto:**
   ```bash
   # abrir no browser
   gh project list
   ```

2. **editar sprint doc:**
   ```bash
   code sprints/sprint-01.md
   ```

3. **iniciar trabalho:**
   ```bash
   # pegar issue
   gh issue edit 10 --add-assignee @me --add-label "status-in-progress"
   
   # criar branch
   git checkout -b feature/10-analise-resultados
   ```

4. **daily standup:**
   - horário: 9h30
   - duração: 15 minutos
   - atualizar: sprints/sprint-01.md

---

## 📚 documentação relacionada

- `.github/GITHUB_PROJECTS_SETUP.md` - guia completo manual
- `README_SETUP_SCRUMBAN.md` - guia visual
- `GUIA_RAPIDO_COMANDOS.md` - cheat sheet
- `.github/SPRINT_TEMPLATE.md` - template sprint

---

## 🤝 contribuindo

encontrou um bug ou tem sugestão?

```bash
gh issue create \
  --title "[AUTOMATION] descrição" \
  --label "component-automation,priority-medium"
```

---

**pronto para criar seu projeto? execute:**
```bash
python .github/setup_project_complete.py
```

🚀

