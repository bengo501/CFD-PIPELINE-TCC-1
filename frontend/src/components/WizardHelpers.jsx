// componentes auxiliares para o wizard

export const HelpModal = ({ show, onClose, section, paramHelp }) => {
  if (!show) return null;

  const sections = {
    'bed': 'geometria do leito',
    'lids': 'tampas',
    'particles': 'partículas',
    'packing': 'empacotamento',
    'export': 'exportação',
    'cfd': 'simulação cfd'
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>ajuda - parâmetros</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="help-sections">
            {Object.entries(sections).map(([key, title]) => (
              <div key={key} className="help-section">
                <h3>{title}</h3>
                <div className="help-params">
                  {Object.entries(paramHelp)
                    .filter(([paramKey]) => paramKey.startsWith(`${key}.`))
                    .map(([paramKey, info]) => (
                      <div key={paramKey} className="help-param">
                        <h4>{paramKey.split('.')[1]}</h4>
                        <p><strong>descrição:</strong> {info.desc}</p>
                        {info.min !== undefined && (
                          <p><strong>range:</strong> {info.min}{info.unit} a {info.max}{info.unit}</p>
                        )}
                        <p><strong>exemplo:</strong> {info.exemplo}</p>
                      </div>
                    ))
                  }
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export const DocsModal = ({ show, onClose }) => {
  if (!show) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-docs" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>documentação do wizard</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="docs-content">
            <section>
              <h3>sobre o wizard</h3>
              <p>
                o wizard permite criar arquivos .bed para definir leitos empacotados.
                esses arquivos são usados para gerar modelos 3D e simulações CFD.
              </p>
            </section>

            <section>
              <h3>modos disponíveis</h3>
              <ul>
                <li><strong>questionário interativo:</strong> preencha formulários passo a passo</li>
                <li><strong>editor de template:</strong> edite diretamente um arquivo .bed de exemplo</li>
                <li><strong>modo blender:</strong> gere apenas modelo 3D (sem CFD)</li>
                <li><strong>blender interativo:</strong> gere e abra automaticamente no blender</li>
              </ul>
            </section>

            <section>
              <h3>parâmetros principais</h3>
              <ul>
                <li><strong>geometria:</strong> diâmetro, altura, espessura da parede</li>
                <li><strong>partículas:</strong> tipo, tamanho, quantidade, densidade</li>
                <li><strong>empacotamento:</strong> método físico, gravidade, tempo</li>
                <li><strong>exportação:</strong> formatos de saída (blend, gltf, obj, stl)</li>
              </ul>
            </section>

            <section>
              <h3>dicas</h3>
              <ul>
                <li>use valores padrão para começar rapidamente</li>
                <li>digite ? em campos numéricos para ver ajuda</li>
                <li>comece com poucas partículas (50-100) para testes</li>
                <li>aumente gradualmente para modelos finais (500-1000+)</li>
              </ul>
            </section>

            <section>
              <h3>formatos de exportação</h3>
              <ul>
                <li><strong>.blend:</strong> arquivo nativo blender (completo)</li>
                <li><strong>.gltf/.glb:</strong> formato web (usado pelo visualizador)</li>
                <li><strong>.obj:</strong> formato universal (importar em outros programas)</li>
                <li><strong>.fbx:</strong> formato autodesk (unity, unreal)</li>
                <li><strong>.stl:</strong> impressão 3D, CAD</li>
              </ul>
            </section>

            <section>
              <h3>links úteis</h3>
              <ul>
                <li><a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
                  documentação da api
                </a></li>
                <li><a href="https://github.com" target="_blank" rel="noopener noreferrer">
                  código fonte no github
                </a></li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export const TemplateEditor = ({ show, onClose, onSubmit }) => {
  const [templateText, setTemplateText] = useState(
    `// template padrao para leito empacotado
// edite os valores conforme necessario

bed {
    diameter = 0.05 m;           // diametro do leito
    height = 0.1 m;              // altura do leito
    wall_thickness = 0.002 m;    // espessura da parede
    clearance = 0.01 m;          // folga superior
    material = "steel";          // material da parede
    roughness = 0.0 m;           // rugosidade (opcional)
}

lids {
    top_type = "flat";           // tipo da tampa superior
    bottom_type = "flat";        // tipo da tampa inferior
    top_thickness = 0.003 m;     // espessura tampa superior
    bottom_thickness = 0.003 m;  // espessura tampa inferior
    seal_clearance = 0.001 m;    // folga do selo (opcional)
}

particles {
    kind = "sphere";             // tipo de particula
    diameter = 0.005 m;          // diametro das particulas
    count = 100;                 // numero de particulas
    target_porosity = 0.4;       // porosidade alvo (opcional)
    density = 2500.0 kg/m3;      // densidade do material
    mass = 0.0 g;                // massa das particulas (opcional)
    restitution = 0.3;           // coeficiente de restituicao (opcional)
    friction = 0.5;              // coeficiente de atrito (opcional)
    rolling_friction = 0.1;      // atrito de rolamento (opcional)
    linear_damping = 0.1;        // amortecimento linear (opcional)
    angular_damping = 0.1;       // amortecimento angular (opcional)
    seed = 42;                   // seed para reproducibilidade (opcional)
}

packing {
    method = "rigid_body";       // metodo de empacotamento
    gravity = -9.81 m/s2;        // gravidade
    substeps = 10;               // sub-passos de simulacao (opcional)
    iterations = 10;             // iteracoes (opcional)
    damping = 0.1;               // amortecimento (opcional)
    rest_velocity = 0.01 m/s;    // velocidade de repouso (opcional)
    max_time = 5.0 s;            // tempo maximo (opcional)
    collision_margin = 0.001 m;  // margem de colisao (opcional)
}

export {
    formats = ["blend", "glb", "obj"];  // formatos de exportacao
    units = "m";                         // unidades de saida (opcional)
    scale = 1.0;                         // escala (opcional)
    wall_mode = "surface";               // modo da parede
    fluid_mode = "none";                 // modo do fluido
    manifold_check = true;               // verificar manifold (opcional)
    merge_distance = 0.001 m;            // distancia de fusao (opcional)
}

// secao CFD (opcional - descomente se necessario)
/*
cfd {
    regime = "laminar";                  // regime CFD
    inlet_velocity = 0.1 m/s;            // velocidade de entrada (opcional)
    fluid_density = 1.225 kg/m3;         // densidade do fluido (opcional)
    fluid_viscosity = 1.8e-5 Pa.s;      // viscosidade do fluido (opcional)
    max_iterations = 1000;               // iteracoes maximas (opcional)
    convergence_criteria = 1e-6;         // criterio de convergencia (opcional)
    write_fields = false;                // escrever campos (opcional)
}
*/`
  );

  if (!show) return null;

  const handleSubmit = () => {
    onSubmit(templateText);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-template" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>editor de template .bed</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <p className="template-hint">
            edite o template abaixo e clique em "usar este template" para continuar
          </p>
          <textarea
            className="template-editor"
            value={templateText}
            onChange={(e) => setTemplateText(e.target.value)}
            spellCheck={false}
          />
        </div>
        
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            cancelar
          </button>
          <button className="btn btn-primary" onClick={handleSubmit}>
            usar este template
          </button>
        </div>
      </div>
    </div>
  );
};

// adicionar import useState
import { useState } from 'react';

