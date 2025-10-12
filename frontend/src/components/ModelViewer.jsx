import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import '../styles/ModelViewer.css';

function ModelViewer({ modelPath }) {
  const mountRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // criar cena
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    sceneRef.current = scene;

    // criar camera
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.001,
      1000
    );
    camera.position.set(0.15, 0.15, 0.15);
    camera.lookAt(0, 0, 0);

    // criar renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // adicionar controles
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 0.05;
    controls.maxDistance = 1;
    controlsRef.current = controls;

    // adicionar luzes
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0.2, 0.3, 0.2);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-0.2, -0.1, -0.2);
    scene.add(directionalLight2);

    // adicionar grid
    const gridHelper = new THREE.GridHelper(0.5, 10, 0x888888, 0xcccccc);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    // carregar modelo (por enquanto, mostrar placeholder)
    // arquivos .blend não podem ser carregados diretamente no browser
    // precisaria converter para gltf/glb ou obj
    createPlaceholderGeometry(scene);
    setLoading(false);

    // animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // handle resize
    const handleResize = () => {
      if (!mountRef.current) return;
      const width = mountRef.current.clientWidth;
      const height = mountRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    // cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
      controls.dispose();
    };
  }, [modelPath]);

  const createPlaceholderGeometry = (scene) => {
    // criar geometria representativa do leito
    // cilindro
    const cylinderGeometry = new THREE.CylinderGeometry(0.025, 0.025, 0.1, 32);
    const cylinderMaterial = new THREE.MeshStandardMaterial({
      color: 0x4CAF50,
      transparent: true,
      opacity: 0.3,
      side: THREE.DoubleSide,
      metalness: 0.3,
      roughness: 0.7
    });
    const cylinder = new THREE.Mesh(cylinderGeometry, cylinderMaterial);
    cylinder.castShadow = true;
    cylinder.receiveShadow = true;
    scene.add(cylinder);

    // contorno
    const edgesGeometry = new THREE.EdgesGeometry(cylinderGeometry);
    const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x2E7D32, linewidth: 2 });
    const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
    cylinder.add(edges);

    // algumas partículas
    const particleGeometry = new THREE.SphereGeometry(0.0025, 16, 16);
    const particleMaterial = new THREE.MeshStandardMaterial({
      color: 0xFF9800,
      metalness: 0.2,
      roughness: 0.8
    });

    const instancedMesh = new THREE.InstancedMesh(particleGeometry, particleMaterial, 50);
    instancedMesh.castShadow = true;
    instancedMesh.receiveShadow = true;

    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const quaternion = new THREE.Quaternion();
    const scale = new THREE.Vector3(1, 1, 1);

    for (let i = 0; i < 50; i++) {
      const angle = Math.random() * Math.PI * 2;
      const radius = Math.random() * 0.02;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = (Math.random() - 0.5) * 0.08;

      position.set(x, y, z);
      quaternion.setFromEuler(
        new THREE.Euler(
          Math.random() * Math.PI,
          Math.random() * Math.PI,
          Math.random() * Math.PI
        )
      );

      matrix.compose(position, quaternion, scale);
      instancedMesh.setMatrixAt(i, matrix);
    }

    instancedMesh.instanceMatrix.needsUpdate = true;
    scene.add(instancedMesh);
  };

  return (
    <div className="model-viewer">
      <div className="viewer-header">
        <h4>visualização 3d do modelo</h4>
        <div className="viewer-controls-info">
          <span>🖱️ arraste para rotacionar</span>
          <span>🔍 scroll para zoom</span>
        </div>
      </div>

      {loading && (
        <div className="viewer-loading">
          <div className="loading-spinner"></div>
          <p>carregando modelo 3d...</p>
        </div>
      )}

      {error && (
        <div className="viewer-error">
          <p>erro ao carregar modelo</p>
          <small>{error}</small>
        </div>
      )}

      <div ref={mountRef} className="viewer-canvas" />

      <div className="viewer-info">
        <div className="info-badge">
          <span className="info-label">arquivo:</span>
          <span className="info-value">{modelPath?.split('/').pop() || 'modelo'}</span>
        </div>
        <div className="info-note">
          <span>💡</span>
          <span>
            preview representativo do leito empacotado.
            para visualização completa, baixe o arquivo .blend e abra no blender
          </span>
        </div>
      </div>
    </div>
  );
}

export default ModelViewer;
