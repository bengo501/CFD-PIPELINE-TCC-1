// contexto react que partilha o id do utilizador ativo em toda a arvore de componentes
// o valor e o mesmo que o axios envia no cabecalho x user id
// assim qualquer pagina pode reler lista quando o utilizador muda no menu
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  getStoredActiveUserId,
  setStoredActiveUserId,
  syncAxiosUserHeader,
} from '../services/api';

// contexto react sem valor default util fora do provider
const UserContext = createContext(null);

export function UserProvider({ children }) {
  // estado inicial vem do local storage para sobreviver a refresh da pagina
  const [activeUserId, setActiveUserIdState] = useState(() => getStoredActiveUserId());

  // sempre que o id muda atualizamos o axios para os proximos pedidos http
  useEffect(() => {
    syncAxiosUserHeader();
  }, [activeUserId]);

  // funcao estavel para o menu de perfil alterar utilizador
  const setActiveUserId = useCallback((id) => {
    setStoredActiveUserId(id);
    setActiveUserIdState(getStoredActiveUserId());
  }, []);

  // memo evita rerender desnecessario dos consumidores
  const value = useMemo(
    () => ({ activeUserId, setActiveUserId }),
    [activeUserId, setActiveUserId]
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export function useActiveUser() {
  const ctx = useContext(UserContext);
  if (!ctx) {
    throw new Error('useActiveUser deve ser usado dentro de UserProvider');
  }
  return ctx;
}
