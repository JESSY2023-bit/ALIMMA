

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
//   FaBoxOpen,
//   FaCog,
// } from "react-icons/fa";

// import { useAuthContext } from "../../hooks/useAuthContext";
// import { useLogout } from "../../hooks/useAuth";
// import ConfirmModal from "../ui/confirmModal";

// const navItems = [
//   { label: "HOMES", to: "/" },
//   { label: "PAGES", to: "/pages" },
//   { label: "PRODUCTS", to: "/products" },
//   { label: "CONTACT", to: "/contact" },
// ];

// export default function Navbar() {
//   const [mobileOpen, setMobileOpen] = useState(false);
//   const [userMenuOpen, setUserMenuOpen] = useState(false);
//   const [logoutModalOpen, setLogoutModalOpen] = useState(false);
//   const userMenuRef = useRef(null);

//   const { user, isAuthenticated, logout } = useAuthContext();
//   const logoutMutation = useLogout();
//   const navigate = useNavigate();

//   // Ferme le menu au clic ailleurs
//   useEffect(() => {
//     const handleClickOutside = (e) => {
//       if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
//         setUserMenuOpen(false);
//       }
//     };
//     document.addEventListener("mousedown", handleClickOutside);
//     return () => document.removeEventListener("mousedown", handleClickOutside);
//   }, []);

//   // 1) Ouvre la modal de confirmation
//   const askLogout = () => {
//     setUserMenuOpen(false);
//     setLogoutModalOpen(true);
//   };

//   // 2) Confirme la déconnexion : appel API + nettoyage + redirection
//   const confirmLogout = () => {
//     logoutMutation.mutate(undefined, {
//       onSettled: () => {
//         logout(); // Nettoie le contexte (user = null, tokens effacés)
//         setLogoutModalOpen(false);
//         navigate("/login", { replace: true });
//       },
//     });
//   };

//   return (
//     <div className="w-full bg-white border-b border-gray-100">
//       <div className="alimma-layout py-4 flex items-center justify-between gap-2">
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
//                     isActive
//                       ? "text-primary"
//                       : "text-gray-800 text-primary-hover"
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
//           {/* Icônes circulaires */}
//           <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
//             <FaExchangeAlt className="text-sm" />
//           </button>

//           <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
//             <FaHeart className="text-sm" />
//           </button>

//           <button className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
//             <FaEye className="text-sm" />
//           </button>

//           {/* =================================== */}
//           {/* Zone utilisateur : connecté ou non  */}
//           {/* =================================== */}
//           {isAuthenticated ? (
//             <div className="relative ml-1 shrink-0" ref={userMenuRef}>
//               <button
//                 onClick={() => setUserMenuOpen(!userMenuOpen)}
//                 className="flex items-center gap-2 cursor-pointer"
//               >
//                 {/* ✅ Avatar avec initiale */}
//                 <div className="w-9 h-9 xl:w-10 xl:h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold text-sm shrink-0">
//                   {user?.nom?.charAt(0)?.toUpperCase() || <FaUser />}
//                 </div>

//                 <div className="text-left leading-tight">
//                   <p className="text-[10px] xl:text-xs uppercase font-bold text-gray-400 tracking-wider">
//                     BIENVENU
//                   </p>
//                   <span className="font-extrabold uppercase text-gray-800 text-xs xl:text-sm flex items-center gap-1">
//                     {user?.nom?.split(" ")[0] || "COMPTE"}
//                     <FaChevronDown
//                       className={`text-[9px] transition-transform ${
//                         userMenuOpen ? "rotate-180" : ""
//                       }`}
//                     />
//                   </span>
//                 </div>
//               </button>

//               {/* Dropdown */}
//               {userMenuOpen && (
//                 <div className="absolute right-0 top-full mt-2 w-60 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50">
//                   {/* En-tête */}
//                   <div className="px-4 py-3 border-b border-gray-100">
//                     <p className="text-sm font-bold text-gray-800 truncate">
//                       {user?.nom || "Utilisateur"}
//                     </p>
//                     <p className="text-xs text-gray-500 truncate">
//                       {user?.email || user?.telephone || ""}
//                     </p>
//                   </div>

//                   {/* Liens */}
//                   <Link
//                     to="/profile"
//                     onClick={() => setUserMenuOpen(false)}
//                     className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <FaUser className="text-xs text-gray-400" />
//                     Mon compte
//                   </Link>

//                   <Link
//                     to="/mes-commandes"
//                     onClick={() => setUserMenuOpen(false)}
//                     className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <FaBoxOpen className="text-xs text-gray-400" />
//                     Mes commandes
//                   </Link>

//                   <Link
//                     to="/favoris"
//                     onClick={() => setUserMenuOpen(false)}
//                     className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <FaHeart className="text-xs text-gray-400" />
//                     Mes favoris
//                   </Link>

//                   <Link
//                     to="/parametres"
//                     onClick={() => setUserMenuOpen(false)}
//                     className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <FaCog className="text-xs text-gray-400" />
//                     Paramètres
//                   </Link>

//                   {/* Séparateur */}
//                   <div className="border-t border-gray-100 my-1"></div>

//                   {/* Déconnexion */}
//                   <button
//                     onClick={askLogout}
//                     className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 transition"
//                   >
//                     <FaSignOutAlt className="text-xs" />
//                     Se déconnecter
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
//                 PANIER
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

//       {/* ================================ */}
//       {/* Menu Mobile                      */}
//       {/* ================================ */}
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
//                   <div className="flex items-center gap-3 mb-3">
//                     <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
//                       {user?.nom?.charAt(0)?.toUpperCase() || <FaUser />}
//                     </div>
//                     <div>
//                       <p className="text-sm font-bold text-gray-800">
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
//                     Mon compte
//                   </Link>
//                   <Link
//                     to="/mes-commandes"
//                     onClick={() => setMobileOpen(false)}
//                     className="block py-2 text-sm font-bold uppercase text-gray-800"
//                   >
//                     Mes commandes
//                   </Link>
//                   <button
//                     onClick={() => {
//                       setMobileOpen(false);
//                       setLogoutModalOpen(true);
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

//       {/* ================================ */}
//       {/* Modal de confirmation déconnexion */}
//       {/* ================================ */}
//       <ConfirmModal
//         isOpen={logoutModalOpen}
//         title="Se déconnecter ?"
//         message="Voulez-vous vraiment vous déconnecter de votre compte ALIMMA ?"
//         confirmLabel="Oui, me déconnecter"
//         cancelLabel="Annuler"
//         onConfirm={confirmLogout}
//         onCancel={() => setLogoutModalOpen(false)}
//         isPending={logoutMutation.isPending}
//         variant="danger"
//       />
//     </div>
//   );
// }




import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Icon, IconButton, Logo } from "../ui";
import SearchBar from "./SearchBar";
import { useAuthContext } from "../../hooks/useAuthContext";
import { useLogout } from "../../hooks/useAuth";
import ConfirmModal from "../ui/confirmModal";
import { CATEGORIES, HIGHLIGHTS, categoryPath, formatFcfa } from "../../config/navigation";

// TODO panier / messages : à brancher sur vos hooks quand ils existent.
const cart = { count: 0, total: 0 };
const unreadMessages = 0;

const getInitials = (name = "") =>
  name.split(" ").filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase();

const ACCOUNT_LINKS = [
  { label: "Mon compte", to: "/profile", icon: "person" },
  { label: "Mes commandes", to: "/mes-commandes", icon: "receipt_long" },
  { label: "Mes favoris", to: "/favoris", icon: "favorite" },
  { label: "Paramètres", to: "/parametres", icon: "settings" },
];

export default function Navbar() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthContext();
  const logoutMutation = useLogout();

  const [menuOpen, setMenuOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [logoutOpen, setLogoutOpen] = useState(false);
  const menuRef = useRef(null);
  const drawerCloseRef = useRef(null);

  const firstName = user?.nom?.split(" ")[0];
  const initials = getInitials(user?.nom);

  // Menu compte : fermeture au clic extérieur et sur Échap.
  useEffect(() => {
    if (!menuOpen) return undefined;
    const onDown = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false); };
    const onKey = (e) => { if (e.key === "Escape") setMenuOpen(false); };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [menuOpen]);

  // Tiroir mobile : Échap, défilement bloqué, focus sur le bouton fermer.
  useEffect(() => {
    if (!drawerOpen) return undefined;
    const onKey = (e) => { if (e.key === "Escape") setDrawerOpen(false); };
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKey);
    drawerCloseRef.current?.focus();
    return () => {
      document.body.style.overflow = previous;
      document.removeEventListener("keydown", onKey);
    };
  }, [drawerOpen]);

  const askLogout = () => {
    setMenuOpen(false);
    setDrawerOpen(false);
    setLogoutOpen(true);
  };

  const confirmLogout = () => {
    logoutMutation.mutate(undefined, {
      onSettled: () => {
        logout();
        setLogoutOpen(false);
        navigate("/login", { replace: true });
      },
    });
  };

  const closeDrawer = () => setDrawerOpen(false);

  return (
    <header className="site-header">
      <div className="site-wrap header__inner">
        <IconButton
          icon="menu" variant="ghost" className="header__burger only-mobile"
          aria-label="Ouvrir le menu" aria-expanded={drawerOpen} onClick={() => setDrawerOpen(true)}
        />

        <Link to="/" className="header__logo" aria-label="ALIMMA, accueil">
          <Logo />
        </Link>

        <SearchBar className="header__search" />

        <div className="header__actions">
          {/* Compte */}
          {isAuthenticated ? (
            <div className="h-account only-desktop" ref={menuRef}>
              <button
                type="button" className="h-action" aria-haspopup="true" aria-expanded={menuOpen}
                onClick={() => setMenuOpen((o) => !o)}
              >
                <span className="h-avatar">{initials || <Icon name="person" />}</span>
                <span className="h-action__text">
                  <small>Bonjour, {firstName || "vous"}</small>
                  <strong>Mon compte <Icon name="expand_more" size={18} className={menuOpen ? "is-open" : ""} /></strong>
                </span>
              </button>

              {menuOpen && (
                <div className="h-menu">
                  <div className="h-menu__head">
                    <p>{user?.nom || "Utilisateur"}</p>
                    <small>{user?.email || user?.telephone || ""}</small>
                  </div>
                  {ACCOUNT_LINKS.map((l) => (
                    <Link key={l.to} to={l.to} className="h-menu__item" onClick={() => setMenuOpen(false)}>
                      <Icon name={l.icon} size={20} /> {l.label}
                    </Link>
                  ))}
                  <button type="button" className="h-menu__item h-menu__item--danger" onClick={askLogout}>
                    <Icon name="logout" size={20} /> Se déconnecter
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="h-action only-desktop">
              <Icon name="person" size={30} />
              <span className="h-action__text">
                <small>Bonjour, identifiez-vous</small>
                <strong>Mon compte</strong>
              </span>
            </Link>
          )}

          {/* Messages (connecté) */}
          {isAuthenticated && (
            <Link to="/messages" className="h-action only-desktop" aria-label={`Messages${unreadMessages ? `, ${unreadMessages} non lus` : ""}`}>
              <span className="h-icon">
                <Icon name="chat_bubble" size={28} />
                {unreadMessages > 0 && <span className="h-badge h-badge--alert">{unreadMessages}</span>}
              </span>
            </Link>
          )}

          {/* Favoris */}
          <Link to="/favoris" className="h-action only-desktop">
            <Icon name="favorite" size={28} />
            <span className="h-action__label">Favoris</span>
          </Link>

          {/* Panier */}
          <Link to="/panier" className="h-action" aria-label={`Panier, ${cart.count} article${cart.count > 1 ? "s" : ""}, ${formatFcfa(cart.total)}`}>
            <span className="h-icon">
              <Icon name="shopping_cart" size={28} />
              {cart.count > 0 && <span className="h-badge">{cart.count}</span>}
            </span>
            <span className="h-action__text only-desktop">
              <small>Panier</small>
              <strong>{formatFcfa(cart.total)}</strong>
            </span>
          </Link>
        </div>
      </div>

      {/* Tiroir mobile (menu latéral) */}
      {drawerOpen && (
        <div className="drawer" role="dialog" aria-modal="true" aria-label="Menu principal">
          <button type="button" className="drawer__backdrop" aria-label="Fermer le menu" tabIndex={-1} onClick={closeDrawer} />
          <aside className="drawer__panel">
            <div className="drawer__head">
              <Logo />
              <IconButton ref={drawerCloseRef} icon="close" variant="ghost" aria-label="Fermer le menu" onClick={closeDrawer} />
            </div>

            <div className="drawer__account">
              {isAuthenticated ? (
                <>
                  <span className="h-avatar">{initials || <Icon name="person" />}</span>
                  <div>
                    <p className="drawer__name">{user?.nom}</p>
                    <small>{user?.email || user?.telephone}</small>
                  </div>
                </>
              ) : (
                <div className="drawer__cta">
                  <Link to="/login" className="ui-btn ui-btn--primary ui-btn--lg ui-btn--full" onClick={closeDrawer}>Se connecter</Link>
                  <Link to="/register" className="ui-btn ui-btn--secondary ui-btn--lg ui-btn--full" onClick={closeDrawer}>Créer un compte gratuit</Link>
                </div>
              )}
            </div>

            <nav className="drawer__nav" aria-label="Menu principal">
              {isAuthenticated && (
                <ul>
                  {ACCOUNT_LINKS.map((l) => (
                    <li key={l.to}>
                      <Link to={l.to} onClick={closeDrawer}><Icon name={l.icon} /> {l.label}</Link>
                    </li>
                  ))}
                  <li><Link to="/messages" onClick={closeDrawer}><Icon name="chat_bubble" /> Messages</Link></li>
                </ul>
              )}

              <p className="drawer__title">Catégories</p>
              <ul>
                {CATEGORIES.map((c) => (
                  <li key={c.slug}>
                    <Link to={categoryPath(c.slug)} onClick={closeDrawer}><Icon name={c.icon} /> {c.label}</Link>
                  </li>
                ))}
              </ul>

              <p className="drawer__title">À la une</p>
              <ul>
                {HIGHLIGHTS.map((h) => (
                  <li key={h.to}>
                    <Link to={h.to} onClick={closeDrawer} data-tone={h.tone}><Icon name={h.icon} filled={h.tone === "flash"} /> {h.label}</Link>
                  </li>
                ))}
                <li><Link to="/aide" onClick={closeDrawer}><Icon name="help" /> Aide</Link></li>
              </ul>
            </nav>

            {isAuthenticated && (
              <button type="button" className="drawer__logout" onClick={askLogout}>
                <Icon name="logout" /> Se déconnecter
              </button>
            )}
          </aside>
        </div>
      )}

      <ConfirmModal
        isOpen={logoutOpen}
        title="Se déconnecter ?"
        message="Voulez-vous vraiment vous déconnecter de votre compte ALIMMA ?"
        confirmLabel="Oui, me déconnecter"
        cancelLabel="Annuler"
        onConfirm={confirmLogout}
        onCancel={() => setLogoutOpen(false)}
        isPending={logoutMutation.isPending}
        variant="danger"
      />
    </header>
  );
}