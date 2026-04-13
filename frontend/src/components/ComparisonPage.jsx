import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../context/LanguageContext';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import { listSimulations } from '../services/api';
import './ComparisonPage.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function mapApiToCard(item, language) {
  const date = item.created_at
    ? new Date(item.created_at).toLocaleDateString(language === 'pt' ? 'pt-BR' : 'en-US')
    : '—';
  let pressure = language === 'pt' ? 'n/d' : 'n/a';
  if (item.pressure_drop != null && Number.isFinite(Number(item.pressure_drop))) {
    pressure = `${Number(item.pressure_drop).toFixed(1)} pa`;
  }
  return {
    id: item.id,
    name: item.name,
    description: item.description || '',
    status: item.status,
    date,
    mainResults: {
      pressure,
      efficiency: language === 'pt' ? 'n/d' : 'n/a'
    }
  };
}

function ComparisonPage() {
  const { language, t } = useLanguage();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('completed');
  const [selectedSimulations, setSelectedSimulations] = useState([]);
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  const loadSimulations = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await listSimulations({ page: 1, per_page: 100 });
      const items = Array.isArray(data?.items) ? data.items : [];
      setSimulations(items.map((row) => mapApiToCard(row, language)));
    } catch (err) {
      console.error('comparison page:', err);
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

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleSimulationSelect = (id) => {
    setSelectedSimulations((prevSelected) => {
      if (prevSelected.includes(id)) {
        return prevSelected.filter((simId) => simId !== id);
      }
      if (prevSelected.length < 2) {
        return [...prevSelected, id];
      }
      return prevSelected;
    });
  };

  const filteredSimulations = simulations.filter((sim) => {
    const desc = (sim.description || '').toLowerCase();
    const matchesSearch =
      sim.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      desc.includes(searchTerm.toLowerCase());
    const matchesFilter = activeFilter === 'all' || sim.status === activeFilter;
    return matchesSearch && matchesFilter;
  });

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

  const getStatusClass = (status) => {
    switch (status) {
      case 'completed':
        return 'status-completed';
      case 'running':
        return 'status-running';
      case 'pending':
        return 'status-pending';
      case 'failed':
        return 'status-failed';
      default:
        return '';
    }
  };

  const getFilterCount = (filter) => {
    if (filter === 'all') return simulations.length;
    return simulations.filter((sim) => sim.status === filter).length;
  };

  const filterOptions = [
    { key: 'all', labelPt: 'todas', labelEn: 'all' },
    { key: 'completed', labelPt: 'concluídas', labelEn: 'completed' },
    { key: 'running', labelPt: 'em execução', labelEn: 'running' },
    { key: 'pending', labelPt: 'pendentes', labelEn: 'pending' },
    { key: 'failed', labelPt: 'falharam', labelEn: 'failed' }
  ];

  const emptyNoData = !loading && !loadError && simulations.length === 0;
  const emptyFiltered =
    !loading && !loadError && simulations.length > 0 && filteredSimulations.length === 0;

  return (
    <div className="comparison-page">
      <div className="comparison-header">
        <div className="comparison-title">
          <ThemeIcon light="compareLight.png" dark="compareDark.png" alt="comparisons" className="title-icon" />
          <h1>{language === 'pt' ? 'comparações' : 'comparisons'}</h1>
        </div>
        <p className="comparison-description">
          {language === 'pt'
            ? 'compare simulações lado a lado e analise diferenças'
            : 'compare simulations side by side and analyze differences'}
        </p>
      </div>

      <div className="comparison-page-toolbar">
        <button type="button" className="comparison-refresh-btn" onClick={loadSimulations} disabled={loading}>
          <ThemeIcon light="refreshLigh.png" dark="refreshDark.png" alt="" className="comparison-refresh-icon" />
          {language === 'pt' ? 'atualizar' : 'refresh'}
        </button>
      </div>

      {loadError && <BackendConnectionError message={loadError} />}

      <div className="selection-section">
        <h2>{language === 'pt' ? 'selecionar simulações para comparar' : 'select simulations to compare'}</h2>
        <p className="selection-instruction">
          {language === 'pt' ? 'selecione exatamente duas simulações concluídas' : 'select exactly two completed simulations'}
        </p>

        {loading && (
          <p className="comparison-loading">{language === 'pt' ? 'carregando…' : 'loading…'}</p>
        )}

        {!loading && !loadError && (
          <>
            <div className="comparison-controls">
              <div className="search-bar">
                <ThemeIcon
                  light="triangle_white_outline.png"
                  dark="triangle_black_outline.png"
                  alt=""
                  className="search-icon"
                />
                <input
                  type="text"
                  placeholder={language === 'pt' ? 'buscar simulações…' : 'search simulations…'}
                  value={searchTerm}
                  onChange={handleSearchChange}
                />
              </div>
              <div className="filter-chips" role="group" aria-label={language === 'pt' ? 'filtro de estado' : 'status filter'}>
                {filterOptions.map((opt) => (
                  <button
                    key={opt.key}
                    type="button"
                    className={`filter-chip ${activeFilter === opt.key ? 'active' : ''}`}
                    onClick={() => setActiveFilter(opt.key)}
                  >
                    {language === 'pt' ? opt.labelPt : opt.labelEn} ({getFilterCount(opt.key)})
                  </button>
                ))}
              </div>
            </div>

            {emptyNoData && (
              <div className="comparison-empty">
                <p>{language === 'pt' ? 'nenhuma simulação encontrada' : 'no simulations found'}</p>
                <p className="comparison-empty-hint">
                  {language === 'pt'
                    ? 'com o backend ativo, as simulações registadas aparecem aqui'
                    : 'with the backend running, registered simulations appear here'}
                </p>
              </div>
            )}

            {emptyFiltered && (
              <div className="comparison-empty">
                <p>{language === 'pt' ? 'nenhum resultado para os filtros atuais' : 'no results for current filters'}</p>
              </div>
            )}

            {!emptyNoData && filteredSimulations.length > 0 && (
              <div className="simulation-cards-grid">
                {filteredSimulations.map((sim) => (
                  <div
                    key={sim.id}
                    className={`simulation-card ${selectedSimulations.includes(sim.id) ? 'selected' : ''} ${
                      sim.status === 'completed' ? '' : 'disabled'
                    }`}
                    onClick={() => sim.status === 'completed' && handleSimulationSelect(sim.id)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        if (sim.status === 'completed') handleSimulationSelect(sim.id);
                      }
                    }}
                    role="button"
                    tabIndex={sim.status === 'completed' ? 0 : -1}
                  >
                    <input
                      type="checkbox"
                      checked={selectedSimulations.includes(sim.id)}
                      onChange={() => sim.status === 'completed' && handleSimulationSelect(sim.id)}
                      disabled={
                        sim.status !== 'completed' ||
                        (selectedSimulations.length === 2 && !selectedSimulations.includes(sim.id))
                      }
                    />
                    <div className="card-content">
                      <span className={`simulation-status ${getStatusClass(sim.status)}`}>{getStatusText(sim.status)}</span>
                      <h3>{sim.name}</h3>
                      <p className="simulation-description">{sim.description}</p>
                      <div className="simulation-meta">
                        <ThemeIcon
                          light="job_monitor_clock_white.png"
                          dark="job_monitor_clock_white.png"
                          alt=""
                          className="meta-icon"
                        />
                        <span>{sim.date}</span>
                      </div>
                      {sim.status === 'completed' && (
                        <div className="main-results">
                          <h4>{language === 'pt' ? 'resultados principais' : 'main results'}</h4>
                          <p>
                            <strong>{language === 'pt' ? 'queda de pressão' : 'pressure drop'}:</strong> {sim.mainResults.pressure}
                          </p>
                          <p>
                            <strong>{language === 'pt' ? 'eficiência' : 'efficiency'}:</strong> {sim.mainResults.efficiency}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default ComparisonPage;
