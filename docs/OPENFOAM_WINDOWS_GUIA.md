# guia openfoam no windows

## visão geral

o openfoam (open field operation and manipulation) é um software de cfd (computational fluid dynamics) open source. no windows, existem 3 formas principais de instalar.

---

## opção 1: wsl2 (windows subsystem for linux) - recomendado

### vantagens
- ✅ instalação oficial suportada
- ✅ melhor performance
- ✅ acesso a todas as ferramentas linux
- ✅ integração com windows
- ✅ gratuito

### requisitos
- windows 10 versão 2004+ ou windows 11
- 8gb ram (mínimo), 16gb recomendado
- 20gb espaço em disco

---

### passo 1: instalar wsl2

#### 1.1 abrir powershell como administrador

```powershell
# comando único para instalar wsl2 com ubuntu
wsl --install
```

**ou manualmente:**

```powershell
# habilitar wsl
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# habilitar virtualizacao
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# reiniciar o computador
shutdown /r /t 0
```

#### 1.2 após reiniciar, definir wsl2 como padrão

```powershell
wsl --set-default-version 2
```

#### 1.3 instalar ubuntu

```powershell
# instalar ubuntu 22.04 lts
wsl --install -d Ubuntu-22.04
```

**ou pela microsoft store:**
- abrir microsoft store
- buscar "ubuntu 22.04 lts"
- clicar em "obter"

#### 1.4 configurar ubuntu

```bash
# primeira vez: criar usuário e senha
# usuario: seu_nome
# senha: sua_senha

# atualizar sistema
sudo apt update
sudo apt upgrade -y
```

---

### passo 2: instalar openfoam no wsl2

#### 2.1 adicionar repositório openfoam

```bash
# adicionar chave gpg
sudo sh -c "wget -O - https://dl.openfoam.org/gpg.key | apt-key add -"

# adicionar repositório
sudo add-apt-repository http://dl.openfoam.org/ubuntu

# atualizar lista de pacotes
sudo apt update
```

#### 2.2 instalar openfoam

```bash
# instalar openfoam 11 (versão mais recente)
sudo apt install openfoam11

# ou openfoam 10
sudo apt install openfoam10

# ou openfoam 9
sudo apt install openfoam9
```

**tempo de instalação:** 10-15 minutos

#### 2.3 configurar ambiente

```bash
# adicionar ao bashrc para carregar automaticamente
echo "source /opt/openfoam11/etc/bashrc" >> ~/.bashrc

# recarregar bashrc
source ~/.bashrc

# verificar instalação
which simpleFoam
# saída: /opt/openfoam11/platforms/linux64GccDPInt32Opt/bin/simpleFoam
```

---

### passo 3: verificar instalação

```bash
# verificar versão
foamVersion
# saída: 11

# verificar aplicações disponíveis
ls $FOAM_APP

# testar caso tutorial
cd $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily
./Allrun
```

---

## opção 2: docker (alternativa)

### vantagens
- ✅ isolado do sistema
- ✅ fácil de remover
- ✅ portável
- ⚠️ performance um pouco menor que wsl2

### passo 1: instalar docker desktop

1. baixar docker desktop: https://www.docker.com/products/docker-desktop
2. instalar e reiniciar
3. abrir docker desktop

### passo 2: baixar imagem openfoam

```bash
# abrir powershell ou cmd
docker pull openfoam/openfoam11-paraview510

# ou versão específica
docker pull openfoam/openfoam10-paraview56
```

### passo 3: executar container

```bash
# criar container interativo
docker run -it --name openfoam openfoam/openfoam11-paraview510

# dentro do container
source /opt/openfoam11/etc/bashrc
cd $FOAM_TUTORIALS
```

---

## opção 3: bluecfd (interface nativa windows) - não recomendado

### vantagens
- ✅ interface gráfica nativa
- ⚠️ versão desatualizada (openfoam 4.x)
- ⚠️ menos recursos

### instalação

1. baixar: http://bluecfd.github.io/Core/Downloads/
2. instalar bluecfd-core 2020
3. abrir "bluecfd-core 2020 shell"

**nota:** não recomendado para projetos novos, versão muito antiga.

---

## uso básico do openfoam

### estrutura de um caso openfoam

```
meuCaso/
├── 0/                    # condições iniciais
│   ├── U                # velocidade
│   ├── p                # pressão
│   └── T                # temperatura
├── constant/            # propriedades constantes
│   ├── polyMesh/       # malha
│   ├── transportProperties
│   └── turbulenceProperties
├── system/             # controle de simulação
│   ├── controlDict     # controle temporal
│   ├── fvSchemes       # esquemas numéricos
│   └── fvSolution      # solver settings
└── Allrun              # script para executar
```

---

### workflow típico

#### 1. criar geometria e malha

```bash
# criar malha com blockmesh (malha estruturada)
blockMesh

# ou snappyhexmesh (malha não estruturada)
snappyHexMesh -overwrite

# ou importar de stl/obj
surfaceFeatureExtract
snappyHexMesh
```

#### 2. verificar malha

```bash
# verificar qualidade da malha
checkMesh

# visualizar malha em paraview
paraFoam
```

#### 3. definir condições iniciais e de contorno

editar arquivos em `0/`:

```bash
# exemplo: 0/U (velocidade)
dimensions      [0 1 -1 0 0 0 0];  // m/s

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }
    
    outlet
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            noSlip;
    }
}
```

#### 4. executar simulação

```bash
# para escoamento incompressível, estacionário
simpleFoam

# para escoamento incompressível, transiente
pisoFoam

# para escoamento compressível
rhoPimpleFoam

# executar em paralelo (4 núcleos)
mpirun -np 4 simpleFoam -parallel
```

#### 5. pós-processamento

```bash
# abrir paraview
paraFoam

# extrair dados
postProcess -func sample
postProcess -func surfaceFieldValue
```

---

## integração com python

### pyfoam (ferramenta python para openfoam)

```bash
# instalar pyfoam no wsl2
pip install PyFoam

# usar pyfoam
pyFoamPlotWatcher.py log
pyFoamRunner.py simpleFoam
```

### executar openfoam de python

```python
import subprocess
import os

# definir caso
case_dir = "/home/user/openfoam/cases/cavity"

# executar blockmesh
subprocess.run(["blockMesh"], cwd=case_dir)

# executar solver
subprocess.run(["simpleFoam"], cwd=case_dir)

# extrair resultados
subprocess.run(["postProcess", "-func", "singleGraph"], cwd=case_dir)
```

---

## integração com o projeto cfd-pipeline-tcc-1

### estrutura proposta

```
CFD-PIPELINE-TCC-1/
├── dsl/                        # já implementado
├── scripts/
│   ├── blender_scripts/       # já implementado
│   └── openfoam_scripts/      # novo!
│       ├── setup_case.py
│       ├── generate_mesh.py
│       ├── run_simulation.py
│       └── extract_results.py
├── templates/
│   └── openfoam/
│       ├── blockMeshDict.template
│       ├── controlDict.template
│       └── fvSchemes.template
└── output/
    ├── models/                # .blend files
    └── cfd/                   # resultados openfoam
        ├── mesh/
        ├── fields/
        └── plots/
```

---

## exemplo completo: leito empacotado

### 1. preparar geometria (já temos do blender)

```python
# exportar malha do blender para stl
import bpy

# exportar leito
bpy.ops.export_mesh.stl(
    filepath="leito.stl",
    use_selection=True
)
```

### 2. criar caso openfoam

```bash
# criar diretório do caso
mkdir -p ~/openfoam/casos/leito_empacotado
cd ~/openfoam/casos/leito_empacotado

# copiar template
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily/* .

# substituir geometria
mkdir -p constant/triSurface
cp /mnt/c/Users/seu_usuario/leito.stl constant/triSurface/
```

### 3. gerar malha com snappyhexmesh

editar `system/snappyHexMeshDict`:

```c++
geometry
{
    leito.stl
    {
        type triSurfaceMesh;
        name leito;
    }
}

castellatedMeshControls
{
    features
    (
        { file "leito.eMesh"; level 1; }
    );
    
    refinementSurfaces
    {
        leito
        {
            level (2 3);
        }
    }
}
```

executar:

```bash
surfaceFeatureExtract
blockMesh
snappyHexMesh -overwrite
checkMesh
```

### 4. configurar física

editar `constant/transportProperties`:

```c++
transportModel  Newtonian;

nu              1.5e-05;  // viscosidade cinemática do ar (m²/s)

// ou para água
// nu              1e-06;
```

### 5. executar simulação

```bash
# simpleFoam para escoamento estacionário
simpleFoam > log.simpleFoam 2>&1

# monitorar convergência
tail -f log.simpleFoam

# ou com pyfoam
pyFoamPlotWatcher.py log.simpleFoam
```

### 6. visualizar resultados

```bash
# abrir paraview
paraFoam

# ou no windows
# windows explorer: \\wsl$\Ubuntu-22.04\home\seu_usuario\openfoam\casos\leito_empacotado
# abrir arquivo .foam no paraview windows
```

---

## acessar arquivos wsl2 do windows

### método 1: explorador de arquivos

```
\\wsl$\Ubuntu-22.04\home\seu_usuario\
```

### método 2: montar drive windows no wsl

```bash
# windows c:\ está em /mnt/c/
cd /mnt/c/Users/seu_usuario/Downloads/CFD-PIPELINE-TCC-1
```

### método 3: criar link simbólico

```bash
# criar link do projeto no wsl
ln -s /mnt/c/Users/seu_usuario/Downloads/CFD-PIPELINE-TCC-1 ~/projeto
cd ~/projeto
```

---

## troubleshooting

### problema 1: wsl2 não inicia

**solução:**
```powershell
# verificar status
wsl --status

# atualizar wsl
wsl --update

# reiniciar wsl
wsl --shutdown
wsl
```

### problema 2: openfoam não encontrado

**solução:**
```bash
# verificar se bashrc está carregado
source ~/.bashrc

# verificar variável foam_app
echo $FOAM_APP

# adicionar manualmente se necessário
source /opt/openfoam11/etc/bashrc
```

### problema 3: paraview não abre

**solução 1 (usar paraview windows):**
```bash
# criar arquivo .foam
touch caso.foam

# abrir no windows
explorer.exe .
# abrir caso.foam no paraview windows
```

**solução 2 (instalar paraview no wsl com x11):**
```bash
# instalar xserver no windows: vcxsrv ou xming
# configurar display
export DISPLAY=:0

# instalar paraview
sudo apt install paraview
paraview
```

### problema 4: simulação muito lenta

**soluções:**
```bash
# usar processamento paralelo
# editar system/decomposeParDict
decomposePar
mpirun -np 4 simpleFoam -parallel
reconstructPar

# reduzir tamanho da malha
# ajustar refinamento em snappyHexMeshDict

# usar solver mais rápido
# simpleFoam (estacionário) é mais rápido que pisoFoam (transiente)
```

---

## recursos adicionais

### documentação oficial
- **openfoam user guide**: https://www.openfoam.com/documentation/user-guide
- **openfoam tutorials**: https://www.openfoam.com/documentation/tutorial-guide
- **openfoam api**: https://www.openfoam.com/documentation/cpp-guide

### tutoriais recomendados
- **wolf dynamics**: https://www.wolfdynamics.com/training.html
- **cfd direct**: https://cfd.direct/openfoam/user-guide/
- **holzmann cfd**: https://holzmann-cfd.com/

### comunidade
- **cfd online forum**: https://www.cfd-online.com/Forums/openfoam/
- **reddit r/cfd**: https://www.reddit.com/r/CFD/
- **stack overflow openfoam**: https://stackoverflow.com/questions/tagged/openfoam

---

## próximos passos para o projeto

### 1. criar módulo openfoam no wizard

```python
# dsl/bed_wizard.py - adicionar modo 8
def openfoam_mode(self):
    """modo openfoam - configurar simulação cfd"""
    # coletar parâmetros cfd
    # gerar caso openfoam
    # executar simulação
    # visualizar resultados
```

### 2. automatizar geração de caso

```python
# scripts/openfoam_scripts/setup_case.py
def create_openfoam_case(bed_params, output_dir):
    """criar caso openfoam a partir de params.json"""
    # ler geometria do blender
    # gerar blockMeshDict ou snappyHexMeshDict
    # configurar boundary conditions
    # gerar controlDict, fvSchemes, fvSolution
```

### 3. integrar com pipeline

```
bed_wizard.py → leito.bed → leito.bed.json
    ↓
leito_extracao.py → leito.blend → leito.stl
    ↓
setup_openfoam.py → caso openfoam
    ↓
run_simulation.py → resultados cfd
    ↓
visualize_results.py → plots e análises
```

---

## comandos úteis - resumo rápido

```bash
# ==== instalação ====
wsl --install -d Ubuntu-22.04
sudo apt install openfoam11
source /opt/openfoam11/etc/bashrc

# ==== criar caso ====
mkdir meuCaso && cd meuCaso
mkdir -p 0 constant system

# ==== malha ====
blockMesh                    # malha estruturada
snappyHexMesh -overwrite    # malha não estruturada
checkMesh                    # verificar qualidade

# ==== simulação ====
simpleFoam                   # estacionário incompressível
pisoFoam                     # transiente incompressível
mpirun -np 4 simpleFoam -parallel  # paralelo

# ==== pós-processamento ====
paraFoam                     # visualização
postProcess -func sample     # extrair dados

# ==== utilitários ====
foamCleanTutorials          # limpar caso
foamListTimes               # listar tempos
foamInfo                    # informações do sistema
```

---

## conclusão

**recomendação final:** use **wsl2 + ubuntu + openfoam 11**

essa é a configuração:
- ✅ mais moderna
- ✅ melhor suportada
- ✅ melhor performance
- ✅ mais documentação disponível
- ✅ integração perfeita com windows

**tempo total de setup:** 30-45 minutos

**próximo passo:** experimentar tutoriais básicos em `$FOAM_TUTORIALS`

---

*guia criado para windows 10/11*  
*última atualização: outubro 2024*  
*openfoam versão: 11*

