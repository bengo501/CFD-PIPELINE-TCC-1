# guia: internacionalização (i18n)

## visão geral

sistema completo de internacionalização português/inglês com troca dinâmica e persistência de preferências.

---

## funcionalidades

### 1. troca de idioma
- **botão no header** com bandeiras 🇧🇷/🇺🇸
- **toggle instantâneo** pt ↔ en
- **persistência** no localStorage
- **animação suave** na troca

### 2. idiomas suportados
- **português (pt)** - padrão
- **inglês (en)**

### 3. cobertura
- ✅ navegação principal
- ✅ títulos e headers
- ✅ botões e ações
- ✅ mensagens de status
- ✅ labels de formulário
- ✅ tooltips e hints

---

## arquitetura

### estrutura de arquivos

```
frontend/src/
├── i18n/
│   └── translations.js       # dicionário pt/en
├── context/
│   └── LanguageContext.jsx   # contexto global
└── components/
    └── App.jsx               # uso do hook
```

---

## como funciona

### 1. dicionário de traduções

```javascript
// frontend/src/i18n/translations.js

export const translations = {
  pt: {
    appTitle: 'pipeline cfd - leitos empacotados',
    createBed: 'criar leito',
    help: 'ajuda',
    // ...
  },
  en: {
    appTitle: 'cfd pipeline - packed beds',
    createBed: 'create bed',
    help: 'help',
    // ...
  }
};
```

### 2. contexto global

```javascript
// frontend/src/context/LanguageContext.jsx

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('pt');
  const { t } = useTranslation(language);

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'pt' ? 'en' : 'pt');
  };

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};
```

### 3. hook useLanguage

```javascript
// usar em qualquer componente

import { useLanguage } from './context/LanguageContext';

function MyComponent() {
  const { language, toggleLanguage, t } = useLanguage();
  
  return (
    <div>
      <h1>{t('appTitle')}</h1>
      <button onClick={toggleLanguage}>
        {language === 'pt' ? '🇧🇷 PT' : '🇺🇸 EN'}
      </button>
    </div>
  );
}
```

---

## como usar

### 1. adicionar nova tradução

```javascript
// em translations.js

export const translations = {
  pt: {
    // adicionar aqui
    myNewKey: 'meu texto em português',
  },
  en: {
    // adicionar aqui
    myNewKey: 'my text in english',
  }
};
```

### 2. usar tradução no componente

```javascript
import { useLanguage } from './context/LanguageContext';

function MyComponent() {
  const { t } = useLanguage();
  
  return <h1>{t('myNewKey')}</h1>;
}
```

### 3. tradução com interpolação

```javascript
// para textos com variáveis dinâmicas

// opção 1: template string
<p>{t('jobs')}: {count} {t('running')}</p>

// opção 2: concatenação
<p>{`${t('total')}: ${count}`}</p>
```

---

## traduções disponíveis

### header
```
appTitle, online, offline, jobs, running
```

### navegação
```
createBed, interactiveWizard, cfdSimulation, results
```

### wizard
```
wizardTitle, selectMode, help, documentation
interactiveMode, templateMode, blenderMode, blenderInteractiveMode
```

### botões
```
back, next, generate, cancel, confirm, save, close, refresh, delete, view
```

### parâmetros
```
bedGeometry, lids, particles, packing, export, cfdParams, confirmation
```

### cfd
```
cfdTitle, createNewSim, createCase, createAndRun, simulations, noSimulations, autoRefresh
```

### status
```
queued, preparing, meshing, running, completed, error
```

### mensagens
```
success, warning, connectionError, fileNotFound, compilationError
```

---

## botão de idioma

### design

```css
.language-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.language-toggle:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}
```

### componente

```jsx
<button 
  className="language-toggle" 
  onClick={toggleLanguage}
  title={language === 'pt' ? 'Switch to English' : 'Mudar para Português'}
>
  <span className="flag">{language === 'pt' ? '🇧🇷' : '🇺🇸'}</span>
  <span className="lang-text">{language === 'pt' ? 'PT' : 'EN'}</span>
</button>
```

---

## persistência

### localStorage

```javascript
// salvar preferência
useEffect(() => {
  localStorage.setItem('language', language);
  document.documentElement.lang = language;
}, [language]);

// carregar preferência
const [language, setLanguage] = useState(() => {
  return localStorage.getItem('language') || 'pt';
});
```

### atributo lang

```javascript
// atualiza <html lang="pt"> ou <html lang="en">
document.documentElement.lang = language;
```

---

## tipografia melhorada

### fontes profissionais

```css
/* Inter - sans-serif moderna */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* JetBrains Mono - monospace código */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 16px;
  line-height: 1.7;
}

code, pre, .monospace {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
}
```

### tamanhos aumentados

| elemento | tamanho | peso |
|----------|---------|------|
| h1 | 2.5rem (40px) | 700 |
| h2 | 2rem (32px) | 600 |
| h3 | 1.5rem (24px) | 600 |
| h4 | 1.25rem (20px) | 500 |
| p, body | 1rem (16px) | 400 |
| button | 1rem (16px) | 500 |

### otimizações

```css
body {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

---

## expandir i18n

### adicionar novo idioma

1. **adicionar ao dicionário:**

```javascript
// translations.js

export const translations = {
  pt: { /* ... */ },
  en: { /* ... */ },
  es: {  // novo idioma
    appTitle: 'pipeline cfd - lechos empacados',
    createBed: 'crear lecho',
    // ...
  }
};
```

2. **atualizar toggle:**

```javascript
const toggleLanguage = () => {
  setLanguage(prev => {
    if (prev === 'pt') return 'en';
    if (prev === 'en') return 'es';
    return 'pt';
  });
};
```

3. **adicionar bandeira:**

```jsx
<span className="flag">
  {language === 'pt' && '🇧🇷'}
  {language === 'en' && '🇺🇸'}
  {language === 'es' && '🇪🇸'}
</span>
```

---

## boas práticas

### 1. chaves descritivas
```javascript
// ❌ ruim
t('text1'), t('msg2')

// ✅ bom
t('createBed'), t('connectionError')
```

### 2. agrupamento lógico
```javascript
// ✅ organizar por contexto
header: { title, subtitle },
buttons: { save, cancel, confirm },
errors: { connection, notFound }
```

### 3. pluralização
```javascript
// simples
t('jobs'): {count} {count === 1 ? t('running') : t('runningPlural')}
```

### 4. fallback
```javascript
// sempre ter fallback
const t = (key) => {
  return translations[language][key] || key;
};
```

---

## testes

### verificar cobertura

```bash
# listar textos não traduzidos
grep -r "'\w\+'" frontend/src/components/
```

### testar troca

1. abrir aplicação
2. clicar no botão de idioma
3. verificar todos os textos
4. recarregar página (persistência)

---

## futuras melhorias

### 1. traduções dinâmicas
```javascript
// carregar traduções da api
const { data } = await fetch('/api/translations');
setTranslations(data);
```

### 2. detecção automática
```javascript
// usar idioma do navegador
const browserLang = navigator.language.split('-')[0];
setLanguage(['pt', 'en'].includes(browserLang) ? browserLang : 'pt');
```

### 3. traduções de formulários
```javascript
// validações e hints em pt/en
const validationMessages = {
  pt: { required: 'campo obrigatório', min: 'valor mínimo' },
  en: { required: 'required field', min: 'minimum value' }
};
```

### 4. datas e números formatados
```javascript
// usar Intl API
new Intl.DateTimeFormat(language).format(date);
new Intl.NumberFormat(language).format(number);
```

---

## conclusão

✅ sistema i18n completo
✅ fácil adicionar traduções
✅ persistência funcional
✅ tipografia profissional
✅ fontes maiores e legíveis

**o sistema agora é totalmente internacional!** 🌍

usuários podem escolher entre português e inglês com um clique, e a preferência é salva automaticamente.

