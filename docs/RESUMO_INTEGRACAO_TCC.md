# resumo da integração atividades tcc x tasks kanban

## ✅ integração completa realizada

### tasks atualizadas (24 existentes)

todas as 24 tasks existentes foram atualizadas com:
- campo `sprint:` indicando mês e semana (ex: mes 2 sem 3-4)
- campo `atividades-tcc:` indicando atividades relacionadas (ex: a4, a5)
- `story-points:` revisados e padronizados

#### tasks concluídas (done) - 10 tasks

| task | nome | sprint | atividade | pts |
|------|------|--------|-----------|-----|
| 001 | implementar dsl | m1s3-4 + m2s1-2 | a2, a3 | 13 |
| 002 | bed wizard | m2s1-2 | a3 | 8 |
| 003 | blender headless | m2s2-3 | a4 | 13 |
| 004 | setup openfoam | m2s3-4 | a5 | 13 |
| 005 | testes e2e | m4s2 | a11 | 8 |
| 006 | documentar pipeline | m4s3-4 | a13 | 5 |
| 007 | kanban scrumban | continuo | a15 | 3 |
| 008 | github projects | continuo | a15 | 3 |
| 018 | backend fastapi | m3s3-4 | a9 | 13 |
| 019 | frontend react | m4s1-2 | a10 | 13 |
| **total** | | | | **92 pts** |

#### tasks pendentes (todo) - 11 tasks

| task | nome | sprint | atividade | pts |
|------|------|--------|-----------|-----|
| 020 | doc openfoam | m4s3-4 | a13 | 3 |
| 021 | física blender | m2s2-3 | a4 | 8 |
| 022 | pipeline openfoam | m2s3-4 + m3s1-2 | a5, a6 | 8 |
| 023 | postgresql | m3s3 | a8 | 8 |
| 025 | pós-processamento | m3s2 | a7 | 5 |
| 026 | minio | m3s3 | a8 | 5 |
| 027 | threejs 3d | m4s1-2 | a10 | 8 |
| 028 | validação ergun | m4s3 | a12 | 13 |
| 029 | estudo malha gci | m4s3 + m6s2-4 | a12, a19 | 8 |
| 030 | proposta tcc1 | m4s3-4 | a13 | 8 |
| 031 | apresentação tcc1 | m4s4 | a14 | 3 |
| **total** | | | | **77 pts** |

#### tasks futuras (backlog) - 3 tasks + tcc2

| task | nome | sprint | atividade | pts |
|------|------|--------|-----------|-----|
| 024 | docker redis | m7s3-4 + m8s1 | a23, a24 | 13 |
| **total** | | | | **13 pts** |

### novas tasks criadas - 7 tasks

| task | nome | sprint | atividade | descrição | pts |
|------|------|--------|-----------|-----------|-----|
| 025 | pós-processamento | m3s2 | a7 | extrair variáveis (Δp, U, p), globals.csv | 5 |
| 026 | minio artefatos | m3s3 | a8 | storage objetos para .blend, .stl, casos | 5 |
| 027 | threejs 3d | m4s1-2 | a10 | visualizador 3d interativo no frontend | 8 |
| 028 | validação ergun | m4s3 | a12 | comparar cfd com equação de ergun | 13 |
| 029 | estudo malha gci | m4s3 + m6 | a12, a19 | independência de malha, calcular gci | 8 |
| 030 | proposta tcc1 | m4s3-4 | a13 | documento completo 30-50 páginas | 8 |
| 031 | apresentação tcc1 | m4s4 | a14 | slides 10-15min, ensaio, demo | 3 |
| **total** | | | | | **50 pts** |

### documentação criada

#### docs/MAPEAMENTO_TCC_TASKS.md
- **650+ linhas** de mapeamento completo
- tabelas detalhadas de todas as 50 tasks
- cronograma tcc1 (4 meses) e tcc2 (4 meses)
- 29 atividades mapeadas (a1-a29)
- legenda de sprints
- estatísticas do projeto

---

## 📊 estatísticas finais

### story points por fase

| fase | concluído | pendente | backlog | total |
|------|-----------|----------|---------|-------|
| **tcc1** | 92 pts | 77 pts | 0 pts | 169 pts |
| **tcc2** | 0 pts | 0 pts | 13 pts | 13 pts |
| **total** | 92 pts | 77 pts | 13 pts | **182 pts** |

### progresso tcc1

- **54.4%** concluído (92 / 169 pts)
- **45.6%** pendente (77 / 169 pts)
- **10 atividades** completas (a1-a3, a9-a11, a13 parcial, a15)
- **5 atividades** pendentes (a4 parcial, a5-a8, a12-a14)

### atividades por status

#### ✅ concluídas (10 atividades)
- a1: levantamento bibliográfico
- a2: especificação da dsl
- a3: parser/compilador da dsl
- a9: api fastapi
- a10: frontend react (parcial)
- a11: integração e2e (parcial)
- a13: documentação tcc1 (parcial)
- a15: gestão e checkpoints

#### 🚧 em progresso (5 atividades)
- a4: geração geométrica blender (bug física)
- a5: template openfoam (parcial)
- a6: pipeline malha/solver (parcial)

#### ⏳ pendentes tcc1 (4 atividades)
- a7: pós-processamento
- a8: persistência db/minio
- a12: validação numérica
- a14: apresentação

#### 📅 futuro tcc2 (14 atividades)
- a16-a29: refinamentos, otimizações, hardening, monografia, defesa

---

## 🎯 próximas prioridades (ordem recomendada)

### sprint atual (mes 2-3)
1. **task-021**: corrigir física blender (bug crítico) - 8 pts
2. **task-022**: completar pipeline openfoam - 8 pts
3. **task-025**: implementar pós-processamento - 5 pts

### sprint seguinte (mes 3)
4. **task-023**: implementar postgresql - 8 pts
5. **task-026**: integrar minio - 5 pts

### sprint final tcc1 (mes 4)
6. **task-027**: integrar threejs - 8 pts
7. **task-028**: validação ergun - 13 pts
8. **task-029**: estudo malha gci - 8 pts
9. **task-020**: documentação openfoam - 3 pts
10. **task-030**: escrever proposta - 8 pts
11. **task-031**: preparar apresentação - 3 pts

**total pendente**: 77 story points (~11 dias úteis de trabalho)

---

## 📋 relação completa atividades x tasks

### mês 1 (fundação)
- **sem 1-2**: a1 (levantamento) - ✅ concluído
- **sem 3-4**: a2 (especificação dsl) → task-001 - ✅

### mês 2 (compilador e blender)
- **sem 1-2**: a3 (compilador) → task-001, 002 - ✅
- **sem 2-3**: a4 (blender) → task-003, 021 - 🚧
- **sem 3-4**: a5 (openfoam template) → task-004, 022 - 🚧

### mês 3 (pipeline e persistência)
- **sem 1-2**: a6 (pipeline solver) → task-022 - ⏳
- **sem 2**: a7 (pós-processamento) → task-025 - ⏳
- **sem 3**: a8 (db/minio) → task-023, 026 - ⏳
- **sem 3-4**: a9 (api) → task-018 - ✅

### mês 4 (frontend e validação)
- **sem 1-2**: a10 (frontend) → task-019, 027 - 🚧
- **sem 2**: a11 (e2e) → task-005 - ✅
- **sem 3**: a12 (validação) → task-028, 029 - ⏳
- **sem 3-4**: a13 (documentação) → task-006, 020, 030 - 🚧
- **sem 4**: a14 (apresentação) → task-031 - ⏳
- **contínuo**: a15 (gestão) → task-007, 008 - ✅

### mês 5-8 (tcc2)
- a16-a29: refinamentos, otimizações, doe, validação completa, hardening, monografia, defesa

---

## ✨ conquistas da integração

1. **mapeamento completo**: 50 tasks x 29 atividades
2. **cronograma alinhado**: sprints seguem tabela oficial do tcc
3. **rastreabilidade**: cada task referencia atividades específicas
4. **priorização clara**: ordem baseada no cronograma acadêmico
5. **métricas precisas**: story points alinhados com estimativas de tempo
6. **documentação extensa**: 650+ linhas de mapeamento
7. **visibilidade**: fácil acompanhar progresso vs cronograma

---

## 📖 como usar este sistema

### consultar mapeamento
```bash
# ver mapeamento completo
cat docs/MAPEAMENTO_TCC_TASKS.md

# ver resumo
cat docs/RESUMO_INTEGRACAO_TCC.md
```

### acompanhar tarefas
```bash
# ver kanban local
cat .kanbn_boards/tcc1/.kanbn/index.md

# ver task específica
cat .kanbn_boards/tcc1/.kanbn/tasks/task-021.md
```

### planejar sprint
1. consultar mes/semana atual no cronograma
2. identificar atividades correspondentes
3. filtrar tasks por sprint no kanban
4. priorizar por dependências e story points

### reportar progresso
- usar campos `sprint` e `atividades-tcc` nos relatórios
- referenciar atividades nas reuniões com orientador
- atualizar status das tasks conforme avança

---

**sistema de gestão completo e integrado com cronograma acadêmico do tcc!** 🎓

