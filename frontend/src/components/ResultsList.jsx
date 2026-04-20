import { useState, useEffect, useCallback } from 'react'
import {
  listModels3D,
  listSimulations,
  getSimulation,
  getSimulationResults,
  buildGeneratedFileUrl,
} from '../services/api'
import ModelViewer from './ModelViewer'
import ThemeIcon from './ThemeIcon'
import BackendConnectionError from './BackendConnectionError'
import { useLanguage } from '../context/LanguageContext'
import { useActiveUser } from '../context/UserContext'

function ResultsList() {
  const { t, language } = useLanguage()
  const { activeUserId } = useActiveUser()
  const [models, setModels] = useState([])
  const [simulations, setSimulations] = useState([])
  const [selectedModel, setSelectedModel] = useState(null)
  const [selectedSimulation, setSelectedSimulation] = useState(null)
  const [selectedSimulationResults, setSelectedSimulationResults] = useState([])
  const [simulationResultsLoading, setSimulationResultsLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [connectionError, setConnectionError] = useState(null)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      setConnectionError(null)
      const [modelsData, simsData] = await Promise.all([
        listModels3D({ page: 1, per_page: 100 }),
        listSimulations({ page: 1, per_page: 100 }),
      ])
      setModels(Array.isArray(modelsData?.items) ? modelsData.items : [])
      setSimulations(Array.isArray(simsData?.items) ? simsData.items : [])
    } catch (error) {
      console.error('erro ao carregar resultados reais:', error)
      setConnectionError(t('backendConnectionError'))
      setModels([])
      setSimulations([])
    } finally {
      setLoading(false)
    }
  }, [t])

  useEffect(() => {
    loadData()
    const timer = window.setInterval(loadData, 5000)
    return () => window.clearInterval(timer)
  }, [activeUserId, loadData])

  const handleOpenSimulationResults = async (simulationId) => {
    try {
      setSimulationResultsLoading(true)
      const [sim, results] = await Promise.all([
        getSimulation(simulationId),
        getSimulationResults(simulationId),
      ])
      setSelectedSimulation(sim)
      setSelectedSimulationResults(Array.isArray(results) ? results : [])
    } catch (error) {
      console.error('erro ao carregar resultados da simulação:', error)
      setConnectionError(t('backendConnectionError'))
    } finally {
      setSimulationResultsLoading(false)
    }
  }

  const handleDownloadSimulationJson = async (simulationId) => {
    try {
      const data = await getSimulation(simulationId)
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `simulacao_${simulationId}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (error) {
      console.error('erro ao baixar json da simulação:', error)
      setConnectionError(t('backendConnectionError'))
    }
  }

  const getModelPreviewPath = (model) => {
    return model.preview_model_url
      ? buildGeneratedFileUrl(model.preview_model_url.replace(/^\/files\//, ''))
      : buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path)
  }

  const getModelDownloadPath = (model) => {
    return buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path)
  }

  return (
    <div className="results-container">
      <h2>
        <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="resultados" className="section-icon" />
        {language === 'pt' ? 'resultados' : 'results'}
      </h2>

      {connectionError && <BackendConnectionError message={connectionError} />}

      <div className="results-layout">
        <section className="results-section">
          <h3>
            <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="modelos" className="section-icon" />
            {language === 'pt' ? 'modelos 3d' : '3d models'} ({models.length})
          </h3>

          {loading ? (
            <p>{language === 'pt' ? 'carregando...' : 'loading...'}</p>
          ) : models.length === 0 ? (
            <p className="empty-state">{language === 'pt' ? 'nenhum modelo encontrado' : 'no models found'}</p>
          ) : (
            <div className="files-grid">
              {models.map((model) => (
                <div key={model.id} className="file-card">
                  <div className="file-icon">
                    <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="modelo" className="file-icon-img" />
                  </div>

                  <div className="file-info">
                    <h4 className="file-name">{model.name}</h4>
                    <p className="file-size">id {model.id}</p>
                    <p className="file-date">
                      {model.created_at
                        ? new Date(model.created_at).toLocaleDateString(language === 'pt' ? 'pt-BR' : 'en-US')
                        : '—'}
                    </p>
                    <p className="file-size">
                      {model.blend_file_path ? '.blend ' : ''}
                      {model.stl_file_path ? '.stl' : ''}
                    </p>
                  </div>

                  <div className="file-actions">
                    <button
                      className="btn-small"
                      onClick={() => setSelectedModel({ ...model, path: getModelPreviewPath(model) })}
                      disabled={!getModelPreviewPath(model)}
                    >
                      <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="visualizar" className="btn-icon" />
                      {language === 'pt' ? 'visualizar' : 'view'}
                    </button>
                    <button
                      className="btn-small"
                      onClick={() => window.open(getModelDownloadPath(model), '_blank')}
                      disabled={!getModelDownloadPath(model)}
                    >
                      <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="baixar" className="btn-icon" />
                      {language === 'pt' ? 'baixar' : 'download'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="results-section">
          <h3>
            <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="simulações" className="section-icon" />
            {language === 'pt' ? 'simulações' : 'simulations'} ({simulations.length})
          </h3>

          {loading ? (
            <p>{language === 'pt' ? 'carregando...' : 'loading...'}</p>
          ) : simulations.length === 0 ? (
            <p className="empty-state">{language === 'pt' ? 'nenhuma simulação encontrada' : 'no simulations found'}</p>
          ) : (
            <div className="files-grid">
              {simulations.map((sim) => (
                <div key={sim.id} className="file-card">
                  <div className="file-icon">
                    <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="simulação" className="file-icon-img" />
                  </div>

                  <div className="file-info">
                    <h4 className="file-name">{sim.name}</h4>
                    <p className="file-size">id {sim.id}</p>
                    <p className="file-date">
                      {sim.created_at
                        ? new Date(sim.created_at).toLocaleDateString(language === 'pt' ? 'pt-BR' : 'en-US')
                        : '—'}
                    </p>
                    <p className="file-size">{sim.status}</p>
                  </div>

                  <div className="file-actions">
                    <button
                      className="btn-small"
                      onClick={() => handleOpenSimulationResults(sim.id)}
                    >
                      <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="resultados" className="btn-icon" />
                      {language === 'pt' ? 'resultados' : 'results'}
                    </button>
                    <button
                      className="btn-small"
                      onClick={() => handleDownloadSimulationJson(sim.id)}
                    >
                      <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="baixar" className="btn-icon" />
                      json
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {selectedModel && (
        <div className="modal-overlay" onClick={() => setSelectedModel(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close"
              onClick={() => setSelectedModel(null)}
            >
              x
            </button>

            <h3>{language === 'pt' ? 'visualização 3d' : '3d preview'}: {selectedModel.name}</h3>

            <ModelViewer modelPath={selectedModel.path} />
          </div>
        </div>
      )}

      {selectedSimulation && (
        <div className="modal-overlay" onClick={() => setSelectedSimulation(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close"
              onClick={() => setSelectedSimulation(null)}
            >
              x
            </button>

            <h3>{language === 'pt' ? 'resultados da simulação' : 'simulation results'}: {selectedSimulation.name}</h3>

            {simulationResultsLoading ? (
              <p>{language === 'pt' ? 'carregando...' : 'loading...'}</p>
            ) : selectedSimulationResults.length === 0 ? (
              <p>{language === 'pt' ? 'nenhum resultado persistido para esta simulação' : 'no persisted results for this simulation'}</p>
            ) : (
              <div className="files-grid">
                {selectedSimulationResults.map((result) => (
                  <div key={result.id} className="file-card">
                    <div className="file-info">
                      <h4 className="file-name">{result.name}</h4>
                      <p className="file-size">{result.result_type}</p>
                      <p className="file-date">
                        {result.value != null ? `${result.value} ${result.unit || ''}`.trim() : (language === 'pt' ? 'sem valor escalar' : 'no scalar value')}
                      </p>
                      <p className="file-size">{result.file_type || 'json'}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ResultsList

