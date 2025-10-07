# arquitetura do projeto cfd-pipeline-tcc-1

## estrutura de arquivos essenciais e comunicacao

### 1. nucleo do projeto - dsl (domain specific language)

#### **arquivos obrigatorios:**

```
dsl/
├── grammar/
│   └── Bed.g4                              # gramatica antlr (essencial)
├── generated/
│   ├── BedLexer.py                         # gerado pelo antlr (essencial)
│   ├── BedParser.py                        # gerado pelo antlr (essencial)
│   └── BedListener.py                      # gerado pelo antlr (essencial)
├── compiler/
│   └── bed_compiler_antlr_standalone.py    # compilador principal (essencial)
├── bed_wizard.py                           # interface usuario (essencial)
├── antlr-4.13.1-complete.jar              # runtime antlr (essencial)
└── examples/
    └── leito_simples.bed                   # exemplo de uso
```

#### **fluxo de comunicacao dsl:**

```
1. usuario cria arquivo .bed (manualmente ou via wizard)
   ↓
2. bed_wizard.py coleta parametros do usuario
   ↓
3. gera arquivo .bed com sintaxe da gramatica
   ↓
4. chama bed_compiler_antlr_standalone.py
   ↓
5. compilador usa BedLexer.py e BedParser.py (gerados de Bed.g4)
   ↓
6. valida sintaxe e gera arquivo.bed.json
   ↓
7. arquivo json pronto para uso pelo blender
```

---

### 2. geracao 3d - blender scripts

#### **arquivos obrigatorios:**

```
scripts/blender_scripts/
├── leito_extracao.py                       # script principal geracao 3d (essencial)
└── cubo_oco.py                             # script alternativo geometria cubica
```

#### **fluxo de comunicacao blender:**

```
1. bed_wizard.py (modo blender) compila arquivo.bed
   ↓
2. gera arquivo.bed.json com parametros
   ↓
3. executa blender em modo headless:
   blender --background --python leito_extracao.py -- --params arquivo.json --output saida.blend
   ↓
4. leito_extracao.py le json e extrai:
   - bed.diameter, bed.height, bed.wall_thickness
   - particles.count, particles.diameter
   ↓
5. cria objetos 3d:
   - criar_cilindro_oco() -> leito
   - criar_tampa() -> tampas superior/inferior
   - criar_particulas() -> particulas esfericas
   ↓
6. aplica fisica rigid body:
   - leito e tampas: passivos (estaticos)
   - particulas: ativos (caem com gravidade)
   ↓
7. salva arquivo.blend em output/models/
```

---

### 3. saida - modelos gerados

#### **diretorio de saida:**

```
output/
└── models/
    └── leito_blender.blend                 # modelo 3d gerado (essencial)
```

---

## mapa completo de comunicacao

```
┌─────────────────────────────────────────────────────────────────┐
│                          usuario                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             v
┌─────────────────────────────────────────────────────────────────┐
│                      bed_wizard.py                               │
│  - coleta parametros (modo interativo/template/blender)          │
│  - gera arquivo .bed                                             │
└────────────┬─────────────────────────────┬──────────────────────┘
             │                             │
             v                             v
┌─────────────────────────┐    ┌──────────────────────────────────┐
│  arquivo.bed            │    │  bed_compiler_antlr_standalone.py│
│  (sintaxe dsl)          │───>│  - usa BedLexer.py               │
└─────────────────────────┘    │  - usa BedParser.py              │
                               │  - valida sintaxe                 │
                               └──────────┬───────────────────────┘
                                          │
                                          v
                               ┌─────────────────────────┐
                               │  arquivo.bed.json       │
                               │  (parametros normalizados)│
                               └──────────┬──────────────┘
                                          │
                                          v
                               ┌─────────────────────────────────┐
                               │  blender (modo headless)         │
                               │  executa leito_extracao.py       │
                               └──────────┬──────────────────────┘
                                          │
                                          v
                               ┌─────────────────────────┐
                               │  leito_extracao.py      │
                               │  - le json              │
                               │  - cria geometria       │
                               │  - aplica fisica        │
                               │  - salva .blend         │
                               └──────────┬──────────────┘
                                          │
                                          v
                               ┌─────────────────────────┐
                               │  output/models/         │
                               │  arquivo.blend          │
                               │  (modelo 3d completo)   │
                               └─────────────────────────┘
```

---

## dependencias entre arquivos

### **1. bed_wizard.py depende de:**
- `compiler/bed_compiler_antlr_standalone.py` (para compilar .bed)
- `scripts/blender_scripts/leito_extracao.py` (para gerar 3d)
- blender instalado no sistema

### **2. bed_compiler_antlr_standalone.py depende de:**
- `generated/BedLexer.py` (gerado por antlr)
- `generated/BedParser.py` (gerado por antlr)
- `generated/BedListener.py` (gerado por antlr)
- biblioteca antlr4 (pip install antlr4-python3-runtime)

### **3. arquivos gerados (generated/) dependem de:**
- `grammar/Bed.g4` (gramatica fonte)
- `antlr-4.13.1-complete.jar` (para gerar parser)
- java (para executar antlr)

### **4. leito_extracao.py depende de:**
- blender (modulo bpy)
- arquivo.bed.json (parametros)
- python stdlib (json, sys, argparse, pathlib)

---

## arquivos nao essenciais (podem ser removidos)

### **exemplos e testes:**
```
models/blender_generated/       # modelos antigos de teste
exports/standalone_generated/   # exports antigos
dsl/leito                       # arquivo de teste
dsl/leito.json                 # json antigo
dsl/leitoBedBED.bed            # teste
dsl/leitoBedBED.bed.json       # teste
teste_simples.blend            # teste raiz
```

### **scripts auxiliares:**
```
scripts/automation/             # scripts de setup (uso unico)
scripts/standalone_scripts/     # scripts antigos/alternativos
```

---

## ordem de execucao (pipeline completo)

### **setup inicial (uma vez):**
```bash
1. instalar java
2. instalar python + antlr4-python3-runtime
3. instalar blender
4. gerar parser:
   cd dsl
   java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 -o generated grammar/Bed.g4
```

### **uso normal (repetido):**
```bash
1. cd dsl
2. python bed_wizard.py
3. escolher opcao 3 (modo blender)
4. preencher parametros (enter/espaco para padrao)
5. confirmar geracao
6. aguardar (1-5 minutos dependendo de particulas)
7. abrir output/models/leito_blender.blend no blender
```

---

## formato dos arquivos de dados

### **arquivo.bed (entrada):**
```
bed {
    diameter = 0.05 m;
    height = 0.1 m;
    wall_thickness = 0.002 m;
}

particles {
    kind = "sphere";
    count = 100;
    diameter = 0.005 m;
}
```

### **arquivo.bed.json (intermediario):**
```json
{
  "bed": {
    "diameter": 0.05,
    "height": 0.1,
    "wall_thickness": 0.002
  },
  "particles": {
    "kind": "sphere",
    "count": 100,
    "diameter": 0.005
  }
}
```

### **arquivo.blend (saida):**
- formato binario do blender
- contem geometria 3d completa
- contem configuracao de fisica
- pode ser aberto no blender para visualizacao/edicao

---

## tecnologias e versoes

### **essenciais:**
- python 3.8+
- java 11+ (para antlr)
- blender 3.0+ (testado com 4.0.2)
- antlr 4.13.1
- antlr4-python3-runtime

### **opcionais (futuro):**
- openfoam (para simulacao cfd)
- docker (para containerizacao)
- postgresql (para metadados)
- minio (para artefatos)
- fastapi (para api)
- react (para frontend)

---

## checklist de arquivos minimos para funcionar

para o projeto funcionar, voce precisa:

### **obrigatorios:**
- [ ] `dsl/grammar/Bed.g4`
- [ ] `dsl/generated/BedLexer.py`
- [ ] `dsl/generated/BedParser.py`
- [ ] `dsl/generated/BedListener.py`
- [ ] `dsl/compiler/bed_compiler_antlr_standalone.py`
- [ ] `dsl/bed_wizard.py`
- [ ] `dsl/antlr-4.13.1-complete.jar`
- [ ] `scripts/blender_scripts/leito_extracao.py`
- [ ] `output/models/` (diretorio, criado automaticamente)

### **recomendados:**
- [ ] `README.md`
- [ ] `dsl/README_BLENDER_MODE.md`
- [ ] `scripts/blender_scripts/README_PARAMETROS.md`
- [ ] `dsl/examples/leito_simples.bed`
- [ ] `ORGANIZACAO_PROJETO.md`

### **total:** 9 arquivos essenciais + 5 documentacoes

---

## resumo da comunicacao

```
usuario -> bed_wizard.py -> arquivo.bed -> compilador -> arquivo.json -> blender -> modelo.blend
```

cada arquivo tem um papel especifico:
1. **bed_wizard.py**: interface com usuario
2. **Bed.g4**: define sintaxe da linguagem
3. **BedParser.py**: valida sintaxe
4. **bed_compiler_antlr_standalone.py**: converte .bed em .json
5. **leito_extracao.py**: le .json e gera geometria 3d
6. **arquivo.blend**: resultado final visualizavel

---

*ultima atualizacao: janeiro 2025*  
*versao: 1.0.0*
