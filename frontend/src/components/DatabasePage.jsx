import { useLanguage } from '../context/LanguageContext';
import './DatabasePage.css';

/**
 * mockup da área de gestão de bases de dados; ícone wip indica desenvolvimento em curso.
 */
export default function DatabasePage() {
  const { language } = useLanguage();
  const pt = language === 'pt';

  const rows = pt
    ? [
        ['backup agendado (postgresql)', 'mock'],
        ['filas e cache (redis)', 'mock'],
        ['objetos e artefactos (s3 / minio)', 'planeado'],
        ['estatísticas de jobs e filas', 'planeado'],
      ]
    : [
        ['scheduled backup (postgresql)', 'mock'],
        ['queues and cache (redis)', 'mock'],
        ['objects and artifacts (s3 / minio)', 'planned'],
        ['job and queue statistics', 'planned'],
      ];

  return (
    <div className="tab-content">
      <div className="database-page">
        <div className="database-layout">
          <section
            className="database-mockup-card"
            aria-label={pt ? 'pré-visualização do painel de banco de dados' : 'database admin preview'}
          >
            <h2>{pt ? 'banco de dados' : 'database'}</h2>
            <p className="database-mockup-lead">
              {pt
                ? 'estrutura prevista para operações administrativas. ainda sem ligação ao backend ou ao motor sql.'
                : 'planned layout for admin operations. not wired to the backend or sql engine yet.'}
            </p>
            <ul className="database-mock-list">
              {rows.map(([title, status]) => (
                <li key={title}>
                  <span>{title}</span>
                  <span>{status}</span>
                </li>
              ))}
            </ul>
            <div className="database-actions-mock">
              <button type="button" disabled>
                {pt ? 'testar ligação' : 'test connection'}
              </button>
              <button type="button" disabled>
                {pt ? 'pedir backup manual' : 'request manual backup'}
              </button>
            </div>
          </section>

          <aside
            className="database-wip-panel"
            aria-label={pt ? 'estado da funcionalidade' : 'feature status'}
          >
            <div className="database-wip-badge">{pt ? 'em construção' : 'work in progress'}</div>
            <img
              src="/image/wip-database.png"
              alt={pt ? 'ícone: funcionalidade em desenvolvimento' : 'work in progress indicator'}
              className="database-wip-icon"
            />
            <p className="database-wip-note">
              {pt
                ? 'esta secção será ligada a postgresql, redis e armazenamento de objetos numa iteração futura.'
                : 'this section will connect to postgresql, redis, and object storage in a future iteration.'}
            </p>
          </aside>
        </div>
      </div>
    </div>
  );
}
