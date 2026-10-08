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
      // Le champ sert uniquement à la validation du formulaire frontend.
      const payload = { ...userData };
      delete payload.confirmPassword;
      const { data } = await api.post('/auth/inscription', payload);
      return data;
    },
  });

//  Vérification OTP
export const useVerifyOtp = () =>
  useMutation({
    mutationFn: async (otpData) => {
      const { data } = await api.post('/auth/verify-otp', otpData);
      return data;
    },
  });

// Déconnexion : révoque le refresh token côté serveur puis nettoie le client
export const useLogout = () => {
  return useMutation({
    mutationFn: async () => {
      const refresh_token = getRefreshToken();
      // Si on a un refresh token, on le révoque côté serveur
      if (refresh_token) {
        try {
          await api.post('/auth/logout', { refresh_token });
        } catch (err) {
          // Si le serveur refuse (token déjà expiré par ex.), on continue
          console.warn('Logout serveur échoué, nettoyage local quand même.', err);
        }
      }
    },
    onSettled: () => {
      // Toujours nettoyer le client, succès ou échec
      clearTokens();
    },
  });
};

// Rafraîchir manuellement (utile avant une action sensible)
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