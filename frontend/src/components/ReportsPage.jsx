import { useLanguage } from '../context/LanguageContext';
import './ReportsPage.css';

/**
 * mockup breve de relatórios; ícone wip indica desenvolvimento em curso.
 */
export default function ReportsPage() {
  const { language } = useLanguage();
  const pt = language === 'pt';

  const rows = pt
    ? [
        ['sumário executivo — leito referência', 'rascunho'],
        ['tabela de métricas (re, δp, porosidade)', 'rascunho'],
        ['anexos: gráficos e malha', 'planeado'],
      ]
    : [
        ['executive summary — reference bed', 'draft'],
        ['metrics table (re, δp, porosity)', 'draft'],
        ['appendix: charts and mesh', 'planned'],
      ];

  return (
    <div className="tab-content">
      <div className="reports-page">
        <div className="reports-layout">
          <section className="reports-mockup-card" aria-label={pt ? 'pré-visualização de relatórios' : 'reports preview'}>
            <h2>{pt ? 'relatórios' : 'reports'}</h2>
            <p className="reports-mockup-lead">
              {pt
                ? 'estrutura prevista para exportação (pdf / zip). ainda sem ligação aos dados reais.'
                : 'planned structure for export (pdf / zip). not wired to live data yet.'}
            </p>
            <ul className="reports-mock-list">
              {rows.map(([title, status]) => (
                <li key={title}>
                  <span>{title}</span>
                  <span>{status}</span>
                </li>
              ))}
            </ul>
            <div className="reports-actions-mock">
              <button type="button" disabled>
                {pt ? 'pré-visualizar pdf' : 'preview pdf'}
              </button>
              <button type="button" disabled>
                {pt ? 'exportar pacote' : 'export bundle'}
              </button>
            </div>
          </section>

          <aside className="reports-wip-panel" aria-label={pt ? 'estado da funcionalidade' : 'feature status'}>
            <div className="reports-wip-badge">{pt ? 'em construção' : 'work in progress'}</div>
            <img
              src="/image/wip-reports.png"
              alt={pt ? 'ícone: funcionalidade em desenvolvimento' : 'work in progress indicator'}
              className="reports-wip-icon"
            />
            <p className="reports-wip-note">
              {pt
                ? 'esta secção será ligada ao pipeline de resultados numa iteração futura.'
                : 'this section will connect to the results pipeline in a future iteration.'}
            </p>
          </aside>
        </div>
      </div>
    </div>
  );
}
