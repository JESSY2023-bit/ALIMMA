// src/hooks/useProfile.js
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";

const PROFILE_KEY = ["profile", "moi"];
const unwrap = (res) => res.data?.data ?? res.data;

/** GET /v1/utilisateurs/moi — mon profil. */
export function useProfile() {
  return useQuery({
    queryKey: PROFILE_KEY,
    queryFn: async () => unwrap(await api.get("/utilisateurs/moi")),
  });
}

/** PATCH /v1/utilisateurs/moi — modifier mon profil ({ nom, email?, photo_url? }). Retourne le profil mis à jour. */
export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload) => unwrap(await api.patch("/utilisateurs/moi", payload)),
    onSuccess: (updated) => {
      if (updated) queryClient.setQueryData(PROFILE_KEY, (old) => ({ ...old, ...updated }));
      else queryClient.invalidateQueries({ queryKey: PROFILE_KEY });
    },
  });
}

/** PUT /v1/utilisateurs/moi/mot-de-passe — { ancien_mot_de_passe, nouveau_mot_de_passe }. */
export function useChangePassword() {
  return useMutation({
    mutationFn: async (payload) => unwrap(await api.put("/utilisateurs/moi/mot-de-passe", payload)),
  });
}
