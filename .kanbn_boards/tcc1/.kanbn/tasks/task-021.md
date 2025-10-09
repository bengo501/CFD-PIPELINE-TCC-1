---
name: corrigir física do blender - colisões e animação
tags:
  - blender
  - fisica
  - bug
created: 2025-10-09
assigned: 
sprint: mes 2 sem 2-3
atividades-tcc: a4
story-points: 8
---

# corrigir física do blender - colisões e animação

corrigir sistema de colisões e animação de empacotamento no blender.

## problemas identificados

1. **tampa superior com colisão**
   - tampa de cima não deve ter colisão
   - partículas devem cair livremente

2. **colisão do cilindro oco**
   - atualmente: colisão sólida
   - esperado: colisão oca (apenas paredes)
   - partículas devem cair dentro

3. **animação de empacotamento**
   - simular queda das partículas
   - aguardar repouso completo
   - salvar apenas após animação terminar

## tarefas
- [ ] remover colisão da tampa superior
- [ ] criar mesh collision para cilindro oco
- [ ] configurar rigid body constraints corretos
- [ ] implementar simulação de frames (100-250 frames)
- [ ] detectar quando partículas param de se mover
- [ ] salvar arquivo apenas após repouso
- [ ] adicionar progresso visual da animação
- [ ] testar com diferentes quantidades de partículas
- [ ] otimizar performance da simulação

## código afetado
- `scripts/blender_scripts/leito_extracao.py`
  - função `criar_cilindro_oco()`
  - função `criar_tampa()`
  - função `aplicar_fisica()`
  - função `configurar_simulacao_fisica()`
  - adicionar `executar_simulacao_empacotamento()`

## exemplo de implementação

```python
def executar_simulacao_empacotamento(frames=200):
    """executa simulação até partículas repousarem"""
    for frame in range(1, frames):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        
        # verificar se partículas pararam
        if frame % 10 == 0:
            movimento = verificar_movimento_particulas()
            if movimento < 0.001:  # threshold
                print(f"empacotamento completo no frame {frame}")
                break
```

## prioridade
alta - bug crítico que afeta qualidade dos modelos

## estimativa
2-3 dias (8 story points)

## critérios de aceitação
- [ ] tampa superior sem colisão
- [ ] cilindro com colisão apenas nas paredes
- [ ] partículas caem e repousam corretamente
- [ ] animação roda até estabilização
- [ ] arquivo salvo apenas após empacotamento
- [ ] progresso visível no terminal
- [ ] funciona com 10-1000 partículas

