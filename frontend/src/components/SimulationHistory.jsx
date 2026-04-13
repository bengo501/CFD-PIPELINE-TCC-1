import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../context/LanguageContext';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import { listSimulations } from '../services/api';
import './SimulationHistory.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function formatDurationSeconds(sec, language) {
  if (typeof sec !== 'number' || sec < 0 || Number.isNaN(sec)) return '—';
  const s = Math.floor(sec);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (h > 0) return language === 'pt' ? `${h}h ${m}m` : `${h}h ${m}m`;
  if (m > 0) return language === 'pt' ? `${m}m` : `${m}m`;
  return language === 'pt' ? `${s}s` : `${s}s`;
}

function mapApiSimulation(item, language) {
  const created = item.created_at ? new Date(item.created_at) : null;
  const createdDate = created
    ? created.toLocaleString(language === 'pt' ? 'pt-BR' : 'en-US')
    : '—';
  return {
    id: item.id,
    name: item.name,
    description: item.description || '',
    status: item.status,
    createdDate,
    duration: formatDurationSeconds(item.execution_time, language),
    bedId: item.bed_id,
    progress: typeof item.progress === 'number' ? item.progress : 0
  };
}

function SimulationHistory() {
  const { language, t } = useLanguage();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  const loadSimulations = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await listSimulations({ page: 1, per_page: 100 });
      const items = Array.isArray(data?.items) ? data.items : [];
      setSimulations(items.map((row) => mapApiSimulation(row, language)));
    } catch (err) {
      console.error('simulation history:', err);
      if (isConnectionError(err)) {
        setLoadError(t('backendConnectionError'));
      } else {
        const detail = err.response?.data?.detail;
        setLoadError(
          typeof detail === 'string'
            ? detail
            : language === 'pt'
              ? 'erro ao carregar simulações'
              : 'failed to load simulations'
        );
      }
      setSimulations([]);
    } finally {
      setLoading(false);
    }
  }, [language, t]);

  useEffect(() => {
    loadSimulations();
  }, [loadSimulations]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="completed" className="status-icon completed" />;
      case 'running':
        return <ThemeIcon light="runLight.png" dark="runDark.png" alt="running" className="status-icon running" />;
      case 'pending':
        return <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="pending" className="status-icon pending" />;
      case 'failed':
        return <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="failed" className="status-icon failed" />;
      default:
        return null;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return language === 'pt' ? 'concluída' : 'completed';
      case 'running':
        return language === 'pt' ? 'em execução' : 'running';
      case 'pending':
        return language === 'pt' ? 'pendente' : 'pending';
      case 'failed':
        return language === 'pt' ? 'falhou' : 'failed';
      default:
        return status;
    }
  };

  const filteredSimulations = simulations.filter((sim) => {
    const desc = (sim.description || '').toLowerCase();
    const matchesSearch =
      sim.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      desc.includes(searchTerm.toLowerCase()) ||
      sim.id.toString().includes(searchTerm);

    const matchesFilter = activeFilter === 'all' || sim.status === activeFilter;

    return matchesSearch && matchesFilter;
  });

  const getFilterCount = (filter) => {
    if (filter === 'all') return simulations.length;
    return simulations.filter((sim) => sim.status === filter).length;
  };

  const handleViewSimulation = (id) => {
    console.log('visualizar simulação:', id);
  };

  const handleDownloadResults = (id) => {
    console.log('baixar resultados:', id);
  };

  const handleDeleteSimulation = (id) => {
    console.log('deletar simulação:', id);
  };

  const handleRerunSimulation = (id) => {
    console.log('reexecutar simulação:', id);
  };

  const emptyNoData = !loading && !loadError && simulations.length === 0;
  const emptyFiltered =
    !loading && !loadError && simulations.length > 0 && filteredSimulations.length === 0;

  return (
    <div className="simulation-history">
      <div className="history-header">
        <div className="history-title">
          <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="histórico" className="title-icon" />
          <h1>{language === 'pt' ? 'histórico de simulações' : 'simulation history'}</h1>
        </div>
        <p className="history-description">
          {language === 'pt'
            ? 'visualize e gerencie todas as suas simulações cfd'
            : 'view and manage all your cfd simulations'}
        </p>
      </div>

      <div className="history-controls">
        <button type="button" className="refresh-btn" onClick={loadSimulations} disabled={loading}>
          <ThemeIcon light="refreshLigh.png" dark="refreshDark.png" alt="atualizar" className="refresh-icon" />
          {language === 'pt' ? 'atualizar' : 'refresh'}
        </button>

        <div className="search-container">
          <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="buscar" className="search-icon" />
          <input
            type="text"
            placeholder={
              language === 'pt' ? 'buscar por nome, descrição ou id…' : 'search by name, description or id…'
            }
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="filter-tabs">
        <button
          type="button"
          className={`filter-tab ${activeFilter === 'all' ? 'active' : ''}`}
          onClick={() => setActiveFilter('all')}
        >
          {language === 'pt' ? 'todas' : 'all'} ({getFilterCount('all')})
        </button>
        <button
          type="button"
          className={`filter-tab ${activeFilter === 'completed' ? 'active' : ''}`}
          onClick={() => setActiveFilter('completed')}
        >
          <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="concluídas" className="filter-icon" />
          {language === 'pt' ? 'concluídas' : 'completed'} ({getFilterCount('completed')})
        </button>
        <button
          type="button"
          className={`filter-tab ${activeFilter === 'running' ? 'active' : ''}`}
          onClick={() => setActiveFilter('running')}
        >
          <ThemeIcon light="runLight.png" dark="runDark.png" alt="executando" className="filter-icon" />
          {language === 'pt' ? 'em execução' : 'running'} ({getFilterCount('running')})
        </button>
        <button
          type="button"
          className={`filter-tab ${activeFilter === 'pending' ? 'active' : ''}`}
          onClick={() => setActiveFilter('pending')}
        >
          <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="pendentes" className="filter-icon" />
          {language === 'pt' ? 'pendentes' : 'pending'} ({getFilterCount('pending')})
        </button>
        <button
          type="button"
          className={`filter-tab ${activeFilter === 'failed' ? 'active' : ''}`}
          onClick={() => setActiveFilter('failed')}
        >
          <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="falharam" className="filter-icon" />
          {language === 'pt' ? 'falharam' : 'failed'} ({getFilterCount('failed')})
        </button>
      </div>

      {loadError && <BackendConnectionError message={loadError} />}

      {loading && (
        <div className="sim-history-loading">
          {language === 'pt' ? 'carregando…' : 'loading…'}
        </div>
      )}

      {!loading && emptyNoData && (
        <div className="sim-history-empty">
          <p>{language === 'pt' ? 'nenhuma simulação encontrada' : 'no simulations found'}</p>
          <p className="sim-history-empty-hint">
            {language === 'pt'
              ? 'use o wizard ou o pipeline para criar leitos e registar simulações'
              : 'use the wizard or pipeline to create beds and register simulations'}
          </p>
        </div>
      )}

      {!loading && !loadError && emptyFiltered && (
        <div className="sim-history-empty">
          <p>{language === 'pt' ? 'nenhum resultado para os filtros atuais' : 'no results for current filters'}</p>
          <p className="sim-history-empty-hint">
            {language === 'pt' ? 'ajuste a busca ou as abas de estado' : 'adjust search or status tabs'}
          </p>
        </div>
      )}

      {!loading && filteredSimulations.length > 0 && (
        <div className="simulations-list">
          {filteredSimulations.map((simulation) => (
            <div key={simulation.id} className="simulation-card">
              <div className="sim-card-row sim-card-row-top">
                <div className="simulation-status">
                  {getStatusIcon(simulation.status)}
                  <span className="status-text">{getStatusText(simulation.status)}</span>
                </div>
                <span className="simulation-id">id {simulation.id}</span>
              </div>

              <div className="simulation-info">
                <h3 className="simulation-name">{simulation.name}</h3>
                {simulation.description ? (
                  <p className="simulation-description">{simulation.description}</p>
                ) : null}
                <div className="simulation-meta">
                  <span className="simulation-date">{simulation.createdDate}</span>
                  <span className="simulation-duration">{simulation.duration}</span>
                  {simulation.status === 'running' ? (
                    <span className="simulation-progress">{simulation.progress}%</span>
                  ) : null}
                </div>
              </div>

              <div className="simulation-actions">
                <button
                  type="button"
                  className="action-btn view-btn"
                  onClick={() => handleViewSimulation(simulation.id)}
                  title={language === 'pt' ? 'visualizar' : 'view'}
                >
                  <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="" className="action-icon" />
                </button>
                <button
                  type="button"
                  className="action-btn download-btn"
                  onClick={() => handleDownloadResults(simulation.id)}
                  title={language === 'pt' ? 'baixar' : 'download'}
                >
                  <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="" className="action-icon" />
                </button>
                <button
                  type="button"
                  className="action-btn delete-btn"
                  onClick={() => handleDeleteSimulation(simulation.id)}
                  title={language === 'pt' ? 'deletar' : 'delete'}
                >
                  <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="" className="action-icon" />
                </button>
                <button
                  type="button"
                  className="action-btn rerun-btn"
                  onClick={() => handleRerunSimulation(simulation.id)}
                  title={language === 'pt' ? 'reexecutar' : 'rerun'}
                >
                  <ThemeIcon light="runLight.png" dark="runDark.png" alt="" className="action-icon" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SimulationHistory;
