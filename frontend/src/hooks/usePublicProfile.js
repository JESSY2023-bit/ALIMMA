import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";

/** GET /v1/utilisateurs/{id} — profil public d’un utilisateur / vendeur. */
export function usePublicProfile(id, { enabled = true } = {}) {
  return useQuery({
    queryKey: ["utilisateur", id],
    enabled: Boolean(id) && enabled,
    queryFn: async () => {
      const { data } = await api.get(`/utilisateurs/${id}`);
      return data?.data ?? data;
    },
  });
}
