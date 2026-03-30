import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useTheme } from '../context/ThemeContext';
import ThemeIcon from './ThemeIcon';
import './Dashboard.css';
import { getSimulationsSummary, listRecentSimulations } from '../services/api';

function Dashboard() {
  const { language } = useLanguage();
  const { theme } = useTheme();
  const [dashboardData, setDashboardData] = useState({
    totalSimulations: 0,
    completedSimulations: 0,
    runningSimulations: 0,
    failedSimulations: 0,
    pendingSimulations: 0,
    successRate: 0,
    averageTime: 0,
    cpuUsage: 0,
    memoryUsage: 0,
    resourceLimit: 100,
    resourceUsed: 0
  });

  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [simulations, setSimulations] = useState([]);

  const filteredSimulations = simulations.filter(sim => {
    const matchesSearch = sim.name.toLowerCase().includes(searchTerm.toLowerCase());
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
      completed: language === 'pt' ? 'Concluída' : 'Completed',
      running: language === 'pt' ? 'Executando' : 'Running',
      pending: language === 'pt' ? 'Pendente' : 'Pending',
      failed: language === 'pt' ? 'Falhou' : 'Failed'
    };
    return statusMap[status] || status;
  };

  const getStatusClass = (status) => {
    return `simulation-status ${status}`;
  };

  useEffect(() => {
    const loadData = async () => {
      try {
        const summary = await getSimulationsSummary();
        const recent = await listRecentSimulations(8);

        setDashboardData(prev => ({
          ...prev,
          totalSimulations: summary.total || 0,
          completedSimulations: summary.by_status?.completed || 0,
          runningSimulations: summary.by_status?.running || 0,
          failedSimulations: summary.by_status?.failed || 0,
          pendingSimulations: summary.by_status?.pending || 0,
          successRate: summary.success_rate || 0,
          // por enquanto mantemos averageTime, cpuUsage, memoryUsage como mock/placeholder
        }));

        if (recent && Array.isArray(recent.items)) {
          // adaptar para o formato esperado pela UI (id, name, status, date)
          const mapped = recent.items.map(sim => ({
            id: sim.id,
            name: sim.name,
            status: sim.status,
            date: sim.created_at ? new Date(sim.created_at).toISOString().slice(0, 10) : '',
          }));
          setSimulations(mapped);
        }
      } catch (error) {
        console.error('erro ao carregar dados do dashboard:', error);
      }
    };

    loadData();
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>{language === 'pt' ? 'Dashboard' : 'Dashboard'}</h1>
        <p>{language === 'pt' ? 'Gerencie suas simulações CFD de leitos empacotados' : 'Manage your packed bed CFD simulations'}</p>
      </div>

      {/* métricas principais */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="total simulations" className="card-icon" />
          </div>
          <div className="metric-content">
            <div className="metric-value">{dashboardData.totalSimulations}</div>
            <div className="metric-label">{language === 'pt' ? 'Total de Simulações' : 'Total Simulations'}</div>
            <div className="metric-subtitle">{dashboardData.completedSimulations} {language === 'pt' ? 'concluídas' : 'completed'}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon success">
            <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="success rate" className="card-icon" />
          </div>
          <div className="metric-content">
            <div className="metric-value">{dashboardData.successRate}%</div>
            <div className="metric-label">{language === 'pt' ? 'Taxa de Sucesso' : 'Success Rate'}</div>
            <div className="metric-subtitle">{dashboardData.completedSimulations}/{dashboardData.totalSimulations}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon warning">
            <ThemeIcon light="runLight.png" dark="runDark.png" alt="running" className="card-icon" />
          </div>
          <div className="metric-content">
            <div className="metric-value">{dashboardData.runningSimulations}</div>
            <div className="metric-label">{language === 'pt' ? 'Em Execução' : 'In Execution'}</div>
            <div className="metric-subtitle">{dashboardData.pendingSimulations} {language === 'pt' ? 'pendentes' : 'pending'}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon error">
            <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="failures" className="card-icon" />
          </div>
          <div className="metric-content">
            <div className="metric-value">{dashboardData.failedSimulations}</div>
            <div className="metric-label">{language === 'pt' ? 'Falhas' : 'Failures'}</div>
            <div className="metric-subtitle">{dashboardData.successRate}%</div>
          </div>
        </div>
      </div>

      {/* métricas de recursos */}
      <div className="resources-grid">
        <div className="resource-card">
          <div className="resource-icon">
            <ThemeIcon light="create_bed_white.png" dark="image-removebg-preview(14).png" alt="available limit" className="card-icon" />
          </div>
          <div className="resource-content">
            <div className="resource-value">{dashboardData.resourceLimit}%</div>
            <div className="resource-label">{language === 'pt' ? 'Limite Disponível' : 'Available Limit'}</div>
            <div className="resource-subtitle">{dashboardData.resourceLimit} {language === 'pt' ? 'simulações restantes' : 'simulations remaining'}</div>
          </div>
        </div>

        <div className="resource-card">
          <div className="resource-icon">
            <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="average time" className="card-icon" />
          </div>
          <div className="resource-content">
            <div className="resource-value">{dashboardData.averageTime}s</div>
            <div className="resource-label">{language === 'pt' ? 'Tempo Médio' : 'Average Time'}</div>
            <div className="resource-subtitle">{language === 'pt' ? 'Por simulação' : 'Per simulation'}</div>
          </div>
        </div>

        <div className="resource-card">
          <div className="resource-icon success">
            <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="cpu usage" className="card-icon" />
          </div>
          <div className="resource-content">
            <div className="resource-value">{dashboardData.cpuUsage}%</div>
            <div className="resource-label">{language === 'pt' ? 'CPU em Uso' : 'CPU in Use'}</div>
            <div className="resource-subtitle">{dashboardData.runningSimulations} {language === 'pt' ? 'processos' : 'processes'}</div>
          </div>
        </div>

        <div className="resource-card">
          <div className="resource-icon">
            <ThemeIcon light="database-01-svgrepo-com.svg" dark="database-01-svgrepo-com.svg" alt="memory" className="card-icon db-memory-icon" />
          </div>
          <div className="resource-content">
            <div className="resource-value">{dashboardData.memoryUsage}GB</div>
            <div className="resource-label">{language === 'pt' ? 'Memória' : 'Memory'}</div>
            <div className="resource-subtitle">{language === 'pt' ? 'Total utilizado' : 'Total used'}</div>
          </div>
        </div>
      </div>

      {/* barra de uso de recursos */}
      <div className="resource-usage">
        <h3>{language === 'pt' ? 'Uso de Recursos' : 'Resource Usage'}</h3>
        <div className="usage-bar">
          <div className="usage-fill" style={{ width: `${dashboardData.resourceUsed}%` }}></div>
        </div>
        <div className="usage-text">
          {dashboardData.resourceUsed}% - {dashboardData.resourceUsed} {language === 'pt' ? 'de 100 simulações utilizadas' : 'of 100 simulations used'}
        </div>
      </div>

      {/* busca e filtros */}
      <div className="simulation-controls">
        <div className="search-section">
          <input
            type="text"
            placeholder={language === 'pt' ? 'Buscar simulações...' : 'Search simulations...'}
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
            {language === 'pt' ? 'Todas' : 'All'} ({simulations.length})
          </button>
          <button
            className={`filter-btn ${activeFilter === 'completed' ? 'active' : ''}`}
            onClick={() => setActiveFilter('completed')}
          >
            <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="completed" className="filter-icon" />
            {language === 'pt' ? 'Concluídas' : 'Completed'} ({simulations.filter(s => s.status === 'completed').length})
          </button>
          <button
            className={`filter-btn ${activeFilter === 'running' ? 'active' : ''}`}
            onClick={() => setActiveFilter('running')}
          >
            <ThemeIcon light="runLight.png" dark="runDark.png" alt="running" className="filter-icon" />
            {language === 'pt' ? 'Executando' : 'Running'} ({simulations.filter(s => s.status === 'running').length})
          </button>
          <button
            className={`filter-btn ${activeFilter === 'pending' ? 'active' : ''}`}
            onClick={() => setActiveFilter('pending')}
          >
            <ThemeIcon light="refreshLight.png" dark="refreshDark.png" alt="pending" className="filter-icon" />
            {language === 'pt' ? 'Pendentes' : 'Pending'} ({simulations.filter(s => s.status === 'pending').length})
          </button>
          <button
            className={`filter-btn ${activeFilter === 'failed' ? 'active' : ''}`}
            onClick={() => setActiveFilter('failed')}
          >
            <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="failed" className="filter-icon" />
            {language === 'pt' ? 'Falharam' : 'Failed'} ({simulations.filter(s => s.status === 'failed').length})
          </button>
        </div>
      </div>

      {/* lista de simulações */}
      <div className="simulations-list">
        <h3>{language === 'pt' ? 'Simulações' : 'Simulations'}</h3>
        <div className="simulations-grid">
          {filteredSimulations.map(simulation => (
            <div key={simulation.id} className="simulation-card">
              <div className="simulation-header">
                <div className="simulation-name">{simulation.name}</div>
                <div className={getStatusClass(simulation.status)}>
                  {getStatusIcon(simulation.status)}
                  {getStatusText(simulation.status)}
                </div>
              </div>
              <div className="simulation-date">{simulation.date}</div>
              <div className="simulation-actions">
                <button className="action-btn view">
                  <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="view" className="action-icon" />
                  {language === 'pt' ? 'Ver' : 'View'}
                </button>
                <button className="action-btn download">
                  <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="download" className="action-icon" />
                  {language === 'pt' ? 'Baixar' : 'Download'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
