


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