# documentacao do projeto cfd-pipeline-tcc

este diretorio contem toda a documentacao tecnica do projeto.

## arquivos disponíveis

### 📊 diagramas uml

**[UML_COMPLETO.md](UML_COMPLETO.md)** - diagramas uml completos do projeto
- 12 secoes de diagramas diferentes usando mermaid.js
- visualize no github ou em qualquer visualizador markdown com suporte a mermaid
- **conteudo:**
  1. diagrama geral de componentes
  2. diagrama de classes - dsl (dataclasses + compilador)
  3. diagrama de classes - blender (scripts + api)
  4. diagrama de classes - openfoam (gerador de casos)
  5. diagrama de sequencia - fluxo completo
  6. diagrama de estados - pipeline
  7. diagrama entidade-relacionamento - parametros
  8. diagrama de dependencias entre arquivos
  9. diagrama de fluxo de dados
  10. diagrama detalhado - bed_wizard
  11. metricas das classes (complexidade)
  12. glossario de tipos

**[UML_DIAGRAMAS.md](UML_DIAGRAMAS.md)** - diagramas uml originais
- versao anterior com foco em entidades e relacionamentos

### 🐧 guias de instalacao

**[OPENFOAM_WINDOWS_GUIA.md](OPENFOAM_WINDOWS_GUIA.md)** - guia completo de openfoam no windows
- instalacao via wsl2 + ubuntu
- estrutura de casos openfoam
- workflow completo (geometria → mesh → simulacao → pos-processamento)
- comandos principais
- integracao com python
- troubleshooting extensivo
- paraview para visualizacao

### 📁 outras documentacoes

**[documentacao/](documentacao/)** - documentacao antiga do projeto original

---

## como visualizar os diagramas

### opcao 1: github (recomendado)
os diagramas mermaid sao renderizados automaticamente ao visualizar os arquivos `.md` no github.

**acesse:** [github.com/bengo501/CFD-PIPELINE-TCC-1/tree/main/docs](https://github.com/bengo501/CFD-PIPELINE-TCC-1/tree/main/docs)

### opcao 2: vscode com extensao
instale a extensao **markdown preview mermaid support**:
```
ext install bierner.markdown-mermaid
```

depois abra o arquivo `.md` e pressione `Ctrl+Shift+V` para preview.

### opcao 3: mermaid live editor
1. acesse [mermaid.live](https://mermaid.live)
2. copie o codigo de qualquer diagrama (bloco ```mermaid)
3. cole no editor online
4. visualize e exporte como svg/png

### opcao 4: typora ou obsidian
editores markdown como typora e obsidian renderizam mermaid nativamente.

---

## arquitetura do projeto

```
CFD-PIPELINE-TCC-1/
├── dsl/                          # camada dsl
│   ├── grammar/
│   │   └── Bed.g4               # gramatica antlr
│   ├── compiler/
│   │   └── bed_compiler_antlr_standalone.py
│   ├── generated/               # arquivos gerados pelo antlr
│   └── bed_wizard.py            # interface usuario
│
├── scripts/
│   ├── blender_scripts/
│   │   └── leito_extracao.py    # geracao 3d
│   ├── openfoam_scripts/
│   │   └── setup_openfoam_case.py  # configuracao cfd
│   └── standalone_scripts/
│       └── executar_leito_headless.py  # executor blender
│
├── output/
│   ├── models/                  # arquivos .blend gerados
│   └── cfd/                     # casos openfoam
│
└── docs/                        # voce esta aqui!
    ├── UML_COMPLETO.md          # diagramas principais
    ├── OPENFOAM_WINDOWS_GUIA.md # guia openfoam
    └── README.md                # este arquivo
```

---

## fluxo de trabalho visual

```
usuario
  │
  ├─> bed_wizard.py (interface)
  │     │
  │     ├─> definir parametros (interativo/manual/blender)
  │     │
  │     └─> compilar .bed → .bed.json
  │
  ├─> leito_extracao.py (via blender headless)
  │     │
  │     ├─> ler .bed.json
  │     │
  │     └─> gerar .blend (geometria + fisica)
  │
  └─> setup_openfoam_case.py
        │
        ├─> exportar .stl do .blend
        │
        ├─> criar caso openfoam
        │
        └─> executar simulacao (opcional --run)
              │
              └─> resultados cfd para paraview
```

---

## principais classes do projeto

| classe | arquivo | linhas | descricao |
|--------|---------|--------|-----------|
| `BedWizard` | `dsl/bed_wizard.py` | 1388 | interface usuario para criar/editar leitos |
| `BedCompilerListener` | `dsl/compiler/bed_compiler_antlr_standalone.py` | 350 | compila .bed para .bed.json |
| `OpenFOAMCaseGenerator` | `scripts/openfoam_scripts/setup_openfoam_case.py` | 890 | gera casos openfoam automaticamente |
| funcoes blender | `scripts/blender_scripts/leito_extracao.py` | 500 | cria geometria 3d com fisica |

---

## proximos passos

para entender o projeto, recomendamos ler nesta ordem:

1. **[UML_COMPLETO.md](UML_COMPLETO.md)** - comece pelo diagrama geral de componentes (secao 1)
2. **[../dsl/README_BLENDER_MODE.md](../dsl/README_BLENDER_MODE.md)** - entenda como usar o wizard
3. **[../scripts/openfoam_scripts/GUIA_SIMULACAO_MANUAL.md](../scripts/openfoam_scripts/GUIA_SIMULACAO_MANUAL.md)** - aprenda a executar simulacoes
4. **[OPENFOAM_WINDOWS_GUIA.md](OPENFOAM_WINDOWS_GUIA.md)** - instale o openfoam

---

## contribuindo

ao adicionar novos componentes ou modificar a arquitetura, por favor:

1. atualize os diagramas uml relevantes em `UML_COMPLETO.md`
2. adicione comentarios explicativos no codigo
3. documente novos parametros no sistema de ajuda do wizard
4. atualize este readme se adicionar novos arquivos de documentacao

---

## referencias

- [mermaid syntax](https://mermaid.js.org/intro/)
- [antlr documentation](https://www.antlr.org/)
- [blender python api](https://docs.blender.org/api/current/)
- [openfoam user guide](https://www.openfoam.com/documentation/user-guide)
- [paraview guide](https://www.paraview.org/Wiki/ParaView/Users_Guide)

