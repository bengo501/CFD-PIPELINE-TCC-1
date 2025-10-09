# milestones e sprints - github projects

## 📅 milestones (sprints) do projeto

### ✅ sprint 1 - fundação dsl e gestão

**período:** 15/09/2025 - 22/09/2025  
**status:** concluído (100%)  
**velocity:** 27 story points

**issues:**
- #1 - implementar dsl (.bed) com antlr (13 pts) ✅
- #2 - bed wizard interativo (8 pts) ✅
- #7 - configurar kanban/scrumban (3 pts) ✅
- #8 - integrar github projects (3 pts) ✅

**entregas:**
- dsl .bed completa
- compilador antlr funcional
- bed wizard com 6 modos
- sistema de gestão kanban

---

### ✅ sprint 2 - modelagem e automação

**período:** 23/09/2025 - 07/10/2025  
**status:** concluído (100%)  
**velocity:** 39 story points

**issues:**
- #3 - integrar blender headless (13 pts) ✅
- #4 - setup openfoam automatizado (13 pts) ✅
- #5 - testes e2e automatizados (8 pts) ✅
- #6 - documentar pipeline completo (5 pts) ✅

**entregas:**
- geração 3d automatizada
- casos openfoam automatizados
- 6 testes e2e
- documentação técnica

---

### ✅ sprint 3 - web e api

**período:** 08/10/2025 - 09/10/2025  
**status:** concluído (100%)  
**velocity:** 26 story points

**issues:**
- #18 - backend fastapi com api rest (13 pts) ✅
- #19 - frontend react com interface web (13 pts) ✅

**entregas:**
- api rest completa (15 endpoints)
- frontend react moderno
- integração full-stack
- documentação swagger

---

### ✅ sprint 4 - documentação

**período:** 09/10/2025  
**status:** concluído (100%)  
**linhas:** ~7050

**entregas:**
- bibliografia completa (46 refs)
- referencial teórico (1800 linhas)
- estrutura openfoam (1500 linhas)
- scripts python (2500 linhas)
- kanban e sprints atualizados

---

### ⏳ sprint 5 - correções e validação (planejada)

**período:** 10/10/2025 - 17/10/2025  
**status:** planejado  
**velocity estimado:** 24 story points

**issues candidatas:**
- #20 - documentação completa openfoam (3 pts)
- #21 - corrigir física blender (8 pts) 🔴 bug crítico
- #22 - pipeline openfoam completo (8 pts)
- #25 - pós-processamento cfd (5 pts)

**foco:** correções de bugs e completar funcionalidades

---

### ⏳ sprint 6 - persistência (planejada)

**período:** 18/10/2025 - 01/11/2025  
**status:** planejado  
**velocity estimado:** 21 story points

**issues candidatas:**
- #23 - implementar postgresql (8 pts)
- #26 - integrar minio artefatos (5 pts)
- #27 - threejs visualização 3d (8 pts)

**foco:** banco de dados e visualização

---

### ⏳ sprint 7 - validação científica (planejada)

**período:** 02/11/2025 - 15/11/2025  
**status:** planejado  
**velocity estimado:** 21 story points

**issues candidatas:**
- #28 - validação com equação de ergun (13 pts)
- #29 - estudo de malha gci (8 pts)

**foco:** validação numérica e física

---

### ⏳ sprint 8 - finalização tcc1 (planejada)

**período:** 16/11/2025 - 30/11/2025  
**status:** planejado  
**velocity estimado:** 11 story points

**issues candidatas:**
- #30 - escrever proposta tcc1 (8 pts)
- #31 - preparar apresentação tcc1 (3 pts)

**foco:** entrega final tcc1

---

## 📊 resumo de velocity

| sprint | período | pts planejados | pts concluídos | taxa |
|--------|---------|----------------|----------------|------|
| 1 | 1 semana | 27 | 27 | 100% |
| 2 | 2 semanas | 39 | 39 | 100% |
| 3 | 2 dias | 26 | 26 | 100% |
| 4 | 1 dia | - | - | 100% |
| **total concluído** | | **92** | **92** | **100%** |
| **pendente tcc1** | | | **77** | - |

### velocity médio

- **sprints 1-3:** 30.7 pts/sprint
- **previsão restante:** 3 sprints para completar tcc1

---

## 🎯 progresso tcc1

```
concluído:    ████████████░░░░░░░  54.4% (92/169 pts)
pendente:     ░░░░░░░░████████████  45.6% (77/169 pts)
```

### atividades completadas

- ✅ a1: levantamento bibliográfico
- ✅ a2: especificação da dsl
- ✅ a3: parser/compilador da dsl
- ✅ a9: api fastapi
- ✅ a10: frontend react
- ✅ a11: integração e2e
- ✅ a13: documentação tcc1 (parcial)
- ✅ a15: gestão e checkpoints

### atividades pendentes

- ⏳ a4: geração geométrica (bug física)
- ⏳ a5: template openfoam (parcial)
- ⏳ a6: pipeline malha/solver
- ⏳ a7: pós-processamento
- ⏳ a8: persistência db/minio
- ⏳ a12: validação numérica
- ⏳ a14: apresentação

---

## 🔧 como usar no github

### criar milestones

```bash
# sprint 1
gh milestone create "Sprint 1 - Fundação" \
  --description "DSL, compilador, kanban" \
  --due-date 2025-09-22

# sprint 2
gh milestone create "Sprint 2 - Modelagem" \
  --description "Blender, OpenFOAM, testes" \
  --due-date 2025-10-07

# sprint 3
gh milestone create "Sprint 3 - Web" \
  --description "FastAPI, React, API" \
  --due-date 2025-10-09

# sprint 5 (próxima)
gh milestone create "Sprint 5 - Correções" \
  --description "Bugs, validação, pipeline" \
  --due-date 2025-10-17
```

### associar issues a milestones

```bash
# associar issue #21 ao sprint 5
gh issue edit 21 --milestone "Sprint 5 - Correções"

# listar issues do milestone
gh issue list --milestone "Sprint 5 - Correções"

# fechar milestone
gh milestone close "Sprint 1 - Fundação"
```

### visualizar progresso

```bash
# ver todos milestones
gh milestone list

# ver milestone específico
gh milestone view "Sprint 5 - Correções"
```

---

## 📚 referências

- sprint-01-fundacao.md
- sprint-02-modelagem.md
- sprint-03-web-api.md
- sprint-04-documentacao.md
- docs/MAPEAMENTO_TCC_TASKS.md
- .kanbn_boards/tcc1/.kanbn/index.md

---

**última atualização:** 9 outubro 2025

