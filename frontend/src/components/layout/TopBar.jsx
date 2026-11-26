


import { Link } from "react-router-dom";
import { Icon } from "../ui";
import { TOPBAR_LINKS } from "../../config/navigation";

/** Bandeau sombre : promesses de service à gauche, liens utiles à droite. */
export default function TopBar() {
  return (
    <div className="topbar">
      <div className="site-wrap topbar__inner">
        <ul className="topbar__info">
          <li>
            <Icon name="local_shipping" size={18} /> Livraison suivie à Douala et Yaoundé
          </li>
          <li>
            <Icon name="smartphone" size={18} /> Paiement en espèces à la livraison · Mobile Money bientôt disponible
          </li>
        </ul>
        <nav className="topbar__links" aria-label="Liens utiles">
          {TOPBAR_LINKS.map((l) => (
            <Link key={l.to} to={l.to}>{l.label}</Link>
          ))}
        </nav>
      </div>
    </div>
  );
}