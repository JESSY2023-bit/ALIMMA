



// // src/components/layout/Navbar.jsx
// import { useState, useRef, useEffect } from "react";
// import { Link, NavLink, useNavigate } from "react-router-dom";
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
// } from "react-icons/fa";

// import { useAuthContext } from "../../hooks/useAuthContext";
// import { useLogout } from "../../hooks/useAuth";

// const navItems = [
//   { label: "HOMES", to: "/" },
//   { label: "PAGES", to: "/pages" },
//   { label: "PRODUCTS", to: "/products" },
//   { label: "CONTACT", to: "/contact" },
// ];

// export default function Navbar() {
//   const [mobileOpen, setMobileOpen] = useState(false);
//   const [userMenuOpen, setUserMenuOpen] = useState(false);
//   const userMenuRef = useRef(null);

//   const { user, isAuthenticated, logout } = useAuthContext();
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

//   const handleLogout = () => {
//     logoutMutation.mutate(undefined, {
//       onSettled: () => {
//         logout();
//         setUserMenuOpen(false);
//         navigate("/login", { replace: true });
//       },
//     });
//   };

//   return (
//     <div className="w-full bg-white border-b border-gray-100">
//   {/* ✅ Remettre alimma-layout */}
//   <div className="alimma-layout py-4 flex items-center justify-between gap-2">
//         {/* ================================ */}
//         {/* Logo + Navigation                 */}
//         {/* ================================ */}
//         <div className="flex items-center gap-4 xl:gap-8 shrink-0">
//           <Link
//             to="/"
//             className="font-display text-2xl xl:text-3xl font-black tracking-tight shrink-0 text-gray-900"
//           >
//             ALIM<span className="text-primary">MA</span>
//           </Link>

//           <nav className="hidden lg:flex items-center gap-4 xl:gap-6">
//             {navItems.map((item) => (
//               <NavLink
//                 key={item.to}
//                 to={item.to}
//                 className={({ isActive }) =>
//                   `flex items-center gap-1 text-xs xl:text-sm font-bold uppercase tracking-wider transition ${
//                     isActive ? "text-primary" : "text-gray-800 text-primary-hover"
//                   }`
//                 }
//               >
//                 {item.label}
//                 <FaChevronDown className="text-[9px] text-gray-500" />
//               </NavLink>
//             ))}
//           </nav>
//         </div>

//         {/* ================================ */}
//         {/* Bloc d'actions à droite           */}
//         {/* ================================ */}
//         <div className="hidden lg:flex items-center gap-2 xl:gap-3 shrink-0">
//           <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
//             <FaExchangeAlt className="text-sm" />
//           </button>

//           <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
//             <FaHeart className="text-sm" />
//           </button>

//           <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
//             <FaEye className="text-sm" />
//           </button>

//           {isAuthenticated ? (
//             <div className="relative ml-1 shrink-0" ref={userMenuRef}>
//               <button
//                 onClick={() => setUserMenuOpen(!userMenuOpen)}
//                 className="text-left leading-tight cursor-pointer group"
//               >
//                 <p className="text-[10px] xl:text-xs uppercase font-bold text-gray-400 tracking-wider">
//                   BIENVENU
//                 </p>
//                 <span className="font-extrabold uppercase text-gray-800 text-primary-hover transition whitespace-nowrap text-xs xl:text-sm flex items-center gap-1">
//                   {user?.nom || "MON COMPTE"}
//                   <FaChevronDown
//                     className={`text-[9px] transition-transform ${
//                       userMenuOpen ? "rotate-180" : ""
//                     }`}
//                   />
//                 </span>
//               </button>

//               {userMenuOpen && (
//                 <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-100 py-2 z-50">
//                   <div className="px-4 py-2 border-b border-gray-100">
//                     <p className="text-sm font-bold text-gray-800 truncate">
//                       {user?.nom}
//                     </p>
//                     <p className="text-xs text-gray-500 truncate">
//                       {user?.email || user?.telephone}
//                     </p>
//                   </div>

//                   <Link
//                     to="/profile"
//                     onClick={() => setUserMenuOpen(false)}
//                     className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <FaUser className="text-xs" />
//                     Mon profil
//                   </Link>

//                   <button
//                     onClick={handleLogout}
//                     disabled={logoutMutation.isPending}
//                     className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-500 hover:bg-red-50 transition disabled:opacity-50"
//                   >
//                     <FaSignOutAlt className="text-xs" />
//                     {logoutMutation.isPending ? "Déconnexion..." : "Se déconnecter"}
//                   </button>
//                 </div>
//               )}
//             </div>
//           ) : (
//             <div className="text-left leading-tight ml-1 shrink-0">
//               <p className="text-[10px] xl:text-xs uppercase font-bold text-gray-400 tracking-wider">
//                 BIENVENU
//               </p>
//               <div className="flex items-center gap-1.5 font-extrabold uppercase text-gray-800 text-xs xl:text-sm">
//                 <Link
//                   to="/login"
//                   className="text-primary-hover transition whitespace-nowrap"
//                 >
//                   CONNEXION
//                 </Link>
//                 <span className="text-gray-300 font-normal">/</span>
//                 <Link
//                   to="/register"
//                   className="text-primary-hover transition whitespace-nowrap"
//                 >
//                   INSCRIPTION
//                 </Link>
//               </div>
//             </div>
//           )}

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
//                 PANIER
//               </span>
//               <span className="font-extrabold text-gray-900 whitespace-nowrap text-xs xl:text-sm">
//                 FCFA 1,689.00
//               </span>
//             </div>
//           </div>
//         </div>

//         <button
//           onClick={() => setMobileOpen(!mobileOpen)}
//           className="lg:hidden p-2 text-2xl text-gray-800"
//         >
//           {mobileOpen ? <FaTimes /> : <FaBars />}
//         </button>
//       </div>

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
//                 {item.label}
//               </NavLink>
//             ))}

//             <div className="border-t border-gray-100 pt-3 mt-2">
//               {isAuthenticated ? (
//                 <>
//                   <p className="text-sm text-gray-500 mb-2">
//                     Connecté en tant que{" "}
//                     <span className="font-bold text-gray-800">{user?.nom}</span>
//                   </p>
//                   <Link
//                     to="/profile"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-gray-800"
//                   >
//                     Mon profil
//                   </Link>
//                   <button
//                     onClick={() => {
//                       handleLogout();
//                       setMobileOpen(false);
//                     }}
//                     className="block py-2 text-sm font-bold uppercase text-red-500"
//                   >
//                     Se déconnecter
//                   </button>
//                 </>
//               ) : (
//                 <div className="flex flex-col gap-1">
//                   <Link
//                     to="/login"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-gray-800 hover:text-primary transition"
//                   >
//                     Connexion
//                   </Link>
//                   <Link
//                     to="/register"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-primary"
//                   >
//                     Inscription
//                   </Link>
//                 </div>
//               )}
//             </div>
//           </nav>
//         </div>
//       )}
//     </div>
//   );
// }




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

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [logoutModalOpen, setLogoutModalOpen] = useState(false);
  const userMenuRef = useRef(null);

  const { user, isAuthenticated, logout } = useAuthContext();
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

  // 1) Ouvre la modal de confirmation
  const askLogout = () => {
    setUserMenuOpen(false);
    setLogoutModalOpen(true);
  };

  // 2) Confirme la déconnexion : appel API + nettoyage + redirection
  const confirmLogout = () => {
    logoutMutation.mutate(undefined, {
      onSettled: () => {
        logout(); // Nettoie le contexte (user = null, tokens effacés)
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
            className="font-display text-2xl xl:text-3xl font-black tracking-tight shrink-0 text-gray-900"
          >
            ALIM<span className="text-primary">MA</span>
          </Link>

          <nav className="hidden lg:flex items-center gap-4 xl:gap-6">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-1 text-xs xl:text-sm font-bold uppercase tracking-wider transition ${
                    isActive
                      ? "text-primary"
                      : "text-gray-800 text-primary-hover"
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
          {/* Zone utilisateur : connecté ou non  */}
          {/* =================================== */}
          {isAuthenticated ? (
            <div className="relative ml-1 shrink-0" ref={userMenuRef}>
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 cursor-pointer"
              >
                {/* ✅ Avatar avec initiale */}
                <div className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold text-sm shrink-0">
                  {user?.nom?.charAt(0)?.toUpperCase() || <FaUser />}
                </div>

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
                <div className="absolute right-0 top-full mt-2 w-60 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50">
                  {/* En-tête */}
                  <div className="px-4 py-3 border-b border-gray-100">
                    <p className="text-sm font-bold text-gray-800 truncate">
                      {user?.nom || "Utilisateur"}
                    </p>
                    <p className="text-xs text-gray-500 truncate">
                      {user?.email || user?.telephone || ""}
                    </p>
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

                  {/* Séparateur */}
                  <div className="border-t border-gray-100 my-1"></div>

                  {/* Déconnexion */}
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
              {isAuthenticated ? (
                <>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
                      {user?.nom?.charAt(0)?.toUpperCase() || <FaUser />}
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-800">
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