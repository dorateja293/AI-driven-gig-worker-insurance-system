import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
};

// Policy API
export const policyAPI = {
  getQuote: (userId) => api.get(`/policy/quote?user_id=${userId}`),
  purchasePolicy: (data) => api.post('/policy/purchase', data),
  getPolicyStatus: (userId) => api.get(`/policy/status?user_id=${userId}`),
};

// Wallet API
export const walletAPI = {
  getWallet: (userId) => api.get(`/wallet?user_id=${userId}`),
  topUp: (data) => api.post('/wallet/top-up', data),
};

// Claims API
export const claimsAPI = {
  getUserClaims: (userId) => api.get(`/claims?user_id=${userId}`),
  getAllClaims: (params) => api.get('/claims/admin/all', { params }),
};

// Events API
export const eventsAPI = {
  getEvents: (zone) => api.get(`/events${zone ? `?zone=${zone}` : ''}`),
  simulateEvent: (data) => api.post('/events/simulate', data),
};

// Fraud API
export const fraudAPI = {
  getFlaggedClaims: (riskLevel) =>
    api.get(`/fraud/flagged${riskLevel ? `?risk_level=${riskLevel}` : ''}`),
};

export default api;
