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
    project: 'tcc - eng. mecânica',
    
    // sidebar
    create: 'criar',
    simulation: 'simulação',
    pipeline: 'pipeline completo',
    casosCfd: 'casos cfd',
    monitoramentoJobs: 'monitoramento de jobs',
    configuracoes: 'configurações',
    
    // settings
    systemSettings: 'configurações do sistema',
    theme: 'tema',
    themeDesc: 'escolha entre tema claro ou escuro',
    language: 'idioma',
    languageDesc: 'português brasileiro ou inglês',
    database: 'banco de dados',
    databaseDesc: 'configurações de conexão',
    simulations: 'simulações',
    simulationsDesc: 'parâmetros padrão do openfoam',
    
    // bed form
    parametrosLeito: 'parâmetros do leito',
    geometriaLeito: 'geometria do leito',
    diametro: 'diâmetro (m)',
    altura: 'altura (m)',
    espessuraParede: 'espessura parede (m)',
    quantidade: 'quantidade',
    diametroParticula: 'diâmetro partícula (m)',
    densidade: 'densidade (kg/m³)',
    metodo: 'método',
    gravidade: 'gravidade (m/s²)',
    tempo: 'tempo (s)',
    gerarLeito: 'gerar leito',
    
    // jobs
    todosJobs: 'todos os jobs',
    jobDetails: 'detalhes do job',
    status: 'status',
    tipo: 'tipo',
    criado: 'criado',
    duracao: 'duração',
    compilacao: 'compilação',
    modelo3d: 'modelo 3d',
    
    // results
    modelos3d: 'modelos 3d',
    simulacoesCfd: 'simulações cfd',
    baixar: 'baixar',
    visualizar: 'visualizar',
    
    // casos cfd
    casosCfdDisponiveis: 'casos cfd disponíveis',
    nome: 'nome',
    parametros: 'parâmetros',
    executar: 'executar',
    remover: 'remover'
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
    project: 'senior project - mechanical eng.',
    
    // sidebar
    create: 'create',
    simulation: 'simulation',
    pipeline: 'complete pipeline',
    casosCfd: 'cfd cases',
    monitoramentoJobs: 'job monitoring',
    configuracoes: 'settings',
    
    // settings
    systemSettings: 'system settings',
    theme: 'theme',
    themeDesc: 'choose between light or dark theme',
    language: 'language',
    languageDesc: 'brazilian portuguese or english',
    database: 'database',
    databaseDesc: 'connection settings',
    simulations: 'simulations',
    simulationsDesc: 'default openfoam parameters',
    
    // bed form
    parametrosLeito: 'bed parameters',
    geometriaLeito: 'bed geometry',
    diametro: 'diameter (m)',
    altura: 'height (m)',
    espessuraParede: 'wall thickness (m)',
    quantidade: 'quantity',
    diametroParticula: 'particle diameter (m)',
    densidade: 'density (kg/m³)',
    metodo: 'method',
    gravidade: 'gravity (m/s²)',
    tempo: 'time (s)',
    gerarLeito: 'generate bed',
    
    // jobs
    todosJobs: 'all jobs',
    jobDetails: 'job details',
    status: 'status',
    tipo: 'type',
    criado: 'created',
    duracao: 'duration',
    compilacao: 'compilation',
    modelo3d: '3d model',
    
    // results
    modelos3d: '3d models',
    simulacoesCfd: 'cfd simulations',
    baixar: 'download',
    visualizar: 'view',
    
    // casos cfd
    casosCfdDisponiveis: 'available cfd cases',
    nome: 'name',
    parametros: 'parameters',
    executar: 'run',
    remover: 'remove'
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

