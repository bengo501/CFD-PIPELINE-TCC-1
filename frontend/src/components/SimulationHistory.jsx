import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useTheme } from '../context/ThemeContext';
import ThemeIcon from './ThemeIcon';
import './SimulationHistory.css';

function SimulationHistory() {
  const { language } = useLanguage();
  const { isDarkMode } = useTheme();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [simulations, setSimulations] = useState([]);

  // dados mock para demonstração
  const mockSimulations = [
    {
      id: 1,
      name: 'Simulação CFD - Leito Empacotado 1',
      description: 'Análise de fluxo de fluido em leito empacotado com esferas de 5mm',
      status: 'completed',
      createdDate: '15/01/2024, 07:30',
      duration: '4h 15m',
      type: 'CFD'
    },
    {
      id: 2,
      name: 'Simulação CFD - Transferência de Calor',
      description: 'Estudo de transferência de calor em leito com partículas de 3mm',
      status: 'running',
      createdDate: '16/01/2024, 06:15',
      duration: '2h 30m',
      type: 'CFD'
    },
    {
      id: 3,
      name: 'Análise de Fluxo - Esferas 2mm',
      description: 'Simulação de fluxo em leito com partículas menores',
      status: 'pending',
      createdDate: '17/01/2024, 14:20',
      duration: '0h 0m',
      type: 'CFD'
    },
    {
      id: 4,
      name: 'Teste de Permeabilidade',
      description: 'Análise de permeabilidade em diferentes configurações',
      status: 'failed',
      createdDate: '18/01/2024, 09:45',
      duration: '1h 15m',
      type: 'CFD'
    }
  ];

  useEffect(() => {
    setSimulations(mockSimulations);
  }, []);

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
        return language === 'pt' ? 'Concluída' : 'Completed';
      case 'running':
        return language === 'pt' ? 'Em Execução' : 'Running';
      case 'pending':
        return language === 'pt' ? 'Pendente' : 'Pending';
      case 'failed':
        return language === 'pt' ? 'Falhou' : 'Failed';
      default:
        return status;
    }
  };

  const filteredSimulations = simulations.filter(sim => {
    const matchesSearch = sim.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         sim.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         sim.id.toString().includes(searchTerm);
    
    const matchesFilter = activeFilter === 'all' || sim.status === activeFilter;
    
    return matchesSearch && matchesFilter;
  });

  const getFilterCount = (filter) => {
    if (filter === 'all') return simulations.length;
    return simulations.filter(sim => sim.status === filter).length;
  };

  const handleViewSimulation = (id) => {
    console.log('Visualizar simulação:', id);
  };

  const handleDownloadResults = (id) => {
    console.log('Baixar resultados:', id);
  };

  const handleDeleteSimulation = (id) => {
    console.log('Deletar simulação:', id);
  };

  const handleRerunSimulation = (id) => {
    console.log('Reexecutar simulação:', id);
  };

  return (
    <div className="simulation-history">
      <div className="history-header">
        <div className="history-title">
          <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="histórico" className="title-icon" />
          <h1>{language === 'pt' ? 'Histórico de Simulações' : 'Simulation History'}</h1>
        </div>
        <p className="history-description">
          {language === 'pt' ? 'Visualize e gerencie todas as suas simulações CFD' : 'Visualize and manage all your CFD simulations'}
        </p>
      </div>

      <div className="history-controls">
        <button className="refresh-btn">
          <ThemeIcon light="refreshLigh.png" dark="refreshDark.png" alt="atualizar" className="refresh-icon" />
          {language === 'pt' ? 'Atualizar' : 'Refresh'}
        </button>

        <div className="search-container">
          <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="buscar" className="search-icon" />
          <input
            type="text"
            placeholder={language === 'pt' ? 'Buscar por nome, descrição ou ID...' : 'Search by name, description or ID...'}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="filter-tabs">
        <button 
          className={`filter-tab ${activeFilter === 'all' ? 'active' : ''}`}
          onClick={() => setActiveFilter('all')}
        >
          {language === 'pt' ? 'Todas' : 'All'} ({getFilterCount('all')})
        </button>
        <button 
          className={`filter-tab ${activeFilter === 'completed' ? 'active' : ''}`}
          onClick={() => setActiveFilter('completed')}
        >
          <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="concluídas" className="filter-icon" />
          {language === 'pt' ? 'Concluídas' : 'Completed'} ({getFilterCount('completed')})
        </button>
        <button 
          className={`filter-tab ${activeFilter === 'running' ? 'active' : ''}`}
          onClick={() => setActiveFilter('running')}
        >
          <ThemeIcon light="runLight.png" dark="runDark.png" alt="executando" className="filter-icon" />
          {language === 'pt' ? 'Em Execução' : 'Running'} ({getFilterCount('running')})
        </button>
        <button 
          className={`filter-tab ${activeFilter === 'pending' ? 'active' : ''}`}
          onClick={() => setActiveFilter('pending')}
        >
          <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="pendentes" className="filter-icon" />
          {language === 'pt' ? 'Pendentes' : 'Pending'} ({getFilterCount('pending')})
        </button>
        <button 
          className={`filter-tab ${activeFilter === 'failed' ? 'active' : ''}`}
          onClick={() => setActiveFilter('failed')}
        >
          <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="falharam" className="filter-icon" />
          {language === 'pt' ? 'Falharam' : 'Failed'} ({getFilterCount('failed')})
        </button>
      </div>

      <div className="simulations-list">
        {filteredSimulations.map((simulation) => (
          <div key={simulation.id} className="simulation-card">
            <div className="simulation-status">
              {getStatusIcon(simulation.status)}
              <span className="status-text">{getStatusText(simulation.status)}</span>
            </div>
            
            <div className="simulation-info">
              <div className="simulation-header">
                <h3 className="simulation-name">{simulation.name}</h3>
                <span className="simulation-id">ID: {simulation.id}</span>
              </div>
              <p className="simulation-description">{simulation.description}</p>
              <div className="simulation-meta">
                <span className="simulation-date">{simulation.createdDate}</span>
                <span className="simulation-duration">{simulation.duration}</span>
              </div>
            </div>

            <div className="simulation-actions">
              <button 
                className="action-btn view-btn"
                onClick={() => handleViewSimulation(simulation.id)}
                title={language === 'pt' ? 'Visualizar' : 'View'}
              >
                <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="visualizar" className="action-icon" />
              </button>
              <button 
                className="action-btn download-btn"
                onClick={() => handleDownloadResults(simulation.id)}
                title={language === 'pt' ? 'Baixar' : 'Download'}
              >
                <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="baixar" className="action-icon" />
              </button>
              <button 
                className="action-btn delete-btn"
                onClick={() => handleDeleteSimulation(simulation.id)}
                title={language === 'pt' ? 'Deletar' : 'Delete'}
              >
                <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="deletar" className="action-icon" />
              </button>
              <button 
                className="action-btn rerun-btn"
                onClick={() => handleRerunSimulation(simulation.id)}
                title={language === 'pt' ? 'Reexecutar' : 'Rerun'}
              >
                <ThemeIcon light="runLight.png" dark="runDark.png" alt="reexecutar" className="action-icon" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SimulationHistory;
