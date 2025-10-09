# estrutura openfoam - documentação

## 📚 conteúdo

esta pasta contém documentação completa sobre a estrutura de casos openfoam utilizados no projeto.

### arquivos

- **`estrutura_caso_openfoam.md`** (1500+ linhas)
  - estrutura completa de diretórios
  - explicação detalhada de cada arquivo
  - parâmetros e valores típicos
  - exemplos comentados
  - troubleshooting

---

## 🎯 público-alvo

- estudantes aprendendo openfoam
- desenvolvedores integrando cfd
- revisores do tcc avaliando implementação

---

## 📖 tópicos cobertos

### estrutura de diretórios

```
caso_openfoam/
├── 0/                  # condições iniciais
├── constant/           # propriedades físicas
└── system/             # configuração numérica
```

### arquivos principais

1. **0/U** - campo de velocidade
2. **0/p** - campo de pressão
3. **constant/transportProperties** - fluido
4. **constant/turbulenceProperties** - turbulência
5. **system/controlDict** - controle geral
6. **system/fvSchemes** - esquemas numéricos
7. **system/fvSolution** - solvers
8. **system/blockMeshDict** - malha de fundo
9. **system/snappyHexMeshDict** - refinamento

### conceitos fundamentais

- condições de contorno (bc)
- dimensões físicas
- esquemas numéricos
- convergência
- qualidade de malha

---

## 💡 como usar

### consulta rápida

use o índice no início do documento para navegar diretamente às seções de interesse.

### estudo completo

leia sequencialmente para entendimento profundo da estrutura openfoam.

### referência

mantenha aberto durante desenvolvimento para consultar parâmetros.

---

## 🔗 documentação relacionada

- `../scripts_python/` - scripts de geração automática
- `../referencial_teorico/` - fundamentação teórica
- `../referencias.bib` - citações

---

**última atualização**: 9 outubro 2025

