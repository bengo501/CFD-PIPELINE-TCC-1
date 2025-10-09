import { Suspense } from 'react'

// componente simplificado de visualização 3d
// em produção, usar @react-three/fiber + @react-three/drei
function ModelViewer({ modelPath }) {
  return (
    <div className="model-viewer">
      <div className="model-placeholder">
        <div className="placeholder-content">
          <div className="placeholder-icon">🎨</div>
          <p>visualização 3d</p>
          <p className="placeholder-info">modelo: {modelPath}</p>
          <p className="placeholder-hint">
            integração com three.js será implementada
          </p>
          <p className="placeholder-note">
            por enquanto, baixe o arquivo .blend e abra no blender
          </p>
        </div>
      </div>
    </div>
  )
}

export default ModelViewer

