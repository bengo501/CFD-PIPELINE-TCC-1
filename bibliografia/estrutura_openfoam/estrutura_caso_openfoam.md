# estrutura de caso openfoam - guia completo

## 📁 visão geral

um caso openfoam é organizado em uma estrutura de diretórios padronizada que separa diferentes aspectos da simulação cfd.

```
leito_interativo/                  # raiz do caso
├── 0/                            # condições iniciais e de contorno
│   ├── U                         # campo de velocidade
│   ├── p                         # campo de pressão
│   └── ...                       # outros campos (k, epsilon, etc)
├── constant/                     # propriedades físicas e malha
│   ├── polyMesh/                 # malha computacional
│   ├── triSurface/              # geometrias stl
│   │   └── leito.stl            # modelo 3d do leito
│   ├── transportProperties      # propriedades do fluido
│   └── turbulenceProperties     # modelo de turbulência
├── system/                       # configuração da simulação
│   ├── controlDict              # controle geral (tempo, gravação)
│   ├── fvSchemes                # esquemas numéricos
│   ├── fvSolution               # solvers e tolerâncias
│   ├── blockMeshDict            # malha de fundo
│   └── snappyHexMeshDict        # malha refinada ao redor do leito
├── Allrun                        # script para executar simulação
└── caso.foam                     # arquivo vazio para paraview
```

---

## 📂 diretório `0/` - condições iniciais

### 0/U - campo de velocidade

**arquivo**: `0/U`  
**tipo**: `volVectorField`  
**dimensões**: [0 1 -1 0 0 0 0] = m/s

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;  // campo vetorial por volume
    object      U;                // velocidade
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];  // [kg m s K mol A cd]
                                    // velocidade = m/s

internalField   uniform (0 0 0.1);  // velocidade inicial em todo domínio
                                     // (vx vy vz) = (0 0 0.1) m/s

boundaryField   // condições de contorno
{
    leito       // patch da geometria do leito
    {
        type            noSlip;  // velocidade zero na parede
    }
    
    walls       // paredes do domínio
    {
        type            noSlip;  // velocidade zero
    }
    
    inlet       // entrada (se existir)
    {
        type            fixedValue;      // valor fixo
        value           uniform (0 0 0.1);  // 0.1 m/s vertical
    }
    
    outlet      // saída (se existir)
    {
        type            zeroGradient;    // gradiente zero (∂U/∂n = 0)
    }
}
```

**explicação dos campos**:

| campo | significado | exemplo |
|-------|-------------|---------|
| `dimensions` | unidades físicas | [0 1 -1 0 0 0 0] = m/s |
| `internalField` | valor inicial em todo domínio | uniform (0 0 0.1) |
| `boundaryField` | condições nos contornos | noSlip, fixedValue, etc |

**tipos de condição de contorno para U**:

| tipo | descrição | uso típico |
|------|-----------|------------|
| `noSlip` | velocidade zero (u=0) | paredes sólidas |
| `fixedValue` | valor prescrito | entrada de fluido |
| `zeroGradient` | ∂U/∂n = 0 | saída livre |
| `slip` | componente normal zero | simetria |
| `pressureInletVelocity` | entrada com pressão fixa | - |

### 0/p - campo de pressão

**arquivo**: `0/p`  
**tipo**: `volScalarField`  
**dimensões**: [0 2 -2 0 0 0 0] = m²/s² (pressão cinemática)

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;  // campo escalar por volume
    object      p;                // pressão
}

dimensions      [0 2 -2 0 0 0 0];  // pressão cinemática = m²/s²
                                    // (para incompressível: p/ρ)

internalField   uniform 0;          // pressão inicial = 0 (referência)

boundaryField
{
    leito
    {
        type            zeroGradient;  // ∂p/∂n = 0 (parede sólida)
    }
    
    walls
    {
        type            zeroGradient;
    }
    
    inlet
    {
        type            zeroGradient;  // velocidade prescrita → ∂p/∂n = 0
    }
    
    outlet
    {
        type            fixedValue;    // pressão prescrita
        value           uniform 0;      // pressão de referência
    }
}
```

**nota importante**: em simulações incompressíveis (simpleFoam), p é na verdade **p/ρ** (pressão cinemática).

---

## 📂 diretório `constant/` - propriedades

### constant/transportProperties - propriedades do fluido

**arquivo**: `constant/transportProperties`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}

transportModel  Newtonian;  // modelo newtoniano (μ constante)

nu              1.8e-05;    // viscosidade cinemática [m²/s]
                            // ar a 20°C: ν ≈ 1.5e-5 m²/s
                            // água a 20°C: ν ≈ 1.0e-6 m²/s
```

**propriedades do fluido**:

| fluido | ν (m²/s) | ρ (kg/m³) | μ (Pa·s) |
|--------|----------|-----------|----------|
| ar (20°C) | 1.5e-5 | 1.2 | 1.8e-5 |
| água (20°C) | 1.0e-6 | 998 | 1.0e-3 |
| óleo (SAE 30) | 1.0e-4 | 900 | 0.09 |

**cálculo da viscosidade dinâmica**:
```
μ = ν × ρ
```

### constant/turbulenceProperties - modelo de turbulência

**arquivo**: `constant/turbulenceProperties`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}

simulationType  laminar;  // ou: RAS (RANS), LES

// para RAS (Reynolds-Averaged Simulation):
/*
simulationType  RAS;

RAS
{
    RASModel        kEpsilon;    // k-ε padrão
                    // ou: kOmegaSST, realizableKE, etc
    
    turbulence      on;
    
    printCoeffs     on;
}
*/
```

**modelos de turbulência disponíveis**:

| modelo | aplicação | re típico |
|--------|-----------|-----------|
| `laminar` | escoamento laminar | re < 2300 |
| `kEpsilon` | geral, industrial | re > 10000 |
| `kOmegaSST` | camada limite, separação | re > 5000 |
| `realizableKE` | jatos, mistura | re > 10000 |
| `SpalartAllmaras` | aeronáutica | re > 10000 |

### constant/polyMesh/ - malha computacional

**diretório gerado automaticamente** por blockMesh e snappyHexMesh.

```
constant/polyMesh/
├── boundary        # definição dos patches (inlet, outlet, walls, etc)
├── faces           # conectividade das faces
├── neighbour       # células vizinhas
├── owner           # células proprietárias das faces
└── points          # coordenadas dos vértices
```

**não editar manualmente!** gerado por:
- `blockMesh`: malha estruturada de fundo
- `snappyHexMesh`: refinamento ao redor da geometria

### constant/triSurface/ - geometrias stl

```
constant/triSurface/
└── leito.stl       # modelo 3d exportado do blender
```

**formato stl** (stereolithography):
- malha triangular da superfície
- exportado pelo blender: `bpy.ops.export_mesh.stl()`
- usado pelo snappyHexMesh para refinar malha

---

## 📂 diretório `system/` - configuração

### system/controlDict - controle geral da simulação

**arquivo**: `system/controlDict`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

application     simpleFoam;    // solver utilizado
                               // simpleFoam: incompressível, regime permanente

startFrom       startTime;     // iniciar de tempo inicial
                               // ou: latestTime (continuar simulação)

startTime       0;             // tempo inicial [s]

stopAt          endTime;       // parar no tempo final
                               // ou: writeNow, noWriteNow

endTime         1000;          // tempo final (iterações para simpleFoam)

deltaT          1;             // passo de tempo [s]
                               // (fictício para regime permanente)

writeControl    timeStep;      // gravar a cada N passos de tempo
                               // ou: runTime, adjustableRunTime

writeInterval   100;           // gravar a cada 100 iterações

purgeWrite      2;             // manter apenas 2 últimos tempos gravados
                               // economiza espaço em disco

writeFormat     binary;        // formato binário (mais rápido)
                               // ou: ascii (legível)

writePrecision  6;             // precisão dos números (6 dígitos)

writeCompression off;          // não comprimir arquivos
                               // ou: on (gzip)

timeFormat      general;       // formato do tempo
                               // ou: fixed, scientific

timePrecision   6;             // precisão do tempo

runTimeModifiable true;        // permite modificar durante execução
                               // (editar e recarregar dicionários)
```

**parâmetros importantes**:

| parâmetro | descrição | valores típicos |
|-----------|-----------|-----------------|
| `application` | solver | simpleFoam, pimpleFoam, icoFoam |
| `endTime` | iterações | 500-2000 (simpleFoam) |
| `writeInterval` | frequência gravação | 50-200 |
| `purgeWrite` | arquivos mantidos | 2-5 |

### system/fvSchemes - esquemas numéricos

**arquivo**: `system/fvSchemes`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes      // derivada temporal (∂/∂t)
{
    default         steadyState;  // regime permanente
                                  // ou: Euler (1ª ordem), backward (2ª ordem)
}

gradSchemes     // gradiente (∇φ)
{
    default         Gauss linear;  // gauss + interpolação linear
                                   // (2ª ordem, preciso)
    
    grad(U)         Gauss linear;
    grad(p)         Gauss linear;
}

divSchemes      // divergente (∇·φ)
{
    default                         none;
    
    div(phi,U)                      bounded Gauss linearUpwind grad(U);
                                    // upwind linearizado (2ª ordem)
                                    // bounded: limita valores não-físicos
    
    div(phi,k)                      bounded Gauss upwind;
                                    // upwind 1ª ordem (estável)
    
    div(phi,epsilon)                bounded Gauss upwind;
    
    div((nuEff*dev2(T(grad(U)))))  Gauss linear;
}

laplacianSchemes  // laplaciano (∇²φ)
{
    default         Gauss linear corrected;
                    // linear + correção de não-ortogonalidade
}

interpolationSchemes  // interpolação centro→face
{
    default         linear;  // 2ª ordem
}

snGradSchemes   // gradiente normal superfície
{
    default         corrected;  // correção de não-ortogonalidade
}
```

**ordem de precisão dos esquemas**:

| esquema | ordem | estabilidade | uso |
|---------|-------|--------------|-----|
| `upwind` | 1ª | alta | turbulência (k, ε) |
| `linearUpwind` | 2ª | média | convecção (U) |
| `linear` | 2ª | baixa | difusão (∇²) |
| `QUICK` | 3ª | muito baixa | alto re |

### system/fvSolution - solvers e tolerâncias

**arquivo**: `system/fvSolution`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

solvers     // configuração dos solvers lineares
{
    p       // solver para pressão
    {
        solver          PCG;        // preconditioned conjugate gradient
                                    // (eficiente para matrizes simétricas)
        
        preconditioner  DIC;        // diagonal incomplete cholesky
        
        tolerance       1e-06;      // tolerância relativa
        relTol          0.01;       // tolerância mínima (1%)
    }
    
    U       // solver para velocidade
    {
        solver          PBiCGStab;  // preconditioned bi-conjugate gradient
                                    // (para matrizes não-simétricas)
        
        preconditioner  DILU;       // diagonal incomplete LU
        
        tolerance       1e-05;
        relTol          0.1;
    }
    
    "(k|epsilon)"   // regex: k ou epsilon
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }
}

SIMPLE      // algoritmo SIMPLE (regime permanente)
{
    nNonOrthogonalCorrectors    0;      // correções não-ortogonais
                                        // 0-2 (malhas boas)
                                        // 2-5 (malhas ruins)
    
    residualControl     // critério de convergência
    {
        p               1e-4;   // resíduo máximo para p
        U               1e-4;   // resíduo máximo para U
        "(k|epsilon)"   1e-4;
    }
}

relaxationFactors   // sub-relaxação (estabilidade)
{
    fields
    {
        p               0.3;    // 0.3 = conservador (mais estável)
                               // 0.7 = agressivo (mais rápido)
    }
    
    equations
    {
        U               0.7;    // 0.5-0.9 típico
        "(k|epsilon)"   0.7;
    }
}
```

**solvers lineares disponíveis**:

| solver | matriz | uso típico |
|--------|--------|------------|
| `PCG` | simétrica positiva definida | pressão |
| `PBiCGStab` | não-simétrica | velocidade, turbulência |
| `GAMG` | multigrid | pressão (grandes casos) |
| `smoothSolver` | iterativo simples | - |

**fatores de relaxação**:

| variável | fator típico | efeito |
|----------|--------------|--------|
| p | 0.3 | convergência lenta, estável |
| U | 0.7 | convergência moderada |
| k, ε | 0.7 | convergência moderada |

### system/blockMeshDict - malha de fundo

**arquivo**: `system/blockMeshDict`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

convertToMeters 1;  // fator de conversão (1 = metros)

vertices    // 8 vértices do domínio (cubo)
(
    (-0.1 -0.1 0)    // vértice 0
    ( 0.1 -0.1 0)    // vértice 1
    ( 0.1  0.1 0)    // vértice 2
    (-0.1  0.1 0)    // vértice 3
    (-0.1 -0.1 0.2)  // vértice 4
    ( 0.1 -0.1 0.2)  // vértice 5
    ( 0.1  0.1 0.2)  // vértice 6
    (-0.1  0.1 0.2)  // vértice 7
);

blocks      // definição do bloco
(
    hex (0 1 2 3 4 5 6 7)  // hexaedro com vértices 0-7
    (40 40 80)              // células em x, y, z
    simpleGrading (1 1 1)   // graduação uniforme
                            // ou: (2 1 0.5) = refinamento variável
);

edges       // arestas curvas (se necessário)
(
);

boundary    // patches (fronteiras)
(
    walls
    {
        type wall;
        faces
        (
            (0 1 5 4)  // face inferior (-z)
            (3 7 6 2)  // face superior (+z)
            (0 4 7 3)  // face esquerda (-x)
            (1 2 6 5)  // face direita (+x)
            (0 3 2 1)  // face frontal (-y)
            (4 5 6 7)  // face traseira (+y)
        );
    }
);

mergePatchPairs     // mesclar patches (se necessário)
(
);
```

**cálculo do número de células**:
```
total = nx × ny × nz
      = 40 × 40 × 80
      = 128,000 células
```

### system/snappyHexMeshDict - refinamento da malha

**arquivo**: `system/snappyHexMeshDict`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}

castellatedMesh true;   // refinar malha (castellação)
snap            true;   // ajustar à superfície (snap)
addLayers       false;  // adicionar camadas (prism layers)

geometry    // geometrias stl
{
    leito.stl
    {
        type triSurfaceMesh;
        name leito;
    }
}

castellatedMeshControls
{
    maxLocalCells           1000000;    // células máx por processador
    maxGlobalCells          2000000;    // células máx total
    minRefinementCells      0;          // células mín para refinar
    nCellsBetweenLevels     3;          // transição suave
    
    features    // refinamento em arestas
    (
    );
    
    refinementSurfaces  // refinamento nas superfícies
    {
        leito
        {
            level (2 3);    // níveis mín e máx
                           // nível 2 = 4x refinamento
                           // nível 3 = 8x refinamento
        }
    }
    
    refinementRegions   // refinamento em regiões
    {
    }
    
    locationInMesh (0 0 0.1);   // ponto dentro do domínio
                                 // (para detectar região interna)
}

snapControls    // ajuste à superfície
{
    nSmoothPatch            3;      // suavização do patch
    tolerance               2.0;    // tolerância de snap
    nSolveIter              30;     // iterações do solver
    nRelaxIter              5;      // iterações de relaxação
}

addLayersControls   // camadas prismáticas (boundary layer)
{
    relativeSizes           true;   // espessuras relativas
    
    layers
    {
        leito
        {
            nSurfaceLayers      3;  // 3 camadas
        }
    }
    
    expansionRatio          1.3;    // razão de expansão (1.2-1.5)
    finalLayerThickness     0.3;    // espessura da última camada
    minThickness            0.1;    // espessura mínima
}

meshQualityControls     // controle de qualidade
{
    maxNonOrtho             65;     // não-ortogonalidade máx (graus)
    maxBoundarySkewness     20;     // skewness máx no contorno
    maxInternalSkewness     4;      // skewness máx interno
    maxConcave              80;     // concavidade máx (graus)
    minVol                  1e-13;  // volume mínimo
    minTetQuality           1e-15;  // qualidade mín tetraedro
    minArea                 -1;     // área mínima
    minTwist                0.02;   // torção mínima
    minDeterminant          0.001;  // determinante mínimo
    minFaceWeight           0.02;   // peso mínimo da face
    minVolRatio             0.01;   // razão de volume mínima
}
```

**níveis de refinamento**:

| nível | fator | células | uso |
|-------|-------|---------|-----|
| 0 | 1x | base | longe da geometria |
| 1 | 2x | 8× base | região intermediária |
| 2 | 4x | 64× base | próximo à geometria |
| 3 | 8x | 512× base | superfície da geometria |

---

## 🚀 script Allrun - execução automatizada

**arquivo**: `Allrun`

```bash
#!/bin/sh
cd "${0%/*}" || exit 1

# source openfoam
source /opt/openfoam11/etc/bashrc

echo "========================================="
echo " executando caso openfoam"
echo "========================================="

# 1. blockMesh: criar malha de fundo
echo "1. gerando malha de fundo (blockMesh)..."
blockMesh > log.blockMesh 2>&1
if [ $? -ne 0 ]; then
    echo "erro no blockMesh! veja log.blockMesh"
    exit 1
fi
echo "   [OK] malha de fundo criada"

# 2. snappyHexMesh: refinar ao redor da geometria
echo "2. gerando malha refinada (snappyHexMesh)..."
snappyHexMesh -overwrite > log.snappyHexMesh 2>&1
if [ $? -ne 0 ]; then
    echo "erro no snappyHexMesh! veja log.snappyHexMesh"
    exit 1
fi
echo "   [OK] malha refinada criada"

# 3. checkMesh: verificar qualidade
echo "3. verificando qualidade da malha..."
checkMesh > log.checkMesh 2>&1
echo "   (veja log.checkMesh para detalhes)"

# 4. simpleFoam: executar simulação
echo "4. executando simulacao (simpleFoam)..."
simpleFoam > log.simpleFoam 2>&1 &
FOAM_PID=$!

# monitorar convergencia
while kill -0 $FOAM_PID 2>/dev/null; do
    if [ -f log.simpleFoam ]; then
        LAST_TIME=$(grep "^Time = " log.simpleFoam | tail -1)
        printf "\r   %s" "$LAST_TIME"
    fi
    sleep 2
done

echo "[OK] simulacao concluida!"

# 5. criar arquivo .foam para paraview
touch caso.foam

echo "proximos passos:"
echo "  - visualizar: paraview caso.foam"
```

**comandos openfoam utilizados**:

| comando | função | tempo típico |
|---------|--------|--------------|
| `blockMesh` | criar malha de fundo | 1-5s |
| `snappyHexMesh` | refinar malha | 30s-5min |
| `checkMesh` | verificar qualidade | 5-30s |
| `simpleFoam` | solver regime permanente | 5min-2h |

---

## 📊 monitoramento da simulação

### logs gerados

```
caso/
├── log.blockMesh           # log do blockMesh
├── log.snappyHexMesh       # log do snappyHexMesh
├── log.checkMesh           # estatísticas da malha
└── log.simpleFoam          # log do solver
```

### interpretar convergência

**arquivo**: `log.simpleFoam`

```
Time = 1
smoothSolver:  Solving for Ux, Initial residual = 1, Final residual = 0.01, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 1, Final residual = 0.01, No Iterations 5
smoothSolver:  Solving for Uz, Initial residual = 1, Final residual = 0.01, No Iterations 5
GAMG:  Solving for p, Initial residual = 1, Final residual = 0.001, No Iterations 10

Time = 100
...
smoothSolver:  Solving for Ux, Initial residual = 0.001, Final residual = 1e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001, Final residual = 1e-07, No Iterations 5
```

**critérios de convergência**:
- resíduos iniciais < 1e-3: simulação estável
- resíduos finais < 1e-4: convergência alcançada
- iterações < 10: malha boa, esquemas adequados

---

## 📈 pós-processamento

### visualização no paraview

```bash
# criar arquivo .foam
touch caso.foam

# abrir no paraview
paraview caso.foam
```

**campos disponíveis**:
- **U**: velocidade [m/s]
- **p**: pressão cinemática [m²/s²]
- **magnitude(U)**: magnitude da velocidade
- **streamlines**: linhas de corrente

### cálculo de métricas

**perda de carga (Δp)**:
```bash
# extrair pressão na entrada e saída
postProcess -func 'patchAverage(name=inlet, field=p)'
postProcess -func 'patchAverage(name=outlet, field=p)'

# calcular delta_p
Δp = p_inlet - p_outlet
```

**velocidade média**:
```bash
postProcess -func 'patchAverage(name=inlet, field=U)'
```

---

## 🔧 troubleshooting

### erros comuns

| erro | causa | solução |
|------|-------|---------|
| `blockMesh: command not found` | openfoam não carregado | `source /opt/openfoam11/etc/bashrc` |
| `Cannot find file "points"` | malha não gerada | rodar blockMesh primeiro |
| `Floating point exception` | malha ruim | verificar checkMesh, refazer malha |
| `Maximum iterations exceeded` | não convergiu | aumentar relaxação, refinar malha |

### dicas de performance

1. **malha**: começar com malha grosseira, refinar gradualmente
2. **relaxação**: valores baixos (0.3-0.5) para estabilidade
3. **tolerâncias**: não exagerar (1e-4 a 1e-6 suficiente)
4. **writeInterval**: gravar apenas o necessário (economiza i/o)

---

## 📚 referências

- openfoam foundation (2025). openfoam user guide. https://www.openfoam.com/documentation/user-guide/
- ferziger, j. h., & perić, m. (2002). computational methods for fluid dynamics (3rd ed.). springer.
- moukalled, f., mangani, l., & darwish, m. (2016). the finite volume method in computational fluid dynamics. springer.

---

**última atualização**: 9 outubro 2025  
**versão**: 1.0

