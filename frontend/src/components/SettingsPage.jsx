import { useCallback, useEffect, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useTheme } from '../context/ThemeContext';
import { useAppUi } from '../context/AppUiContext';
import { getSettings, patchSettings, postAdminDevShutdown, getApiBase } from '../services/api';
import BackendConnectionError from './BackendConnectionError';
import './SettingsPage.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function apiBaseUrl() {
  return String(getApiBase()).replace(/\/$/, '');
}

/**
 * @param {{ navigateTab: (tab: string) => void, onLogout?: () => void }} props
 */
export default function SettingsPage({ navigateTab, onLogout }) {
  const { language, t, setLanguage } = useLanguage();
  const { setThemeMode } = useTheme();
  const { applySettingsFromApi, setSimpleMode, setDevMode } = useAppUi();
  const pt = language === 'pt';

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);
  const [devMsg, setDevMsg] = useState('');

  const [themeMode, setThemeModeLocal] = useState('system');
  const [lang, setLangLocal] = useState('pt');
  const [jobsPollSec, setJobsPollSec] = useState(5);
  const [advancedHints, setAdvancedHints] = useState(false);
  const [simpleModeDraft, setSimpleModeDraft] = useState(false);
  const [devModeDraft, setDevModeDraft] = useState(false);

  const [dbNotes, setDbNotes] = useState('');
  const [clientTimeoutSec, setClientTimeoutSec] = useState(30);

  const [ofSolver, setOfSolver] = useState('simpleFoam');
  const [ofMaxIter, setOfMaxIter] = useState(1000);
  const [ofTurb, setOfTurb] = useState('kEpsilon');
  const [ofConv, setOfConv] = useState(1e-6);

  const [modelingProfile, setModelingProfile] = useState('blender');
  const [modelingNotes, setModelingNotes] = useState('');
  const [cfdOtherNotes, setCfdOtherNotes] = useState('');

  const [updatedAt, setUpdatedAt] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const s = await getSettings();
      const tm = s.theme_mode === 'dark' || s.theme_mode === 'light' || s.theme_mode === 'system'
        ? s.theme_mode
        : 'system';
      setThemeModeLocal(tm);
      setThemeMode(tm);
      const lg = s.language === 'en' ? 'en' : 'pt';
      setLangLocal(lg);
      setLanguage(lg);
      const j = Number(s.jobs_poll_interval_sec);
      setJobsPollSec(Number.isFinite(j) && j >= 3 && j <= 120 ? j : 5);
      setAdvancedHints(!!s.show_advanced_hints);
      setSimpleModeDraft(!!s.simple_mode);
      setDevModeDraft(!!s.dev_mode);
      setDbNotes(s.database_ui?.notes ?? '');
      const ct = Number(s.database_ui?.client_timeout_sec);
      setClientTimeoutSec(Number.isFinite(ct) && ct >= 5 && ct <= 600 ? ct : 30);
      setOfSolver(s.openfoam_defaults?.solver ?? 'simpleFoam');
      const mi = Number(s.openfoam_defaults?.max_iterations);
      setOfMaxIter(Number.isFinite(mi) && mi >= 1 ? mi : 1000);
      setOfTurb(s.openfoam_defaults?.turbulence_model ?? 'kEpsilon');
      const cv = Number(s.openfoam_defaults?.convergence);
      setOfConv(Number.isFinite(cv) && cv > 0 ? cv : 1e-6);
      setModelingProfile(s.modeling?.profile === 'python' ? 'python' : 'blender');
      setModelingNotes(s.modeling?.notes ?? '');
      setCfdOtherNotes(s.cfd_other?.notes ?? '');
      setUpdatedAt(s.updated_at || '');
      applySettingsFromApi(s);
      localStorage.setItem(
        'jobsPollIntervalSec',
        String(Number.isFinite(j) && j >= 3 && j <= 120 ? j : 5)
      );
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'não foi possível carregar as configurações' : 'could not load settings')
        );
      }
    } finally {
      setLoading(false);
    }
  }, [applySettingsFromApi, pt, setLanguage, setThemeMode, t]);

  useEffect(() => {
    load();
  }, [load]);

  const onThemeChange = (value) => {
    setThemeModeLocal(value);
    setThemeMode(value);
  };

  const onLangChange = (value) => {
    setLangLocal(value);
    setLanguage(value);
  };

  const handleSave = async () => {
    setSaving(true);
    setOpError(null);
    setConnectionError(null);
    try {
      const s = await patchSettings({
        theme_mode: themeMode,
        language: lang,
        jobs_poll_interval_sec: jobsPollSec,
        show_advanced_hints: advancedHints,
        simple_mode: simpleModeDraft,
        dev_mode: devModeDraft,
        database_ui: {
          notes: dbNotes,
          client_timeout_sec: clientTimeoutSec,
        },
        openfoam_defaults: {
          solver: ofSolver,
          max_iterations: ofMaxIter,
          turbulence_model: ofTurb,
          convergence: ofConv,
        },
        modeling: {
          profile: modelingProfile,
          notes: modelingNotes,
        },
        cfd_other: {
          notes: cfdOtherNotes,
        },
      });
      setUpdatedAt(s.updated_at || '');
      localStorage.setItem('jobsPollIntervalSec', String(jobsPollSec));
      applySettingsFromApi(s);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'falha ao guardar' : 'save failed')
        );
      }
    } finally {
      setSaving(false);
    }
  };

  const openSwagger = () => {
    window.open(`${apiBaseUrl()}/docs`, '_blank', 'noopener,noreferrer');
  };

  const tryQuitFrontend = () => {
    window.close();
    setDevMsg(
      pt
        ? 'se o separador não fechar, foi aberto manualmente: feche-o à mão ou use atalho do navegador.'
        : 'if the tab did not close, it was opened manually: close it yourself or use a browser shortcut.'
    );
  };

  const shutdownBackend = async () => {
    setDevMsg('');
    try {
      await postAdminDevShutdown();
      setDevMsg(
        pt
          ? 'pedido de encerramento enviado. o backend deve parar em breve; reinicie uvicorn ou o container manualmente.'
          : 'shutdown request sent. the backend should stop shortly; restart uvicorn or your container manually.'
      );
    } catch (err) {
      const detail = err.response?.data?.detail;
      setDevMsg(
        typeof detail === 'string'
          ? detail
          : pt
            ? 'falha ao encerrar (confirme ALLOW_DEV_SHUTDOWN=1 no servidor).'
            : 'shutdown failed (set ALLOW_DEV_SHUTDOWN=1 on the server).'
      );
    }
  };

  const handleLogout = () => {
    if (typeof onLogout === 'function') {
      onLogout();
    }
  };

  return (
    <div className="tab-content">
      <div className="settings-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="settings-op-error" role="alert">
            {opError}
          </div>
        )}

        {devMsg && (
          <div className="settings-dev-msg" role="status">
            {devMsg}
          </div>
        )}

        <div className="settings-page-layout">
          <div className="settings-main">
            <h2 className="settings-title">{t('systemSettings')}</h2>
            <p className="settings-lead">
              {pt
                ? 'preferências na tabela app_settings (singleton). idioma sincroniza com user_profiles. opções extra ficam em options_json.'
                : 'preferences in app_settings (singleton). language syncs to user_profiles. extra options live in options_json.'}
            </p>
            {updatedAt && (
              <p className="settings-meta">
                {pt ? 'última atualização na base:' : 'last saved:'}{' '}
                {new Date(updatedAt).toLocaleString(pt ? 'pt-BR' : 'en-GB')}
              </p>
            )}

            {loading ? (
              <p className="settings-status">{pt ? 'a carregar…' : 'loading…'}</p>
            ) : (
              <>
                <div className="settings-grid">
                  <section className="setting-card">
                    <h3>{t('theme')}</h3>
                    <p className="setting-card-desc">{t('themeDesc')}</p>
                    <label className="settings-control">
                      <span>{pt ? 'modo' : 'mode'}</span>
                      <select
                        value={themeMode}
                        onChange={(e) => onThemeChange(e.target.value)}
                        aria-label={t('theme')}
                      >
                        <option value="light">{pt ? 'claro' : 'light'}</option>
                        <option value="dark">{pt ? 'escuro' : 'dark'}</option>
                        <option value="system">{pt ? 'sistema' : 'system'}</option>
                      </select>
                    </label>
                  </section>

                  <section className="setting-card">
                    <h3>{t('language')}</h3>
                    <p className="setting-card-desc">{t('languageDesc')}</p>
                    <label className="settings-control">
                      <span>{pt ? 'idioma da interface' : 'interface language'}</span>
                      <select
                        value={lang}
                        onChange={(e) => onLangChange(e.target.value)}
                        aria-label={t('language')}
                      >
                        <option value="pt">português (brasil)</option>
                        <option value="en">english</option>
                      </select>
                    </label>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'modo simples e modo dev' : 'simple mode and dev mode'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'modo simples reduz o menu lateral às áreas principais do fluxo cfd. modo dev mostra, em cada página, referências de api e persistência.'
                        : 'simple mode trims the sidebar to core cfd areas. dev mode shows api and persistence hints on every page.'}
                    </p>
                    <label className="settings-check">
                      <input
                        type="checkbox"
                        checked={simpleModeDraft}
                        onChange={(e) => {
                          const v = e.target.checked;
                          setSimpleModeDraft(v);
                          setSimpleMode(v);
                        }}
                      />
                      <span>{pt ? 'modo simples (menu reduzido)' : 'simple mode (reduced menu)'}</span>
                    </label>
                    <label className="settings-check">
                      <input
                        type="checkbox"
                        checked={devModeDraft}
                        onChange={(e) => {
                          const v = e.target.checked;
                          setDevModeDraft(v);
                          setDevMode(v);
                        }}
                      />
                      <span>{pt ? 'modo dev (painel por página)' : 'dev mode (per-page panel)'}</span>
                    </label>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'banco de dados (interface)' : 'database (ui)'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'notas e tempo limite do cliente http (axios) para pedidos ao backend. não altera a url da base no servidor.'
                        : 'notes and axios client timeout for backend requests. does not change the server database url.'}
                    </p>
                    <label className="settings-control settings-control-stack">
                      <span>{pt ? 'notas / checklist' : 'notes / checklist'}</span>
                      <textarea
                        className="settings-textarea"
                        rows={3}
                        value={dbNotes}
                        onChange={(e) => setDbNotes(e.target.value)}
                        placeholder={pt ? 'ex.: usar postgresql em produção; backup diário…' : 'e.g. use postgresql in prod; daily backup…'}
                      />
                    </label>
                    <label className="settings-control">
                      <span>{pt ? 'timeout cliente (s)' : 'client timeout (s)'}</span>
                      <input
                        type="number"
                        min={5}
                        max={600}
                        value={clientTimeoutSec}
                        onChange={(e) => setClientTimeoutSec(Number(e.target.value))}
                      />
                    </label>
                    <button
                      type="button"
                      className="settings-link-btn"
                      onClick={() => navigateTab('database')}
                    >
                      {pt ? 'abrir painel banco de dados' : 'open database panel'}
                    </button>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'parâmetros padrão openfoam' : 'default openfoam parameters'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'referência para formulários e futuros templates de caso; o motor openfoam continua a ser configurado nos ficheiros do caso.'
                        : 'reference for forms and future case templates; the openfoam engine is still driven by case files.'}
                    </p>
                    <div className="settings-inline-grid">
                      <label className="settings-control">
                        <span>solver</span>
                        <input
                          type="text"
                          value={ofSolver}
                          onChange={(e) => setOfSolver(e.target.value)}
                        />
                      </label>
                      <label className="settings-control">
                        <span>{pt ? 'iterações máx.' : 'max iterations'}</span>
                        <input
                          type="number"
                          min={1}
                          max={100000}
                          value={ofMaxIter}
                          onChange={(e) => setOfMaxIter(Number(e.target.value))}
                        />
                      </label>
                      <label className="settings-control">
                        <span>{pt ? 'turbulência' : 'turbulence'}</span>
                        <input
                          type="text"
                          value={ofTurb}
                          onChange={(e) => setOfTurb(e.target.value)}
                        />
                      </label>
                      <label className="settings-control">
                        <span>{pt ? 'convergência' : 'convergence'}</span>
                        <input
                          type="number"
                          step="any"
                          min={1e-12}
                          value={ofConv}
                          onChange={(e) => setOfConv(Number(e.target.value))}
                        />
                      </label>
                    </div>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'modelagem 3d' : '3d modeling'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'o pipeline suporta geração via blender e caminhos python/stl; escolha o perfil preferido para a equipa.'
                        : 'the pipeline supports blender generation and python/stl paths; pick the preferred profile for your team.'}
                    </p>
                    <label className="settings-control">
                      <span>{pt ? 'perfil' : 'profile'}</span>
                      <select
                        value={modelingProfile}
                        onChange={(e) => setModelingProfile(e.target.value)}
                      >
                        <option value="blender">blender</option>
                        <option value="python">python / stl</option>
                      </select>
                    </label>
                    <label className="settings-control settings-control-stack">
                      <span>{pt ? 'notas' : 'notes'}</span>
                      <textarea
                        className="settings-textarea"
                        rows={2}
                        value={modelingNotes}
                        onChange={(e) => setModelingNotes(e.target.value)}
                        placeholder={pt ? 'caminhos, scripts, versão do blender…' : 'paths, scripts, blender version…'}
                      />
                    </label>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'outros softwares cfd' : 'other cfd software'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'campo livre para ansys, fluent, su2, etc. (apenas documentação na interface).'
                        : 'free text for ansys, fluent, su2, etc. (documentation in the ui only).'}
                    </p>
                    <textarea
                      className="settings-textarea"
                      rows={3}
                      value={cfdOtherNotes}
                      onChange={(e) => setCfdOtherNotes(e.target.value)}
                    />
                  </section>

                  <section className="setting-card">
                    <h3>{t('simulations')}</h3>
                    <p className="setting-card-desc">{t('simulationsDesc')}</p>
                    <label className="settings-control">
                      <span>
                        {pt
                          ? 'intervalo de atualização dos jobs (s)'
                          : 'jobs list refresh interval (s)'}
                      </span>
                      <input
                        type="number"
                        min={3}
                        max={120}
                        value={jobsPollSec}
                        onChange={(e) => setJobsPollSec(Number(e.target.value))}
                      />
                    </label>
                    <p className="setting-card-hint settings-hint-small">
                      {pt
                        ? 'afeta a página «jobs» (recarregue a aba para aplicar o novo intervalo).'
                        : 'affects the «jobs» page (reload that tab to apply the new interval).'}
                    </p>
                    <button
                      type="button"
                      className="settings-link-btn"
                      onClick={() => navigateTab('jobs')}
                    >
                      {pt ? 'abrir jobs' : 'open jobs'}
                    </button>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'avançado' : 'advanced'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'dicas técnicas adicionais nas áreas de simulação e pipeline (reservado para extensões futuras da ui).'
                        : 'extra technical hints in simulation and pipeline areas (reserved for future ui extensions).'}
                    </p>
                    <label className="settings-check">
                      <input
                        type="checkbox"
                        checked={advancedHints}
                        onChange={(e) => setAdvancedHints(e.target.checked)}
                      />
                      <span>{pt ? 'ativar dicas avançadas' : 'enable advanced hints'}</span>
                    </label>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'sessão' : 'session'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'sem login real: limpa preferências locais e repõe idioma/tema padrão.'
                        : 'no real login: clears local preferences and resets default language/theme.'}
                    </p>
                    <button type="button" className="settings-danger-btn" onClick={handleLogout}>
                      {pt ? 'sair / deslogar' : 'log out'}
                    </button>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'desenvolvimento e serviço' : 'development and service'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'swagger abre num novo separador. encerrar o backend requer ALLOW_DEV_SHUTDOWN=1. o navegador não fecha abas abertas pelo utilizador por segurança.'
                        : 'swagger opens in a new tab. backend shutdown needs ALLOW_DEV_SHUTDOWN=1. browsers block closing user-opened tabs.'}
                    </p>
                    <div className="settings-btn-row">
                      <button type="button" className="settings-link-btn" onClick={openSwagger}>
                        swagger /docs
                      </button>
                      <button type="button" className="settings-link-btn" onClick={shutdownBackend}>
                        {pt ? 'encerrar backend' : 'shutdown backend'}
                      </button>
                      <button type="button" className="settings-link-btn" onClick={tryQuitFrontend}>
                        {pt ? 'tentar fechar este separador' : 'try to close this tab'}
                      </button>
                    </div>
                    <p className="setting-card-hint settings-hint-small">
                      {pt
                        ? '«reiniciar» backend = encerrar processo e voltar a correr uvicorn ou docker compose up manualmente.'
                        : '«restart» backend = stop the process and run uvicorn or docker compose up again manually.'}
                    </p>
                  </section>
                </div>

                <div className="settings-footer-actions">
                  <button type="button" className="settings-save-btn" onClick={handleSave} disabled={saving}>
                    {saving ? (pt ? 'a guardar…' : 'saving…') : pt ? 'guardar configurações' : 'save settings'}
                  </button>
                  <button type="button" className="settings-reload-btn" onClick={() => load()} disabled={loading}>
                    {pt ? 'recarregar da base' : 'reload from database'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
