// cliente http para api backend
import axios from 'axios';

const apiBase =
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) ||
  'http://localhost:8000';

const api = axios.create({
  baseURL: apiBase,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// bed compiler
export const compileBed = async (parameters) => {
  const response = await api.post('/api/bed/compile', { parameters });
  return response.data;
};

// gerar modelo 3d
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

// resultados de uma simulacao especifica
export const getSimulationResults = async (simulationId, resultType = null) => {
  const params = {};
  if (resultType) params.result_type = resultType;
  const response = await api.get(`/api/results/simulation/${simulationId}`, { params });
  return response.data;
};

export default api;

