// // src/schemas/profileSchemas.js
// import { z } from 'zod';

// export const profileSchema = z.object({
//   nom: z
//     .string()
//     .min(2, "Le nom doit contenir au moins 2 caractères")
//     .max(100, "Le nom est trop long"),
//   email: z
//     .string()
//     .email("Adresse email invalide")
//     .optional()
//     .or(z.literal('')),
//   telephone: z
//     .string()
//     .regex(/^\+237[0-9]{9}$/, "Le numéro doit être au format +237XXXXXXXXX")
//     .optional()
//     .or(z.literal('')),
//   photo_url: z
//     .string()
//     .url("L'URL de la photo est invalide")
//     .optional()
//     .or(z.literal('')),
// });

// export const passwordSchema = z
//   .object({
//     ancien_mot_de_passe: z
//       .string()
//       .min(1, "L'ancien mot de passe est requis"),
//     nouveau_mot_de_passe: z
//       .string()
//       .min(8, "Le nouveau mot de passe doit contenir au moins 8 caractères"),
//     confirm_password: z.string(),
//   })
//   .refine((data) => data.nouveau_mot_de_passe === data.confirm_password, {
//     message: "Les mots de passe ne correspondent pas",
//     path: ["confirm_password"],
//   });



// src/schemas/profileSchema.js
import { z } from 'zod';

// ✅ Accepte URL classique OU base64 (data:image/...)
const photoUrlSchema = z
  .string()
  .optional()
  .or(z.literal(''))
  .refine(
    (val) => {
      if (!val) return true; // vide = OK
      // URL http(s) classique
      if (/^https?:\/\//.test(val)) return true;
      // Base64 image
      if (/^data:image\/(png|jpe?g|gif|webp);base64,/.test(val)) return true;
      return false;
    },
    { message: "Format d'image invalide" }
  );

export const profileSchema = z.object({
  nom: z
    .string()
    .min(2, "Le nom doit contenir au moins 2 caractères")
    .max(100, "Le nom est trop long"),
  email: z
    .string()
    .email("Adresse email invalide")
    .optional()
    .or(z.literal('')),
  telephone: z
    .string()
    .regex(/^\+237[0-9]{9}$/, "Le numéro doit être au format +237XXXXXXXXX")
    .optional()
    .or(z.literal('')),
  photo_url: photoUrlSchema,
});

export const passwordSchema = z
  .object({
    ancien_mot_de_passe: z
      .string()
      .min(1, "L'ancien mot de passe est requis"),
    nouveau_mot_de_passe: z
      .string()
      .min(8, "Le nouveau mot de passe doit contenir au moins 8 caractères"),
    confirm_password: z.string(),
  })
  .refine((data) => data.nouveau_mot_de_passe === data.confirm_password, {
    message: "Les mots de passe ne correspondent pas",
    path: ["confirm_password"],
  });