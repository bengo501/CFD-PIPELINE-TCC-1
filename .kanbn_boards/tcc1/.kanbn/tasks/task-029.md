---
name: estudo de independência de malha (gci)
tags:
  - validacao
  - malha
  - gci
created: 2025-10-09
assigned: 
sprint: mes 4 sem 3 + mes 6 sem 2-4
atividades-tcc: a12, a19
story-points: 8
---

# estudo de independência de malha (gci)

verificar independência de resultados em relação ao refinamento de malha.

## fundamento teórico

### grid convergence index (gci)

```
GCI = Fs * |ε| / (r^p - 1)
```

onde:
- Fs = fator de segurança (1.25 para 3 malhas)
- ε = erro relativo entre malhas
- r = razão de refinamento
- p = ordem de convergência observada

## tarefas

### geração de malhas
- [ ] malha grosseira (baseline)
- [ ] malha média (2x refinamento)
- [ ] malha fina (4x refinamento)
- [ ] documentar células de cada nível
- [ ] manter geometria idêntica

### execução de casos
- [ ] simular com malha 1 (grosseira)
- [ ] simular com malha 2 (média)
- [ ] simular com malha 3 (fina)
- [ ] mesmos parâmetros físicos
- [ ] mesma configuração de solver

### variáveis monitoradas
- [ ] Δp (perda de carga total)
- [ ] Δp/L (perda normalizada)
- [ ] velocidade máxima
- [ ] velocidade média
- [ ] tempo de simulação

### cálculo gci
- [ ] criar `scripts/validation/gci_study.py`
- [ ] calcular ε12, ε23 (erros relativos)
- [ ] calcular p (ordem de convergência)
- [ ] calcular GCI_fine, GCI_coarse
- [ ] verificar convergência assintótica

### análise de resultados
- [ ] tabela com 3 níveis de malha
- [ ] gráfico convergência
- [ ] determinar malha adequada
- [ ] balanço custo x precisão

## casos de malha

| nível | células | Δp (Pa) | tempo (s) | GCI (%) |
|-------|---------|---------|-----------|---------|
| 1     | 50k     | ?       | ?         | ?       |
| 2     | 200k    | ?       | ?         | ?       |
| 3     | 800k    | ?       | ?         | ?       |

## código gci

```python
# scripts/validation/gci_study.py
import numpy as np

def calculate_gci(phi1, phi2, phi3, r=2):
    """
    calcula gci entre 3 malhas
    phi1, phi2, phi3 = variável de interesse (ex: Δp)
    r = razão de refinamento
    """
    # erros relativos
    epsilon_32 = (phi3 - phi2) / phi2
    epsilon_21 = (phi2 - phi1) / phi1
    
    # ordem de convergência
    s = np.sign(epsilon_21 / epsilon_32)
    p = abs(np.log(abs(epsilon_21 / epsilon_32)) / np.log(r))
    
    # gci
    Fs = 1.25  # 3 malhas
    GCI_fine = Fs * abs(epsilon_32) / (r**p - 1)
    GCI_coarse = Fs * abs(epsilon_21) / (r**p - 1)
    
    return {
        'p': p,
        'GCI_fine': GCI_fine * 100,  # em %
        'GCI_coarse': GCI_coarse * 100,
        'converged': (r**p * GCI_fine) / GCI_coarse < 1.1
    }

# exemplo de uso
delta_p_1 = 250.5  # malha grosseira
delta_p_2 = 248.3  # malha média
delta_p_3 = 247.8  # malha fina

result = calculate_gci(delta_p_1, delta_p_2, delta_p_3, r=2)
print(f"ordem de convergência: {result['p']:.2f}")
print(f"GCI malha fina: {result['GCI_fine']:.2f}%")
print(f"GCI malha grosseira: {result['GCI_coarse']:.2f}%")
print(f"convergência assintótica: {result['converged']}")
```

## critério de aceite
- GCI < 3% na malha mais fina
- convergência monotônica
- ordem p entre 1 e 3
- convergência assintótica verificada

## prioridade
alta - fundamental para confiabilidade

## estimativa
2-3 dias (8 story points)

## critérios de aceitação
- [ ] 3 níveis de malha testados
- [ ] índice GCI calculado
- [ ] GCI < 3% na malha fina
- [ ] ordem de convergência determinada
- [ ] tabela de convergência
- [ ] malha adequada selecionada
- [ ] documentação completa

