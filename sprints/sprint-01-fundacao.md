# sprint 1 - fundação dsl e gestão

**período:** 15/09/2025 - 22/09/2025  
**duração:** 1 semana  
**status:** ✅ concluído

---

## 🎯 objetivo da sprint

implementar a fundação do projeto: domain-specific language (.bed), compilador antlr e sistema de gestão ágil (kanban/scrumban).

---

## 📋 backlog da sprint

### tarefas concluídas

| tarefa | descrição | story points | status |
|--------|-----------|--------------|--------|
| task-001 | implementar dsl (.bed) com antlr | 13 | ✅ concluído |
| task-002 | bed wizard interativo | 8 | ✅ concluído |
| task-007 | configurar kanban/scrumban | 3 | ✅ concluído |
| task-008 | integrar github projects | 3 | ✅ concluído |

**total story points:** 27 pts

---

## ✅ entregáveis

### task-001: dsl + antlr (13 pts)

**entregas:**
- ✅ gramática `Bed.g4` completa (7 seções)
- ✅ compilador antlr instalado (v4.13.1)
- ✅ parser python gerado (`dsl/generated/`)
- ✅ `bed_compiler_antlr_standalone.py` (400+ linhas)
- ✅ suporte a unidades (m, cm, kg, Pa)
- ✅ normalização para si
- ✅ validação de sintaxe
- ✅ geração de `.bed.json`

**arquivos criados:**
- `dsl/grammar/Bed.g4`
- `dsl/compiler/bed_compiler_antlr_standalone.py`
- `dsl/generated/BedLexer.py`
- `dsl/generated/BedParser.py`
- `dsl/generated/BedListener.py`

### task-002: bed wizard (8 pts)

**entregas:**
- ✅ interface cli interativa
- ✅ modo 1: responder perguntas
- ✅ modo 2: editar arquivo padrão
- ✅ modo 3: blender (apenas 3d)
- ✅ modo 4: blender interativo (abre gui)
- ✅ modo 5: ajuda completa (47 parâmetros)
- ✅ modo 6: documentação html
- ✅ validação de ranges (min/max)
- ✅ confirmação com espaço/enter

**arquivos criados:**
- `dsl/bed_wizard.py` (1400+ linhas)
- `dsl/documentacao.html`
- `dsl/README_SISTEMA_AJUDA.md`
- `dsl/EXEMPLO_USO_AJUDA.md`

### task-007: kanban/scrumban (3 pts)

**entregas:**
- ✅ estrutura `.kanbn/` criada
- ✅ colunas definidas (backlog, todo, in progress, done)
- ✅ 50+ tasks organizadas
- ✅ templates sprint planning
- ✅ templates issue (feature, bug, task)
- ✅ documentação scrumban

**arquivos criados:**
- `.kanbn_boards/tcc1/.kanbn/index.md`
- `.kanbn_boards/tcc1/.kanbn/tasks/` (50+ arquivos)
- `.github/SPRINT_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/`

### task-008: github projects (3 pts)

**entregas:**
- ✅ script `migrate_kanbn_to_github.py`
- ✅ labels padronizados criados
- ✅ milestones configurados
- ✅ guia setup manual
- ✅ scripts powershell e bash

**arquivos criados:**
- `.github/migrate_kanbn_to_github.py`
- `.github/GITHUB_PROJECTS_SETUP.md`
- `setup_github_scrumban.sh`
- `setup_github_scrumban.ps1`

---

## 📊 métricas da sprint

### velocity

```
story points planejados: 27
story points concluídos: 27
velocity: 27 pts (100%)
```

### commits

- total: 15+ commits
- arquivos modificados: 30+
- linhas adicionadas: 4000+

### qualidade

- bugs encontrados: 3 (corrigidos)
- code review: aprovado
- documentação: 100%

---

## 🎬 sprint review

**data:** 22/09/2025

### demos realizadas

1. **dsl e compilador**
   - demo: criar arquivo `.bed` e compilar para `.bed.json`
   - resultado: sucesso, sintaxe clara e intuitiva
   - feedback: excelente, facilitará muito o uso

2. **bed wizard**
   - demo: modo interativo e modo blender
   - resultado: interface amigável, validação funcional
   - feedback: sistema de ajuda muito útil

3. **kanban**
   - demo: estrutura completa de tasks
   - resultado: 50+ tasks organizadas por sprint
   - feedback: ótima organização

---

## 🔄 retrospectiva

**data:** 22/09/2025

### start (começar a fazer)

- ✅ usar antlr para dsls complexas
- ✅ validar input do usuário sempre
- ✅ documentar inline extensivamente

### stop (parar de fazer)

- ❌ commits muito grandes
- ❌ criar arquivos sem documentação

### continue (continuar fazendo)

- ✅ testes manuais constantes
- ✅ iteração rápida baseada em feedback
- ✅ commits atômicos

### melhorias identificadas

1. adicionar testes unitários para compilador
2. criar exemplos de `.bed` válidos e inválidos
3. melhorar mensagens de erro do antlr

---

## 📌 dificuldades e soluções

### impedimentos

| problema | solução | tempo |
|----------|---------|-------|
| java não no path | adicionar paths explícitos no código | 2h |
| conflito labels antlr | renomear labels na gramática | 1h |
| wizard não salva arquivo | corrigir path do json | 1h |

---

## 🔜 próxima sprint

**sprint 2 - modelagem e automação**

### candidatos

- task-003: blender headless (13 pts)
- task-004: setup openfoam (13 pts)
- task-005: testes e2e (8 pts)
- task-006: documentação (5 pts)

**total estimado:** 39 pts

---

**sprint 1 concluída com sucesso! 🎉**

