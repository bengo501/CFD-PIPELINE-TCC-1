// entrada react monta a arvore com tema idioma e modo ui
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { LanguageProvider } from './context/LanguageContext'
import { ThemeProvider } from './context/ThemeContext'
import { AppUiProvider } from './context/AppUiContext'
import './styles/App.css'

// strict mode ajuda a detetar efeitos secundarios duplos em dev
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider>
      <LanguageProvider>
        <AppUiProvider>
          <App />
        </AppUiProvider>
      </LanguageProvider>
    </ThemeProvider>
  </React.StrictMode>,
)
