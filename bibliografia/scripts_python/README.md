# scripts python - documentação

## 📚 conteúdo

esta pasta contém documentação completa sobre os scripts python utilizados para automação no projeto.

### arquivos

1. **`scripts_blender_explicacao.md`** (1200+ linhas)
   - api do blender (bpy)
   - modelagem procedural
   - física rigid body
   - exportação stl
   - execução headless

2. **`scripts_openfoam_explicacao.md`** (1300+ linhas)
   - classe OpenFOAMCaseGenerator
   - geração automática de casos
   - integração com dsl
   - configuração de simulações
   - workflow completo

---

## 🎯 scripts documentados

### blender (leito_extracao.py)

**funções principais**:
- `limpar_cena()` - reset do ambiente
- `criar_cilindro_oco()` - geometria do leito
- `criar_tampa()` - tampas superior/inferior
- `criar_particulas()` - esferas aleatórias
- `aplicar_fisica()` - rigid body physics
- `configurar_simulacao_fisica()` - parâmetros globais
- `ler_parametros_json()` - integração com dsl
- `main_com_parametros()` - ponto de entrada

**conceitos cobertos**:
- operações booleanas
- modificadores procedurais
- física de empacotamento
- distribuição espacial
- cálculo de massa
- headless execution

### openfoam (setup_openfoam_case.py)

**classe OpenFOAMCaseGenerator**:
- `__init__()` - inicialização
- `export_stl_from_blender()` - exportação
- `create_case_structure()` - diretórios
- `copy_stl_to_case()` - geometria
- `create_mesh_dict()` - malha
- `create_control_dicts()` - configuração
- `create_initial_conditions()` - condições
- `create_run_script()` - automação
- `run()` - pipeline completo

**conceitos cobertos**:
- estrutura de casos openfoam
- geração de dicionários
- cálculo de domínio
- refinamento de malha
- condições de contorno
- integração python-openfoam

---

## 💡 como usar

### para desenvolvedores

leia para entender:
- arquitetura dos scripts
- decisões de design
- parâmetros configuráveis
- pontos de extensão

### para usuários

use como referência para:
- troubleshooting
- ajuste de parâmetros
- compreensão do workflow
- modificações customizadas

### para tcc

utilize para:
- capítulo de implementação
- documentação de código
- justificativa técnica
- exemplos de uso

---

## 📊 estatísticas

| script | linhas | funções | classes | comentários |
|--------|--------|---------|---------|-------------|
| leito_extracao.py | 500+ | 8 | 0 | 150+ |
| setup_openfoam_case.py | 890+ | 12 | 1 | 200+ |

**cobertura de documentação**: 100%

---

## 🔗 integração

### fluxo completo

```
.bed → compilador → .bed.json
                        ↓
                   leito_extracao.py (blender)
                        ↓
                   .blend + .stl
                        ↓
                   setup_openfoam_case.py
                        ↓
                   caso openfoam
                        ↓
                   simulação cfd
```

### dependências

- **blender**: api bpy
- **openfoam**: comandos cli
- **python**: 3.8+
- **libs**: json, subprocess, pathlib

---

## 📚 referências

### documentação técnica

- blender foundation (2025). blender python api
- openfoam foundation (2025). user guide
- conlan (2017). the blender python api
- ferziger (2002). computational methods for fluid dynamics

### documentação relacionada

- `../estrutura_openfoam/` - estrutura de casos
- `../referencial_teorico/` - fundamentação
- `../../scripts/` - código-fonte

---

**última atualização**: 9 outubro 2025

