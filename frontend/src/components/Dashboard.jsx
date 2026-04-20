import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useTheme } from '../context/ThemeContext';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import './Dashboard.css';
import { getDashboardSummary } from '../services/api';
import { useActiveUser } from '../context/UserContext';

function formatDurationSeconds(sec) {
  if (typeof sec !== 'number' || Number.isNaN(sec) || sec < 0) return '—';
  const total = Math.floor(sec);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m`;
  return `${s}s`;
}

function Dashboard() {
  const { language, t } = useLanguage();
  const { theme } = useTheme();
  const { activeUserId } = useActiveUser();
  const [dashboardData, setDashboardData] = useState({
    totalSimulations: 0,
    totalModels3D: 0,
    completedSimulations: 0,
    runningSimulations: 0,
    failedSimulations: 0,
    pendingSimulations: 0,
    successRate: 0,
    averageExecutionTime: null,
    averagePressureDrop: null,
    averageReynoldsNumber: null,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(null);

  const filteredSimulations = simulations.filter((sim) => {
    const matchesSearch =
      sim.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(sim.id).includes(searchTerm);
    const matchesFilter = activeFilter === 'all' || sim.status === activeFilter;
    return matchesSearch && matchesFilter;
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="completed" className="status-icon" />;
      case 'running':
        return <ThemeIcon light="runLight.png" dark="runDark.png" alt="running" className="status-icon" />;
      case 'pending':
        return <ThemeIcon light="refreshLight.png" dark="refreshDark.png" alt="pending" className="status-icon" />;
      case 'failed':
        return <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="failed" className="status-icon" />;
      default:
        return null;
    }
  };

  const getStatusText = (status) => {
    const statusMap = {
      completed: language === 'pt' ? 'concluída' : 'completed',
      running: language === 'pt' ? 'executando' : 'running',
      pending: language === 'pt' ? 'pendente' : 'pending',
      failed: language === 'pt' ? 'falhou' : 'failed'
    };
    return statusMap[status] || status;
  };

  const getStatusClass = (status) => {
    return `simulation-status ${status}`;
  };

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setConnectionError(null);
      const summary = await getDashboardSummary(8);

      setDashboardData({
        totalSimulations: summary.total_simulations || 0,
        totalModels3D: summary.total_models_3d || 0,
        completedSimulations: summary.by_status?.completed || 0,
        runningSimulations: summary.by_status?.running || 0,
        failedSimulations: summary.by_status?.failed || 0,
        pendingSimulations: summary.by_status?.pending || 0,
        successRate: summary.success_rate || 0,
        averageExecutionTime: summary.average_execution_time,
        averagePressureDrop: summary.average_pressure_drop,
        averageReynoldsNumber: summary.average_reynolds_number,
      });

      const recentItems = Array.isArray(summary?.recent_simulations) ? summary.recent_simulations : [];
      setSimulations(
        recentItems.map((sim) => ({
          id: sim.id,
          name: sim.name,
          status: sim.status,
          date: sim.created_at
            ? new Date(sim.created_at).toLocaleString(language === 'pt' ? 'pt-BR' : 'en-US')
            : '—',
          duration: formatDurationSeconds(sim.execution_time),
          bedId: sim.bed_id,
        }))
      );
    } catch (error) {
      console.error('erro ao carregar dados do dashboard:', error);
      setConnectionError(t('backendConnectionError'));
      setSimulations([]);
    } finally {
      setLoading(false);
    }
  }, [language, t]);

  useEffect(() => {
    loadData();
    const timer = window.setInterval(loadData, 5000);
    return () => window.clearInterval(timer);
  }, [activeUserId, loadData]);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>{language === 'pt' ? 'dashboard' : 'dashboard'}</h1>
        <p>{language === 'pt' ? 'dados reais vindos do fastapi e persistidos no sqlite' : 'real data from fastapi persisted in sqlite'}</p>
      </div>

      {connectionError && <BackendConnectionError message={connectionError} />}

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="total simulations" className="card-icon" />
          </div>
          <div className="metric-content">
            <div className="metric-value">{dashboardData.totalSimulations}</div>
            <div className="metric-label">{language === 'pt' ? 'total de simulações' : 'total simulations'}</div>
            <div className="metric-subtitle">{dashboardData.completedSimulations} {language === 'pt' ? 'concluídas' : 'completed'}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon success">
            <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="models" className="card-icon" />
          </div>
          <div className="metric-content">
            <div className="metric-value">{dashboardData.totalModels3D}</div>
            <div className="metric-label">{language === 'pt' ? 'modelos 3d' : '3d models'}</div>
            <div className="metric-subtitle">{language === 'pt' ? 'persistidos no sqlite' : 'persisted in sqlite'}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon warning">
            <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="success rate" className="card-icon" />
          </div>
          <div className="metric-content">
            <div className="metric-value">{dashboardData.successRate.toFixed(1)}%</div>
            <div className="metric-label">{language === 'pt' ? 'taxa de sucesso' : 'success rate'}</div>
            <div className="metric-subtitle">{dashboardData.completedSimulations}/{dashboardData.totalSimulations}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon error">
            <ThemeIcon light="runLight.png" dark="runDark.png" alt="running" className="card-icon" />
          </div>
          <div className="metric-content">
            <div className="metric-value">{dashboardData.runningSimulations}</div>
            <div className="metric-label">{language === 'pt' ? 'em execução' : 'running'}</div>
            <div className="metric-subtitle">{dashboardData.pendingSimulations} {language === 'pt' ? 'pendentes' : 'pending'}</div>
          </div>
        </div>
      </div>

      <div className="resources-grid">
        <div className="resource-card">
          <div className="resource-icon">
            <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="average time" className="card-icon" />
          </div>
          <div className="resource-content">
            <div className="resource-value">{formatDurationSeconds(dashboardData.averageExecutionTime)}</div>
            <div className="resource-label">{language === 'pt' ? 'tempo médio' : 'average time'}</div>
            <div className="resource-subtitle">{language === 'pt' ? 'simulações concluídas' : 'completed simulations'}</div>
          </div>
        </div>

        <div className="resource-card">
          <div className="resource-icon">
            <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="pressure" className="card-icon" />
          </div>
          <div className="resource-content">
            <div className="resource-value">
              {dashboardData.averagePressureDrop != null ? dashboardData.averagePressureDrop.toFixed(2) : '—'}
            </div>
            <div className="resource-label">{language === 'pt' ? 'queda média de pressão' : 'average pressure drop'}</div>
            <div className="resource-subtitle">pa</div>
          </div>
        </div>

        <div className="resource-card">
          <div className="resource-icon success">
            <ThemeIcon light="database-01-svgrepo-com.svg" dark="database-01-svgrepo-com.svg" alt="reynolds" className="card-icon db-memory-icon" />
          </div>
          <div className="resource-content">
            <div className="resource-value">
              {dashboardData.averageReynoldsNumber != null ? dashboardData.averageReynoldsNumber.toFixed(2) : '—'}
            </div>
            <div className="resource-label">{language === 'pt' ? 'reynolds médio' : 'average reynolds'}</div>
            <div className="resource-subtitle">{language === 'pt' ? 'dados reais' : 'real data'}</div>
          </div>
        </div>

        <div className="resource-card">
          <div className="resource-icon error">
            <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="failed" className="card-icon" />
          </div>
          <div className="resource-content">
            <div className="resource-value">{dashboardData.failedSimulations}</div>
            <div className="resource-label">{language === 'pt' ? 'falhas' : 'failures'}</div>
            <div className="resource-subtitle">{language === 'pt' ? 'sincronizadas do backend' : 'synced from backend'}</div>
          </div>
        </div>
      </div>

      <div className="simulation-controls">
        <div className="search-section">
          <input
            type="text"
            placeholder={language === 'pt' ? 'buscar simulações...' : 'search simulations...'}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-section">
          <button
            className={`filter-btn ${activeFilter === 'all' ? 'active' : ''}`}
            onClick={() => setActiveFilter('all')}
          >
            {language === 'pt' ? 'todas' : 'all'} ({simulations.length})
          </button>
          <button
            className={`filter-btn ${activeFilter === 'completed' ? 'active' : ''}`}
            onClick={() => setActiveFilter('completed')}
          >
            <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="completed" className="filter-icon" />
            {language === 'pt' ? 'concluídas' : 'completed'} ({simulations.filter((s) => s.status === 'completed').length})
          </button>
          <button
            className={`filter-btn ${activeFilter === 'running' ? 'active' : ''}`}
            onClick={() => setActiveFilter('running')}
          >
            <ThemeIcon light="runLight.png" dark="runDark.png" alt="running" className="filter-icon" />
            {language === 'pt' ? 'executando' : 'running'} ({simulations.filter((s) => s.status === 'running').length})
          </button>
          <button
            className={`filter-btn ${activeFilter === 'pending' ? 'active' : ''}`}
            onClick={() => setActiveFilter('pending')}
          >
            <ThemeIcon light="refreshLight.png" dark="refreshDark.png" alt="pending" className="filter-icon" />
            {language === 'pt' ? 'pendentes' : 'pending'} ({simulations.filter((s) => s.status === 'pending').length})
          </button>
          <button
            className={`filter-btn ${activeFilter === 'failed' ? 'active' : ''}`}
            onClick={() => setActiveFilter('failed')}
          >
            <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="failed" className="filter-icon" />
            {language === 'pt' ? 'falharam' : 'failed'} ({simulations.filter((s) => s.status === 'failed').length})
          </button>
        </div>
      </div>

      <div className="simulations-list">
        <h3>{language === 'pt' ? 'simulações recentes' : 'recent simulations'}</h3>
        <div className="simulations-grid">
          {loading && <p>{language === 'pt' ? 'carregando...' : 'loading...'}</p>}
          {!loading && filteredSimulations.length === 0 && (
            <p>{language === 'pt' ? 'nenhuma simulação recente encontrada' : 'no recent simulations found'}</p>
          )}
          {filteredSimulations.map((simulation) => (
            <div key={simulation.id} className="simulation-card">
              <div className="simulation-header">
                <div className="simulation-name">{simulation.name}</div>
                <div className={getStatusClass(simulation.status)}>
                  {getStatusIcon(simulation.status)}
                  {getStatusText(simulation.status)}
                </div>
              </div>
              <div className="simulation-date">id {simulation.id}</div>
              <div className="simulation-date">{simulation.date}</div>
              <div className="simulation-date">bed #{simulation.bedId}</div>
              <div className="simulation-date">{language === 'pt' ? 'duração' : 'duration'}: {simulation.duration}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
