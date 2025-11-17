# scripts openfoam

## visão geral

scripts python para integrar o blender com o openfoam, criando e executando simulações cfd automaticamente.

## arquivo principal

### `setup_openfoam_case.py`

script completo que:

carrega parâmetros do `arquivo.bed.json`

exporta geometria do blender para stl

cria caso openfoam completo

gera malha com snappyhexmesh

configura condições de contorno

executa simulação (opcional)prepara visualização no paraview

## como usar

### uso básico

```bash
cd scripts/openfoam_scripts

# criar caso openfoam (sem executar)
python setup_openfoam_case.py \
    ../../dsl/leito_blender.bed.json \
    ../../output/models/leito_blender.blend

# criar e executar simulação
python setup_openfoam_case.py \
    ../../dsl/leito_blender.bed.json \
    ../../output/models/leito_blender.blend \
    --run
```

### especificar diretório de saída

```bash
python setup_openfoam_case.py \
    ../../dsl/leito_blender.bed.json \
    ../../output/models/leito_blender.blend \
    --output-dir ../../output/cfd/meu_caso
```

## workflow completo

### 1. gerar modelo no blender

```bash
cd dsl
python bed_wizard.py
# escolher opção 3 ou 4 (modo blender)
```

### 2. criar caso openfoam

```bash
cd ../scripts/openfoam_scripts
python setup_openfoam_case.py \
    ../../dsl/leito_blender.bed.json \
    ../../output/models/leito_blender.blend
```

### 3. executar simulação (no wsl/ubuntu)

```bash
# copiar caso para wsl
cp -r ../../output/cfd/leito_blender ~/openfoam/

# executar no wsl
cd ~/openfoam/leito_blender
./Allrun
```

### 4. visualizar resultados

```bash
# criar arquivo .foam
touch caso.foam

# abrir no paraview (windows)
explorer.exe .
# duplo clique em caso.foam
```

## estrutura do caso gerado

```
output/cfd/leito_blender/
├── 0/                          # condições iniciais
│   ├── U                       # velocidade
│   └── p                       # pressão
│
├── constant/                   # propriedades
│   ├── triSurface/
│   │   └── leito.stl          # geometria
│   ├── transportProperties    # viscosidade
│   └── turbulenceProperties   # modelo turbulência
│
├── system/                     # controle
│   ├── controlDict           # tempo, iterações
│   ├── blockMeshDict         # malha de fundo
│   ├── snappyHexMeshDict     # malha refinada
│   ├── fvSchemes             # esquemas numéricos
│   └── fvSolution            # solver settings
│
├── Allrun                      # script executável
├── log.blockMesh              # logs (após executar)
├── log.snappyHexMesh
├── log.simpleFoam
└── caso.foam                   # para paraview
```

## parâmetros cfd suportados

o script lê os seguintes parâmetros do `arquivo.bed.json`:

### seção `cfd` (opcional)

```json
{
  "cfd": {
    "regime": "laminar",
    "inlet_velocity": 0.1,
    "fluid_density": 1.225,
    "fluid_viscosity": 1.5e-05,
    "max_iterations": 1000,
    "convergence_criteria": 1e-06
  }
}
```

### valores padrão

se a seção `cfd` não existir, usa:

- **inlet_velocity**: 0.1 m/s
- **fluid_viscosity**: 1.5e-5 m²/s (ar)
- **max_iterations**: 1000

## saída do script

### exemplo de execução

```
============================================================
  configuração de caso openfoam
============================================================

[1/8] carregando parametros de leito_blender.bed.json
  ✓ parametros carregados
    - leito: 0.05m x 0.1m
    - particulas: 100

[2/8] exportando stl do blender
  executando blender...
  ✓ stl exportado: output/cfd/leito_blender.stl
    tamanho: 1.25 mb

[3/8] criando estrutura do caso openfoam
  ✓ caso criado em: output/cfd/leito_blender

[4/8] copiando stl para caso
  ✓ stl copiado para: output/cfd/leito_blender/constant/triSurface/leito.stl

[5/8] criando configuracao de malha
  ✓ blockMeshDict criado
  ✓ snappyHexMeshDict criado

[6/8] criando configuracao de simulacao
  ✓ arquivos de controle criados

[7/8] criando condicoes iniciais
  ✓ condicoes iniciais criadas

[8/8] criando script de execucao
  ✓ script Allrun criado

============================================================
  ✓ caso openfoam configurado com sucesso!
============================================================

caso criado em: output/cfd/leito_blender

para executar a simulacao:
  cd output/cfd/leito_blender
  ./Allrun

ou execute este script com --run
```

## executar simulação

### opção 1: flag --run

```bash
python setup_openfoam_case.py \
    ../../dsl/leito_blender.bed.json \
    ../../output/models/leito_blender.blend \
    --run
```

### opção 2: script allrun

```bash
cd ../../output/cfd/leito_blender
./Allrun
```

### opção 3: comandos manuais

```bash
cd ../../output/cfd/leito_blender

# 1. gerar malha de fundo
blockMesh

# 2. gerar malha refinada
snappyHexMesh -overwrite

# 3. verificar malha
checkMesh

# 4. executar simulação
simpleFoam > log.simpleFoam 2>&1 &

# 5. monitorar
tail -f log.simpleFoam
```

## monitoramento

### durante a execução

o script `Allrun` mostra o progresso:

```
=========================================
 executando caso openfoam
=========================================

1. gerando malha de fundo (blockMesh)...
   ✓ malha de fundo criada

2. gerando malha refinada (snappyHexMesh)...
   (isso pode demorar alguns minutos...)
   ✓ malha refinada criada

3. verificando qualidade da malha...
   (veja log.checkMesh para detalhes)

4. executando simulacao (simpleFoam)...
   (monitorando convergencia...)
   Time = 100
   Time = 200
   ...
   Time = 1000
   ✓ simulacao concluida!

=========================================
 caso executado com sucesso!
=========================================

proximos passos:
  - visualizar: touch caso.foam && paraview caso.foam
  - pos-processar: postProcess -func sample
```

### logs gerados

- `log.blockMesh`: geração malha de fundo
- `log.snappyHexMesh`: geração malha refinada
- `log.checkMesh`: qualidade da malha
- `log.simpleFoam`: simulação principal

## visualização

### paraview (recomendado)

```bash
# no diretório do caso
touch caso.foam

# abrir no windows
explorer.exe .
# duplo clique em caso.foam

# ou no linux
paraview caso.foam
```

### pós-processamento

```bash
# extrair dados em linha
postProcess -func singleGraph

# calcular forças
postProcess -func forces

# calcular pressão média
postProcess -func surfaceFieldValue
```

## troubleshooting

### problema 1: blender não encontrado

**erro:**

```
FileNotFoundError: blender nao encontrado no sistema
```

**solução:**
adicione o caminho do blender no script ou ao path do sistema.

### problema 2: openfoam não encontrado

**erro:**

```
./Allrun: line 5: blockMesh: command not found
```

**solução:**

```bash
# no wsl, carregar openfoam
source /opt/openfoam11/etc/bashrc

# adicionar ao ~/.bashrc para carregar sempre
echo "source /opt/openfoam11/etc/bashrc" >> ~/.bashrc
```

### problema 3: erro na geração de malha

**erro:**

```
erro no snappyHexMesh! veja log.snappyHexMesh
```

**solução:**

```bash
# verificar log
cat log.snappyHexMesh

# possíveis causas:
# 1. stl com erros (verificar no blender)
# 2. refinamento muito alto (editar snappyHexMeshDict)
# 3. locationInMesh fora do domínio
```

### problema 4: simulação não converge

**sintomas:**

```
Time = 500
Courant Number mean: 0.5 max: 10.5  <- muito alto!
```

**solução:**

```bash
# editar system/fvSolution
# aumentar relaxationFactors:
relaxationFactors
{
    fields
    {
        p    0.3;  # era 0.3, deixar igual
    }
    equations
    {
        U    0.5;  # era 0.7, diminuir para 0.5
    }
}
```

## próximas melhorias

### recursos planejados

- [ ] paralelização automática
- [ ] extração automática de resultados
- [ ] geração de relatório com plots
- [ ] integração com dashboard web
- [ ] suporte a diferentes solvers (pisoFoam, etc)
- [ ] templates para diferentes tipos de escoamento

## exemplos

### exemplo 1: leito com 100 partículas

```bash
python setup_openfoam_case.py \
    ../../dsl/leito_100.bed.json \
    ../../output/models/leito_100.blend
```

### exemplo 2: leito com velocidade alta

editar `leito.bed.json`:

```json
{
  "cfd": {
    "inlet_velocity": 1.0  # 10x mais rápido
  }
}
```

```bash
python setup_openfoam_case.py \
    ../../dsl/leito_rapido.bed.json \
    ../../output/models/leito_rapido.blend \
    --run
```

### exemplo 3: simulação com água

editar `leito.bed.json`:

```json
{
  "cfd": {
    "fluid_viscosity": 1e-6,  # água
    "fluid_density": 1000.0
  }
}
```

## dependências

### python

- python 3.8+
- bibliotecas padrão (json, subprocess, pathlib)

### software externo

- blender 3.0+ (para exportar stl)
- openfoam 9+ (para simulação)
- paraview 5.0+ (para visualização)

### sistema

- wsl2 + ubuntu (windows)
- ou linux nativo

## referências

- **openfoam user guide**: https://www.openfoam.com/documentation/user-guide
- **snappyhexmesh tutorial**: https://cfd.direct/openfoam/user-guide/v6-snappyHexMesh/
- **simpleFoam**: https://www.openfoam.com/documentation/guides/latest/doc/guide-applications-solvers-incompressible-simpleFoam.html
