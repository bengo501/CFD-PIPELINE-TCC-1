import { useState, useEffect } from 'react'
import { listFiles, downloadFile } from '../services/api'
import ModelViewer from './ModelViewer'
import ThemeIcon from './ThemeIcon'

function ResultsList() {
  const [models, setModels] = useState([])
  const [simulations, setSimulations] = useState([])
  const [selectedModel, setSelectedModel] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadFiles()
  }, [])

  const loadFiles = async () => {
    setLoading(true)
    try {
      // carregar modelos
      const modelsData = await listFiles('blend')
      setModels(modelsData.files)

      // carregar simulações
      const simsData = await listFiles('simulations')
      setSimulations(simsData.files)
    } catch (error) {
      console.error('erro ao carregar arquivos:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const handleDownload = (fileType, filename) => {
    const url = downloadFile(fileType, filename)
    window.open(url, '_blank')
  }

  return (
    <div className="results-container">
      <h2>
        <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="resultados" className="section-icon" />
        resultados
      </h2>

      <div className="results-layout">
        {/* modelos 3d */}
        <section className="results-section">
          <h3>
            <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="modelos" className="section-icon" />
            modelos 3d ({models.length})
          </h3>
          
          {loading ? (
            <p>carregando...</p>
          ) : models.length === 0 ? (
            <p className="empty-state">nenhum modelo encontrado</p>
          ) : (
            <div className="files-grid">
              {models.map((file, idx) => (
                <div key={idx} className="file-card">
                  <div className="file-icon">
                    <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="modelo" className="file-icon-img" />
                  </div>
                  
                  <div className="file-info">
                    <h4 className="file-name">{file.filename}</h4>
                    <p className="file-size">{formatFileSize(file.size)}</p>
                    <p className="file-date">
                      {new Date(file.created_at).toLocaleDateString('pt-BR')}
                    </p>
                  </div>

                  <div className="file-actions">
                    <button
                      className="btn-small"
                      onClick={() => setSelectedModel(file)}
                    >
                      <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="visualizar" className="btn-icon" />
                      visualizar
                    </button>
                    <button
                      className="btn-small"
                      onClick={() => handleDownload('blend', file.filename)}
                    >
                      <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="baixar" className="btn-icon" />
                      baixar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* simulações */}
        <section className="results-section">
          <h3>
            <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="simulações" className="section-icon" />
            simulações ({simulations.length})
          </h3>
          
          {loading ? (
            <p>carregando...</p>
          ) : simulations.length === 0 ? (
            <p className="empty-state">nenhuma simulação encontrada</p>
          ) : (
            <div className="files-grid">
              {simulations.map((sim, idx) => (
                <div key={idx} className="file-card">
                  <div className="file-icon">📊</div>
                  
                  <div className="file-info">
                    <h4 className="file-name">{sim.filename}</h4>
                    <p className="file-size">{formatFileSize(sim.size)}</p>
                    <p className="file-date">
                      {new Date(sim.created_at).toLocaleDateString('pt-BR')}
                    </p>
                  </div>

                  <div className="file-actions">
                    <button
                      className="btn-small"
                      onClick={() => alert('visualização de resultados em desenvolvimento')}
                    >
                      📈 resultados
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* modal de visualização */}
      {selectedModel && (
        <div className="modal-overlay" onClick={() => setSelectedModel(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close"
              onClick={() => setSelectedModel(null)}
            >
              ✕
            </button>
            
            <h3>visualização 3d: {selectedModel.filename}</h3>
            
            <ModelViewer modelPath={selectedModel.path} />
          </div>
        </div>
      )}
    </div>
  )
}

export default ResultsList

