import { useState } from 'react';
import BedPreview3D from './BedPreview3D';
import { HelpModal, DocsModal } from './WizardHelpers';
import ThemeIcon from './ThemeIcon';
import '../styles/BedWizard.css';

const BedWizard = () => {
  const [step, setStep] = useState(0);
  const [mode, setMode] = useState(null);
  const [params, setParams] = useState({
    bed: {
      diameter: '0.05',
      height: '0.1',
      wall_thickness: '0.002',
      clearance: '0.01',
      material: 'steel',
      roughness: '0.0'
    },
    lids: {
      top_type: 'flat',
      bottom_type: 'flat',
      top_thickness: '0.003',
      bottom_thickness: '0.003',
      seal_clearance: '0.001'
    },
    particles: {
      kind: 'sphere',
      diameter: '0.005',
      count: '100',
      target_porosity: '0.4',
      density: '2500.0',
      mass: '0.0',
      restitution: '0.3',
      friction: '0.5',
      rolling_friction: '0.1',
      linear_damping: '0.1',
      angular_damping: '0.1',
      seed: '42'
    },
    packing: {
      method: 'rigid_body',
      gravity: '-9.81',
      substeps: '10',
      iterations: '10',
      damping: '0.1',
      rest_velocity: '0.01',
      max_time: '5.0',
      collision_margin: '0.001'
    },
    export: {
      formats: ['stl_binary', 'blend'],
      units: 'm',
      scale: '1.0',
      wall_mode: 'surface',
      fluid_mode: 'none',
      manifold_check: true,
      merge_distance: '0.001'
    },
    cfd: null
  });
  const [includeCFD, setIncludeCFD] = useState(false);
  const [fileName, setFileName] = useState('meu_leito.bed');

  // informações de ajuda para cada parâmetro
  const paramHelp = {
    'bed.diameter': {
      desc: 'diâmetro interno do leito cilíndrico',
      min: 0.01, max: 2.0, unit: 'm',
      exemplo: 'leito de 5cm = 0.05m'
    },
    'bed.height': {
      desc: 'altura total do leito cilíndrico',
      min: 0.01, max: 5.0, unit: 'm',
      exemplo: 'leito de 10cm = 0.1m'
    },
    'bed.wall_thickness': {
      desc: 'espessura da parede do cilindro',
      min: 0.0001, max: 0.1, unit: 'm',
      exemplo: 'parede de 2mm = 0.002m'
    },
    'particles.count': {
      desc: 'quantidade total de partículas',
      min: 1, max: 10000, unit: '',
      exemplo: '100 partículas = empacotamento rápido'
    },
    'particles.diameter': {
      desc: 'diâmetro das partículas esféricas',
      min: 0.0001, max: 0.5, unit: 'm',
      exemplo: 'partícula de 5mm = 0.005m'
    }
  };

  const [showHelp, setShowHelp] = useState(false);
  const [helpSection, setHelpSection] = useState(null);
  const [showDocs, setShowDocs] = useState(false);
  const [showBedFileOptions, setShowBedFileOptions] = useState(false);
  const [bedFileContent, setBedFileContent] = useState('');
  const [bedFileName, setBedFileName] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);

  const steps = [
    { title: 'escolha o modo', section: 'mode' },
    { title: 'geometria do leito', section: 'bed' },
    { title: 'tampas', section: 'lids' },
    { title: 'partículas', section: 'particles' },
    { title: 'empacotamento', section: 'packing' },
    { title: 'exportação', section: 'export' },
    { title: 'cfd (opcional)', section: 'cfd' },
    { title: 'confirmação', section: 'confirm' }
  ];

  const handleModeSelect = (selectedMode) => {
    setMode(selectedMode);
    setStep(1);
  };

  const handleInputChange = (section, field, value) => {
    setParams(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleNext = () => {
    if (step < steps.length - 1) {
      // sempre ir para próximo passo sequencialmente
      // não pular mais automaticamente
      setStep(step + 1);
    }
  };

  const handlePrev = () => {
    if (step > 0) {
      // sempre voltar sequencialmente
      setStep(step - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      // preparar dados para envio
      const bedData = {
        mode: mode,
        fileName: fileName,
        params: params
      };

      // enviar para API backend
      const response = await fetch('http://localhost:3000/api/bed/wizard', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bedData)
      });

      if (response.ok) {
        const result = await response.json();
        alert(`sucesso! arquivo ${fileName} criado\nJSON gerado: ${result.json_file}`);
        
        // se modo blender, perguntar se quer gerar modelo
        if (mode === 'blender' || mode === 'blender_interactive') {
          if (confirm('deseja gerar o modelo 3D agora?')) {
            // chamar endpoint de geração
            const genResponse = await fetch('http://localhost:3000/api/model/generate', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 
                json_file: result.json_file,
                open_blender: mode === 'blender_interactive'
              })
            });
            
            if (genResponse.ok) {
              alert('modelo 3D gerado com sucesso!');
            }
          }
        }
        
        // se modo pipeline completo, executar pipeline end-to-end
        if (mode === 'pipeline_completo') {
          if (confirm('deseja executar o pipeline completo agora? (modelo 3d + simulação cfd)')) {
            // chamar endpoint do pipeline completo
            const pipelineResponse = await fetch('http://localhost:3000/api/pipeline/full-simulation', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                bed: params.bed,
                lids: params.lids,
                particles: params.particles,
                packing: params.packing,
                export: params.export,
                cfd: includeCFD ? {
                  solver: 'simpleFoam',
                  turbulence: 'kEpsilon',
                  convergence: 1e-6,
                  max_iterations: 1000
                } : null
              })
            });
            
            if (pipelineResponse.ok) {
              const pipelineResult = await pipelineResponse.json();
              alert(`pipeline completo iniciado!\njob_id: ${pipelineResult.job_id}\nmonitore o progresso na seção 'jobs'`);
            } else {
              alert('erro ao iniciar pipeline completo');
            }
          }
        }
        
        // resetar wizard
        setStep(0);
        setMode(null);
      } else {
        alert('erro ao criar arquivo .bed');
      }
    } catch (error) {
      console.error('erro:', error);
      alert('erro de conexão com o backend');
    }
  };

  // renderizar modo de seleção
  const renderModeSelection = () => (
    <div className="mode-selection">
      <div className="mode-header">
        <h2>escolha o modo de criação</h2>
        <div className="mode-actions">
          <button className="btn-help" onClick={() => setShowHelp(true)}>
            ajuda
          </button>
          <button className="btn-docs" onClick={() => setShowDocs(true)}>
            documentação
          </button>
        </div>
      </div>
      
      <div className="mode-cards">
        <div className="mode-card" onClick={() => handleModeSelectWithTemplate('blender')}>
          <div className="mode-icon">🎨</div>
          <h3>modo blender</h3>
          <p>geração de modelo 3D (sem parâmetros CFD)</p>
        </div>
        
        <div className="mode-card" onClick={() => handleModeSelectWithTemplate('pipeline_blender_cfd')}>
          <ThemeIcon light="pipelineLight.png" dark="pipelineLight.png" alt="pipeline" className="mode-icon" />
          <h3>pipeline blender + cfd</h3>
          <p>gera modelo 3D + cria caso CFD (sem executar simulação)</p>
          <div className="mode-options">
            <button 
              className="btn-mode-option" 
              onClick={(e) => {
                e.stopPropagation();
                setShowBedFileOptions(true);
              }}
            >
              📁 carregar .bed
            </button>
            <button 
              className="btn-mode-option" 
              onClick={(e) => {
                e.stopPropagation();
                loadDefaultBedTemplate();
                setShowBedFileOptions(true);
              }}
            >
              ✏️ editar padrão
            </button>
          </div>
        </div>
        
        <div className="mode-card" onClick={() => handleModeSelectWithTemplate('cfd_only')}>
          <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="cfd" className="mode-icon" />
          <h3>apenas caso CFD</h3>
          <p>cria caso CFD sem gerar novo leito</p>
          <div className="mode-options">
            <button 
              className="btn-mode-option" 
              onClick={(e) => {
                e.stopPropagation();
                setShowBedFileOptions(true);
              }}
            >
              📁 carregar .bed
            </button>
            <button 
              className="btn-mode-option" 
              onClick={(e) => {
                e.stopPropagation();
                loadDefaultBedTemplate();
                setShowBedFileOptions(true);
              }}
            >
              ✏️ editar padrão
            </button>
          </div>
        </div>
        
        <div className="mode-card" onClick={() => handleModeSelectWithTemplate('blender_interactive')}>
          <div className="mode-icon">🚀</div>
          <h3>blender interativo</h3>
          <p>gera modelo e abre automaticamente no blender</p>
          <div className="mode-options">
            <button 
              className="btn-mode-option" 
              onClick={(e) => {
                e.stopPropagation();
                setShowBedFileOptions(true);
              }}
            >
              📁 carregar .bed
            </button>
            <button 
              className="btn-mode-option" 
              onClick={(e) => {
                e.stopPropagation();
                loadDefaultBedTemplate();
                setShowBedFileOptions(true);
              }}
            >
              ✏️ editar padrão
            </button>
          </div>
        </div>
        
        <div className="mode-card" onClick={() => handleModeSelectWithTemplate('pipeline_completo')}>
          <ThemeIcon light="pipelineLight.png" dark="pipelineLight.png" alt="pipeline" className="mode-icon" />
          <h3>pipeline completo</h3>
          <p>execução end-to-end: modelo 3d + simulação cfd automática</p>
          <div className="mode-options">
            <button 
              className="btn-mode-option" 
              onClick={(e) => {
                e.stopPropagation();
                setShowBedFileOptions(true);
              }}
            >
              📁 carregar .bed
            </button>
            <button 
              className="btn-mode-option" 
              onClick={(e) => {
                e.stopPropagation();
                loadDefaultBedTemplate();
                setShowBedFileOptions(true);
              }}
            >
              ✏️ editar padrão
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // renderizar seção bed
  const renderBedSection = () => (
    <div className="form-section">
      <h2>geometria do leito</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>diâmetro (m)</label>
          <input
            type="number"
            step="0.001"
            value={params.bed.diameter}
            onChange={(e) => handleInputChange('bed', 'diameter', e.target.value)}
          />
          <small>ex: 0.05m = 5cm</small>
        </div>
        
        <div className="form-group">
          <label>altura (m)</label>
          <input
            type="number"
            step="0.001"
            value={params.bed.height}
            onChange={(e) => handleInputChange('bed', 'height', e.target.value)}
          />
          <small>ex: 0.1m = 10cm</small>
        </div>
        
        <div className="form-group">
          <label>espessura da parede (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.bed.wall_thickness}
            onChange={(e) => handleInputChange('bed', 'wall_thickness', e.target.value)}
          />
          <small>ex: 0.002m = 2mm</small>
        </div>
        
        <div className="form-group">
          <label>folga superior (m)</label>
          <input
            type="number"
            step="0.001"
            value={params.bed.clearance}
            onChange={(e) => handleInputChange('bed', 'clearance', e.target.value)}
          />
          <small>espaço livre acima das partículas</small>
        </div>
        
        <div className="form-group">
          <label>material da parede</label>
          <input
            type="text"
            value={params.bed.material}
            onChange={(e) => handleInputChange('bed', 'material', e.target.value)}
          />
          <small>ex: steel, aluminum, glass</small>
        </div>
        
        <div className="form-group">
          <label>rugosidade (m) - opcional</label>
          <input
            type="number"
            step="0.0001"
            value={params.bed.roughness}
            onChange={(e) => handleInputChange('bed', 'roughness', e.target.value)}
          />
          <small>0.0 = superfície lisa</small>
        </div>
      </div>
    </div>
  );

  // renderizar seção lids
  const renderLidsSection = () => (
    <div className="form-section">
      <h2>tampas</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>tipo tampa superior</label>
          <select
            value={params.lids.top_type}
            onChange={(e) => handleInputChange('lids', 'top_type', e.target.value)}
          >
            <option value="flat">plana</option>
            <option value="hemispherical">hemisférica</option>
            <option value="none">sem tampa</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>tipo tampa inferior</label>
          <select
            value={params.lids.bottom_type}
            onChange={(e) => handleInputChange('lids', 'bottom_type', e.target.value)}
          >
            <option value="flat">plana</option>
            <option value="hemispherical">hemisférica</option>
            <option value="none">sem tampa</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>espessura tampa superior (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.lids.top_thickness}
            onChange={(e) => handleInputChange('lids', 'top_thickness', e.target.value)}
          />
          <small>ex: 0.003m = 3mm</small>
        </div>
        
        <div className="form-group">
          <label>espessura tampa inferior (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.lids.bottom_thickness}
            onChange={(e) => handleInputChange('lids', 'bottom_thickness', e.target.value)}
          />
          <small>ex: 0.003m = 3mm</small>
        </div>
      </div>
    </div>
  );

  // renderizar seção particles
  const renderParticlesSection = () => (
    <div className="form-section">
      <h2>partículas</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>tipo de partícula</label>
          <select
            value={params.particles.kind}
            onChange={(e) => handleInputChange('particles', 'kind', e.target.value)}
          >
            <option value="sphere">esfera</option>
            <option value="cube">cubo</option>
            <option value="cylinder">cilindro</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>diâmetro (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.particles.diameter}
            onChange={(e) => handleInputChange('particles', 'diameter', e.target.value)}
          />
          <small>ex: 0.005m = 5mm</small>
        </div>
        
        <div className="form-group">
          <label>quantidade</label>
          <input
            type="number"
            value={params.particles.count}
            onChange={(e) => handleInputChange('particles', 'count', e.target.value)}
          />
          <small>100 = rápido, 1000 = detalhado</small>
        </div>
        
        <div className="form-group">
          <label>densidade (kg/m³)</label>
          <input
            type="number"
            step="10"
            value={params.particles.density}
            onChange={(e) => handleInputChange('particles', 'density', e.target.value)}
          />
          <small>vidro = 2500, aço = 7850</small>
        </div>
        
        <div className="form-group">
          <label>seed para reproducibilidade</label>
          <input
            type="number"
            value={params.particles.seed}
            onChange={(e) => handleInputChange('particles', 'seed', e.target.value)}
          />
          <small>42 = resultado reproduzível</small>
        </div>
      </div>
      
      <details className="advanced-params">
        <summary>parâmetros avançados de física</summary>
        <div className="form-grid">
          <div className="form-group">
            <label>restituição (quique)</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={params.particles.restitution}
              onChange={(e) => handleInputChange('particles', 'restitution', e.target.value)}
            />
            <small>0.0 = sem quique, 1.0 = quique total</small>
          </div>
          
          <div className="form-group">
            <label>atrito</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={params.particles.friction}
              onChange={(e) => handleInputChange('particles', 'friction', e.target.value)}
            />
            <small>0.5 = atrito moderado</small>
          </div>
        </div>
      </details>
    </div>
  );

  // renderizar seção packing
  const renderPackingSection = () => (
    <div className="form-section">
      <h2>empacotamento</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>método</label>
          <select
            value={params.packing.method}
            onChange={(e) => handleInputChange('packing', 'method', e.target.value)}
          >
            <option value="rigid_body">corpo rígido (física)</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>gravidade (m/s²)</label>
          <input
            type="number"
            step="0.1"
            value={params.packing.gravity}
            onChange={(e) => handleInputChange('packing', 'gravity', e.target.value)}
          />
          <small>terra = -9.81, lua = -1.62</small>
        </div>
        
        <div className="form-group">
          <label>sub-passos</label>
          <input
            type="number"
            value={params.packing.substeps}
            onChange={(e) => handleInputChange('packing', 'substeps', e.target.value)}
          />
          <small>10 = boa precisão</small>
        </div>
        
        <div className="form-group">
          <label>tempo máximo (s)</label>
          <input
            type="number"
            step="0.5"
            value={params.packing.max_time}
            onChange={(e) => handleInputChange('packing', 'max_time', e.target.value)}
          />
          <small>5s = suficiente para empacotamento</small>
        </div>
      </div>
    </div>
  );

  // renderizar seção export
  const renderExportSection = () => {
    const formatosDisponiveis = [
      { value: 'blend', label: 'blend (nativo blender)' },
      { value: 'gltf', label: 'gltf (web - multiplos arquivos)' },
      { value: 'glb', label: 'glb (web - arquivo unico)' },
      { value: 'obj', label: 'obj (universal)' },
      { value: 'fbx', label: 'fbx (unity, unreal)' },
      { value: 'stl', label: 'stl (impressao 3d)' }
    ];

    const toggleFormato = (formato) => {
      const formatos = params.export.formats || [];
      const novosFormatos = formatos.includes(formato)
        ? formatos.filter(f => f !== formato)
        : [...formatos, formato];
      
      handleInputChange('export', 'formats', novosFormatos);
    };

    return (
      <div className="form-section">
        <h2>exportação</h2>
        
        <div className="form-group">
          <label>formatos de exportação</label>
          <div className="checkbox-group-formats">
            {formatosDisponiveis.map(({ value, label }) => (
              <label key={value} className="checkbox-format">
                <input
                  type="checkbox"
                  checked={params.export.formats?.includes(value) || false}
                  onChange={() => toggleFormato(value)}
                />
                {label}
              </label>
            ))}
          </div>
          <small>
            selecionados: {params.export.formats?.length || 0} formato(s) - 
            recomendado: blend + glb + obj
          </small>
        </div>
        
        <div className="form-grid">
          <div className="form-group">
            <label>modo da parede</label>
            <select
              value={params.export.wall_mode}
              onChange={(e) => handleInputChange('export', 'wall_mode', e.target.value)}
            >
              <option value="surface">superfície (recomendado)</option>
              <option value="solid">sólido</option>
            </select>
            <small>surface = melhor para cfd</small>
          </div>
          
          <div className="form-group">
            <label>modo do fluido</label>
            <select
              value={params.export.fluid_mode}
              onChange={(e) => handleInputChange('export', 'fluid_mode', e.target.value)}
            >
              <option value="none">nenhum (recomendado)</option>
              <option value="cavity">cavidade</option>
            </select>
          </div>
          
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={params.export.manifold_check}
                onChange={(e) => handleInputChange('export', 'manifold_check', e.target.checked)}
              />
              verificar manifold (recomendado)
            </label>
            <small>garante integridade da malha</small>
          </div>
        </div>
      </div>
    );
  };

  // renderizar confirmação
  const renderConfirmation = () => (
    <div className="form-section confirmation">
      <h2>confirmação dos parâmetros</h2>
      
      {/* preview 3D */}
      <BedPreview3D params={params} />
      
      <div className="summary-grid">
        <div className="summary-card">
          <h3>geometria</h3>
          <p>leito: {params.bed.diameter}m × {params.bed.height}m</p>
          <p>parede: {params.bed.material}</p>
        </div>
        
        <div className="summary-card">
          <h3>partículas</h3>
          <p>{params.particles.count} {params.particles.kind}</p>
          <p>diâmetro: {params.particles.diameter}m</p>
          <p>densidade: {params.particles.density} kg/m³</p>
        </div>
        
        <div className="summary-card">
          <h3>empacotamento</h3>
          <p>{params.packing.method}</p>
          <p>gravidade: {params.packing.gravity} m/s²</p>
        </div>
        
        <div className="summary-card">
          <h3>exportação</h3>
          <p>formatos: {params.export.formats.join(', ')}</p>
          <p>modo: {params.export.wall_mode}</p>
        </div>
      </div>
      
      <div className="form-group">
        <label>nome do arquivo</label>
        <input
          type="text"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          placeholder="meu_leito.bed"
        />
      </div>
    </div>
  );



  // carregar arquivo .bed
  const handleBedFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.bed')) {
      setUploadedFile(file);
      setBedFileName(file.name);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setBedFileContent(e.target.result);
      };
      reader.readAsText(file);
    } else {
      alert('por favor, selecione um arquivo .bed válido');
    }
  };

  // carregar template padrão
  const loadDefaultBedTemplate = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/bed/template/default');
      if (response.ok) {
        const data = await response.json();
        setBedFileContent(data.content);
        setBedFileName('template_padrao.bed');
        setUploadedFile(null);
      } else {
        alert('erro ao carregar template padrão');
      }
    } catch (error) {
      console.error('erro:', error);
      alert('erro de conexão com o backend');
    }
  };

  // processar arquivo .bed carregado
  const processBedFile = async () => {
    if (!bedFileContent.trim()) {
      alert('arquivo .bed está vazio');
      return;
    }

    try {
      const response = await fetch('http://localhost:3000/api/bed/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: bedFileContent,
          filename: bedFileName || 'leito_custom.bed'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        
        // se modo blender interativo, gerar modelo
        if (mode === 'blender_interactive') {
          const genResponse = await fetch('http://localhost:3000/api/model/generate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              json_file: result.json_file,
              open_blender: true
            })
          });
          
          if (genResponse.ok) {
            alert('modelo 3D gerado com sucesso!');
          }
        }
        
        // se modo pipeline blender + cfd, gerar modelo e criar caso CFD
        if (mode === 'pipeline_blender_cfd') {
          const genResponse = await fetch('http://localhost:3000/api/model/generate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              json_file: result.json_file,
              open_blender: false
            })
          });
          
          if (genResponse.ok) {
            const genResult = await genResponse.json();
            
            // criar caso CFD
            const cfdResponse = await fetch('http://localhost:3000/api/cfd/create-case', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                blend_file: genResult.blend_file,
                json_file: result.json_file,
                case_name: `leito_${Date.now()}`
              })
            });
            
            if (cfdResponse.ok) {
              const cfdResult = await cfdResponse.json();
              alert(`pipeline blender + CFD concluído!\nmodelo: ${genResult.blend_file}\ncaso CFD: ${cfdResult.case_dir}`);
            } else {
              alert('erro ao criar caso CFD');
            }
          } else {
            alert('erro ao gerar modelo 3D');
          }
        }
        
        // se modo apenas caso CFD, criar caso CFD sem gerar modelo
        if (mode === 'cfd_only') {
          const cfdResponse = await fetch('http://localhost:3000/api/cfd/create-case-only', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              json_file: result.json_file,
              case_name: `leito_${Date.now()}`
            })
          });
          
          if (cfdResponse.ok) {
            const cfdResult = await cfdResponse.json();
            alert(`caso CFD criado com sucesso!\ncaso: ${cfdResult.case_dir}`);
          } else {
            alert('erro ao criar caso CFD');
          }
        }
        
        // se modo pipeline completo, executar pipeline
        if (mode === 'pipeline_completo') {
          const pipelineResponse = await fetch('http://localhost:3000/api/pipeline/full-simulation', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              bed_file: result.bed_file,
              json_file: result.json_file
            })
          });
          
          if (pipelineResponse.ok) {
            const pipelineResult = await pipelineResponse.json();
            alert(`pipeline completo iniciado!\njob_id: ${pipelineResult.job_id}`);
          }
        }
        
        // resetar wizard
        setStep(0);
        setMode(null);
        setShowBedFileOptions(false);
        setBedFileContent('');
        setBedFileName('');
        setUploadedFile(null);
        
      } else {
        alert('erro ao processar arquivo .bed');
      }
    } catch (error) {
      console.error('erro:', error);
      alert('erro de conexão com o backend');
    }
  };

  // handler quando seleciona modo
  const handleModeSelectWithTemplate = (selectedMode) => {
    handleModeSelect(selectedMode);
  };

  return (
    <div className="bed-wizard">
      {/* modais */}
      <HelpModal 
        show={showHelp} 
        onClose={() => setShowHelp(false)} 
        section={helpSection}
        paramHelp={paramHelp}
      />
      
      <DocsModal 
        show={showDocs} 
        onClose={() => setShowDocs(false)} 
      />
      

      {/* modal de opções de arquivo .bed */}
      {showBedFileOptions && (
        <div className="modal-overlay">
          <div className="modal-content bed-file-options">
            <div className="modal-header">
              <h2>opções de arquivo .bed</h2>
              <button 
                className="btn-close" 
                onClick={() => {
                  setShowBedFileOptions(false);
                  setBedFileContent('');
                  setBedFileName('');
                  setUploadedFile(null);
                }}
              >
                ✕
              </button>
            </div>
            
            <div className="bed-file-content">
              <div className="file-upload-section">
                <h3>carregar arquivo .bed</h3>
                <input
                  type="file"
                  accept=".bed"
                  onChange={handleBedFileUpload}
                  className="file-input"
                />
                {uploadedFile && (
                  <p className="file-info">arquivo carregado: {uploadedFile.name}</p>
                )}
              </div>
              
              <div className="file-editor-section">
                <h3>editor de arquivo .bed</h3>
                <div className="editor-controls">
                  <button 
                    className="btn-load-template"
                    onClick={loadDefaultBedTemplate}
                  >
                    📄 carregar template padrão
                  </button>
                </div>
                <textarea
                  value={bedFileContent}
                  onChange={(e) => setBedFileContent(e.target.value)}
                  placeholder="cole aqui o conteúdo do arquivo .bed ou carregue um arquivo..."
                  className="bed-editor"
                  rows={15}
                />
              </div>
              
              <div className="file-actions">
                <button 
                  className="btn-process"
                  onClick={processBedFile}
                  disabled={!bedFileContent.trim()}
                >
                  {mode === 'blender_interactive' ? '🚀 gerar modelo 3d' : 
                   mode === 'pipeline_blender_cfd' ? '🔄 pipeline blender + cfd' :
                   mode === 'cfd_only' ? '⚙️ criar caso cfd' :
                   '🔄 executar pipeline completo'}
                </button>
                <button 
                  className="btn-cancel"
                  onClick={() => {
                    setShowBedFileOptions(false);
                    setBedFileContent('');
                    setBedFileName('');
                    setUploadedFile(null);
                  }}
                >
                  cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    
      {/* header com progresso */}
      {step > 0 && (
        <div className="wizard-header">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(step / (steps.length - 1)) * 100}%` }}
            ></div>
          </div>
          <div className="step-indicator">
            passo {step} de {steps.length - 1}: {steps[step].title}
          </div>
        </div>
      )}

      {/* conteúdo do wizard */}
      <div className="wizard-content">
        {step === 0 && renderModeSelection()}
        {step === 1 && renderBedSection()}
        {step === 2 && renderLidsSection()}
        {step === 3 && renderParticlesSection()}
        {step === 4 && renderPackingSection()}
        {step === 5 && renderExportSection()}
        {step === 6 && (
          <div className="form-section">
            <h2>parâmetros CFD (opcional)</h2>
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={includeCFD}
                  onChange={(e) => setIncludeCFD(e.target.checked)}
                />
                incluir parâmetros de simulação CFD
              </label>
            </div>
            {includeCFD && (
              <p className="info-message">
                parâmetros CFD serão configurados na próxima etapa
              </p>
            )}
          </div>
        )}
        {step === 7 && renderConfirmation()}
      </div>

      {/* botões de navegação */}
      {step > 0 && (
        <div className="wizard-footer">
          <button 
            className="btn btn-secondary" 
            onClick={handlePrev}
            disabled={step === 1}
          >
            ← voltar
          </button>
          
          {step < steps.length - 1 ? (
            <button className="btn btn-primary" onClick={handleNext}>
              próximo →
            </button>
          ) : (
            <button className="btn btn-success" onClick={handleSubmit}>
              gerar arquivo .bed
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default BedWizard;

