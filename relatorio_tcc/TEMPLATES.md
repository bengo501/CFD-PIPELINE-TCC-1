# templates úteis para latex

## figuras

### figura simples

```latex
\begin{figure}[htb]
    \centering
    \includegraphics[width=0.8\textwidth]{figuras/arquitetura/pipeline.pdf}
    \caption{pipeline automatizado para simulações cfd}
    \label{fig:pipeline}
\end{figure}
```

### duas figuras lado a lado

```latex
\begin{figure}[htb]
    \centering
    \begin{subfigure}[b]{0.45\textwidth}
        \centering
        \includegraphics[width=\textwidth]{figuras/caso1.pdf}
        \caption{caso 1}
        \label{fig:caso1}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.45\textwidth}
        \centering
        \includegraphics[width=\textwidth]{figuras/caso2.pdf}
        \caption{caso 2}
        \label{fig:caso2}
    \end{subfigure}
    \caption{comparação entre casos}
    \label{fig:comparacao}
\end{figure}
```

## tabelas

### tabela simples

```latex
\begin{table}[htb]
\centering
\caption{resultados experimentais}
\label{tab:resultados}
\begin{tabular}{lcc}
\toprule
\textbf{caso} & \textbf{$\Delta P$ (pa)} & \textbf{desvio (\%)} \\
\midrule
1 & 1250 & 3.2 \\
2 & 2150 & 5.8 \\
3 & 980 & 2.1 \\
\bottomrule
\end{tabular}
\end{table}
```

### tabela com múltiplas colunas

```latex
\begin{table}[htb]
\centering
\caption{parâmetros dos casos de teste}
\label{tab:parametros}
\begin{tabular}{lccccc}
\toprule
\multirow{2}{*}{\textbf{caso}} & \multicolumn{2}{c}{\textbf{geometria}} & \multicolumn{2}{c}{\textbf{partículas}} & \multirow{2}{*}{\textbf{$\varepsilon$}} \\
\cmidrule(lr){2-3} \cmidrule(lr){4-5}
& $D$ (mm) & $H$ (mm) & $n$ & $d_p$ (mm) & \\
\midrule
1 & 50 & 100 & 500 & 5 & 0.42 \\
2 & 100 & 200 & 800 & 10 & 0.40 \\
3 & 75 & 150 & 650 & 7.5 & 0.41 \\
\bottomrule
\end{tabular}
\end{table}
```

## equações

### equação simples

```latex
\begin{equation}
\frac{\Delta P}{L} = 150 \frac{(1-\varepsilon)^2}{\varepsilon^3} \frac{\mu u_s}{d_p^2} + 1.75 \frac{(1-\varepsilon)}{\varepsilon^3} \frac{\rho u_s^2}{d_p}
\label{eq:ergun}
\end{equation}
```

### múltiplas equações alinhadas

```latex
\begin{align}
Re &= \frac{\rho u_s d_p}{\mu(1-\varepsilon)} \label{eq:reynolds} \\
\varepsilon &= \frac{V_{vazio}}{V_{total}} \label{eq:porosidade} \\
u_s &= \varepsilon \cdot u_{fluido} \label{eq:velocidade_superficial}
\end{align}
```

## código

### python

```latex
\begin{lstlisting}[language=Python, caption={exemplo python}]
def calcular_perda_carga(velocidade, diametro, porosidade):
    """calcula perda de carga pela equação de ergun"""
    termo1 = 150 * ((1-porosidade)**2 / porosidade**3)
    termo2 = 1.75 * ((1-porosidade) / porosidade**3)
    return termo1 + termo2
\end{lstlisting}
```

### javascript/typescript

```latex
\begin{lstlisting}[language=JavaScript, caption={exemplo react}]
const BedViewer = ({ bedId }) => {
    const [bed, setBed] = useState(null);
    
    useEffect(() => {
        fetch(`/api/beds/${bedId}`)
            .then(res => res.json())
            .then(data => setBed(data));
    }, [bedId]);
    
    return <div>{bed && <ModelViewer model={bed.blend_file} />}</div>;
};
\end{lstlisting}
```

### bash/shell

```latex
\begin{lstlisting}[language=bash, caption={comandos docker}]
# iniciar todos containers
docker-compose up -d

# ver logs do backend
docker-compose logs -f backend

# parar tudo
docker-compose down
\end{lstlisting}
```

## listas

### lista com marcadores

```latex
\begin{itemize}
    \item primeiro item
    \item segundo item
    \begin{itemize}
        \item subitem 2.1
        \item subitem 2.2
    \end{itemize}
    \item terceiro item
\end{itemize}
```

### lista numerada

```latex
\begin{enumerate}
    \item primeiro passo
    \item segundo passo
    \item terceiro passo
\end{enumerate}
```

### lista de descrição

```latex
\begin{description}
    \item[fastapi] framework web para api rest
    \item[react] biblioteca javascript para ui
    \item[docker] plataforma de containerização
\end{description}
```

## citações

### citação inline

```latex
segundo \cite{ergun1952}, a perda de carga...
```

### múltiplas citações

```latex
diversos autores \cite{ergun1952, dixon2006, versteeg2007} discutem...
```

### citação com número de página

```latex
como afirma \citeonline[p.~42]{fowler2010}...
```

## referências cruzadas

### figuras

```latex
conforme ilustrado na figura \ref{fig:pipeline}...
as figuras \ref{fig:caso1} e \ref{fig:caso2} mostram...
```

### tabelas

```latex
a tabela \ref{tab:resultados} apresenta...
os dados da tabela \ref{tab:parametros} foram utilizados...
```

### equações

```latex
aplicando a equação \ref{eq:ergun}...
utilizando as equações \ref{eq:reynolds} e \ref{eq:porosidade}...
```

### seções/capítulos

```latex
conforme descrito no capítulo \ref{cap:referencial}...
veja a seção \ref{sec:validacao} para mais detalhes...
```

## notas de rodapé

```latex
o openfoam\footnote{open source field operation and manipulation} é amplamente utilizado...
```

## destaque de texto

### negrito

```latex
\textbf{texto em negrito}
```

### itálico

```latex
\textit{texto em itálico}
```

### código inline

```latex
o comando \texttt{docker-compose up} inicia os containers...
```

### sublinhado

```latex
\underline{texto sublinhado}
```

## símbolos especiais

### gregos

```latex
$\alpha, \beta, \gamma, \delta, \epsilon, \varepsilon$
$\mu, \nu, \rho, \sigma, \tau$
$\Delta, \Gamma, \Omega$
```

### matemáticos

```latex
$\leq, \geq, \neq, \approx, \sim$
$\times, \div, \pm, \mp$
$\infty, \partial, \nabla$
$\sum, \int, \prod$
```

### setas

```latex
$\rightarrow, \leftarrow, \leftrightarrow$
$\Rightarrow, \Leftarrow, \Leftrightarrow$
```

## cores (se necessário)

```latex
\usepackage{xcolor}

\textcolor{red}{texto vermelho}
\textcolor{blue}{texto azul}
\colorbox{yellow}{fundo amarelo}
```

## comentários

```latex
% isso é um comentário de linha

\begin{comment}
isso é um
comentário
de múltiplas linhas
\end{comment}
```

## quebras

### quebra de página

```latex
\newpage
```

### quebra de linha

```latex
primeira linha \\
segunda linha
```

### espaço vertical

```latex
\vspace{1cm}  % espaço de 1cm
\vspace*{\fill}  % espaço flexível até preencher
```

## caixas

### caixa simples

```latex
\fbox{texto dentro de caixa}
```

### caixa com largura específica

```latex
\framebox[10cm][c]{texto centralizado em caixa de 10cm}
```

### minipage

```latex
\begin{minipage}{0.45\textwidth}
conteúdo da primeira coluna
\end{minipage}
\hfill
\begin{minipage}{0.45\textwidth}
conteúdo da segunda coluna
\end{minipage}
```

## links e urls

```latex
\url{https://www.exemplo.com}
\href{https://www.exemplo.com}{texto do link}
```

