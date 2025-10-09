# scripts python openfoam - guia completo

## 📋 visão geral

o script `setup_openfoam_case.py` automatiza a configuração completa de um caso openfoam, desde a exportação stl do blender até a execução da simulação cfd.

---

## 📁 estrutura

```
scripts/
└── openfoam_scripts/
    ├── setup_openfoam_case.py    # script principal (890 linhas)
    ├── post_process.py            # pós-processamento (planejado)
    └── README.md                  # documentação
```

---

## 🐍 setup_openfoam_case.py - arquitetura

### classe OpenFOAMCaseGenerator

**responsabilidades**:
1. carregar parâmetros do .bed.json
2. exportar geometria stl do blender
3. criar estrutura de diretórios openfoam
4. gerar dicionários de configuração
5. executar pipeline de malha
6. executar simulação
7. gerar relatório de resultados

```python
class OpenFOAMCaseGenerator:
    """
    gerador de caso openfoam integrado com dsl
    
    fundamentação:
    - openfoam foundation (2025): estrutura de casos
    - ferziger & perić (2002): métodos numéricos
    """
    
    def __init__(self, bed_json_path: Path, output_dir: Path):
        """
        inicializa gerador
        
        parâmetros:
            bed_json_path: arquivo .bed.json (saída do compilador)
            output_dir: diretório para caso openfoam
        
        atributos criados:
            self.params: dicionário com parâmetros
            self.case_dir: diretório do caso
            self.case_name: nome do caso
        """
        self.bed_json_path = Path(bed_json_path)
        self.output_dir = Path(output_dir)
        self.params = self._load_params()
        self.case_name = self.bed_json_path.stem.replace('.bed', '')
        self.case_dir = self.output_dir / self.case_name
```

---

## 📖 métodos principais

### 1. _load_params()

**função**: carrega e valida parâmetros do json

```python
def _load_params(self) -> Dict[str, Any]:
    """
    carregar parametros do arquivo .bed.json
    
    estrutura esperada:
        {
            "bed": {
                "diameter": 0.05,
                "height": 0.1,
                "wall_thickness": 0.002
            },
            "particles": {
                "count": 100,
                "diameter": 0.005
            },
            "cfd": {
                "inlet_velocity": 0.1,
                "fluid_density": 1.2,
                "fluid_viscosity": 1.8e-5,
                "regime": "laminar"
            }
        }
    
    retorna:
        dicionário com parâmetros validados
    
    exceções:
        FileNotFoundError: arquivo não encontrado
        json.JSONDecodeError: json inválido
    """
    
    print(f"\n[1/8] carregando parametros de {self.bed_json_path}")
    
    if not self.bed_json_path.exists():
        raise FileNotFoundError(f"arquivo nao encontrado: {self.bed_json_path}")
    
    with open(self.bed_json_path, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    # validar campos obrigatórios
    required_fields = ['bed', 'particles', 'cfd']
    for field in required_fields:
        if field not in params:
            raise ValueError(f"campo obrigatorio ausente: {field}")
    
    print(f"  [OK] parametros carregados")
    print(f"    - leito: {params['bed']['diameter']}m x {params['bed']['height']}m")
    print(f"    - particulas: {params['particles']['count']}")
    print(f"    - velocidade: {params['cfd']['inlet_velocity']} m/s")
    
    return params
```

**integração com dsl**:

```
.bed → antlr → .bed.json → setup_openfoam_case.py → caso openfoam
```

---

### 2. export_stl_from_blender()

**função**: exporta geometria do .blend para .stl

```python
def export_stl_from_blender(self, blend_file: Path) -> Path:
    """
    exportar geometria do blender para stl
    
    fluxo:
        1. criar script python temporário
        2. executar blender headless
        3. script blender exporta stl
        4. retornar caminho do stl
    
    parâmetro:
        blend_file: arquivo .blend gerado pelo leito_extracao.py
    
    retorna:
        caminho do arquivo .stl gerado
    
    fundamentação:
    - blender api: export_mesh.stl()
    - formato binário (menor e mais rápido)
    """
    
    print(f"\n[2/8] exportando stl do blender")
    
    if not blend_file.exists():
        raise FileNotFoundError(f"arquivo blend nao encontrado: {blend_file}")
    
    # script python para executar dentro do blender
    export_script = f"""
import bpy
import os

# selecionar todos objetos
bpy.ops.object.select_all(action='SELECT')

# exportar para stl
output_path = "{self.output_dir / f'{self.case_name}.stl'}"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

bpy.ops.export_mesh.stl(
    filepath=output_path,
    use_selection=True,
    ascii=False,  # binário = menor
    use_mesh_modifiers=True,
    global_scale=1.0
)

print(f"STL exportado: {{output_path}}")
"""
    
    # salvar script temporário
    script_path = self.output_dir / "export_stl.py"
    with open(script_path, 'w') as f:
        f.write(export_script)
    
    # executar blender headless
    blender_cmd = [
        "blender",
        "--background",
        str(blend_file),
        "--python", str(script_path)
    ]
    
    try:
        result = subprocess.run(
            blender_cmd,
            capture_output=True,
            text=True,
            timeout=60  # timeout 1 minuto
        )
        
        stl_path = self.output_dir / f"{self.case_name}.stl"
        
        if stl_path.exists():
            file_size = stl_path.stat().st_size / 1024  # KB
            print(f"  [OK] STL exportado: {stl_path.name} ({file_size:.1f} KB)")
            return stl_path
        else:
            raise RuntimeError("STL não foi criado!")
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("timeout na exportacao do STL")
    except Exception as e:
        print(f"  [ERRO] falha ao exportar STL: {e}")
        raise
```

**formato stl (stereolithography)**:

```
stl binário (compacto):
[cabeçalho 80 bytes]
[número de triângulos: 4 bytes]
para cada triângulo:
  [normal: 3 floats]
  [vértice 1: 3 floats]
  [vértice 2: 3 floats]
  [vértice 3: 3 floats]
  [atributos: 2 bytes]
```

**tamanhos típicos**:
- 100 partículas: ~500 KB
- 500 partículas: ~2 MB
- 1000 partículas: ~5 MB

---

### 3. create_case_structure()

**função**: cria estrutura de diretórios padrão openfoam

```python
def create_case_structure(self) -> None:
    """
    criar estrutura de diretórios do caso openfoam
    
    estrutura criada:
        caso/
        ├── 0/              # condições iniciais
        │   ├── U           # velocidade
        │   └── p           # pressão
        ├── constant/       # propriedades
        │   ├── polyMesh/   # malha (gerada depois)
        │   ├── triSurface/ # stl da geometria
        │   ├── transportProperties
        │   └── turbulenceProperties
        └── system/         # configuração
            ├── controlDict
            ├── fvSchemes
            ├── fvSolution
            ├── blockMeshDict
            └── snappyHexMeshDict
    
    fundamentação:
    - openfoam foundation (2025): case structure
    """
    
    print(f"\n[3/8] criando estrutura do caso")
    
    # criar diretórios
    dirs_to_create = [
        self.case_dir / "0",
        self.case_dir / "constant" / "polyMesh",
        self.case_dir / "constant" / "triSurface",
        self.case_dir / "system"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] {dir_path.relative_to(self.output_dir)}")
```

---

### 4. copy_stl_to_case()

**função**: copia arquivo stl para constant/triSurface/

```python
def copy_stl_to_case(self, stl_path: Path) -> None:
    """
    copiar stl para triSurface/
    
    parâmetro:
        stl_path: caminho do arquivo .stl
    
    destino:
        constant/triSurface/leito.stl
    
    nota:
        nome do arquivo deve ser consistente com
        snappyHexMeshDict (geometry section)
    """
    
    print(f"\n[4/8] copiando stl para caso")
    
    dest = self.case_dir / "constant" / "triSurface" / "leito.stl"
    shutil.copy2(stl_path, dest)
    
    print(f"  [OK] {dest.name}")
```

---

### 5. create_mesh_dict()

**função**: gera blockMeshDict e snappyHexMeshDict

```python
def create_mesh_dict(self) -> None:
    """
    gerar dicionários de malha
    
    gera dois arquivos:
        1. system/blockMeshDict: malha de fundo
        2. system/snappyHexMeshDict: refinamento
    
    cálculos:
        - domínio: 2x diâmetro do leito em x,y
                   1.5x altura do leito em z
        - células: 40 x 40 x 80 (base)
        - refinamento: nível 2-3 perto do leito
    
    fundamentação:
    - openfoam user guide: blockMesh, snappyHexMesh
    - ferziger (2002): resolução de malha
    """
    
    print(f"\n[5/8] gerando dicionarios de malha")
    
    # extrair parâmetros
    diameter = self.params['bed']['diameter']
    height = self.params['bed']['height']
    
    # calcular dimensões do domínio
    domain_x = diameter * 2  # 2x o diâmetro
    domain_y = diameter * 2
    domain_z = height * 1.5  # 1.5x a altura
    
    # número de células
    nx = 40
    ny = 40
    nz = int(80 * (height / 0.1))  # escalar com altura
    
    total_cells = nx * ny * nz
    print(f"  - dominio: {domain_x:.3f} x {domain_y:.3f} x {domain_z:.3f} m")
    print(f"  - celulas base: {nx} x {ny} x {nz} = {total_cells:,}")
    
    # 1. gerar blockMeshDict
    blockmesh_content = self._generate_blockmesh_dict(
        domain_x, domain_y, domain_z, nx, ny, nz
    )
    
    blockmesh_path = self.case_dir / "system" / "blockMeshDict"
    with open(blockmesh_path, 'w') as f:
        f.write(blockmesh_content)
    
    print(f"  [OK] blockMeshDict criado")
    
    # 2. gerar snappyHexMeshDict
    snappy_content = self._generate_snappy_dict(diameter, height)
    
    snappy_path = self.case_dir / "system" / "snappyHexMeshDict"
    with open(snappy_path, 'w') as f:
        f.write(snappy_content)
    
    print(f"  [OK] snappyHexMeshDict criado")
```

**cálculo do domínio computacional**:

```
vista superior:
    
       domain_x = 2 × diameter
    ←─────────────────────→
    ┌───────────────────────┐  ↑
    │                       │  │
    │     ┌─────────┐      │  │ domain_y
    │     │  leito  │      │  │
    │     └─────────┘      │  │
    │                       │  ↓
    └───────────────────────┘
    
vista lateral:
    
    ↑ domain_z = 1.5 × height
    │  ┌─┐
    │  │ │ ← leito
    │  │ │
    │  └─┘
    └──────→
```

**níveis de refinamento**:

```
região          | células      | uso
----------------|--------------|------------------
base (level 0)  | 40×40×80     | longe do leito
refinamento 1   | 2× base      | região média
refinamento 2   | 4× base      | próximo ao leito
refinamento 3   | 8× base      | superfície do leito
```

---

### 6. _generate_blockmesh_dict()

**função**: template do blockMeshDict

```python
def _generate_blockmesh_dict(self, dx, dy, dz, nx, ny, nz) -> str:
    """
    gerar conteúdo do blockMeshDict
    
    parâmetros:
        dx, dy, dz: dimensões do domínio [m]
        nx, ny, nz: número de células
    
    retorna:
        string com conteúdo do arquivo
    
    estrutura:
        - 8 vértices definindo cubo
        - 1 bloco hexaédrico
        - patches: walls (todas as faces)
    """
    
    # coordenadas dos vértices
    x0, x1 = -dx/2, dx/2
    y0, y1 = -dy/2, dy/2
    z0, z1 = 0, dz
    
    content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

vertices
(
    ({x0} {y0} {z0})    // 0
    ({x1} {y0} {z0})    // 1
    ({x1} {y1} {z0})    // 2
    ({x0} {y1} {z0})    // 3
    ({x0} {y0} {z1})    // 4
    ({x1} {y0} {z1})    // 5
    ({x1} {y1} {z1})    // 6
    ({x0} {y1} {z1})    // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    walls
    {{
        type wall;
        faces
        (
            (0 3 2 1)  // bottom
            (4 5 6 7)  // top
            (0 1 5 4)  // front
            (2 3 7 6)  // back
            (0 4 7 3)  // left
            (1 2 6 5)  // right
        );
    }}
);

mergePatchPairs
(
);

// ************************************************************************* //
"""
    
    return content
```

---

### 7. _generate_snappy_dict()

**função**: template do snappyHexMeshDict

```python
def _generate_snappy_dict(self, diameter, height) -> str:
    """
    gerar conteúdo do snappyHexMeshDict
    
    parâmetros:
        diameter: diâmetro do leito [m]
        height: altura do leito [m]
    
    retorna:
        string com conteúdo do arquivo
    
    configuração:
        - castellated: true (refinar)
        - snap: true (ajustar à superfície)
        - addLayers: false (sem boundary layers)
        - refinamento: level (2 3) = 4x a 8x
        - locationInMesh: ponto dentro do domínio
    """
    
    # ponto dentro do domínio (para detectar região interna)
    location_x = 0
    location_y = 0
    location_z = height * 0.5  # meio do leito
    
    content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

castellatedMesh true;
snap            true;
addLayers       false;

geometry
{{
    leito.stl
    {{
        type triSurfaceMesh;
        name leito;
    }}
}}

castellatedMeshControls
{{
    maxLocalCells           1000000;
    maxGlobalCells          2000000;
    minRefinementCells      0;
    nCellsBetweenLevels     3;
    
    features
    (
    );
    
    refinementSurfaces
    {{
        leito
        {{
            level (2 3);
        }}
    }}
    
    refinementRegions
    {{
    }}
    
    locationInMesh ({location_x} {location_y} {location_z});
}}

snapControls
{{
    nSmoothPatch            3;
    tolerance               2.0;
    nSolveIter              30;
    nRelaxIter              5;
}}

addLayersControls
{{
    relativeSizes           true;
    layers
    {{
    }}
    expansionRatio          1.0;
    finalLayerThickness     0.3;
    minThickness            0.1;
}}

meshQualityControls
{{
    maxNonOrtho             65;
    maxBoundarySkewness     20;
    maxInternalSkewness     4;
    maxConcave              80;
    minVol                  1e-13;
    minTetQuality           1e-15;
    minArea                 -1;
    minTwist                0.02;
    minDeterminant          0.001;
    minFaceWeight           0.02;
    minVolRatio             0.01;
}}

// ************************************************************************* //
"""
    
    return content
```

---

### 8. create_control_dicts()

**função**: gera controlDict, fvSchemes, fvSolution

```python
def create_control_dicts(self) -> None:
    """
    gerar dicionários de controle da simulação
    
    gera três arquivos:
        1. system/controlDict: controle geral
        2. system/fvSchemes: esquemas numéricos
        3. system/fvSolution: solvers e tolerâncias
    
    parâmetros extraídos do json:
        - regime: "laminar" ou "turbulent"
        - max_iterations: número de iterações
        - convergence_criteria: tolerância de convergência
    
    fundamentação:
    - ferziger (2002): esquemas numéricos
    - openfoam guide: solver configuration
    """
    
    print(f"\n[6/8] gerando dicionarios de controle")
    
    # extrair parâmetros cfd
    cfd = self.params.get('cfd', {})
    regime = cfd.get('regime', 'laminar')
    max_iter = cfd.get('max_iterations', 1000)
    convergence = cfd.get('convergence_criteria', 1e-4)
    
    # 1. controlDict
    control_content = self._generate_control_dict(max_iter)
    control_path = self.case_dir / "system" / "controlDict"
    with open(control_path, 'w') as f:
        f.write(control_content)
    print(f"  [OK] controlDict criado")
    
    # 2. fvSchemes
    schemes_content = self._generate_fvschemes()
    schemes_path = self.case_dir / "system" / "fvSchemes"
    with open(schemes_path, 'w') as f:
        f.write(schemes_content)
    print(f"  [OK] fvSchemes criado")
    
    # 3. fvSolution
    solution_content = self._generate_fvsolution(convergence)
    solution_path = self.case_dir / "system" / "fvSolution"
    with open(solution_path, 'w') as f:
        f.write(solution_content)
    print(f"  [OK] fvSolution criado")
```

---

### 9. create_initial_conditions()

**função**: gera arquivos 0/U, 0/p e transportProperties

```python
def create_initial_conditions(self) -> None:
    """
    gerar condições iniciais e de contorno
    
    gera três arquivos:
        1. 0/U: campo de velocidade
        2. 0/p: campo de pressão
        3. constant/transportProperties: propriedades do fluido
    
    parâmetros usados:
        - inlet_velocity: velocidade na entrada [m/s]
        - fluid_density: densidade [kg/m³]
        - fluid_viscosity: viscosidade dinâmica [Pa·s]
    
    cálculos:
        - viscosidade cinemática: ν = μ / ρ
        - pressão inicial: p = 0 (referência)
        - velocidade inicial: U = (0 0 inlet_velocity)
    """
    
    print(f"\n[7/8] criando condicoes iniciais")
    
    # extrair parâmetros
    cfd = self.params['cfd']
    velocity = cfd['inlet_velocity']
    density = cfd['fluid_density']
    viscosity = cfd['fluid_viscosity']
    
    # calcular viscosidade cinemática
    nu = viscosity / density
    
    print(f"  - fluido: ρ={density} kg/m³, μ={viscosity} Pa·s")
    print(f"  - viscosidade cinematica: ν={nu:.2e} m²/s")
    print(f"  - velocidade entrada: {velocity} m/s")
    
    # 1. arquivo 0/U
    u_content = self._generate_u_field(velocity)
    u_path = self.case_dir / "0" / "U"
    with open(u_path, 'w') as f:
        f.write(u_content)
    print(f"  [OK] 0/U criado")
    
    # 2. arquivo 0/p
    p_content = self._generate_p_field()
    p_path = self.case_dir / "0" / "p"
    with open(p_path, 'w') as f:
        f.write(p_content)
    print(f"  [OK] 0/p criado")
    
    # 3. transportProperties
    transport_content = self._generate_transport_properties(nu)
    transport_path = self.case_dir / "constant" / "transportProperties"
    with open(transport_path, 'w') as f:
        f.write(transport_content)
    print(f"  [OK] transportProperties criado")
```

**condições de contorno típicas**:

| patch | tipo U | valor U | tipo p | valor p |
|-------|--------|---------|--------|---------|
| leito | noSlip | (0 0 0) | zeroGradient | - |
| walls | noSlip | (0 0 0) | zeroGradient | - |
| inlet | fixedValue | (0 0 v) | zeroGradient | - |
| outlet | zeroGradient | - | fixedValue | 0 |

---

### 10. create_run_script()

**função**: gera script Allrun para executar simulação

```python
def create_run_script(self, execute_simulation: bool = False) -> None:
    """
    criar script allrun para executar pipeline
    
    script gerado executa sequencialmente:
        1. blockMesh: malha de fundo
        2. snappyHexMesh: refinamento
        3. checkMesh: validação
        4. simpleFoam: solver (se execute_simulation=True)
    
    parâmetro:
        execute_simulation: se True, executa simpleFoam
                           se False, apenas prepara caso
    
    formato:
        bash script com tratamento de erros
        logs salvos em: log.blockMesh, log.snappyHexMesh, etc
    """
    
    print(f"\n[8/8] criando script de execucao")
    
    allrun_content = """#!/bin/sh
cd "${0%/*}" || exit 1

# source openfoam
source /opt/openfoam11/etc/bashrc

echo "========================================="
echo " executando caso openfoam"
echo "========================================="

# 1. blockMesh
echo "1. gerando malha de fundo (blockMesh)..."
blockMesh > log.blockMesh 2>&1
if [ $? -ne 0 ]; then
    echo "erro no blockMesh! veja log.blockMesh"
    exit 1
fi
echo "   [OK] malha de fundo criada"

# 2. snappyHexMesh
echo "2. gerando malha refinada (snappyHexMesh)..."
snappyHexMesh -overwrite > log.snappyHexMesh 2>&1
if [ $? -ne 0 ]; then
    echo "erro no snappyHexMesh! veja log.snappyHexMesh"
    exit 1
fi
echo "   [OK] malha refinada criada"

# 3. checkMesh
echo "3. verificando qualidade da malha..."
checkMesh > log.checkMesh 2>&1
echo "   (veja log.checkMesh para detalhes)"
"""
    
    if execute_simulation:
        allrun_content += """
# 4. simpleFoam
echo "4. executando simulacao (simpleFoam)..."
simpleFoam > log.simpleFoam 2>&1 &
FOAM_PID=$!

# monitorar convergência
while kill -0 $FOAM_PID 2>/dev/null; do
    if [ -f log.simpleFoam ]; then
        LAST_TIME=$(grep "^Time = " log.simpleFoam | tail -1)
        printf "\\r   %s" "$LAST_TIME"
    fi
    sleep 2
done
wait $FOAM_PID

echo ""
echo "   [OK] simulacao concluida!"

# criar arquivo .foam para paraview
touch caso.foam
"""
    
    allrun_content += """
echo "========================================="
echo " caso preparado com sucesso!"
echo "========================================="
exit 0
"""
    
    allrun_path = self.case_dir / "Allrun"
    with open(allrun_path, 'w') as f:
        f.write(allrun_content)
    
    # tornar executável (linux/mac)
    try:
        allrun_path.chmod(0o755)
    except:
        pass  # windows não suporta chmod
    
    print(f"  [OK] Allrun criado")
```

---

### 11. run()

**função**: método principal que orquestra tudo

```python
def run(self, blend_file: Path = None, execute_simulation: bool = False):
    """
    executar pipeline completo
    
    workflow:
        1. carregar parâmetros (já feito no __init__)
        2. exportar stl do blender (opcional)
        3. criar estrutura de diretórios
        4. copiar stl para triSurface
        5. gerar dicionários de malha
        6. gerar dicionários de controle
        7. gerar condições iniciais
        8. criar script allrun
        9. executar simulação (opcional)
    
    parâmetros:
        blend_file: arquivo .blend (se None, assume stl já existe)
        execute_simulation: se True, executa simpleFoam
    
    retorna:
        caminho do caso gerado
    """
    
    try:
        print("\n" + "="*60)
        print(" CFD-PIPELINE: SETUP OPENFOAM CASE")
        print("="*60)
        
        # 1. exportar stl (se blend_file fornecido)
        if blend_file:
            stl_path = self.export_stl_from_blender(blend_file)
        else:
            stl_path = self.output_dir / f"{self.case_name}.stl"
            if not stl_path.exists():
                raise FileNotFoundError("STL não encontrado e blend_file não fornecido")
        
        # 2. criar estrutura
        self.create_case_structure()
        
        # 3. copiar stl
        self.copy_stl_to_case(stl_path)
        
        # 4. gerar dicionários de malha
        self.create_mesh_dict()
        
        # 5. gerar dicionários de controle
        self.create_control_dicts()
        
        # 6. gerar condições iniciais
        self.create_initial_conditions()
        
        # 7. criar script allrun
        self.create_run_script(execute_simulation)
        
        print("\n" + "="*60)
        print(" CASO OPENFOAM CRIADO COM SUCESSO!")
        print("="*60)
        print(f"\ncaso: {self.case_dir}")
        print("\nproximoscontinuar...")
    
    except Exception as e:
        print(f"\n[ERRO] falha ao criar caso: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    return self.case_dir
```

---

## 🚀 uso do script

### exemplo básico

```python
from pathlib import Path
from setup_openfoam_case import OpenFOAMCaseGenerator

# caminhos
bed_json = Path("output/dsl/leito01.bed.json")
blend_file = Path("output/models/leito01.blend")
output_dir = Path("output/cfd")

# criar gerador
generator = OpenFOAMCaseGenerator(bed_json, output_dir)

# executar pipeline (sem simulação)
case_dir = generator.run(blend_file=blend_file, execute_simulation=False)

print(f"caso criado em: {case_dir}")
```

### executar com simulação

```python
# executar pipeline completo (incluindo simulação)
case_dir = generator.run(blend_file=blend_file, execute_simulation=True)

# aguardar conclusão
print("simulação concluída!")
print(f"visualizar: paraview {case_dir}/caso.foam")
```

### via linha de comando

```bash
python setup_openfoam_case.py \
    --params output/dsl/leito01.bed.json \
    --blend output/models/leito01.blend \
    --output output/cfd \
    --run  # opcional: executar simulação
```

---

## 📊 fluxo completo integrado

```
.bed file
    ↓
antlr compiler
    ↓
.bed.json ──────────────┐
    ↓                    │
bed_wizard.py           │
    ↓                    │
blender headless        │
    ↓                    │
.blend file             │
    ↓                    │
export stl              │
    ↓                    │
.stl file               │
    ↓                    │
setup_openfoam_case.py ←┘
    ↓
openfoam case
    ├── blockMesh
    ├── snappyHexMesh
    ├── checkMesh
    └── simpleFoam
        ↓
    resultados
        ├── campos U, p
        ├── caso.foam
        └── logs
```

---

## 🔧 troubleshooting

### erros comuns

| erro | causa | solução |
|------|-------|---------|
| `blender: command not found` | blender não no PATH | adicionar ao PATH ou usar caminho absoluto |
| `KeyError: 'cfd'` | json incompleto | verificar estrutura do .bed.json |
| `snappyHexMesh failed` | stl ruim | verificar geometria no blender |
| `cells with negative volume` | malha ruim | ajustar locationInMesh |

### dicas de performance

1. **começar com malha grosseira**: nx=20, ny=20, nz=40 (teste)
2. **refinamento gradual**: level (1 2) primeiro, depois (2 3)
3. **monitorar memória**: 2000000 células ≈ 4 GB RAM
4. **paralelização**: decomposePar para múltiplos cores

---

## 📚 referências

- openfoam foundation (2025). openfoam user guide. https://www.openfoam.com/documentation/
- ferziger, j. h., & perić, m. (2002). computational methods for fluid dynamics. springer.
- moukalled, f., mangani, l., & darwish, m. (2016). the finite volume method in cfd. springer.

---

**última atualização**: 9 outubro 2025  
**versão**: 1.0

