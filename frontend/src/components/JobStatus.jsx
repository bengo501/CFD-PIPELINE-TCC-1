import { useState, useEffect } from 'react'
import { getJobStatus, listJobs } from '../services/api'
import ThemeIcon from './ThemeIcon'

function JobStatus({ currentJob }) {
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadJobs()
    
    // atualizar a cada 2 segundos
    const interval = setInterval(loadJobs, 2000)
    
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (currentJob) {
      setSelectedJob(currentJob)
    }
  }, [currentJob])

  const loadJobs = async () => {
    try {
      const jobsList = await listJobs()
      setJobs(jobsList)
      
      // atualizar job selecionado se existir
      if (selectedJob) {
        const updated = jobsList.find(j => j.job_id === selectedJob.job_id)
        if (updated) {
          setSelectedJob(updated)
        }
      }
    } catch (error) {
      console.error('erro ao carregar jobs:', error)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'queued': return '⏳'
      case 'running': return '🔄'
      case 'completed': return '✅'
      case 'failed': return '❌'
      default: return '❔'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'queued': return 'status-queued'
      case 'running': return 'status-running'
      case 'completed': return 'status-completed'
      case 'failed': return 'status-failed'
      default: return ''
    }
  }

  const getJobTypeLabel = (jobType) => {
    switch (jobType) {
      case 'compile': return (
        <>
          <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="compilação" className="status-icon" />
          compilação
        </>
      )
      case 'generate_model': return '🎨 modelo 3d'
      case 'simulation': return '🌊 simulação'
      case 'full_pipeline': return '🚀 pipeline completo'
      default: return jobType
    }
  }

  return (
    <div className="job-status-container">
      <h2>
        <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="monitoramento" className="section-icon" />
        monitoramento de jobs
      </h2>

      <div className="jobs-layout">
        {/* lista de jobs */}
        <div className="jobs-list">
          <h3>todos os jobs ({jobs.length})</h3>
          
          {jobs.length === 0 ? (
            <p className="empty-state">nenhum job encontrado</p>
          ) : (
            <div className="jobs-items">
              {jobs.map(job => (
                <div
                  key={job.job_id}
                  className={`job-item ${selectedJob?.job_id === job.job_id ? 'selected' : ''}`}
                  onClick={() => setSelectedJob(job)}
                >
                  <div className="job-header">
                    <span className="job-icon">{getStatusIcon(job.status)}</span>
                    <span className="job-type">{getJobTypeLabel(job.job_type)}</span>
                  </div>
                  
                  <div className={`job-status ${getStatusColor(job.status)}`}>
                    {job.status}
                  </div>
                  
                  <div className="job-progress">
                    <div
                      className="progress-bar"
                      style={{ width: `${job.progress}%` }}
                    />
                    <span className="progress-text">{job.progress}%</span>
                  </div>
                  
                  <div className="job-time">
                    {new Date(job.created_at).toLocaleString('pt-BR')}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* detalhes do job selecionado */}
        <div className="job-details">
          {selectedJob ? (
            <>
              <h3>detalhes do job</h3>
              
              <div className="detail-group">
                <label>id:</label>
                <code>{selectedJob.job_id}</code>
              </div>

              <div className="detail-group">
                <label>tipo:</label>
                <span>{getJobTypeLabel(selectedJob.job_type)}</span>
              </div>

              <div className="detail-group">
                <label>status:</label>
                <span className={`badge ${getStatusColor(selectedJob.status)}`}>
                  {getStatusIcon(selectedJob.status)} {selectedJob.status}
                </span>
              </div>

              <div className="detail-group">
                <label>progresso:</label>
                <div className="progress-bar-large">
                  <div
                    className="progress-fill"
                    style={{ width: `${selectedJob.progress}%` }}
                  />
                  <span className="progress-label">{selectedJob.progress}%</span>
                </div>
              </div>

              <div className="detail-group">
                <label>criado em:</label>
                <span>{new Date(selectedJob.created_at).toLocaleString('pt-BR')}</span>
              </div>

              <div className="detail-group">
                <label>atualizado em:</label>
                <span>{new Date(selectedJob.updated_at).toLocaleString('pt-BR')}</span>
              </div>

              {selectedJob.output_files && selectedJob.output_files.length > 0 && (
                <div className="detail-group">
                  <label>arquivos gerados:</label>
                  <ul className="output-files">
                    {selectedJob.output_files.map((file, idx) => (
                      <li key={idx}>
                        <code>{file}</code>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedJob.error_message && (
                <div className="detail-group">
                  <label>erro:</label>
                  <div className="error-message">
                    {selectedJob.error_message}
                  </div>
                </div>
              )}

              {selectedJob.metadata && Object.keys(selectedJob.metadata).length > 0 && (
                <div className="detail-group">
                  <label>metadata:</label>
                  <pre className="metadata">
                    {JSON.stringify(selectedJob.metadata, null, 2)}
                  </pre>
                </div>
              )}
            </>
          ) : (
            <p className="empty-state">selecione um job para ver detalhes</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default JobStatus

