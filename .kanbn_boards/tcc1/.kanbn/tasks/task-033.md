---
name: corrigir física blender (animação + colisões)
tags:
  - blender
  - physics
  - bugfix
  - critical
created: 2025-10-12
assigned: 
sprint: mes 4 sem 1-2
atividades-tcc: a5, a6
story-points: 5
---

# corrigir física blender (animação + colisões)

corrigir 3 problemas críticos na geração de modelos 3d

## problemas identificados
1. ❌ partículas ficavam suspensas (não caíam)
2. ❌ tampa superior bloqueava entrada de partículas
3. ❌ cilindro oco tinha colisão fantasma interna

## soluções implementadas
- [x] executar animação automaticamente (20s padrão)
- [x] função executar_simulacao_fisica()
- [x] tampa superior sem colisão (tem_colisao=False)
- [x] cilindro com mesh collision (não convex hull)
- [x] bake automático de física (fixar posições)
- [x] logs detalhados com progresso

## resultado
modelos 3d fisicamente corretos, partículas acomodadas naturalmente, prontos para cfd

