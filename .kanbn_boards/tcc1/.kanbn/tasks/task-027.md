---
name: integrar three.js para visualização 3d
tags:
  - frontend
  - threejs
  - 3d
created: 2025-10-09
assigned: 
sprint: mes 4 sem 1-2
atividades-tcc: a10
story-points: 8
---

# integrar three.js para visualização 3d

implementar visualizador 3d interativo no frontend usando three.js.

## tarefas

### setup three.js
- [ ] instalar three.js e react-three-fiber
- [ ] criar componente `ModelViewer3D`
- [ ] configurar canvas e cena
- [ ] iluminação e câmera
- [ ] controles orbitais

### carregamento de modelos
- [ ] loader para arquivos .stl
- [ ] loader para .obj (opcional)
- [ ] parsing de geometria
- [ ] renderização de mesh
- [ ] materiais e texturas

### interatividade
- [ ] zoom com mouse wheel
- [ ] rotação com mouse drag
- [ ] pan com botão direito
- [ ] reset de câmera
- [ ] fullscreen
- [ ] wireframe toggle
- [ ] transparência toggle

### ui controles
- [ ] slider de opacidade
- [ ] seleção de cor
- [ ] toggle partículas
- [ ] toggle cilindro
- [ ] toggle tampas
- [ ] informações do modelo (vértices, faces)

### integração api
- [ ] buscar .stl do backend
- [ ] download via url assinada
- [ ] loading state
- [ ] error handling
- [ ] cache de modelos

### performance
- [ ] geometry simplification (opcional)
- [ ] level of detail (lod)
- [ ] frustum culling
- [ ] otimização de renderização

## estrutura de código

```jsx
// frontend/src/components/ModelViewer3D.jsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls, STLLoader } from '@react-three/drei'

function ModelViewer3D({ stlUrl }) {
  const [geometry, setGeometry] = useState(null)
  
  useEffect(() => {
    const loader = new STLLoader()
    loader.load(stlUrl, (geom) => {
      setGeometry(geom)
    })
  }, [stlUrl])
  
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <spotLight position={[10, 10, 10]} />
      {geometry && (
        <mesh geometry={geometry}>
          <meshStandardMaterial color="#4A90E2" />
        </mesh>
      )}
      <OrbitControls />
    </Canvas>
  )
}
```

## bibliotecas necessárias

```json
{
  "dependencies": {
    "three": "^0.158.0",
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.88.0"
  }
}
```

## prioridade
média - melhora experiência do usuário

## estimativa
2-3 dias (8 story points)

## critérios de aceitação
- [ ] visualiza .stl corretamente
- [ ] controles interativos funcionais
- [ ] zoom, rotação, pan
- [ ] ui com controles visuais
- [ ] performance aceitável (>30fps)
- [ ] integrado com api backend
- [ ] loading e error states
- [ ] responsivo

