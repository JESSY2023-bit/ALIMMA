// src/hooks/useAuth.js
import { useMutation } from '@tanstack/react-query';
import { api } from '../services/api';

// Hook pour la connexion
export const useLogin = () => {
  return useMutation({
    mutationFn: async (credentials) => {
      const { data } = await api.post('/auth/login', credentials);
      return data; // Retourne LoginResponse
    },
  });
};

// Hook pour l'inscription
export const useRegister = () => {
  return useMutation({
    mutationFn: async (userData) => {
      // On retire confirmPassword car l'API ne le demande pas
      const { confirmPassword, ...payload } = userData;
      const { data } = await api.post('/auth/inscription', payload);
      return data; // Retourne Utilisateur
    },
  });
};

// Hook pour la vérification OTP
export const useVerifyOtp = () => {
  return useMutation({
    mutationFn: async (otpData) => {
      const { data } = await api.post('/auth/verify-otp', otpData);
      return data; // Retourne LoginResponse final avec les tokens
    },
  });
};