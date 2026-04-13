import { useLanguage } from '../context/LanguageContext';
import './SavedTemplatesPage.css';

/**
 * mockup da biblioteca de templates salvos; painel wip alinhado a perfil/relatórios.
 */
export default function SavedTemplatesPage() {
  const { language } = useLanguage();
  const pt = language === 'pt';

  const items = pt
    ? [
        { title: 'leito_cilindrico_padrao.bed', meta: 'atualizado · há 3 dias · origem: editor', tag: 'bed' },
        { title: 'malha_grossa_referencia', meta: 'atualizado · há 1 semana · origem: duplicado', tag: 'preset' },
        { title: 'cfd_bloco_entrada_01', meta: 'rascunho · sem associação a simulação', tag: 'cfd' },
      ]
    : [
        { title: 'cylindrical_bed_default.bed', meta: 'updated · 3 days ago · source: editor', tag: 'bed' },
        { title: 'coarse_mesh_reference', meta: 'updated · 1 week ago · source: duplicate', tag: 'preset' },
        { title: 'cfd_inlet_block_01', meta: 'draft · no simulation link', tag: 'cfd' },
      ];

  return (
    <div className="tab-content">
      <div className="saved-templates-page">
        <div className="saved-templates-layout">
          <section
            className="saved-templates-mockup-card"
            aria-label={pt ? 'pré-visualização da biblioteca' : 'library preview'}
          >
            <h2>{pt ? 'templates salvos' : 'saved templates'}</h2>
            <p className="saved-templates-lead">
              {pt
                ? 'lista fictícia de presets reutilizáveis. persistência e api virão depois.'
                : 'fictional list of reusable presets. persistence and api will follow.'}
            </p>

            <div className="saved-templates-toolbar">
              <input
                type="search"
                readOnly
                placeholder={pt ? 'pesquisar por nome ou etiqueta…' : 'search by name or tag…'}
                aria-label={pt ? 'pesquisa (desativada)' : 'search (disabled)'}
              />
            </div>

            <div className="saved-templates-grid">
              {items.map((row) => (
                <article key={row.title} className="saved-templates-card">
                  <div className="saved-templates-card-title">{row.title}</div>
                  <span className="saved-templates-card-tag">{row.tag}</span>
                  <div className="saved-templates-card-meta">{row.meta}</div>
                </article>
              ))}
            </div>

            <div className="saved-templates-actions">
              <button type="button" disabled>
                {pt ? 'importar ficheiro' : 'import file'}
              </button>
              <button type="button" disabled>
                {pt ? 'duplicar selecionado' : 'duplicate selected'}
              </button>
              <button type="button" disabled>
                {pt ? 'eliminar' : 'delete'}
              </button>
            </div>
          </section>

          <aside
            className="saved-templates-wip-panel"
            aria-label={pt ? 'estado da funcionalidade' : 'feature status'}
          >
            <div className="saved-templates-wip-badge">{pt ? 'em construção' : 'work in progress'}</div>
            <img
              src="/image/wip-templates-saved.png"
              alt={pt ? 'ícone: funcionalidade em desenvolvimento' : 'work in progress indicator'}
              className="saved-templates-wip-icon"
            />
            <p className="saved-templates-wip-note">
              {pt
                ? 'o editor de templates já existe; a biblioteca guardada na nuvem ou disco será integrada mais tarde.'
                : 'the template editor exists; a saved library on disk or backend will be integrated later.'}
            </p>
          </aside>
        </div>
      </div>
    </div>
  );
}
