import { useCallback, useEffect, useRef, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import {
  listTemplates,
  saveTemplate,
  deleteTemplate,
  duplicateTemplate,
} from '../services/api';
import BackendConnectionError from './BackendConnectionError';
import PaginationControls from './PaginationControls';
import './SavedTemplatesPage.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function sourceLabel(source, pt) {
  const s = (source || 'editor').toLowerCase();
  if (s === 'import') return pt ? 'importação' : 'import';
  if (s === 'duplicate') return pt ? 'duplicado' : 'duplicate';
  return pt ? 'editor' : 'editor';
}

function formatUpdatedLine(iso, pt) {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    const now = Date.now();
    const sec = Math.round((now - d.getTime()) / 1000);
    const rtf = new Intl.RelativeTimeFormat(pt ? 'pt' : 'en', { numeric: 'auto' });
    if (Math.abs(sec) < 60) return rtf.format(-sec, 'second');
    const min = Math.round(sec / 60);
    if (Math.abs(min) < 60) return rtf.format(-min, 'minute');
    const h = Math.round(min / 60);
    if (Math.abs(h) < 48) return rtf.format(-h, 'hour');
    const days = Math.round(h / 24);
    if (Math.abs(days) < 14) return rtf.format(-days, 'day');
    return d.toLocaleDateString(pt ? 'pt-PT' : 'en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

/**
 * biblioteca de templates .bed persistidos no banco (api /api/templates/*).
 */
export default function SavedTemplatesPage() {
  const { language, t } = useLanguage();
  const pt = language === 'pt';
  const fileRef = useRef(null);

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(8);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    search: '',
    tag: '',
    source: '',
  });
  const [selectedId, setSelectedId] = useState(null);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const data = await listTemplates({
        page,
        limit,
        search: filters.search,
        tag: filters.tag || null,
        source: filters.source || null,
      });
      setItems(Array.isArray(data?.items) ? data.items : []);
      setTotal(data?.total || 0);
      setTotalPages(data?.total_pages || data?.pages || 1);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
        setItems([]);
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'não foi possível carregar os templates' : 'could not load templates')
        );
        setItems([]);
        setTotal(0);
      }
    } finally {
      setLoading(false);
    }
  }, [filters, limit, page, pt, t]);

  useEffect(() => {
    loadTemplates();
  }, [loadTemplates]);

  const toggleSelect = (id) => {
    setSelectedId((prev) => (prev === id ? null : id));
    setOpError(null);
  };

  const handleDuplicate = async () => {
    if (!selectedId) return;
    setOpError(null);
    setConnectionError(null);
    try {
      await duplicateTemplate(selectedId);
      await loadTemplates();
      setSelectedId(null);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else
        setOpError(
          err.response?.data?.detail ||
            (pt ? 'falha ao duplicar' : 'duplicate failed')
        );
    }
  };

  const handleDelete = async () => {
    if (!selectedId) return;
    const ok = window.confirm(
      pt ? 'eliminar este template da base de dados?' : 'delete this template from the database?'
    );
    if (!ok) return;
    setOpError(null);
    setConnectionError(null);
    try {
      await deleteTemplate(selectedId);
      setSelectedId(null);
      await loadTemplates();
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else
        setOpError(
          err.response?.data?.detail || (pt ? 'falha ao eliminar' : 'delete failed')
        );
    }
  };

  const handleImportClick = () => {
    fileRef.current?.click();
  };

  const handleImportFile = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async () => {
      const content = typeof reader.result === 'string' ? reader.result : '';
      const defaultName = file.name.replace(/\.bed$/i, '') || file.name || 'importado';
      const nameInput = window.prompt(
        pt ? 'nome do template na biblioteca:' : 'template name in library:',
        defaultName
      );
      if (!nameInput || !nameInput.trim()) return;

      setOpError(null);
      setConnectionError(null);
      try {
        await saveTemplate({
          name: nameInput.trim(),
          content,
          tag: 'bed',
          source: 'import',
        });
        await loadTemplates();
      } catch (err) {
        console.error(err);
        if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
        else
          setOpError(
            err.response?.data?.detail || (pt ? 'falha ao importar' : 'import failed')
          );
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="tab-content">
      <div className="saved-templates-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="saved-templates-op-error" role="alert">
            {opError}
          </div>
        )}

        <div className="saved-templates-layout">
          <section
            className="saved-templates-mockup-card"
            aria-label={pt ? 'biblioteca de templates' : 'template library'}
          >
            <h2>{pt ? 'templates salvos' : 'saved templates'}</h2>
            <p className="saved-templates-lead">
              {pt
                ? 'presets .bed guardados na base de dados do backend. criar ou editar conteúdo continua disponível no separador editor de templates.'
                : '.bed presets stored in the backend database. create or edit content in the template editor tab.'}
            </p>

            <div className="saved-templates-toolbar">
              <input
                type="search"
                value={filters.search}
                onChange={(e) => {
                  setPage(1);
                  setFilters((prev) => ({ ...prev, search: e.target.value }));
                }}
                placeholder={pt ? 'pesquisar por nome ou etiqueta…' : 'search by name or tag…'}
                aria-label={pt ? 'pesquisar templates' : 'search templates'}
              />
              <select
                className="saved-templates-select"
                value={filters.tag}
                onChange={(e) => {
                  setPage(1);
                  setFilters((prev) => ({ ...prev, tag: e.target.value }));
                }}
              >
                <option value="">{pt ? 'todas as etiquetas' : 'all tags'}</option>
                <option value="bed">bed</option>
                <option value="preset">preset</option>
                <option value="cfd">cfd</option>
              </select>
              <select
                className="saved-templates-select"
                value={filters.source}
                onChange={(e) => {
                  setPage(1);
                  setFilters((prev) => ({ ...prev, source: e.target.value }));
                }}
              >
                <option value="">{pt ? 'todas as origens' : 'all sources'}</option>
                <option value="editor">{pt ? 'editor' : 'editor'}</option>
                <option value="import">{pt ? 'importação' : 'import'}</option>
                <option value="duplicate">{pt ? 'duplicado' : 'duplicate'}</option>
              </select>
              <button
                type="button"
                className="saved-templates-refresh"
                onClick={() => loadTemplates()}
                disabled={loading}
              >
                {pt ? 'atualizar' : 'refresh'}
              </button>
              <button
                type="button"
                className="saved-templates-refresh"
                onClick={() => {
                  setPage(1);
                  setFilters({ search: '', tag: '', source: '' });
                }}
                disabled={loading}
              >
                {pt ? 'limpar filtros' : 'clear filters'}
              </button>
            </div>

            {loading ? (
              <p className="saved-templates-status">{pt ? 'a carregar…' : 'loading…'}</p>
            ) : items.length === 0 ? (
              <p className="saved-templates-status">
                {total === 0
                  ? pt
                    ? 'nenhum template na biblioteca. importe um .bed ou guarde a partir do editor.'
                    : 'no templates yet. import a .bed or save from the editor.'
                  : pt
                    ? 'nenhum resultado para a pesquisa.'
                    : 'no matches for your search.'}
              </p>
            ) : (
              <div className="saved-templates-grid">
                {items.map((row) => {
                  const meta = pt
                    ? `atualizado ${formatUpdatedLine(row.updated_at, true)} · origem: ${sourceLabel(row.source, true)}`
                    : `updated ${formatUpdatedLine(row.updated_at, false)} · source: ${sourceLabel(row.source, false)}`;
                  return (
                    <article
                      key={row.id}
                      className={`saved-templates-card ${selectedId === row.id ? 'selected' : ''}`}
                    >
                      <button
                        type="button"
                        className="saved-templates-card-hit"
                        onClick={() => toggleSelect(row.id)}
                        aria-pressed={selectedId === row.id}
                      >
                        <span className="saved-templates-card-title">{row.name}</span>
                        <span className="saved-templates-card-tag">{row.tag || 'bed'}</span>
                        <span className="saved-templates-card-meta">{meta}</span>
                      </button>
                    </article>
                  );
                })}
              </div>
            )}

            <PaginationControls
              page={page}
              totalPages={totalPages}
              total={total}
              limit={limit}
              loading={loading}
              onPageChange={setPage}
              onLimitChange={(value) => {
                setPage(1);
                setLimit(value);
              }}
              label={pt ? 'templates .bed' : '.bed templates'}
              pt={pt}
            />

            <input
              ref={fileRef}
              type="file"
              accept=".bed,text/plain"
              className="saved-templates-file-input"
              aria-hidden
              tabIndex={-1}
              onChange={handleImportFile}
            />

            <div className="saved-templates-actions">
              <button type="button" onClick={handleImportClick}>
                {pt ? 'importar ficheiro' : 'import file'}
              </button>
              <button type="button" disabled={!selectedId} onClick={handleDuplicate}>
                {pt ? 'duplicar selecionado' : 'duplicate selected'}
              </button>
              <button type="button" disabled={!selectedId} onClick={handleDelete}>
                {pt ? 'eliminar' : 'delete'}
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
