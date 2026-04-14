// cliente axios partilhado para todas as chamadas rest
import axios from 'axios';

// url base vem de vite env ou fallback localhost8000
const apiBase =
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) ||
  'http://localhost:8000';

// instancia unica com json e timeout 30s
const api = axios.create({
  baseURL: apiBase,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// envia parametros flat e recebe caminhos bed json
export const compileBed = async (parameters) => {
  const response = await api.post('/api/bed/compile', { parameters });
  return response.data;
};

// inicia job blender devolve job_id para polling
export const generateModel = async (jsonFile, openBlender = false) => {
  const response = await api.post('/api/model/generate', {
    json_file: jsonFile,
    open_blender: openBlender
  });
  return response.data;
};

// criar simulação
export const createSimulation = async (jsonFile, blendFile, runSimulation = false) => {
  const response = await api.post('/api/simulation/create', {
    json_file: jsonFile,
    blend_file: blendFile,
    run_simulation: runSimulation
  });
  return response.data;
};

// buscar status de job
export const getJobStatus = async (jobId) => {
  const response = await api.get(`/api/job/${jobId}`);
  return response.data;
};

// listar jobs
export const listJobs = async (status = null, jobType = null) => {
  const params = {};
  if (status) params.status = status;
  if (jobType) params.job_type = jobType;
  
  const response = await api.get('/api/jobs', { params });
  return response.data;
};

// listar arquivos
export const listFiles = async (fileType) => {
  const response = await api.get(`/api/files/${fileType}`);
  return response.data;
};

// download de arquivo
export const downloadFile = (fileType, filename) => {
  return `${apiBase}/api/files/download/${fileType}/${filename}`;
};

// status do sistema
export const getSystemStatus = async () => {
  const response = await api.get('/api/status');
  return response.data;
};

// resumo de simulacoes para o dashboard
export const getSimulationsSummary = async () => {
  const response = await api.get('/api/simulations/summary');
  return response.data;
};

// simulacoes recentes (para o dashboard)
export const listRecentSimulations = async (limit = 8) => {
  const response = await api.get('/api/simulations/recent', {
    params: { limit }
  });
  return response.data;
};

// lista paginada de simulacoes (sqlite/postgresql)
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

// resultados de uma simulacao especifica
export const getSimulationResults = async (simulationId, resultType = null) => {
  const params = {};
  if (resultType) params.result_type = resultType;
  const response = await api.get(`/api/results/simulation/${simulationId}`, { params });
  return response.data;
};

// templates .bed persistidos (bed_templates no sqlite/postgresql)
export const listTemplates = async () => {
  const response = await api.get('/api/templates/list');
  return response.data;
};

export const getTemplate = async (templateId) => {
  const response = await api.get(`/api/templates/${templateId}`);
  return response.data;
};

export const saveTemplate = async (payload) => {
  const response = await api.post('/api/templates/save', {
    name: payload.name,
    content: payload.content,
    tag: payload.tag ?? 'bed',
    source: payload.source ?? 'editor',
  });
  return response.data;
};

export const deleteTemplate = async (templateId) => {
  await api.delete(`/api/templates/${templateId}`);
};

export const duplicateTemplate = async (templateId) => {
  const response = await api.post(`/api/templates/${templateId}/duplicate`);
  return response.data;
};

// painel banco de dados (admin_panel_events + contagens)
export const getDatabasePanel = async () => {
  const response = await api.get('/api/database/panel');
  return response.data;
};

export const postDatabasePanelEvent = async (eventType, detail = null) => {
  const response = await api.post('/api/database/events', {
    event_type: eventType,
    detail,
  });
  return response.data;
};

// relatorios tabelas reports e report_attachments
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

export const reportsCatalog = async () => {
  const response = await api.get('/api/reports/meta/catalog');
  return response.data;
};

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

// perfil singleton (user_profiles id=1)
export const getProfile = async () => {
  const response = await api.get('/api/profile');
  return response.data;
};

export const patchProfile = async (payload) => {
  const response = await api.patch('/api/profile', payload);
  return response.data;
};

export const getSettings = async () => {
  const response = await api.get('/api/settings');
  return response.data;
};

export const patchSettings = async (payload) => {
  const response = await api.patch('/api/settings', payload);
  return response.data;
};

// mata processo backend so se env allow dev shutdown
export const postAdminDevShutdown = async () => {
  const response = await api.post('/api/admin/dev/shutdown');
  return response.data;
};

// texto de ajuda para correr wizard no terminal
export const getWizardCliInstructions = async () => {
  const response = await api.get('/api/wizard/cli-instructions');
  return response.data;
};

// pede ao backend abrir janela de terminal com o cli
export const launchWizardCliTerminal = async () => {
  const response = await api.post('/api/wizard/launch-cli-terminal');
  return response.data;
};

export default api;

