// src/services/api.js
import axios from 'axios';

// L'URL dépend de l'environnement Vite : local avec Docker ou API distante.
// Le secours localhost est réservé au mode développement.
const DEFAULT_API_BASE_URL = import.meta.env.DEV
  ? 'http://localhost:8000/v1'
  : '/v1';

const API_BASE_URL = (
  import.meta.env.VITE_API_URL || DEFAULT_API_BASE_URL
).replace(/\/$/, '');

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});


// GESTION de token

export const getAccessToken = () => localStorage.getItem('access_token');
export const getRefreshToken = () => localStorage.getItem('refresh_token');

export const setTokens = ({ access_token, refresh_token }) => {
  if (access_token) localStorage.setItem('access_token', access_token);
  if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
};

export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

// ============================================================
// INTERCEPTEUR DE REQ Ajout automatique du JWT
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// ============================================================
// INTERCEPTEUR DE RÉPONSE : Refresh automatique sur 401
// ============================================================

// File d'attente des requêtes en attendant le nouveau token
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // ❌ Pas de réponse (erreur réseau) → on laisse passer
    if (!error.response) return Promise.reject(error);

    const status = error.response.status;

    // 🔒 401 : tentative de refresh automatique
    if (status === 401 && !originalRequest._retry) {
      // Si on est déjà en train de refresh, on met la requête en attente
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = getRefreshToken();

      // ⚠️ Pas de refresh_token stocké → déconnexion immédiate
      if (!refreshToken) {
        clearTokens();
        isRefreshing = false;
        processQueue(error, null);
        if (window.location.pathname !== '/login') window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        // On utilise une instance axios "nue" pour éviter la boucle infinie
        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        setTokens(data);
        api.defaults.headers.common.Authorization = `Bearer ${data.access_token}`;

        processQueue(null, data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Le refresh a échoué (token expiré ou révoqué) → déconnexion
        clearTokens();
        processQueue(refreshError, null);
        if (window.location.pathname !== '/login') window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // 🚫 403 : rôle insuffisant
    if (status === 403) console.warn('Accès refusé : rôle insuffisant.');

    return Promise.reject(error);
  }
);