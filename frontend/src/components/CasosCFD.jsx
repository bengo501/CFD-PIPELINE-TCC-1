import { useState, useEffect } from 'react';
import '../styles/CasosCFD.css';
import ThemeIcon from './ThemeIcon';

const CasosCFD = () => {
  const [casos, setCasos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [casoSelecionado, setCasoSelecionado] = useState(null);

  // carregar casos ao montar
  useEffect(() => {
    carregarCasos();
  }, []);

  const carregarCasos = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/casos/list');
      
      if (response.ok) {
        const data = await response.json();
        setCasos(data.casos);
      } else {
        setError('erro ao carregar casos');
      }
    } catch (err) {
      setError('erro de conexão com o backend');
      console.error('erro:', err);
    } finally {
      setLoading(false);
    }
  };

  const obterDetalhes = async (nomeCaso) => {
    try {
      const response = await fetch(`http://localhost:8000/api/casos/${nomeCaso}/detalhes`);
      
      if (response.ok) {
        const data = await response.json();
        setCasoSelecionado(data);
      }
    } catch (err) {
      console.error('erro ao obter detalhes:', err);
    }
  };

  const deletarCaso = async (nomeCaso) => {
    if (!confirm(`tem certeza que deseja deletar o caso "${nomeCaso}"? esta ação não pode ser desfeita!`)) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8000/api/casos/${nomeCaso}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        alert('caso deletado com sucesso!');
        carregarCasos();
        setCasoSelecionado(null);
      } else {
        alert('erro ao deletar caso');
      }
    } catch (err) {
      alert('erro de conexão');
      console.error('erro:', err);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'configured': { text: 'configurado', class: 'status-configured', desc: 'pronto para executar' },
      'meshed': { text: 'com malha', class: 'status-meshed', desc: 'malha gerada' },
      'running': { text: 'executando', class: 'status-running', desc: 'simulação em andamento' },
      'completed': { text: 'concluído', class: 'status-completed', desc: 'simulação finalizada' },
      'unknown': { text: 'desconhecido', class: 'status-unknown', desc: 'status indefinido' }
    };
    
    const info = statusMap[status] || statusMap['unknown'];
    
    return (
      <span className={`status-badge ${info.class}`} title={info.desc}>
        {info.text}
      </span>
    );
  };

  const abrirExplorador = (caminho) => {
    // copiar caminho para clipboard
    navigator.clipboard.writeText(caminho);
    alert(`caminho copiado!\n\n${caminho}\n\nabra o explorador de arquivos e cole o caminho na barra de endereço.`);
  };

  if (loading) {
    return (
      <div className="casos-cfd">
        <div className="loading">carregando casos...</div>
      </div>
    );
  }

  return (
    <div className="casos-cfd">
      <div className="casos-header">
        <div>
          <h2>casos cfd existentes</h2>
          <p className="casos-desc">
            gerenciamento de casos openfoam criados pelo sistema
          </p>
        </div>
        <button className="btn btn-refresh" onClick={carregarCasos}>
          <ThemeIcon light="updateLight-removebg-preview.png" dark="updateDark-removebg-preview.png" alt="atualizar" className="btn-icon" />
          atualizar
        </button>
      </div>

      {error && (
        <div className="error-message">
          <strong>erro:</strong> {error}
        </div>
      )}

      {casos.length === 0 ? (
        <div className="sem-casos">
          <p>nenhum caso cfd encontrado</p>
          <p className="hint">
            use o wizard para criar leitos e gerar casos cfd
          </p>
        </div>
      ) : (
        <div className="casos-grid">
          {casos.map((caso) => (
            <div key={caso.nome} className="caso-card">
              <div className="caso-header">
                <h3>{caso.nome}</h3>
                {getStatusBadge(caso.status)}
              </div>
              
              <div className="caso-info">
                <div className="info-row">
                  <span className="info-label">criado:</span>
                  <span>{new Date(caso.created_at).toLocaleString()}</span>
                </div>
                
                <div className="info-row">
                  <span className="info-label">tamanho:</span>
                  <span>{caso.tamanho_mb} mb</span>
                </div>
                
                <div className="info-row">
                  <span className="info-label">pastas de tempo:</span>
                  <span>{caso.pastas_tempo} resultado(s)</span>
                </div>
                
                <div className="info-row">
                  <span className="info-label">malha:</span>
                  <span>{caso.tem_malha ? '✅ gerada' : '❌ não gerada'}</span>
                </div>
              </div>
              
              <div className="caso-caminho">
                <strong>caminho:</strong>
                <code onClick={() => abrirExplorador(caso.caminho)} title="clique para copiar">
                  {caso.caminho_relativo}
                </code>
              </div>
              
              {caso.logs.length > 0 && (
                <div className="caso-logs">
                  <strong>logs:</strong>
                  <div className="logs-list">
                    {caso.logs.map((log) => (
                      <span key={log} className="log-badge">{log}</span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="caso-acoes">
                <button 
                  className="btn btn-small btn-details"
                  onClick={() => obterDetalhes(caso.nome)}
                >
                  ver detalhes
                </button>
                
                {caso.status === 'configured' && (
                  <button className="btn btn-small btn-execute">
                    executar no wsl
                  </button>
                )}
                
                <button 
                  className="btn btn-small btn-delete"
                  onClick={() => deletarCaso(caso.nome)}
                >
                  deletar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {casoSelecionado && (
        <div className="modal-overlay" onClick={() => setCasoSelecionado(null)}>
          <div className="modal-detalhes" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>detalhes do caso: {casoSelecionado.nome}</h3>
              <button className="modal-close" onClick={() => setCasoSelecionado(null)}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="detalhe-secao">
                <h4>status</h4>
                {getStatusBadge(casoSelecionado.status)}
              </div>
              
              <div className="detalhe-secao">
                <h4>informações</h4>
                <p><strong>criado:</strong> {new Date(casoSelecionado.created_at).toLocaleString()}</p>
                <p><strong>modificado:</strong> {new Date(casoSelecionado.modified_at).toLocaleString()}</p>
                <p><strong>tamanho:</strong> {casoSelecionado.tamanho_mb} mb</p>
              </div>
              
              <div className="detalhe-secao">
                <h4>arquivos</h4>
                <p>✅ allrun: {casoSelecionado.tem_allrun ? 'sim' : 'não'}</p>
                <p>✅ geometria stl: {casoSelecionado.tem_stl ? 'sim' : 'não'}</p>
                <p>✅ malha: {casoSelecionado.tem_malha ? 'sim' : 'não'}</p>
              </div>
              
              {casoSelecionado.tempos_disponiveis && (
                <div className="detalhe-secao">
                  <h4>tempos disponíveis ({casoSelecionado.tempos_disponiveis.length})</h4>
                  <div className="tempos-list">
                    {casoSelecionado.tempos_disponiveis.slice(0, 10).map(t => (
                      <span key={t} className="tempo-badge">{t}</span>
                    ))}
                    {casoSelecionado.tempos_disponiveis.length > 10 && (
                      <span className="tempo-badge">+{casoSelecionado.tempos_disponiveis.length - 10} mais</span>
                    )}
                  </div>
                </div>
              )}
              
              {casoSelecionado.configuracao && (
                <div className="detalhe-secao">
                  <h4>configuração temporal</h4>
                  <p><strong>tempo inicial:</strong> {casoSelecionado.configuracao.startTime}</p>
                  <p><strong>tempo final:</strong> {casoSelecionado.configuracao.endTime}</p>
                  <p><strong>delta t:</strong> {casoSelecionado.configuracao.deltaT}</p>
                </div>
              )}
              
              <div className="detalhe-secao">
                <h4>como executar</h4>
                <pre className="comando-wsl">
{`# abrir wsl
wsl

# navegar até o caso
cd ${casoSelecionado.caminho.replace(/\\/g, '/').replace('C:', '/mnt/c')}

# carregar openfoam
source /opt/openfoam11/etc/bashrc

# executar
./Allrun`}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CasosCFD;

