# CFD-PIPELINE-TCC-1

pipeline automatizado para simulacao cfd de leitos empacotados usando dsl, blender e openfoam.

https://github.com/bengo501/CFD-PIPELINE-TCC-1/issues

https://github.com/bengo501/CFD-PIPELINE-TCC-1/milestones

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Blender](https://img.shields.io/badge/blender-4.0+-orange.svg)](https://blender.org)
[![OpenFOAM](https://img.shields.io/badge/openfoam-11-green.svg)](https://openfoam.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## sobre o projeto

este projeto implementa um pipeline completo e reproduzivel para simulacao cfd (computational fluid dynamics) de leitos empacotados. a solucao aborda os principais problemas de reproducibilidade em simulacoes cientificas atraves de:

1. **dsl (domain specific language)** - linguagem `.bed` para descrever parametros de leitos
2. **geracao automatica de geometria 3d** - usando blender com fisica rigid body
3. **simulacao cfd automatizada** - usando openfoam (blockmesh, snappyhexmesh, simplefoam)
4. **containerizacao** - docker compose para reproducibilidade total (em desenvolvimento)
5. **interface web** - dashboard para visualizacao e analise (planejado)

## instalacao rapida

### windows

```batch
# baixar o projeto
git clone https://github.com/bengo501/CFD-PIPELINE-TCC-1.git
cd CFD-PIPELINE-TCC-1

# executar configuracao automatica
scripts\automation\setup_all.bat
```

### linux / macos

```bash
# baixar o projeto
git clone https://github.com/bengo501/CFD-PIPELINE-TCC-1.git
cd CFD-PIPELINE-TCC-1

# executar configuracao automatica
python3 scripts/automation/setup_complete.py
```

**tempo estimado:** 15-60 minutos (depende dos componentes escolhidos)

### 1. dsl - domain specific language

linguagem declarativa `.bed` para descrever leitos empacotados:

```
bed {
    diameter = 5cm
    height = 10cm
    wall_thickness = 2mm
    shape = "cylinder"
}

particles {
    count = 100
    kind = "sphere"
    diameter = 5mm
    mass = 0.1kg
}

packing {
    method = "rigid_body"
    gravity = (0, 0, -9.81) m/s2
}

cfd {
    regime = "laminar"
    inlet_velocity = 0.1 m/s
    fluid_density = 1000 kg/m3
}
```

### 2. compilador antlr

compila `.bed` para `.bed.json` normalizado (valores em si):

```bash
python dsl/compiler/bed_compiler_antlr_standalone.py leito.bed
# saida: leito.bed.json
```

### 3. geracao 3d com blender

cria modelo 3d com fisica rigid body:

```bash
python dsl/bed_wizard.py
# escolher modo blender
# modelo salvo em output/models/
```

**features:**
- cilindros ou cubos
- tampas planas ou hemisfericas
- particulas esfericas com fisica
- simulacao de empacotamento por gravidade

### 4. simulacao cfd com openfoam

configura e executa simulacao automaticamente:

```bash
python scripts/openfoam_scripts/setup_openfoam_case.py \
  dsl/leito.bed.json \
  output/models/leito.blend \
  --output-dir output/cfd \
  --run
```

**etapas automatizadas:**
1. exportar stl do blender
2. criar caso openfoam (0/, constant/, system/)
3. gerar malha com blockmesh
4. refinar malha com snappyhexmesh
5. verificar qualidade com checkmesh
6. resolver com simplefoam
7. gerar arquivo para paraview

## tecnologias utilizadas

| componente | tecnologia | versao | uso |
|------------|-----------|--------|-----|
| dsl | antlr | 4.13.1 | parser e compilador |
| geometria | blender | 4.0+ | geracao 3d e fisica |
| cfd | openfoam | 11 | simulacao fluidos |
| visualizacao | paraview | 5.11+ | pos-processamento |
| linguagem | python | 3.8+ | automacao e scripts |
| ambiente | wsl2 + ubuntu | 22.04 | execucao openfoam no windows |

## documentacao

### guias principais

- **[scripts/automation/README.md](scripts/automation/README.md)** - instalacao e configuracao
- **[docs/UML_COMPLETO.md](docs/UML_COMPLETO.md)** - arquitetura e diagramas
- **[docs/OPENFOAM_WINDOWS_GUIA.md](docs/OPENFOAM_WINDOWS_GUIA.md)** - guia openfoam
- **[dsl/documentacao.html](dsl/documentacao.html)** - documentacao web interativa

### guias especificos

- **[dsl/README_BLENDER_MODE.md](dsl/README_BLENDER_MODE.md)** - modo blender do wizard
- **[dsl/README_SISTEMA_AJUDA.md](dsl/README_SISTEMA_AJUDA.md)** - sistema de ajuda
- **[scripts/openfoam_scripts/GUIA_SIMULACAO_MANUAL.md](scripts/openfoam_scripts/GUIA_SIMULACAO_MANUAL.md)** - simulacao manual
- **[scripts/openfoam_scripts/README.md](scripts/openfoam_scripts/README.md)** - scripts openfoam

## uso basico

### 1. criar um leito com wizard interativo

```bash
cd dsl
python bed_wizard.py
```

**opcoes:**
1. modo interativo - responder questoes
2. modo edicao - editar arquivo .bed
3. modo blender - gerar apenas 3d
4. modo blender interativo - gerar e abrir blender
5. documentacao - abrir docs html

### 2. gerar modelo 3d

o wizard ja gera automaticamente no modo blender. ou manualmente:

```bash
cd scripts/standalone_scripts
python executar_leito_headless.py
```

### 3. executar simulacao cfd

```bash
# configurar caso
python scripts/openfoam_scripts/setup_openfoam_case.py \
  dsl/leito_interativo.bed.json \
  output/models/leito_interativo.blend \
  --output-dir output/cfd

# executar no wsl
wsl
cd /mnt/c/Users/[SEU_USUARIO]/Downloads/CFD-PIPELINE-TCC-1/output/cfd/leito_interativo
source /opt/openfoam11/etc/bashrc
./Allrun

# visualizar
paraview caso.foam
```

## estrutura do projeto

```
CFD-PIPELINE-TCC-1/
├── dsl/                              # domain specific language
│   ├── grammar/
│   │   └── Bed.g4                   # gramatica antlr
│   ├── compiler/
│   │   └── bed_compiler_antlr_standalone.py
│   ├── generated/                    # parser gerado
│   ├── bed_wizard.py                # interface principal
│   └── documentacao.html            # docs web
│
├── scripts/
│   ├── automation/                   # scripts de instalacao
│   │   ├── setup_complete.py        # setup completo
│   │   ├── install_openfoam.py      # instalador openfoam
│   │   ├── install_antlr.py         # instalador antlr
│   │   └── README.md                # guia instalacao
│   ├── blender_scripts/
│   │   └── leito_extracao.py        # geracao 3d
│   ├── openfoam_scripts/
│   │   └── setup_openfoam_case.py   # configuracao cfd
│   └── standalone_scripts/
│       └── executar_leito_headless.py
│
├── output/
│   ├── models/                       # arquivos .blend gerados
│   └── cfd/                          # casos openfoam
│
├── docs/                             # documentacao
│   ├── UML_COMPLETO.md              # diagramas arquitetura
│   ├── OPENFOAM_WINDOWS_GUIA.md     # guia openfoam
│   └── README.md                    # indice docs
│
└── README.md                         # este arquivo
```

## scripts de automacao

### instalacao completa

```bash
# instala tudo (python, java, antlr, blender, openfoam)
python scripts/automation/setup_complete.py
```

### instalacao por componente

```bash
# apenas antlr + java
python scripts/automation/install_antlr.py

# apenas blender
python scripts/automation/install_blender.py

# apenas openfoam (windows)
python scripts/automation/install_openfoam.py
```

mais detalhes: [scripts/automation/README.md](scripts/automation/README.md)

## exemplos

### exemplo 1: leito cilindrico com 100 particulas

```bash
python dsl/bed_wizard.py
# escolher modo blender
# diametro: 0.05m
# altura: 0.1m
# particulas: 100
# diametro particula: 0.005m
```

**resultado:** `output/models/leito_blender.blend`

### exemplo 2: simulacao cfd completa

```bash
# 1. criar leito
python dsl/bed_wizard.py  # modo interativo

# 2. gerar modelo
# (ja gerado automaticamente)

# 3. configurar cfd
python scripts/openfoam_scripts/setup_openfoam_case.py \
  dsl/leito_interativo.bed.json \
  output/models/leito_interativo.blend \
  --output-dir output/cfd \
  --run

# 4. visualizar
# (automatico ao final da simulacao)
```

## testes

### testar compilador dsl

```bash
cd dsl
python compiler/bed_compiler_antlr_standalone.py examples/leito.bed
```

### testar geracao 3d

```bash
python scripts/standalone_scripts/executar_leito_headless.py
```

### testar setup openfoam

```bash
python scripts/openfoam_scripts/setup_openfoam_case.py --help
```
## autor

**bengo501**

- github: [@bengo501](https://github.com/bengo501)
- projeto: [CFD-PIPELINE-TCC-1](https://github.com/bengo501/CFD-PIPELINE-TCC-1)
