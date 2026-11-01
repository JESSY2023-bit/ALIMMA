import { z } from "zod";

/** Informations personnelles (le téléphone n’est pas modifiable : c’est l’identifiant de connexion). */
export const profileSchema = z.object({
  nom: z.string().trim().min(2, "Saisissez au moins 2 caractères."),
  email: z.string().trim().email("Il manque la fin de l’adresse, par exemple « @gmail.com ».").optional().or(z.literal("")),
});

/** Changement de mot de passe */
export const passwordSchema = z
  .object({
    ancien_mot_de_passe: z.string().min(1, "Saisissez votre mot de passe actuel."),
    nouveau_mot_de_passe: z
      .string()
      .min(8, "Trop court : 8 caractères minimum, dont au moins 1 chiffre.")
      .regex(/\d/, "Ajoutez au moins 1 chiffre (8 caractères minimum)."),
    confirm_password: z.string().min(1, "Confirmez le nouveau mot de passe."),
  })
  .refine((d) => d.nouveau_mot_de_passe === d.confirm_password, {
    message: "Les deux mots de passe ne correspondent pas.",
    path: ["confirm_password"],
  })
  .refine((d) => d.nouveau_mot_de_passe !== d.ancien_mot_de_passe, {
    message: "Choisissez un mot de passe différent de l’actuel.",
    path: ["nouveau_mot_de_passe"],
  });
