import { Link, NavLink } from "react-router-dom";
import { Icon } from "../ui";
import { CATEGORIES, HIGHLIGHTS, categoryPath } from "../../config/navigation";

/** Barre violette des catégories (desktop uniquement ; sur mobile, tout est dans le menu latéral). */
export default function CategoryNav() {
  return (
    <nav className="catnav only-desktop" aria-label="Catégories">
      <div className="site-wrap catnav__inner">
        <Link to="/categories" className="catnav__all">
          <Icon name="menu" /> Toutes les catégories
        </Link>

        <ul className="catnav__list">
          {CATEGORIES.map((c) => (
            <li key={c.slug}>
              <NavLink to={categoryPath(c.slug)} className={({ isActive }) => (isActive ? "is-active" : undefined)}>
                {c.label}
              </NavLink>
            </li>
          ))}
        </ul>

        <ul className="catnav__list catnav__list--end">
          {HIGHLIGHTS.map((h) => (
            <li key={h.to}>
              <NavLink to={h.to} data-tone={h.tone} className={({ isActive }) => (isActive ? "is-active" : undefined)}>
                <Icon name={h.icon} filled={h.tone === "flash"} size={22} /> {h.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
