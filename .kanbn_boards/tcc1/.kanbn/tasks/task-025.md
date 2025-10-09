---
name: implementar pós-processamento cfd
tags:
  - openfoam
  - pos-processamento
  - metricas
created: 2025-10-09
assigned: 
sprint: mes 3 sem 2
atividades-tcc: a7
story-points: 5
---

# implementar pós-processamento cfd

extrair e processar variáveis relevantes das simulações openfoam.

## tarefas

### extração de dados
- [ ] extrair campo de velocidade (U)
- [ ] extrair campo de pressão (p)
- [ ] calcular perda de carga (Δp)
- [ ] calcular Δp/L normalizado
- [ ] calcular velocidade média
- [ ] calcular número de reynolds (Re)
- [ ] extrair número de células da malha
- [ ] registrar tempo de simulação

### geração de globals.csv
- [ ] criar `scripts/openfoam_scripts/post_process.py`
- [ ] formato padronizado de saída
- [ ] colunas fixas: timestamp, bed_id, Re, Δp, Δp/L, cells, time, status
- [ ] validação de dados
- [ ] tratamento de erros

### integração
- [ ] integrar com setup_openfoam_case.py
- [ ] executar automaticamente após solver
- [ ] salvar resultados em output/results/
- [ ] logs detalhados

## estrutura globals.csv

```csv
timestamp,bed_id,diameter,height,particles,Re,delta_p,delta_p_L,cells,sim_time,status
2025-10-09T10:30:00,leito001,0.05,0.1,100,150.5,250.3,2503.0,45000,120.5,converged
```

## código afetado
- criar `scripts/openfoam_scripts/post_process.py`
- atualizar `scripts/openfoam_scripts/setup_openfoam_case.py`
  - adicionar `post_process_results()`

## prioridade
média - necessário para validação

## estimativa
1-2 dias (5 story points)

## critérios de aceitação
- [ ] extrai U, p e streamlines
- [ ] calcula Δp, Δp/L, Re corretamente
- [ ] gera globals.csv padronizado
- [ ] valores plausíveis
- [ ] integrado ao pipeline
- [ ] documentação completa

