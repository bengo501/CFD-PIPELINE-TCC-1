import { useLanguage } from '../context/LanguageContext';
import './ProfilePage.css';

/**
 * mockup da página de perfil; ícone wip indica que a funcionalidade não está finalizada.
 */
export default function ProfilePage() {
  const { language } = useLanguage();
  const pt = language === 'pt';

  return (
    <div className="tab-content">
      <div className="profile-page">
        <div className="profile-page-layout">
          <section className="profile-mockup-card" aria-label={pt ? 'pré-visualização do perfil' : 'profile preview'}>
            <h2>{pt ? 'pré-visualização' : 'preview'}</h2>
            <p className="profile-mockup-sub">
              {pt
                ? 'dados fictícios — edição e persistência virão numa versão futura.'
                : 'placeholder data — editing and persistence will ship in a future version.'}
            </p>

            <div className="profile-avatar-row">
              <div className="profile-avatar-placeholder" aria-hidden="true">
                ?
              </div>
              <div className="profile-avatar-meta">
                <strong>{pt ? 'utilizador de demonstração' : 'demo user'}</strong>
                <span>{pt ? 'papel: investigador' : 'role: researcher'}</span>
              </div>
            </div>

            <div className="profile-field-grid">
              <div className="profile-field">
                <label htmlFor="profile-mock-name">{pt ? 'nome' : 'name'}</label>
                <input id="profile-mock-name" type="text" readOnly value="ana silva" />
              </div>
              <div className="profile-field">
                <label htmlFor="profile-mock-email">{pt ? 'e-mail' : 'email'}</label>
                <input id="profile-mock-email" type="email" readOnly value="ana.silva@exemplo.edu" />
              </div>
              <div className="profile-field">
                <label htmlFor="profile-mock-org">{pt ? 'instituição' : 'organization'}</label>
                <input id="profile-mock-org" type="text" readOnly value={pt ? 'laboratório de engenharia — demo' : 'engineering lab — demo'} />
              </div>
            </div>

            <div className="profile-actions-mock">
              <button type="button" disabled>
                {pt ? 'guardar alterações' : 'save changes'}
              </button>
              <button type="button" disabled>
                {pt ? 'alterar palavra-passe' : 'change password'}
              </button>
            </div>
          </section>

          <aside className="profile-wip-panel" aria-label={pt ? 'estado da funcionalidade' : 'feature status'}>
            <div className="profile-wip-badge">{pt ? 'em construção' : 'work in progress'}</div>
            <img
              src="/image/wip-profile.png"
              alt={pt ? 'ícone: página em construção' : 'work in progress indicator'}
              className="profile-wip-icon"
            />
            <p className="profile-wip-note">
              {pt
                ? 'esta área ainda não está concluída. o mockup acima mostra apenas a linha visual prevista.'
                : 'this area is not finished yet. the mockup shows the intended layout only.'}
            </p>
          </aside>
        </div>
      </div>
    </div>
  );
}
