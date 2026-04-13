import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { LanguageProvider } from './context/LanguageContext'
import { ThemeProvider } from './context/ThemeContext'
import { AppUiProvider } from './context/AppUiContext'
import './styles/App.css'

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

