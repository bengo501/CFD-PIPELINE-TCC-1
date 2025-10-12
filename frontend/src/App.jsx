import { useState, useEffect } from 'react'
import BedForm from './components/BedForm'
import BedWizard from './components/BedWizard'
import CFDSimulation from './components/CFDSimulation'
import JobStatus from './components/JobStatus'
import ModelViewer from './components/ModelViewer'
import ResultsList from './components/ResultsList'
import { getSystemStatus } from './services/api'

function App() {
  const [activeTab, setActiveTab] = useState('create') // create, wizard, cfd, jobs, results
  const [systemStatus, setSystemStatus] = useState(null)
  const [currentJob, setCurrentJob] = useState(null)
  const [lastBedFile, setLastBedFile] = useState(null)

  useEffect(() => {
    // verificar status do sistema ao carregar
    checkSystemStatus()
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
      <header className="header">
        <div className="header-content">
          <h1>🔬 CFD Pipeline - Leitos Empacotados</h1>
          <div className="system-status">
            {systemStatus && (
              <>
                <span className={`status-indicator ${systemStatus.api === 'running' ? 'online' : 'offline'}`}>
                  {systemStatus.api === 'running' ? '🟢 online' : '🔴 offline'}
                </span>
                <span className="jobs-count">
                  jobs: {systemStatus.jobs?.running || 0} em execução
                </span>
              </>
            )}
          </div>
        </div>
      </header>

      {/* navegação */}
      <nav className="tabs">
        <button
          className={`tab ${activeTab === 'create' ? 'active' : ''}`}
          onClick={() => setActiveTab('create')}
        >
          ✨ criar leito
        </button>
        <button
          className={`tab ${activeTab === 'wizard' ? 'active' : ''}`}
          onClick={() => setActiveTab('wizard')}
        >
          🧙 wizard interativo
        </button>
        <button
          className={`tab ${activeTab === 'cfd' ? 'active' : ''}`}
          onClick={() => setActiveTab('cfd')}
        >
          🌊 simulacao cfd
        </button>
        <button
          className={`tab ${activeTab === 'jobs' ? 'active' : ''}`}
          onClick={() => setActiveTab('jobs')}
        >
          📊 jobs ({systemStatus?.jobs?.total || 0})
        </button>
        <button
          className={`tab ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          📁 resultados
        </button>
      </nav>

      {/* conteúdo */}
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

        {activeTab === 'cfd' && (
          <div className="tab-content">
            <CFDSimulation bedFileName={lastBedFile} />
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

      {/* footer */}
      <footer className="footer">
        <p>cfd pipeline v0.1.0 | tcc - eng. mecânica</p>
      </footer>
    </div>
  )
}

export default App

