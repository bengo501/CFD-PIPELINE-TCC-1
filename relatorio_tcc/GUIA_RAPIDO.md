# guia rápido - começar a escrever

## 🚀 início rápido (5 minutos)

### 1. upload para overleaf

1. compactar a pasta `relatorio_tcc` em zip
2. acessar https://www.overleaf.com/login
3. criar conta (gratuita)
4. new project → upload project → selecionar zip
5. esperar upload completar
6. clicar em "recompile" (símbolo de play verde)
7. pronto! pdf gerado!

### 2. editar informações básicas

abrir `main.tex` e editar:

```latex
\titulo{Pipeline Automatizado para Simulações CFD de Leitos Empacotados}
\autor{SEU NOME COMPLETO AQUI}  % <-- MUDAR
\local{Sua Cidade, Estado}       % <-- MUDAR
\data{2025}
\orientador{Prof. Dr. Nome do Orientador}  % <-- MUDAR
\instituicao{%
  Nome da sua Universidade       % <-- MUDAR
  \par
  Nome da Faculdade             % <-- MUDAR
  \par
  Nome do Curso}                % <-- MUDAR
```

### 3. escrever os capítulos

os capítulos estão em `capitulos/`:

- `cap01_introducao.tex` - já tem estrutura base
- `cap02_referencial_teorico.tex` - já tem conteúdo técnico
- `cap03_materiais_metodos.tex` - já tem estrutura
- `cap04_desenvolvimento.tex` - **criar este**
- `cap05_resultados.tex` - **criar este**
- `cap06_conclusao.tex` - **criar este**

### 4. adicionar figuras

1. colocar imagem em `figuras/arquitetura/` (ou outra subpasta)
2. no texto, adicionar:

```latex
\begin{figure}[htb]
    \centering
    \includegraphics[width=0.8\textwidth]{figuras/arquitetura/pipeline.pdf}
    \caption{seu texto explicativo aqui}
    \label{fig:pipeline}
\end{figure}
```

3. referenciar no texto: `conforme figura \ref{fig:pipeline}...`

### 5. adicionar referências

1. buscar no google scholar
2. clicar em "citar" → "bibtex"
3. copiar para `bibliografia/referencias.bib`
4. citar no texto: `\cite{nome_referencia}`

## 📝 ordem de escrita recomendada

### semana 1-2: estrutura

- [ ] preencher informações pessoais em `main.tex`
- [ ] escrever resumo (`pretextual/resumo.tex`)
- [ ] escrever abstract (`pretextual/abstract.tex`)
- [ ] revisar introdução (`cap01_introducao.tex`)

### semana 3-4: desenvolvimento

- [ ] criar `cap04_desenvolvimento.tex`
- [ ] escrever sobre implementação da dsl
- [ ] escrever sobre geração de geometria
- [ ] escrever sobre simulação openfoam
- [ ] escrever sobre banco de dados e api

### semana 5: resultados

- [ ] criar `cap05_resultados.tex`
- [ ] adicionar gráficos de validação
- [ ] adicionar tabelas de resultados
- [ ] escrever discussão

### semana 6: finalização

- [ ] criar `cap06_conclusao.tex`
- [ ] revisar todos capítulos
- [ ] adicionar todas figuras
- [ ] verificar todas referências
- [ ] pedir feedback do orientador

## ✏️ dicas de escrita

### seja objetivo

❌ evite: "talvez seja possível que..."
✅ prefira: "o sistema permite..."

### use voz ativa

❌ evite: "foi implementado um sistema..."
✅ prefira: "implementou-se um sistema..." ou "este trabalho implementa..."

### seja técnico mas claro

❌ muito simples: "o programa funciona bem"
✅ adequado: "o sistema demonstrou eficiência de 95% nos testes"

### cite sempre

sempre que afirmar algo técnico, cite a fonte:

```latex
os leitos empacotados são amplamente utilizados \cite{dullien1992}.
```

## 📊 elementos essenciais

### todo trabalho deve ter:

- [ ] capa e folha de rosto
- [ ] resumo (pt) e abstract (en)
- [ ] lista de figuras
- [ ] lista de tabelas
- [ ] lista de siglas
- [ ] sumário
- [ ] introdução
- [ ] referencial teórico
- [ ] metodologia
- [ ] desenvolvimento/implementação
- [ ] resultados e discussão
- [ ] conclusão
- [ ] referências bibliográficas
- [ ] apêndices (código, diagramas)

## 🎯 metas semanais

### meta página 60-80

se dividir em 6 semanas:

- semana 1: 10 páginas (introdução + início referencial)
- semana 2: 15 páginas (completar referencial)
- semana 3: 15 páginas (materiais e métodos)
- semana 4: 15 páginas (desenvolvimento)
- semana 5: 15 páginas (resultados)
- semana 6: 10 páginas (conclusão + revisão)

**total:** 80 páginas ✅

## 🔥 atalhos úteis overleaf

- `ctrl + /` - comentar linha
- `ctrl + enter` - recompilar
- `ctrl + f` - buscar
- `ctrl + h` - buscar e substituir
- `ctrl + b` - negrito
- `ctrl + i` - itálico

## 📚 recursos úteis

- **abntex2 doc**: https://www.abntex.net.br
- **overleaf doc**: https://www.overleaf.com/learn
- **latex symbols**: http://detexify.kirelabs.org/classify.html
- **tabelas latex**: https://www.tablesgenerator.com

## ⚠️ erros comuns

### erro: undefined control sequence

**causa:** comando latex errado ou pacote faltando
**solução:** verificar se escreveu corretamente

### erro: file not found

**causa:** caminho de figura errado
**solução:** verificar nome e caminho do arquivo

### referências não aparecem

**solução:** 
1. recompilar
2. clicar em "logs and output files"
3. procurar por erros no .bib

## 💡 próximos passos

1. fazer upload para overleaf ✅
2. editar informações pessoais
3. começar a escrever introdução
4. adicionar primeira figura
5. adicionar primeira referência
6. mostrar para orientador

boa escrita! 🚀📝

