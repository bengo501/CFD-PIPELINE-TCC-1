# referencial teórico - documentação técnica e científica

## 📚 conteúdo

esta pasta contém a fundamentação teórica e técnica completa do projeto cfd-pipeline-tcc, relacionando decisões de implementação com literatura científica e documentação técnica.

### arquivos

1. **`fundamentacao_teorica.md`** (15 seções, 1000+ linhas)
   - fundamentação científica de cada componente
   - relação código ↔ literatura
   - validação e verificação
   - contribuições e inovações

2. **`decisoes_arquiteturais.md`** (9 seções, 800+ linhas)
   - decisões técnicas detalhadas
   - comparação de alternativas
   - trade-offs e justificativas
   - lições aprendidas

---

## 🎯 objetivo

demonstrar que **cada decisão técnica do projeto** está fundamentada em:

1. **literatura científica** (livros, artigos, teses)
2. **documentação oficial** (ferramentas, frameworks)
3. **melhores práticas** (padrões da indústria)

---

## 📊 estrutura da fundamentação

### fundamentacao_teorica.md

```
1. introdução
2. domain-specific languages (dsl)
   ├── fowler (2010)
   └── implementação gramática .bed

3. modelagem 3d automatizada (blender)
   ├── conlan (2017)
   ├── brito (2018)
   ├── mdpi (2025)
   └── física rigid body

4. simulação cfd (openfoam)
   ├── ferziger & perić (2002)
   ├── pope (2000)
   ├── equação de ergun (1952)
   └── geração de malha

5. verificação e validação
   ├── roache (1998) - gci
   └── comparação com ergun

6. arquitetura web e api
   ├── fastapi (2025)
   └── openapi (2025)

7. visualização 3d web
   └── three.js (2025)

8. pós-processamento
   ├── paraview (kitware, 2025)
   └── plotly (2025)

9. containerização
   └── docker (2025)

10. persistência
    ├── postgresql (2025)
    └── minio (2025)

11. metodologia ágil
    └── sutherland (2014)

12. síntese de decisões
13. contribuições
14. trabalhos futuros
15. conclusão
```

### decisoes_arquiteturais.md

```
1. escolha da stack
   ├── fastapi vs flask vs django
   └── análise comparativa

2. frontend
   ├── react vs vue vs angular
   └── vite vs create-react-app

3. visualização 3d
   ├── three.js vs babylon.js vs vtk.js
   └── react-three-fiber

4. containerização
   ├── docker vs vm vs bare metal
   └── docker-compose

5. persistência
   ├── postgresql vs mongodb
   └── minio vs s3

6. job queue
   ├── celery vs rq vs arq
   └── implementação planejada

7. parser dsl
   ├── antlr vs pyparsing vs lark
   └── gramática externa

8. síntese
9. lições aprendidas
```

---

## 🔑 principais referências utilizadas

### científicas (livros e artigos)

| referência | tema | aplicação no projeto |
|------------|------|---------------------|
| **ergun (1952)** | perda de carga | validação Δp/L |
| **ferziger & perić (2002)** | métodos cfd | volumes finitos |
| **pope (2000)** | turbulência | modelos rans |
| **roache (1998)** | v&v | gci, convergência |
| **fowler (2010)** | dsl | arquitetura compilador |
| **conlan (2017)** | blender api | automação 3d |
| **sutherland (2014)** | scrum | gestão do projeto |

### documentação técnica

| ferramenta | documentação | aplicação |
|------------|-------------|-----------|
| **openfoam** | foundation (2025) | simulação cfd |
| **blender** | foundation (2025) | modelagem 3d |
| **fastapi** | oficial (2025) | backend api |
| **three.js** | foundation (2025) | visualização 3d |
| **docker** | inc. (2025) | containerização |
| **postgresql** | global dev (2025) | persistência |
| **plotly** | oficial (2025) | gráficos |

---

## 💡 como usar este material

### para leitura sequencial

1. comece por `fundamentacao_teorica.md` (contexto científico)
2. depois `decisoes_arquiteturais.md` (escolhas técnicas)
3. consulte `../referencias.bib` para citações latex

### para consulta rápida

use o índice no início de cada documento para ir direto à seção de interesse.

### para citação no tcc

**exemplo de como referenciar**:

```latex
\section{Domain-Specific Language}

A implementação da DSL seguiu os princípios estabelecidos 
por \textcite{fowler2010}, que define linguagens de domínio 
específico como ferramentas especializadas para resolver 
problemas em domínios restritos \cite[p.~27]{fowler2010}.

A escolha do ANTLR como parser generator foi baseada em sua 
robustez e documentação \cite{lark2025,fowler2010}.
```

---

## 📈 métricas de fundamentação

### cobertura bibliográfica

- **46 referências** utilizadas no total
- **28 documentações oficiais** (60.9%)
- **9 livros acadêmicos** (19.6%)
- **9 artigos e tutoriais** (19.6%)

### distribuição por componente

| componente | refs | principais |
|------------|------|-----------|
| cfd/openfoam | 8 | ferziger, pope, ergun |
| blender | 6 | conlan, brito, mdpi |
| web/api | 7 | fastapi, three.js |
| dsl | 2 | fowler, lark |
| infraestrutura | 8 | docker, postgresql |
| validação | 4 | roache, ergun, cutec |

### decisões fundamentadas

**100% das decisões técnicas** possuem:
- ✅ fundamentação teórica
- ✅ comparação de alternativas
- ✅ justificativa explícita
- ✅ referência bibliográfica

---

## 🎓 relação com o tcc

### uso na monografia

estes documentos servem como base para:

1. **capítulo 2 - revisão bibliográfica**
   - copiar seções relevantes de `fundamentacao_teorica.md`
   - expandir com mais detalhes teóricos

2. **capítulo 3 - metodologia**
   - usar `decisoes_arquiteturais.md` para justificar escolhas
   - incluir diagramas e tabelas comparativas

3. **capítulo 4 - implementação**
   - referenciar código-fonte citando literatura
   - mostrar aplicação prática da teoria

4. **capítulo 5 - validação**
   - usar seção de v&v de `fundamentacao_teorica.md`
   - adicionar resultados experimentais

### uso na apresentação

slides para defesa:

- **slide "tecnologias"**: tabela de `decisoes_arquiteturais.md` (seção 8.1)
- **slide "validação"**: equação de ergun e gci de `fundamentacao_teorica.md`
- **slide "contribuições"**: seção 13 de `fundamentacao_teorica.md`

---

## 🔗 navegação

### documentos relacionados

```
bibliografia/
├── referencias.txt              # lista completa de refs
├── referencias.bib              # formato bibtex
├── README.md                    # guia da bibliografia
└── referencial_teorico/
    ├── README.md               # este arquivo
    ├── fundamentacao_teorica.md    # base científica
    └── decisoes_arquiteturais.md   # escolhas técnicas
```

### links rápidos

- [fundamentação teórica completa](fundamentacao_teorica.md)
- [decisões arquiteturais detalhadas](decisoes_arquiteturais.md)
- [referências bibliográficas](../referencias.txt)
- [arquivo bibtex](../referencias.bib)

---

## ✅ checklist de uso

ao escrever a monografia:

- [ ] ler `fundamentacao_teorica.md` completo
- [ ] ler `decisoes_arquiteturais.md` completo
- [ ] identificar seções relevantes para cada capítulo
- [ ] verificar todas as citações em `referencias.bib`
- [ ] expandir conteúdo com análise crítica própria
- [ ] adicionar resultados experimentais
- [ ] revisar consistência entre documentos
- [ ] validar todas as referências

---

## 📝 estatísticas dos documentos

| documento | linhas | seções | refs citadas | tabelas | códigos |
|-----------|--------|--------|--------------|---------|---------|
| fundamentacao_teorica.md | 1000+ | 15 | 30+ | 5 | 20+ |
| decisoes_arquiteturais.md | 800+ | 9 | 15+ | 10 | 15+ |
| **total** | **1800+** | **24** | **45+** | **15** | **35+** |

---

## 🎯 pontos fortes da fundamentação

1. **abrangência**: cobre todos os aspectos do projeto
2. **profundidade**: cada decisão justificada em detalhes
3. **atualidade**: referências de 2023-2025
4. **diversidade**: livros clássicos + documentação moderna
5. **aplicabilidade**: código real demonstrando conceitos
6. **rigor**: seguindo padrões acadêmicos

---

## 📖 exemplo de uso em latex

```latex
\chapter{Fundamentação Teórica}

\section{Linguagens de Domínio Específico}

\subsection{Conceitos Fundamentais}

\textcite{fowler2010} define Domain-Specific Languages (DSL) 
como linguagens especializadas para resolver problemas em um 
domínio específico, oferecendo maior expressividade que 
linguagens de propósito geral.

\begin{quote}
A DSL is a computer language that's targeted to a particular 
kind of problem, rather than a general purpose language 
that's aimed at any kind of software problem.
\cite[p.~27]{fowler2010}
\end{quote}

No contexto deste trabalho, foi desenvolvida uma DSL 
declarativa denominada \texttt{.bed} para especificar 
leitos empacotados...

[continua com detalhes da implementação]

\section{Dinâmica de Fluidos Computacional}

\subsection{Método dos Volumes Finitos}

O OpenFOAM utiliza o método dos volumes finitos conforme 
descrito por \textcite{ferziger2002}...
```

---

**última atualização**: 9 outubro 2025  
**versão**: 1.0  
**autor**: sistema de documentação do projeto

