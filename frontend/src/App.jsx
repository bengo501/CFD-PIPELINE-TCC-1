import { useState, useEffect } from 'react'
import BedForm from './components/BedForm'
import BedWizard from './components/BedWizard'
import CFDSimulation from './components/CFDSimulation'
import PipelineCompleto from './components/PipelineCompleto'
import CasosCFD from './components/CasosCFD'
import JobStatus from './components/JobStatus'
import ModelViewer from './components/ModelViewer'
import ResultsList from './components/ResultsList'
import ThemeIcon from './components/ThemeIcon'
import { getSystemStatus } from './services/api'
import { useLanguage } from './context/LanguageContext'
import { useTheme } from './context/ThemeContext'

function App() {
  const { language, toggleLanguage, t } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('create') // create, wizard, pipeline, cfd, jobs, results
  const [systemStatus, setSystemStatus] = useState(null)
  const [currentJob, setCurrentJob] = useState(null)
  const [lastBedFile, setLastBedFile] = useState(null)
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    // verificar status do sistema ao carregar
    checkSystemStatus()
    
    // detectar scroll para encolher header
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setIsScrolled(true)
      } else {
        setIsScrolled(false)
      }
    }
    
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const checkSystemStatus = async () => {
    try {
      const status = await getSystemStatus()
      setSystemStatus(status)
    } catch (error) {
      console.error('erro ao verificar sistema:', error)
    }
  }

  const handleJobCreated = (job) => {
    setCurrentJob(job)
    setActiveTab('jobs')
  }

  return (
    <div className="app">
      {/* header */}
      <header className={`header ${isScrolled ? 'header-scrolled' : ''}`}>
        <div className="header-content">
          <div className="header-left">
            <div className="logo-container">
              <img 
                src="/image/logoCFDpipeline.png" 
                alt="cfd pipeline logo" 
                className={`logo-icon ${theme === 'dark' ? 'logo-dark' : 'logo-light'}`}
              />
              <div className="logo-text">
                <h1>CFD Pipeline</h1>
                <span className="subtitle">packed beds - computational fluid dynamics</span>
              </div>
            </div>
          </div>
          
          <div className="header-right">
            <div className="system-status">
              {systemStatus && (
                <>
                  <div className="status-item">
                    <span className={`status-dot ${systemStatus.api === 'running' ? 'online' : 'offline'}`}></span>
                    <span className="status-label">
                      {systemStatus.api === 'running' ? t('online') : t('offline')}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-icon">⚙️</span>
                    <span className="status-label">
                      {systemStatus.jobs?.running || 0} {t('running')}
                    </span>
                  </div>
                </>
              )}
            </div>
            
            <button 
              className="theme-toggle" 
              onClick={toggleTheme} 
              title={theme === 'light' ? (language === 'pt' ? 'modo escuro' : 'dark mode') : (language === 'pt' ? 'modo claro' : 'light mode')}
              aria-label={theme === 'light' ? 'toggle dark mode' : 'toggle light mode'}
            >
              {theme === 'light' ? (
                <>
                  <span className="theme-icon">🌙</span>
                  <span className="theme-text">{language === 'pt' ? 'escuro' : 'dark'}</span>
                </>
              ) : (
                <>
                  <span className="theme-icon">☀️</span>
                  <span className="theme-text">{language === 'pt' ? 'claro' : 'light'}</span>
                </>
              )}
            </button>
            
            <button 
              className="language-toggle" 
              onClick={toggleLanguage} 
              title={language === 'pt' ? 'switch to english' : 'mudar para português'}
              aria-label={language === 'pt' ? 'mudar idioma' : 'change language'}
            >
              <span className="flag">{language === 'pt' ? '🇧🇷' : '🇺🇸'}</span>
              <span className="lang-text">{language === 'pt' ? 'pt' : 'en'}</span>
            </button>
          </div>
        </div>
      </header>

      <div className="app-body">
        {/* sidebar */}
        <aside className="sidebar">
          <nav className="sidebar-nav">
            <div className="nav-section">
              <h3 className="nav-section-title">{language === 'pt' ? 'criar' : 'create'}</h3>
              <button
                className={`nav-item ${activeTab === 'create' ? 'active' : ''}`}
                onClick={() => setActiveTab('create')}
              >
                <span className="nav-icon">✨</span>
                <span className="nav-label">{t('createBed')}</span>
              </button>
              <button
                className={`nav-item ${activeTab === 'wizard' ? 'active' : ''}`}
                onClick={() => setActiveTab('wizard')}
              >
                <span className="nav-icon">🧙</span>
                <span className="nav-label">{t('interactiveWizard')}</span>
              </button>
            </div>

            <div className="nav-section">
              <h3 className="nav-section-title">{language === 'pt' ? 'simulação' : 'simulation'}</h3>
              <button
                className={`nav-item ${activeTab === 'pipeline' ? 'active' : ''}`}
                onClick={() => setActiveTab('pipeline')}
              >
                <span className="nav-icon">🚀</span>
                <span className="nav-label">pipeline completo</span>
              </button>
              <button
                className={`nav-item ${activeTab === 'cfd' ? 'active' : ''}`}
                onClick={() => setActiveTab('cfd')}
              >
                <span className="nav-icon">🌊</span>
                <span className="nav-label">{t('cfdSimulation')}</span>
              </button>
              <button
                className={`nav-item ${activeTab === 'casos' ? 'active' : ''}`}
                onClick={() => setActiveTab('casos')}
              >
                <span className="nav-icon">📂</span>
                <span className="nav-label">casos cfd</span>
              </button>
            </div>

            <div className="nav-section">
              <h3 className="nav-section-title">{language === 'pt' ? 'resultados' : 'results'}</h3>
              <button
                className={`nav-item ${activeTab === 'jobs' ? 'active' : ''}`}
                onClick={() => setActiveTab('jobs')}
              >
                <span className="nav-icon">📊</span>
                <span className="nav-label">{t('jobs')} ({systemStatus?.jobs?.total || 0})</span>
              </button>
              <button
                className={`nav-item ${activeTab === 'results' ? 'active' : ''}`}
                onClick={() => setActiveTab('results')}
              >
                <img src="/image/results-svgrepo-com.svg" alt="results" className="nav-icon" />
                <span className="nav-label">{t('results')}</span>
              </button>
            </div>
          </nav>
        </aside>

        {/* conteúdo principal */}
        <main className="main-content">
          {activeTab === 'create' && (
            <div className="tab-content">
              <BedForm onJobCreated={handleJobCreated} />
            </div>
          )}

          {activeTab === 'wizard' && (
            <div className="tab-content">
              <BedWizard />
            </div>
          )}

          {activeTab === 'pipeline' && (
            <div className="tab-content">
              <PipelineCompleto />
            </div>
          )}

          {activeTab === 'cfd' && (
            <div className="tab-content">
              <CFDSimulation bedFileName={lastBedFile} />
            </div>
          )}

          {activeTab === 'casos' && (
            <div className="tab-content">
              <CasosCFD />
            </div>
          )}

          {activeTab === 'jobs' && (
            <div className="tab-content">
              <JobStatus currentJob={currentJob} />
            </div>
          )}

          {activeTab === 'results' && (
            <div className="tab-content">
              <ResultsList />
            </div>
          )}
        </main>
      </div>

      {/* footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section footer-info">
            <div className="footer-logo">
              <img 
                src="/image/logoCFDpipeline.png" 
                alt="cfd pipeline logo" 
                className="footer-icon"
              />
              <span className="footer-title">cfd pipeline</span>
            </div>
            <p className="footer-description">
              {language === 'pt' 
                ? 'sistema de simulação de leitos empacotados com openfoam e blender'
                : 'packed bed simulation system with openfoam and blender'}
            </p>
            <div className="footer-version">
              <span className="version-badge">v0.1.0</span>
              <span className="version-status">beta</span>
            </div>
          </div>

          <div className="footer-section footer-links">
            <h4>{language === 'pt' ? 'projeto' : 'project'}</h4>
            <ul>
              <li>
                <a href="https://github.com/bengo501/CFD-PIPELINE-TCC-1" target="_blank" rel="noopener noreferrer">
                  <ThemeIcon light="githubLight.png" dark="github.png" alt="github" className="link-icon" />
                  github
                </a>
              </li>
              <li>
                <a href="https://github.com/bengo501/CFD-PIPELINE-TCC-1/issues" target="_blank" rel="noopener noreferrer">
                  <ThemeIcon light="issuesLight.png" dark="issuesDark.png" alt="issues" className="link-icon" />
                  {language === 'pt' ? 'issues' : 'issues'}
                </a>
              </li>
              <li>
                <a href="https://github.com/users/bengo501/projects/2" target="_blank" rel="noopener noreferrer">
                  <ThemeIcon light="kanbanLight.png" dark="kanbanDark.png" alt="kanban" className="link-icon" />
                  {language === 'pt' ? 'kanban' : 'kanban'}
                </a>
              </li>
            </ul>
          </div>

          <div className="footer-section footer-tech">
            <h4>{language === 'pt' ? 'tecnologias' : 'technologies'}</h4>
            <ul>
              <li>
                <span className="tech-icon openfoam-icon">🌊</span>
                <span className="tech-badge">openfoam</span>
                <span className="tech-version">11</span>
              </li>
              <li>
                <ThemeIcon light="blenderLight.png" dark="blender-svgrepo-com.svg" alt="blender" className="tech-icon" />
                <span className="tech-badge">blender</span>
                <span className="tech-version">4.x</span>
              </li>
              <li>
                <ThemeIcon light="reactLight.png" dark="free-react-logo-icon-svg-download-png-3032257.png" alt="react" className="tech-icon" />
                <span className="tech-badge">react</span>
                <span className="tech-version">18</span>
              </li>
              <li>
                <ThemeIcon light="fastApiLight.png" dark="fastApiLight.png" alt="fastapi" className="tech-icon" />
                <span className="tech-badge">fastapi</span>
                <span className="tech-version">0.x</span>
              </li>
              <li>
                <ThemeIcon light="railwayLight.png" dark="railway.png" alt="railway" className="tech-icon" />
                <span className="tech-badge">railway</span>
                <span className="tech-version">cloud</span>
              </li>
            </ul>
          </div>

          <div className="footer-section footer-database">
            <h4>{language === 'pt' ? 'banco de dados' : 'database'}</h4>
            <ul>
              <li>
                <ThemeIcon light="2106624.png" dark="postgresqlDark.png" alt="postgresql" className="db-icon" />
                <span className="db-badge">postgresql</span>
                <span className="db-version">15</span>
              </li>
              <li>
                <ThemeIcon light="redis.png" dark="redisDark.png" alt="redis" className="db-icon" />
                <span className="db-badge">redis</span>
                <span className="db-version">7</span>
              </li>
              <li>
                <ThemeIcon light="minio.png" dark="minioDark.png" alt="minio" className="db-icon" />
                <span className="db-badge">minio</span>
                <span className="db-version">s3</span>
              </li>
            </ul>
          </div>

          <div className="footer-section footer-academic">
            <h4>{language === 'pt' ? 'acadêmico' : 'academic'}</h4>
            <div className="academic-logos">
              <img 
                src="/image/logo-light.png" 
                alt="pucrs logo" 
                className="academic-logo"
              />
              <img 
                src="/image/escola-politecnica.png" 
                alt="escola politecnica" 
                className="academic-logo"
              />
              <img 
                src="/image/logo_lope.png" 
                alt="lope laboratorio" 
                className="academic-logo"
              />
            </div>
            <p className="academic-info">
              <strong>{language === 'pt' ? 'tcc' : 'final project'}</strong><br />
              {language === 'pt' ? 'ciência da computação' : 'computer science'}<br />
              {language === 'pt' ? 'engenharia química' : 'chemical engineering'}
            </p>
            <p className="academic-year">2024/2025</p>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <p className="copyright">
              © 2024-2025 cfd pipeline. 
              {language === 'pt' ? ' código aberto sob licença mit.' : ' open source under mit license.'}
            </p>
            <div className="footer-social">
              <a href="https://github.com/bengo501" target="_blank" rel="noopener noreferrer" title="github profile">
                <span className="social-icon">🐙</span>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

