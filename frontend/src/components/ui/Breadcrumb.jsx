import { Link } from "react-router-dom";
import { Icon } from "./Icon";

/** items : [{ label, to? }] — le dernier est la page courante. */
export function Breadcrumb({ items }) {
  return (
    <nav aria-label="Fil d’Ariane" className="ui-crumb">
      {items.map((item, i) => {
        const last = i === items.length - 1;
        return (
          <span key={`${item.label}-${i}`} className="ui-crumb__item">
            {i > 0 && <Icon name="chevron_right" size={16} />}
            {last ? <span aria-current="page">{item.label}</span> : item.to ? <Link to={item.to}>{item.label}</Link> : <span>{item.label}</span>}
          </span>
        );
      })}
    </nav>
  );
}
