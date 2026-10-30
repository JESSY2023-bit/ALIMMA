


// // src/pages/Profile.jsx
// import { useState, useEffect, useRef } from 'react';
// import { Link, useLocation } from 'react-router-dom';
// import { useForm } from 'react-hook-form';
// import { zodResolver } from '@hookform/resolvers/zod';
// import {
//   FaArrowRight,
//   FaUser,
//   FaBoxOpen,
//   FaMapMarkerAlt,
//   FaLock,
//   FaCamera,
//   FaCheckCircle,
//   FaTimesCircle,
//   FaCopy,
//   FaCheck,
//   FaShieldAlt,
// } from 'react-icons/fa';
// import { profileSchema, passwordSchema } from '../schemas/profileSchema';
// import {
//   useProfile,
//   useUpdateProfile,
//   useChangePassword,
//   useToggle2FA,
// } from '../hooks/useProfile';
// import { useAuthContext } from '../hooks/useAuthContext';

// const MENU_ITEMS = [
//   { key: 'account', label: 'Account info', icon: FaUser },
//   { key: 'orders', label: 'My order', icon: FaBoxOpen },
//   { key: 'address', label: 'My address', icon: FaMapMarkerAlt },
//   { key: 'password', label: 'Change password', icon: FaLock },
// ];

// // ✅ Utilitaire : fichier → base64
// const fileToBase64 = (file) =>
//   new Promise((resolve, reject) => {
//     const reader = new FileReader();
//     reader.readAsDataURL(file);
//     reader.onload = () => resolve(reader.result);
//     reader.onerror = reject;
//   });

// // ✅ Toggle switch réutilisable
// function ToggleSwitch({ checked, onChange, disabled }) {
//   return (
//     <button
//       type="button"
//       role="switch"
//       aria-checked={checked}
//       disabled={disabled}
//       onClick={() => onChange(!checked)}
//       className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
//         checked ? 'bg-green-500' : 'bg-gray-300'
//       } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
//     >
//       <span
//         className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
//           checked ? 'translate-x-6' : 'translate-x-1'
//         }`}
//       />
//     </button>
//   );
// }

// export default function Profile() {
//   const location = useLocation();
//   const { user: authUser, setUser } = useAuthContext();
//   const { data: profile, isLoading } = useProfile();
//   const updateProfile = useUpdateProfile();
//   const changePassword = useChangePassword();
//   const toggle2FA = useToggle2FA();

//   const [activeTab, setActiveTab] = useState(
//     new URLSearchParams(location.search).get('tab') === 'password'
//       ? 'password'
//       : 'account'
//   );

//   const [successMsg, setSuccessMsg] = useState('');
//   const [errorMsg, setErrorMsg] = useState('');
//   const [copiedField, setCopiedField] = useState(null);

//   // ✅ États pour la photo
//   const [photoPreview, setPhotoPreview] = useState(null);
//   const [photoBase64, setPhotoBase64] = useState(null);
//   const fileInputRef = useRef(null);

//   // Formulaire de profil
//   const {
//     register: registerProfile,
//     handleSubmit: handleSubmitProfile,
//     reset: resetProfile,
//     setValue: setProfileValue,
//     formState: { errors: profileErrors, isSubmitting: isSubmittingProfile },
//   } = useForm({
//     resolver: zodResolver(profileSchema),
//     defaultValues: { nom: '', email: '', telephone: '', photo_url: '' },
//   });

//   // Formulaire de mot de passe
//   const {
//     register: registerPassword,
//     handleSubmit: handleSubmitPassword,
//     reset: resetPassword,
//     formState: { errors: passwordErrors, isSubmitting: isSubmittingPassword },
//   } = useForm({
//     resolver: zodResolver(passwordSchema),
//     defaultValues: {
//       ancien_mot_de_passe: '',
//       nouveau_mot_de_passe: '',
//       confirm_password: '',
//     },
//   });

//   // Hydrater le formulaire quand le profil arrive
//   useEffect(() => {
//     if (profile) {
//       resetProfile({
//         nom: profile.nom || '',
//         email: profile.email || '',
//         telephone: profile.telephone || '',
//         photo_url: profile.photo_url || '',
//       });
//       setPhotoPreview(profile.photo_url || null);
//     }
//   }, [profile, resetProfile]);

//   // ✅ Copier dans le presse-papiers
//   const handleCopy = async (text, field) => {
//     try {
//       await navigator.clipboard.writeText(text);
//       setCopiedField(field);
//       setTimeout(() => setCopiedField(null), 2000);
//     } catch {
//       setErrorMsg('Impossible de copier.');
//     }
//   };

//   // ✅ Gestion de la sélection de fichier
//   const handleFileChange = async (e) => {
//     const file = e.target.files?.[0];
//     if (!file) return;

//     if (!file.type.startsWith('image/')) {
//       setErrorMsg('Le fichier doit être une image (JPG, PNG, GIF).');
//       return;
//     }
//     if (file.size > 5 * 1024 * 1024) {
//       setErrorMsg("L'image ne doit pas dépasser 5 Mo.");
//       return;
//     }

//     try {
//       const base64 = await fileToBase64(file);
//       setPhotoPreview(base64);
//       setPhotoBase64(base64);
//       setProfileValue('photo_url', base64, { shouldValidate: true });
//       setErrorMsg('');
//     } catch (err) {
//       setErrorMsg("Erreur lors de la lecture de l'image.");
//     }
//   };

//   // Soumission du profil
//   const onSubmitProfile = async (data) => {
//     setSuccessMsg('');
//     setErrorMsg('');
//     try {
//       const updated = await updateProfile.mutateAsync(data);
//       if (setUser) setUser(updated);
//       setPhotoBase64(null);
//       setSuccessMsg('Profil mis à jour avec succès.');
//       setTimeout(() => setSuccessMsg(''), 3000);
//     } catch (err) {
//       const msg = err.response?.data?.message || 'Erreur lors de la mise à jour.';
//       setErrorMsg(msg);
//     }
//   };

//   // Soumission du mot de passe
//   const onSubmitPassword = async (data) => {
//     setSuccessMsg('');
//     setErrorMsg('');
//     try {
//       await changePassword.mutateAsync({
//         ancien_mot_de_passe: data.ancien_mot_de_passe,
//         nouveau_mot_de_passe: data.nouveau_mot_de_passe,
//       });
//       resetPassword();
//       setSuccessMsg('Mot de passe modifié avec succès.');
//       setTimeout(() => setSuccessMsg(''), 3000);
//     } catch (err) {
//       const msg = err.response?.data?.message || 'Erreur lors du changement de mot de passe.';
//       setErrorMsg(msg);
//     }
//   };

//   // ✅ Toggle 2FA
//   const handleToggle2FA = async (enabled) => {
//     setSuccessMsg('');
//     setErrorMsg('');
//     try {
//       const updated = await toggle2FA.mutateAsync(enabled);
//       if (setUser) setUser(updated);
//       setSuccessMsg(
//         enabled
//           ? 'Double authentification activée.'
//           : 'Double authentification désactivée.'
//       );
//       setTimeout(() => setSuccessMsg(''), 3000);
//     } catch (err) {
//       const msg =
//         err.response?.data?.message ||
//         "Impossible de modifier la double authentification. Vérifiez que l'API le supporte.";
//       setErrorMsg(msg);
//     }
//   };

//   if (isLoading) {
//     return (
//       <div className="alimma-layout py-16 flex justify-center">
//         <div className="animate-pulse text-gray-400">Chargement du profil...</div>
//       </div>
//     );
//   }

//   const displayUser = profile || authUser;
//   const initial = displayUser?.nom?.charAt(0)?.toUpperCase() || 'U';

//   return (
//     <div className="alimma-layout py-8">
//       {/* Fil d'Ariane */}
//       <nav className="text-xs text-gray-500 mb-6">
//         <Link to="/" className="hover:text-primary">Home</Link>
//         <span className="mx-1">/</span>
//         <span className="text-gray-700">pages</span>
//         <span className="mx-1">/</span>
//         <span className="font-bold text-gray-800">profile</span>
//       </nav>

//       <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6">
//         {/* ============================== */}
//         {/* Sidebar                        */}
//         {/* ============================== */}
//         <aside className="bg-gray-50 rounded-lg p-5">
//           {/* Avatar cliquable pour changer la photo */}
//           <div className="flex flex-col items-center text-center mb-5">
//             <button
//               type="button"
//               onClick={() => fileInputRef.current?.click()}
//               className="relative w-32 h-32 rounded-lg bg-gray-200 flex items-center justify-center overflow-hidden mb-3 group cursor-pointer"
//               title="Cliquez pour changer la photo"
//             >
//               {photoPreview ? (
//                 <img
//                   src={photoPreview}
//                   alt={displayUser?.nom}
//                   className="w-full h-full object-cover"
//                 />
//               ) : (
//                 <span className="text-4xl font-bold text-gray-500">{initial}</span>
//               )}
//               <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
//                 <FaCamera className="text-white text-2xl" />
//               </div>
//             </button>
//             <input
//               ref={fileInputRef}
//               type="file"
//               accept="image/*"
//               onChange={handleFileChange}
//               className="hidden"
//             />

//             <h3 className="font-bold text-lg text-gray-900">
//               {displayUser?.nom || 'Utilisateur'}
//             </h3>
//             <p className="text-xs text-gray-500 mt-1">
//               {displayUser?.email || displayUser?.telephone || ''}
//             </p>
//           </div>

//           {/* Statistiques rapides */}
//           <div className="grid grid-cols-2 gap-2 mb-4">
//             <div className="bg-white rounded-md p-2 text-center">
//               <p className="text-lg font-bold text-gray-900">
//                 {displayUser?.note_moyenne || '—'}
//               </p>
//               <p className="text-[10px] uppercase text-gray-500">Note</p>
//             </div>
//             <div className="bg-white rounded-md p-2 text-center">
//               <p className="text-lg font-bold text-gray-900">
//                 {displayUser?.nb_avis || 0}
//               </p>
//               <p className="text-[10px] uppercase text-gray-500">Avis</p>
//             </div>
//           </div>

//           {/* Menu */}
//           <nav className="space-y-2">
//             {MENU_ITEMS.map((item) => {
//               const Icon = item.icon;
//               const isActive = activeTab === item.key;
//               return (
//                 <button
//                   key={item.key}
//                   onClick={() => {
//                     setActiveTab(item.key);
//                     setSuccessMsg('');
//                     setErrorMsg('');
//                   }}
//                   className={`w-full flex items-center justify-between px-4 py-3 rounded-md text-sm font-medium transition ${
//                     isActive
//                       ? 'bg-primary text-white'
//                       : 'bg-white text-gray-700 hover:bg-gray-100'
//                   }`}
//                 >
//                   <span className="flex items-center gap-3">
//                     <Icon className="text-xs" />
//                     {item.label}
//                   </span>
//                   <FaArrowRight className="text-xs opacity-70" />
//                 </button>
//               );
//             })}
//           </nav>
//         </aside>

//         {/* ============================== */}
//         {/* Contenu principal              */}
//         {/* ============================== */}
//         <main className="bg-white rounded-lg p-6">
//           {successMsg && (
//             <div className="mb-4 p-3 bg-green-50 text-green-700 text-sm rounded border border-green-200 flex items-center gap-2">
//               <FaCheckCircle /> {successMsg}
//             </div>
//           )}
//           {errorMsg && (
//             <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded border border-red-200 flex items-center gap-2">
//               <FaTimesCircle /> {errorMsg}
//             </div>
//           )}

//           {/* Onglet "Account info" */}
//           {activeTab === 'account' && (
//             <>
//               <h2 className="text-xl font-bold text-gray-900 mb-6">Account Info</h2>

//               <form onSubmit={handleSubmitProfile(onSubmitProfile)} className="space-y-5">
//                 <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
//                   {/* Nom complet */}
//                   <div>
//                     <label className="block text-sm text-gray-700 mb-1">
//                       Nom complet <span className="text-red-500">*</span>
//                     </label>
//                     <input
//                       type="text"
//                       {...registerProfile('nom')}
//                       className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
//                     />
//                     {profileErrors.nom && (
//                       <p className="text-xs text-red-500 mt-1">{profileErrors.nom.message}</p>
//                     )}
//                   </div>

//                   {/* Téléphone */}
//                   <div>
//                     <label className="block text-sm text-gray-700 mb-1">
//                       Phone Number (Optional)
//                     </label>
//                     <input
//                       type="text"
//                       placeholder="+237XXXXXXXXX"
//                       {...registerProfile('telephone')}
//                       className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
//                     />
//                     {profileErrors.telephone && (
//                       <p className="text-xs text-red-500 mt-1">{profileErrors.telephone.message}</p>
//                     )}
//                   </div>
//                 </div>

//                 {/* Email */}
//                 <div>
//                   <label className="block text-sm text-gray-700 mb-1">
//                     Email Address <span className="text-red-500">*</span>
//                   </label>
//                   <input
//                     type="email"
//                     {...registerProfile('email')}
//                     className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
//                   />
//                   {profileErrors.email && (
//                     <p className="text-xs text-red-500 mt-1">{profileErrors.email.message}</p>
//                   )}
//                 </div>

//                 <input type="hidden" {...registerProfile('photo_url')} />

//                 {/* Bouton pour changer la photo */}
//                 <div>
//                   <label className="block text-sm text-gray-700 mb-2">Photo de profil</label>
//                   <button
//                     type="button"
//                     onClick={() => fileInputRef.current?.click()}
//                     className="flex items-center gap-3 border border-dashed border-gray-300 rounded-md px-4 py-3 text-sm text-gray-600 hover:border-primary hover:text-primary transition w-full"
//                   >
//                     <FaCamera />
//                     {photoBase64 ? 'Changer la photo sélectionnée' : 'Sélectionner une nouvelle photo'}
//                   </button>
//                   <p className="text-xs text-gray-500 mt-1">
//                     JPG, PNG ou GIF. Taille max : 5 Mo.
//                   </p>
//                   {profileErrors.photo_url && (
//                     <p className="text-xs text-red-500 mt-1">{profileErrors.photo_url.message}</p>
//                   )}
//                 </div>

//                 <div>
//                   <button
//                     type="submit"
//                     disabled={isSubmittingProfile}
//                     className="bg-primary text-white text-sm font-bold uppercase px-6 py-2.5 rounded-md hover:bg-primary-hover transition disabled:opacity-50"
//                   >
//                     {isSubmittingProfile ? 'Enregistrement...' : 'Save'}
//                   </button>
//                 </div>
//               </form>

//               {/* =========================================== */}
//               {/* Informations du compte (sans ID ni rôle)    */}
//               {/* =========================================== */}
//               <div className="mt-10 pt-6 border-t border-gray-200">
//                 <h3 className="text-sm font-bold text-gray-900 uppercase mb-4">
//                   Informations du compte
//                 </h3>

//                 <dl className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
//                   {/* Points de parrainage */}
//                   <div>
//                     <dt className="text-xs text-gray-500 uppercase">Points de parrainage</dt>
//                     <dd className="text-gray-900 font-medium">
//                       {displayUser?.points_parrainage ?? 0}
//                     </dd>
//                   </div>

//                   {/* Code de parrainage (avec copie) */}
//                   <div>
//                     <dt className="text-xs text-gray-500 uppercase">Code de parrainage</dt>
//                     <dd className="flex items-center gap-2">
//                       <span className="text-gray-900 font-mono">
//                         {displayUser?.code_parrainage ?? '—'}
//                       </span>
//                       {displayUser?.code_parrainage && (
//                         <button
//                           type="button"
//                           onClick={() =>
//                             handleCopy(displayUser.code_parrainage, 'code_parrainage')
//                           }
//                           className="text-gray-400 hover:text-primary transition"
//                           title="Copier le code"
//                         >
//                           {copiedField === 'code_parrainage' ? (
//                             <FaCheck className="text-green-500 text-xs" />
//                           ) : (
//                             <FaCopy className="text-xs" />
//                           )}
//                         </button>
//                       )}
//                     </dd>
//                   </div>

//                   {/* Double authentification (2FA) */}
//                   <div className="md:col-span-2">
//                     <dt className="text-xs text-gray-500 uppercase mb-2 flex items-center gap-2">
//                       <FaShieldAlt /> Double authentification (2FA)
//                     </dt>
//                     <dd className="flex items-center justify-between bg-gray-50 rounded-md p-3">
//                       <div>
//                         <p className="text-sm font-medium text-gray-900">
//                           {displayUser?.deux_fa_active ? 'Activée' : 'Désactivée'}
//                         </p>
//                         <p className="text-xs text-gray-500 mt-0.5">
//                           {displayUser?.deux_fa_active
//                             ? 'Un code sera demandé à chaque connexion.'
//                             : 'Activez la 2FA pour sécuriser votre compte.'}
//                         </p>
//                       </div>
//                       <ToggleSwitch
//                         checked={!!displayUser?.deux_fa_active}
//                         onChange={handleToggle2FA}
//                         disabled={toggle2FA.isPending}
//                       />
//                     </dd>
//                   </div>

//                   {/* Dernière connexion */}
//                   <div>
//                     <dt className="text-xs text-gray-500 uppercase">Dernière connexion</dt>
//                     <dd className="text-gray-900 font-medium">
//                       {displayUser?.derniere_connexion
//                         ? new Date(displayUser.derniere_connexion).toLocaleString('fr-FR')
//                         : '—'}
//                     </dd>
//                   </div>

//                   {/* Date d'inscription */}
//                   <div>
//                     <dt className="text-xs text-gray-500 uppercase">Date d'inscription</dt>
//                     <dd className="text-gray-900 font-medium">
//                       {displayUser?.date_inscription
//                         ? new Date(displayUser.date_inscription).toLocaleDateString('fr-FR')
//                         : '—'}
//                     </dd>
//                   </div>

//                   {/* Note moyenne */}
//                   <div>
//                     <dt className="text-xs text-gray-500 uppercase">Note moyenne</dt>
//                     <dd className="text-gray-900 font-medium">
//                       {displayUser?.note_moyenne ?? '—'} ({displayUser?.nb_avis ?? 0} avis)
//                     </dd>
//                   </div>
//                 </dl>
//               </div>
//             </>
//           )}

//           {/* Onglet "Change password" */}
//           {activeTab === 'password' && (
//             <>
//               <h2 className="text-xl font-bold text-gray-900 mb-6">Change Password</h2>
//               <form onSubmit={handleSubmitPassword(onSubmitPassword)} className="space-y-5 max-w-md">
//                 <div>
//                   <label className="block text-sm text-gray-700 mb-1">
//                     Ancien mot de passe <span className="text-red-500">*</span>
//                   </label>
//                   <input
//                     type="password"
//                     {...registerPassword('ancien_mot_de_passe')}
//                     className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
//                   />
//                   {passwordErrors.ancien_mot_de_passe && (
//                     <p className="text-xs text-red-500 mt-1">
//                       {passwordErrors.ancien_mot_de_passe.message}
//                     </p>
//                   )}
//                 </div>

//                 <div>
//                   <label className="block text-sm text-gray-700 mb-1">
//                     Nouveau mot de passe <span className="text-red-500">*</span>
//                   </label>
//                   <input
//                     type="password"
//                     {...registerPassword('nouveau_mot_de_passe')}
//                     className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
//                   />
//                   {passwordErrors.nouveau_mot_de_passe && (
//                     <p className="text-xs text-red-500 mt-1">
//                       {passwordErrors.nouveau_mot_de_passe.message}
//                     </p>
//                   )}
//                 </div>

//                 <div>
//                   <label className="block text-sm text-gray-700 mb-1">
//                     Confirmer le mot de passe <span className="text-red-500">*</span>
//                   </label>
//                   <input
//                     type="password"
//                     {...registerPassword('confirm_password')}
//                     className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
//                   />
//                   {passwordErrors.confirm_password && (
//                     <p className="text-xs text-red-500 mt-1">
//                       {passwordErrors.confirm_password.message}
//                     </p>
//                   )}
//                 </div>

//                 <div>
//                   <button
//                     type="submit"
//                     disabled={isSubmittingPassword}
//                     className="bg-primary text-white text-sm font-bold uppercase px-6 py-2.5 rounded-md hover:bg-primary-hover transition disabled:opacity-50"
//                   >
//                     {isSubmittingPassword ? 'Modification...' : 'Change Password'}
//                   </button>
//                 </div>
//               </form>
//             </>
//           )}

//           {(activeTab === 'orders' || activeTab === 'address') && (
//             <div className="text-center py-16 text-gray-500">
//               <p className="text-sm">Cette section sera bientôt disponible.</p>
//             </div>
//           )}
//         </main>
//       </div>
//     </div>
//   );
// }







// src/pages/Profile.jsx
import { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  FaArrowRight,
  FaUser,
  FaBoxOpen,
  FaMapMarkerAlt,
  FaLock,
  FaCamera,
  FaCheckCircle,
  FaTimesCircle,
  FaCopy,
  FaCheck,
  FaShieldAlt,
} from 'react-icons/fa';
import { profileSchema, passwordSchema } from '../schemas/profileSchema';
import {
  useProfile,
  useUpdateProfile,
  useChangePassword,
  useToggle2FA,
} from '../hooks/useProfile';
import { useAuthContext } from '../hooks/useAuthContext';

const MENU_ITEMS = [
  { key: 'account', label: 'Informations du compte', icon: FaUser },
  { key: 'orders', label: 'Mes commandes', icon: FaBoxOpen },
  { key: 'address', label: 'Mon adresse', icon: FaMapMarkerAlt },
  { key: 'password', label: 'Changer le mot de passe', icon: FaLock },
];

// ✅ Utilitaire : fichier → base64
const fileToBase64 = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
  });

// ✅ Toggle switch réutilisable
function ToggleSwitch({ checked, onChange, disabled }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        checked ? 'bg-green-500' : 'bg-gray-300'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          checked ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  );
}

export default function Profile() {
  const location = useLocation();
  const { user: authUser, setUser } = useAuthContext();
  const { data: profile, isLoading } = useProfile();
  const updateProfile = useUpdateProfile();
  const changePassword = useChangePassword();
  const toggle2FA = useToggle2FA();

  const [activeTab, setActiveTab] = useState(
    new URLSearchParams(location.search).get('tab') === 'password'
      ? 'password'
      : 'account'
  );

  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [copiedField, setCopiedField] = useState(null);

  // ✅ États pour la photo
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoBase64, setPhotoBase64] = useState(null);
  const fileInputRef = useRef(null);

  // Formulaire de profil
  const {
    register: registerProfile,
    handleSubmit: handleSubmitProfile,
    reset: resetProfile,
    setValue: setProfileValue,
    formState: { errors: profileErrors, isSubmitting: isSubmittingProfile },
  } = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: { nom: '', email: '', telephone: '', photo_url: '' },
  });

  // Formulaire de mot de passe
  const {
    register: registerPassword,
    handleSubmit: handleSubmitPassword,
    reset: resetPassword,
    formState: { errors: passwordErrors, isSubmitting: isSubmittingPassword },
  } = useForm({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      ancien_mot_de_passe: '',
      nouveau_mot_de_passe: '',
      confirm_password: '',
    },
  });

  // Hydrater le formulaire quand le profil arrive
  useEffect(() => {
    if (profile) {
      resetProfile({
        nom: profile.nom || '',
        email: profile.email || '',
        telephone: profile.telephone || '',
        photo_url: profile.photo_url || '',
      });
      setPhotoPreview(profile.photo_url || null);
    }
  }, [profile, resetProfile]);

  // ✅ Copier dans le presse-papiers
  const handleCopy = async (text, field) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch {
      setErrorMsg('Impossible de copier le texte.');
    }
  };

  // ✅ Gestion de la sélection de fichier
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setErrorMsg('Le fichier doit être une image (JPG, PNG, GIF).');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg("L'image ne doit pas dépasser 5 Mo.");
      return;
    }

    try {
      const base64 = await fileToBase64(file);
      setPhotoPreview(base64);
      setPhotoBase64(base64);
      setProfileValue('photo_url', base64, { shouldValidate: true });
      setErrorMsg('');
    } catch (err) {
      setErrorMsg("Erreur lors de la lecture de l'image.");
    }
  };

  // Soumission du profil
  const onSubmitProfile = async (data) => {
    setSuccessMsg('');
    setErrorMsg('');
    try {
      const updated = await updateProfile.mutateAsync(data);
      if (setUser) setUser(updated);
      setPhotoBase64(null);
      setSuccessMsg('Profil mis à jour avec succès.');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      const msg = err.response?.data?.message || 'Erreur lors de la mise à jour du profil.';
      setErrorMsg(msg);
    }
  };

  // Soumission du mot de passe
  const onSubmitPassword = async (data) => {
    setSuccessMsg('');
    setErrorMsg('');
    try {
      await changePassword.mutateAsync({
        ancien_mot_de_passe: data.ancien_mot_de_passe,
        nouveau_mot_de_passe: data.nouveau_mot_de_passe,
      });
      resetPassword();
      setSuccessMsg('Mot de passe modifié avec succès.');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      const msg = err.response?.data?.message || 'Erreur lors du changement de mot de passe.';
      setErrorMsg(msg);
    }
  };

  // ✅ Toggle 2FA
  const handleToggle2FA = async (enabled) => {
    setSuccessMsg('');
    setErrorMsg('');
    try {
      const updated = await toggle2FA.mutateAsync(enabled);
      if (setUser) setUser(updated);
      setSuccessMsg(
        enabled
          ? 'Double authentification activée.'
          : 'Double authentification désactivée.'
      );
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      const msg =
        err.response?.data?.message ||
        "Impossible de modifier la double authentification. Vérifiez que l'API la prend en charge.";
      setErrorMsg(msg);
    }
  };

  if (isLoading) {
    return (
      <div className="alimma-layout py-16 flex justify-center">
        <div className="animate-pulse text-gray-400">Chargement du profil...</div>
      </div>
    );
  }

  const displayUser = profile || authUser;
  const initial = displayUser?.nom?.charAt(0)?.toUpperCase() || 'U';

  return (
    <div className="alimma-layout py-8">
      {/* Fil d'Ariane */}
      <nav className="text-xs text-gray-500 mb-6">
        <Link to="/" className="hover:text-primary">Accueil</Link>
        <span className="mx-1">/</span>
        <span className="text-gray-700">pages</span>
        <span className="mx-1">/</span>
        <span className="font-bold text-gray-800">profil</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6">
        {/* ============================== */}
        {/* Barre latérale                 */}
        {/* ============================== */}
        <aside className="bg-gray-50 rounded-lg p-5">
          {/* Avatar cliquable pour changer la photo */}
          <div className="flex flex-col items-center text-center mb-5">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="relative w-32 h-32 rounded-lg bg-gray-200 flex items-center justify-center overflow-hidden mb-3 group cursor-pointer"
              title="Cliquez pour changer la photo"
            >
              {photoPreview ? (
                <img
                  src={photoPreview}
                  alt={displayUser?.nom}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-4xl font-bold text-gray-500">{initial}</span>
              )}
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                <FaCamera className="text-white text-2xl" />
              </div>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />

            <h3 className="font-bold text-lg text-gray-900">
              {displayUser?.nom || 'Utilisateur'}
            </h3>
            <p className="text-xs text-gray-500 mt-1">
              {displayUser?.email || displayUser?.telephone || ''}
            </p>
          </div>

          {/* Statistiques rapides */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            <div className="bg-white rounded-md p-2 text-center">
              <p className="text-lg font-bold text-gray-900">
                {displayUser?.note_moyenne || '—'}
              </p>
              <p className="text-[10px] uppercase text-gray-500">Note</p>
            </div>
            <div className="bg-white rounded-md p-2 text-center">
              <p className="text-lg font-bold text-gray-900">
                {displayUser?.nb_avis || 0}
              </p>
              <p className="text-[10px] uppercase text-gray-500">Avis</p>
            </div>
          </div>

          {/* Menu */}
          <nav className="space-y-2">
            {MENU_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.key;
              return (
                <button
                  key={item.key}
                  onClick={() => {
                    setActiveTab(item.key);
                    setSuccessMsg('');
                    setErrorMsg('');
                  }}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-md text-sm font-medium transition ${
                    isActive
                      ? 'bg-primary text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <span className="flex items-center gap-3">
                    <Icon className="text-xs" />
                    {item.label}
                  </span>
                  <FaArrowRight className="text-xs opacity-70" />
                </button>
              );
            })}
          </nav>
        </aside>

        {/* ============================== */}
        {/* Contenu principal              */}
        {/* ============================== */}
        <main className="bg-white rounded-lg p-6">
          {successMsg && (
            <div className="mb-4 p-3 bg-green-50 text-green-700 text-sm rounded border border-green-200 flex items-center gap-2">
              <FaCheckCircle /> {successMsg}
            </div>
          )}
          {errorMsg && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded border border-red-200 flex items-center gap-2">
              <FaTimesCircle /> {errorMsg}
            </div>
          )}

          {/* Onglet "Informations du compte" */}
          {activeTab === 'account' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                Informations du compte
              </h2>

              <form onSubmit={handleSubmitProfile(onSubmitProfile)} className="space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {/* Nom complet */}
                  <div>
                    <label className="block text-sm text-gray-700 mb-1">
                      Nom complet <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      {...registerProfile('nom')}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
                    />
                    {profileErrors.nom && (
                      <p className="text-xs text-red-500 mt-1">{profileErrors.nom.message}</p>
                    )}
                  </div>

                  {/* Téléphone */}
                  <div>
                    <label className="block text-sm text-gray-700 mb-1">
                      Numéro de téléphone (facultatif)
                    </label>
                    <input
                      type="text"
                      placeholder="+237XXXXXXXXX"
                      {...registerProfile('telephone')}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
                    />
                    {profileErrors.telephone && (
                      <p className="text-xs text-red-500 mt-1">{profileErrors.telephone.message}</p>
                    )}
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm text-gray-700 mb-1">
                    Adresse e-mail <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    {...registerProfile('email')}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
                  />
                  {profileErrors.email && (
                    <p className="text-xs text-red-500 mt-1">{profileErrors.email.message}</p>
                  )}
                </div>

                <input type="hidden" {...registerProfile('photo_url')} />

                {/* Bouton pour changer la photo */}
                <div>
                  <label className="block text-sm text-gray-700 mb-2">
                    Photo de profil
                  </label>
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center gap-3 border border-dashed border-gray-300 rounded-md px-4 py-3 text-sm text-gray-600 hover:border-primary hover:text-primary transition w-full"
                  >
                    <FaCamera />
                    {photoBase64
                      ? 'Changer la photo sélectionnée'
                      : 'Sélectionner une nouvelle photo'}
                  </button>
                  <p className="text-xs text-gray-500 mt-1">
                    JPG, PNG ou GIF. Taille maximale : 5 Mo.
                  </p>
                  {profileErrors.photo_url && (
                    <p className="text-xs text-red-500 mt-1">{profileErrors.photo_url.message}</p>
                  )}
                </div>

                <div>
                  <button
                    type="submit"
                    disabled={isSubmittingProfile}
                    className="bg-primary text-white text-sm font-bold uppercase px-6 py-2.5 rounded-md hover:bg-primary-hover transition disabled:opacity-50"
                  >
                    {isSubmittingProfile ? 'Enregistrement...' : 'Enregistrer'}
                  </button>
                </div>
              </form>

              {/* =========================================== */}
              {/* Informations du compte                      */}
              {/* =========================================== */}
              <div className="mt-10 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-bold text-gray-900 uppercase mb-4">
                  Informations du compte
                </h3>

                <dl className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  {/* Points de parrainage */}
                  <div>
                    <dt className="text-xs text-gray-500 uppercase">Points de parrainage</dt>
                    <dd className="text-gray-900 font-medium">
                      {displayUser?.points_parrainage ?? 0}
                    </dd>
                  </div>

                  {/* Code de parrainage (avec copie) */}
                  <div>
                    <dt className="text-xs text-gray-500 uppercase">Code de parrainage</dt>
                    <dd className="flex items-center gap-2">
                      <span className="text-gray-900 font-mono">
                        {displayUser?.code_parrainage ?? '—'}
                      </span>
                      {displayUser?.code_parrainage && (
                        <button
                          type="button"
                          onClick={() =>
                            handleCopy(displayUser.code_parrainage, 'code_parrainage')
                          }
                          className="text-gray-400 hover:text-primary transition"
                          title="Copier le code"
                        >
                          {copiedField === 'code_parrainage' ? (
                            <FaCheck className="text-green-500 text-xs" />
                          ) : (
                            <FaCopy className="text-xs" />
                          )}
                        </button>
                      )}
                    </dd>
                  </div>

                  {/* Double authentification (2FA) */}
                  <div className="md:col-span-2">
                    <dt className="text-xs text-gray-500 uppercase mb-2 flex items-center gap-2">
                      <FaShieldAlt /> Double authentification (2FA)
                    </dt>
                    <dd className="flex items-center justify-between bg-gray-50 rounded-md p-3">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {displayUser?.deux_fa_active ? 'Activée' : 'Désactivée'}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {displayUser?.deux_fa_active
                            ? 'Un code sera demandé à chaque connexion.'
                            : 'Activez la 2FA pour sécuriser votre compte.'}
                        </p>
                      </div>
                      <ToggleSwitch
                        checked={!!displayUser?.deux_fa_active}
                        onChange={handleToggle2FA}
                        disabled={toggle2FA.isPending}
                      />
                    </dd>
                  </div>

                  {/* Dernière connexion */}
                  <div>
                    <dt className="text-xs text-gray-500 uppercase">Dernière connexion</dt>
                    <dd className="text-gray-900 font-medium">
                      {displayUser?.derniere_connexion
                        ? new Date(displayUser.derniere_connexion).toLocaleString('fr-FR')
                        : '—'}
                    </dd>
                  </div>

                  {/* Date d'inscription */}
                  <div>
                    <dt className="text-xs text-gray-500 uppercase">Date d'inscription</dt>
                    <dd className="text-gray-900 font-medium">
                      {displayUser?.date_inscription
                        ? new Date(displayUser.date_inscription).toLocaleDateString('fr-FR')
                        : '—'}
                    </dd>
                  </div>

                  {/* Note moyenne */}
                  <div>
                    <dt className="text-xs text-gray-500 uppercase">Note moyenne</dt>
                    <dd className="text-gray-900 font-medium">
                      {displayUser?.note_moyenne ?? '—'} ({displayUser?.nb_avis ?? 0} avis)
                    </dd>
                  </div>
                </dl>
              </div>
            </>
          )}

          {/* Onglet "Changer le mot de passe" */}
          {activeTab === 'password' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                Changer le mot de passe
              </h2>
              <form
                onSubmit={handleSubmitPassword(onSubmitPassword)}
                className="space-y-5 max-w-md"
              >
                <div>
                  <label className="block text-sm text-gray-700 mb-1">
                    Ancien mot de passe <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    {...registerPassword('ancien_mot_de_passe')}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
                  />
                  {passwordErrors.ancien_mot_de_passe && (
                    <p className="text-xs text-red-500 mt-1">
                      {passwordErrors.ancien_mot_de_passe.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm text-gray-700 mb-1">
                    Nouveau mot de passe <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    {...registerPassword('nouveau_mot_de_passe')}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
                  />
                  {passwordErrors.nouveau_mot_de_passe && (
                    <p className="text-xs text-red-500 mt-1">
                      {passwordErrors.nouveau_mot_de_passe.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm text-gray-700 mb-1">
                    Confirmer le mot de passe <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    {...registerPassword('confirm_password')}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary"
                  />
                  {passwordErrors.confirm_password && (
                    <p className="text-xs text-red-500 mt-1">
                      {passwordErrors.confirm_password.message}
                    </p>
                  )}
                </div>

                <div>
                  <button
                    type="submit"
                    disabled={isSubmittingPassword}
                    className="bg-primary text-white text-sm font-bold uppercase px-6 py-2.5 rounded-md hover:bg-primary-hover transition disabled:opacity-50"
                  >
                    {isSubmittingPassword
                      ? 'Modification en cours...'
                      : 'Changer le mot de passe'}
                  </button>
                </div>
              </form>
            </>
          )}

          {(activeTab === 'orders' || activeTab === 'address') && (
            <div className="text-center py-16 text-gray-500">
              <p className="text-sm">Cette section sera bientôt disponible.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}