---
name: testes end-to-end (e2e)
tags:
  - testes
  - e2e
  - validacao
created: 2025-10-07
---

# testes end-to-end (e2e)

suite completa de testes automatizados do pipeline.

## tarefas
- [x] test_full_pipeline.py (900 linhas)
- [x] teste 1: geracao basica
- [x] teste 2: geracao 3d completa
- [x] teste 3: gerar e abrir blender
- [x] teste 4: configuracao openfoam
- [x] teste 5: simulacao completa rapida
- [x] teste 6: estudo parametrico
- [x] estrutura organizada (outputs/results/logs)
- [x] relatorios json
- [x] logs detalhados

## resultado
- `tests/e2e/test_full_pipeline.py`
- `tests/e2e/README.md` (400 linhas)
- 6 testes automatizados
- testa todo o pipeline (dsl → 3d → cfd)

