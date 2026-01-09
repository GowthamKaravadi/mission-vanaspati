import axios from 'axios';

// Use environment variable or default to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('email');
      localStorage.removeItem('isAdmin');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  signup: (username, email, password) => 
    api.post(`/auth/signup?username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`),
  
  login: (usernameOrEmail, password) => {
    const formData = new FormData();
    formData.append('username', usernameOrEmail);
    formData.append('password', password);
    return api.post('/auth/login', formData);
  },
  
  getCurrentUser: () => api.get('/auth/me'),
};

export const predictionAPI = {
  predict: (file, confidenceThreshold = 0.5) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('confidence_threshold', confidenceThreshold);
    return api.post('/predict', formData);
  },
  
  predictBatch: (files, confidenceThreshold = 0.5) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('confidence_threshold', confidenceThreshold);
    return api.post('/predict/batch', formData);
  },
};

export const adminAPI = {
  getUsers: () => api.get('/admin/users'),
  toggleAdmin: (userId) => api.put(`/admin/users/${userId}/toggle-admin`),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  getFeedback: (status = null) => 
    api.get('/admin/feedback', { params: status ? { status } : {} }),
  updateFeedbackStatus: (feedbackId, status) =>
    api.patch(`/admin/feedback/${feedbackId}?status=${status}`),
};

export const gardenAPI = {
  getPlants: () => api.get('/garden/plants'),
  savePlant: (plantName, diseaseName, confidence, notes = null, status = 'monitoring') =>
    api.post('/garden/plants', null, {
      params: { plant_name: plantName, disease_name: diseaseName, confidence, notes, status }
    }),
  updatePlant: (plantId, notes = null, status = null) =>
    api.patch(`/garden/plants/${plantId}`, null, { params: { notes, status } }),
  deletePlant: (plantId) => api.delete(`/garden/plants/${plantId}`),
};

export const historyAPI = {
  getHistory: (limit = 50, offset = 0) => 
    api.get('/history/diagnosis', { params: { limit, offset } }),
  saveHistory: (data) => api.post('/history/diagnosis', data),
  deleteHistory: (diagnosisId) => api.delete(`/history/diagnosis/${diagnosisId}`),
  clearHistory: () => api.delete('/history/diagnosis'),
};

export default api;
