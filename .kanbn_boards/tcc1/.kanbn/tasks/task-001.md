---
name: implementar dsl (.bed) com antlr
tags:
  - dsl
  - antlr
  - compilador
created: 2025-09-15
assigned: 
sprint: mes 1 sem 3-4 + mes 2 sem 1-2
atividades-tcc: a2, a3
story-points: 13
---

# implementar dsl (.bed) com antlr

criar linguagem de dominio especifico para descrever leitos empacotados.

## tarefas
- [x] criar gramatica Bed.g4
- [x] instalar antlr 4.13.1
- [x] gerar parser python
- [x] implementar compilador standalone
- [x] adicionar suporte a unidades (m, cm, kg, Pa)
- [x] validacao de sintaxe
- [x] gerar arquivo .bed.json normalizado

## resultado
- gramatica completa em `dsl/grammar/Bed.g4`
- compilador funcional em `dsl/compiler/bed_compiler_antlr_standalone.py`
- parser gerado em `dsl/generated/`

