import { useCallback, useEffect, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import {
  listReports,
  getReport,
  createReport,
  updateReport,
  deleteReport,
  reportsCatalog,
  reportsResultsForSimulation,
  addReportAttachment,
  removeReportAttachment,
} from '../services/api';
import BackendConnectionError from './BackendConnectionError';
import './ReportsPage.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function statusLabel(status, pt) {
  const m = {
    draft: pt ? 'rascunho' : 'draft',
    planned: pt ? 'planeado' : 'planned',
    published: pt ? 'publicado' : 'published',
  };
  return m[status] || status;
}

function kindLabel(kind, pt) {
  const m = {
    simulation: pt ? 'simulação' : 'simulation',
    template: pt ? 'template .bed' : '.bed template',
    result: pt ? 'resultado' : 'result',
    data_note: pt ? 'dados / nota' : 'data note',
  };
  return m[kind] || kind;
}

/**
 * relatórios persistidos (reports + report_attachments); modal para editar e anexar entidades.
 */
export default function ReportsPage() {
  const { language, t } = useLanguage();
  const pt = language === 'pt';

  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [activeReportId, setActiveReportId] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detail, setDetail] = useState(null);
  const [localTitle, setLocalTitle] = useState('');
  const [localBody, setLocalBody] = useState('');
  const [localStatus, setLocalStatus] = useState('draft');
  const [saving, setSaving] = useState(false);

  const [catalog, setCatalog] = useState(null);
  const [addSimId, setAddSimId] = useState('');
  const [addTmplId, setAddTmplId] = useState('');
  const [pickSimForResult, setPickSimForResult] = useState('');
  const [resultRows, setResultRows] = useState([]);
  const [addResultId, setAddResultId] = useState('');
  const [dataNoteText, setDataNoteText] = useState('');
  const [attBusy, setAttBusy] = useState(false);

  const loadReports = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const data = await listReports();
      setReports(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
        setReports([]);
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'falha ao carregar relatórios' : 'failed to load reports')
        );
      }
    } finally {
      setLoading(false);
    }
  }, [pt, t]);

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  const closeModal = useCallback(() => {
    setModalOpen(false);
    setActiveReportId(null);
    setDetail(null);
    setAddSimId('');
    setAddTmplId('');
    setPickSimForResult('');
    setResultRows([]);
    setAddResultId('');
    setDataNoteText('');
  }, []);

  useEffect(() => {
    if (!modalOpen) return;
    const onKey = (e) => {
      if (e.key === 'Escape') closeModal();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [modalOpen, closeModal]);

  const loadCatalog = useCallback(async () => {
    if (catalog) return;
    try {
      setConnectionError(null);
      const c = await reportsCatalog();
      setCatalog(c);
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setCatalog({ simulations: [], templates: [] });
    }
  }, [catalog, t]);

  const openReport = async (id) => {
    setActiveReportId(id);
    setModalOpen(true);
    setDetail(null);
    setDetailLoading(true);
    setOpError(null);
    setConnectionError(null);
    await loadCatalog();
    try {
      const d = await getReport(id);
      setDetail(d);
      setLocalTitle(d.title);
      setLocalBody(d.body || '');
      setLocalStatus(d.status || 'draft');
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || err.message);
      closeModal();
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCreate = async () => {
    setOpError(null);
    setConnectionError(null);
    try {
      const created = await createReport({
        title: pt ? 'novo relatório' : 'new report',
        body: '',
        status: 'draft',
      });
      await loadReports();
      await openReport(created.id);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'não foi possível criar' : 'create failed'));
    }
  };

  const saveFields = async () => {
    if (!activeReportId) return;
    setSaving(true);
    setOpError(null);
    setConnectionError(null);
    try {
      const d = await updateReport(activeReportId, {
        title: localTitle,
        body: localBody,
        status: localStatus,
      });
      setDetail(d);
      await loadReports();
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao guardar' : 'save failed'));
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteReport = async () => {
    if (!activeReportId) return;
    const ok = window.confirm(
      pt ? 'eliminar este relatório e todos os anexos?' : 'delete this report and all attachments?'
    );
    if (!ok) return;
    setConnectionError(null);
    setOpError(null);
    try {
      await deleteReport(activeReportId);
      closeModal();
      await loadReports();
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao eliminar' : 'delete failed'));
    }
  };

  const refreshDetail = async () => {
    if (!activeReportId) return;
    try {
      const d = await getReport(activeReportId);
      setDetail(d);
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
    }
  };

  useEffect(() => {
    if (!pickSimForResult) {
      setResultRows([]);
      setAddResultId('');
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const rows = await reportsResultsForSimulation(Number(pickSimForResult));
        if (!cancelled) setResultRows(Array.isArray(rows) ? rows : []);
      } catch {
        if (!cancelled) setResultRows([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [pickSimForResult]);

  const attachSimulation = async () => {
    if (!activeReportId || !addSimId) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await addReportAttachment(activeReportId, {
        kind: 'simulation',
        ref_id: String(addSimId),
      });
      setAddSimId('');
      await refreshDetail();
      await loadReports();
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha no anexo' : 'attach failed'));
    } finally {
      setAttBusy(false);
    }
  };

  const attachTemplate = async () => {
    if (!activeReportId || !addTmplId) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await addReportAttachment(activeReportId, {
        kind: 'template',
        ref_id: addTmplId,
      });
      setAddTmplId('');
      await refreshDetail();
      await loadReports();
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha no anexo' : 'attach failed'));
    } finally {
      setAttBusy(false);
    }
  };

  const attachResult = async () => {
    if (!activeReportId || !addResultId) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await addReportAttachment(activeReportId, {
        kind: 'result',
        ref_id: String(addResultId),
      });
      setAddResultId('');
      await refreshDetail();
      await loadReports();
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha no anexo' : 'attach failed'));
    } finally {
      setAttBusy(false);
    }
  };

  const attachDataNote = async () => {
    if (!activeReportId || !dataNoteText.trim()) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await addReportAttachment(activeReportId, {
        kind: 'data_note',
        note: dataNoteText.trim(),
      });
      setDataNoteText('');
      await refreshDetail();
      await loadReports();
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha no anexo' : 'attach failed'));
    } finally {
      setAttBusy(false);
    }
  };

  const detach = async (attachmentId) => {
    if (!activeReportId) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await removeReportAttachment(activeReportId, attachmentId);
      await refreshDetail();
      await loadReports();
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao remover' : 'remove failed'));
    } finally {
      setAttBusy(false);
    }
  };

  return (
    <div className="tab-content">
      <div className="reports-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="reports-op-error" role="alert">
            {opError}
          </div>
        )}

        <div className="reports-layout">
          <section className="reports-mockup-card" aria-label={pt ? 'relatórios' : 'reports'}>
            <div className="reports-card-header">
              <h2>{pt ? 'relatórios' : 'reports'}</h2>
              <button type="button" className="reports-btn-primary" onClick={handleCreate}>
                {pt ? 'criar relatório' : 'create report'}
              </button>
            </div>
            <p className="reports-mockup-lead">
              {pt
                ? 'documentos técnicos guardados na base de dados. clique num relatório para editar o texto e associar simulações, templates, resultados ou notas de dados.'
                : 'technical documents stored in the database. click a report to edit text and link simulations, templates, results, or data notes.'}
            </p>

            <div className="reports-toolbar">
              <button type="button" onClick={() => loadReports()} disabled={loading}>
                {pt ? 'atualizar lista' : 'refresh list'}
              </button>
            </div>

            {loading ? (
              <p className="reports-status">{pt ? 'a carregar…' : 'loading…'}</p>
            ) : reports.length === 0 ? (
              <p className="reports-status">
                {pt
                  ? 'nenhum relatório. use «criar relatório» para começar.'
                  : 'no reports yet. use «create report» to start.'}
              </p>
            ) : (
              <ul className="reports-mock-list reports-mock-list-clickable">
                {reports.map((row) => (
                  <li key={row.id}>
                    <button
                      type="button"
                      className="reports-row-hit"
                      onClick={() => openReport(row.id)}
                    >
                      <span className="reports-row-title">{row.title}</span>
                      <span className={`reports-status-pill status-${row.status}`}>
                        {statusLabel(row.status, pt)}
                      </span>
                      <span className="reports-row-meta">
                        {row.attachment_count ?? 0}{' '}
                        {pt ? 'anexos' : 'attachments'} ·{' '}
                        {row.updated_at
                          ? new Date(row.updated_at).toLocaleString(pt ? 'pt-PT' : 'en-GB')
                          : '—'}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}

            <div className="reports-actions-mock">
              <button type="button" disabled title={pt ? 'em breve' : 'coming soon'}>
                {pt ? 'pré-visualizar pdf' : 'preview pdf'}
              </button>
              <button type="button" disabled title={pt ? 'em breve' : 'coming soon'}>
                {pt ? 'exportar pacote' : 'export bundle'}
              </button>
            </div>
          </section>
        </div>

        {modalOpen && (
          <div
            className="reports-modal-overlay"
            role="presentation"
            onClick={(e) => {
              if (e.target === e.currentTarget) closeModal();
            }}
          >
            <div
              className="reports-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="reports-modal-title"
            >
              <div className="reports-modal-header">
                <h2 id="reports-modal-title">{pt ? 'editar relatório' : 'edit report'}</h2>
                <button type="button" className="reports-modal-close" onClick={closeModal}>
                  ×
                </button>
              </div>

              {detailLoading ? (
                <p className="reports-modal-loading">{pt ? 'a carregar…' : 'loading…'}</p>
              ) : detail ? (
                <div className="reports-modal-body">
                  <label className="reports-field">
                    <span>{pt ? 'título' : 'title'}</span>
                    <input
                      type="text"
                      value={localTitle}
                      onChange={(e) => setLocalTitle(e.target.value)}
                      maxLength={500}
                    />
                  </label>
                  <label className="reports-field">
                    <span>{pt ? 'estado' : 'status'}</span>
                    <select
                      value={localStatus}
                      onChange={(e) => setLocalStatus(e.target.value)}
                    >
                      <option value="draft">{statusLabel('draft', pt)}</option>
                      <option value="planned">{statusLabel('planned', pt)}</option>
                      <option value="published">{statusLabel('published', pt)}</option>
                    </select>
                  </label>
                  <label className="reports-field reports-field-grow">
                    <span>{pt ? 'conteúdo' : 'body'}</span>
                    <textarea
                      value={localBody}
                      onChange={(e) => setLocalBody(e.target.value)}
                      rows={12}
                      placeholder={
                        pt
                          ? 'sumário, método, conclusões, referências…'
                          : 'summary, method, conclusions, references…'
                      }
                    />
                  </label>

                  <div className="reports-modal-actions">
                    <button type="button" onClick={saveFields} disabled={saving}>
                      {saving ? (pt ? 'a guardar…' : 'saving…') : pt ? 'guardar texto' : 'save text'}
                    </button>
                    <button
                      type="button"
                      className="reports-btn-danger"
                      onClick={handleDeleteReport}
                    >
                      {pt ? 'eliminar relatório' : 'delete report'}
                    </button>
                  </div>

                  <h3 className="reports-attach-heading">{pt ? 'anexos' : 'attachments'}</h3>
                  <ul className="reports-attach-list">
                    {detail.attachments?.length ? (
                      detail.attachments.map((a) => (
                        <li key={a.id}>
                          <div className="reports-attach-top">
                            <div className="reports-attach-main">
                              <span className="reports-attach-kind">{kindLabel(a.kind, pt)}</span>
                              <span className="reports-attach-ref">{a.display_ref}</span>
                            </div>
                            <button
                              type="button"
                              className="reports-attach-remove"
                              onClick={() => detach(a.id)}
                              disabled={attBusy}
                            >
                              {pt ? 'remover' : 'remove'}
                            </button>
                          </div>
                          {a.note && a.kind !== 'data_note' && (
                            <span className="reports-attach-note">{a.note}</span>
                          )}
                          {a.kind === 'data_note' && a.note && (
                            <pre className="reports-attach-data">{a.note}</pre>
                          )}
                        </li>
                      ))
                    ) : (
                      <li className="reports-attach-empty">
                        {pt ? 'sem anexos.' : 'no attachments.'}
                      </li>
                    )}
                  </ul>

                  <div className="reports-attach-add">
                    <h4>{pt ? 'adicionar simulação' : 'add simulation'}</h4>
                    <div className="reports-attach-row">
                      <select
                        value={addSimId}
                        onChange={(e) => setAddSimId(e.target.value)}
                        aria-label={pt ? 'simulação' : 'simulation'}
                      >
                        <option value="">{pt ? '— escolher —' : '— choose —'}</option>
                        {(catalog?.simulations || []).map((s) => (
                          <option key={s.id} value={String(s.id)}>
                            #{s.id} · {s.name} ({s.status})
                          </option>
                        ))}
                      </select>
                      <button type="button" onClick={attachSimulation} disabled={attBusy || !addSimId}>
                        {pt ? 'anexar' : 'attach'}
                      </button>
                    </div>

                    <h4>{pt ? 'adicionar template .bed' : 'add .bed template'}</h4>
                    <div className="reports-attach-row">
                      <select
                        value={addTmplId}
                        onChange={(e) => setAddTmplId(e.target.value)}
                        aria-label={pt ? 'template' : 'template'}
                      >
                        <option value="">{pt ? '— escolher —' : '— choose —'}</option>
                        {(catalog?.templates || []).map((x) => (
                          <option key={x.id} value={x.id}>
                            {x.name} [{x.tag}]
                          </option>
                        ))}
                      </select>
                      <button type="button" onClick={attachTemplate} disabled={attBusy || !addTmplId}>
                        {pt ? 'anexar' : 'attach'}
                      </button>
                    </div>

                    <h4>{pt ? 'adicionar resultado (orm)' : 'add result (orm)'}</h4>
                    <div className="reports-attach-row reports-attach-stack">
                      <select
                        value={pickSimForResult}
                        onChange={(e) => setPickSimForResult(e.target.value)}
                        aria-label={pt ? 'simulação para resultados' : 'simulation for results'}
                      >
                        <option value="">{pt ? '— simulação —' : '— simulation —'}</option>
                        {(catalog?.simulations || []).map((s) => (
                          <option key={s.id} value={String(s.id)}>
                            #{s.id} · {s.name}
                          </option>
                        ))}
                      </select>
                      <select
                        value={addResultId}
                        onChange={(e) => setAddResultId(e.target.value)}
                        aria-label={pt ? 'resultado' : 'result'}
                      >
                        <option value="">{pt ? '— resultado —' : '— result —'}</option>
                        {resultRows.map((r) => (
                          <option key={r.id} value={String(r.id)}>
                            #{r.id} · {r.name} ({r.result_type})
                            {r.value != null ? ` = ${r.value}${r.unit ? ` ${r.unit}` : ''}` : ''}
                          </option>
                        ))}
                      </select>
                      <button type="button" onClick={attachResult} disabled={attBusy || !addResultId}>
                        {pt ? 'anexar' : 'attach'}
                      </button>
                    </div>

                    <h4>{pt ? 'nota / dados livres' : 'free-form data note'}</h4>
                    <div className="reports-attach-row reports-attach-stack">
                      <textarea
                        rows={4}
                        value={dataNoteText}
                        onChange={(e) => setDataNoteText(e.target.value)}
                        placeholder={
                          pt
                            ? 'cole métricas, tabelas, json, observações…'
                            : 'paste metrics, tables, json, notes…'
                        }
                      />
                      <button
                        type="button"
                        onClick={attachDataNote}
                        disabled={attBusy || !dataNoteText.trim()}
                      >
                        {pt ? 'anexar nota' : 'attach note'}
                      </button>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
