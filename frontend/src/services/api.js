// modulo que centraliza o cliente http axios para falar com o backend fastapi
// cada export e uma funcao fina que escolhe metodo url e parametros e devolve response data
import axios from 'axios';

// guarda o host e prefixo da api
// tenta ler vite env vite api url se existir senao usa localhost porta 8000
const apiBase =
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) ||
  'http://localhost:8000';

// fabrica uma instancia axios com base url timeout e cabecalho json padrao
// timeout 30000 significa 30 segundos ate falhar por rede lenta
const api = axios.create({
  baseURL: apiBase,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// envia objeto parameters no corpo e espera caminhos dos ficheiros bed e json gerados
export const compileBed = async (parameters) => {
  const response = await api.post('/api/bed/compile', { parameters });
  return response.data;
};

// pede geracao de modelo 3d a partir do json
// open blender quando true pode abrir gui no servidor se o backend permitir
export const generateModel = async (jsonFile, openBlender = false) => {
  const response = await api.post('/api/model/generate', {
    json_file: jsonFile,
    open_blender: openBlender
  });
  return response.data;
};

// cria caso de simulacao ligando json e blend
// run simulation true pede execucao imediata no backend
export const createSimulation = async (jsonFile, blendFile, runSimulation = false) => {
  const response = await api.post('/api/simulation/create', {
    json_file: jsonFile,
    blend_file: blendFile,
    run_simulation: runSimulation
  });
  return response.data;
};

// le estado atual de um job por id uuid
export const getJobStatus = async (jobId) => {
  const response = await api.get(`/api/job/${jobId}`);
  return response.data;
};

// lista jobs com filtros opcionais de estado e tipo
export const listJobs = async (status = null, jobType = null) => {
  const params = {};
  if (status) params.status = status;
  if (jobType) params.job_type = jobType;
  
  const response = await api.get('/api/jobs', { params });
  return response.data;
};

// inventario de ficheiros por tipo logico bed json blend stl simulations
export const listFiles = async (fileType) => {
  const response = await api.get(`/api/files/${fileType}`);
  return response.data;
};

// devolve url absoluta para o browser fazer download direto sem axios blob
export const downloadFile = (fileType, filename) => {
  return `${apiBase}/api/files/download/${fileType}/${filename}`;
};

// estado geral da api e flags de servicos externos
export const getSystemStatus = async () => {
  const response = await api.get('/api/status');
  return response.data;
};

// agregados para graficos do dashboard contagens medias etc
export const getSimulationsSummary = async () => {
  const response = await api.get('/api/simulations/summary');
  return response.data;
};

// lista curta ordenada por data para widgets recentes
export const listRecentSimulations = async (limit = 8) => {
  const response = await api.get('/api/simulations/recent', {
    params: { limit }
  });
  return response.data;
};

// lista completa com paginacao e filtros bed id e status
export const listSimulations = async ({
  page = 1,
  per_page = 100,
  bed_id = null,
  status = null
} = {}) => {
  const params = { page, per_page };
  if (bed_id != null && bed_id !== '') params.bed_id = bed_id;
  if (status != null && status !== '') params.status = status;
  const response = await api.get('/api/simulations', { params });
  return response.data;
};

// metricas e ficheiros associados a uma simulacao na base sql
export const getSimulationResults = async (simulationId, resultType = null) => {
  const params = {};
  if (resultType) params.result_type = resultType;
  const response = await api.get(`/api/results/simulation/${simulationId}`, { params });
  return response.data;
};

// templates texto bed guardados na tabela bed templates
export const listTemplates = async () => {
  const response = await api.get('/api/templates/list');
  return response.data;
};

// busca um template por id string uuid
export const getTemplate = async (templateId) => {
  const response = await api.get(`/api/templates/${templateId}`);
  return response.data;
};

// grava nome conteudo tag e origem com defaults seguros
export const saveTemplate = async (payload) => {
  const response = await api.post('/api/templates/save', {
    name: payload.name,
    content: payload.content,
    tag: payload.tag ?? 'bed',
    source: payload.source ?? 'editor',
  });
  return response.data;
};

// apaga template sem corpo de resposta util
export const deleteTemplate = async (templateId) => {
  await api.delete(`/api/templates/${templateId}`);
};

// cria copia no servidor com novo id
export const duplicateTemplate = async (templateId) => {
  const response = await api.post(`/api/templates/${templateId}/duplicate`);
  return response.data;
};

// painel admin mostra motor sql contagens e ultimos eventos
export const getDatabasePanel = async () => {
  const response = await api.get('/api/database/panel');
  return response.data;
};

// regista clique de backup ou teste de ligacao no painel
export const postDatabasePanelEvent = async (eventType, detail = null) => {
  const response = await api.post('/api/database/events', {
    event_type: eventType,
    detail,
  });
  return response.data;
};

// crud simples de relatorios markdown ou texto livre
export const listReports = async () => {
  const response = await api.get('/api/reports');
  return response.data;
};

export const getReport = async (reportId) => {
  const response = await api.get(`/api/reports/${reportId}`);
  return response.data;
};

export const createReport = async (payload) => {
  const response = await api.post('/api/reports', payload);
  return response.data;
};

export const updateReport = async (reportId, payload) => {
  const response = await api.patch(`/api/reports/${reportId}`, payload);
  return response.data;
};

export const deleteReport = async (reportId) => {
  await api.delete(`/api/reports/${reportId}`);
};

// meta para autocompletar anexos com simulacoes e templates existentes
export const reportsCatalog = async () => {
  const response = await api.get('/api/reports/meta/catalog');
  return response.data;
};

// lista resultados possiveis para uma simulacao escolhida
export const reportsResultsForSimulation = async (simulationId) => {
  const response = await api.get('/api/reports/meta/results', {
    params: { simulation_id: simulationId },
  });
  return response.data;
};

export const addReportAttachment = async (reportId, payload) => {
  const response = await api.post(`/api/reports/${reportId}/attachments`, payload);
  return response.data;
};

export const removeReportAttachment = async (reportId, attachmentId) => {
  await api.delete(`/api/reports/${reportId}/attachments/${attachmentId}`);
};

// perfil unico local sem fluxo oauth completo
export const getProfile = async () => {
  const response = await api.get('/api/profile');
  return response.data;
};

export const patchProfile = async (payload) => {
  const response = await api.patch('/api/profile', payload);
  return response.data;
};

// preferencias globais tema idioma timeouts openfoam
export const getSettings = async () => {
  const response = await api.get('/api/settings');
  return response.data;
};

export const patchSettings = async (payload) => {
  const response = await api.patch('/api/settings', payload);
  return response.data;
};

// cuidado so funciona se o servidor tiver env allow dev shutdown
export const postAdminDevShutdown = async () => {
  const response = await api.post('/api/admin/dev/shutdown');
  return response.data;
};

// texto explicando como correr o wizard no terminal do sistema
export const getWizardCliInstructions = async () => {
  const response = await api.get('/api/wizard/cli-instructions');
  return response.data;
};

// pede ao sistema operativo abrir terminal com comando sugerido
export const launchWizardCliTerminal = async () => {
  const response = await api.post('/api/wizard/launch-cli-terminal');
  return response.data;
};

export default api;
