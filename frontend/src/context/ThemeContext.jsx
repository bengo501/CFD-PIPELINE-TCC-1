// tema claro escuro ou segue preferencia do sistema operativo
import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const ThemeContext = createContext();

function getSystemTheme() {
  // media query padrao do css para dark mode
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

function readInitialThemeMode() {
  // compativel com chave antiga theme
  const m = localStorage.getItem('themeMode');
  if (m === 'light' || m === 'dark' || m === 'system') return m;
  const legacy = localStorage.getItem('theme');
  if (legacy === 'light' || legacy === 'dark') return legacy;
  return 'system';
}

function resolveEffective(mode) {
  // system calcula light ou dark em tempo real
  if (mode === 'light') return 'light';
  if (mode === 'dark') return 'dark';
  return getSystemTheme();
}

export function ThemeProvider({ children }) {
  const [themeMode, setThemeModeState] = useState(readInitialThemeMode);
  const [theme, setTheme] = useState(() => resolveEffective(readInitialThemeMode()));

  useEffect(() => {
    const eff = resolveEffective(themeMode);
    setTheme(eff);
    if (themeMode !== 'system') return undefined;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = () => setTheme(mq.matches ? 'dark' : 'light');
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, [themeMode]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    localStorage.setItem('themeMode', themeMode);
  }, [theme, themeMode]);

  const setThemeMode = useCallback((mode) => {
    if (mode === 'light' || mode === 'dark' || mode === 'system') {
      setThemeModeState(mode);
    }
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeModeState((prev) => {
      if (prev === 'light') return 'dark';
      if (prev === 'dark') return 'light';
      return getSystemTheme() === 'dark' ? 'light' : 'dark';
    });
  }, []);

  const isDarkMode = theme === 'dark';

  return (
    <ThemeContext.Provider
      value={{ theme, themeMode, setThemeMode, toggleTheme, isDarkMode }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
