import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import api from '../services/api';

const AppUiContext = createContext(null);

export function AppUiProvider({ children }) {
  const [simpleMode, setSimpleModeState] = useState(
    () => localStorage.getItem('app_simple_mode') === '1'
  );
  const [devMode, setDevModeState] = useState(
    () => localStorage.getItem('app_dev_mode') === '1'
  );

  const setSimpleMode = useCallback((value) => {
    const b = !!value;
    setSimpleModeState(b);
    localStorage.setItem('app_simple_mode', b ? '1' : '0');
  }, []);

  const setDevMode = useCallback((value) => {
    const b = !!value;
    setDevModeState(b);
    localStorage.setItem('app_dev_mode', b ? '1' : '0');
  }, []);

  const applySettingsFromApi = useCallback((s) => {
    if (!s || typeof s !== 'object') return;
    if (typeof s.simple_mode === 'boolean') {
      setSimpleMode(s.simple_mode);
    }
    if (typeof s.dev_mode === 'boolean') {
      setDevMode(s.dev_mode);
    }
    const sec = s.database_ui?.client_timeout_sec;
    if (sec != null) {
      const n = Number(sec);
      if (Number.isFinite(n) && n >= 5 && n <= 600) {
        api.defaults.timeout = n * 1000;
      }
    }
  }, [setDevMode, setSimpleMode]);

  const value = useMemo(
    () => ({
      simpleMode,
      devMode,
      setSimpleMode,
      setDevMode,
      applySettingsFromApi,
    }),
    [applySettingsFromApi, devMode, setDevMode, setSimpleMode, simpleMode]
  );

  return <AppUiContext.Provider value={value}>{children}</AppUiContext.Provider>;
}

export function useAppUi() {
  const ctx = useContext(AppUiContext);
  if (!ctx) {
    throw new Error('useAppUi deve ser usado dentro de AppUiProvider');
  }
  return ctx;
}
