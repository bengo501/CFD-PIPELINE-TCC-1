# guia: onde ficam os resultados das simulações cfd

## locais dos resultados

### 1. resultados via web/api

**caminho padrão:**
```
output/cfd/sim_XXXXXXXX/
```

**como encontrar:**

#### opção a: interface web
```
1. abrir http://localhost:5173
2. clicar em "🌊 simulação cfd"
3. ver lista de simulações
4. copiar caminho do caso
```

**exemplo de card na interface:**
```
┌────────────────────────────────────┐
│ #a1b2c3d4              ✅ concluído │
│ [██████████████████████] 100%      │
│ simulação concluída com sucesso!   │
│                                    │
│ caso: output/cfd/sim_a1b2c3d4/    │ ← AQUI
│                                    │
│ [visualizar resultados] [remover]  │
└────────────────────────────────────┘
```

#### opção b: api rest
```bash
curl http://localhost:8000/api/cfd/list
```

**resposta:**
```json
{
  "simulations": [
    {
      "simulation_id": "a1b2c3d4",
      "status": "completed",
      "case_dir": "C:\\Users\\joxto\\Downloads\\CFD-PIPELINE-TCC-1\\output\\cfd\\sim_a1b2c3d4"
    }
  ]
}
```

### 2. resultados via script manual

**você executou:**
```bash
cd scripts/openfoam_scripts
python setup_openfoam_case.py \
  ../../dsl/leito_interativo.bed.json \
  ../../output/models/leito_interativo.blend \
  --output-dir ../../output/cfd
```

**resultados em:**
```
output/cfd/leito_interativo/  ← nome do arquivo .bed
```

**seu caso atual:**
```
C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1\output\cfd\leito_interativo\
```

---

## estrutura de resultados

### visão geral

```
output/cfd/leito_interativo/
│
├── 📁 0/                      # condições iniciais (t=0)
│   ├── U                     # velocidade inicial
│   ├── p                     # pressão inicial
│   ├── nut                   # viscosidade turbulenta
│   └── ...
│
├── 📁 constant/               # dados constantes
│   ├── polyMesh/             # malha gerada
│   │   ├── points            # coordenadas dos pontos
│   │   ├── faces             # faces da malha
│   │   ├── owner             # conectividade
│   │   ├── neighbour         # conectividade
│   │   └── boundary          # condições de contorno
│   │
│   ├── triSurface/           # geometria stl
│   │   └── leito.stl         # leito em stl
│   │
│   ├── transportProperties   # propriedades fluido
│   └── turbulenceProperties  # modelo turbulência
│
├── 📁 system/                 # configuração simulação
│   ├── controlDict           # controle temporal
│   ├── fvSchemes            # esquemas numéricos
│   ├── fvSolution           # solvers e tolerâncias
│   ├── blockMeshDict        # malha de fundo
│   └── snappyHexMeshDict    # malha refinada
│
├── 📁 1/                      # resultados tempo 1 (se executou)
│   ├── U                     # velocidade em t=1
│   ├── p                     # pressão em t=1
│   └── ...
│
├── 📁 2/, 3/, ... N/          # outros tempos
│
├── 📄 log.blockMesh          # log malha de fundo
├── 📄 log.snappyHexMesh      # log malha refinada
├── 📄 log.checkMesh          # log verificação
├── 📄 log.simpleFoam         # log simulação cfd
│
├── 📜 Allrun                  # script para executar tudo
└── 📄 caso.foam               # arquivo paraview
```

---

## arquivos importantes

### resultados da simulação

**campos de velocidade e pressão:**

```
1/, 2/, 3/, ... N/
├── U      # velocidade [m/s]
├── p      # pressão [Pa]
├── nut    # viscosidade turbulenta
└── phi    # fluxo de face
```

**onde:**
- `1/` = primeiro passo de tempo
- `2/` = segundo passo de tempo
- `N/` = tempo final

**formato:**
- arquivos texto em formato openfoam
- podem ser lidos com paraview

### logs de execução

**log.simpleFoam (principal):**
```
Time = 1
smoothSolver:  Solving for Ux, Initial residual = 0.5, Final residual = 0.001
smoothSolver:  Solving for Uy, Initial residual = 0.4, Final residual = 0.0008
...

Time = 2
smoothSolver:  Solving for Ux, Initial residual = 0.01, Final residual = 1e-05
...
```

**o que procurar:**
- residuais diminuindo (convergindo)
- "final residual" < 1e-4 (bom)
- sem mensagens de erro

**outros logs:**
- `log.blockMesh` - geração malha de fundo
- `log.snappyHexMesh` - malha refinada (pode ter 1000+ linhas)
- `log.checkMesh` - qualidade da malha

---

## como visualizar

### método 1: paraview (recomendado)

**no windows:**

1. **baixar paraview:**
   ```
   https://www.paraview.org/download/
   ```

2. **navegar até o caso:**
   ```
   C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1\output\cfd\leito_interativo\
   ```

3. **duplo clique em:**
   ```
   caso.foam
   ```

4. **no paraview:**
   - clicar em "apply"
   - escolher variável (U, p, etc)
   - ver campo colorido
   - rotacionar, zoom, etc

**no wsl:**

```bash
cd /mnt/c/Users/joxto/Downloads/CFD-PIPELINE-TCC-1/output/cfd/leito_interativo

# criar arquivo .foam se não existe
touch caso.foam

# abrir paraview
paraview caso.foam &
```

### método 2: ler arquivos texto

**campos em formato texto:**

```bash
cd output/cfd/leito_interativo

# ver velocidade final
cat 100/U

# ou último tempo disponível
ls -d [0-9]* | sort -n | tail -1
cd 100/
cat U
```

**estrutura do arquivo U:**
```
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];  # [m/s]

internalField   uniform (0.1 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (0.1 0 0);
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

### método 3: web viewer (futuro)

**planejado:**
- vtk.js para visualização web
- mostrar campos na interface
- sem precisar paraview

---

## como acessar seu caso atual

### seu caso existente

**caminho completo:**
```
C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1\output\cfd\leito_interativo\
```

**verificar estrutura:**

<function_calls>
<invoke name="run_terminal_cmd">
<parameter name="command">dir output\cfd\leito_interativo
