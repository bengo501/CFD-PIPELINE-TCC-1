---
name: completar pipeline openfoam com solver e paraview
tags:
  - openfoam
  - cfd
  - paraview
created: 2025-10-09
assigned: 
sprint: sprint 2
story-points: 8
---

# completar pipeline openfoam com solver e paraview

finalizar integração openfoam com execução de solver e visualização.

## tarefas

### execução do solver
- [ ] configurar solver (simpleFoam/pimpleFoam)
- [ ] executar blockMesh corretamente
- [ ] executar snappyHexMesh
- [ ] executar checkMesh (validação)
- [ ] rodar solver até convergência
- [ ] monitorar resíduos
- [ ] detectar divergência
- [ ] gerar logs detalhados

### geração arquivo .foam
- [ ] criar arquivo `caso.foam` vazio
- [ ] configurar para paraview
- [ ] documentar como abrir

### pós-processamento
- [ ] extrair campos (U, p, streamlines)
- [ ] gerar screenshots automáticos
- [ ] calcular métricas (perda de carga)
- [ ] exportar dados para análise

### integração
- [ ] atualizar `setup_openfoam_case.py`
- [ ] adicionar execução de solver
- [ ] adicionar geração de .foam
- [ ] adicionar pós-processamento básico
- [ ] testes end-to-end

## código afetado
- `scripts/openfoam_scripts/setup_openfoam_case.py`
  - adicionar `run_solver()`
  - adicionar `create_foam_file()`
  - adicionar `post_process()`

## exemplo de .foam file

```python
def create_foam_file(case_dir):
    """cria arquivo .foam para paraview"""
    foam_file = case_dir / "caso.foam"
    foam_file.touch()
    print(f"arquivo .foam criado: {foam_file}")
```

## comandos openfoam

```bash
# pipeline completo
blockMesh
snappyHexMesh -overwrite
checkMesh
simpleFoam
touch caso.foam
paraview caso.foam
```

## prioridade
alta - pipeline incompleto sem solver

## estimativa
2-3 dias (8 story points)

## critérios de aceitação
- [ ] solver executa sem erros
- [ ] convergência alcançada
- [ ] arquivo .foam gerado
- [ ] abre corretamente no paraview
- [ ] campos visualizáveis (U, p)
- [ ] métricas calculadas
- [ ] logs completos
- [ ] documentação atualizada

