import { useCallback, useEffect, useMemo, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { getProfile, patchProfile } from '../services/api';
import BackendConnectionError from './BackendConnectionError';
import './ProfilePage.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function initialsFromName(name) {
  const p = (name || '').trim().split(/\s+/).filter(Boolean);
  if (p.length >= 2) return (p[0][0] + p[1][0]).toUpperCase();
  if (p.length === 1 && p[0].length) return p[0].slice(0, 2).toUpperCase();
  return '?';
}

function roleLabel(role, pt) {
  const m = {
    researcher: pt ? 'pesquisador' : 'researcher',
    engineer: pt ? 'engenheiro' : 'engineer',
    student: pt ? 'estudante' : 'student',
    other: pt ? 'outro' : 'other',
  };
  return m[role] || role;
}

/**
 * perfil persistido em user_profiles (singleton); preferência de idioma opcionalmente sincroniza com a ui.
 */
export default function ProfilePage() {
  const { language, t, setLanguage } = useLanguage();
  const pt = language === 'pt';

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);

  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [organization, setOrganization] = useState('');
  const [role, setRole] = useState('researcher');
  const [bio, setBio] = useState('');
  const [preferredLanguage, setPreferredLanguage] = useState('pt');
  const [updatedAt, setUpdatedAt] = useState('');

  const loadProfile = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const p = await getProfile();
      setDisplayName(p.display_name || '');
      setEmail(p.email || '');
      setOrganization(p.organization || '');
      setRole(p.role || 'researcher');
      setBio(p.bio || '');
      setPreferredLanguage(p.preferred_language === 'en' ? 'en' : 'pt');
      setUpdatedAt(p.updated_at || '');
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'não foi possível carregar o perfil' : 'could not load profile')
        );
      }
    } finally {
      setLoading(false);
    }
  }, [pt, t]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const avatarLetter = useMemo(() => initialsFromName(displayName), [displayName]);

  const handleSave = async () => {
    setSaving(true);
    setOpError(null);
    setConnectionError(null);
    try {
      const p = await patchProfile({
        display_name: displayName,
        email,
        organization,
        role,
        bio: bio.trim() ? bio : '',
        preferred_language: preferredLanguage,
      });
      setUpdatedAt(p.updated_at || '');
      if (p.preferred_language === 'pt' || p.preferred_language === 'en') {
        setLanguage(p.preferred_language);
      }
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'falha ao salvar' : 'save failed')
        );
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="tab-content">
      <div className="profile-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="profile-op-error" role="alert">
            {opError}
          </div>
        )}

        <div className="profile-page-layout">
          <section className="profile-mockup-card" aria-label={pt ? 'perfil' : 'profile'}>
            <h2>{pt ? 'perfil' : 'profile'}</h2>
            <p className="profile-mockup-sub">
              {pt
                ? 'dados salvos na tabela user_profiles (uma linha). útil para identificar o operador nas exportações e relatórios futuros.'
                : 'data stored in the user_profiles table (single row). useful for operator identity in future exports and reports.'}
            </p>

            {loading ? (
              <p className="profile-status">{pt ? 'a carregar…' : 'loading…'}</p>
            ) : (
              <>
                <div className="profile-avatar-row">
                  <div className="profile-avatar-placeholder" aria-hidden="true">
                    {avatarLetter}
                  </div>
                  <div className="profile-avatar-meta">
                    <strong>{displayName || (pt ? 'sem nome' : 'no name')}</strong>
                    <span>
                      {pt ? 'papel:' : 'role:'} {roleLabel(role, pt)}
                    </span>
                    {updatedAt && (
                      <span className="profile-updated">
                        {pt ? 'última atualização:' : 'last updated:'}{' '}
                        {new Date(updatedAt).toLocaleString(pt ? 'pt-PT' : 'en-GB')}
                      </span>
                    )}
                  </div>
                </div>

                <div className="profile-field-grid">
                  <div className="profile-field">
                    <label htmlFor="profile-name">{pt ? 'nome' : 'name'}</label>
                    <input
                      id="profile-name"
                      type="text"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      maxLength={200}
                      autoComplete="name"
                    />
                  </div>
                  <div className="profile-field">
                    <label htmlFor="profile-email">{pt ? 'e-mail' : 'email'}</label>
                    <input
                      id="profile-email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      maxLength={255}
                      autoComplete="email"
                    />
                  </div>
                  <div className="profile-field">
                    <label htmlFor="profile-org">{pt ? 'instituição' : 'organization'}</label>
                    <input
                      id="profile-org"
                      type="text"
                      value={organization}
                      onChange={(e) => setOrganization(e.target.value)}
                      maxLength={300}
                    />
                  </div>
                  <div className="profile-field">
                    <label htmlFor="profile-role">{pt ? 'papel' : 'role'}</label>
                    <select
                      id="profile-role"
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                    >
                      <option value="researcher">{roleLabel('researcher', pt)}</option>
                      <option value="engineer">{roleLabel('engineer', pt)}</option>
                      <option value="student">{roleLabel('student', pt)}</option>
                      <option value="other">{roleLabel('other', pt)}</option>
                    </select>
                  </div>
                  <div className="profile-field">
                    <label htmlFor="profile-lang">{pt ? 'idioma preferido (ui)' : 'preferred language (ui)'}</label>
                    <select
                      id="profile-lang"
                      value={preferredLanguage}
                      onChange={(e) => setPreferredLanguage(e.target.value)}
                    >
                      <option value="pt">português</option>
                      <option value="en">english</option>
                    </select>
                  </div>
                  <div className="profile-field profile-field-bio">
                    <label htmlFor="profile-bio">{pt ? 'biografia / notas' : 'bio / notes'}</label>
                    <textarea
                      id="profile-bio"
                      rows={5}
                      value={bio}
                      onChange={(e) => setBio(e.target.value)}
                      placeholder={
                        pt
                          ? 'área de pesquisa, contatos, observações…'
                          : 'research area, contacts, notes…'
                      }
                    />
                  </div>
                </div>

                <div className="profile-actions-mock">
                  <button type="button" className="profile-btn-save" onClick={handleSave} disabled={saving}>
                    {saving ? (pt ? 'salvando…' : 'saving…') : pt ? 'salvar alterações' : 'save changes'}
                  </button>
                  <button
                    type="button"
                    className="profile-btn-muted"
                    disabled
                    title={pt ? 'não há autenticação nesta versão do aplicativo' : 'no authentication in this app version'}
                  >
                    {pt ? 'alterar senha' : 'change password'}
                  </button>
                  <button type="button" className="profile-btn-secondary" onClick={() => loadProfile()} disabled={loading}>
                    {pt ? 'atualizar' : 'update'}
                  </button>
                </div>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
