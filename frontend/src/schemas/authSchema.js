// schemas/authSchemas.js
import { z } from 'zod';

// Schéma de connexion
export const loginSchema = z.object({
  identifiant: z.string().min(1, "L'email ou le téléphone est requis"),
  password: z.string().min(6, "Le mot de passe doit contenir au moins 6 caractères"),
});

// Schéma d'inscription
export const registerSchema = z.object({
  nom: z.string().min(2, "Le nom complet est requis"),
  telephone: z.string().regex(/^\+237[0-9]{9}$/, "Le numéro doit être au format +237XXXXXXXXX"),
  email: z.string().email("Adresse email invalide").optional().or(z.literal('')),
  password: z.string().min(8, "Le mot de passe doit contenir au moins 8 caractères"),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Les mots de passe ne correspondent pas",
  path: ["confirmPassword"], // L'erreur s'affichera sur le champ confirmPassword
});

// Schéma OTP
export const otpSchema = z.object({
  code: z.string().length(6, "Le code OTP doit contenir exactement 6 chiffres"),
});