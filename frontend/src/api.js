import axios from 'axios';

// Determine API base URL based on environment
const getApiUrl = () => {
  // If VITE_API_URL is set, use it (for external/separate deployments)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // If in production, API calls are proxied by nginx at root
  // No need to specify a base URL, relative paths will work
  if (import.meta.env.PROD) {
    return '';
  }
  
  // Development: use localhost backend on port 7999 (or 8000)
  return 'http://localhost:7999';
};

const API_BASE_URL = getApiUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  // Get statistics
  stats: () => api.get('/stats'),
  
  // Document operations
  uploadDocument: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getDocuments: () => api.get('/documents'),
  
  deleteDocument: (documentId) => api.delete(`/documents/${documentId}`),
  
  // QA operations
  askQuestion: (question, topK = 3, threshold = 0.50) =>
    api.post('/ask', {
      question,
      top_k: topK,
      similarity_threshold: threshold,
    }),

  // QA with LLM
  askQuestionWithLLM: (question, topK = 3, threshold = 0.50, model = 'gemini-pro') =>
    api.post('/ask-llm', {
      question,
      top_k: topK,
      similarity_threshold: threshold,
      model,
    }),
};

export default api;
