import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useTheme } from '../context/ThemeContext';
import ThemeIcon from './ThemeIcon';
import './ComparisonPage.css';

function ComparisonPage() {
  const { language } = useLanguage();
  const { isDarkMode } = useTheme();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('concluídas');
  const [selectedSimulations, setSelectedSimulations] = useState([]);
  const [simulations, setSimulations] = useState([]);

  // dados mock para demonstração
  const mockSimulations = [
    {
      id: 1,
      name: 'Simulação Leito Empacotado 1',
      description: 'Simulação de leito empacotado com configuração padrão',
      status: 'concluída',
      date: '14/01/2024',
      mainResults: {
        pressure: '1250 Pa',
        efficiency: '85.0%'
      }
    },
    {
      id: 2,
      name: 'Simulação Leito Empacotado 2',
      description: 'Simulação com diferentes parâmetros de porosidade',
      status: 'concluída',
      date: '09/01/2024',
      mainResults: {
        pressure: '1450 Pa',
        efficiency: '78.0%'
      }
    },
    {
      id: 3,
      name: 'Simulação Leito Empacotado 3',
      description: 'Simulação com maior velocidade de entrada',
      status: 'concluída',
      date: '19/01/2024',
      mainResults: {
        pressure: '1800 Pa',
        efficiency: '72.0%'
      }
    },
    {
      id: 4,
      name: 'Simulação Leito Empacotado 4',
      description: 'Simulação com partículas de diâmetro variado',
      status: 'em execução',
      date: '20/01/2024',
      mainResults: {
        pressure: 'N/A',
        efficiency: 'N/A'
      }
    },
    {
      id: 5,
      name: 'Simulação Leito Empacotado 5',
      description: 'Teste de nova geometria de leito',
      status: 'pendente',
      date: '21/01/2024',
      mainResults: {
        pressure: 'N/A',
        efficiency: 'N/A'
      }
    },
    {
      id: 6,
      name: 'Simulação Leito Empacotado 6',
      description: 'Simulação com erro de convergência',
      status: 'falhou',
      date: '22/01/2024',
      mainResults: {
        pressure: 'N/A',
        efficiency: 'N/A'
      }
    }
  ];

  useEffect(() => {
    setSimulations(mockSimulations);
  }, []);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleFilterChange = (filter) => {
    setActiveFilter(filter);
  };

  const handleSimulationSelect = (id) => {
    setSelectedSimulations((prevSelected) => {
      if (prevSelected.includes(id)) {
        return prevSelected.filter((simId) => simId !== id);
      } else {
        if (prevSelected.length < 2) {
          return [...prevSelected, id];
        }
        return prevSelected; // máximo 2 simulações
      }
    });
  };

  const filteredSimulations = simulations.filter((sim) => {
    const matchesSearch = sim.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         sim.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = activeFilter === 'todas' || sim.status === activeFilter;
    return matchesSearch && matchesFilter;
  });

  const getStatusText = (status) => {
    switch (status) {
      case 'concluída':
        return language === 'pt' ? 'CONCLUÍDA' : 'COMPLETED';
      case 'em execução':
        return language === 'pt' ? 'EM EXECUÇÃO' : 'RUNNING';
      case 'pendente':
        return language === 'pt' ? 'PENDENTE' : 'PENDING';
      case 'falhou':
        return language === 'pt' ? 'FALHOU' : 'FAILED';
      default:
        return status;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'concluída':
        return 'status-completed';
      case 'em execução':
        return 'status-running';
      case 'pendente':
        return 'status-pending';
      case 'falhou':
        return 'status-failed';
      default:
        return '';
    }
  };

  const getFilterCount = (filter) => {
    if (filter === 'todas') return simulations.length;
    return simulations.filter(sim => sim.status === filter).length;
  };

  return (
    <div className="comparison-page">
      <div className="comparison-header">
        <div className="comparison-title">
          <ThemeIcon light="compareLight.png" dark="compareDark.png" alt="comparisons" className="title-icon" />
          <h1>{language === 'pt' ? 'Comparações' : 'Comparisons'}</h1>
        </div>
        <p className="comparison-description">
          {language === 'pt' ? 'Compare simulações lado a lado e analise diferenças' : 'Compare simulations side by side and analyze differences'}
        </p>
      </div>

      <div className="selection-section">
        <h2>{language === 'pt' ? 'Selecionar Simulações para Comparar' : 'Select Simulations to Compare'}</h2>
        <p className="selection-instruction">
          {language === 'pt' ? 'Selecione exatamente duas simulações concluídas' : 'Select exactly two completed simulations'}
        </p>

        <div className="comparison-controls">
          <div className="search-bar">
            <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="search" className="search-icon" />
            <input
              type="text"
              placeholder={language === 'pt' ? 'Buscar simulações...' : 'Search simulations...'}
              value={searchTerm}
              onChange={handleSearchChange}
            />
          </div>
          <div className="filter-dropdown">
            <button className="filter-btn">
              <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="filter" className="filter-icon" />
              {language === 'pt' ? 'Concluídas' : 'Completed'}
              <span className="dropdown-arrow">▼</span>
            </button>
          </div>
        </div>

        <div className="simulation-cards-grid">
          {filteredSimulations.map((sim) => (
            <div
              key={sim.id}
              className={`simulation-card ${selectedSimulations.includes(sim.id) ? 'selected' : ''} ${sim.status === 'concluída' ? '' : 'disabled'}`}
              onClick={() => sim.status === 'concluída' && handleSimulationSelect(sim.id)}
            >
              <input
                type="checkbox"
                checked={selectedSimulations.includes(sim.id)}
                onChange={() => sim.status === 'concluída' && handleSimulationSelect(sim.id)}
                disabled={sim.status !== 'concluída' || (selectedSimulations.length === 2 && !selectedSimulations.includes(sim.id))}
              />
              <div className="card-content">
                <span className={`simulation-status ${getStatusClass(sim.status)}`}>
                  {getStatusText(sim.status)}
                </span>
                <h3>{sim.name}</h3>
                <p className="simulation-description">{sim.description}</p>
                <div className="simulation-meta">
                  <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="date" className="meta-icon" />
                  <span>{sim.date}</span>
                </div>
                {sim.status === 'concluída' && (
                  <div className="main-results">
                    <h4>{language === 'pt' ? 'Resultados Principais:' : 'Main Results:'}</h4>
                    <p><strong>{language === 'pt' ? 'Pressão:' : 'Pressure:'}</strong> {sim.mainResults.pressure}</p>
                    <p><strong>{language === 'pt' ? 'Eficiência:' : 'Efficiency:'}</strong> {sim.mainResults.efficiency}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ComparisonPage;
