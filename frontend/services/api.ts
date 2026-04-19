'use client';

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  
  register: (data: { email: string; password: string; full_name: string; confirm_password: string }) =>
    api.post('/auth/register', data),
  
  logout: () => api.post('/auth/logout'),
  
  getMe: () => api.get('/auth/me'),
  
  refreshToken: () => api.post('/auth/refresh'),
};

// Market Data API
export const marketAPI = {
  getOverview: () => api.get('/market/overview'),
  
  getPrice: (symbol: string) => api.get(`/market/price/${symbol}`),
  
  getCandles: (symbol: string, timeframe: string, count?: number) =>
    api.get(`/market/candles/${symbol}`, { params: { timeframe, count } }),
};

// Signals API
export const signalsAPI = {
  generate: (data: {
    symbol: string;
    timeframe: string;
    balance: number;
    risk_percent: number;
    candle_count?: number;
  }) => api.post('/signals/generate', data),
  
  getHistory: (params?: {
    symbol?: string;
    timeframe?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/signals/history', { params }),
  
  getLatest: (limit?: number) => api.get('/signals/latest', { params: { limit } }),
  
  updateStatus: (signalId: number, status: string) =>
    api.patch(`/signals/${signalId}/status`, null, { params: { new_status: status } }),
  
  getStats: () => api.get('/signals/stats'),
};

// Calculator API
export const calculatorAPI = {
  calculateLotSize: (data: {
    balance: number;
    risk_percent: number;
    stop_loss_pips: number;
    symbol: string;
  }) => api.post('/calculator/lot-size', data),
  
  calculateFromPrices: (params: {
    balance: number;
    risk_percent: number;
    entry_price: number;
    stop_loss_price: number;
    symbol: string;
  }) => api.post('/calculator/lot-size-from-prices', null, { params }),
};

// Subscriptions API
export const subscriptionAPI = {
  getPlans: () => api.get('/subscriptions/plans'),
  
  getPlanDetails: (tier: string) => api.get(`/subscriptions/plans/${tier}`),
  
  getMySubscription: () => api.get('/subscriptions/my'),
  
  subscribe: (data: { tier: string; payment_method?: string; auto_renew?: boolean }) =>
    api.post('/subscriptions/subscribe', data),
  
  cancel: () => api.post('/subscriptions/cancel'),
  
  renew: () => api.post('/subscriptions/renew'),
  
  getStats: () => api.get('/subscriptions/stats'),
  
  getHistory: (limit?: number) => api.get('/subscriptions/history', { params: { limit } }),
};

// Admin API
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  
  getUsers: (params?: { skip?: number; limit?: number; tier?: string }) =>
    api.get('/admin/users', { params }),
  
  getUserDetails: (userId: number) => api.get(`/admin/users/${userId}`),
  
  updateUserSubscription: (userId: number, tier: string) =>
    api.patch(`/admin/users/${userId}/subscription`, null, { params: { new_tier: tier } }),
  
  getSignals: (params?: {
    skip?: number;
    limit?: number;
    symbol?: string;
    signal_type?: string;
    status?: string;
  }) => api.get('/admin/signals', { params }),
  
  getSignalsStats: () => api.get('/admin/signals/stats'),
  
  getWebhooks: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/admin/webhooks', { params }),
  
  getSubscriptions: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/admin/subscriptions', { params }),
  
  getPayments: (params?: { skip?: number; limit?: number }) =>
    api.get('/admin/payments', { params }),
  
  deactivateUser: (userId: number) => api.post(`/admin/users/${userId}/deactivate`),
  
  activateUser: (userId: number) => api.post(`/admin/users/${userId}/activate`),
  
  deleteSignal: (signalId: number) => api.delete(`/admin/signals/${signalId}`),
};

// Webhook API
export const webhookAPI = {
  testWebhook: (data: {
    symbol: string;
    timeframe?: string;
    trigger: string;
    price: number;
    volume?: number;
    bar_time?: string;
    text?: string;
  }) => api.post('/webhook/test', data),
};

export default api;