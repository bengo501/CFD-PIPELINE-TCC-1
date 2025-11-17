# guia de simulacao manual openfoam

## como fazer a simulacao manualmente no windows

### passo 1: preparar o caso openfoam

execute o script python a partir do diretorio `scripts/openfoam_scripts`:

```powershell
cd scripts/openfoam_scripts

python setup_openfoam_case.py ^
  ../../dsl/leito_interativo.bed.json ^
  ../../output/models/leito_interativo.blend ^
  --output-dir ../../output/cfd
```

**parametros:**

- primeiro argumento: caminho para arquivo `.bed.json` (gerado pelo compilador)
- segundo argumento: caminho para arquivo `.blend` (gerado pelo blender)
- `--output-dir`: diretorio onde o caso openfoam sera criado

**saida esperada:**

```
[1/8] carregando parametros...
[2/8] exportando stl do blender...
[3/8] criando estrutura do caso openfoam...
[4/8] copiando stl para caso...
[5/8] criando configuracao de malha...
[6/8] criando configuracao de simulacao...
[7/8] criando condicoes iniciais...
[8/8] criando script de execucao...
[OK] caso openfoam configurado com sucesso!
```

### passo 2: acessar wsl2

abra o terminal wsl2 (ubuntu):

```powershell
wsl
```

### passo 3: navegar ate o caso criado

no terminal wsl, navegue ate o diretorio do caso:

```bash
cd /mnt/c/Users/joxto/Downloads/CFD-PIPELINE-TCC-1/output/cfd/leito_interativo
```

**nota:** substitua `joxto` pelo seu nome de usuario do windows

### passo 4: carregar ambiente openfoam

antes de executar a simulacao, carregue o ambiente openfoam:

```bash
source /opt/openfoam11/etc/bashrc
```

**verificar se openfoam esta carregado:**

```bash
which simpleFoam
```

**saida esperada:** `/opt/openfoam11/platforms/linux64GccDPInt32Opt/bin/simpleFoam`

### passo 5: executar simulacao

existem duas opcoes:

#### opcao a: usar script allrun (recomendado)

```bash
./Allrun
```

este script executa automaticamente:

1. `blockMesh` - cria malha de fundo
2. `snappyHexMesh` - refina malha ao redor da geometria
3. `checkMesh` - verifica qualidade da malha
4. `simpleFoam` - resolve equacoes cfd

#### opcao b: executar passo a passo (debug)

se quiser controle total ou debugar problemas:

```bash
# 1. criar malha de fundo
blockMesh

# 2. refinar malha ao redor do leito
snappyHexMesh -overwrite

# 3. verificar qualidade da malha
checkMesh

# 4. executar simulacao
simpleFoam
```

### passo 6: monitorar progresso

durante a execucao do `simpleFoam`, voce vera:

```
Time = 1
smoothSolver:  Solving for Ux, Initial residual = 0.5, Final residual = 0.001
smoothSolver:  Solving for Uy, Initial residual = 0.4, Final residual = 0.001
...
```

**residuos devem diminuir a cada iteracao!**

### passo 7: verificar resultados

apos a simulacao, verifique os arquivos:

```bash
ls -la
```

**diretorios de resultado:**

- `0/` - condicoes iniciais
- `constant/` - propriedades e geometria
- `system/` - configuracoes de simulacao
- `1/`, `2/`, ... `N/` - resultados em cada passo de tempo
- `log.*` - arquivos de log de cada comando

### passo 8: visualizar no paraview

#### no wsl:

```bash
# criar arquivo .foam para paraview
touch caso.foam

# abrir paraview
paraview caso.foam &
```

#### no windows:

1. instale paraview para windows
2. abra o arquivo `caso.foam` no caminho:
   ```
   C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1\output\cfd\leito_interativo\caso.foam
   ```

## executar simulacao diretamente (sem parar)

se quiser preparar o caso **e** executar a simulacao em um unico comando:

```powershell
cd scripts/openfoam_scripts

python setup_openfoam_case.py ^
  ../../dsl/leito_interativo.bed.json ^
  ../../output/models/leito_interativo.blend ^
  --output-dir ../../output/cfd ^
  --run
```

**atencao:** a flag `--run` tentara executar o `Allrun` no wsl automaticamente!

## estrutura de arquivos do caso

```
leito_interativo/
├── 0/                           # condicoes iniciais
│   ├── U                        # campo de velocidade
│   ├── p                        # campo de pressao
├── constant/                    # propriedades constantes
│   ├── triSurface/
│   │   └── leito.stl           # geometria do leito
│   ├── transportProperties      # propriedades do fluido
│   └── turbulenceProperties     # modelo de turbulencia
├── system/                      # configuracoes
│   ├── controlDict             # parametros de tempo
│   ├── fvSchemes               # esquemas numericos
│   ├── fvSolution              # solver e tolerancias
│   ├── blockMeshDict           # malha de fundo
│   └── snappyHexMeshDict       # refinamento de malha
├── Allrun                       # script de execucao
└── caso.foam                    # arquivo para paraview
```

## parametros cfd configurados automaticamente

o script `setup_openfoam_case.py` le do arquivo `.bed.json`:

| parametro json               | uso no openfoam       | localizacao                      |
| ---------------------------- | --------------------- | -------------------------------- |
| `cfd.inlet_velocity`       | velocidade de entrada | `0/U`                          |
| `cfd.fluid_density`        | densidade do fluido   | `constant/transportProperties` |
| `cfd.fluid_viscosity`      | viscosidade dinamica  | `constant/transportProperties` |
| `cfd.max_iterations`       | numero de iteracoes   | `system/controlDict`           |
| `cfd.convergence_criteria` | criterio de parada    | `system/fvSolution`            |

## troubleshooting

### erro: "blockMesh: command not found"

**solucao:** carregue o ambiente openfoam:

```bash
source /opt/openfoam11/etc/bashrc
```

### erro: "cannot find file leito.stl"

**solucao:** verifique se o stl foi copiado:

```bash
ls -la constant/triSurface/
```

### erro: "simulation diverged" ou "floating point exception"

**causas possiveis:**

1. malha de baixa qualidade (execute `checkMesh`)
2. condicoes iniciais muito altas (reduza `inlet_velocity`)
3. timestep muito grande (reduza `deltaT` no `controlDict`)

**solucoes:**

```bash
# verificar malha
checkMesh

# editar velocidade de entrada
nano 0/U

# editar timestep
nano system/controlDict
```

### simulacao muito lenta

**otimizacoes:**

1. reduzir refinamento em `snappyHexMeshDict`
2. usar computacao paralela (adicionar `mpirun -np 4 simpleFoam -parallel`)
3. aumentar tolerancias em `fvSolution`

## proximos passos

1. **integrar ao bed_wizard**: adicionar modo "simulacao completa" que gera modelo + executa cfd
2. **analise automatica**: script python para extrair resultados (pressao, velocidade, perda de carga)
3. **visualizacao web**: dashboard para visualizar resultados sem paraview
4. **batch processing**: executar multiplas simulacoes variando parametros

## referencias

- [openfoam user guide](https://www.openfoam.com/documentation/user-guide)
- [snappyhexmesh tutorial](https://www.openfoam.com/documentation/tutorial-guide)
- [simpleFoam solver](https://www.openfoam.com/documentation/guides/latest/doc/guide-applications-solvers-incompressible-simpleFoam.html)
- [paraview tutorial](https://www.paraview.org/Wiki/ParaView/Users_Guide/Introduction)
