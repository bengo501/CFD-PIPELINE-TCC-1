# diagramas uml completos do projeto cfd-pipeline-tcc

este documento contem todos os diagramas uml do projeto, incluindo classes, componentes, sequencia, estados e fluxo de dados.

## indice

1. [diagrama geral de componentes](#1-diagrama-geral-de-componentes)
2. [diagrama de classes - dsl](#2-diagrama-de-classes---dsl)
3. [diagrama de classes - blender](#3-diagrama-de-classes---blender)
4. [diagrama de classes - openfoam](#4-diagrama-de-classes---openfoam)
5. [diagrama de sequencia - fluxo completo](#5-diagrama-de-sequencia---fluxo-completo)
6. [diagrama de estados - pipeline](#6-diagrama-de-estados---pipeline)
7. [diagrama entidade-relacionamento](#7-diagrama-entidade-relacionamento---parametros)
8. [diagrama de dependencias](#8-diagrama-de-dependencias-entre-arquivos)
9. [diagrama de fluxo de dados](#9-diagrama-de-fluxo-de-dados)
10. [diagrama detalhado - bed_wizard](#10-diagrama-de-classes-detalhado---bed_wizard)
11. [metricas das classes](#11-diagrama-de-metricas-das-classes)
12. [glossario de tipos](#12-glossario-de-tipos)

---

## 1. diagrama geral de componentes

```mermaid
graph TB
    subgraph "camada de interface"
        A[bed_wizard.py<br/>interface usuario]
    end
    
    subgraph "camada dsl"
        B[Bed.g4<br/>gramatica antlr]
        C[bed_compiler_antlr_standalone.py<br/>compilador]
        D[BedParameters<br/>dataclasses]
    end
    
    subgraph "camada geometria"
        E[leito_extracao.py<br/>script blender]
        F[executar_leito_headless.py<br/>executor blender]
    end
    
    subgraph "camada cfd"
        G[setup_openfoam_case.py<br/>gerador caso openfoam]
        H[OpenFOAMCaseGenerator<br/>classe principal]
    end
    
    subgraph "camada dados"
        I[.bed files<br/>entrada usuario]
        J[.bed.json<br/>parametros normalizados]
        K[.blend files<br/>modelos 3d]
        L[.stl files<br/>geometria exportada]
        M[caso openfoam<br/>diretorios + configs]
    end
    
    A -->|cria/edita| I
    I -->|compilado por| C
    B -->|define sintaxe| C
    C -->|gera| J
    C -->|usa| D
    
    J -->|lido por| E
    F -->|executa| E
    E -->|gera| K
    
    J -->|lido por| G
    K -->|processado por| G
    G -->|usa| H
    G -->|exporta| L
    G -->|cria| M
    
    style A fill:#e1f5ff
    style C fill:#fff4e1
    style E fill:#e8f5e9
    style G fill:#fce4ec
```

---

## 2. diagrama de classes - dsl

### 2.1 classes de parametros (dataclasses)

```mermaid
classDiagram
    class BedParameters {
        +BedGeometry bed
        +LidsConfig lids
        +ParticlesConfig particles
        +PackingConfig packing
        +ExportConfig export
        +CFDConfig cfd
    }
    
    class BedGeometry {
        +float diameter
        +float height
        +float wall_thickness
        +str shape
        +to_dict() dict
    }
    
    class LidsConfig {
        +str top_type
        +str bottom_type
        +float thickness
        +bool has_inlet
        +bool has_outlet
        +to_dict() dict
    }
    
    class ParticlesConfig {
        +int count
        +str kind
        +float diameter
        +float mass
        +float friction
        +float restitution
        +to_dict() dict
    }
    
    class PackingConfig {
        +str method
        +int seed
        +int substeps
        +int iterations
        +float gravity_x
        +float gravity_y
        +float gravity_z
        +to_dict() dict
    }
    
    class ExportConfig {
        +list~str~ formats
        +str output_dir
        +bool save_packing_data
        +to_dict() dict
    }
    
    class CFDConfig {
        +str regime
        +float inlet_velocity
        +float outlet_pressure
        +float fluid_density
        +float fluid_viscosity
        +int max_iterations
        +float convergence_criteria
        +str turbulence_model
        +to_dict() dict
    }
    
    BedParameters "1" --> "1" BedGeometry
    BedParameters "1" --> "1" LidsConfig
    BedParameters "1" --> "1" ParticlesConfig
    BedParameters "1" --> "1" PackingConfig
    BedParameters "1" --> "1" ExportConfig
    BedParameters "1" --> "1" CFDConfig
```

### 2.2 classes do compilador

```mermaid
classDiagram
    class BedCompilerListener {
        -BedParameters params
        -dict current_section
        
        +__init__(params)
        +exitBedSection(ctx)
        +exitLidsSection(ctx)
        +exitParticlesSection(ctx)
        +exitPackingSection(ctx)
        +exitExportSection(ctx)
        +exitCfdSection(ctx)
        +_extract_number_with_unit(text) float
        +_extract_string_value(ctx) str
    }
    
    class BedErrorListener {
        -list errors
        
        +syntaxError(recognizer, offendingSymbol, line, column, msg, e)
        +has_errors() bool
        +get_errors() list
    }
    
    class BedWizard {
        -str mode
        -str output_file
        -Path compiler_path
        -dict param_help
        
        +run()
        +interactive_mode()
        +blender_mode()
        +edit_mode()
        +show_help_menu()
        +get_number_input(prompt, default, param_key) float
        +compile_bed_file(bed_file) tuple
        +execute_blender(open_after) tuple
    }
    
    BedCompilerListener ..> BedParameters : usa
    BedWizard ..> BedCompilerListener : invoca
```

---

## 3. diagrama de classes - blender

```mermaid
classDiagram
    class BlenderScript {
        <<leito_extracao.py>>
        
        +limpar_cena()
        +criar_cilindro_oco(altura, diametro, espessura, nome) Object
        +criar_tampa(posicao_z, diametro, espessura, nome) Object
        +criar_particulas(quantidade, raio_leito, altura_leito, raio_particula) list
        +aplicar_fisica(obj, tipo, massa, friccao, restituicao)
        +configurar_simulacao_fisica(gravidade, substeps, iteracoes)
        +ler_parametros_json(json_path) dict
        +main_com_parametros()
    }
    
    class BlenderExecutor {
        <<executar_leito_headless.py>>
        
        +encontrar_blender() Path
        +executar_blender_headless(script_path, json_path, output_dir) int
        +main()
    }
    
    class BlenderObject {
        <<bpy.types.Object>>
        +str name
        +Vector location
        +Vector rotation_euler
        +Vector scale
        +Mesh data
        +RigidBodySettings rigid_body
    }
    
    class RigidBodySettings {
        <<bpy.types.RigidBodySettings>>
        +str type
        +float mass
        +float friction
        +float restitution
        +bool enabled
    }
    
    class Scene {
        <<bpy.types.Scene>>
        +Collection collection
        +RigidBodyWorld rigidbody_world
        +int frame_start
        +int frame_end
    }
    
    BlenderScript ..> BlenderObject : cria
    BlenderScript ..> Scene : modifica
    BlenderObject "1" --> "0..1" RigidBodySettings
    BlenderExecutor ..> BlenderScript : executa
```

---

## 4. diagrama de classes - openfoam

```mermaid
classDiagram
    class OpenFOAMCaseGenerator {
        -Path bed_json_path
        -Path output_dir
        -str case_name
        -Path case_dir
        -dict params
        
        +__init__(bed_json_path, output_dir)
        +_load_params() dict
        +export_stl_from_blender(blend_file) Path
        +create_case_structure()
        +copy_stl_to_case(stl_path)
        +create_mesh_dict()
        +create_control_dicts()
        +create_initial_conditions()
        +create_run_script()
        +run(blend_file, execute_simulation) bool
        +execute_simulation()
    }
    
    class OpenFOAMCase {
        <<estrutura diretorios>>
        +Path case_root
        +Path zero_dir
        +Path constant_dir
        +Path system_dir
    }
    
    class MeshConfiguration {
        +tuple domain_min
        +tuple domain_max
        +tuple cells
        +int refinement_level
    }
    
    class SimulationConfiguration {
        +str solver
        +float end_time
        +float delta_t
        +dict schemes
        +dict solution_methods
    }
    
    class BoundaryConditions {
        +dict inlet
        +dict outlet
        +dict walls
    }
    
    OpenFOAMCaseGenerator "1" --> "1" OpenFOAMCase : cria
    OpenFOAMCaseGenerator ..> MeshConfiguration : usa
    OpenFOAMCaseGenerator ..> SimulationConfiguration : usa
    OpenFOAMCaseGenerator ..> BoundaryConditions : configura
```

---

## 5. diagrama de sequencia - fluxo completo

```mermaid
sequenceDiagram
    actor Usuario
    participant Wizard as BedWizard
    participant Compiler as BedCompiler
    participant Blender as BlenderScript
    participant OpenFOAM as OpenFOAMGenerator
    participant WSL as WSL2
    
    Usuario->>Wizard: executar bed_wizard.py
    Wizard->>Usuario: mostrar menu
    
    alt modo interativo
        Usuario->>Wizard: escolher opcao 1
        loop para cada parametro
            Wizard->>Usuario: solicitar valor
            Usuario->>Wizard: fornecer valor
        end
    else modo edicao
        Usuario->>Wizard: escolher opcao 2
        Wizard->>Usuario: abrir editor
        Usuario->>Wizard: editar e salvar
    end
    
    Wizard->>Compiler: compilar .bed
    Compiler->>Compiler: parse antlr
    Compiler->>Compiler: validar
    Compiler->>Wizard: retornar .bed.json
    
    opt gerar modelo 3d
        Wizard->>Blender: executar headless
        Blender->>Blender: ler json
        Blender->>Blender: criar geometria
        Blender->>Blender: aplicar fisica
        Blender->>Blender: simular
        Blender->>Wizard: salvar .blend
    end
    
    opt executar cfd
        Usuario->>OpenFOAM: executar setup_openfoam_case.py
        OpenFOAM->>Blender: exportar stl
        OpenFOAM->>OpenFOAM: criar caso
        OpenFOAM->>OpenFOAM: configurar
        
        opt --run
            OpenFOAM->>WSL: invocar allrun
            WSL->>WSL: blockmesh
            WSL->>WSL: snappyhexmesh
            WSL->>WSL: simplefoam
            WSL->>OpenFOAM: resultados
        end
    end
```

---

## 6. diagrama de estados - pipeline

```mermaid
stateDiagram-v2
    [*] --> Inicial
    
    Inicial --> DefiniParametros : usuario inicia wizard
    
    DefiniParametros --> EdicaoInterativa : modo 1
    DefiniParametros --> EdicaoManual : modo 2
    DefiniParametros --> ModoBlender : modo 3
    
    EdicaoInterativa --> ArquivoBed : responder questoes
    EdicaoManual --> ArquivoBed : editar arquivo
    ModoBlender --> ArquivoBed : definir geometria
    
    ArquivoBed --> Compilacao : salvar .bed
    
    Compilacao --> ValidacaoSintaxe : invocar antlr
    ValidacaoSintaxe --> ErroSintaxe : sintaxe invalida
    ValidacaoSintaxe --> ConversaoUnidades : sintaxe valida
    
    ErroSintaxe --> DefiniParametros : corrigir
    
    ConversaoUnidades --> GeracaoJson : normalizar SI
    GeracaoJson --> JsonGerado : salvar .bed.json
    
    JsonGerado --> GeracaoModelo3D : modo blender
    JsonGerado --> AguardandoAcao : modo interativo
    
    GeracaoModelo3D --> ExecutarBlender
    ExecutarBlender --> LimparCena
    LimparCena --> CriarLeito
    CriarLeito --> CriarParticulas
    CriarParticulas --> AplicarFisica
    AplicarFisica --> SimularEmpacotamento
    SimularEmpacotamento --> SalvarBlend
    
    SalvarBlend --> ModeloGerado
    ModeloGerado --> AguardandoAcao
    
    AguardandoAcao --> ConfigurarCFD : executar setup_openfoam_case.py
    
    ConfigurarCFD --> ExportarSTL
    ExportarSTL --> CriarEstruturaCaso
    CriarEstruturaCaso --> ConfigurarSolver
    ConfigurarSolver --> CasoConfigurado
    
    CasoConfigurado --> ExecutarSimulacao : --run
    CasoConfigurado --> Finalizado : sem --run
    
    ExecutarSimulacao --> ExecutarBlockMesh
    ExecutarBlockMesh --> ExecutarSnappyHexMesh
    ExecutarSnappyHexMesh --> ExecutarSimpleFoam
    ExecutarSimpleFoam --> SimulacaoCompleta : convergiu
    ExecutarSimpleFoam --> ErroSimulacao : divergiu
    
    SimulacaoCompleta --> Finalizado
    ErroSimulacao --> ConfigurarCFD : ajustar
    
    Finalizado --> [*]
```

---

## 7. diagrama entidade-relacionamento - parametros

```mermaid
erDiagram
    BED_FILE ||--|| BED_PARAMETERS : compila_para
    BED_PARAMETERS ||--|| BED_GEOMETRY : contem
    BED_PARAMETERS ||--|| LIDS_CONFIG : contem
    BED_PARAMETERS ||--|| PARTICLES_CONFIG : contem
    BED_PARAMETERS ||--|| PACKING_CONFIG : contem
    BED_PARAMETERS ||--|| EXPORT_CONFIG : contem
    BED_PARAMETERS ||--|| CFD_CONFIG : contem
    
    BED_FILE {
        string filename
        string content
        datetime created_at
    }
    
    BED_GEOMETRY {
        float diameter
        float height
        float wall_thickness
        string shape
    }
    
    LIDS_CONFIG {
        string top_type
        string bottom_type
        float thickness
        bool has_inlet
    }
    
    PARTICLES_CONFIG {
        int count
        string kind
        float diameter
        float mass
    }
    
    PACKING_CONFIG {
        string method
        int seed
        int substeps
        float gravity_z
    }
    
    EXPORT_CONFIG {
        string formats
        string output_dir
    }
    
    CFD_CONFIG {
        string regime
        float inlet_velocity
        float fluid_density
        float fluid_viscosity
    }
    
    BED_PARAMETERS ||--o{ BLENDER_MODEL : gera
    BLENDER_MODEL ||--|| STL_FILE : exporta
    BED_PARAMETERS ||--o{ OPENFOAM_CASE : configura
    STL_FILE ||--|| OPENFOAM_CASE : usado_em
    OPENFOAM_CASE ||--o{ SIMULATION_RESULTS : produz
    
    BLENDER_MODEL {
        string filename
        datetime created_at
        int particle_count
    }
    
    STL_FILE {
        string filename
        float file_size
        int triangle_count
    }
    
    OPENFOAM_CASE {
        string case_name
        string case_directory
        string solver
    }
    
    SIMULATION_RESULTS {
        string result_directory
        datetime completed_at
        bool converged
    }
```

---

## 8. diagrama de dependencias entre arquivos

```mermaid
graph LR
    subgraph "entrada"
        A[usuario]
    end
    
    subgraph "dsl"
        B[bed_wizard.py]
        C[Bed.g4]
        D[bed_compiler_antlr_standalone.py]
        E[BedLexer.py]
        F[BedParser.py]
    end
    
    subgraph "intermediarios"
        H[*.bed]
        I[*.bed.json]
    end
    
    subgraph "blender"
        J[leito_extracao.py]
        K[executar_leito_headless.py]
    end
    
    subgraph "saida blender"
        L[*.blend]
        M[*.stl]
    end
    
    subgraph "openfoam"
        N[setup_openfoam_case.py]
        O[caso openfoam]
    end
    
    subgraph "wsl"
        P[blockMesh]
        Q[snappyHexMesh]
        R[simpleFoam]
    end
    
    A -->|interage| B
    B -->|cria| H
    C -->|gera| E
    C -->|gera| F
    D -->|usa| E
    D -->|usa| F
    B -->|invoca| D
    D -->|compila| H
    H -->|transforma| I
    
    I -->|entrada| J
    K -->|executa| J
    J -->|gera| L
    
    I -->|entrada| N
    L -->|entrada| N
    N -->|exporta| M
    N -->|cria| O
    
    O -->|executado| P
    P -->|pipe| Q
    Q -->|pipe| R
    
    style A fill:#e1f5ff
    style I fill:#fff4e1
    style L fill:#e8f5e9
    style O fill:#fce4ec
```

---

## 9. diagrama de fluxo de dados

```mermaid
flowchart TD
    A[usuario define parametros] --> B{metodo entrada}
    
    B -->|interativo| C[responder questoes]
    B -->|manual| D[editar .bed]
    B -->|blender| E[definir geometria]
    
    C --> F[arquivo .bed]
    D --> F
    E --> F
    
    F --> G[compilador antlr]
    
    G --> H{validacao}
    H -->|erro| I[mostrar erros]
    I --> A
    
    H -->|ok| J[converter unidades]
    J --> K[arquivo .bed.json]
    
    K --> L{proxima acao}
    
    L -->|gerar 3d| M[blender headless]
    L -->|aguardar| N[fim dsl]
    
    M --> O[criar geometria]
    O --> P[aplicar fisica]
    P --> Q[salvar .blend]
    
    Q --> R{executar cfd?}
    N --> R
    
    R -->|nao| S[fim]
    R -->|sim| T[setup openfoam]
    
    T --> U[exportar stl]
    U --> V[criar caso]
    V --> W[configurar]
    
    W --> X{--run?}
    
    X -->|nao| Y[caso configurado]
    X -->|sim| Z[invocar wsl]
    
    Z --> AA[mesh]
    AA --> AB[solve]
    AB --> AC[resultados]
    
    Y --> S
    AC --> S
    
    style F fill:#fff4e1
    style K fill:#fff4e1
    style Q fill:#e8f5e9
    style Y fill:#fce4ec
```

---

## 10. diagrama de classes detalhado - bed_wizard

```mermaid
classDiagram
    class BedWizard {
        -str mode
        -str output_file
        -Path compiler_path
        -dict param_help
        -dict bed_params
        -dict lids_params
        -dict particles_params
        -dict packing_params
        -dict export_params
        -dict cfd_params
        
        +run()
        +interactive_mode()
        +blender_mode()
        +blender_interactive_mode()
        +edit_mode()
        +show_help_menu()
        +show_documentation()
        +get_number_input(prompt, default, param_key) float
        +show_param_help(param_key)
        +compile_bed_file(bed_file) tuple
        +execute_blender(open_after) tuple
        +open_blender_with_file(blender_exe, blend_file)
    }
```

---

## 11. diagrama de metricas das classes

```mermaid
graph TD
    A[BedWizard<br/>1388 linhas<br/>25 metodos]
    B[BedCompilerListener<br/>350 linhas<br/>15 metodos]
    C[BlenderScript<br/>500 linhas<br/>8 funcoes]
    D[OpenFOAMCaseGenerator<br/>890 linhas<br/>12 metodos]
    
    style A fill:#ff6b6b
    style B fill:#ffd93d
    style C fill:#ffd93d
    style D fill:#ff6b6b
```

---

## 12. glossario de tipos

| tipo | descricao | exemplo |
|------|-----------|---------|
| `Path` | caminho arquivo pathlib | `Path("dsl/leito.bed")` |
| `dict` | dicionario python | `{"diameter": 0.05}` |
| `list` | lista python | `["blend", "stl"]` |
| `str` | string | `"cylinder"` |
| `float` | numero decimal | `0.05` |
| `int` | numero inteiro | `100` |
| `bool` | booleano | `True` / `False` |
| `tuple` | tupla imutavel | `(0.0, 0.0, -9.81)` |
| `Object` | objeto blender | `bpy.types.Object` |

---

## resumo de relacionamentos

### composicao
- `BedParameters` compoe 6 dataclasses
- `OpenFOAMCase` compoe 3 diretorios principais

### uso
- `BedWizard` usa `BedCompilerListener`
- `BlenderScript` usa `bpy`
- `OpenFOAMCaseGenerator` usa parametros json

### invocacao
- `BedWizard` invoca compilador
- `BedWizard` invoca blender headless
- `setup_openfoam_case.py` invoca blender para stl
- `Allrun` invoca comandos openfoam

### transformacao
- `.bed` → `.bed.json` (compilador)
- `.bed.json` → `.blend` (blender)
- `.blend` → `.stl` (exportacao)
- `.stl` → malha (snappyhexmesh)
- malha → resultados (simplefoam)
