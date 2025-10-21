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
              <ThemeIcon 
                light="image-removebg-preview(15).png" 
                dark="darkmode_moon_sun_white.png" 
                alt={theme === 'light' ? 'dark mode' : 'light mode'} 
                className="theme-icon" 
              />
              <span className="theme-text">{theme === 'light' ? (language === 'pt' ? 'escuro' : 'dark') : (language === 'pt' ? 'claro' : 'light')}</span>
            </button>
            
            <button 
              className="language-toggle" 
              onClick={toggleLanguage} 
              title={language === 'pt' ? 'switch to english' : 'mudar para português'}
              aria-label={language === 'pt' ? 'mudar idioma' : 'change language'}
            >
              <ThemeIcon 
                light={language === 'pt' ? "brazil_flag_icon_black.png" : "usa_flag_icon_black_50stars.png"} 
                dark={language === 'pt' ? "brazil_flag_icon_white.png" : "usa_flag_icon_white_50stars.png"} 
                alt={language === 'pt' ? 'brasil' : 'usa'} 
                className="flag" 
              />
              <span className="lang-text">{language === 'pt' ? 'br' : 'us'}</span>
            </button>
          </div>
        </div>
      </header>

      <div className="app-body">
        {/* sidebar */}
        <aside className="sidebar">
          <nav className="sidebar-nav">
            <div className="nav-section">
              <h3 className="nav-section-title">{t('create')}</h3>
              <button
                className={`nav-item ${activeTab === 'wizard' ? 'active' : ''}`}
                onClick={() => setActiveTab('wizard')}
              >
                <ThemeIcon light="create_bed_white.png" dark="image-removebg-preview(14).png" alt="criar leito" className="nav-icon" />
                <span className="nav-label">{t('createBed')}</span>
              </button>
            </div>

            <div className="nav-section">
              <h3 className="nav-section-title">templates</h3>
              <button
                className={`nav-item ${activeTab === 'templates' ? 'active' : ''}`}
                onClick={() => setActiveTab('templates')}
              >
                <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="templates" className="nav-icon" />
                <span className="nav-label">templates</span>
              </button>
            </div>

            <div className="nav-section">
              <h3 className="nav-section-title">{t('simulation')}</h3>
              <button
                className={`nav-item ${activeTab === 'cfd' ? 'active' : ''}`}
                onClick={() => setActiveTab('cfd')}
              >
                <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="simulações CFD" className="nav-icon" />
                <span className="nav-label">{t('cfdSimulation')}</span>
              </button>
              <button
                className={`nav-item ${activeTab === 'casos' ? 'active' : ''}`}
                onClick={() => setActiveTab('casos')}
              >
                <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="casos cfd" className="nav-icon" />
                <span className="nav-label">{t('casosCfd')}</span>
              </button>
            </div>

            <div className="nav-section">
              <h3 className="nav-section-title">{t('results')}</h3>
              <button
                className={`nav-item ${activeTab === 'jobs' ? 'active' : ''}`}
                onClick={() => setActiveTab('jobs')}
              >
                <ThemeIcon light="jobLight.png" dark="jobDark.png" alt="jobs" className="nav-icon" />
                <span className="nav-label">{t('jobs')} ({systemStatus?.jobs?.total || 0})</span>
              </button>
              <button
                className={`nav-item ${activeTab === 'results' ? 'active' : ''}`}
                onClick={() => setActiveTab('results')}
              >
                <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="results" className="nav-icon" />
                <span className="nav-label">{t('results')}</span>
              </button>
            </div>

            <div className="nav-section">
              <h3 className="nav-section-title">settings</h3>
              <button
                className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
                onClick={() => setActiveTab('settings')}
              >
                <ThemeIcon light="settingsLight.png" dark="settingsDark.png" alt="settings" className="nav-icon" />
                <span className="nav-label">{t('configuracoes')}</span>
              </button>
            </div>
          </nav>
        </aside>

        {/* conteúdo principal */}
        <main className="main-content">
          {activeTab === 'wizard' && (
            <div className="tab-content">
              <BedWizard />
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

          {activeTab === 'templates' && (
            <div className="tab-content">
              <div className="templates-container">
                <h2>templates</h2>
                <div className="templates-grid">
                  <div className="template-card">
                    <h3>
                      <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="editor" className="section-icon" />
                      editor de template
                    </h3>
                    <p>edite um arquivo .bed diretamente</p>
                    <button 
                      className="btn-primary"
                      onClick={() => {
                        // implementar editor de template
                        alert('editor de template será implementado aqui');
                      }}
                    >
                      abrir editor
                    </button>
                  </div>
                  <div className="template-card">
                    <h3>
                      <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="gerenciar" className="section-icon" />
                      gerenciar templates
                    </h3>
                    <p>visualize, edite e delete templates salvos</p>
                    <button 
                      className="btn-secondary"
                      onClick={() => {
                        // implementar gerenciamento de templates
                        alert('funcionalidade em desenvolvimento');
                      }}
                    >
                      gerenciar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="tab-content">
              <div className="settings-container">
                <h2>{t('systemSettings')}</h2>
                <div className="settings-grid">
                  <div className="setting-card">
                    <h3>{t('theme')}</h3>
                    <p>{t('themeDesc')}</p>
                  </div>
                  <div className="setting-card">
                    <h3>{t('language')}</h3>
                    <p>{t('languageDesc')}</p>
                  </div>
                  <div className="setting-card">
                    <h3>{t('database')}</h3>
                    <p>{t('databaseDesc')}</p>
                  </div>
                  <div className="setting-card">
                    <h3>{t('simulations')}</h3>
                    <p>{t('simulationsDesc')}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section footer-info">
            <div className="footer-logo">
              <ThemeIcon 
                light="logoCFDpipeline.png" 
                dark="cfdPipelineLight.png" 
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
                <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="openfoam" className="tech-icon openfoam-icon" />
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

