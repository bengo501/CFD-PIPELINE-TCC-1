// ponto de entrada do bundle vite que monta react na div root do index html
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { LanguageProvider } from './context/LanguageContext'
import { ThemeProvider } from './context/ThemeContext'
import { AppUiProvider } from './context/AppUiContext'
import { UserProvider } from './context/UserContext'
import './styles/App.css'

// create root liga o react a um elemento dom existente
// strict mode executa certas verificacoes duplicadas em desenvolvimento para achar bugs
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* theme define data theme no html para css */}
    <ThemeProvider>
      {/* language guarda codigo pt ou en e funcao de traducao t */}
      <LanguageProvider>
        {/* app ui sincroniza modo simples modo dev e timeout axios com settings */}
        <AppUiProvider>
          <UserProvider>
            <App />
          </UserProvider>
        </AppUiProvider>
      </LanguageProvider>
    </ThemeProvider>
  </React.StrictMode>,
)
