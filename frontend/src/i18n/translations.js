// sistema de internacionalização - português e inglês

export const translations = {
  pt: {
    // header
    appTitle: 'pipeline cfd - leitos empacotados',
    online: 'online',
    offline: 'offline',
    jobs: 'jobs',
    running: 'em execução',
    
    // navegação
    createBed: 'criar leito',
    interactiveWizard: 'wizard interativo',
    cfdSimulation: 'simulação cfd',
    results: 'resultados',
    
    // wizard
    wizardTitle: 'wizard de parametrização de leitos empacotados',
    selectMode: 'escolha o modo de criação',
    help: 'ajuda',
    documentation: 'documentação',
    
    // modos
    interactiveMode: 'questionário interativo',
    interactiveDesc: 'responda perguntas passo a passo para criar seu leito',
    templateMode: 'editor de template',
    templateDesc: 'edite um arquivo .bed de exemplo diretamente',
    blenderMode: 'modo blender',
    blenderDesc: 'geração de modelo 3d (sem parâmetros cfd)',
    blenderInteractiveMode: 'blender interativo',
    blenderInteractiveDesc: 'gera modelo e abre automaticamente no blender',
    
    // botões
    back: 'voltar',
    next: 'próximo',
    generate: 'gerar arquivo .bed',
    cancel: 'cancelar',
    confirm: 'confirmar',
    save: 'salvar',
    close: 'fechar',
    refresh: 'atualizar',
    delete: 'remover',
    view: 'visualizar resultados',
    
    // parâmetros
    bedGeometry: 'geometria do leito',
    lids: 'tampas',
    particles: 'partículas',
    packing: 'empacotamento',
    export: 'exportação',
    cfdParams: 'parâmetros cfd (opcional)',
    confirmation: 'confirmação',
    
    // cfd
    cfdTitle: 'simulações cfd',
    createNewSim: 'criar nova simulação',
    createCase: 'criar caso openfoam',
    createAndRun: 'criar e executar simulação',
    simulations: 'simulações',
    noSimulations: 'nenhuma simulação encontrada',
    autoRefresh: 'auto-atualizar',
    
    // status
    queued: 'na fila',
    preparing: 'preparando',
    meshing: 'gerando malha',
    running: 'executando',
    completed: 'concluído',
    error: 'erro',
    
    // mensagens
    success: 'sucesso',
    warning: 'aviso',
    connectionError: 'erro de conexão com o backend',
    fileNotFound: 'arquivo não encontrado',
    compilationError: 'erro na compilação',
    
    // footer
    version: 'versão',
    project: 'tcc - eng. mecânica'
  },
  
  en: {
    // header
    appTitle: 'cfd pipeline - packed beds',
    online: 'online',
    offline: 'offline',
    jobs: 'jobs',
    running: 'running',
    
    // navigation
    createBed: 'create bed',
    interactiveWizard: 'interactive wizard',
    cfdSimulation: 'cfd simulation',
    results: 'results',
    
    // wizard
    wizardTitle: 'packed bed parameterization wizard',
    selectMode: 'choose creation mode',
    help: 'help',
    documentation: 'documentation',
    
    // modes
    interactiveMode: 'interactive questionnaire',
    interactiveDesc: 'answer questions step by step to create your bed',
    templateMode: 'template editor',
    templateDesc: 'directly edit a .bed example file',
    blenderMode: 'blender mode',
    blenderDesc: '3d model generation (no cfd parameters)',
    blenderInteractiveMode: 'interactive blender',
    blenderInteractiveDesc: 'generates model and opens automatically in blender',
    
    // buttons
    back: 'back',
    next: 'next',
    generate: 'generate .bed file',
    cancel: 'cancel',
    confirm: 'confirm',
    save: 'save',
    close: 'close',
    refresh: 'refresh',
    delete: 'remove',
    view: 'view results',
    
    // parameters
    bedGeometry: 'bed geometry',
    lids: 'lids',
    particles: 'particles',
    packing: 'packing',
    export: 'export',
    cfdParams: 'cfd parameters (optional)',
    confirmation: 'confirmation',
    
    // cfd
    cfdTitle: 'cfd simulations',
    createNewSim: 'create new simulation',
    createCase: 'create openfoam case',
    createAndRun: 'create and run simulation',
    simulations: 'simulations',
    noSimulations: 'no simulations found',
    autoRefresh: 'auto-refresh',
    
    // status
    queued: 'queued',
    preparing: 'preparing',
    meshing: 'meshing',
    running: 'running',
    completed: 'completed',
    error: 'error',
    
    // messages
    success: 'success',
    warning: 'warning',
    connectionError: 'backend connection error',
    fileNotFound: 'file not found',
    compilationError: 'compilation error',
    
    // footer
    version: 'version',
    project: 'senior project - mechanical eng.'
  }
};

// hook para usar traduções
export const useTranslation = (language) => {
  const t = (key) => {
    const keys = key.split('.');
    let value = translations[language];
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    return value || key;
  };
  
  return { t };
};

