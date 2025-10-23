import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import SimulationHistory from './components/SimulationHistory'
import BedForm from './components/BedForm'
import BedWizard from './components/BedWizard'
import CFDSimulation from './components/CFDSimulation'
import PipelineCompleto from './components/PipelineCompleto'
import CasosCFD from './components/CasosCFD'
import JobStatus from './components/JobStatus'
import ModelViewer from './components/ModelViewer'
import ResultsList from './components/ResultsList'
import TemplateEditor from './components/TemplateEditor'
import ThemeIcon from './components/ThemeIcon'
import { HelpModal, DocsModal } from './components/WizardHelpers'
import { getSystemStatus } from './services/api'
import { useLanguage } from './context/LanguageContext'
import { useTheme } from './context/ThemeContext'

function App() {
  const { language, toggleLanguage, t } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('dashboard') // dashboard, create, wizard, pipeline, cfd, jobs, results
  const [systemStatus, setSystemStatus] = useState(null)
  const [currentJob, setCurrentJob] = useState(null)
  const [lastBedFile, setLastBedFile] = useState(null)
  const [isScrolled, setIsScrolled] = useState(false)
  const [showHelp, setShowHelp] = useState(false)
  const [showDocs, setShowDocs] = useState(false)

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
                <h1>{activeTab === 'dashboard' ? 'Dashboard CFD' : 'CFD Pipeline'}</h1>
                <span className="subtitle">packed beds - computational fluid dynamics</span>
              </div>
            </div>
          </div>
          
          <div className="header-right">
            {activeTab === 'dashboard' && (
              <button className="new-simulation-btn">
                <ThemeIcon light="runLight.png" dark="runDark.png" alt="nova simulação" className="btn-icon" />
                {language === 'pt' ? '+ Nova Simulação' : '+ New Simulation'}
              </button>
            )}
            <div className="system-status">
              {systemStatus && (
                <>
                  <div className="status-item">
                    <ThemeIcon 
                      light={systemStatus.api === 'running' ? "onlineLight.png" : "offlineLight.png"} 
                      dark={systemStatus.api === 'running' ? "onlineDark.png" : "offlineDark.png"} 
                      alt={systemStatus.api === 'running' ? 'online' : 'offline'} 
                      className="status-icon" 
                    />
                    <span className="status-label">
                      {systemStatus.api === 'running' ? t('online') : t('offline')}
                    </span>
                  </div>
                  <div className="status-item">
                    <ThemeIcon light="jobLight.png" dark="jobDark.png" alt="jobs" className="status-icon" />
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
              <h3 className="nav-section-title">{language === 'pt' ? 'dashboard' : 'dashboard'}</h3>
              <button
                className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => setActiveTab('dashboard')}
              >
                <ThemeIcon light="dashboardLight.png" dark="dashboardDark.png" alt="dashboard" className="nav-icon" />
                <span className="nav-label">{language === 'pt' ? 'dashboard' : 'dashboard'}</span>
              </button>
            </div>

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
              <button
                className={`nav-item ${activeTab === 'templates-saved' ? 'active' : ''}`}
                onClick={() => setActiveTab('templates-saved')}
              >
                <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="templates salvos" className="nav-icon" />
                <span className="nav-label">{language === 'pt' ? 'templates salvos' : 'saved templates'}</span>
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
              <h3 className="nav-section-title">{language === 'pt' ? 'banco de dados' : 'database'}</h3>
              <button
                className={`nav-item ${activeTab === 'database' ? 'active' : ''}`}
                onClick={() => setActiveTab('database')}
              >
                <ThemeIcon light="databaseLight.png" dark="databaseDark.png" alt="banco de dados" className="nav-icon" />
                <span className="nav-label">{language === 'pt' ? 'banco de dados' : 'database'}</span>
              </button>
            </div>

            <div className="nav-section">
              <h3 className="nav-section-title">{language === 'pt' ? 'análises' : 'analysis'}</h3>
              <button
                className={`nav-item ${activeTab === 'analysis' ? 'active' : ''}`}
                onClick={() => setActiveTab('analysis')}
              >
                <ThemeIcon light="analiseLight.png" dark="analiseDark.png" alt="análises" className="nav-icon" />
                <span className="nav-label">{language === 'pt' ? 'análises' : 'analysis'}</span>
              </button>
              <button
                className={`nav-item ${activeTab === 'comparisons' ? 'active' : ''}`}
                onClick={() => setActiveTab('comparisons')}
              >
                <ThemeIcon light="compareLight.png" dark="compareDark.png" alt="comparações" className="nav-icon" />
                <span className="nav-label">{language === 'pt' ? 'comparações' : 'comparisons'}</span>
              </button>
              <button
                className={`nav-item ${activeTab === 'reports' ? 'active' : ''}`}
                onClick={() => setActiveTab('reports')}
              >
                <ThemeIcon light="reportLight.png" dark="reportDark.png" alt="relatórios" className="nav-icon" />
                <span className="nav-label">{language === 'pt' ? 'relatórios' : 'reports'}</span>
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
              <button
                className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
                onClick={() => setActiveTab('history')}
              >
                <ThemeIcon light="historyLight.png" dark="historyDark.png" alt="histórico" className="nav-icon" />
                <span className="nav-label">{language === 'pt' ? 'histórico' : 'history'}</span>
              </button>
            </div>

            <div className="nav-section">
              <h3 className="nav-section-title">{language === 'pt' ? 'perfil' : 'profile'}</h3>
              <button
                className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
                onClick={() => setActiveTab('profile')}
              >
                <ThemeIcon light="profileLight.png" dark="profileDark.png" alt="perfil" className="nav-icon" />
                <span className="nav-label">{language === 'pt' ? 'perfil' : 'profile'}</span>
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

          {activeTab === 'history' && (
            <div className="tab-content">
              <SimulationHistory />
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="tab-content">
              <TemplateEditor />
            </div>
          )}

          {activeTab === 'templates-saved' && (
            <div className="tab-content">
              <div className="page-container">
                <div className="wip-header">
                  <ThemeIcon light="wipLogoLight.png" dark="wipLogoDark.png" alt="work in progress" className="wip-logo" />
                  <h2>{language === 'pt' ? 'templates salvos' : 'saved templates'}</h2>
                </div>
                <p>{language === 'pt' ? 'gerencie seus templates salvos' : 'manage your saved templates'}</p>
                <div className="info-message">
                  {language === 'pt' ? 'funcionalidade em desenvolvimento' : 'feature under development'}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'database' && (
            <div className="tab-content">
              <div className="page-container">
                <div className="wip-header">
                  <ThemeIcon light="wipLogoLight.png" dark="wipLogoDark.png" alt="work in progress" className="wip-logo" />
                  <h2>{language === 'pt' ? 'banco de dados' : 'database'}</h2>
                </div>
                <p>{language === 'pt' ? 'gerencie o banco de dados do sistema' : 'manage system database'}</p>
                <div className="info-message">
                  {language === 'pt' ? 'funcionalidade em desenvolvimento' : 'feature under development'}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="tab-content">
              <div className="page-container">
                <div className="wip-header">
                  <ThemeIcon light="wipLogoLight.png" dark="wipLogoDark.png" alt="work in progress" className="wip-logo" />
                  <h2>{language === 'pt' ? 'análises' : 'analysis'}</h2>
                </div>
                <p>{language === 'pt' ? 'realize análises dos resultados' : 'perform result analysis'}</p>
                <div className="info-message">
                  {language === 'pt' ? 'funcionalidade em desenvolvimento' : 'feature under development'}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'comparisons' && (
            <div className="tab-content">
              <div className="page-container">
                <div className="wip-header">
                  <ThemeIcon light="wipLogoLight.png" dark="wipLogoDark.png" alt="work in progress" className="wip-logo" />
                  <h2>{language === 'pt' ? 'comparações' : 'comparisons'}</h2>
                </div>
                <p>{language === 'pt' ? 'compare diferentes simulações' : 'compare different simulations'}</p>
                <div className="info-message">
                  {language === 'pt' ? 'funcionalidade em desenvolvimento' : 'feature under development'}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="tab-content">
              <div className="page-container">
                <div className="wip-header">
                  <ThemeIcon light="wipLogoLight.png" dark="wipLogoDark.png" alt="work in progress" className="wip-logo" />
                  <h2>{language === 'pt' ? 'relatórios' : 'reports'}</h2>
                </div>
                <p>{language === 'pt' ? 'gere relatórios das simulações' : 'generate simulation reports'}</p>
                <div className="info-message">
                  {language === 'pt' ? 'funcionalidade em desenvolvimento' : 'feature under development'}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="tab-content">
              <div className="page-container">
                <div className="wip-header">
                  <ThemeIcon light="wipLogoLight.png" dark="wipLogoDark.png" alt="work in progress" className="wip-logo" />
                  <h2>{language === 'pt' ? 'histórico' : 'history'}</h2>
                </div>
                <p>{language === 'pt' ? 'visualize o histórico das simulações' : 'view simulation history'}</p>
                <div className="info-message">
                  {language === 'pt' ? 'funcionalidade em desenvolvimento' : 'feature under development'}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'dashboard' && (
            <div className="tab-content">
              <Dashboard />
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="tab-content">
              <div className="page-container">
                <div className="wip-header">
                  <ThemeIcon light="wipLogoLight.png" dark="wipLogoDark.png" alt="work in progress" className="wip-logo" />
                  <h2>{language === 'pt' ? 'perfil' : 'profile'}</h2>
                </div>
                <p>{language === 'pt' ? 'gerencie seu perfil e configurações pessoais' : 'manage your profile and personal settings'}</p>
                <div className="info-message">
                  {language === 'pt' ? 'funcionalidade em desenvolvimento' : 'feature under development'}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="tab-content">
              <div className="settings-container">
                <h2>{t('systemSettings')}</h2>
                <div className="development-notice">
                  <p>esta página está em desenvolvimento</p>
                </div>
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
              <li>
                <button className="footer-help-btn" onClick={() => setShowHelp(true)}>
                  <ThemeIcon light="helpLight.png" dark="helpDark.png" alt="ajuda" className="link-icon" />
                  {language === 'pt' ? 'ajuda' : 'help'}
                </button>
              </li>
              <li>
                <button className="footer-docs-btn" onClick={() => setShowDocs(true)}>
                  <ThemeIcon light="docsLight.png" dark="docsDark.png" alt="documentação" className="link-icon" />
                  {language === 'pt' ? 'documentação' : 'documentation'}
                </button>
              </li>
              <li>
                <a href="https://github.com/bengo501" target="_blank" rel="noopener noreferrer">
                  <ThemeIcon light="githubProfileLight.png" dark="GithubProfileDark.png" alt="github profile" className="link-icon" />
                  {language === 'pt' ? 'perfil github' : 'github profile'}
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
                <ThemeIcon light="viteLight.png" dark="viteDark.png" alt="vite" className="tech-icon" />
                <span className="tech-badge">vite</span>
                <span className="tech-version">5.x</span>
              </li>
              <li>
                <ThemeIcon light="pythonLogoLight.png" dark="pythonLogoDark.png" alt="python" className="tech-icon" />
                <span className="tech-badge">python</span>
                <span className="tech-version">3.11</span>
              </li>
              <li>
                <ThemeIcon light="wslLogoLight.png" dark="wslLogoDark.png" alt="wsl" className="tech-icon" />
                <span className="tech-badge">wsl</span>
                <span className="tech-version">2</span>
              </li>
              <li>
                <ThemeIcon light="jsLight.png" dark="jsDark.png" alt="javascript" className="tech-icon" />
                <span className="tech-badge">javascript</span>
                <span className="tech-version">es6+</span>
              </li>
              <li>
                <ThemeIcon light="javaLight.png" dark="javaDark.png" alt="java" className="tech-icon" />
                <span className="tech-badge">java</span>
                <span className="tech-version">17</span>
              </li>
              <li>
                <ThemeIcon light="cssLight.png" dark="cssDark.png" alt="css" className="tech-icon" />
                <span className="tech-badge">css</span>
                <span className="tech-version">3</span>
              </li>
              <li>
                <ThemeIcon light="antlrLight.png" dark="antlrDark.png" alt="antlr" className="tech-icon" />
                <span className="tech-badge">antlr</span>
                <span className="tech-version">4.x</span>
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

      {/* modais de ajuda e documentação */}
      <HelpModal 
        show={showHelp} 
        onClose={() => setShowHelp(false)} 
        section="general"
        paramHelp={{
          'bed.diameter': {
            desc: 'diâmetro interno do leito cilíndrico',
            min: 0.01,
            max: 1.0,
            unit: 'm',
            exemplo: '0.05m para leito de 5cm'
          },
          'bed.height': {
            desc: 'altura do leito empacotado',
            min: 0.01,
            max: 2.0,
            unit: 'm',
            exemplo: '0.1m para leito de 10cm'
          },
          'particles.diameter': {
            desc: 'diâmetro das partículas esféricas',
            min: 0.001,
            max: 0.01,
            unit: 'm',
            exemplo: '0.005m para partículas de 5mm'
          },
          'particles.count': {
            desc: 'número de partículas no leito',
            min: 10,
            max: 10000,
            unit: '',
            exemplo: '100 partículas'
          }
        }}
      />
      
      <DocsModal 
        show={showDocs} 
        onClose={() => setShowDocs(false)} 
      />
    </div>
  )
}

export default App

