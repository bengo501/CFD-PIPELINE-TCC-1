import { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import ThemeIcon from './ThemeIcon';
import '../styles/PipelineCompletoFull.css';

/**
 * pipeline completo end-to-end com execucao cfd
 * 
 * novo fluxo com endpoint /pipeline/full-simulation:
 * 1. enviar parametros → backend cria job
 * 2. monitorar job em tempo real
 * 3. exibir logs e progresso
 * 4. mostrar resultados finais
 * 
 * etapas executadas pelo backend:
 * - compilacao .bed -> .json (0-15%)
 * - modelagem 3d com blender (15-40%)
 * - criacao caso openfoam (40-50%)
 * - execucao simulacao cfd no wsl (50-100%)
 */
const PipelineCompletoFull = () => {
  const { language } = useLanguage();
  const [etapaAtual, setEtapaAtual] = useState('inicio'); // inicio, configuracao, executando, concluido
  const [jobId, setJobId] = useState(null);
  const [jobData, setJobData] = useState(null);
  const [parametros, setParametros] = useState({
    diameter: 0.05,
    height: 0.1,
    wall_thickness: 0.002,
    lid_top: 'flat',
    lid_bottom: 'flat',
    lid_thickness: 0.003,
    particle_count: 100,
    particle_type: 'sphere',
    particle_diameter: 0.005,
    packing_method: 'rigid_body',
    gravity: -9.81,
    friction: 0.5,
    substeps: 10,
    cfd_regime: 'laminar',
    inlet_velocity: 0.1,
    fluid_density: 1000,
    fluid_viscosity: 0.001
  });

  // polling para monitorar job
  useEffect(() => {
    if (!jobId || etapaAtual !== 'executando') return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/pipeline/job/${jobId}`);
        if (response.ok) {
          const data = await response.json();
          setJobData(data);

          // verificar se concluiu ou falhou
          if (data.status === 'completed') {
            setEtapaAtual('concluido');
            clearInterval(interval);
          } else if (data.status === 'failed') {
            setEtapaAtual('erro');
            clearInterval(interval);
          }
        }
      } catch (error) {
        console.error('erro ao monitorar job:', error);
      }
    }, 2000); // atualiza a cada 2 segundos

    return () => clearInterval(interval);
  }, [jobId, etapaAtual]);

  const iniciarPipeline = async () => {
    try {
      setEtapaAtual('executando');
      setJobData(null);

      const response = await fetch('http://localhost:8000/api/pipeline/full-simulation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parametros)
      });

      if (!response.ok) {
        throw new Error('falha ao iniciar pipeline');
      }

      const data = await response.json();
      setJobId(data.job_id);
    } catch (error) {
      console.error('erro ao iniciar pipeline:', error);
      setEtapaAtual('erro');
    }
  };

  const renderInicio = () => (
    <div className="pipeline-inicio">
      <div className="pipeline-header">
        <ThemeIcon 
          light="pipelineLight.png" 
          dark="pipelineLight.png" 
          alt="pipeline" 
          className="pipeline-icon-large" 
        />
        <h2>{language === 'pt' ? 'pipeline completo end-to-end' : 'full end-to-end pipeline'}</h2>
        <p className="pipeline-description">
          {language === 'pt' 
            ? 'executa automaticamente: compilação → modelagem 3d → caso cfd → simulação'
            : 'automatically executes: compilation → 3d modeling → cfd case → simulation'}
        </p>
      </div>

      <div className="pipeline-info">
        <div className="info-card">
          <h3>⚙️ {language === 'pt' ? 'etapas executadas' : 'executed stages'}</h3>
          <ul>
            <li>✓ {language === 'pt' ? 'compilação dsl (.bed → .json)' : 'dsl compilation (.bed → .json)'}</li>
            <li>✓ {language === 'pt' ? 'modelagem 3d com física (blender)' : '3d modeling with physics (blender)'}</li>
            <li>✓ {language === 'pt' ? 'criação de caso cfd (openfoam)' : 'cfd case creation (openfoam)'}</li>
            <li>✓ {language === 'pt' ? 'execução de simulação (wsl)' : 'simulation execution (wsl)'}</li>
          </ul>
        </div>

        <div className="info-card">
          <h3>⏱️ {language === 'pt' ? 'tempo estimado' : 'estimated time'}</h3>
          <p>{language === 'pt' ? '10-45 minutos' : '10-45 minutes'}</p>
          <small>
            {language === 'pt' 
              ? 'depende de: quantidade de partículas, refinamento de malha, convergência'
              : 'depends on: particle count, mesh refinement, convergence'}
          </small>
        </div>

        <div className="info-card">
          <h3>📋 {language === 'pt' ? 'requisitos' : 'requirements'}</h3>
          <ul>
            <li>blender {language === 'pt' ? 'instalado' : 'installed'}</li>
            <li>wsl2 + ubuntu</li>
            <li>openfoam {language === 'pt' ? 'no wsl' : 'on wsl'}</li>
            <li>~2gb {language === 'pt' ? 'espaço livre' : 'free space'}</li>
          </ul>
        </div>
      </div>

      <button 
        className="btn-iniciar-pipeline"
        onClick={() => setEtapaAtual('configuracao')}
      >
        {language === 'pt' ? '🚀 configurar e iniciar pipeline' : '🚀 configure and start pipeline'}
      </button>
    </div>
  );

  const renderConfiguracao = () => (
    <div className="pipeline-configuracao">
      <h2>{language === 'pt' ? 'configuração do leito' : 'bed configuration'}</h2>
      
      <div className="config-section">
        <h3>{language === 'pt' ? 'geometria do leito' : 'bed geometry'}</h3>
        <div className="config-grid">
          <label>
            {language === 'pt' ? 'diâmetro (m)' : 'diameter (m)'}
            <input 
              type="number" 
              value={parametros.diameter} 
              onChange={(e) => setParametros({...parametros, diameter: parseFloat(e.target.value)})}
              step="0.01"
              min="0.01"
              max="1.0"
            />
          </label>
          <label>
            {language === 'pt' ? 'altura (m)' : 'height (m)'}
            <input 
              type="number" 
              value={parametros.height} 
              onChange={(e) => setParametros({...parametros, height: parseFloat(e.target.value)})}
              step="0.01"
              min="0.01"
              max="2.0"
            />
          </label>
          <label>
            {language === 'pt' ? 'espessura parede (m)' : 'wall thickness (m)'}
            <input 
              type="number" 
              value={parametros.wall_thickness} 
              onChange={(e) => setParametros({...parametros, wall_thickness: parseFloat(e.target.value)})}
              step="0.001"
              min="0.001"
              max="0.05"
            />
          </label>
        </div>
      </div>

      <div className="config-section">
        <h3>{language === 'pt' ? 'partículas' : 'particles'}</h3>
        <div className="config-grid">
          <label>
            {language === 'pt' ? 'quantidade' : 'count'}
            <input 
              type="number" 
              value={parametros.particle_count} 
              onChange={(e) => setParametros({...parametros, particle_count: parseInt(e.target.value)})}
              step="10"
              min="10"
              max="1000"
            />
          </label>
          <label>
            {language === 'pt' ? 'diâmetro (m)' : 'diameter (m)'}
            <input 
              type="number" 
              value={parametros.particle_diameter} 
              onChange={(e) => setParametros({...parametros, particle_diameter: parseFloat(e.target.value)})}
              step="0.001"
              min="0.001"
              max="0.01"
            />
          </label>
          <label>
            {language === 'pt' ? 'tipo' : 'type'}
            <select 
              value={parametros.particle_type} 
              onChange={(e) => setParametros({...parametros, particle_type: e.target.value})}
            >
              <option value="sphere">{language === 'pt' ? 'esfera' : 'sphere'}</option>
              <option value="cube">{language === 'pt' ? 'cubo' : 'cube'}</option>
            </select>
          </label>
        </div>
      </div>

      <div className="config-section">
        <h3>{language === 'pt' ? 'simulação cfd' : 'cfd simulation'}</h3>
        <div className="config-grid">
          <label>
            {language === 'pt' ? 'velocidade entrada (m/s)' : 'inlet velocity (m/s)'}
            <input 
              type="number" 
              value={parametros.inlet_velocity} 
              onChange={(e) => setParametros({...parametros, inlet_velocity: parseFloat(e.target.value)})}
              step="0.01"
              min="0.01"
              max="10.0"
            />
          </label>
          <label>
            {language === 'pt' ? 'densidade fluido (kg/m³)' : 'fluid density (kg/m³)'}
            <input 
              type="number" 
              value={parametros.fluid_density} 
              onChange={(e) => setParametros({...parametros, fluid_density: parseFloat(e.target.value)})}
              step="10"
              min="1"
              max="2000"
            />
          </label>
          <label>
            {language === 'pt' ? 'viscosidade (Pa.s)' : 'viscosity (Pa.s)'}
            <input 
              type="number" 
              value={parametros.fluid_viscosity} 
              onChange={(e) => setParametros({...parametros, fluid_viscosity: parseFloat(e.target.value)})}
              step="0.0001"
              min="0.00001"
              max="0.1"
            />
          </label>
        </div>
      </div>

      <div className="config-actions">
        <button 
          className="btn-voltar"
          onClick={() => setEtapaAtual('inicio')}
        >
          {language === 'pt' ? '← voltar' : '← back'}
        </button>
        <button 
          className="btn-executar"
          onClick={iniciarPipeline}
        >
          {language === 'pt' ? '🚀 executar pipeline completo' : '🚀 execute full pipeline'}
        </button>
      </div>
    </div>
  );

  const renderExecutando = () => {
    if (!jobData) {
      return (
        <div className="pipeline-loading">
          <div className="spinner"></div>
          <p>{language === 'pt' ? 'iniciando pipeline...' : 'starting pipeline...'}</p>
        </div>
      );
    }

    const progress = jobData.progress || 0;
    const status = jobData.status || 'queued';
    const logs = jobData.logs || [];

    return (
      <div className="pipeline-executando">
        <h2>{language === 'pt' ? 'pipeline em execução' : 'pipeline running'}</h2>
        
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{width: `${progress}%`}}
            ></div>
          </div>
          <span className="progress-text">{progress}%</span>
        </div>

        <div className="status-indicator">
          <span className={`status-badge ${status}`}>{status}</span>
        </div>

        <div className="etapas-pipeline">
          <div className={`etapa ${progress >= 0 ? 'ativa' : ''} ${progress > 15 ? 'concluida' : ''}`}>
            <div className="etapa-icone">1</div>
            <span className="etapa-nome">{language === 'pt' ? 'compilação .bed' : 'compile .bed'}</span>
          </div>
          <div className={`etapa ${progress >= 15 ? 'ativa' : ''} ${progress > 40 ? 'concluida' : ''}`}>
            <div className="etapa-icone">2</div>
            <span className="etapa-nome">{language === 'pt' ? 'modelagem 3d' : '3d modeling'}</span>
          </div>
          <div className={`etapa ${progress >= 40 ? 'ativa' : ''} ${progress > 50 ? 'concluida' : ''}`}>
            <div className="etapa-icone">3</div>
            <span className="etapa-nome">{language === 'pt' ? 'caso openfoam' : 'openfoam case'}</span>
          </div>
          <div className={`etapa ${progress >= 50 ? 'ativa' : ''} ${progress >= 100 ? 'concluida' : ''}`}>
            <div className="etapa-icone">4</div>
            <span className="etapa-nome">{language === 'pt' ? 'simulação cfd' : 'cfd simulation'}</span>
          </div>
        </div>

        <div className="logs-container">
          <h3>{language === 'pt' ? 'logs de execução' : 'execution logs'}</h3>
          <div className="logs-content">
            {logs.map((log, index) => (
              <div key={index} className="log-line">
                {log}
              </div>
            ))}
            {logs.length === 0 && (
              <div className="log-line">{language === 'pt' ? 'aguardando logs...' : 'waiting for logs...'}</div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderConcluido = () => {
    if (!jobData) return null;

    const outputFiles = jobData.output_files || [];
    const metadata = jobData.metadata || {};

    return (
      <div className="pipeline-concluido">
        <div className="sucesso-header">
          <div className="sucesso-icone">✓</div>
          <h2>{language === 'pt' ? 'pipeline concluído com sucesso!' : 'pipeline completed successfully!'}</h2>
        </div>

        <div className="resultados-grid">
          <div className="resultado-card">
            <h3>📄 {language === 'pt' ? 'arquivos gerados' : 'generated files'}</h3>
            <ul>
              {outputFiles.map((file, index) => (
                <li key={index}>
                  <code>{file}</code>
                </li>
              ))}
            </ul>
          </div>

          <div className="resultado-card">
            <h3>📊 {language === 'pt' ? 'resultados cfd' : 'cfd results'}</h3>
            {metadata.case_dir && (
              <div>
                <p><strong>{language === 'pt' ? 'caso:' : 'case:'}</strong> <code>{metadata.case_dir}</code></p>
                <p><strong>{language === 'pt' ? 'paraview:' : 'paraview:'}</strong> <code>{metadata.case_dir}/caso.foam</code></p>
              </div>
            )}
          </div>

          <div className="resultado-card">
            <h3>🔍 {language === 'pt' ? 'próximos passos' : 'next steps'}</h3>
            <ul>
              <li>{language === 'pt' ? 'visualizar resultados no paraview' : 'visualize results in paraview'}</li>
              <li>{language === 'pt' ? 'analisar campos de velocidade e pressão' : 'analyze velocity and pressure fields'}</li>
              <li>{language === 'pt' ? 'comparar com equação de ergun' : 'compare with ergun equation'}</li>
            </ul>
          </div>
        </div>

        <div className="logs-finais">
          <h3>{language === 'pt' ? 'logs completos' : 'complete logs'}</h3>
          <div className="logs-content">
            {jobData.logs?.map((log, index) => (
              <div key={index} className="log-line">{log}</div>
            ))}
          </div>
        </div>

        <button 
          className="btn-novo-pipeline"
          onClick={() => {
            setEtapaAtual('inicio');
            setJobId(null);
            setJobData(null);
          }}
        >
          {language === 'pt' ? '🔄 executar novo pipeline' : '🔄 run new pipeline'}
        </button>
      </div>
    );
  };

  const renderErro = () => {
    if (!jobData) return null;

    return (
      <div className="pipeline-erro">
        <div className="erro-header">
          <div className="erro-icone">✗</div>
          <h2>{language === 'pt' ? 'erro na execução do pipeline' : 'pipeline execution error'}</h2>
        </div>

        <div className="erro-detalhes">
          <p><strong>{language === 'pt' ? 'mensagem:' : 'message:'}</strong> {jobData.error_message}</p>
        </div>

        <div className="logs-erro">
          <h3>{language === 'pt' ? 'logs de erro' : 'error logs'}</h3>
          <div className="logs-content">
            {jobData.logs?.map((log, index) => (
              <div key={index} className="log-line log-erro">{log}</div>
            ))}
          </div>
        </div>

        <button 
          className="btn-tentar-novamente"
          onClick={() => {
            setEtapaAtual('configuracao');
            setJobId(null);
            setJobData(null);
          }}
        >
          {language === 'pt' ? '🔄 tentar novamente' : '🔄 try again'}
        </button>
      </div>
    );
  };

  return (
    <div className="pipeline-completo-container">
      {etapaAtual === 'inicio' && renderInicio()}
      {etapaAtual === 'configuracao' && renderConfiguracao()}
      {etapaAtual === 'executando' && renderExecutando()}
      {etapaAtual === 'concluido' && renderConcluido()}
      {etapaAtual === 'erro' && renderErro()}
    </div>
  );
};

export default PipelineCompletoFull;

