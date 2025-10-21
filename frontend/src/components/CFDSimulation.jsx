import { useState, useEffect } from 'react';
import '../styles/CFDSimulation.css';
import ThemeIcon from './ThemeIcon';

const CFDSimulation = ({ bedFileName }) => {
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // carregar lista de simulacoes
  const loadSimulations = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/cfd/list');
      if (response.ok) {
        const data = await response.json();
        setSimulations(data.simulations);
      }
    } catch (err) {
      console.error('erro ao carregar simulacoes:', err);
    }
  };

  // criar nova simulacao
  const startSimulation = async (runSim = true) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:3000/api/cfd/run-from-wizard', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileName: bedFileName,
          runSimulation: runSim
        }),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`simulacao iniciada! id: ${data.simulation_id}`);
        loadSimulations();
      } else {
        const error = await response.json();
        setError(error.detail);
      }
    } catch (err) {
      setError('erro de conexao com o backend');
      console.error('erro:', err);
    } finally {
      setLoading(false);
    }
  };

  // deletar simulacao
  const deleteSimulation = async (simId) => {
    try {
      const response = await fetch(`http://localhost:3000/api/cfd/${simId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        loadSimulations();
      }
    } catch (err) {
      console.error('erro ao deletar:', err);
    }
  };

  // auto-refresh
  useEffect(() => {
    loadSimulations();
    
    if (autoRefresh) {
      const interval = setInterval(loadSimulations, 3000); // atualizar a cada 3s
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // status badge
  const getStatusBadge = (status) => {
    const statusMap = {
      'queued': { text: 'na fila', class: 'status-queued' },
      'preparing': { text: 'preparando', class: 'status-preparing' },
      'meshing': { text: 'gerando malha', class: 'status-meshing' },
      'running': { text: 'executando', class: 'status-running' },
      'completed': { text: 'concluido', class: 'status-completed' },
      'error': { text: 'erro', class: 'status-error' }
    };
    
    const info = statusMap[status] || { text: status, class: 'status-unknown' };
    
    return <span className={`status-badge ${info.class}`}>{info.text}</span>;
  };

  return (
    <div className="cfd-simulation">
      <div className="cfd-header">
        <h2>simulacoes cfd</h2>
        <div className="cfd-actions">
          <label className="auto-refresh">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            auto-atualizar
          </label>
          <button 
            className="btn btn-refresh"
            onClick={loadSimulations}
            disabled={loading}
          >
            <ThemeIcon light="updateLight-removebg-preview.png" dark="updateDark-removebg-preview.png" alt="atualizar" className="btn-icon" />
            atualizar
          </button>
        </div>
      </div>

      {bedFileName && (
        <div className="cfd-create">
          <h3>criar nova simulacao</h3>
          <p>arquivo: <strong>{bedFileName}</strong></p>
          <div className="create-buttons">
            <button
              className="btn btn-primary"
              onClick={() => startSimulation(false)}
              disabled={loading}
            >
              criar caso openfoam
            </button>
            <button
              className="btn btn-success"
              onClick={() => startSimulation(true)}
              disabled={loading}
            >
              criar e executar simulacao
            </button>
          </div>
          <p className="hint">
            "criar caso" apenas prepara arquivos. "executar" roda a simulacao completa.
          </p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <strong>erro:</strong> {error}
        </div>
      )}

      <div className="simulations-list">
        <h3>simulacoes ({simulations.length})</h3>
        
        {simulations.length === 0 ? (
          <p className="no-simulations">nenhuma simulacao encontrada</p>
        ) : (
          <div className="simulations-grid">
            {simulations.map((sim) => (
              <div key={sim.simulation_id} className="simulation-card">
                <div className="sim-header">
                  <span className="sim-id">#{sim.simulation_id}</span>
                  {getStatusBadge(sim.status)}
                </div>
                
                <div className="sim-progress">
                  <div className="progress-bar-container">
                    <div 
                      className="progress-bar-fill" 
                      style={{ width: `${sim.progress}%` }}
                    />
                  </div>
                  <span className="progress-text">{sim.progress}%</span>
                </div>
                
                <p className="sim-message">{sim.message}</p>
                
                <div className="sim-info">
                  <small>criado: {new Date(sim.created_at).toLocaleString()}</small>
                  {sim.completed_at && (
                    <small>concluido: {new Date(sim.completed_at).toLocaleString()}</small>
                  )}
                </div>
                
                {sim.case_dir && (
                  <div className="sim-path">
                    <strong>caso:</strong> <code>{sim.case_dir}</code>
                  </div>
                )}
                
                {sim.error && (
                  <div className="sim-error">
                    <strong>erro:</strong> {sim.error}
                  </div>
                )}
                
                <div className="sim-actions">
                  {sim.status === 'completed' && (
                    <button className="btn btn-small btn-view">
                      visualizar resultados
                    </button>
                  )}
                  <button 
                    className="btn btn-small btn-delete"
                    onClick={() => deleteSimulation(sim.simulation_id)}
                  >
                    remover
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CFDSimulation;

