# diagramas uml do projeto cfd-pipeline-tcc-1

## visão geral

este documento contém os diagramas uml (unified modeling language) de todas as classes e entidades do projeto, incluindo relacionamentos, atributos e métodos.

---

## 1. diagrama de classes principal

### 1.1 classe BedWizard

```mermaid
classDiagram
    class BedWizard {
        -dict params
        -str output_file
        -dict param_help
        
        +__init__()
        +clear_screen()
        +print_header(title: str)
        +print_section(title: str)
        +show_param_help(param_key: str)
        +get_input(prompt: str, default: str, required: bool) str
        +get_number_input(prompt: str, default: str, unit: str, required: bool, param_key: str) str
        +get_choice(prompt: str, options: List, default: int) str
        +get_boolean(prompt: str, default: bool) bool
        +get_list_input(prompt: str, separator: str) List
        +interactive_mode()
        +template_mode()
        +blender_mode()
        +blender_interactive_mode()
        +confirm_and_save()
        +confirm_and_generate_blender()
        +confirm_and_generate_blender_interactive()
        +save_bed_file()
        +generate_bed_content() str
        +verify_and_compile() bool
        +execute_blender(open_after: bool) tuple
        +open_blender_with_file(blender_exe: str, blend_file: Path)
        +create_default_template() str
        +show_help_menu()
        +show_documentation()
        +run()
    }
```

### 1.2 classe BedCompilerListener

```mermaid
classDiagram
    class BedCompilerListener {
        -BedParameters params
        -list errors
        
        +__init__()
        +_parse_number_with_unit(number: str, unit: str) float
        +exitBedDiameter(ctx)
        +exitBedHeight(ctx)
        +exitBedWallThickness(ctx)
        +exitBedClearance(ctx)
        +exitBedMaterial(ctx)
        +exitBedRoughness(ctx)
        +exitLidsTopType(ctx)
        +exitLidsBottomType(ctx)
        +exitLidsTopThickness(ctx)
        +exitLidsBottomThickness(ctx)
        +exitLidsSealClearance(ctx)
        +exitParticlesKind(ctx)
        +exitParticlesDiameter(ctx)
        +exitParticlesCount(ctx)
        +exitParticlesTargetPorosity(ctx)
        +exitParticlesDensity(ctx)
        +exitParticlesMass(ctx)
        +exitParticlesRestitution(ctx)
        +exitParticlesFriction(ctx)
        +exitParticlesRollingFriction(ctx)
        +exitParticlesLinearDamping(ctx)
        +exitParticlesAngularDamping(ctx)
        +exitParticlesSeed(ctx)
        +exitPackingMethodProp(ctx)
        +exitPackingGravity(ctx)
        +exitPackingSubsteps(ctx)
        +exitPackingIterations(ctx)
        +exitPackingDamping(ctx)
        +exitPackingRestVelocity(ctx)
        +exitPackingMaxTime(ctx)
        +exitPackingCollisionMargin(ctx)
        +exitExportFormats(ctx)
        +exitExportUnits(ctx)
        +exitExportScale(ctx)
        +exitExportWallMode(ctx)
        +exitExportFluidMode(ctx)
        +exitExportManifoldCheck(ctx)
        +exitExportMergeDistance(ctx)
        +exitCfdRegimeProp(ctx)
        +exitCfdInletVelocity(ctx)
        +exitCfdFluidDensity(ctx)
        +exitCfdFluidViscosity(ctx)
        +exitCfdMaxIterations(ctx)
        +exitCfdConvergenceCriteria(ctx)
        +exitCfdWriteFields(ctx)
    }
    
    BedCompilerListener --> BedParameters : usa
```

### 1.3 classe BedErrorListener

```mermaid
classDiagram
    class BedErrorListener {
        -list errors
        
        +__init__()
        +syntaxError(recognizer, offendingSymbol, line, column, msg, e)
    }
```

---

## 2. dataclasses (entidades de dados)

### 2.1 BedParameters (classe principal)

```mermaid
classDiagram
    class BedParameters {
        +BedGeometry bed
        +LidsConfig lids
        +ParticlesConfig particles
        +PackingConfig packing
        +ExportConfig export
        +CFDConfig cfd
        
        +to_dict() dict
        +to_json(indent: int) str
    }
    
    BedParameters "1" --> "1" BedGeometry
    BedParameters "1" --> "1" LidsConfig
    BedParameters "1" --> "1" ParticlesConfig
    BedParameters "1" --> "1" PackingConfig
    BedParameters "1" --> "1" ExportConfig
    BedParameters "1" --> "0..1" CFDConfig
```

### 2.2 BedGeometry

```mermaid
classDiagram
    class BedGeometry {
        +float diameter
        +float height
        +float wall_thickness
        +float clearance
        +str material
        +float roughness
        
        +to_dict() dict
        +validate() bool
        +get_internal_radius() float
        +get_volume() float
    }
```

### 2.3 LidsConfig

```mermaid
classDiagram
    class LidsConfig {
        +str top_type
        +str bottom_type
        +float top_thickness
        +float bottom_thickness
        +float seal_clearance
        
        +to_dict() dict
        +validate() bool
        +has_top_lid() bool
        +has_bottom_lid() bool
    }
```

### 2.4 ParticlesConfig

```mermaid
classDiagram
    class ParticlesConfig {
        +str kind
        +float diameter
        +int count
        +float target_porosity
        +float density
        +float mass
        +float restitution
        +float friction
        +float rolling_friction
        +float linear_damping
        +float angular_damping
        +int seed
        
        +to_dict() dict
        +validate() bool
        +get_particle_volume() float
        +get_total_volume() float
        +get_particle_mass() float
    }
```

### 2.5 PackingConfig

```mermaid
classDiagram
    class PackingConfig {
        +str method
        +float gravity
        +int substeps
        +int iterations
        +float damping
        +float rest_velocity
        +float max_time
        +float collision_margin
        
        +to_dict() dict
        +validate() bool
        +get_simulation_frames() int
    }
```

### 2.6 ExportConfig

```mermaid
classDiagram
    class ExportConfig {
        +List~str~ formats
        +str units
        +float scale
        +str wall_mode
        +str fluid_mode
        +bool manifold_check
        +float merge_distance
        
        +to_dict() dict
        +validate() bool
        +has_format(format: str) bool
    }
```

### 2.7 CFDConfig

```mermaid
classDiagram
    class CFDConfig {
        +str regime
        +float inlet_velocity
        +float fluid_density
        +float fluid_viscosity
        +int max_iterations
        +float convergence_criteria
        +bool write_fields
        
        +to_dict() dict
        +validate() bool
        +get_reynolds_number() float
        +is_turbulent() bool
    }
```

---

## 3. diagrama de relacionamentos completo

```mermaid
classDiagram
    class BedWizard {
        -dict params
        -str output_file
        -dict param_help
    }
    
    class BedCompilerListener {
        -BedParameters params
        -list errors
    }
    
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
    }
    
    class LidsConfig {
        +str top_type
        +str bottom_type
        +float top_thickness
    }
    
    class ParticlesConfig {
        +str kind
        +float diameter
        +int count
        +float density
    }
    
    class PackingConfig {
        +str method
        +float gravity
        +int substeps
    }
    
    class ExportConfig {
        +List~str~ formats
        +str units
        +float scale
    }
    
    class CFDConfig {
        +str regime
        +float inlet_velocity
        +float fluid_density
    }
    
    BedWizard --> BedCompilerListener : usa
    BedCompilerListener --> BedParameters : cria
    BedParameters --> BedGeometry : contém
    BedParameters --> LidsConfig : contém
    BedParameters --> ParticlesConfig : contém
    BedParameters --> PackingConfig : contém
    BedParameters --> ExportConfig : contém
    BedParameters --> CFDConfig : contém (opcional)
```

---

## 4. diagrama de sequência - geração de modelo

```mermaid
sequenceDiagram
    participant U as Usuário
    participant W as BedWizard
    participant C as BedCompiler
    participant B as Blender
    
    U->>W: escolhe modo blender interativo
    W->>U: solicita parâmetros
    U->>W: fornece valores
    W->>W: valida parâmetros
    W->>W: gera arquivo.bed
    W->>C: compila arquivo.bed
    C->>C: parse com ANTLR
    C->>C: valida sintaxe
    C->>W: retorna arquivo.bed.json
    W->>B: executa em modo headless
    B->>B: gera geometria 3D
    B->>B: aplica física
    B->>B: salva arquivo.blend
    B->>W: retorna sucesso
    W->>B: abre em modo GUI
    B->>U: exibe modelo 3D
```

---

## 5. diagrama de estados - wizard

```mermaid
stateDiagram-v2
    [*] --> MenuPrincipal
    
    MenuPrincipal --> ModoInterativo : opção 1
    MenuPrincipal --> ModoTemplate : opção 2
    MenuPrincipal --> ModoBlender : opção 3
    MenuPrincipal --> ModoBlenderInterativo : opção 4
    MenuPrincipal --> MenuAjuda : opção 5
    MenuPrincipal --> Documentacao : opção 6
    MenuPrincipal --> [*] : opção 7
    
    ModoInterativo --> ColetaParametros
    ModoTemplate --> EdicaoTemplate
    ModoBlender --> ColetaParametros
    ModoBlenderInterativo --> ColetaParametros
    
    ColetaParametros --> Confirmacao
    EdicaoTemplate --> Confirmacao
    
    Confirmacao --> Compilacao : usuário confirma
    Confirmacao --> MenuPrincipal : usuário cancela
    
    Compilacao --> GeracaoModelo : sucesso
    Compilacao --> MenuPrincipal : erro
    
    GeracaoModelo --> AberturaBlender : modo interativo
    GeracaoModelo --> MenuPrincipal : modo normal
    
    AberturaBlender --> MenuPrincipal
    
    MenuAjuda --> MenuPrincipal
    Documentacao --> MenuPrincipal
```

---

## 6. diagrama de componentes - arquitetura

```mermaid
graph TB
    subgraph "Camada de Interface"
        W[BedWizard]
        H[Sistema de Ajuda]
        D[Documentação HTML]
    end
    
    subgraph "Camada de Compilação"
        G[Gramática ANTLR]
        L[BedLexer]
        P[BedParser]
        CL[BedCompilerListener]
    end
    
    subgraph "Camada de Dados"
        BP[BedParameters]
        BG[BedGeometry]
        LC[LidsConfig]
        PC[ParticlesConfig]
        PK[PackingConfig]
        EC[ExportConfig]
        CC[CFDConfig]
    end
    
    subgraph "Camada de Geração"
        BS[Blender Scripts]
        LE[leito_extracao.py]
    end
    
    subgraph "Camada de Saída"
        JSON[arquivo.bed.json]
        BLEND[arquivo.blend]
    end
    
    W --> CL
    W --> H
    W --> D
    W --> BS
    
    G --> L
    G --> P
    L --> CL
    P --> CL
    
    CL --> BP
    BP --> BG
    BP --> LC
    BP --> PC
    BP --> PK
    BP --> EC
    BP --> CC
    
    BP --> JSON
    JSON --> LE
    LE --> BLEND
```

---

## 7. diagrama de casos de uso

```mermaid
graph LR
    U((Usuário))
    
    subgraph "Sistema Wizard"
        UC1[Criar Leito Interativo]
        UC2[Editar Template]
        UC3[Gerar Modelo 3D]
        UC4[Gerar e Visualizar]
        UC5[Consultar Ajuda]
        UC6[Ver Documentação]
    end
    
    subgraph "Sistema de Validação"
        UC7[Validar Sintaxe]
        UC8[Validar Parâmetros]
    end
    
    subgraph "Sistema de Geração"
        UC9[Gerar Geometria]
        UC10[Aplicar Física]
        UC11[Exportar Modelo]
    end
    
    U --> UC1
    U --> UC2
    U --> UC3
    U --> UC4
    U --> UC5
    U --> UC6
    
    UC1 --> UC7
    UC2 --> UC7
    UC3 --> UC7
    UC4 --> UC7
    
    UC7 --> UC8
    UC8 --> UC9
    UC9 --> UC10
    UC10 --> UC11
```

---

## 8. detalhamento de atributos por classe

### 8.1 BedWizard

| Atributo | Tipo | Descrição | Valor Inicial |
|----------|------|-----------|---------------|
| params | dict | dicionário com parâmetros coletados | {} |
| output_file | str | nome do arquivo de saída | None |
| param_help | dict | dicionário com 47 parâmetros documentados | {...} |

**Métodos Principais:**
- `run()`: loop principal do wizard
- `blender_interactive_mode()`: novo modo com abertura automática
- `execute_blender(open_after)`: execução do blender
- `show_param_help(param_key)`: exibe ajuda contextual

---

### 8.2 BedGeometry

| Atributo | Tipo | Range | Unidade | Descrição |
|----------|------|-------|---------|-----------|
| diameter | float | 0.01 - 2.0 | m | diâmetro interno do leito |
| height | float | 0.01 - 5.0 | m | altura do leito |
| wall_thickness | float | 0.0001 - 0.1 | m | espessura da parede |
| clearance | float | 0.0 - 1.0 | m | folga superior |
| material | str | - | - | material (steel, glass, etc) |
| roughness | float | 0.0 - 0.01 | m | rugosidade da superfície |

**Métodos Calculados:**
```python
get_internal_radius() -> diameter/2 - wall_thickness
get_volume() -> π * radius² * height
```

---

### 8.3 ParticlesConfig

| Atributo | Tipo | Range | Unidade | Descrição |
|----------|------|-------|---------|-----------|
| kind | str | sphere/cube/cylinder | - | formato da partícula |
| diameter | float | 0.0001 - 0.5 | m | diâmetro |
| count | int | 1 - 10000 | - | quantidade |
| target_porosity | float | 0.1 - 0.9 | - | porosidade alvo |
| density | float | 100 - 20000 | kg/m³ | densidade |
| mass | float | 0.0 - 1000.0 | g | massa individual |
| restitution | float | 0.0 - 1.0 | - | coef. restituição |
| friction | float | 0.0 - 1.0 | - | coef. atrito |
| rolling_friction | float | 0.0 - 1.0 | - | atrito rolamento |
| linear_damping | float | 0.0 - 1.0 | - | amortecimento linear |
| angular_damping | float | 0.0 - 1.0 | - | amortecimento angular |
| seed | int | 0 - 99999 | - | seed aleatória |

**Métodos Calculados:**
```python
get_particle_volume() -> (4/3) * π * (diameter/2)³  # para esferas
get_total_volume() -> particle_volume * count
get_particle_mass() -> volume * density
```

---

### 8.4 PackingConfig

| Atributo | Tipo | Range | Unidade | Descrição |
|----------|------|-------|---------|-----------|
| method | str | rigid_body | - | método empacotamento |
| gravity | float | -50.0 - 50.0 | m/s² | aceleração gravidade |
| substeps | int | 1 - 100 | - | subdivisões frame |
| iterations | int | 1 - 100 | - | iterações solver |
| damping | float | 0.0 - 1.0 | - | amortecimento global |
| rest_velocity | float | 0.0001 - 1.0 | m/s | velocidade repouso |
| max_time | float | 0.1 - 60.0 | s | tempo máximo |
| collision_margin | float | 0.00001 - 0.01 | m | margem colisão |

**Métodos Calculados:**
```python
get_simulation_frames() -> max_time * fps
# assumindo fps = 24 (padrão blender)
```

---

### 8.5 CFDConfig

| Atributo | Tipo | Range | Unidade | Descrição |
|----------|------|-------|---------|-----------|
| regime | str | laminar/turbulent_rans | - | regime escoamento |
| inlet_velocity | float | 0.001 - 100.0 | m/s | velocidade entrada |
| fluid_density | float | 0.1 - 2000.0 | kg/m³ | densidade fluido |
| fluid_viscosity | float | 1e-6 - 1.0 | Pa.s | viscosidade |
| max_iterations | int | 10 - 100000 | - | iterações máximas |
| convergence_criteria | float | 1e-10 - 1e-2 | - | critério convergência |
| write_fields | bool | true/false | - | salvar campos |

**Métodos Calculados:**
```python
get_reynolds_number() -> (density * velocity * length) / viscosity
is_turbulent() -> reynolds_number > 2300
```

---

## 9. cardinalidade dos relacionamentos

```mermaid
erDiagram
    BedWizard ||--o{ BedParameters : cria
    BedParameters ||--|| BedGeometry : contém
    BedParameters ||--|| LidsConfig : contém
    BedParameters ||--|| ParticlesConfig : contém
    BedParameters ||--|| PackingConfig : contém
    BedParameters ||--|| ExportConfig : contém
    BedParameters ||--o| CFDConfig : contém
    
    BedWizard {
        dict params
        str output_file
        dict param_help
    }
    
    BedParameters {
        BedGeometry bed
        LidsConfig lids
        ParticlesConfig particles
        PackingConfig packing
        ExportConfig export
        CFDConfig cfd
    }
    
    BedGeometry {
        float diameter
        float height
        float wall_thickness
        float clearance
        str material
        float roughness
    }
    
    ParticlesConfig {
        str kind
        float diameter
        int count
        float target_porosity
        float density
    }
    
    PackingConfig {
        str method
        float gravity
        int substeps
        int iterations
    }
```

---

## 10. padrões de design utilizados

### 10.1 Padrão Builder (BedWizard)

```mermaid
classDiagram
    class Builder~BedWizard~ {
        <<pattern>>
        +build_bed_section()
        +build_lids_section()
        +build_particles_section()
        +build_packing_section()
        +build_export_section()
        +get_result() BedParameters
    }
    
    class Director~User~ {
        <<pattern>>
        +construct()
    }
    
    Director --> Builder : usa
```

### 10.2 Padrão Visitor (BedCompilerListener)

```mermaid
classDiagram
    class Visitor~BedCompilerListener~ {
        <<pattern>>
        +visitBedSection()
        +visitLidsSection()
        +visitParticlesSection()
        +visitPackingSection()
    }
    
    class Element~ParseTree~ {
        <<pattern>>
        +accept(visitor)
    }
    
    Element --> Visitor : aceita
```

### 10.3 Padrão Facade (BedWizard.run)

```mermaid
classDiagram
    class Facade~BedWizard~ {
        <<pattern>>
        +interactive_mode()
        +template_mode()
        +blender_mode()
        +blender_interactive_mode()
    }
    
    class SubSystem1~Compiler~ {
        +compile()
    }
    
    class SubSystem2~Blender~ {
        +generate()
    }
    
    class SubSystem3~Validator~ {
        +validate()
    }
    
    Facade --> SubSystem1
    Facade --> SubSystem2
    Facade --> SubSystem3
```

---

## 11. métricas das classes

| Classe | Atributos | Métodos | LOC | Complexidade |
|--------|-----------|---------|-----|--------------|
| BedWizard | 3 | 28 | 1388 | Alta |
| BedCompilerListener | 2 | 45 | 450 | Média |
| BedParameters | 6 | 2 | 50 | Baixa |
| BedGeometry | 6 | 3 | 30 | Baixa |
| LidsConfig | 5 | 4 | 25 | Baixa |
| ParticlesConfig | 12 | 4 | 40 | Baixa |
| PackingConfig | 8 | 2 | 30 | Baixa |
| ExportConfig | 7 | 3 | 30 | Baixa |
| CFDConfig | 7 | 3 | 30 | Baixa |

---

## 12. glossário de termos

| Termo | Significado |
|-------|-------------|
| **bed** | leito cilíndrico que contém as partículas |
| **lids** | tampas superior e inferior do leito |
| **particles** | partículas empacotadas dentro do leito |
| **packing** | processo de empacotamento físico |
| **export** | configurações de exportação do modelo |
| **cfd** | computational fluid dynamics (simulação) |
| **headless** | execução sem interface gráfica |
| **gui** | graphical user interface |
| **rigid_body** | corpo rígido com física |
| **substeps** | subdivisões de frame para precisão |
| **porosity** | percentual de vazios no empacotamento |

---

*diagramas gerados com mermaid.js*  
*compatível com github, gitlab, vscode*  
*última atualização: outubro 2024*

