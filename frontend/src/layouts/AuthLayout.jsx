import { useNavigate } from "react-router-dom";
import { Icon, IconButton, Logo } from "../components/ui";

const CHIPS = [
  { icon: "smartphone", price: "95 000" },
  { icon: "chair", price: "75 000" },
  { icon: "headphones", price: "85 000" },
];

const GRID = [
  { icon: "smartphone", name: "Galaxy S9 64 Go", price: "95 000", badge: "−20 %" },
  { icon: "chair", name: "Fauteuil velours", price: "75 000" },
  { icon: "laptop_mac", name: "MacBook Air M1", price: "420 000" },
  { icon: "headphones", name: "Casque Bose QC45", price: "85 000", badge: "−23 %" },
  { icon: "watch", name: "Apple Watch S3", price: "60 000" },
  { icon: "speaker", name: "Enceinte Beosound", price: "110 000" },
];

function PanelRegister() {
  return (
    <>
      <h2 className="auth__headline">Achetez malin, vendez vite.</h2>
      <p className="auth__lead">
        Votre compte gratuit débloque l’achat protégé, les ventes flash et la publication d’annonces.
      </p>
      <div className="showcase-offers">
        <article className="showcase-card">
          <span className="showcase-card__thumb"><Icon name="headphones" size={28} /></span>
          <div>
            <p className="showcase-card__tag" data-tone="flash"><Icon name="bolt" filled /> Vente flash · −23 %</p>
            <p className="showcase-card__name">Casque Bose QuietComfort 45</p>
            <p className="showcase-card__price" data-tone="flash"><b>85 000 <small>FCFA</small></b><s>110 000</s></p>
          </div>
        </article>
        <article className="showcase-card">
          <span className="showcase-card__thumb"><Icon name="chair" size={28} /></span>
          <div>
            <p className="showcase-card__tag" data-tone="sold"><Icon name="sell" filled /> Vendu en 2 jours à Bastos</p>
            <p className="showcase-card__name">Fauteuil en velours orange</p>
            <p className="showcase-card__price">75 000 <small>FCFA</small></p>
          </div>
        </article>
        <article className="showcase-card">
          <span className="showcase-card__thumb"><Icon name="smartphone" size={28} /></span>
          <div>
            <p className="showcase-card__tag" data-tone="ship"><Icon name="local_shipping" filled /> Livré demain à Bonamoussadi</p>
            <p className="showcase-card__name">Samsung Galaxy S9 64 Go</p>
            <p className="showcase-card__price">95 000 <small>FCFA</small></p>
          </div>
        </article>
      </div>
    </>
  );
}

function PanelLogin() {
  return (
    <>
      <h2 className="auth__headline">Tout le Cameroun fait son marché ici.</h2>
      <p className="auth__lead">
        Téléphones, maison, mode, informatique : achetez près de chez vous, payez à la livraison.
      </p>
      <div className="showcase-grid">
        {GRID.map((p) => (
          <article key={p.name} className="showcase-card">
            {p.badge && <span className="showcase-badge">{p.badge}</span>}
            <span className="showcase-card__thumb"><Icon name={p.icon} size={36} /></span>
            <p className="showcase-card__name">{p.name}</p>
            <p className="showcase-card__price">{p.price} <small>FCFA</small></p>
          </article>
        ))}
      </div>
    </>
  );
}

/**
 * Mise en page Connexion / Inscription.
 *  variant : "register" | "login" (contenu du panneau desktop)
 *  closeIcon : "arrow_back" | "close" · onClose : action du bouton (défaut : retour)
 *  heroTitle / heroText : en-tête violet (mobile) · title / subtitle : en-tête de la carte (desktop)
 */
export default function AuthLayout({
  variant = "register", closeIcon = "arrow_back", onClose, heroTitle, heroText, title, subtitle, children,
}) {
  const navigate = useNavigate();
  const close = onClose ?? (() => navigate(-1));
  return (
    <div className="auth">
      <aside className="auth__panel">
        <Logo inverse />
        {variant === "login" ? <PanelLogin /> : <PanelRegister />}
        <p className="auth__panel-foot">
          Payez à la livraison : <span className="auth__pill">Espèces</span>
        </p>
      </aside>

      <div className="auth__col">
        <header className="auth__hero">
          <div className="auth__bar">
            <IconButton
              icon={closeIcon}
              variant="ghost"
              className="auth__back"
              aria-label={closeIcon === "close" ? "Fermer" : "Retour"}
              onClick={close}
            />
            <Logo inverse />
          </div>
          <h1 className="auth__hero-title">{heroTitle}</h1>
          <p className="auth__hero-text">{heroText}</p>
          <div className="auth__chips" aria-hidden="true">
            {CHIPS.map((c) => (
              <span key={c.icon} className="auth__chip">
                <span className="auth__thumb"><Icon name={c.icon} size={20} /></span>
                <span>{c.price} <small>FCFA</small></span>
              </span>
            ))}
          </div>
        </header>

        <main className="auth__sheet">
          <div className="auth__card">
            <div className="auth__card-head">
              <h1 className="auth__card-title">{title}</h1>
              {subtitle && <p className="auth__card-sub">{subtitle}</p>}
            </div>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
