// // src/hooks/useProfile.js
// import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
// import { api } from '../services/api';

// // Récupérer mon profil
// export const useProfile = () =>
//   useQuery({
//     queryKey: ['profile', 'me'],
//     queryFn: async () => {
//       const { data } = await api.get('/utilisateurs/moi');
//       return data;
//     },
//     staleTime: 1000 * 60 * 5, // 5 min
//   });

// // Mettre à jour mon profil
// export const useUpdateProfile = () => {
//   const queryClient = useQueryClient();

//   return useMutation({
//     mutationFn: async (payload) => {
//       // On ne garde que les champs non vides
//       const cleanPayload = Object.fromEntries(
//         Object.entries(payload).filter(([_, v]) => v !== '' && v != null)
//       );
//       const { data } = await api.patch('/utilisateurs/moi', cleanPayload);
//       return data;
//     },
//     onSuccess: (data) => {
//       // Mettre à jour le cache React Query
//       queryClient.setQueryData(['profile', 'me'], data);
//       // Invalider pour forcer un re-fetch si besoin
//       queryClient.invalidateQueries({ queryKey: ['profile', 'me'] });
//     },
//   });
// };

// // Changer mon mot de passe
// export const useChangePassword = () =>
//   useMutation({
//     mutationFn: async ({ ancien_mot_de_passe, nouveau_mot_de_passe }) => {
//       await api.put('/utilisateurs/moi/mot-de-passe', {
//         ancien_mot_de_passe,
//         nouveau_mot_de_passe,
//       });
//     },
//   });



// src/hooks/useProfile.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

export const useProfile = () =>
  useQuery({
    queryKey: ['profile', 'me'],
    queryFn: async () => {
      const { data } = await api.get('/utilisateurs/moi');
      return data;
    },
    staleTime: 1000 * 60 * 5,
  });

export const useUpdateProfile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload) => {
      const cleanPayload = Object.fromEntries(
        Object.entries(payload).filter(([_, v]) => v !== '' && v != null)
      );
      const { data } = await api.patch('/utilisateurs/moi', cleanPayload);
      return data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['profile', 'me'], data);
      queryClient.invalidateQueries({ queryKey: ['profile', 'me'] });
    },
  });
};

export const useChangePassword = () =>
  useMutation({
    mutationFn: async ({ ancien_mot_de_passe, nouveau_mot_de_passe }) => {
      await api.put('/utilisateurs/moi/mot-de-passe', {
        ancien_mot_de_passe,
        nouveau_mot_de_passe,
      });
    },
  });

// ✅ Nouveau : activer / désactiver la 2FA
export const useToggle2FA = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (enabled) => {
      const { data } = await api.patch('/utilisateurs/moi', {
        deux_fa_active: enabled,
      });
      return data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['profile', 'me'], data);
    },
  });
};