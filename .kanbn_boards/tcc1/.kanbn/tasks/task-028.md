---
name: validação com equação de ergun
tags:
  - validacao
  - ergun
  - cfd
created: 2025-10-09
assigned: 
sprint: mes 4 sem 3
atividades-tcc: a12
story-points: 13
---

# validação com equação de ergun

validar resultados do openfoam comparando com equação de ergun.

## fundamento teórico

### equação de ergun

```
Δp/L = 150 * (μ * U * (1-ε)²) / (dp² * ε³) + 1.75 * (ρ * U² * (1-ε)) / (dp * ε³)
```

onde:
- Δp/L = perda de carga por unidade de comprimento (Pa/m)
- μ = viscosidade dinâmica (Pa.s)
- U = velocidade superficial (m/s)
- ε = porosidade do leito
- dp = diâmetro da partícula (m)
- ρ = densidade do fluido (kg/m³)

## tarefas

### implementação ergun
- [ ] criar `scripts/validation/ergun_equation.py`
- [ ] função para calcular Δp/L teórico
- [ ] função para calcular porosidade
- [ ] função para calcular Re da partícula

### coleta de dados experimentais
- [ ] executar 10-15 simulações
- [ ] variar velocidade superficial (0.1-1.0 m/s)
- [ ] variar diâmetro de partícula (2-10 mm)
- [ ] fixar porosidade ~0.4
- [ ] registrar todos os parâmetros

### análise comparativa
- [ ] calcular Δp/L cfd para cada caso
- [ ] calcular Δp/L ergun para cada caso
- [ ] calcular erro relativo
- [ ] plotar curva cfd vs ergun
- [ ] análise estatística (r², rmse)

### geração de relatório
- [ ] tabela comparativa
- [ ] gráfico Δp/L vs U
- [ ] gráfico erro vs Re
- [ ] discussão de desvios
- [ ] conclusões

### casos de teste

| caso | U (m/s) | dp (mm) | ε | Re | Δp/L_ergun | Δp/L_cfd | erro (%) |
|------|---------|---------|---|----|-----------| ---------|----------|
| 1    | 0.1     | 5       | 0.4 | 50  | 2500      | ?        | ?        |
| 2    | 0.5     | 5       | 0.4 | 250 | 8000      | ?        | ?        |
| ...  | ...     | ...     | ... | ... | ...       | ...      | ...      |

## código de validação

```python
# scripts/validation/ergun_equation.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def ergun_pressure_drop(U, dp, epsilon, mu, rho):
    """calcula Δp/L pela equação de ergun"""
    term1 = 150 * (mu * U * (1 - epsilon)**2) / (dp**2 * epsilon**3)
    term2 = 1.75 * (rho * U**2 * (1 - epsilon)) / (dp * epsilon**3)
    return term1 + term2

def compare_with_cfd(results_csv):
    """compara resultados cfd com ergun"""
    df = pd.read_csv(results_csv)
    
    df['delta_p_L_ergun'] = df.apply(
        lambda row: ergun_pressure_drop(
            row['U'], row['dp'], row['epsilon'], 
            row['mu'], row['rho']
        ), axis=1
    )
    
    df['erro_rel'] = 100 * abs(
        df['delta_p_L_cfd'] - df['delta_p_L_ergun']
    ) / df['delta_p_L_ergun']
    
    return df
```

## critério de aceite
- erro Δp/L dentro de ±20% para Re < 500
- r² > 0.95 entre cfd e ergun
- tabela preliminar gerada
- curva comparativa plotada

## prioridade
alta - fundamental para validação

## estimativa
3-4 dias (13 story points)

## critérios de aceitação
- [ ] 10+ casos simulados
- [ ] Δp/L calculado (cfd e ergun)
- [ ] erro relativo < 20%
- [ ] gráficos comparativos
- [ ] tabela de validação
- [ ] análise estatística
- [ ] relatório completo
- [ ] documentação

