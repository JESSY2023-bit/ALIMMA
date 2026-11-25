import { Link } from "react-router-dom";
import { Logo } from "../ui";
import { FOOTER_COLUMNS } from "../../config/navigation";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="site-footer__pattern" aria-hidden="true" />
      <div className="site-wrap">
        <div className="site-footer__grid">
          <div className="site-footer__brand">
            <Logo inverse />
            <p className="site-footer__tagline">La marketplace de confiance du Cameroun.</p>
            <p className="site-footer__label">Moyens de paiement</p>
            <div className="site-footer__pay">
              <span className="auth__pill">Espèces</span>
              <span>Mobile Money (MTN, Orange) : bientôt disponible</span>
            </div>
          </div>

          {FOOTER_COLUMNS.map((col) => (
            <nav key={col.title} aria-label={col.title}>
              <h2>{col.title}</h2>
              <ul>
                {col.links.map((l) => (
                  <li key={l.label}><Link to={l.to}>{l.label}</Link></li>
                ))}
              </ul>
            </nav>
          ))}
        </div>

        <div className="site-footer__bottom">
          <p>© {new Date().getFullYear()} ALIMMA · Douala, Cameroun</p>
          <p>Conforme à la loi n° 2010/012 relative à la cybersécurité</p>
        </div>
      </div>
    </footer>
  );
}