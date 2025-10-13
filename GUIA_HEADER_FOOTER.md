# guia: header e footer profissionais

## visão geral

implementação de header e footer modernos e profissionais para a aplicação web, com design responsivo, paleta institucional e informações completas do projeto.

---

## header

### características

**visual:**
- gradiente vinho institucional com borda amarela
- logo animado com pulse suave
- subtítulo "computational fluid dynamics"
- sticky (fixo no topo ao rolar)

**funcionalidades:**
- status do sistema em tempo real
  - indicador online/offline com animação
  - contador de jobs em execução
- botão de idioma pt/en
- backdrop blur (efeito vidro)

**estrutura:**
```
┌─────────────────────────────────────────────┐
│  🔬 cfd pipeline              🟢 online ⚙️ 2  │
│     computational fluid dynamics   🇧🇷 PT    │
└─────────────────────────────────────────────┘
```

### componentes

#### logo container
- ícone: 🔬 (microscópio)
- título: "cfd pipeline"
- subtítulo: "computational fluid dynamics"

#### status do sistema
- **status dot**: bola pulsante verde (online) / vermelha (offline)
- **jobs counter**: ícone ⚙️ + número de jobs rodando

#### language toggle
- bandeira: 🇧🇷 (pt) / 🇺🇸 (en)
- texto: PT / EN
- hover: levanta e muda cor

---

## footer

### características

**visual:**
- gradiente vinho escuro → claro
- borda amarela superior
- 4 colunas de informações
- rodapé inferior com copyright

**seções:**

#### 1. informações (coluna maior)
- logo + nome do projeto
- descrição bilíngue
- versão (v0.1.0 beta)

#### 2. links do projeto
- github repositório
- issues
- kanban project

#### 3. tecnologias
- openfoam 11
- blender 4.x
- react 18
- fastapi 0.x

#### 4. informações acadêmicas
- tcc
- ciência da computação
- engenharia química
- ano: 2024/2025

#### rodapé inferior
- copyright com licença mit
- link para perfil github

---

## responsividade

### desktop (> 1024px)
- header: logo à esquerda, status + idioma à direita
- footer: 4 colunas lado a lado

### tablet (640px - 1024px)
- header: mesma estrutura
- footer: 2 colunas em grid

### mobile (< 640px)
- header: empilhado verticalmente
- footer: 1 coluna
- status: vertical
- copyright: centralizado

---

## código

### app.jsx

```jsx
// header
<header className="header">
  <div className="header-content">
    <div className="header-left">
      <div className="logo-container">
        <div className="logo-icon">🔬</div>
        <div className="logo-text">
          <h1>{t('appTitle')}</h1>
          <span className="subtitle">computational fluid dynamics</span>
        </div>
      </div>
    </div>
    
    <div className="header-right">
      <div className="system-status">
        {/* status items */}
      </div>
      <button className="language-toggle">
        {/* idioma */}
      </button>
    </div>
  </div>
</header>

// footer
<footer className="footer">
  <div className="footer-content">
    <div className="footer-section footer-info">
      {/* logo, descrição, versão */}
    </div>
    <div className="footer-section footer-links">
      {/* links projeto */}
    </div>
    <div className="footer-section footer-tech">
      {/* tecnologias */}
    </div>
    <div className="footer-section footer-academic">
      {/* info acadêmica */}
    </div>
  </div>
  
  <div className="footer-bottom">
    <div className="footer-bottom-content">
      <p className="copyright">
        © 2024-2025 cfd pipeline. código aberto sob licença mit.
      </p>
      <div className="footer-social">
        <a href="https://github.com/bengo501">
          <span className="social-icon">🐙</span>
        </a>
      </div>
    </div>
  </div>
</footer>
```

### app.css (principais classes)

```css
/* header */
.header { /* gradiente vinho + sticky */ }
.logo-container { /* flex horizontal */ }
.logo-icon { /* animação pulse */ }
.status-dot { /* bola pulsante */ }
.language-toggle { /* botão idioma */ }

/* footer */
.footer { /* gradiente vinho + grid */ }
.footer-content { /* 4 colunas */ }
.footer-section { /* seção individual */ }
.version-badge { /* badge v0.1.0 */ }
.tech-badge { /* badge tecnologia */ }
.academic-year { /* ano acadêmico */ }
.footer-social { /* ícone github */ }
```

---

## animações

### header
- **logo pulse**: escala 1.0 → 1.05 (2s loop)
- **status blink**: opacity 1.0 → 0.5 (2s loop)
- **language hover**: translateY(-2px) + shadow

### footer
- **link hover**: translateX(5px) + cor amarela
- **social hover**: translateY(-3px) + scale(1.1)

---

## paleta de cores

```css
--wine: #5F1923        /* primário */
--wine-2: #641E23      /* primário escuro */
--yellow: #F0B91E      /* destaque */
--green: #50AF50       /* sucesso */
--orange: #DC7323      /* warning */
```

---

## acessibilidade

- **aria-label**: botão idioma
- **title**: tooltips
- **rel="noopener noreferrer"**: links externos
- **contraste**: texto branco sobre vinho (AAA)
- **foco**: outline visível em todos interativos

---

## i18n

textos bilíngues:
- footer description
- seções (projeto/project, tecnologias/technologies, acadêmico/academic)
- copyright (código aberto/open source)
- títulos (tcc/final project, ciência da computação/computer science)

---

## links externos

**projeto:**
- repositório: https://github.com/bengo501/CFD-PIPELINE-TCC-1
- issues: https://github.com/bengo501/CFD-PIPELINE-TCC-1/issues
- kanban: https://github.com/users/bengo501/projects/2

**perfil:**
- github: https://github.com/bengo501

---

## tecnologias usadas

**frontend:**
- react 18.3.1
- vite 6.0.1
- css modules
- google fonts (inter, jetbrains mono)

**recursos:**
- gradientes css
- backdrop-filter blur
- css grid / flexbox
- animações keyframes
- media queries

---

## estrutura de arquivos

```
frontend/src/
├── App.jsx                 # componente com header/footer
├── styles/
│   └── App.css            # estilos header/footer
└── context/
    └── LanguageContext.jsx # i18n
```

---

## próximos passos possíveis

1. adicionar mais redes sociais (linkedin, twitter)
2. newsletter / mailing list
3. modo escuro (dark mode)
4. scroll to top button
5. breadcrumbs no header
6. search bar global
7. user profile dropdown
8. notificações toast

---

## referências

- design system: material design
- gradientes: institutional colors
- tipografia: inter + jetbrains mono
- ícones: unicode emojis
- layout: css grid + flexbox

---

**atualizado:** 2025-01-13  
**versão:** 1.0.0  
**autor:** cfd pipeline team

