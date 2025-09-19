# DSL para Leitos Empacotados (.bed)

Esta é a implementação da **Domain Specific Language (DSL)** para descrição de leitos empacotados, conforme proposto no TCC. A linguagem `.bed` permite descrever de forma declarativa todos os parâmetros necessários para gerar geometrias 3D e executar simulações CFD.

## Visão Geral

```
arquivo.bed  →  [Compilador]  →  params.json  →  [Blender]  →  modelo_3d.stl
```

## Estrutura da Linguagem

### Seções Obrigatórias

#### 1. `bed` - Geometria do Leito
```bed
bed {
    diameter = 0.05 m;           // diâmetro interno
    height = 0.1 m;              // altura útil
    wall_thickness = 0.002 m;    // espessura da parede
    clearance = 0.01 m;          // folga superior
    material = "steel";          // material (metadado)
    roughness = 0.0001 m;        // rugosidade (opcional)
}
```

#### 2. `lids` - Configuração das Tampas
```bed
lids {
    top_type = "flat";           // flat, hemispherical, none
    bottom_type = "flat";        // flat, hemispherical, none
    top_thickness = 0.003 m;     // espessura da tampa superior
    bottom_thickness = 0.003 m;  // espessura da tampa inferior
    seal_clearance = 0.001 m;    // folga de vedação (opcional)
}
```

#### 3. `particles` - Propriedades das Partículas
```bed
particles {
    kind = "sphere";             // sphere, cube, cylinder
    diameter = 0.005 m;          // diâmetro/aresta
    count = 100;                 // número fixo de partículas
    // OU
    target_porosity = 0.4;       // porosidade alvo (0.0 a 1.0)
    
    density = 2500.0 kg/m3;      // densidade do material
    restitution = 0.3;           // coeficiente de restituição
    friction = 0.5;              // atrito estático
    rolling_friction = 0.1;      // atrito de rolamento
    linear_damping = 0.1;        // amortecimento linear
    angular_damping = 0.1;       // amortecimento angular
    seed = 42;                   // seed para reprodutibilidade
}
```

#### 4. `packing` - Empacotamento Físico
```bed
packing {
    method = "rigid_body";       // método de empacotamento
    gravity = -9.81 m/s;         // aceleração gravitacional
    substeps = 10;               // sub-passos por frame
    iterations = 10;             // iterações do solver
    damping = 0.1;               // amortecimento global
    rest_velocity = 0.01 m/s;    // critério de repouso
    max_time = 5.0 s;            // tempo máximo de simulação
    collision_margin = 0.001 m;  // margem de colisão
}
```

#### 5. `export` - Configuração de Exportação
```bed
export {
    formats = ["stl_binary", "obj"];  // formatos de saída
    units = "m";                      // unidades
    scale = 1.0;                      // escala de exportação
    wall_mode = "surface";            // surface ou solid
    fluid_mode = "none";              // none ou cavity
    manifold_check = true;            // verificar geometria
    merge_distance = 0.0001 m;        // distância de merge
}
```

### Seção Opcional

#### 6. `cfd` - Parâmetros para CFD
```bed
cfd {
    regime = "laminar";              // laminar ou turbulent_rans
    inlet_velocity = 0.1 m/s;        // velocidade de entrada
    fluid_density = 1000.0 kg/m3;    // densidade do fluido
    fluid_viscosity = 1e-6 Pa.s;     // viscosidade dinâmica
    max_iterations = 1000;           // iterações máximas
    convergence_criteria = 1e-6;     // critério de convergência
    write_fields = true;             // escrever campos
}
```

## Unidades Suportadas

- **Comprimento**: `m`, `cm`, `mm`
- **Massa**: `kg`, `g`
- **Tempo**: `s`
- **Pressão**: `Pa`, `N`
- **Velocidade**: `m/s`
- **Densidade**: `kg/m3`
- **Viscosidade**: `Pa.s`

## Comentários

```bed
// comentário de linha
/* comentário 
   de bloco */
```

## Uso do Compilador

### Instalação
```bash
# instalar dependências (se necessário)
pip install pathlib dataclasses
```

### Compilação
```bash
# compilar arquivo .bed
python dsl/compiler/bed_compiler.py examples/leito_simples.bed -o params.json

# compilação com saída detalhada
python dsl/compiler/bed_compiler.py examples/leito_simples.bed -o params.json --verbose
```

### Teste
```bash
# testar todos os exemplos
python dsl/test_compiler.py
```

## Exemplos Inclusos

1. **`leito_simples.bed`** - Exemplo básico com esferas
2. **`leito_avancado.bed`** - Exemplo completo com CFD
3. **`leito_cubos.bed`** - Exemplo com partículas cúbicas

## Integração com Blender

```python
from dsl.integration.blender_adapter import BlenderAdapter

# carregar parâmetros
adapter = BlenderAdapter('params.json')

# obter configurações para blender
altura, diametro, espessura = adapter.get_bed_geometry()
particles_config = adapter.get_particles_config()

# mostrar resumo
adapter.print_summary()
```

## Arquivo de Saída (params.json)

O compilador gera um arquivo JSON estruturado:

```json
{
  "bed": {
    "diameter": 0.05,
    "height": 0.1,
    "wall_thickness": 0.002,
    "clearance": 0.01,
    "material": "steel"
  },
  "particles": {
    "kind": "sphere",
    "diameter": 0.005,
    "count": 100,
    "density": 2500.0,
    "seed": 42
  },
  "hash": "a1b2c3d4e5f6g7h8",
  "version": "1.0"
}
```

## Validações

O compilador verifica automaticamente:

- Valores positivos para dimensões
- Espessura da parede não excede raio
- Partículas cabem no leito
- Exclusividade entre `count` e `target_porosity`
- Coeficientes físicos em faixas válidas
- Consistência geométrica

## Fluxo Completo

1. **Escrever** arquivo `.bed` com parâmetros do leito
2. **Compilar** usando `bed_compiler.py` → gera `params.json`
3. **Executar** script Blender que lê `params.json`
4. **Gerar** geometria 3D (STL, OBJ, FBX)
5. **Executar** simulação CFD (OpenFOAM)
6. **Visualizar** resultados no dashboard

## Vantagens da DSL

- **Declarativa** - descreve "o que" ao invés de "como"
- **Reprodutível** - mesmos parâmetros = mesmos resultados
- **Legível** - sintaxe simples e intuitiva
- **Validada** - verificações automáticas de consistência
- **Versionada** - hash único para cada configuração
- **Extensível** - fácil adicionar novos parâmetros

Esta DSL implementa exatamente o que foi proposto no TCC: uma linguagem específica do domínio que padroniza a entrada, facilita a reprodutibilidade e reduz erros na configuração de simulações CFD de leitos empacotados.
