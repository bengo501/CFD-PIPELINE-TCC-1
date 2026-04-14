// estado global pt en sincroniza html lang e localstorage
import { createContext, useContext, useState, useEffect } from 'react';
import { useTranslation } from '../i18n/translations';

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  // valor inicial vem do browser ou pt
  const [language, setLanguageState] = useState(() => {
    return localStorage.getItem('language') || 'pt';
  });

  const { t } = useTranslation(language);

  // cada mudanca persiste e atualiza atributo lang da pagina
  useEffect(() => {
    localStorage.setItem('language', language);
    document.documentElement.lang = language;
  }, [language]);

  const toggleLanguage = () => {
    // alterna entre as duas linguas suportadas
    setLanguageState((prev) => (prev === 'pt' ? 'en' : 'pt'));
  };

  const setLanguage = (lang) => {
    // ignora codigos desconhecidos
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

