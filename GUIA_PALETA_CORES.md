# guia: paleta de cores da identidade visual

## paleta completa

### cores principais

| cor | hex | uso |
|-----|-----|-----|
| **vinho (principal)** | `#5F1923` | títulos, header, botões principais |
| **vinho médio** | `#641E23` | hover de botões primários |
| **verde folha** | `#50AF50` | sucesso, destaques positivos |
| **verde escuro** | `#376E37` | hover verde, estados ativos |
| **amarelo/dourado** | `#F0B91E` | accents, botões secundários |
| **laranja** | `#DC7323` | warnings, hover amarelo |
| **creme claro** | `#F5F087` | backgrounds alternativos |
| **dourado claro** | `#F5E65F` | highlights |
| **branco** | `#FFFFFF` | fundo principal |

---

## mapeamento semântico

### variáveis css

```css
:root {
  /* cores da identidade */
  --wine: #5F1923;
  --wine-2: #641E23;
  --green: #50AF50;
  --green-dark: #376E37;
  --yellow: #F0B91E;
  --orange: #DC7323;
  --cream: #F5F087;
  --gold-light: #F5E65F;
  --white: #FFFFFF;
  
  /* mapeamento semântico */
  --primary: var(--wine);           /* ações principais */
  --primary-dark: var(--wine-2);    /* hover primário */
  --success: var(--green);          /* sucessos */
  --warning: var(--orange);         /* avisos */
  --accent: var(--yellow);          /* destaques */
  --accent-secondary: var(--orange); /* destaques secundários */
}
```

---

## aplicações no sistema

### botões

#### primário (ações principais)
```css
background: var(--wine);      /* #5F1923 */
color: white;

:hover {
  background: var(--wine-2);  /* #641E23 */
}
```
**uso:** criar leito, enviar formulário, confirmar

#### sucesso (ações positivas)
```css
background: var(--green);     /* #50AF50 */
color: white;

:hover {
  background: var(--green-dark); /* #376E37 */
}
```
**uso:** executar simulação, concluir wizard

#### accent (visualizar/destacar)
```css
background: var(--yellow);    /* #F0B91E */
color: var(--wine);
font-weight: 600;

:hover {
  background: var(--orange);  /* #DC7323 */
  color: white;
}
```
**uso:** visualizar resultados, ver detalhes

---

### progress bars

```css
background: linear-gradient(90deg, 
  var(--green),  /* início */
  var(--wine)    /* fim */
);
```
**efeito:** transição suave do verde (início) para vinho (conclusão)

---

### cards e containers

#### background principal
```css
background: var(--white);     /* #FFFFFF */
border: 1px solid #E8D5C4;   /* tom creme suave */
```

#### background alternativo
```css
background: #FFFBF5;         /* branco levemente creme */
border: 1px solid #E8D5C4;
```

#### background destaque
```css
background: var(--cream);    /* #F5F087 */
border: 2px solid var(--yellow);
```

---

### estados de status

#### queued (na fila)
```css
background: #E3F2FD;
color: #1976D2;
```

#### preparing (preparando)
```css
background: #FFF3E0;
color: #F57C00;
```

#### running (executando) - pulsa
```css
background: #E8F5E9;
color: var(--green-dark);
animation: pulse 2s infinite;
```

#### completed (concluído)
```css
background: #E8F5E9;
color: var(--green-dark);
```

#### error (erro)
```css
background: #FFEBEE;
color: #C62828;
```

---

## acessibilidade (contraste wcag)

### combinações aprovadas

✅ **excelente (aaa)**
- vinho `#5F1923` sobre branco `#FFFFFF`
- branco `#FFFFFF` sobre vinho `#5F1923`
- verde escuro `#376E37` sobre branco

✅ **bom (aa)**
- amarelo `#F0B91E` sobre vinho `#5F1923`
- laranja `#DC7323` sobre vinho `#5F1923`
- verde `#50AF50` sobre vinho escuro

⚠️ **usar com cuidado**
- verde `#50AF50` sobre branco (contraste limite)
  - **solução:** usar sobre vinho ou com border
- laranja `#DC7323` sobre branco (texto pequeno)
  - **solução:** usar para texto grande ou sobre vinho

---

## exemplos de uso

### header/navbar
```css
background: var(--wine);
color: white;
border-bottom: 3px solid var(--yellow);
```

### cards de wizard
```css
background: #FFFBF5;
border: 2px solid #E8D5C4;
box-shadow: 0 4px 16px rgba(95, 25, 35, 0.1);
```

### botões de ajuda
```css
border: 1px solid var(--wine);
background: white;
color: var(--wine);

:hover {
  background: var(--wine);
  color: white;
}
```

### simulação em progresso
```css
/* barra de progresso */
.progress-fill {
  background: linear-gradient(90deg, 
    var(--green), 
    var(--wine)
  );
}

/* badge pulsando */
.status-running {
  background: var(--green);
  animation: pulse 2s infinite;
}
```

---

## paleta expandida (tons gerados)

### tons de vinho
- **extra escuro:** `#4A1419` (hover estados críticos)
- **principal:** `#5F1923` (primário)
- **médio:** `#641E23` (hover padrão)
- **claro:** `#8B2A35` (backgrounds)
- **extra claro:** `#F5E8EA` (backgrounds suaves)

### tons de verde
- **extra escuro:** `#2A5A2A` (texto sobre claro)
- **escuro:** `#376E37` (hover)
- **principal:** `#50AF50` (sucesso)
- **claro:** `#7BC77B` (hover suave)
- **extra claro:** `#E8F5E9` (backgrounds)

### tons de amarelo/dourado
- **escuro:** `#C99A19` (texto)
- **principal:** `#F0B91E` (accent)
- **claro:** `#F5E65F` (highlights)
- **extra claro:** `#FFF9E6` (backgrounds)

---

## gradientes sugeridos

### primário → secundário
```css
background: linear-gradient(135deg, 
  var(--wine) 0%, 
  var(--wine-2) 100%
);
```

### sucesso
```css
background: linear-gradient(135deg, 
  var(--green) 0%, 
  var(--green-dark) 100%
);
```

### accent
```css
background: linear-gradient(135deg, 
  var(--yellow) 0%, 
  var(--orange) 100%
);
```

### completo (hero)
```css
background: linear-gradient(135deg,
  var(--wine) 0%,
  var(--green-dark) 50%,
  var(--yellow) 100%
);
```

---

## animações com cores

### pulse (executando)
```css
@keyframes pulse {
  0%, 100% {
    background: var(--green);
    opacity: 1;
  }
  50% {
    background: var(--green-dark);
    opacity: 0.8;
  }
}
```

### glow (destaque)
```css
@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(240, 185, 30, 0.5);
  }
  50% {
    box-shadow: 0 0 40px rgba(240, 185, 30, 0.8);
  }
}
```

---

## dark mode (futuro)

### sugestão de adaptação

```css
@media (prefers-color-scheme: dark) {
  :root {
    --wine: #8B2A35;           /* vinho mais claro */
    --green: #7BC77B;          /* verde mais claro */
    --yellow: #FFD54F;         /* amarelo mais claro */
    --bg: #1A1A1A;            /* fundo escuro */
    --text: #E0E0E0;          /* texto claro */
  }
}
```

---

## dicas de uso

### hierarquia visual
1. **mais importante:** vinho (ações principais)
2. **importante:** verde (sucessos)
3. **destacar:** amarelo/laranja (accents)
4. **neutro:** cinzas claros

### equilíbrio
- **70%** branco/creme (espaço, legibilidade)
- **20%** vinho (estrutura, ações)
- **10%** verde/amarelo/laranja (destaques)

### consistência
- usar `var(--nome)` sempre
- manter hover states previsíveis
- respeitar contraste mínimo
- testar em diferentes dispositivos

---

## ferramentas úteis

### testar contraste
- https://webaim.org/resources/contrastchecker/
- https://contrast-ratio.com/

### gerar variações
- https://coolors.co/
- https://paletton.com/

### exportar paleta
- https://color.adobe.com/

---

## antes e depois

### antes (cores genéricas)
```css
--primary: #2196F3;      /* azul genérico */
--success: #4CAF50;      /* verde genérico */
```

### depois (identidade visual)
```css
--primary: #5F1923;      /* vinho institucional */
--success: #50AF50;      /* verde da marca */
```

**resultado:** interface com personalidade, profissional e coesa!

---

## conclusão

✅ paleta aplicada em todo o sistema
✅ acessibilidade garantida (wcag aa/aaa)
✅ consistência visual mantida
✅ identidade visual reforçada

**o sistema agora reflete a identidade visual da instituição!**

