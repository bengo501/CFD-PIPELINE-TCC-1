import { useState } from 'react';
import ThemeIcon from './ThemeIcon';
import '../styles/PipelineCompleto.css';

/**
 * pipeline completo web - replica bed_wizard.py
 *
 * fluxo:
 * 1. criar parametros → .bed
 * 2. compilar dsl → .json
 * 3. gerar modelo 3d → .blend, .glb, etc
 * 4. criar caso cfd → openfoam
 * 5. executar simulacao → resultados
 * 6. visualizar → paraview/web
 */
const PipelineCompleto = () => {
  const [etapaAtual, setEtapaAtual] = useState('inicio'); // inicio, params, compilando, gerando3d, cfd, executando, concluido
  const [dadosPipeline, setDadosPipeline] = useState(null);
  const [log, setLog] = useState([]);
  const [erro, setErro] = useState(null);
  const [progresso, setProgresso] = useState(0);

  const adicionarLog = (mensagem, tipo = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLog(prev => [...prev, { timestamp, mensagem, tipo }]);
  };

  const aguardarJobModelo = (jobId) =>
    new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const res = await fetch(`http://localhost:8000/api/job/${jobId}`);
          if (!res.ok) {
            reject(new Error('job de modelo 3d não encontrado'));
            return;
          }
          const job = await res.json();
          if (job.status === 'completed') {
            resolve(job);
            return;
          }
          if (job.status === 'failed') {
            reject(new Error(job.error_message || 'falha na geração do modelo 3d'));
            return;
          }
          adicionarLog(`  job modelo: ${job.status} (${job.progress ?? 0}%)`, 'info');
          setTimeout(poll, 2000);
        } catch (e) {
          reject(e);
        }
      };
      poll();
    });

  // etapa 1: criar arquivo .bed
  const iniciarPipeline = async (parametros) => {
    setErro(null);
    setLog([]);
    setProgresso(0);

    try {
      // 1. compilar dsl
      setEtapaAtual('compilando');
      setProgresso(10);
      adicionarLog('compilando arquivo .bed com antlr...', 'info');

      const respostaCompilacao = await fetch('http://localhost:8000/api/bed/wizard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parametros)
      });

      if (!respostaCompilacao.ok) {
        throw new Error('erro na compilação do arquivo .bed');
      }

      const dadosCompilacao = await respostaCompilacao.json();
      adicionarLog(`arquivo .bed compilado: ${dadosCompilacao.bed_file}`, 'success');
      adicionarLog(`arquivo .json gerado: ${dadosCompilacao.json_file}`, 'success');
      setProgresso(25);

      // 2. gerar modelo 3d
      setEtapaAtual('gerando3d');
      adicionarLog('gerando modelo 3d no blender (com física)...', 'info');
      adicionarLog('executando animação de queda das partículas (20s)...', 'info');

      const respostaBlender = await fetch('http://localhost:8000/api/model/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          json_file: dadosCompilacao.json_file,
          open_blender: false
        })
      });

      if (!respostaBlender.ok) {
        throw new Error('erro na geração do modelo 3d');
      }

      const jobInicio = await respostaBlender.json();
      const jobId = jobInicio.job_id;
      if (!jobId) {
        throw new Error('api não devolveu job_id para o modelo 3d');
      }
      adicionarLog(`modelo 3d em fila (job: ${jobId})`, 'info');
      const jobFinal = await aguardarJobModelo(jobId);
      const caminhoModelo =
        jobFinal.metadata?.blend_file ||
        jobFinal.metadata?.geometry_file ||
        (jobFinal.output_files && jobFinal.output_files[0]) ||
        '(ver output_files no job)';
      adicionarLog('animação de física e exportação concluídas no backend', 'success');
      adicionarLog(`modelo 3d: ${caminhoModelo}`, 'success');
      setProgresso(50);

      // 3. criar caso cfd (se incluir cfd)
      if (parametros.params.cfd) {
        setEtapaAtual('cfd');
        adicionarLog('criando caso openfoam...', 'info');

        const respostaCFD = await fetch('http://localhost:8000/api/cfd/run-from-wizard', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            fileName: parametros.fileName,
            runSimulation: true
          })
        });

        if (!respostaCFD.ok) {
          throw new Error('erro ao criar caso cfd');
        }

        const dadosCFD = await respostaCFD.json();
        adicionarLog(`caso cfd criado: ${dadosCFD.simulation_id}`, 'success');
        setProgresso(75);

        // 4. monitorar execução
        setEtapaAtual('executando');
        adicionarLog('executando simulação cfd...', 'info');
        adicionarLog('isso pode levar vários minutos...', 'warning');

        // polling do status
        const monitorarSimulacao = async () => {
          const intervalo = setInterval(async () => {
            try {
              const respostaStatus = await fetch(`http://localhost:8000/api/cfd/status/${dadosCFD.simulation_id}`);
              const status = await respostaStatus.json();

              setProgresso(status.progress);

              if (status.status === 'completed') {
                clearInterval(intervalo);
                adicionarLog('simulação cfd concluída', 'success');
                setEtapaAtual('concluido');
                setProgresso(100);
                setDadosPipeline({
                  bedFile: dadosCompilacao.bed_file,
                  jsonFile: dadosCompilacao.json_file,
                  modelFile: caminhoModelo,
                  cfdCase: status.case_dir,
                  simulationId: dadosCFD.simulation_id
                });
              } else if (status.status === 'error') {
                clearInterval(intervalo);
                throw new Error(status.error || 'erro na simulação');
              } else {
                adicionarLog(`  ${status.message} (${status.progress}%)`, 'info');
              }
            } catch (err) {
              clearInterval(intervalo);
              setErro(err.message);
            }
          }, 3000); // verificar a cada 3s
        };

        monitorarSimulacao();
      } else {
        // sem cfd, concluir
        setEtapaAtual('concluido');
        setProgresso(100);
        adicionarLog('pipeline concluído (sem simulação cfd)', 'success');
        setDadosPipeline({
          bedFile: dadosCompilacao.bed_file,
          jsonFile: dadosCompilacao.json_file,
          modelFile: caminhoModelo
        });
      }
    } catch (err) {
      setErro(err.message);
      adicionarLog(`erro: ${err.message}`, 'error');
      setEtapaAtual('erro');
    }
  };

  // renderizar interface baseada na etapa
  const renderConteudo = () => {
    switch (etapaAtual) {
      case 'inicio':
        return (
          <div className="pipeline-inicio">
            <h2>pipeline completo - leitos empacotados</h2>
            <p className="descricao">
              execute o pipeline completo end-to-end: dsl → blender → openfoam
            </p>

            <div className="fluxo-visual">
              <div className="fluxo-etapa">
                <span className="fluxo-numero">1</span>
                <span className="fluxo-texto">criar parâmetros (.bed)</span>
              </div>
              <div className="fluxo-seta">→</div>
              <div className="fluxo-etapa">
                <span className="fluxo-numero">2</span>
                <span className="fluxo-texto">compilar dsl (.json)</span>
              </div>
              <div className="fluxo-seta">→</div>
              <div className="fluxo-etapa">
                <span className="fluxo-numero">3</span>
                <span className="fluxo-texto">gerar 3d (blender)</span>
              </div>
              <div className="fluxo-seta">→</div>
              <div className="fluxo-etapa">
                <span className="fluxo-numero">4</span>
                <span className="fluxo-texto">simular (openfoam)</span>
              </div>
              <div className="fluxo-seta">→</div>
              <div className="fluxo-etapa">
                <span className="fluxo-numero">5</span>
                <span className="fluxo-texto">visualizar</span>
              </div>
            </div>

            <div className="opcoes-inicio">
              <button className="btn btn-primary btn-large" onClick={() => setEtapaAtual('params')}>
                iniciar pipeline completo
              </button>
              <p className="hint">
                ou use as outras abas para executar etapas individuais
              </p>
            </div>
          </div>
        );

      case 'params':
        return (
          <div className="pipeline-params">
            <h2>parâmetros do pipeline</h2>
            <p>use o wizard interativo para configurar o leito</p>
            <div className="redirect-info">
              <p>redirecionando para o wizard...</p>
              <button className="btn btn-secondary" onClick={() => setEtapaAtual('inicio')}>
                voltar
              </button>
            </div>
          </div>
        );

      case 'compilando':
      case 'gerando3d':
      case 'cfd':
      case 'executando':
        return renderExecutando();

      case 'concluido':
        return renderConcluido();

      case 'erro':
        return renderErro();

      default:
        return null;
    }
  };

  const renderExecutando = () => (
    <div className="pipeline-executando">
      <h2>executando pipeline</h2>

      <div className="etapas-status">
        <div className={`etapa-item ${etapaAtual === 'compilando' ? 'ativa' : progresso > 25 ? 'concluida' : ''}`}>
          <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="editor" className="etapa-icone" />
          <span className="etapa-nome">compilando dsl</span>
        </div>
        <div className={`etapa-item ${etapaAtual === 'gerando3d' ? 'ativa' : progresso > 50 ? 'concluida' : ''}`}>
          <span className="etapa-icone etapa-marcador" aria-hidden="true">3d</span>
          <span className="etapa-nome">gerando modelo 3d</span>
        </div>
        <div className={`etapa-item ${etapaAtual === 'cfd' ? 'ativa' : progresso > 75 ? 'concluida' : ''}`}>
          <span className="etapa-icone etapa-marcador" aria-hidden="true">cfd</span>
          <span className="etapa-nome">preparando cfd</span>
        </div>
        <div className={`etapa-item ${etapaAtual === 'executando' ? 'ativa' : progresso === 100 ? 'concluida' : ''}`}>
          <span className="etapa-icone etapa-marcador" aria-hidden="true">run</span>
          <span className="etapa-nome">simulando</span>
        </div>
      </div>

      <div className="progress-container">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progresso}%` }} />
        </div>
        <span className="progress-text">{progresso}%</span>
      </div>

      <div className="log-container">
        <h3>log de execução</h3>
        <div className="log-content">
          {log.map((entrada, idx) => (
            <div key={idx} className={`log-entry log-${entrada.tipo}`}>
              <span className="log-time">{entrada.timestamp}</span>
              <span className="log-message">{entrada.mensagem}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderConcluido = () => (
    <div className="pipeline-concluido">
      <div className="success-header">
        <span className="success-icon" aria-hidden="true">ok</span>
        <h2>pipeline executado com sucesso!</h2>
      </div>

      {dadosPipeline && (
        <div className="resultados">
          <h3>arquivos gerados</h3>

          <div className="resultado-item">
            <strong>arquivo .bed:</strong>
            <code>{dadosPipeline.bedFile}</code>
          </div>

          <div className="resultado-item">
            <strong>parâmetros json:</strong>
            <code>{dadosPipeline.jsonFile}</code>
          </div>

          <div className="resultado-item">
            <strong>modelo 3d:</strong>
            <code>{dadosPipeline.modelFile}</code>
          </div>

          {dadosPipeline.cfdCase && (
            <div className="resultado-item">
              <strong>caso cfd:</strong>
              <code>{dadosPipeline.cfdCase}</code>
            </div>
          )}
        </div>
      )}

      <div className="proximos-passos">
        <h3>próximos passos</h3>
        <ul>
          <li>visualizar modelo 3d na aba "resultados"</li>
          {dadosPipeline?.cfdCase && (
            <>
              <li>abrir caso openfoam no wsl: <code>cd {dadosPipeline.cfdCase}</code></li>
              <li>executar simulação: <code>./Allrun</code></li>
              <li>visualizar no paraview: <code>paraview caso.foam</code></li>
            </>
          )}
          <li>ou executar novo pipeline</li>
        </ul>
      </div>

      <div className="acoes-final">
        <button className="btn btn-primary" onClick={() => window.location.reload()}>
          executar novo pipeline
        </button>
        <button className="btn btn-secondary" onClick={() => setEtapaAtual('inicio')}>
          voltar ao início
        </button>
      </div>

      <div className="log-final">
        <h4>log completo</h4>
        <div className="log-content-small">
          {log.map((entrada, idx) => (
            <div key={idx} className={`log-entry-small log-${entrada.tipo}`}>
              <span>{entrada.timestamp}</span> - {entrada.mensagem}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderErro = () => (
    <div className="pipeline-erro">
      <div className="erro-header">
        <span className="erro-icon" aria-hidden="true">!</span>
        <h2>erro no pipeline</h2>
      </div>

      <div className="erro-message">
        <strong>erro:</strong> {erro}
      </div>

      <div className="log-erro">
        <h4>log de execução</h4>
        <div className="log-content-small">
          {log.map((entrada, idx) => (
            <div key={idx} className={`log-entry-small log-${entrada.tipo}`}>
              <span>{entrada.timestamp}</span> - {entrada.mensagem}
            </div>
          ))}
        </div>
      </div>

      <div className="acoes-erro">
        <button className="btn btn-primary" onClick={() => setEtapaAtual('inicio')}>
          tentar novamente
        </button>
      </div>
    </div>
  );

  return (
    <div className="pipeline-completo">
      <div className="pipeline-header">
        <h1>pipeline completo end-to-end</h1>
        <p className="subtitle">
          automatize todo o processo: desde a criação até a simulação cfd
        </p>
      </div>

      {renderConteudo()}
    </div>
  );
};

export default PipelineCompleto;
