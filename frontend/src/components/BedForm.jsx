import { useState } from 'react'
import { compileBed, generateModel } from '../services/api'
import { useTheme } from '../context/ThemeContext'
import { useLanguage } from '../context/LanguageContext'
import { useTranslation } from '../i18n/translations'
import ThemeIcon from './ThemeIcon'

function BedForm({ onJobCreated }) {
  const { theme } = useTheme()
  const { language } = useLanguage()
  const { t } = useTranslation(language)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  
  const [parameters, setParameters] = useState({
    diameter: 0.05,
    height: 0.1,
    wall_thickness: 0.002,
    particle_count: 100,
    particle_type: 'sphere',
    particle_diameter: 0.005,
    packing_method: 'rigid_body',
    gravity: -9.81,
    friction: 0.5,
    substeps: 10
  })

  const handleChange = (e) => {
    const { name, value, type } = e.target
    setParameters(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      // passo 1: compilar .bed
      console.log('compilando .bed...')
      const compileResult = await compileBed(parameters)
      
      setSuccess(`✅ arquivo compilado: ${compileResult.bed_file}`)
      
      // passo 2: gerar modelo 3d
      console.log('gerando modelo 3d...')
      const modelJob = await generateModel(compileResult.json_file, false)
      
      setSuccess(`✅ modelo 3d em geração (job: ${modelJob.job_id})`)
      
      // notificar componente pai
      if (onJobCreated) {
        onJobCreated(modelJob)
      }

    } catch (err) {
      console.error('erro:', err)
      setError(err.response?.data?.detail || err.message || 'erro desconhecido')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bed-form-container">
      <h2>
        <ThemeIcon light="parametros_leito_white_v2.png" dark="image-removebg-preview(9).png" alt="parâmetros" className="section-icon" />
        {t('parametrosLeito')}
      </h2>
      
      {error && (
        <div className="alert alert-error">
          ❌ {error}
        </div>
      )}
      
      {success && (
        <div className="alert alert-success">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bed-form">
        {/* geometria do leito */}
        <fieldset>
          <legend>
            <ThemeIcon light="bed_geometry_white.png" dark="bed_geometry_black.png" alt="geometria" className="legend-icon" />
            {t('geometriaLeito')}
          </legend>
          
          <div className="form-group">
            <label>
              diâmetro (m):
              <input
                type="number"
                name="diameter"
                value={parameters.diameter}
                onChange={handleChange}
                step="0.001"
                min="0.01"
                max="1.0"
                required
              />
            </label>
            <span className="hint">entre 0.01 e 1.0 m</span>
          </div>

          <div className="form-group">
            <label>
              altura (m):
              <input
                type="number"
                name="height"
                value={parameters.height}
                onChange={handleChange}
                step="0.001"
                min="0.01"
                max="2.0"
                required
              />
            </label>
            <span className="hint">entre 0.01 e 2.0 m</span>
          </div>

          <div className="form-group">
            <label>
              espessura parede (m):
              <input
                type="number"
                name="wall_thickness"
                value={parameters.wall_thickness}
                onChange={handleChange}
                step="0.0001"
                min="0.001"
                max="0.01"
              />
            </label>
          </div>
        </fieldset>

        {/* partículas */}
        <fieldset>
          <legend>
            <ThemeIcon light="particles_grid_white.png" dark="particles_grid_black.png" alt="partículas" className="legend-icon" />
            partículas
          </legend>
          
          <div className="form-group">
            <label>
              quantidade:
              <input
                type="number"
                name="particle_count"
                value={parameters.particle_count}
                onChange={handleChange}
                min="10"
                max="10000"
                required
              />
            </label>
            <span className="hint">entre 10 e 10000</span>
          </div>

          <div className="form-group">
            <label>
              tipo:
              <select
                name="particle_type"
                value={parameters.particle_type}
                onChange={handleChange}
              >
                <option value="sphere">esfera</option>
                <option value="cube">cubo</option>
              </select>
            </label>
          </div>

          <div className="form-group">
            <label>
              diâmetro (m):
              <input
                type="number"
                name="particle_diameter"
                value={parameters.particle_diameter}
                onChange={handleChange}
                step="0.0001"
                min="0.001"
                max="0.1"
                required
              />
            </label>
            <span className="hint">entre 0.001 e 0.1 m</span>
          </div>
        </fieldset>

        {/* física */}
        <fieldset>
          <legend>
            <ThemeIcon light="packingLight.png" dark="packingDark.png" alt="empacotamento" className="legend-icon" />
            empacotamento
          </legend>
          
          <div className="form-group">
            <label>
              método:
              <select
                name="packing_method"
                value={parameters.packing_method}
                onChange={handleChange}
              >
                <option value="rigid_body">rigid body</option>
                <option value="random">aleatório</option>
              </select>
            </label>
          </div>

          <div className="form-group">
            <label>
              gravidade (m/s²):
              <input
                type="number"
                name="gravity"
                value={parameters.gravity}
                onChange={handleChange}
                step="0.1"
              />
            </label>
          </div>

          <div className="form-group">
            <label>
              fricção:
              <input
                type="number"
                name="friction"
                value={parameters.friction}
                onChange={handleChange}
                step="0.1"
                min="0"
                max="1"
              />
            </label>
          </div>

          <div className="form-group">
            <label>
              substeps:
              <input
                type="number"
                name="substeps"
                value={parameters.substeps}
                onChange={handleChange}
                min="1"
                max="100"
              />
            </label>
          </div>
        </fieldset>

        {/* botão */}
        <button
          type="submit"
          className="btn-primary"
          disabled={loading}
        >
          {loading ? '⏳ processando...' : '🚀 gerar leito'}
        </button>
      </form>
    </div>
  )
}

export default BedForm

