# mapeamento atividades tcc x tasks kanban

## cronograma tcc1 (meses 1-4)

### mês 1 - fundação dsl e geometria

#### semana 1-2: a1. levantamento bibliográfico
- **status**: concluído
- **tasks relacionadas**: não há task específica (atividade anterior ao repo)

#### semana 3-4: a2. especificação da dsl
- **status**: concluído
- **tasks relacionadas**:
  - task-001: implementar dsl (.bed) com antlr
  - sprint: mes 1 sem 3-4
  - story points: 13

### mês 2 - compilador e blender

#### semana 1-2: a3. parser/compilador da dsl
- **status**: concluído
- **tasks relacionadas**:
  - task-001: implementar dsl (.bed) com antlr (continuação)
  - task-002: criar bed wizard interativo
  - sprint: mes 2 sem 1-2
  - story points: 13 + 8 = 21

#### semana 2-3: a4. geração geométrica (blender)
- **status**: em progresso (com bugs)
- **tasks relacionadas**:
  - task-003: integrar blender headless
  - task-021: corrigir física do blender
  - sprint: mes 2 sem 2-3
  - story points: 13 + 8 = 21

#### semana 3-4: a5. template openfoam (caso base)
- **status**: parcialmente concluído
- **tasks relacionadas**:
  - task-004: criar setup openfoam automatizado
  - task-022: pipeline openfoam completo
  - sprint: mes 2 sem 3-4
  - story points: 13 + 8 = 21

### mês 3 - pipeline e persistência

#### semana 1-2: a6. pipeline malha/solver
- **status**: parcialmente concluído
- **tasks relacionadas**:
  - task-022: pipeline openfoam completo
  - sprint: mes 3 sem 1-2
  - story points: 8

#### semana 2: a7. pós-processamento (variáveis)
- **status**: não iniciado
- **tasks relacionadas**:
  - task-025: implementar pós-processamento cfd (nova)
  - sprint: mes 3 sem 2
  - story points: 5

#### semana 3: a8. ingestão e persistência (db/minio)
- **status**: não iniciado
- **tasks relacionadas**:
  - task-023: banco de dados postgresql
  - task-026: integrar minio para artefatos (nova)
  - sprint: mes 3 sem 3
  - story points: 8 + 5 = 13

#### semana 3-4: a9. api (fastapi)
- **status**: concluído (básico)
- **tasks relacionadas**:
  - task-018: implementar backend fastapi
  - sprint: mes 3 sem 3-4
  - story points: 13

### mês 4 - frontend e integração

#### semana 1-2: a10. frontend (react/plotly/three.js)
- **status**: concluído (básico)
- **tasks relacionadas**:
  - task-019: implementar frontend react
  - task-027: integrar three.js para visualização 3d (nova)
  - sprint: mes 4 sem 1-2
  - story points: 13 + 8 = 21

#### semana 2: a11. integração ponta a ponta (e2e)
- **status**: parcialmente concluído
- **tasks relacionadas**:
  - task-005: criar testes e2e automatizados
  - sprint: mes 4 sem 2
  - story points: 8

#### semana 3: a12. validação inicial (numérica/física)
- **status**: não iniciado
- **tasks relacionadas**:
  - task-028: validação com equação de ergun (nova)
  - task-029: estudo de independência de malha (nova)
  - sprint: mes 4 sem 3
  - story points: 13 + 8 = 21

#### semana 3-4: a13. documentação tcc1
- **status**: em progresso
- **tasks relacionadas**:
  - task-006: documentar pipeline completo
  - task-020: documentação openfoam
  - task-030: escrever proposta tcc1 (nova)
  - sprint: mes 4 sem 3-4
  - story points: 5 + 3 + 8 = 16

#### semana 4: a14. apresentação (slides/ensaio)
- **status**: não iniciado
- **tasks relacionadas**:
  - task-031: preparar apresentação tcc1 (nova)
  - sprint: mes 4 sem 4
  - story points: 3

#### contínuo: a15. gestão e checkpoints
- **status**: em progresso
- **tasks relacionadas**:
  - task-007: configurar kanban/scrumban
  - task-008: integrar github projects
  - sprint: continuo
  - story points: 3 + 3 = 6

---

## cronograma tcc2 (meses 5-8)

### mês 5 - refinamento e otimização

#### semana 1-2: a16. refino da dsl e do compilador
- **status**: não iniciado
- **tasks relacionadas**:
  - task-032: suporte a partículas polidispersas (nova)
  - task-033: adicionar presets de leito (nova)
  - sprint: mes 5 sem 1-2
  - story points: 8 + 5 = 13

#### semana 2-3: a17. otimizações de modelagem (blender)
- **status**: não iniciado
- **tasks relacionadas**:
  - task-034: validação automática de manifold (nova)
  - task-035: otimizar tempo de empacotamento (nova)
  - sprint: mes 5 sem 2-3
  - story points: 5 + 8 = 13

#### semana 3-4 + mês 6 sem 1-4: a18. automação de estudos e doe
- **status**: não iniciado
- **tasks relacionadas**:
  - task-036: implementar execução em lote (nova)
  - task-037: planejamento de experimentos doe (nova)
  - sprint: mes 5 sem 3-4 + mes 6 sem 1-4
  - story points: 13 + 13 = 26

### mês 6 - validação e comparação

#### semana 2-4: a19. gci completo e validação δp/l
- **status**: não iniciado
- **tasks relacionadas**:
  - task-029: estudo de independência de malha (continuação)
  - task-038: implementar cálculo gci (nova)
  - sprint: mes 6 sem 2-4
  - story points: 13

#### semana 1-2: a20. comparador no dashboard
- **status**: não iniciado
- **tasks relacionadas**:
  - task-039: tela de comparação no frontend (nova)
  - sprint: mes 6 sem 1-2
  - story points: 8

#### semana 2-3: a21. relatórios automáticos
- **status**: não iniciado
- **tasks relacionadas**:
  - task-040: gerador de relatórios pdf (nova)
  - sprint: mes 6 sem 2-3
  - story points: 8

### mês 7 - hardening e performance

#### semana 3-4: a22. hardening do backend
- **status**: não iniciado
- **tasks relacionadas**:
  - task-041: implementar rbac e autenticação (nova)
  - task-042: rate limiting e logs estruturados (nova)
  - sprint: mes 7 sem 3-4
  - story points: 8 + 5 = 13

#### semana 3-4: a23. performance e execução avançada
- **status**: não iniciado
- **tasks relacionadas**:
  - task-024: docker e orquestração (inclui filas)
  - task-043: paralelização de jobs (nova)
  - sprint: mes 7 sem 3-4
  - story points: 13 + 8 = 21

### mês 8 - finalização e entrega

#### semana 1: a24. pacote de replicação
- **status**: parcialmente concluído
- **tasks relacionadas**:
  - task-024: docker e orquestração
  - task-044: dataset exemplo e scripts (nova)
  - sprint: mes 8 sem 1
  - story points: 5

#### semana 1-3: a25. monografia tcc2
- **status**: não iniciado
- **tasks relacionadas**:
  - task-045: escrever monografia tcc2 (nova)
  - sprint: mes 8 sem 1-3
  - story points: 21

#### semana 3-4: a26. defesa e demonstração
- **status**: não iniciado
- **tasks relacionadas**:
  - task-046: preparar defesa tcc2 (nova)
  - task-047: criar vídeo demonstração (nova)
  - sprint: mes 8 sem 3-4
  - story points: 5 + 3 = 8

#### semana 2-4: a27. publicação e depósito
- **status**: não iniciado
- **tasks relacionadas**:
  - task-048: publicar no zenodo com doi (nova)
  - sprint: mes 8 sem 2-4
  - story points: 3

#### semana 3-4: a28. auditoria de reprodutibilidade
- **status**: não iniciado
- **tasks relacionadas**:
  - task-049: executar auditoria externa (nova)
  - sprint: mes 8 sem 3-4
  - story points: 5

#### contínuo: a29. gestão e checkpoints tcc2
- **status**: não iniciado
- **tasks relacionadas**:
  - task-050: gestão semanal tcc2 (nova)
  - sprint: continuo
  - story points: 5

---

## resumo estatístico

### tcc1 (atual)
- **atividades**: 15 (a1-a15)
- **tasks concluídas**: 10
- **tasks em progresso**: 5
- **tasks planejadas**: 6 novas
- **total story points tcc1**: ~180 pontos

### tcc2 (futuro)
- **atividades**: 14 (a16-a29)
- **tasks planejadas**: 25 novas
- **total story points tcc2**: ~220 pontos

### status geral do projeto
- ✅ **concluído**: a1, a2, a3, a9, a10 (parcial)
- 🚧 **em progresso**: a4, a5, a6, a11, a13, a15
- ⏳ **pendente tcc1**: a7, a8, a12, a14
- ⏳ **pendente tcc2**: a16-a29

---

## mapeamento task → atividade

| task | nome | atividade(s) | sprint | pts |
|------|------|--------------|--------|-----|
| task-001 | implementar dsl | a2, a3 | m1s3-4, m2s1-2 | 13 |
| task-002 | bed wizard | a3 | m2s1-2 | 8 |
| task-003 | blender headless | a4 | m2s2-3 | 13 |
| task-004 | setup openfoam | a5 | m2s3-4 | 13 |
| task-005 | testes e2e | a11 | m4s2 | 8 |
| task-006 | documentar pipeline | a13 | m4s3-4 | 5 |
| task-007 | kanban/scrumban | a15 | continuo | 3 |
| task-008 | github projects | a15 | continuo | 3 |
| task-018 | backend fastapi | a9 | m3s3-4 | 13 |
| task-019 | frontend react | a10 | m4s1-2 | 13 |
| task-020 | doc openfoam | a13 | m4s3-4 | 3 |
| task-021 | física blender | a4 | m2s2-3 | 8 |
| task-022 | pipeline openfoam | a5, a6 | m2s3-4, m3s1-2 | 8 |
| task-023 | postgresql | a8 | m3s3 | 8 |
| task-024 | docker/redis | a23, a24 | m7s3-4, m8s1 | 13 |
| task-025 | pós-processamento | a7 | m3s2 | 5 |
| task-026 | minio artefatos | a8 | m3s3 | 5 |
| task-027 | three.js 3d | a10 | m4s1-2 | 8 |
| task-028 | validação ergun | a12 | m4s3 | 13 |
| task-029 | estudo malha | a12, a19 | m4s3, m6s2-4 | 8 |
| task-030 | proposta tcc1 | a13 | m4s3-4 | 8 |
| task-031 | apresentação tcc1 | a14 | m4s4 | 3 |
| task-032 | polidispersão | a16 | m5s1-2 | 8 |
| task-033 | presets leito | a16 | m5s1-2 | 5 |
| task-034 | validação manifold | a17 | m5s2-3 | 5 |
| task-035 | otimizar empacotamento | a17 | m5s2-3 | 8 |
| task-036 | execução lote | a18 | m5s3-4 + m6s1-4 | 13 |
| task-037 | doe planejamento | a18 | m5s3-4 + m6s1-4 | 13 |
| task-038 | cálculo gci | a19 | m6s2-4 | 13 |
| task-039 | comparador dashboard | a20 | m6s1-2 | 8 |
| task-040 | relatórios pdf | a21 | m6s2-3 | 8 |
| task-041 | rbac autenticação | a22 | m7s3-4 | 8 |
| task-042 | rate limiting logs | a22 | m7s3-4 | 5 |
| task-043 | paralelização jobs | a23 | m7s3-4 | 8 |
| task-044 | dataset exemplo | a24 | m8s1 | 5 |
| task-045 | monografia tcc2 | a25 | m8s1-3 | 21 |
| task-046 | defesa tcc2 | a26 | m8s3-4 | 5 |
| task-047 | vídeo demo | a26 | m8s3-4 | 3 |
| task-048 | publicar zenodo | a27 | m8s2-4 | 3 |
| task-049 | auditoria externa | a28 | m8s3-4 | 5 |
| task-050 | gestão tcc2 | a29 | continuo | 5 |

---

## legenda sprints

- **m1s1-2**: mês 1, semanas 1-2
- **m2s3-4**: mês 2, semanas 3-4
- **continuo**: atividade contínua durante todo o período

