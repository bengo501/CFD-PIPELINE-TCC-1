// contexto de idioma pt en com persistencia e funcao t de traducao
import { createContext, useContext, useState, useEffect } from 'react';
import { useTranslation } from '../i18n/translations';

// sem valor default forcando uso dentro do provider
const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  // estado string codigo lingua atual
  // inicializa de local storage ou cai em pt
  const [language, setLanguageState] = useState(() => {
    return localStorage.getItem('language') || 'pt';
  });

  // hook de traducao recebe codigo e devolve mapa t
  const { t } = useTranslation(language);

  // efeito sincroniza storage e atributo lang acessivel a leitores de ecra e seo
  useEffect(() => {
    localStorage.setItem('language', language);
    document.documentElement.lang = language;
  }, [language]);

  const toggleLanguage = () => {
    // alternancia simples entre duas linguas suportadas pelo bundle
    setLanguageState((prev) => (prev === 'pt' ? 'en' : 'pt'));
  };

  const setLanguage = (lang) => {
    // filtra codigos desconhecidos para nao quebrar o hook de i18n
    if (lang === 'pt' || lang === 'en') {
      setLanguageState(lang);
    }
  };

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage deve ser usado dentro de LanguageProvider');
  }
  return context;
};

