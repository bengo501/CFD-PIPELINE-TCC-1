# integração three.js no wizard

visualização 3d interativa dos leitos empacotados antes da geração.

## 🎨 funcionalidades implementadas

### preview 3d completo

✅ **geometria do leito**
- cilindro com paredes transparentes
- diâmetro e altura configuráveis
- espessura de parede visual
- material com transparência e metalness

✅ **tampas**
- suporte para tampas planas
- suporte para tampas hemisféricas
- opção "none" (sem tampa)
- material azul translúcido

✅ **partículas**
- 3 tipos: esfera, cubo, cilindro
- distribuição aleatória dentro do cilindro
- rotação aleatória
- instanced mesh para performance (até 200 partículas no preview)

✅ **controles interativos**
- orbit controls (arrastar para rotacionar)
- zoom com scroll do mouse
- damping suave
- limites de distância (min/max)

✅ **iluminação**
- luz ambiente (0.6 intensidade)
- 2 luzes direcionais
- sombras realistas (PCFSoftShadow)
- shadow mapping 2048×2048

✅ **elementos visuais**
- grid helper para referência de escala
- edges geometry para contornos
- background gradiente
- informações abaixo do preview

## 📁 arquivos criados

### componente principal

**`frontend/src/components/BedPreview3D.jsx`** (367 linhas)

```jsx
import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const BedPreview3D = ({ params }) => {
  // renderiza cena 3d com base nos parâmetros
  // ...
};
```

**recursos:**
- useEffect para criar/limpar cena
- refs para scene, renderer, controls
- função createBedGeometry() para construir geometria
- animation loop para renderização contínua
- handle resize para responsividade

### estilos

**`frontend/src/styles/BedPreview3D.css`** (182 linhas)

**features:**
- container responsivo
- canvas 400px altura (300px mobile)
- header com informações de controle
- info cards abaixo do preview
- suporte a modo escuro
- animações de loading

## 🎯 como funciona

### fluxo de renderização

1. **componente monta**
   - cria scene, camera, renderer
   - adiciona OrbitControls
   - configura luzes e sombras
   - adiciona grid helper

2. **cria geometria**
   - lê parâmetros do wizard (params prop)
   - converte strings para números
   - cria cilindro externo com transparência
   - adiciona tampas se configuradas
   - distribui partículas aleatoriamente
   - usa instanced mesh para performance

3. **animation loop**
   - atualiza controls
   - renderiza cena
   - roda em requestAnimationFrame

4. **cleanup**
   - remove event listeners
   - dispose de renderer e controls
   - remove DOM elements

### geometrias criadas

#### cilindro (parede do leito)

```js
const cylinderGeometry = new THREE.CylinderGeometry(
  outerRadius,      // raio topo
  outerRadius,      // raio base
  bedHeight,        // altura
  32,               // segments
  1,                // height segments
  true              // open ended (sem tampas)
);
```

**material:**
- cor verde (#4CAF50)
- transparência 30%
- metalness 0.3, roughness 0.7
- double side

#### partículas

**esfera:**
```js
new THREE.SphereGeometry(radius, 16, 16);
```

**cubo:**
```js
new THREE.BoxGeometry(diameter, diameter, diameter);
```

**cilindro:**
```js
new THREE.CylinderGeometry(radius, radius, diameter, 16);
```

**distribuição:**
```js
// posição aleatória dentro do cilindro
const angle = Math.random() * Math.PI * 2;
const radius = Math.random() * (innerRadius - particleRadius);
const x = Math.cos(angle) * radius;
const z = Math.sin(angle) * radius;
const y = (Math.random() - 0.5) * (bedHeight - particleDiameter * 2);
```

### otimizações de performance

#### instanced mesh

em vez de criar 1000+ objetos individuais:

```js
// ❌ lento - múltiplos meshes
for (let i = 0; i < 1000; i++) {
  const particle = new THREE.Mesh(geometry, material);
  scene.add(particle);
}

// ✅ rápido - instanced mesh
const instancedMesh = new THREE.InstancedMesh(
  geometry,
  material,
  maxParticlesToShow
);
// define matrices uma vez
instancedMesh.setMatrixAt(i, matrix);
instancedMesh.instanceMatrix.needsUpdate = true;
scene.add(instancedMesh);
```

**benefícios:**
- 1 draw call para todas as partículas
- menos overhead de objetos
- ~10x mais rápido

#### limitação de partículas

```js
const maxParticlesToShow = Math.min(particleCount, 200);
```

preview mostra até 200 partículas, mesmo que usuário configure 5000.

**por quê:**
- preview visual, não precisa ser exato
- mantém 60 fps
- reduz consumo de memória

#### shadow map resolution

```js
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
```

qualidade de sombra equilibrada (não 4096 ou 8192).

## 🎨 integração com wizard

### no BedWizard.jsx

```jsx
import BedPreview3D from './BedPreview3D';

// na função renderConfirmation()
<BedPreview3D params={params} />
```

**quando aparece:**
- etapa final (confirmação)
- após usuário preencher todos os parâmetros
- antes de clicar "gerar arquivo .bed"

**params passados:**
```js
{
  bed: { diameter, height, wall_thickness, material, ... },
  lids: { top_type, bottom_type, ... },
  particles: { kind, diameter, count, density, ... },
  packing: { ... },
  export: { ... }
}
```

## 🎮 controles do usuário

### interações disponíveis

| ação | resultado |
|------|-----------|
| **arrastar** | rotaciona câmera ao redor do leito |
| **scroll up** | zoom in (aproximar) |
| **scroll down** | zoom out (afastar) |
| **botão meio** | pan (mover lateralmente) |

### limites configurados

```js
controls.minDistance = 0.05;  // não passar por dentro
controls.maxDistance = 1;     // não afastar demais
```

### damping (suavização)

```js
controls.enableDamping = true;
controls.dampingFactor = 0.05;  // movimento suave
```

## 📊 informações exibidas

abaixo do canvas 3d:

```
┌─────────────────────────────────────────────┐
│ geometria: ø 0.05m × 0.1m                   │
├─────────────────────────────────────────────┤
│ partículas: 100 sphere (ø 0.005m)           │
├─────────────────────────────────────────────┤
│ material: steel (2500 kg/m³)                │
└─────────────────────────────────────────────┘
```

## 🎨 cores e materiais

### esquema de cores

- **cilindro (parede):** #4CAF50 (verde)
- **tampas:** #2196F3 (azul)
- **partículas:** #FF9800 (laranja)
- **grid:** #888888 (cinza)
- **background:** gradiente #f5f7fa → #c3cfe2

### propriedades de materiais

**cilindro:**
```js
{
  color: 0x4CAF50,
  transparent: true,
  opacity: 0.3,
  metalness: 0.3,
  roughness: 0.7,
  side: THREE.DoubleSide
}
```

**partículas:**
```js
{
  color: 0xFF9800,
  metalness: 0.2,
  roughness: 0.8
}
```

## 🌐 responsividade

### desktop (> 768px)

- canvas: 400px altura
- info cards: 3 colunas
- controles inline

### mobile (≤ 768px)

- canvas: 300px altura
- info cards: 1 coluna (stack)
- controles stacked
- touch gestures funcionam

### handle resize

```js
window.addEventListener('resize', handleResize);

const handleResize = () => {
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
};
```

## 🌙 modo escuro

detecção automática:

```css
@media (prefers-color-scheme: dark) {
  .bed-preview-3d {
    background: #2d2d2d;
  }
  /* ... */
}
```

scene background também muda:

```js
scene.background = new THREE.Color(0xf0f0f0); // claro
// ou
scene.background = new THREE.Color(0x2d2d2d); // escuro
```

## 🐛 debugging

### console logs

```js
console.log(`preview: mostrando ${maxParticlesToShow} de ${particleCount} partículas`);
```

### stats (opcional)

adicionar stats.js para fps monitoring:

```bash
npm install stats.js
```

```js
import Stats from 'stats.js';
const stats = new Stats();
document.body.appendChild(stats.dom);

// no animation loop
stats.begin();
renderer.render(scene, camera);
stats.end();
```

## 🚀 melhorias futuras

### curto prazo

- [ ] adicionar axes helper (eixos xyz)
- [ ] botão "reset camera"
- [ ] toggle wireframe
- [ ] export screenshot

### médio prazo

- [ ] animação de empacotamento (física)
- [ ] cores customizáveis
- [ ] diferentes ângulos preset (top, side, front)
- [ ] medidas/dimensões na cena

### longo prazo

- [ ] vr/ar support
- [ ] preview de resultados cfd
- [ ] comparação lado a lado
- [ ] edição 3d direta

## 📚 dependências

### three.js

```json
{
  "three": "^0.158.0"
}
```

**instalado via:**
```bash
npm install three
```

### imports utilizados

```js
import * THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
```

## 🔗 recursos externos

- **three.js docs:** https://threejs.org/docs/
- **examples:** https://threejs.org/examples/
- **orbit controls:** https://threejs.org/docs/#examples/en/controls/OrbitControls
- **instanced mesh:** https://threejs.org/docs/#api/en/objects/InstancedMesh

## 🎓 conceitos three.js utilizados

### core

- Scene
- PerspectiveCamera
- WebGLRenderer
- Mesh, Geometry, Material

### geometries

- CylinderGeometry
- SphereGeometry
- BoxGeometry

### materials

- MeshStandardMaterial (PBR)

### lights

- AmbientLight
- DirectionalLight
- Shadows (PCFSoftShadow)

### helpers

- GridHelper
- EdgesGeometry

### avançado

- InstancedMesh
- Matrix4
- Quaternion
- OrbitControls

---

**desenvolvido para o tcc: pipeline cfd de leitos empacotados**

versão: 0.1.0
data: outubro 2025

