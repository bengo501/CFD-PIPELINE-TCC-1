import { useCallback, useEffect, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { getDatabasePanel, postDatabasePanelEvent } from '../services/api';
import BackendConnectionError from './BackendConnectionError';
import './DatabasePage.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function eventLabel(type, pt) {
  if (type === 'backup_request') return pt ? 'pedido de backup' : 'backup request';
  if (type === 'connection_test') return pt ? 'teste de ligação' : 'connection test';
  return type;
}

/**
 * painel banco de dados: contagens reais (sqlalchemy) e registo de eventos em admin_panel_events.
 */
export default function DatabasePage() {
  const { language, t } = useLanguage();
  const pt = language === 'pt';

  const [panel, setPanel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const loadPanel = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const data = await getDatabasePanel();
      setPanel(data);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
        setPanel(null);
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'não foi possível carregar o painel' : 'could not load panel')
        );
      }
    } finally {
      setLoading(false);
    }
  }, [pt, t]);

  useEffect(() => {
    loadPanel();
  }, [loadPanel]);

  const runAction = async (eventType) => {
    setActionLoading(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await postDatabasePanelEvent(eventType);
      await loadPanel();
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else
        setOpError(
          err.response?.data?.detail || (pt ? 'ação falhou' : 'action failed')
        );
    } finally {
      setActionLoading(false);
    }
  };

  const counts = panel?.counts;
  const rows =
    counts != null
      ? [
          [
            pt ? 'leitos (tabela beds)' : 'beds table',
            String(counts.beds),
            pt ? 'registos' : 'rows',
          ],
          [
            pt ? 'simulações (simulations)' : 'simulations',
            String(counts.simulations),
            pt ? 'registos' : 'rows',
          ],
          [
            pt ? 'resultados (results)' : 'results',
            String(counts.results),
            pt ? 'registos' : 'rows',
          ],
          [
            pt ? 'templates .bed (bed_templates)' : 'bed templates',
            String(counts.bed_templates),
            pt ? 'registos' : 'rows',
          ],
        ]
      : [];

  const integ = panel?.integrations || {};
  const integRows = [
    [
      pt ? 'redis (filas / cache)' : 'redis (queues / cache)',
      integ.redis || '—',
      pt ? 'estado' : 'status',
    ],
    [
      pt ? 'armazenamento de objetos (s3 / minio)' : 'object storage (s3 / minio)',
      integ.object_storage || '—',
      pt ? 'estado' : 'status',
    ],
  ];

  return (
    <div className="tab-content">
      <div className="database-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="database-op-error" role="alert">
            {opError}
          </div>
        )}

        <div className="database-layout">
          <section
            className="database-mockup-card"
            aria-label={pt ? 'painel do motor sql' : 'sql engine panel'}
          >
            <h2>{pt ? 'banco de dados' : 'database'}</h2>
            <p className="database-mockup-lead">
              {pt
                ? 'visão operacional do sqlite/postgresql usado pela api: contagens das tabelas principais e histórico de pedidos feitos a partir desta página.'
                : 'operational view of the sqlite/postgresql used by the api: main table counts and history of requests made from this page.'}
            </p>

            {loading ? (
              <p className="database-status">{pt ? 'a carregar…' : 'loading…'}</p>
            ) : panel ? (
              <>
                <div
                  className={`database-connection-banner ${panel.connected ? 'ok' : 'bad'}`}
                  role="status"
                >
                  <span className="database-connection-label">
                    {pt ? 'motor sql' : 'sql engine'}
                  </span>
                  <span className="database-connection-value">{panel.database_display}</span>
                  <span className="database-connection-badge">
                    {panel.connected
                      ? pt
                        ? 'ligado'
                        : 'connected'
                      : pt
                        ? 'indisponível'
                        : 'unavailable'}
                  </span>
                  {panel.checked_at && (
                    <span className="database-checked-at">
                      {pt ? 'verificado:' : 'checked:'}{' '}
                      {new Date(panel.checked_at).toLocaleString(pt ? 'pt-PT' : 'en-GB')}
                    </span>
                  )}
                </div>
                {panel.error && (
                  <p className="database-panel-error" role="alert">
                    {panel.error}
                  </p>
                )}

                <h3 className="database-subheading">
                  {pt ? 'dados persistidos (orm)' : 'persisted data (orm)'}
                </h3>
                <ul className="database-mock-list">
                  {rows.map(([title, value, kind]) => (
                    <li key={title}>
                      <span>{title}</span>
                      <span>
                        {value} · {kind}
                      </span>
                    </li>
                  ))}
                </ul>

                <h3 className="database-subheading">
                  {pt ? 'integrações externas' : 'external integrations'}
                </h3>
                <ul className="database-mock-list database-mock-list-muted">
                  {integRows.map(([title, value, kind]) => (
                    <li key={title}>
                      <span>{title}</span>
                      <span>
                        {value} · {kind}
                      </span>
                    </li>
                  ))}
                </ul>

                <h3 className="database-subheading">
                  {pt ? 'registo de ações (admin_panel_events)' : 'action log (admin_panel_events)'}
                </h3>
                {panel.recent_events?.length ? (
                  <ul className="database-events-list">
                    {panel.recent_events.map((ev) => (
                      <li key={ev.id}>
                        <span className="database-events-type">{eventLabel(ev.event_type, pt)}</span>
                        <time dateTime={ev.created_at}>
                          {ev.created_at
                            ? new Date(ev.created_at).toLocaleString(pt ? 'pt-PT' : 'en-GB')
                            : '—'}
                        </time>
                        {ev.detail && (
                          <span className="database-events-detail">{ev.detail}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="database-events-empty">
                    {pt
                      ? 'ainda não há eventos. use os botões abaixo para registar pedidos.'
                      : 'no events yet. use the buttons below to log requests.'}
                  </p>
                )}

                <div className="database-actions-mock">
                  <button
                    type="button"
                    onClick={() => loadPanel()}
                    disabled={loading || actionLoading}
                  >
                    {pt ? 'atualizar' : 'refresh'}
                  </button>
                  <button
                    type="button"
                    onClick={() => runAction('connection_test')}
                    disabled={actionLoading || !!connectionError}
                  >
                    {pt ? 'testar ligação' : 'test connection'}
                  </button>
                  <button
                    type="button"
                    onClick={() => runAction('backup_request')}
                    disabled={actionLoading || !!connectionError}
                  >
                    {pt ? 'pedir backup manual' : 'request manual backup'}
                  </button>
                </div>
                <p className="database-actions-hint">
                  {pt
                    ? 'o backup manual apenas regista o pedido na base de dados; a cópia física (pg_dump, ficheiro sqlite, etc.) deve ser feita à parte nos seus scripts de operação.'
                    : 'manual backup only logs the request in the database; physical backup (pg_dump, sqlite file copy, etc.) must be done separately in your ops scripts.'}
                </p>
              </>
            ) : null}
          </section>
        </div>
      </div>
    </div>
  );
}
