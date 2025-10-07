# documentação html interativa

## visão geral

a documentação completa do projeto agora está disponível em formato html interativo, acessível diretamente pelo wizard.

---

## como acessar

### método 1: via wizard (recomendado)

```bash
cd dsl
python bed_wizard.py
# escolher opcao 5
```

### método 2: abrir diretamente

```bash
# windows
start dsl/documentacao.html

# linux/mac
xdg-open dsl/documentacao.html
# ou
open dsl/documentacao.html
```

### método 3: navegador

abra o arquivo `dsl/documentacao.html` diretamente no seu navegador favorito

---

## conteúdo

### 📋 seções principais

1. **introdução**
   - o que é o projeto
   - componentes principais (dsl, blender, openfoam)
   - tecnologias utilizadas

2. **arquitetura**
   - fluxograma visual do pipeline
   - tabela de componentes e status
   - estrutura de arquivos essenciais

3. **instalação**
   - pré-requisitos detalhados
   - comandos passo a passo
   - verificação de instalação

4. **uso rápido**
   - 3 modos de uso (wizard, template, manual)
   - exemplos práticos de código
   - comandos de compilação

5. **parâmetros**
   - tabelas completas por seção
   - ranges permitidos para cada parâmetro
   - descrições objetivas

6. **workflow**
   - processo típico de uso
   - tempos estimados por quantidade de partículas
   - próximos passos do projeto

---

## características do design

### 🎨 visual

- **gradiente moderno**: roxo/azul (#667eea → #764ba2)
- **cards coloridos**: info (azul), warning (amarelo), success (verde)
- **badges de status**: implementado, em progresso, pendente
- **navegação sticky**: menu fixo no topo ao rolar

### 📱 responsividade

- **layout adaptativo**: grid que se ajusta ao tamanho da tela
- **tabelas responsivas**: scroll horizontal em telas pequenas
- **tipografia escalável**: fontes que se adaptam ao dispositivo

### 🎯 usabilidade

- **navegação por âncoras**: clique no menu para ir direto à seção
- **código destacado**: syntax highlighting para melhor legibilidade
- **exemplos práticos**: código real pronto para copiar
- **links úteis**: acesso rápido a recursos externos

---

## estrutura do html

```
documentacao.html (700+ linhas)
├── <head>
│   ├── meta tags (charset, viewport)
│   └── <style> (css inline completo)
│
├── <body>
│   ├── <header> (título e subtítulo)
│   ├── <nav> (menu de navegação sticky)
│   ├── <main>
│   │   ├── #intro (introdução)
│   │   ├── #arquitetura (componentes e fluxo)
│   │   ├── #instalacao (guia de setup)
│   │   ├── #uso (exemplos de uso)
│   │   ├── #parametros (tabelas de params)
│   │   ├── #workflow (processo típico)
│   │   └── #links (recursos adicionais)
│   │
│   └── <footer> (informações do projeto)
```

---

## elementos visuais

### cards informativos

```html
<div class="card card-info">
    <!-- informações importantes -->
</div>

<div class="card card-warning">
    <!-- avisos e atenções -->
</div>

<div class="card card-success">
    <!-- confirmações e sucessos -->
</div>
```

### fluxograma do pipeline

visualização clara do fluxo:
```
usuário → compilador → blender → openfoam → visualização
```

### badges de status

- 🟢 **implementado**: componente funcional
- 🟡 **em progresso**: em desenvolvimento ativo
- 🔴 **pendente**: ainda não iniciado

### tabelas de parâmetros

formato consistente:
- coluna 1: nome do parâmetro
- coluna 2: range permitido
- coluna 3: descrição objetiva

---

## tecnologias usadas

### html5
- estrutura semântica
- tags modernas (header, nav, main, section, footer)
- viewport meta tag para responsividade

### css3
- flexbox e grid layout
- gradientes lineares
- transições e hover effects
- box-shadow para profundidade
- border-radius para cantos arredondados

### javascript
- não utilizado (html puro)
- navegação via âncoras nativas
- interatividade apenas com :hover css

---

## manutenção

### atualizar conteúdo

edite o arquivo `dsl/documentacao.html`:

1. **adicionar nova seção**:
```html
<section id="nova-secao">
    <h2>título da nova seção</h2>
    <p>conteúdo...</p>
</section>
```

2. **atualizar menu**:
```html
<nav>
    <a href="#nova-secao">nova seção</a>
</nav>
```

3. **adicionar tabela**:
```html
<table>
    <tr>
        <th>coluna 1</th>
        <th>coluna 2</th>
    </tr>
    <tr>
        <td>dado 1</td>
        <td>dado 2</td>
    </tr>
</table>
```

### personalizar cores

altere as variáveis de cor no css:

```css
/* gradiente principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* cor dos títulos */
color: #667eea;

/* cor dos badges */
.badge-primary { background: #667eea; }
```

---

## vantagens

### 📚 documentação sempre atualizada
- um único arquivo html
- fácil de manter e versionar
- não requer servidor web

### 🚀 acesso instantâneo
- abre direto no navegador
- não precisa de internet
- funciona offline completamente

### 🎨 apresentação profissional
- design moderno e atraente
- navegação intuitiva
- formatação consistente

### 📱 multiplataforma
- funciona em windows, linux, mac
- compatível com todos os navegadores
- responsivo para mobile

---

## comparação com markdown

| aspecto | markdown | html |
|---------|----------|------|
| **edição** | mais simples | mais verboso |
| **estilo** | limitado | totalmente customizável |
| **navegação** | básica | interativa com âncoras |
| **visualização** | precisa de conversor | direto no navegador |
| **design** | padronizado | completamente personalizado |
| **interatividade** | nenhuma | css hover, smooth scroll |

---

## próximos passos

### melhorias futuras (opcional)

1. **busca interna**: adicionar campo de busca com javascript
2. **modo escuro**: toggle para tema dark/light
3. **impressão**: css otimizado para print
4. **screenshots**: adicionar imagens do wizard e blender
5. **vídeos**: embeds de tutoriais em vídeo
6. **multilíngue**: versões em inglês e português

---

## exemplo de uso completo

```bash
# 1. iniciar wizard
cd dsl
python bed_wizard.py

# 2. ver documentação
escolha (1-6): 5

# saída:
abrindo documentacao no navegador...
arquivo: C:\...\dsl\documentacao.html
sucesso: documentacao aberta no navegador!

# 3. navegador abre automaticamente
# 4. ler documentação
# 5. pressionar enter para voltar ao menu
# 6. escolher modo de criação (1, 2 ou 3)
```

---

## troubleshooting

### problema: navegador não abre

**solução 1**: copie o caminho exibido e abra manualmente

**solução 2**: navegue até `dsl/` e abra `documentacao.html`

### problema: formatação quebrada

**verificação**: abra o arquivo em um editor e verifique se o html está completo

**correção**: o arquivo deve começar com `<!DOCTYPE html>` e terminar com `</html>`

### problema: links não funcionam

**causa**: navegação por âncoras (#secao) requer que as ids existam

**verificação**: cada `<a href="#intro">` deve ter um `<section id="intro">`

---

## conclusão

a documentação html interativa oferece uma experiência profissional e moderna para entender e utilizar o projeto, sendo facilmente acessível através do wizard ou diretamente no navegador.

---

*última atualização: outubro 2024*  
*versão: 1.0.0*  
*arquivo: dsl/documentacao.html (703 linhas)*

