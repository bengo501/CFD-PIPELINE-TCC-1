---
name: criar setup openfoam automatizado
tags:
  - cfd
  - openfoam
  - simulacao
created: 2025-10-05
assigned: 
sprint: mes 2 sem 3-4
atividades-tcc: a5
story-points: 13
---

# criar setup openfoam automatizado

automatizar configuracao completa de casos openfoam (template base).

## tarefas
- [x] script setup_openfoam_case.py
- [x] exportar stl do blender
- [x] criar estrutura de caso (0/, constant/, system/)
- [x] gerar blockMeshDict
- [x] gerar snappyHexMeshDict
- [x] configurar controlDict, fvSchemes, fvSolution
- [x] definir condicoes iniciais (U, p)
- [x] transportProperties
- [x] script Allrun
- [x] executar simulacao (opcional)
- [x] arquivo para paraview

## resultado
- `scripts/openfoam_scripts/setup_openfoam_case.py` (890 linhas)
- `docs/OPENFOAM_WINDOWS_GUIA.md` (690 linhas)
- guia de simulacao manual
- casos openfoam automatizados

