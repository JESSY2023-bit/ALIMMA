// src/hooks/useAuth.js
import { useMutation } from '@tanstack/react-query';
import { api, getRefreshToken, setTokens, clearTokens } from '../services/api';

// Connexion
export const useLogin = () =>
  useMutation({
    mutationFn: async (credentials) => {
      const { data } = await api.post('/auth/login', credentials);
      return data;
    },
  });

// Inscription
export const useRegister = () =>
  useMutation({
    mutationFn: async (userData) => {
      // ✅ On retire confirmPassword avant d'envoyer à l'API
      const { confirmPassword, ...payload } = userData;
      const { data } = await api.post('/auth/inscription', payload);
      return data;
    },
  });

// Vérification OTP
export const useVerifyOtp = () =>
  useMutation({
    mutationFn: async (otpData) => {
      const { data } = await api.post('/auth/verify-otp', otpData);
      return data;
    },
  });

// Déconnexion
export const useLogout = () => {
  return useMutation({
    mutationFn: async () => {
      const refresh_token = getRefreshToken();
      if (refresh_token) {
        try {
          await api.post('/auth/logout', { refresh_token });
        } catch (err) {
          console.warn('Logout serveur échoué, nettoyage local quand même.', err);
        }
      }
    },
    onSettled: () => {
      clearTokens();
    },
  });
};

// Rafraîchir manuellement
export const useRefreshToken = () => {
  return useMutation({
    mutationFn: async () => {
      const refresh_token = getRefreshToken();
      if (!refresh_token) throw new Error('Aucun refresh token disponible.');
      const { data } = await api.post('/auth/refresh', { refresh_token });
      setTokens(data);
      return data;
    },
  });
};