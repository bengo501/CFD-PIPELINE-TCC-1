import { createContext, useContext, useState, useEffect } from 'react';
import { useTranslation } from '../i18n/translations';

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  // carregar idioma do localStorage ou usar português como padrão
  const [language, setLanguageState] = useState(() => {
    return localStorage.getItem('language') || 'pt';
  });

  const { t } = useTranslation(language);

  // salvar preferência no localStorage
  useEffect(() => {
    localStorage.setItem('language', language);
    document.documentElement.lang = language;
  }, [language]);

  const toggleLanguage = () => {
    setLanguageState((prev) => (prev === 'pt' ? 'en' : 'pt'));
  };

  const setLanguage = (lang) => {
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

