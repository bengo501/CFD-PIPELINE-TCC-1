import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../context/LanguageContext';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import {
  getHistoryFeed,
  getSimulation,
  deleteSimulation,
  createSimulationRecord,
  buildGeneratedFileUrl,
} from '../services/api';
import { useActiveUser } from '../context/UserContext';
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

function slugify(s) {
  return String(s || 'simulacao')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60) || 'simulacao';
}

function SimulationHistory() {
  const { language, t } = useLanguage();
  const { activeUserId } = useActiveUser();
  const pt = language === 'pt';
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [simulations, setSimulations] = useState([]);
  const [models3d, setModels3d] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [opError, setOpError] = useState(null);
  const [opSuccess, setOpSuccess] = useState(null);
  const [actionBusyId, setActionBusyId] = useState(null);
  const [viewModalId, setViewModalId] = useState(null);
  const [viewDetail, setViewDetail] = useState(null);
  const [viewLoading, setViewLoading] = useState(false);

  const loadSimulations = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await getHistoryFeed(100);
      const items = Array.isArray(data?.simulations) ? data.simulations : [];
      const modelItems = Array.isArray(data?.models_3d) ? data.models_3d : [];
      setSimulations(items.map((row) => mapApiSimulation(row, language)));
      setModels3d(modelItems);
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
      setModels3d([]);
    } finally {
      setLoading(false);
    }
  }, [language, t]);

  useEffect(() => {
    loadSimulations();
    const timer = window.setInterval(loadSimulations, 5000);
    return () => window.clearInterval(timer);
  }, [activeUserId, loadSimulations]);

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

  const flashSuccess = useCallback((msg) => {
    setOpSuccess(msg);
    setTimeout(() => setOpSuccess(null), 2500);
  }, []);

  const closeViewModal = useCallback(() => {
    setViewModalId(null);
    setViewDetail(null);
    setViewLoading(false);
  }, []);

  useEffect(() => {
    if (viewModalId == null) return;
    const onKey = (e) => {
      if (e.key === 'Escape') closeViewModal();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [viewModalId, closeViewModal]);

  const handleViewSimulation = async (id) => {
    setOpError(null);
    setViewModalId(id);
    setViewLoading(true);
    setViewDetail(null);
    try {
      const data = await getSimulation(id);
      setViewDetail(data);
    } catch (err) {
      console.error('erro ao obter simulacao:', err);
      if (isConnectionError(err)) setOpError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao carregar detalhes' : 'failed to load details'));
      closeViewModal();
    } finally {
      setViewLoading(false);
    }
  };

  const handleDownloadResults = async (id) => {
    setOpError(null);
    setActionBusyId(id);
    try {
      const data = await getSimulation(id);
      const filename = `simulacao_${data.id}_${slugify(data.name)}.json`;
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      flashSuccess(pt ? 'dados baixados' : 'data downloaded');
    } catch (err) {
      console.error('erro ao baixar:', err);
      if (isConnectionError(err)) setOpError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao baixar' : 'download failed'));
    } finally {
      setActionBusyId(null);
    }
  };

  const handleDeleteSimulation = async (id) => {
    setOpError(null);
    const ok = window.confirm(
      pt
        ? `eliminar a simulação #${id} e todos os seus resultados? esta ação é irreversível.`
        : `delete simulation #${id} and all its results? this action cannot be undone.`
    );
    if (!ok) return;
    setActionBusyId(id);
    try {
      await deleteSimulation(id);
      flashSuccess(pt ? 'simulação eliminada' : 'simulation deleted');
      await loadSimulations();
    } catch (err) {
      console.error('erro ao deletar:', err);
      if (isConnectionError(err)) setOpError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao eliminar' : 'delete failed'));
    } finally {
      setActionBusyId(null);
    }
  };

  const handleRerunSimulation = async (id) => {
    setOpError(null);
    const ok = window.confirm(
      pt
        ? `duplicar os parâmetros da simulação #${id} e criar uma nova execução?`
        : `clone parameters of simulation #${id} and create a new run?`
    );
    if (!ok) return;
    setActionBusyId(id);
    try {
      const src = await getSimulation(id);
      const payload = {
        bed_id: src.bed_id,
        name: `${src.name || (pt ? 'simulação' : 'simulation')} (${pt ? 're-execução' : 're-run'})`,
        description: src.description || '',
        regime: src.regime,
        inlet_velocity: src.inlet_velocity,
        fluid_density: src.fluid_density,
        fluid_viscosity: src.fluid_viscosity,
        solver: src.solver || 'simpleFoam',
        max_iterations: src.max_iterations ?? 1000,
        convergence_criteria: src.convergence_criteria ?? 1e-4,
        parameters_json: src.parameters_json || null,
      };
      const created = await createSimulationRecord(payload);
      flashSuccess(pt ? `nova simulação criada #${created.id}` : `new simulation created #${created.id}`);
      await loadSimulations();
    } catch (err) {
      console.error('erro ao reexecutar:', err);
      if (isConnectionError(err)) setOpError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao reexecutar' : 'rerun failed'));
    } finally {
      setActionBusyId(null);
    }
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

      {opError && (
        <div className="history-op-error" role="alert">
          {opError}
        </div>
      )}

      {opSuccess && (
        <div className="history-op-success" role="status">
          {opSuccess}
        </div>
      )}

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

      {!loading && models3d.length > 0 && (
        <div className="simulations-list">
          <h2 className="history-subtitle">{pt ? 'modelos 3d persistidos' : 'persisted 3d models'}</h2>
          {models3d.map((model) => (
            <div key={`model-${model.id}`} className="simulation-card">
              <div className="sim-card-row sim-card-row-top">
                <div className="simulation-status">
                  <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="model" className="status-icon" />
                  <span className="status-text">{pt ? 'modelo 3d' : '3d model'}</span>
                </div>
                <span className="simulation-id">id {model.id}</span>
              </div>

              <div className="simulation-info">
                <h3 className="simulation-name">{model.name}</h3>
                {model.description ? (
                  <p className="simulation-description">{model.description}</p>
                ) : null}
                <div className="simulation-meta">
                  <span className="simulation-date">
                    {model.created_at
                      ? new Date(model.created_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                      : '—'}
                  </span>
                  <span className="simulation-duration">
                    {model.blend_file_path ? '.blend ' : ''}{model.stl_file_path ? '.stl' : ''}
                  </span>
                </div>
              </div>

              <div className="simulation-actions">
                <button
                  type="button"
                  className="action-btn download-btn"
                  onClick={() => {
                    const url = buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path);
                    if (url) window.open(url, '_blank');
                  }}
                  title={pt ? 'baixar modelo' : 'download model'}
                  disabled={!buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path)}
                >
                  <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="" className="action-icon" />
                </button>
              </div>
            </div>
          ))}
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
                  disabled={actionBusyId === simulation.id}
                >
                  <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="" className="action-icon" />
                </button>
                <button
                  type="button"
                  className="action-btn download-btn"
                  onClick={() => handleDownloadResults(simulation.id)}
                  title={language === 'pt' ? 'baixar' : 'download'}
                  disabled={actionBusyId === simulation.id}
                >
                  <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="" className="action-icon" />
                </button>
                <button
                  type="button"
                  className="action-btn delete-btn"
                  onClick={() => handleDeleteSimulation(simulation.id)}
                  title={language === 'pt' ? 'deletar' : 'delete'}
                  disabled={actionBusyId === simulation.id}
                >
                  <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="" className="action-icon" />
                </button>
                <button
                  type="button"
                  className="action-btn rerun-btn"
                  onClick={() => handleRerunSimulation(simulation.id)}
                  title={language === 'pt' ? 'reexecutar' : 'rerun'}
                  disabled={actionBusyId === simulation.id}
                >
                  <ThemeIcon light="runLight.png" dark="runDark.png" alt="" className="action-icon" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {viewModalId != null && (
        <div
          className="history-modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-label={pt ? 'detalhes da simulação' : 'simulation details'}
          onClick={closeViewModal}
        >
          <div className="history-modal" onClick={(e) => e.stopPropagation()}>
            <div className="history-modal-header">
              <h2>
                {pt ? 'detalhes da simulação' : 'simulation details'}
                {viewDetail ? ` · #${viewDetail.id}` : ''}
              </h2>
              <button
                type="button"
                className="history-modal-close"
                onClick={closeViewModal}
                aria-label={pt ? 'fechar' : 'close'}
              >
                ×
              </button>
            </div>
            <div className="history-modal-body">
              {viewLoading && (
                <div className="history-modal-loading">
                  {pt ? 'carregando…' : 'loading…'}
                </div>
              )}
              {!viewLoading && viewDetail && (
                <div className="history-detail-grid">
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'nome' : 'name'}</span>
                    <span className="history-detail-value">{viewDetail.name || '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'estado' : 'status'}</span>
                    <span className="history-detail-value">{getStatusText(viewDetail.status)}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'leito' : 'bed'}</span>
                    <span className="history-detail-value">#{viewDetail.bed_id}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'regime' : 'regime'}</span>
                    <span className="history-detail-value">{viewDetail.regime || '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'solver' : 'solver'}</span>
                    <span className="history-detail-value">{viewDetail.solver || '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'velocidade de entrada' : 'inlet velocity'}</span>
                    <span className="history-detail-value">{viewDetail.inlet_velocity} m/s</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'densidade' : 'density'}</span>
                    <span className="history-detail-value">{viewDetail.fluid_density} kg/m³</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'viscosidade' : 'viscosity'}</span>
                    <span className="history-detail-value">{viewDetail.fluid_viscosity} Pa·s</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'iterações máx.' : 'max iterations'}</span>
                    <span className="history-detail-value">{viewDetail.max_iterations ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'critério convergência' : 'convergence criteria'}</span>
                    <span className="history-detail-value">{viewDetail.convergence_criteria ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'progresso' : 'progress'}</span>
                    <span className="history-detail-value">{viewDetail.progress ?? 0}%</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'queda de pressão' : 'pressure drop'}</span>
                    <span className="history-detail-value">
                      {viewDetail.pressure_drop != null ? `${viewDetail.pressure_drop} Pa` : '—'}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'velocidade média' : 'average velocity'}</span>
                    <span className="history-detail-value">
                      {viewDetail.average_velocity != null ? `${viewDetail.average_velocity} m/s` : '—'}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'número de reynolds' : 'reynolds number'}</span>
                    <span className="history-detail-value">{viewDetail.reynolds_number ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'células de malha' : 'mesh cells'}</span>
                    <span className="history-detail-value">{viewDetail.mesh_cells_count ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'qualidade da malha' : 'mesh quality'}</span>
                    <span className="history-detail-value">{viewDetail.mesh_quality ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'duração' : 'execution time'}</span>
                    <span className="history-detail-value">
                      {formatDurationSeconds(viewDetail.execution_time, language)}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'criado em' : 'created at'}</span>
                    <span className="history-detail-value">
                      {viewDetail.created_at
                        ? new Date(viewDetail.created_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                        : '—'}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'iniciado em' : 'started at'}</span>
                    <span className="history-detail-value">
                      {viewDetail.started_at
                        ? new Date(viewDetail.started_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                        : '—'}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'concluído em' : 'completed at'}</span>
                    <span className="history-detail-value">
                      {viewDetail.completed_at
                        ? new Date(viewDetail.completed_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                        : '—'}
                    </span>
                  </div>
                  {viewDetail.description ? (
                    <div className="history-detail-row history-detail-row-wide">
                      <span className="history-detail-label">{pt ? 'descrição' : 'description'}</span>
                      <span className="history-detail-value">{viewDetail.description}</span>
                    </div>
                  ) : null}
                  {viewDetail.case_directory ? (
                    <div className="history-detail-row history-detail-row-wide">
                      <span className="history-detail-label">{pt ? 'diretório do caso' : 'case directory'}</span>
                      <code className="history-detail-code">{viewDetail.case_directory}</code>
                    </div>
                  ) : null}
                  {viewDetail.log_file_path ? (
                    <div className="history-detail-row history-detail-row-wide">
                      <span className="history-detail-label">{pt ? 'arquivo de log' : 'log file'}</span>
                      <code className="history-detail-code">{viewDetail.log_file_path}</code>
                    </div>
                  ) : null}
                  {viewDetail.parameters_json ? (
                    <div className="history-detail-row history-detail-row-wide">
                      <span className="history-detail-label">{pt ? 'parâmetros' : 'parameters'}</span>
                      <pre className="history-detail-json">
                        {JSON.stringify(viewDetail.parameters_json, null, 2)}
                      </pre>
                    </div>
                  ) : null}
                </div>
              )}
            </div>
            <div className="history-modal-footer">
              <button
                type="button"
                className="history-modal-btn"
                onClick={() => viewDetail && handleDownloadResults(viewDetail.id)}
                disabled={!viewDetail || actionBusyId === viewDetail?.id}
              >
                {pt ? 'baixar json' : 'download json'}
              </button>
              <button type="button" className="history-modal-btn primary" onClick={closeViewModal}>
                {pt ? 'fechar' : 'close'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SimulationHistory;
