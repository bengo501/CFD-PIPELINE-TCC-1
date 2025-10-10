# relatório de tcc - pipeline cfd automatizado

estrutura de pastas para escrita do relatório de tcc no formato overleaf/latex.

## 📁 estrutura de pastas

```
relatorio_tcc/
├── main.tex                    # arquivo principal (compile este)
├── bibliografia/               # referências bibliográficas
│   └── referencias.bib
├── capitulos/                  # capítulos do trabalho
│   ├── cap01_introducao.tex
│   ├── cap02_referencial_teorico.tex
│   ├── cap03_materiais_metodos.tex
│   ├── cap04_desenvolvimento.tex
│   ├── cap05_resultados.tex
│   └── cap06_conclusao.tex
├── figuras/                    # imagens e diagramas
│   ├── arquitetura/
│   ├── diagramas/
│   ├── graficos/
│   └── screenshots/
├── tabelas/                    # tabelas complexas (opcional)
├── pretextual/                 # elementos pré-textuais
│   ├── resumo.tex
│   ├── abstract.tex
│   ├── siglas.tex
│   ├── dedicatoria.tex
│   ├── agradecimentos.tex
│   ├── epigrafe.tex
│   └── folha_aprovacao.tex
├── postextual/                 # elementos pós-textuais
├── apendices/                  # apêndices
│   ├── apendice_a_codigo.tex
│   ├── apendice_b_diagramas.tex
│   └── apendice_c_manual.tex
└── anexos/                     # anexos (opcional)
    └── anexo_a_documentacao.tex
```

## 🚀 como usar

### opção 1: overleaf (recomendado)

1. acesse https://www.overleaf.com
2. crie novo projeto → "upload project"
3. faça upload da pasta `relatorio_tcc` (como zip)
4. o arquivo principal é `main.tex`
5. compile com `pdflatex` ou `xelatex`

### opção 2: latex local

```bash
# instalar texlive (linux/mac)
sudo apt-get install texlive-full  # ubuntu/debian
brew install --cask mactex          # macos

# instalar miktex (windows)
# baixar de: https://miktex.org/download

# compilar
cd relatorio_tcc
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex  # duas vezes para referências cruzadas
```

### opção 3: vscode + latex workshop

1. instalar extensão "latex workshop"
2. abrir `main.tex`
3. clicar em "build latex project" (ícone verde)

## 📝 como escrever

### adicionar figuras

```latex
\begin{figure}[htb]
    \centering
    \includegraphics[width=0.8\textwidth]{figuras/arquitetura/pipeline.pdf}
    \caption{pipeline automatizado cfd}
    \label{fig:pipeline}
\end{figure}

% referenciar: veja a figura \ref{fig:pipeline}
```

### adicionar tabelas

```latex
\begin{table}[htb]
\centering
\caption{resultados experimentais}
\label{tab:resultados}
\begin{tabular}{lcc}
\toprule
caso & perda de carga (pa) & desvio (\%) \\
\midrule
1 & 1250 & 3.2 \\
2 & 2150 & 5.8 \\
\bottomrule
\end{tabular}
\end{table}
```

### adicionar código

```latex
\begin{lstlisting}[language=Python, caption={exemplo de código}]
def compilar_bed(arquivo):
    parser = BedParser(arquivo)
    return parser.gerar_json()
\end{lstlisting}
```

### adicionar equações

```latex
% equação inline
a velocidade $v = \frac{d}{t}$ foi calculada.

% equação numerada
\begin{equation}
\frac{\Delta P}{L} = 150 \frac{(1-\varepsilon)^2}{\varepsilon^3}
\label{eq:ergun}
\end{equation}
```

### citações

```latex
segundo \cite{ergun1952}, a perda de carga...

% múltiplas citações
diversos autores \cite{ergun1952, dixon2006} discutem...
```

## 📚 referências bibliográficas

as referências estão em `bibliografia/referencias.bib` no formato bibtex:

```bibtex
@article{ergun1952,
    author = {Ergun, S.},
    title = {Fluid flow through packed columns},
    journal = {Chemical Engineering Progress},
    year = {1952},
    volume = {48},
    pages = {89--94}
}
```

para adicionar nova referência:
1. buscar no google scholar
2. clicar em "citar" → "bibtex"
3. copiar para `referencias.bib`
4. citar no texto: `\cite{ergun1952}`

## 📐 estrutura dos capítulos

### capítulo 1: introdução
- contextualização
- motivação
- problema
- objetivos (geral e específicos)
- justificativa
- estrutura do trabalho

### capítulo 2: referencial teórico
- leitos empacotados
- cfd e openfoam
- dsl e antlr
- arquitetura de software
- tecnologias utilizadas

### capítulo 3: materiais e métodos
- metodologia de desenvolvimento
- arquitetura do sistema
- tecnologias selecionadas
- pipeline de processamento
- validação

### capítulo 4: desenvolvimento
- implementação da dsl
- geração de geometria (blender)
- simulação cfd (openfoam)
- banco de dados e api
- interface web
- containerização

### capítulo 5: resultados e discussão
- casos de teste
- validação com ergun
- estudos paramétricos
- análise de performance
- discussão

### capítulo 6: conclusão
- síntese dos resultados
- contribuições
- limitações
- trabalhos futuros

## 🎨 dicas de formatação

### listas

```latex
% lista com marcadores
\begin{itemize}
    \item primeiro item
    \item segundo item
\end{itemize}

% lista numerada
\begin{enumerate}
    \item primeiro passo
    \item segundo passo
\end{enumerate}
```

### seções

```latex
\chapter{título do capítulo}
\section{seção}
\subsection{subseção}
\subsubsection{subsubseção}
```

### referências cruzadas

```latex
% definir label
\section{métodos}
\label{sec:metodos}

% referenciar
conforme descrito na seção \ref{sec:metodos}...

% figuras
veja a figura \ref{fig:diagrama}...

% equações
a equação \ref{eq:ergun} mostra que...
```

## 🔧 troubleshooting

### erro de compilação

1. verificar se todos `\begin{...}` têm `\end{...}`
2. verificar acentuação (usar utf8)
3. compilar 2-3 vezes (para referências)
4. limpar arquivos auxiliares (.aux, .log)

### figuras não aparecem

1. verificar caminho do arquivo
2. usar formato: pdf, png ou jpg
3. não usar espaços no nome do arquivo
4. usar `\graphicspath{{figuras/}}`

### referências quebradas

1. compilar com `bibtex`
2. compilar novamente com `pdflatex` (2x)
3. verificar se chave da citação existe no .bib

## 📊 métricas do documento

- **páginas esperadas**: 60-80
- **palavras**: ~15.000-20.000
- **figuras**: 20-30
- **tabelas**: 10-15
- **referências**: 30-50

## ✅ checklist final

- [ ] todos capítulos escritos
- [ ] todas figuras incluídas e referenciadas
- [ ] todas tabelas formatadas
- [ ] todas equações numeradas e referenciadas
- [ ] todas citações no texto têm entrada no .bib
- [ ] resumo e abstract completos
- [ ] lista de figuras e tabelas
- [ ] lista de siglas e abreviaturas
- [ ] folha de aprovação assinada
- [ ] revisão ortográfica
- [ ] formatação abnt verificada
- [ ] numeração de páginas correta

## 📧 suporte

para dúvidas sobre latex/overleaf:
- documentação overleaf: https://www.overleaf.com/learn
- abnTeX2: https://www.abntex.net.br
- latex wikibook: https://en.wikibooks.org/wiki/LaTeX

boa escrita! 🚀

