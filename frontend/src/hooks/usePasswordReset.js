// src/hooks/usePasswordReset.js
import { useMutation } from "@tanstack/react-query";
import { api } from "../services/api"; // export nommé

/** Étape 1 : envoie un code SMS au numéro. */
export const useForgotPassword = () =>
  useMutation({
    mutationFn: (telephone) => api.post("/auth/mot-de-passe-oublie", { telephone }).then((r) => r.data),
  });

/** Étape 2 : vérifie le code. Réponse attendue : { reset_token }. */
export const useVerifyResetCode = () =>
  useMutation({
    mutationFn: ({ telephone, code }) =>
      api.post("/auth/mot-de-passe-oublie/verifier", { telephone, code }).then((r) => r.data),
  });

/** Étape 3 : enregistre le nouveau mot de passe. */
export const useResetPassword = () =>
  useMutation({
    mutationFn: ({ reset_token, password }) =>
      api.post("/auth/mot-de-passe-oublie/reinitialiser", { reset_token, password }).then((r) => r.data),
  });