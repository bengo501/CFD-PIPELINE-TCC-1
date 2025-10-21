import { useState, useEffect } from 'react'
import { useLanguage } from '../context/LanguageContext'
import { useTheme } from '../context/ThemeContext'
import ThemeIcon from './ThemeIcon'
import '../styles/TemplateEditor.css'

function TemplateEditor() {
  const { language, t } = useLanguage()
  const { theme } = useTheme()
  const [bedContent, setBedContent] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [savedTemplates, setSavedTemplates] = useState([])
  const [showTemplateManager, setShowTemplateManager] = useState(false)

  useEffect(() => {
    loadDefaultTemplate()
    loadSavedTemplates()
  }, [])

  const loadDefaultTemplate = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('http://localhost:3000/api/bed/template/default')
      if (response.ok) {
        const data = await response.json()
        setBedContent(data.content)
      }
    } catch (error) {
      console.error('erro ao carregar template padrão:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadSavedTemplates = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/templates/list')
      if (response.ok) {
        const data = await response.json()
        setSavedTemplates(data.templates || [])
      }
    } catch (error) {
      console.error('erro ao carregar templates salvos:', error)
    }
  }

  const handleGenerateFromForm = async () => {
    try {
      setIsLoading(true)
      // aqui você pode implementar a lógica para gerar baseado nos parâmetros do formulário
      // por enquanto, vamos usar o template padrão
      await loadDefaultTemplate()
    } catch (error) {
      console.error('erro ao gerar template:', error)
    }
  }

  const handleImportFile = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setBedContent(e.target.result)
      }
      reader.readAsText(file)
    }
  }

  const handleCopyContent = () => {
    navigator.clipboard.writeText(bedContent)
    alert('conteúdo copiado para a área de transferência!')
  }

  const handleDownloadFile = () => {
    const blob = new Blob([bedContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'template.bed'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleSaveTemplate = async () => {
    const templateName = prompt('nome do template:')
    if (templateName) {
      try {
        const response = await fetch('http://localhost:3000/api/templates/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: templateName,
            content: bedContent
          })
        })
        if (response.ok) {
          alert('template salvo com sucesso!')
          loadSavedTemplates()
        }
      } catch (error) {
        console.error('erro ao salvar template:', error)
      }
    }
  }

  const handleLoadTemplate = async (templateId) => {
    try {
      const response = await fetch(`http://localhost:3000/api/templates/${templateId}`)
      if (response.ok) {
        const data = await response.json()
        setBedContent(data.content)
        setShowTemplateManager(false)
      }
    } catch (error) {
      console.error('erro ao carregar template:', error)
    }
  }

  const handleDeleteTemplate = async (templateId) => {
    if (confirm('tem certeza que deseja excluir este template?')) {
      try {
        const response = await fetch(`http://localhost:3000/api/templates/${templateId}`, {
          method: 'DELETE'
        })
        if (response.ok) {
          alert('template excluído com sucesso!')
          loadSavedTemplates()
        }
      } catch (error) {
        console.error('erro ao excluir template:', error)
      }
    }
  }

  const handleCreateAndExecute = () => {
    // aqui você pode implementar a lógica para criar e executar o pipeline
    alert('funcionalidade de criar e executar será implementada aqui!')
  }

  return (
    <div className="template-editor-container">
      <div className="template-editor-header">
        <h2>arquivo .bed</h2>
      </div>

      <div className="template-editor-actions">
        <button 
          className="btn-generate" 
          onClick={handleGenerateFromForm}
          disabled={isLoading}
        >
          <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="gerar" className="btn-icon" />
          gerar automaticamente
          <span className="btn-subtitle">baseado nos parâmetros do formulário</span>
        </button>

        <label className="btn-import">
          <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="importar" className="btn-icon" />
          importar arquivo
          <span className="btn-subtitle">carregar arquivo .bed existente</span>
          <input 
            type="file" 
            accept=".bed" 
            onChange={handleImportFile}
            style={{ display: 'none' }}
          />
        </label>
      </div>

      <div className="template-editor-content">
        <div className="content-header">
          <h3>conteúdo do arquivo .bed</h3>
          <div className="content-actions">
            <button className="btn-copy" onClick={handleCopyContent}>
              <ThemeIcon light="copyLight.png" dark="copyDark.png" alt="copiar" className="btn-icon" />
              copiar
            </button>
            <button className="btn-download" onClick={handleDownloadFile}>
              <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="baixar" className="btn-icon" />
              baixar
            </button>
          </div>
        </div>

        <div className="bed-editor">
          <textarea
            value={bedContent}
            onChange={(e) => setBedContent(e.target.value)}
            placeholder="conteúdo do arquivo .bed..."
            className="bed-textarea"
          />
        </div>

        <div className="template-info">
          <p>este arquivo .bed é gerado automaticamente baseado nos parâmetros do formulário. você pode editá-lo manualmente se necessário.</p>
        </div>
      </div>

      <div className="template-editor-footer">
        <button className="btn-cancel">
          cancelar
        </button>
        <button className="btn-execute" onClick={handleCreateAndExecute}>
          <ThemeIcon light="playLight.png" dark="playDark.png" alt="executar" className="btn-icon" />
          criar e executar
        </button>
      </div>

      {/* modal para gerenciar templates */}
      {showTemplateManager && (
        <div className="template-manager-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>gerenciar templates</h3>
              <button 
                className="btn-close" 
                onClick={() => setShowTemplateManager(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              {savedTemplates.length === 0 ? (
                <p className="no-templates">nenhum template salvo</p>
              ) : (
                <div className="template-list">
                  {savedTemplates.map((template) => (
                    <div key={template.id} className="template-item">
                      <div className="template-info">
                        <h4>{template.name}</h4>
                        <p>criado em: {new Date(template.created_at).toLocaleDateString()}</p>
                      </div>
                      <div className="template-actions">
                        <button 
                          className="btn-load" 
                          onClick={() => handleLoadTemplate(template.id)}
                        >
                          carregar
                        </button>
                        <button 
                          className="btn-delete" 
                          onClick={() => handleDeleteTemplate(template.id)}
                        >
                          excluir
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TemplateEditor
