---
name: integrar blender headless com dsl
tags:
  - blender
  - 3d
  - integracao
created: 2025-09-22
assigned: 
sprint: mes 2 sem 2-3
atividades-tcc: a4
story-points: 13
---

# integrar blender headless com dsl

integrar blender para gerar modelos 3d a partir de arquivos .bed.json.

## tarefas
- [x] script leito_extracao.py com leitura de json
- [x] criar cilindro oco
- [x] criar tampas (planas/hemisfericas)
- [x] gerar particulas esfericas
- [x] aplicar fisica rigid body (passive/active)
- [x] configurar simulacao fisica (gravidade, substeps)
- [x] salvar arquivo .blend
- [x] exportar stl
- [x] executor headless
- [x] integrar com bed_wizard

## resultado
- `scripts/blender_scripts/leito_extracao.py` (500+ linhas)
- `scripts/standalone_scripts/executar_leito_headless.py`
- modelos 3d funcionais exportados como .blend e .stl

