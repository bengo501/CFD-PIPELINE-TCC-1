# bibliografia - tcc cfd pipeline

## 📚 conteúdo

esta pasta contém todas as referências bibliográficas utilizadas no desenvolvimento do tcc.

### arquivos

- **`referencias.txt`**: lista completa de referências organizadas por categoria (texto simples)
- **`referencias.bib`**: arquivo bibtex para citações em latex
- **`categorias.md`**: análise detalhada das referências por tema

---

## 📊 estatísticas

**total de referências**: 46

### distribuição por categoria

| categoria | quantidade | % |
|-----------|------------|---|
| frameworks web | 7 | 15.2% |
| blender | 6 | 13.0% |
| openfoam/cfd | 8 | 17.4% |
| visualização | 3 | 6.5% |
| leitos empacotados | 5 | 10.9% |
| dsl | 2 | 4.3% |
| infraestrutura | 8 | 17.4% |
| apis/padrões | 2 | 4.3% |
| python | 2 | 4.3% |
| metodologia | 1 | 2.2% |
| tendências | 2 | 4.3% |

### distribuição por tipo

| tipo | quantidade | % |
|------|------------|---|
| documentação oficial | 28 | 60.9% |
| livros acadêmicos | 9 | 19.6% |
| artigos e tutoriais | 9 | 19.6% |

---

## 🔑 referências principais

### fundamentais para o projeto

1. **ergun1952**: equação fundamental para validação de perda de carga
2. **fowler2010**: base teórica para domain-specific languages
3. **ferziger2002**: métodos computacionais em dinâmica de fluidos
4. **roache1998**: verificação e validação em cfd
5. **conlan2017**: desenvolvimento com blender python api

### documentação técnica essencial

- **openfoam_docs2025**: guia completo openfoam
- **blender_api2025**: api python do blender
- **fastapi2025**: framework backend
- **threejs2025**: visualização 3d web
- **docker2025**: containerização

---

## 🎓 uso em latex

### configuração básica

```latex
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[portuguese]{babel}
\usepackage[style=abnt]{biblatex}

\addbibresource{bibliografia/referencias.bib}

\begin{document}

% seu conteúdo aqui

\printbibliography

\end{document}
```

### exemplos de citação

```latex
% citação textual
segundo \textcite{ergun1952}, a perda de carga em leitos empacotados...

% citação entre parênteses
a dsl foi implementada seguindo as diretrizes de fowler \cite{fowler2010}.

% múltiplas citações
diversos autores discutem cfd \cite{ferziger2002, pope2000, roache1998}.

% citação com página específica
conforme \textcite[p.~89]{ergun1952}, ...
```

### compilação

```bash
# compilar documento latex com bibliografia
pdflatex documento.tex
biber documento
pdflatex documento.tex
pdflatex documento.tex
```

---

## 📖 categorias detalhadas

### frameworks e bibliotecas web

frameworks utilizados no desenvolvimento da interface web e api.

**principais**:
- fastapi: backend rest api
- three.js: visualização 3d no navegador
- plotly: gráficos científicos interativos

### blender

documentação e recursos para automação de modelagem 3d.

**principais**:
- blender python api: automação completa
- conlan (2017): guia de desenvolvimento de add-ons
- brito (2018): quick start guide

### openfoam e cfd

simulação numérica de escoamento em meios porosos.

**principais**:
- openfoam foundation: documentação oficial
- ferziger & perić (2002): métodos computacionais
- pope (2000): escoamentos turbulentos
- roache (1998): verificação e validação

### leitos empacotados

teoria e aplicações de cfd em leitos empacotados.

**principais**:
- ergun (1952): artigo seminal sobre perda de carga
- mdpi: comparação blender vs star-ccm+
- cutec: relatórios técnicos

### infraestrutura e devops

tecnologias para containerização e deploy.

**principais**:
- docker: containerização
- postgresql: banco de dados
- redis: fila de jobs assíncronos
- minio: object storage

---

## 🔍 busca por tema

### cfd e simulação
```
ergun1952, ferziger2002, pope2000, roache1998,
openfoam_docs2025, openfoam_wiki2025
```

### automação python
```
lutz2013, matthes2019, blender_api2025,
njanakiev_blender
```

### web development
```
fastapi2025, threejs2025, nodejs2025,
django2025, flask2025
```

### validação numérica
```
roache1998, ergun1952, cutec2025
```

### containerização
```
docker2025, dockercompose2025, minio2025,
postgresql2025, redis2025
```

---

## 📝 formato abnt

todas as referências estão formatadas conforme normas abnt (associação brasileira de normas técnicas).

### estrutura para livros
```
AUTOR. Título: subtítulo. Edição. Local: Editora, ano.
```

### estrutura para artigos
```
AUTOR. Título do artigo. Nome do Periódico, v. X, n. Y, p. início-fim, ano.
```

### estrutura para documentação web
```
AUTOR/ENTIDADE. Título. Disponível em: <url>. Acesso em: data.
```

---

## ✅ checklist de citação

ao adicionar novas referências:

- [ ] verificar se já existe no arquivo
- [ ] adicionar em `referencias.txt` na categoria correta
- [ ] adicionar em `referencias.bib` com chave única
- [ ] incluir url completa para recursos online
- [ ] incluir data de acesso para recursos web
- [ ] verificar formatação abnt
- [ ] atualizar estatísticas neste readme

---

## 📎 recursos adicionais

### ferramentas úteis

- **jabref**: gerenciador de referências bibtex
- **zotero**: gerenciamento bibliográfico com plugin bibtex
- **mendeley**: alternativa ao zotero
- **doi2bib**: converter doi para bibtex automaticamente

### validadores

- **biblatex**: validador de sintaxe bibtex
- **abntex2**: pacote latex para abnt

### conversores

- converter bibtex → word: usar zotero ou mendeley
- converter bibtex → markdown: pandoc

---

**última atualização**: 9 out. 2025  
**responsável**: sistema de gestão bibliográfica do projeto

