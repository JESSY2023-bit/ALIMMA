
// src/components/layout/Navbar.jsx
import { useState, useRef, useEffect } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import {
  FaChevronDown,
  FaHeart,
  FaShoppingCart,
  FaBars,
  FaTimes,
  FaExchangeAlt,
  FaEye,
  FaUser,
  FaSignOutAlt,
  FaBoxOpen,
  FaCog,
} from "react-icons/fa";

import { useAuthContext } from "../../hooks/useAuthContext";
import { useLogout } from "../../hooks/useAuth";
import ConfirmModal from "../ui/confirmModal";

const navItems = [
  { label: "HOMES", to: "/" },
  { label: "PAGES", to: "/pages" },
  { label: "PRODUCTS", to: "/products" },
  { label: "CONTACT", to: "/contact" },
];

// ✅ Avatar réutilisable (photo ou initiale)
function UserAvatar({ user, size = "md", onClick }) {
  const sizeClasses = {
    sm: "w-9 h-9 xl:w-10 xl:h-10 text-sm",
    md: "w-10 h-10 text-sm",
    lg: "w-12 h-12 text-base",
  };

  const initial = user?.nom?.charAt(0)?.toUpperCase();

  return (
    <div
      onClick={onClick}
      className={`${sizeClasses[size]} rounded-full bg-primary flex items-center justify-center text-white font-bold shrink-0 overflow-hidden`}
    >
      {user?.photo_url ? (
        <img
          src={user.photo_url}
          alt={user.nom || "Utilisateur"}
          className="w-full h-full object-cover"
        />
      ) : (
        initial || <FaUser />
      )}
    </div>
  );
}

// ✅ Squelette de chargement (évite le flash "CONNEXION")
function LoadingSkeleton() {
  return (
    <div className="flex items-center gap-2 ml-1 shrink-0">
      <div className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-200 animate-pulse"></div>
      <div className="flex flex-col gap-1">
        <div className="w-16 h-2 bg-gray-200 rounded animate-pulse"></div>
        <div className="w-20 h-3 bg-gray-200 rounded animate-pulse"></div>
      </div>
    </div>
  );
}

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [logoutModalOpen, setLogoutModalOpen] = useState(false);
  const userMenuRef = useRef(null);

  const { user, isAuthenticated, isLoading, logout } = useAuthContext();
  const logoutMutation = useLogout();
  const navigate = useNavigate();

  // Ferme le menu au clic ailleurs
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const askLogout = () => {
    setUserMenuOpen(false);
    setLogoutModalOpen(true);
  };

  const confirmLogout = () => {
    logoutMutation.mutate(undefined, {
      onSettled: () => {
        logout();
        setLogoutModalOpen(false);
        navigate("/login", { replace: true });
      },
    });
  };

  return (
    <div className="w-full bg-white border-b border-gray-100">
      <div className="alimma-layout py-4 flex items-center justify-between gap-2">
        {/* ================================ */}
        {/* Logo + Navigation                 */}
        {/* ================================ */}
        <div className="flex items-center gap-4 xl:gap-8 shrink-0">
          <Link
            to="/"
            className="flex items-center gap-3 font-display text-2xl xl:text-3xl font-black tracking-tight shrink-0 text-gray-900"
          >
            <img
              src="/logo1.png"
              alt="ALIMMA Logo"
              className="w-10 h-10 xl:w-11 xl:h-11 object-contain rounded-xl"
            />
            <span>
              ALIM<span className="text-primary">MA</span>
            </span>
          </Link>

          <nav className="hidden lg:flex items-center gap-4 xl:gap-6">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-1 text-xs xl:text-sm font-bold uppercase tracking-wider transition ${
                    isActive ? "text-primary" : "text-gray-800 text-primary-hover"
                  }`
                }
              >
                {item.label}
                <FaChevronDown className="text-[9px] text-gray-500" />
              </NavLink>
            ))}
          </nav>
        </div>

        {/* ================================ */}
        {/* Bloc d'actions à droite           */}
        {/* ================================ */}
        <div className="hidden lg:flex items-center gap-2 xl:gap-3 shrink-0">
          {/* Icônes circulaires */}
          <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
            <FaExchangeAlt className="text-sm" />
          </button>

          <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
            <FaHeart className="text-sm" />
          </button>

          <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
            <FaEye className="text-sm" />
          </button>

          {/* =================================== */}
          {/* Zone utilisateur                    */}
          {/* =================================== */}
          {isLoading ? (
            <LoadingSkeleton />
          ) : isAuthenticated ? (
            <div className="relative ml-1 shrink-0" ref={userMenuRef}>
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 cursor-pointer"
              >
                {/* ✅ Avatar avec photo ou initiale */}
                <UserAvatar user={user} size="sm" />

                <div className="text-left leading-tight">
                  <p className="text-[10px] xl:text-xs uppercase font-bold text-gray-400 tracking-wider">
                    BIENVENU
                  </p>
                  <span className="font-extrabold uppercase text-gray-800 text-xs xl:text-sm flex items-center gap-1">
                    {user?.nom?.split(" ")[0] || "COMPTE"}
                    <FaChevronDown
                      className={`text-[9px] transition-transform ${
                        userMenuOpen ? "rotate-180" : ""
                      }`}
                    />
                  </span>
                </div>
              </button>

              {/* Dropdown */}
              {userMenuOpen && (
                <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50">
                  {/* En-tête avec avatar */}
                  <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-3">
                    <UserAvatar user={user} size="md" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-bold text-gray-800 truncate">
                        {user?.nom || "Utilisateur"}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {user?.email || user?.telephone || ""}
                      </p>
                      {user?.role && (
                        <span className="inline-block mt-1 px-2 py-0.5 bg-primary/10 text-primary text-[10px] font-bold uppercase rounded">
                          {user.role}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Liens */}
                  <Link
                    to="/profile"
                    onClick={() => setUserMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
                  >
                    <FaUser className="text-xs text-gray-400" />
                    Mon compte
                  </Link>

                  <Link
                    to="/mes-commandes"
                    onClick={() => setUserMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
                  >
                    <FaBoxOpen className="text-xs text-gray-400" />
                    Mes commandes
                  </Link>

                  <Link
                    to="/favoris"
                    onClick={() => setUserMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
                  >
                    <FaHeart className="text-xs text-gray-400" />
                    Mes favoris
                  </Link>

                  <Link
                    to="/parametres"
                    onClick={() => setUserMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
                  >
                    <FaCog className="text-xs text-gray-400" />
                    Paramètres
                  </Link>

                  <div className="border-t border-gray-100 my-1"></div>

                  <button
                    onClick={askLogout}
                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 transition"
                  >
                    <FaSignOutAlt className="text-xs" />
                    Se déconnecter
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-left leading-tight ml-1 shrink-0">
              <p className="text-[10px] xl:text-xs uppercase font-bold text-gray-400 tracking-wider">
                BIENVENU
              </p>
              <div className="flex items-center gap-1.5 font-extrabold uppercase text-gray-800 text-xs xl:text-sm">
                <Link
                  to="/login"
                  className="text-primary-hover transition whitespace-nowrap"
                >
                  CONNEXION
                </Link>
                <span className="text-gray-300 font-normal">/</span>
                <Link
                  to="/register"
                  className="text-primary-hover transition whitespace-nowrap"
                >
                  INSCRIPTION
                </Link>
              </div>
            </div>
          )}

          {/* Panier */}
          <div className="flex items-center gap-2 ml-1 xl:ml-3 shrink-0">
            <div className="relative shrink-0">
              <div className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600">
                <FaShoppingCart className="text-sm" />
              </div>
              <span className="badge-primary absolute -top-1 -right-1 text-[10px] xl:text-xs w-5 h-5 border-2 border-white">
                5
              </span>
            </div>

            <div className="flex flex-col justify-center text-left leading-tight shrink-0">
              <span className="text-[10px] xl:text-xs uppercase font-bold text-gray-400 tracking-wider mb-0.5">
                PANIER
              </span>
              <span className="font-extrabold text-gray-900 whitespace-nowrap text-xs xl:text-sm">
                FCFA 1,689.00
              </span>
            </div>
          </div>
        </div>

        {/* Bouton mobile */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="lg:hidden p-2 text-2xl text-gray-800"
        >
          {mobileOpen ? <FaTimes /> : <FaBars />}
        </button>
      </div>

      {/* ================================ */}
      {/* Menu Mobile                      */}
      {/* ================================ */}
      {mobileOpen && (
        <div className="lg:hidden bg-white border-t border-gray-200 px-4 py-3">
          <nav className="flex flex-col gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setMobileOpen(false)}
                className="py-2 text-sm font-bold uppercase text-gray-800"
              >
                {item.label}
              </NavLink>
            ))}

            <div className="border-t border-gray-100 pt-3 mt-2">
              {isLoading ? (
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-gray-200 animate-pulse"></div>
                  <div className="flex flex-col gap-1">
                    <div className="w-24 h-3 bg-gray-200 rounded animate-pulse"></div>
                    <div className="w-32 h-2 bg-gray-200 rounded animate-pulse"></div>
                  </div>
                </div>
              ) : isAuthenticated ? (
                <>
                  <div className="flex items-center gap-3 mb-3">
                    {/* ✅ Avatar avec photo dans le menu mobile */}
                    <UserAvatar user={user} size="md" />
                    <div className="min-w-0">
                      <p className="text-sm font-bold text-gray-800 truncate">
                        {user?.nom}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {user?.email || user?.telephone}
                      </p>
                    </div>
                  </div>

                  <Link
                    to="/profile"
                    onClick={() => setMobileOpen(false)}
                    className="block py-2 text-sm font-bold uppercase text-gray-800"
                  >
                    Mon compte
                  </Link>
                  <Link
                    to="/mes-commandes"
                    onClick={() => setMobileOpen(false)}
                    className="block py-2 text-sm font-bold uppercase text-gray-800"
                  >
                    Mes commandes
                  </Link>
                  <Link
                    to="/favoris"
                    onClick={() => setMobileOpen(false)}
                    className="block py-2 text-sm font-bold uppercase text-gray-800"
                  >
                    Mes favoris
                  </Link>
                  <Link
                    to="/parametres"
                    onClick={() => setMobileOpen(false)}
                    className="block py-2 text-sm font-bold uppercase text-gray-800"
                  >
                    Paramètres
                  </Link>
                  <button
                    onClick={() => {
                      setMobileOpen(false);
                      setLogoutModalOpen(true);
                    }}
                    className="block py-2 text-sm font-bold uppercase text-red-500"
                  >
                    Se déconnecter
                  </button>
                </>
              ) : (
                <div className="flex flex-col gap-1">
                  <Link
                    to="/login"
                    onClick={() => setMobileOpen(false)}
                    className="block py-2 text-sm font-bold uppercase text-gray-800 hover:text-primary transition"
                  >
                    Connexion
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setMobileOpen(false)}
                    className="block py-2 text-sm font-bold uppercase text-primary"
                  >
                    Inscription
                  </Link>
                </div>
              )}
            </div>
          </nav>
        </div>
      )}

      {/* ================================ */}
      {/* Modal de confirmation déconnexion */}
      {/* ================================ */}
      <ConfirmModal
        isOpen={logoutModalOpen}
        title="Se déconnecter ?"
        message="Voulez-vous vraiment vous déconnecter de votre compte ALIMMA ?"
        confirmLabel="Oui, me déconnecter"
        cancelLabel="Annuler"
        onConfirm={confirmLogout}
        onCancel={() => setLogoutModalOpen(false)}
        isPending={logoutMutation.isPending}
        variant="danger"
      />
    </div>
  );
}



// // src/components/layout/Navbar.jsx
// import { useState, useRef, useEffect } from "react";
// import { Link, NavLink, useNavigate } from "react-router-dom";
// import { useLingui, Trans } from "@lingui/react/macro";
// import {
//   FaChevronDown,
//   FaHeart,
//   FaShoppingCart,
//   FaBars,
//   FaTimes,
//   FaExchangeAlt,
//   FaEye,
//   FaUser,
//   FaSignOutAlt,
//   FaBoxOpen,
//   FaCog,
// } from "react-icons/fa";

// import { useAuthContext } from "../../hooks/useAuthContext";
// import { useLogout } from "../../hooks/useAuth";
// import ConfirmModal from "../ui/confirmModal";

// // ✅ Clés i18n (les valeurs seront traduites dans les .po)
// const navItems = [
//   { key: "nav.home", to: "/" },
//   { key: "nav.pages", to: "/pages" },
//   { key: "nav.products", to: "/products" },
//   { key: "nav.contact", to: "/contact" },
// ];

// // ✅ Avatar réutilisable (photo ou initiale)
// function UserAvatar({ user, size = "md", onClick }) {
//   const sizeClasses = {
//     sm: "w-9 h-9 xl:w-10 xl:h-10 text-sm",
//     md: "w-10 h-10 text-sm",
//     lg: "w-12 h-12 text-base",
//   };

//   const initial = user?.nom?.charAt(0)?.toUpperCase();

//   return (
//     <div
//       onClick={onClick}
//       className={`${sizeClasses[size]} rounded-full bg-primary flex items-center justify-center text-white font-bold shrink-0 overflow-hidden`}
//     >
//       {user?.photo_url ? (
//         <img
//           src={user.photo_url}
//           alt={user.nom || "Utilisateur"}
//           className="w-full h-full object-cover"
//         />
//       ) : (
//         initial || <FaUser />
//       )}
//     </div>
//   );
// }

// // ✅ Squelette de chargement
// function LoadingSkeleton() {
//   return (
//     <div className="flex items-center gap-2 ml-1 shrink-0">
//       <div className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-200 animate-pulse"></div>
//       <div className="flex flex-col gap-1">
//         <div className="w-16 h-2 bg-gray-200 rounded animate-pulse"></div>
//         <div className="w-20 h-3 bg-gray-200 rounded animate-pulse"></div>
//       </div>
//     </div>
//   );
// }

// export default function Navbar() {
//   // ✅ t() via le macro React
//   const { t } = useLingui();

//   const [mobileOpen, setMobileOpen] = useState(false);
//   const [userMenuOpen, setUserMenuOpen] = useState(false);
//   const [logoutModalOpen, setLogoutModalOpen] = useState(false);
//   const userMenuRef = useRef(null);

//   const { user, isAuthenticated, isLoading, logout } = useAuthContext();
//   const logoutMutation = useLogout();
//   const navigate = useNavigate();

//   useEffect(() => {
//     const handleClickOutside = (e) => {
//       if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
//         setUserMenuOpen(false);
//       }
//     };
//     document.addEventListener("mousedown", handleClickOutside);
//     return () => document.removeEventListener("mousedown", handleClickOutside);
//   }, []);

//   const askLogout = () => {
//     setUserMenuOpen(false);
//     setLogoutModalOpen(true);
//   };

//   const confirmLogout = () => {
//     logoutMutation.mutate(undefined, {
//       onSettled: () => {
//         logout();
//         setLogoutModalOpen(false);
//         navigate("/login", { replace: true });
//       },
//     });
//   };

//   return (
//     <div className="w-full bg-white border-b border-gray-100">
//       <div className="alimma-layout py-4 flex items-center justify-between gap-2">
//         {/* Logo + Navigation */}
//         <div className="flex items-center gap-4 xl:gap-8 shrink-0">
//           <Link
//             to="/"
//             className="flex items-center gap-3 font-display text-2xl xl:text-3xl font-black tracking-tight shrink-0 text-gray-900"
//           >
//             <img
//               src="/logo1.png"
//               alt="ALIMMA Logo"
//               className="w-10 h-10 xl:w-11 xl:h-11 object-contain rounded-xl"
//             />
//             <span>
//               ALIM<span className="text-primary">MA</span>
//             </span>
//           </Link>

//           <nav className="hidden lg:flex items-center gap-4 xl:gap-6">
//             {navItems.map((item) => (
//               <NavLink
//                 key={item.to}
//                 to={item.to}
//                 className={({ isActive }) =>
//                   `flex items-center gap-1 text-xs xl:text-sm font-bold uppercase tracking-wider transition ${
//                     isActive ? "text-primary" : "text-gray-800 hover:text-primary"
//                   }`
//                 }
//               >
//                 {/* ✅ t() pour les clés i18n dynamiques */}
//                 {t(item.key)}
//                 <FaChevronDown className="text-[9px] text-gray-500" />
//               </NavLink>
//             ))}
//           </nav>
//         </div>

//         {/* Bloc d'actions à droite */}
//         <div className="hidden lg:flex items-center gap-2 xl:gap-3 shrink-0">
//           <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 hover:text-primary transition cursor-pointer shrink-0">
//             <FaExchangeAlt className="text-sm" />
//           </button>

//           <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 hover:text-primary transition cursor-pointer shrink-0">
//             <FaHeart className="text-sm" />
//           </button>

//           <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 hover:text-primary transition cursor-pointer shrink-0">
//             <FaEye className="text-sm" />
//           </button>

//           {/* Zone utilisateur */}
//           {isLoading ? (
//             <LoadingSkeleton />
//           ) : isAuthenticated ? (
//             <div className="relative ml-1 shrink-0" ref={userMenuRef}>
//               <button
//                 onClick={() => setUserMenuOpen(!userMenuOpen)}
//                 className="flex items-center gap-2 cursor-pointer"
//               >
//                 <UserAvatar user={user} size="sm" />

//                 <div className="text-left leading-tight">
//                   <p className="text-[10px] xl:text-xs uppercase font-bold text-gray-400 tracking-wider">
//                     <Trans>BIENVENU</Trans>
//                   </p>
//                   <span className="font-extrabold uppercase text-gray-800 text-xs xl:text-sm flex items-center gap-1">
//                     {user?.nom?.split(" ")[0] || t`COMPTE`}
//                     <FaChevronDown
//                       className={`text-[9px] transition-transform ${
//                         userMenuOpen ? "rotate-180" : ""
//                       }`}
//                     />
//                   </span>
//                 </div>
//               </button>

//               {userMenuOpen && (
//                 <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50">
//                   <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-3">
//                     <UserAvatar user={user} size="md" />
//                     <div className="min-w-0 flex-1">
//                       <p className="text-sm font-bold text-gray-800 truncate">
//                         {user?.nom || t`Utilisateur`}
//                       </p>
//                       <p className="text-xs text-gray-500 truncate">
//                         {user?.email || user?.telephone || ""}
//                       </p>
//                       {user?.role && (
//                         <span className="inline-block mt-1 px-2 py-0.5 bg-primary/10 text-primary text-[10px] font-bold uppercase rounded">
//                           {user.role}
//                         </span>
//                       )}
//                     </div>
//                   </div>

//                   <Link
//                     to="/profile"
//                     onClick={() => setUserMenuOpen(false)}
//                     className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <FaUser className="text-xs text-gray-400" />
//                     <Trans>Mon compte</Trans>
//                   </Link>

//                   <Link
//                     to="/mes-commandes"
//                     onClick={() => setUserMenuOpen(false)}
//                     className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <FaBoxOpen className="text-xs text-gray-400" />
//                     <Trans>Mes commandes</Trans>
//                   </Link>

//                   <Link
//                     to="/favoris"
//                     onClick={() => setUserMenuOpen(false)}
//                     className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <FaHeart className="text-xs text-gray-400" />
//                     <Trans>Mes favoris</Trans>
//                   </Link>

//                   <Link
//                     to="/parametres"
//                     onClick={() => setUserMenuOpen(false)}
//                     className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <FaCog className="text-xs text-gray-400" />
//                     <Trans>Paramètres</Trans>
//                   </Link>

//                   <div className="border-t border-gray-100 my-1"></div>

//                   <button
//                     onClick={askLogout}
//                     className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 transition"
//                   >
//                     <FaSignOutAlt className="text-xs" />
//                     <Trans>Se déconnecter</Trans>
//                   </button>
//                 </div>
//               )}
//             </div>
//           ) : (
//             <div className="text-left leading-tight ml-1 shrink-0">
//               <p className="text-[10px] xl:text-xs uppercase font-bold text-gray-400 tracking-wider">
//                 <Trans>BIENVENU</Trans>
//               </p>
//               <div className="flex items-center gap-1.5 font-extrabold uppercase text-gray-800 text-xs xl:text-sm">
//                 <Link
//                   to="/login"
//                   className="hover:text-primary transition whitespace-nowrap"
//                 >
//                   <Trans>CONNEXION</Trans>
//                 </Link>
//                 <span className="text-gray-300 font-normal">/</span>
//                 <Link
//                   to="/register"
//                   className="hover:text-primary transition whitespace-nowrap"
//                 >
//                   <Trans>INSCRIPTION</Trans>
//                 </Link>
//               </div>
//             </div>
//           )}

//           {/* Panier */}
//           <div className="flex items-center gap-2 ml-1 xl:ml-3 shrink-0">
//             <div className="relative shrink-0">
//               <div className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600">
//                 <FaShoppingCart className="text-sm" />
//               </div>
//               <span className="badge-primary absolute -top-1 -right-1 text-[10px] xl:text-xs w-5 h-5 border-2 border-white">
//                 5
//               </span>
//             </div>

//             <div className="flex flex-col justify-center text-left leading-tight shrink-0">
//               <span className="text-[10px] xl:text-xs uppercase font-bold text-gray-400 tracking-wider mb-0.5">
//                 <Trans>PANIER</Trans>
//               </span>
//               <span className="font-extrabold text-gray-900 whitespace-nowrap text-xs xl:text-sm">
//                 FCFA 1,689.00
//               </span>
//             </div>
//           </div>
//         </div>

//         {/* Bouton mobile */}
//         <button
//           onClick={() => setMobileOpen(!mobileOpen)}
//           className="lg:hidden p-2 text-2xl text-gray-800"
//         >
//           {mobileOpen ? <FaTimes /> : <FaBars />}
//         </button>
//       </div>

//       {/* Menu Mobile */}
//       {mobileOpen && (
//         <div className="lg:hidden bg-white border-t border-gray-200 px-4 py-3">
//           <nav className="flex flex-col gap-2">
//             {navItems.map((item) => (
//               <NavLink
//                 key={item.to}
//                 to={item.to}
//                 onClick={() => setMobileOpen(false)}
//                 className="py-2 text-sm font-bold uppercase text-gray-800"
//               >
//                 {t(item.key)}
//               </NavLink>
//             ))}

//             <div className="border-t border-gray-100 pt-3 mt-2">
//               {isLoading ? (
//                 <div className="flex items-center gap-3 mb-3">
//                   <div className="w-10 h-10 rounded-full bg-gray-200 animate-pulse"></div>
//                   <div className="flex flex-col gap-1">
//                     <div className="w-24 h-3 bg-gray-200 rounded animate-pulse"></div>
//                     <div className="w-32 h-2 bg-gray-200 rounded animate-pulse"></div>
//                   </div>
//                 </div>
//               ) : isAuthenticated ? (
//                 <>
//                   <div className="flex items-center gap-3 mb-3">
//                     <UserAvatar user={user} size="md" />
//                     <div className="min-w-0">
//                       <p className="text-sm font-bold text-gray-800 truncate">
//                         {user?.nom}
//                       </p>
//                       <p className="text-xs text-gray-500 truncate">
//                         {user?.email || user?.telephone}
//                       </p>
//                     </div>
//                   </div>

//                   <Link
//                     to="/profile"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-gray-800"
//                   >
//                     <Trans>Mon compte</Trans>
//                   </Link>
//                   <Link
//                     to="/mes-commandes"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-gray-800"
//                   >
//                     <Trans>Mes commandes</Trans>
//                   </Link>
//                   <Link
//                     to="/favoris"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-gray-800"
//                   >
//                     <Trans>Mes favoris</Trans>
//                   </Link>
//                   <Link
//                     to="/parametres"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-gray-800"
//                   >
//                     <Trans>Paramètres</Trans>
//                   </Link>
//                   <button
//                     onClick={() => {
//                       setMobileOpen(false);
//                       setLogoutModalOpen(true);
//                     }}
//                     className="block py-2 text-sm font-bold uppercase text-red-500"
//                   >
//                     <Trans>Se déconnecter</Trans>
//                   </button>
//                 </>
//               ) : (
//                 <div className="flex flex-col gap-1">
//                   <Link
//                     to="/login"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-gray-800 hover:text-primary transition"
//                   >
//                     <Trans>CONNEXION</Trans>
//                   </Link>
//                   <Link
//                     to="/register"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-primary"
//                   >
//                     <Trans>INSCRIPTION</Trans>
//                   </Link>
//                 </div>
//               )}
//             </div>
//           </nav>
//         </div>
//       )}

//       {/* Modal confirmation */}
//       <ConfirmModal
//         isOpen={logoutModalOpen}
//         title={t`Se déconnecter ?`}
//         message={t`Voulez-vous vraiment vous déconnecter de votre compte ALIMMA ?`}
//         confirmLabel={t`Oui, me déconnecter`}
//         cancelLabel={t`Annuler`}
//         onConfirm={confirmLogout}
//         onCancel={() => setLogoutModalOpen(false)}
//         isPending={logoutMutation.isPending}
//         variant="danger"
//       />
//     </div>
//   );
// }